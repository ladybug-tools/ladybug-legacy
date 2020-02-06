# Solar Envelope
# Provides two solar envelopes as both a 3d point grid and a polysurface given a filtered list of suns and a border line representing the building site
# The first (Solar Rights envelope) represents the maximum heights in which new masses could be placed in a given site withought interfering with the sun rights of surrounding buildings
# The second (Solar Collection envelope) represents the opposite - the minimum heights from which new developemnt would recieve sun access, given an urban context
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2020, Boris Plotnikov <pborisp@gmail.com> and with the assistance and guidance of Prof. Guedi Capeluto, based on SustArc model
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
Use this component to generate a solar envelope for a given test surface, set of solar vectors,
and context geometry that you want to ensure solar access to.  Solar envelopes are typically used to
illustrate the volume that can be built within in order to ensure that a new development does not
shade the surrounding properties for a given set of sun vectors.

-
Provided by Ladybug 0.0.68
"""

ghenv.Component.Name = 'Ladybug_SolarEnvelope'
ghenv.Component.NickName = 'SolarEnvelope'
ghenv.Component.Message = 'VER 0.0.68\nFEB_06_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = 'LB-Legacy'
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
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
incrementDefaultVal = 1
defaultNumOfCPUs = 1
inputsDictEnvelope = {
    
0: ["_baseSrf", "A surface representing the area for which you want to create the solar envelope."],
1: ["_obstacleCrvs", "List of curves indicating the bottom borders of our surroundings that are taken into account in calculating the solar envelope."],
2: ["context_", "An optional list of existing context shading objects, which already block solar access and therefore permit a higher solar envelope in their 'wake'."],
3: ["_sunVectors", "Sun vectors representing hours of the year when sun should be accessible to the properties surrounding the baseSrf.  sunVectors can be generated using the Ladybug sunPath component."],
4: ["gridSize_", "A numeric value inidcating the gird size of the analysis in Rhino model units. The smaller the grid size - the more test points( more accurate but slower). Default value is automatically set based on the size of the input _baseSrf."],
5: ["maxHeight_", "If there are no obstrucsions, this would be the heighest value for the solar envelope points. The default value set to 100 meters above the average baseSrf height."],
6: ["increment_", "A number for the height at which the vector will be incremented duing context intersection calculations. The default value is 1 meter. Note that this value is only used when context is input."],
7: ["envelopeToRun_", "Set to 'True' if you would like the component to calculate a solar rights boundary and 'False' if you would like a solar collection boundary.  The default is set to solar envelope."],
8: ["_numOfCPUs_", "Number of CPUs to be used for the simulation. Default value would be " + str(defaultNumOfCPUs)],
9: ["_runIt", "Set to 'True' to run the component and generate solar envelope points."]
}

inputsDictCollection = {
    
0: ["_baseSrf", "A surface representing the area for which you want to create the solar envelope."],
1: ["_obstacleCrvs", "List of curves indicating the top borders of our surroundings that are taken into account in calculating the solar collection."],
2: ["context_", "An optional list of existing context shading objects, which already block solar access and therefore permit a higher solar envelope in their 'wake'."],
3: ["_sunVectors", "Sun vectors representing hours of the year when sun should be accessible to the properties surrounding the baseSrf.  sunVectors can be generated using the Ladybug sunPath component."],
4: ["gridSize_", "A numeric value inidcating the gird size of the analysis in Rhino model units. The smaller the grid size - the more test points( more accurate but slower). Default value is automatically set based on the size of the input _baseSrf."],
5: ["maxHeight_", "If there are no obstrucsions this would be the lowest value for the solar collection points. Default value set to 20 meters below the average baseSrf height."],
6: ["increment_", "A number for the height at which the vector will be incremented duing context intersection calculations. The default value is 1 meter. Note that this value is only used when context is input."],
7: ["envelopeToRun_", "Set to 'True' if you would like the component to calculate a solar rights boundary and 'False' if you would like a solar collection boundary.  The default is set to solar envelope."],
8: ["_numOfCPUs_", "Number of CPUs to be used for the simulation. Default value would be " + str(defaultNumOfCPUs)],
9: ["_runIt", "Set to 'True' to run the component and generate solar collection points."]
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


def calculateModelUnits(allDataProvided):
    """Get the Rhino model units.
    
    Args:
        allDataProvided: boolean. If even before we run this function not all
        data is provided then we'll return False either way but also would
        add the messages is something in the units is also problematic.
     """
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
    """If some of the component inputs and outputs are not right, blot them out
    or change them.
    """
    for input in range(10):
        ghenv.Component.Params.Input[input].NickName = inputsDictCollection[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDictCollection[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDictCollection[input][1]
    for output in range(3):
        ghenv.Component.Params.Output[output].NickName = outputsDictCollect[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDictCollect[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDictCollect[output][1]


def restoreInputOutput():
    """If some of the component inputs and outputs are not right, blot them out
    or change them.
    """
    for input in range(10):
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
    """Class for Solar Envelopes.
    
    Properties:
        defaultHeight
        suns
        gridPoints
        finalPointsList
        chunks
        NumOfThreads
        obstacleCurves
        envelopeBrep
        envelopePts
    """
    
    def __init__(self, baseSrf, gridSize, obstacleCurves, sunVectors, context,
                 defaultHeight, increment, numOfCPUs_, _solarEnvelope=True):
        
        # set parameters of the envelope based on the inputs
        self._solarEnvelope = _solarEnvelope # True for solar envelope, False for solar collection
        self.defaultHeight = self.computeHeightWithBaseSrf(defaultHeight ,baseSrf)
        self.increment = increment
        self.suns = []
        self.gridPoints = []
        self.finalPointsList = []
        self.chunks = []
        self.NumOfThreads = numOfCPUs_
        self.obstacleCurves = obstacleCurves
        if len(context) == 0 or context[0] is None:
            self.context = None
        else:
            self.context = Rhino.Geometry.Mesh()
            for mesh in context:
                self.context.Append(mesh)
        
        # get a line length for intersection using the bounding box around all geometry
        all_verts = []
        for crv in obstacleCurves:
            all_verts.extend([crv.Point(i) for i in range(crv.PointCount - 1)])
        all_verts.extend([vert.Location for vert in baseSrf.Vertices])
        allGeoBB = Rhino.Geometry.BoundingBox(all_verts)
        if self._solarEnvelope:
            # positive number means were going forward (for use in solar rights)
            self.lineExtention = allGeoBB.Diagonal.Length
        else:
            # negative number means we're going back to the sun (for use in solar collection)
            self.lineExtention = -allGeoBB.Diagonal.Length
        
        # compute the solar envelope
        self.buildSunPosList(sunVectors)
        self.getPtsFromClosedCrv(baseSrf, gridSize)
        self.parallelFindPointHeights()
    
    def computeHeightWithBaseSrf(self,defaultHeight,baseSf):
        """Get max envelope height accounting for the baseSrfHeight and the defaultHeight."""
        baseSrfBB = Rhino.Geometry.Brep.GetBoundingBox(baseSf, Rhino.Geometry.Plane.WorldXY)
        baseSrfHeight = baseSrfBB.Center.Z
        defaultHeightFinal = baseSrfHeight + defaultHeight
        return defaultHeightFinal
    
    def buildSunPosList(self, sunVectors):
        """Generate altitude and azimuth angles from the sun vectors."""
        azimuthAngles = []
        alltitudeAngles = []
        for vec in sunVectors:
            self.suns.append(SingleSun(vec))
    
    def getPtsFromClosedCrv(self, srf, gridSize):
        """Generate vertices over the base surface by meshing it."""
        regionMeshPar = Rhino.Geometry.MeshingParameters.Default
        regionMeshPar.MinimumEdgeLength = regionMeshPar.MaximumEdgeLength = gridSize / 2
        self.regionMesh = Rhino.Geometry.Mesh.CreateFromBrep(srf, regionMeshPar)[0]
        vertices = self.regionMesh.Vertices
        for item in vertices:
            g = GridPt(Rhino.Geometry.Point3d(item), self.defaultHeight, self)
            self.gridPoints.Add(g)
    
    def parallelFindPointHeights(self):
        """Calculate the max height for each of the grid points."""
        
        def _findPointsHeight(i):
            chunk = self.chunks[i]
            for x in range(len(chunk.points)):
                g = chunk.points[x]
                for y in range(len(chunk.obstacleCurves)):
                    obCurve = chunk.obstacleCurves[y]
                    for j in range(len(chunk.suns)):
                        if self.context is None:
                            tempHeight = g.getPointHeight(obCurve, chunk.suns[j])
                        else:
                            tempHeight = g.getPointHeightContext(obCurve, chunk.suns[j])
                        if self._solarEnvelope : 
                            if  tempHeight < g.point.Z : 
                                g.point.Z = tempHeight
                        else :
                            if  tempHeight > g.point.Z : 
                                g.point.Z = tempHeight
        
        # split the array of points into equeal size chunks, the last item will contain the remaining elements
        itemsInEveryChunk = int(math.ceil(len(self.gridPoints) / self.NumOfThreads))
        splittedPoints = [self.gridPoints[i:i+itemsInEveryChunk]
                          for i in range(0, len(self.gridPoints), itemsInEveryChunk)]
        self.chunks = []
        for i in range(self.NumOfThreads):
            self.chunks.append(ParallelChunkObject(copy.deepcopy(splittedPoints[i]),
                copy.deepcopy(self.suns), copy.deepcopy(self.obstacleCurves)))
        
        # Run every chunk on its own thread
        tasks.Parallel.ForEach(xrange(self.NumOfThreads), _findPointsHeight)
        self.gridPoints = []
        for pointChunk in self.chunks:
            self.gridPoints.extend(pointChunk.points)
    
    def computeFinalSolarVol(self):
        """Change the vertex heights of the initial mesh to yields a final envelope mesh."""
        finalPoints = []
        for vertexCount, gridPt in enumerate(self.gridPoints):
            self.regionMesh.Vertices[vertexCount] = \
                Rhino.Geometry.Point3f(gridPt.point.X, gridPt.point.Y, gridPt.point.Z)
            finalPoints.Add(gridPt.point)
        finalEnvelopeBrep = Rhino.Geometry.Brep.CreateFromMesh(self.regionMesh,True)
        return finalEnvelopeBrep, finalPoints


class ParallelChunkObject:
    """The point array of input meshes to test is divided into spearate ParallelChunkObjects
    such that each object can be run independently on its own thread. Otherwise,
    a race condition can occour even from just reading the same data from each thread.
    """
    
    def __init__(self,points,_suns, _obstacleCurves):
        self.points = points
        self.suns = _suns
        self.obstacleCurves = _obstacleCurves


class GridPt:
    def __init__(self, point, defaultHeight, mainRef):
        self.point = point
        self.point.Z = defaultHeight
        self.defaultHeight = defaultHeight
        self.mainRef = mainRef
        self.isStart = False
    
    def getPointHeight(self, bLine, singleSun):
        """Calculate the z (height) of the point for one specified obstacle polyline.
        
        Args:
            bLine: The boundary polyline of the shape to protect.
            singleSun: The sun position that is bein evaluated.
        """
        
        self.initialHeight = bLine.PointAtEnd.Z
        _checkPoint = Rhino.Geometry.Point2d(self.point.X, self.point.Y)
        xAdd = - self.mainRef.lineExtention * math.sin(singleSun.azimuth)
        yAdd = - self.mainRef.lineExtention * math.cos(singleSun.azimuth)
        point1 = Rhino.Geometry.Point3d(self.point.X, self.point.Y, self.initialHeight)
        point2 = Rhino.Geometry.Point3d(self.point.X + xAdd, self.point.Y + yAdd, self.initialHeight)
        _sunLine = Rhino.Geometry.LineCurve(point1, point2)       
        _intersections = Rhino.Geometry.Intersect.Intersection.CurveCurve(_sunLine, bLine, 0.001, 0.0)
        
        if _intersections:
            _intersectionPoint = Rhino.Geometry.Point2d(_intersections[0].PointA[0], _intersections[0].PointA[1])
            dist = (_intersectionPoint - _checkPoint).Length
            t = math.tan(singleSun.alltitude)
            if self.mainRef._solarEnvelope:  # solar rights
                return dist * t + self.initialHeight
            else:  # solar collection
                return self.initialHeight - dist * t 
        else:
            # sun not relevant so no obstacles to look out for
            # return the heighest(rights) or lowest(collection) point defined
            return self.defaultHeight
    
    def getPointHeightContext(self, bLine, singleSun):
        """Calculate the z (height) of the point accounting for context geometry.
        
        Args:
            bLine: The boundary polyline of the shape to protect.
            singleSun: The sun position that is bein evaluated.
        """
        initial_height = self.getPointHeight(bLine, singleSun)
        if initial_height == self.defaultHeight:  # sun not relevant
            return initial_height
        
        ray = Rhino.Geometry.Ray3d(
            Rhino.Geometry.Point3d(self.point.X, self.point.Y, initial_height),
            singleSun.sun_vector)
        _intersections = Rhino.Geometry.Intersect.Intersection.MeshRay(self.mainRef.context, ray)
        if _intersections == -1:
            # No intersection with context. The original height is correct.
            return initial_height
        
        # incrementally move the point until it clears the context.
        num_moves = int((self.defaultHeight - initial_height) / self.mainRef.increment)
        for i in range(num_moves):
            initial_height += self.mainRef.increment
            new_pt = Rhino.Geometry.Point3d(self.point.X, self.point.Y, initial_height)
            new_ray = Rhino.Geometry.Ray3d(new_pt, singleSun.sun_vector)
            _inters = Rhino.Geometry.Intersect.Intersection.MeshRay(self.mainRef.context, new_ray)
            if _inters == -1:
                return initial_height
        return initial_height


class SingleSun:
    """Class to hold the altitue and azimuth data of a sun position."""
    
    def __init__(self, vec):
        self.sun_vector = vec
        
        baseVec = Rhino.Geometry.Vector3d(vec.X, vec.Y, 0)
        self.alltitude = Rhino.Geometry.Vector3d.VectorAngle(vec, baseVec)
        if vec.X < 0.0:
            self.azimuth = Rhino.Geometry.Vector3d.VectorAngle(
                vec, Rhino.Geometry.Vector3d.YAxis, Rhino.Geometry.Plane.WorldXY) - math.pi
        else:
            self.azimuth = Rhino.Geometry.Vector3d.VectorAngle(
                vec, Rhino.Geometry.Vector3d.YAxis, Rhino.Geometry.Plane.WorldXY) + math.pi


if envelopeToRun_: restoreInputOutput()
else: collectInputOutput()


if _runIt == True:
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
        if not gridSize_: 
            gridSize_ = computeGridSize(_baseSrf)
            print "No gridSize provided. Grid size automatically set to " + str(gridSize_) + " " + unitsTxt + " based on the size of tha _baseSrf."
        
        if not _numOfCPUs_ :  # let the default number of CPUs be 1
            _numOfCPUs_ = defaultNumOfCPUs
            print "No number of availible CPUs provided. Using the default value of  " + str(defaultNumOfCPUs)
        
        if envelopeToRun_:  #solar rights envelope specific parameters, tests and settings
            if maxHeight_ is None:
                maxHeight_ = maxHeightDefaultVal / conversionFactor
                print "No height provided, using the default value of " + str(maxHeightDefaultVal) + " meters above the baseSrf height."
            if not _obstacleCrvs:
                print "No top obstacle curves selected, taking the base surface as the solar envelope border"
                _obstacleCrvs = []
                for crv in _baseSrf.Curves3D:   _obstacleCrvs.append(crv)
        else:  #solar collection specific parameters, tests and settings
            if maxHeight_ is None:
                maxHeight_ = minHeightDefaultVal / conversionFactor
                print "No height provided, using the default value of " + str(minHeightDefaultVal) + " meters above the baseSrf height."         
        
        if increment_ is None:
            increment_ = incrementDefaultVal / conversionFactor
        
        se = SolarEnvelope(_baseSrf, gridSize_, _obstacleCrvs, _sunVectors, context_,
                           maxHeight_, increment_, _numOfCPUs_, envelopeToRun_)
        envelopeBrep, envelopePts = se.computeFinalSolarVol()
else:
    print "To run the component, set _runIt to True"
ghenv.Component.Params.Output[1].Hidden = True
