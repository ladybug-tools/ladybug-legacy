# Solar Envelope
# Provides two solar envelopes as both a 3d point grid and a polysurface given a filtered list of suns and a border line representing the building site
# The first (Solar Rights envelope) represents the maximum heights in which new masses could be placed in a given site withought interfering with the sun rights of surrounding buildings
# The second (Solar Collection envelope) represents the opposite - the minimum heights from which new developemnt would recieve sun access, given an urban context
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Boris Plotnikov <pborisp@gmail.com> and with the assistance and guidance of Prof. Guedi Capeluto, based on SustArc model
# For further reading it might be worth taking a look at Ralph Knowles's work, e.g - http://www.fau.usp.br/aut5823/Acesso_ao_Sol/Knowles_2003_Solar_Envelope.pdf
# and G. Capeluto and E. Shaviv's, e.g - http://www.ibpsa.org/proceedings/BS1999/BS99_C-22.pdf
# the component relies to a great extend on the concepts described there
# Ladybug is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Ladybug is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to generate a solar envelope for a given test surface, set of solar vectors, and context geometry that you want to ensure solar access to.  Solar envelopes are typically used to illustrate the volume that can be built within in order to ensure that a new development does not shade the surrounding properties for a given set of sun vectors.

-
Provided by Ladybug 0.0.60
"""
ghenv.Component.Name = 'Ladybug_SolarEnvelopeAdvanced'
ghenv.Component.NickName = 'SolarEnvelopeAdvanced'
ghenv.Component.Message = 'VER 0.0.60\nAUG_18_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import time, math, Rhino, copy
import System.Threading.Tasks as tasks
import Grasshopper.Kernel as gh
import scriptcontext as scriptc

#defualt values
maxHeightDefaultVal = 100
minHeightDefaultVal = -20
defaultNumOfCPUs = 1
inputsDictEnvelope = {
    
0: ["_baseSrf", "A surface representing the area for which you want to create the solar envelope."],
1: ["_obstacleCrvs", "List of curves indicating the bottom borders of our surroundings that are taken into account in calculating the solar envelope."],
2: ["_sunVectors", "Sun vectors representing hours of the year when sun should be accessible to the properties surrounding the baseSrf.  sunVectors can be generated using the Ladybug sunPath component."],
3: ["gridSize_", "A numeric value inidcating the gird size of the analysis in Rhino model units. The smaller the grid size - the more test points( more accurate but slower). Default value is automatically set based on the size of the input _baseSrf."],
4: ["maxHeight_", "If there are no obstrucsions, this would be the heighest value for the solar envelope points. The default value set to 100 meters above the average baseSrf height."],
5: ["envelopeToRun_", "Set to 'True' if you would like the component to calculate a solar rights boundary and 'False' if you would like a solar collection boundary.  The default is set to solar envelope."],
6: ["_numOfCPUs_", "Number of CPUs to be used for the simulation. Default value would be " + str(defaultNumOfCPUs)],
7: ["_runIt", "Set to 'True' to run the component and generate solar envelope points."]
}

inputsDictCollection = {
    
0: ["_baseSrf", "A surface representing the area for which you want to create the solar envelope."],
1: ["_obstacleCrvs", "List of curves indicating the top borders of our surroundings that are taken into account in calculating the solar collection."],
2: ["_sunVectors", "Sun vectors representing hours of the year when sun should be accessible to the properties surrounding the baseSrf.  sunVectors can be generated using the Ladybug sunPath component."],
3: ["gridSize_", "A numeric value inidcating the gird size of the analysis in Rhino model units. The smaller the grid size - the more test points( more accurate but slower). Default value is automatically set based on the size of the input _baseSrf."],
4: ["maxHeight_", "If there are no obstrucsions this would be the lowest value for the solar collection points. Default value set to 20 meters below the average baseSrf height."],
5: ["envelopeToRun_", "Set to 'True' if you would like the component to calculate a solar rights boundary and 'False' if you would like a solar collection boundary.  The default is set to solar envelope."],
6: ["_numOfCPUs_", "Number of CPUs to be used for the simulation. Default value would be " + str(defaultNumOfCPUs)],
7: ["_runIt", "Set to 'True' to run the component and generate solar collection points."]
}

outputsDictEnvelope = {
    
0: ["readMe!", "Log of the component."],
1: ["envelopePts", "A list of 3d points representing the heights to which the solar envelope reaches.  Plug into a native GH 'Delunay Mesh' component to visualize the full solar envelope."],
2: ["envelopeBrep", "The closed volume in which you can build that will not shade the surrounding obstacleCrvs from the input sunVectors."]
}

outputsDictCollect = {
    
0: ["readMe!", "Log of the component."],
1: ["envelopePts", "A list of 3d points representing the heights to which the solar collection reaches.  Plug into a native GH 'Delunay Mesh' component to visualize the full solar collection boundary."],
2: ["envelopeBrep", "The closed volume in which you can build above which the building will have direct solar access to the input sunVectors."]
}
def issueWarning(message,boolToReturn = False):
    print message
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, message)
    return boolToReturn
#allDataProvided - boolean. if even before we run this function not all data is provided then we'll resutnr false either way but also would
# add the messages is something in the units is also problematic
def calculateModelUnits(allDataProvided):
    units = scriptc.doc.ModelUnitSystem
    unitsTxt = str(units).split('.')[-1]
    if `units` == 'Rhino.UnitSystem.Meters': conversionFactor = 1.00
    elif `units` == 'Rhino.UnitSystem.Centimeters': conversionFactor = 0.01
    elif `units` == 'Rhino.UnitSystem.Millimeters': conversionFactor = 0.001
    elif `units` == 'Rhino.UnitSystem.Feet': conversionFactor = 0.305
    elif `units` == 'Rhino.UnitSystem.Inches': conversionFactor = 0.0254
    else:
        issueWarning("You're Kidding me! Which units are you using?"+ unitsTxt + "?")
        allDataProvided = issueWarning("Please use Meters, Centimeters, Millimeters, Inches or Feet")
    return allDataProvided, units , unitsTxt, conversionFactor
def collectInputOutput():
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(8):
        ghenv.Component.Params.Input[input].NickName = inputsDictCollection[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDictCollection[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDictCollection[input][1]
    for output in range(3):
        ghenv.Component.Params.Output[output].NickName = outputsDictCollect[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDictCollect[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDictCollect[output][1]

def restoreInputOutput():
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(8):
        ghenv.Component.Params.Input[input].NickName = inputsDictEnvelope[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDictEnvelope[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDictEnvelope[input][1]
    for output in range(3):
        ghenv.Component.Params.Output[output].NickName = outputsDictEnvelope[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDictEnvelope[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDictEnvelope[output][1]
        
def computeGridSize(baseSrf):
    baseSrfBB = Rhino.Geometry.Brep.GetBoundingBox(baseSrf, Rhino.Geometry.Plane.WorldXY)
    baseSrfBB = Rhino.Geometry.Box(baseSrfBB)
    baseSrfBBDim = [baseSrfBB.X[1]-baseSrfBB.X[0], baseSrfBB.Y[1]-baseSrfBB.Y[0], baseSrfBB.Z[1]-baseSrfBB.Z[0]]
    gridSizeInit = baseSrfBBDim[1]/5
    gridsize = round(gridSizeInit, 4)
    return gridsize

class SolarEnvelope:
    def __init__(self,_baseSrf,gridSize,obstacleCurves,sunVectors, defaultHeight,numOfCPUs_,_solarEnvelope = True) :
        self._solarEnvelope = _solarEnvelope # true for solar envelope and false for solar collection
        self.defaultHeight = self.computeHeightWithBaseSrf(defaultHeight,_baseSrf)
        self.suns = []
        self.gridPoints = []
        self.finalPointsList = []
        self.chunks = []
        self.NumOfThreads = numOfCPUs_
        #this is the minimum angle under which we consider the sun - below that angle 
        #(between the sun vector and the obstacle curve) we act as if the sun vector isn't relevant
        #currently not in use, WIP
        marginAngle = 20
        if self._solarEnvelope:
            self.lineExtention = 1000 #positive number means were going forward (for use in solar rights envelope)
        else:
            self.lineExtention = -1000 #negative number means we're going back to the sun (for use in solar collection envelope)
        #we don't care if the angle is very big or very small so we get the sin of it - TODO - make this work
        marginAngle = math.sin(math.radians(marginAngle))
        self.obstacleCurves = obstacleCurves
        self.buildSunPosList(sunVectors)
        self.getPtsFromClosedCrv(_baseSrf,gridSize)
        self.parallelFindPointHeights()
    def computeHeightWithBaseSrf(self,defaultHeight,baseSf):
        baseSrfBB = Rhino.Geometry.Brep.GetBoundingBox(baseSf, Rhino.Geometry.Plane.WorldXY)
        baseSrfHeight = baseSrfBB.Center.Z
        defaultHeightFinal = baseSrfHeight + defaultHeight
        return defaultHeightFinal
    def buildSunPosList(self,sunVectors):
        azimuthAngles = []
        alltitudeAngles = []
        for vec in sunVectors:
            baseVec = Rhino.Geometry.Vector3d(vec.X, vec.Y, 0)
            alt = math.degrees(Rhino.Geometry.Vector3d.VectorAngle(vec, baseVec))
            if vec.X < 0.0: az = math.degrees(Rhino.Geometry.Vector3d.VectorAngle(vec, Rhino.Geometry.Vector3d.YAxis, Rhino.Geometry.Plane.WorldXY)) - 180
            else: az = math.degrees(Rhino.Geometry.Vector3d.VectorAngle(vec, Rhino.Geometry.Vector3d.YAxis, Rhino.Geometry.Plane.WorldXY)) + 180
            azimuthAngles.append(az)
            alltitudeAngles.append(alt)
        for (i, _azimuthAngle) in enumerate(azimuthAngles):
            self.suns.Add(SingleSun(alltitudeAngles[i], _azimuthAngle))

    def parallelFindPointHeights(self):
        
        def _findPointsHeight(i):
            chunk = self.chunks[i]
            for x in range(len(chunk.points)):
                g = chunk.points[x]
                for y in range(len(chunk.obstacleCurves)):
                    obCurve = chunk.obstacleCurves[y]
                    #not using this for now
                    #lineAngles = getLineEdgeAngles(obCurve,checkPoint,yVector)
                    for j in range(len(chunk.suns)):
                        tempHeight = g.getPointHeight(obCurve, chunk.suns[j])
                        if self._solarEnvelope : 
                            if  tempHeight < g.point.Z : 
                                g.point.Z = tempHeight
                        else :
                            if  tempHeight > g.point.Z : 
                                g.point.Z = tempHeight
                            
        #split an array into equeal size chunks, the last item will contain the remaining elements
        itemsInEveryChunk = int(math.ceil(len(self.gridPoints) / self.NumOfThreads))
        splittedPoints = [self.gridPoints[i:i+itemsInEveryChunk] for i in range(0,len(self.gridPoints),itemsInEveryChunk)]
        #divide to chunks and run every chunk as a thread
        self.chunks = []    #do we really need this?
        for i in range(self.NumOfThreads):
            self.chunks.append(ParallelChunkObject(copy.deepcopy(splittedPoints[i]),copy.deepcopy(self.suns), copy.deepcopy(self.obstacleCurves)))
        tasks.Parallel.ForEach(xrange(self.NumOfThreads),_findPointsHeight)
        self.gridPoints = []
        for pointChunk in self.chunks:
            self.gridPoints.extend(pointChunk.points)    
    def getPtsFromClosedCrv(self,srf,gridSize):
        regionMeshPar = Rhino.Geometry.MeshingParameters.Default
        regionMeshPar.MinimumEdgeLength = regionMeshPar.MaximumEdgeLength = gridSize/2
        self.regionMesh = Rhino.Geometry.Mesh.CreateFromBrep(srf, regionMeshPar)[0]
        vertices = self.regionMesh.Vertices
        for item in vertices:
            g = GridPt(Rhino.Geometry.Point3d(item),self.defaultHeight,self)
            self.gridPoints.Add(g)
    def computeFinalSolarVol(self):
        #Change the vertex heights of the initial mesh.
        finalPoints = []
        for vertexCount, gridPt in enumerate(self.gridPoints):
            self.regionMesh.Vertices[vertexCount] = Rhino.Geometry.Point3f(gridPt.point.X, gridPt.point.Y, gridPt.point.Z)
            finalPoints.Add(gridPt.point)
        finalEnvelopeBrep = Rhino.Geometry.Brep.CreateFromMesh(self.regionMesh,True)
        return finalEnvelopeBrep, finalPoints
#divide our point array that we need to calculate to several subarrays and calculate every subarray in multithreading
# seems like when we're doing multithreading, a race condition can occour even on just reading data so copy all the data
#for every subarray and wrap it in an object
class ParallelChunkObject:
    def __init__(self,points,_suns, _obstacleCurves) :
        self.points = points
        self.suns = _suns
        self.obstacleCurves = _obstacleCurves
class GridPt:
    def __init__(self, point, defaultHeight,mainRef):
        self.point = point
        self.point.Z = defaultHeight
        self.defaultHeight = defaultHeight
        self.mainRef = mainRef
        self.isStart = False        
    #handle all the logic and return the z (height) of the relevant point for one specified obstacle line
    #if the z value is lower than what we had replace it (because the lowest one is the relevant one)
    def getPointHeight(self, bLine, singleSun):
        self.initialHeight = bLine.PointAtEnd.Z
        _checkPoint = Rhino.Geometry.Point2d(self.point.X,self.point.Y)
        xAdd = - self.mainRef.lineExtention * math.sin(math.radians(singleSun.azimuth));
        yAdd = - self.mainRef.lineExtention * math.cos(math.radians(singleSun.azimuth)); 
        point1 = Rhino.Geometry.Point3d( self.point.X,self.point.Y,self.initialHeight )
        point2 = Rhino.Geometry.Point3d( self.point.X + xAdd,self.point.Y + yAdd,self.initialHeight)
        _sunLine = Rhino.Geometry.LineCurve(point1,point2)       
        _intersections = Rhino.Geometry.Intersect.Intersection.CurveCurve(_sunLine, bLine, 0.001, 0.0)
        if _intersections : 
            _intersectionPoint = Rhino.Geometry.Point2d(_intersections[0].PointA[0],_intersections[0].PointA[1])
            dist = (_intersectionPoint - _checkPoint).Length
            t = math.tan(math.radians(singleSun.alltitude))
            if self.mainRef._solarEnvelope :
                return dist * t + self.initialHeight
            else :
                return self.initialHeight - dist * t 
        else :
            #sun not relevant so no obstacles to look out for - return the heighest(rights)/lowest(collection) point defined
            return self.defaultHeight
#class to organize all the data in a single sun object
#properties for later use, when we'll get more comprehensive data from and epw file - hour, day, month, temperature, radiation
class SingleSun:
    def __init__(self, _alltitude, _azimuth):
        self.alltitude = _alltitude
        self.azimuth = _azimuth

if envelopeToRun_: restoreInputOutput()
else: collectInputOutput()

if _runIt == True:
    #if we want to use it (for debugging externally with pydev we need to define and set the debug variable to True
    #if debug:
    #    import pydevd as py
    #    py.settrace()
    allDataProvided = True
    if not _baseSrf :
        allDataProvided = issueWarning("Base surface must be provided")
    if len(_sunVectors) == 0:
        allDataProvided = issueWarning("A list of sun vectors from ladybug must be provided")        
    if gridSize_ != None and gridSize_<=0:
        allDataProvided = issueWarning("gridSize_ must be greater than or equal to zero")
    allDataProvided, units, unitsTxt, conversionFactor = calculateModelUnits(allDataProvided)
    
    #solar rights envelope specific conditions that must be met
    if envelopeToRun_ : 
        if maxHeight_ != None and maxHeight_< 0:
            allDataProvided = issueWarning("maxHeight_ must be greater than or equal to zero")
    #solar collection specific conditions that must be met
    else : 
        if not _obstacleCrvs:
            allDataProvided = issueWarning("Top obstacle curves must be provided")
        if maxHeight_ != None and maxHeight_ > 0:
            allDataProvided = issueWarning("maxHeight_ must be smaller than or equal to zero")

    if allDataProvided:
        print "Starting simulation"
        if not gridSize_ : 
            gridSize_ = computeGridSize(_baseSrf)
            print "No gridSize provided. Grid size automatically set to " + str(gridSize_) + " " + unitsTxt + " based on the size of tha _baseSrf."
        #let the default value be 1, at least for now, maybe later on calculate availible cpus and make this automatic
        if not _numOfCPUs_ : 
            _numOfCPUs_ = defaultNumOfCPUs
            print "No number of availible CPUs provided. Using the default value of  " + str(defaultNumOfCPUs)
        #solar rights envelope specific parameters, tests and settings
        if envelopeToRun_:
            if maxHeight_ == None :
                maxHeight_ = maxHeightDefaultVal / conversionFactor
                print "No height provided, using the default value of " + str(maxHeightDefaultVal) + " meters above the baseSrf height."
            if not _obstacleCrvs :
                print "No top obstacle curves selected, taking the base surface as the solar envelope border"
                _obstacleCrvs = []
                for crv in _baseSrf.Curves3D:   _obstacleCrvs.append(crv)
        #solar collection specific parameters, tests and settings
        else:
            if maxHeight_ == None:
                maxHeight_ = minHeightDefaultVal / conversionFactor
                print "No height provided, using the default value of " + str(minHeightDefaultVal) + " meters above the baseSrf height."         
        se = SolarEnvelope(_baseSrf,gridSize_,_obstacleCrvs, _sunVectors, maxHeight_,_numOfCPUs_,envelopeToRun_)
        envelopeBrep, envelopePts = se.computeFinalSolarVol()
else:
    print "To run the component, set _runIt to True"
ghenv.Component.Params.Output[1].Hidden = True