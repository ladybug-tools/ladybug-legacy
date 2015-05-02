# Solar Envelope
# Provides an envelope (as a list of points) which represents the area in which new masses could be placed withought
# interfering with the sun rights of surrounding buildings, given a filtered list of suns
# By Boris Plotnikov with the assistance and guidance of Prof. Guedi Capeluto
# pborisp@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
"""
Use this component to generate a solar envelope for a given test surface, set of solar vectors, and context geometry that you want to ensure solar access to.  Solar envelopes are typically used to illustrate the volume that can be built within in order to ensure that a new development does not shade the surrounding properties for a given set of sun vectors.

-
Provided by Ladybug 0.0.59
    
    Args:
        _baseSrf: A surface representing the area for which you want to create the solar envelope.
        _obstacleCurves: A list of curves indicating the bottom borders of your surroundings for which you would like solar access to be kept.
        _sunVectors: Sun vectors representing hours of the year when sun should be accessible to the properties surrounding the baseSrf.  sunVectors can be generated using the Ladybug sunPath component. 
        _gridSize: An numeric value inidcating the gird size of the analysis in Rhino model units. The smaller the grid size - the more test points( more accurate but slower).
        _runIt: Set to True to run the component and generate a solar envelope.
    Returns:
        readMe!:Log of the component
        finalPointList: A list of points representing the heights to which you can build without shading any of the _obstacleCurves from the input _sunVectors.
        total_ms: The time that it took this component to run
"""
ghenv.Component.Name = 'Ladybug_SolarEnvelopeAdvanced'
ghenv.Component.NickName = 'SolarEnvelopeAdvanced'
ghenv.Component.Message = 'VER 0.0.59\nMAY_02_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import time, math, Rhino
import System.Threading.Tasks as tasks

def computeAzAltFromSunVec(sunVectors):
    azimuthAngles = []
    alltitudeAngles = []
    for vec in sunVectors:
        baseVec = Rhino.Geometry.Vector3d(vec.X, vec.Y, 0)
        alt = math.degrees(Rhino.Geometry.Vector3d.VectorAngle(vec, baseVec))
        if vec.X < 0.0: az = math.degrees(Rhino.Geometry.Vector3d.VectorAngle(vec, Rhino.Geometry.Vector3d.YAxis, Rhino.Geometry.Plane.WorldXY)) - 180
        else: az = math.degrees(Rhino.Geometry.Vector3d.VectorAngle(vec, Rhino.Geometry.Vector3d.YAxis, Rhino.Geometry.Plane.WorldXY)) + 180
        azimuthAngles.append(az)
        alltitudeAngles.append(alt)
    
    return azimuthAngles, alltitudeAngles

class SolarEnvelope:    
    solarEnvelope = True 
    def initParameters(self):
        self.suns = []
        self.gridPoints = []
        self.finalPointsList = []
        #this is the minimum angle under which we consider the sun - below that angle 
        #(between the sun vector and the obstacle curve) we act as if the sun vector isn't relevant
        #currently not in use, WIP
        marginAngle = 20
        if self.solarEnvelope:
            self.lineExtention = 1000 #positive number means were going forward (for use in solar envelope)
            #initial height of the point In solar envelope set it to the max height that we'll have if no obstacles
            #are there and go down from there in solar access it opposite
            self.defaultHeight = 100
        else:
            self.lineExtention = -1000 #negative number means we're going back to the sun (for use in solar access)
            self.defaultHeight = -100
        #we don't care if the angle is very big or very small so we get the sin of it - TODO - make this actually work!!
        marginAngle = math.sin(math.radians(marginAngle))

    def buildSunPosList(self,_azimuthAngles, _alltitudeAngles):
        for (i, _azimuthAngle) in enumerate(_azimuthAngles):
            self.suns.Add(SingleSun(_alltitudeAngles[i], _azimuthAngle))

    def parallelFindPointHeights(self,checkPointList,obstacleCurves):
        
        def _findPointHeight(i):
            g = GridPt(checkPointList[i],self.defaultHeight,self)
            self.gridPoints.Add(g)
            for obCurve in obstacleCurves:
                #not using this for now
                #lineAngles = getLineEdgeAngles(obCurve,checkPoint,yVector)
                for sun in self.suns:
                    tempHeight = g.getPointHeight(obCurve, sun)
                    if self.solarEnvelope : 
                        if  tempHeight < g.height : 
                            g.height = tempHeight
                    else :
                        if  tempHeight > g.height : 
                            g.height = tempHeight
        tasks.Parallel.ForEach(xrange(len(checkPointList)),_findPointHeight)
    
    def __init__(self,_baseSrf,_gridSize,obstacleCurves,azimuthAngles, alltitudeAngles):
        self.initParameters()
        self.buildSunPosList(azimuthAngles, alltitudeAngles)
        self.getPtsFromClosedCrv(_baseSrf,_gridSize)
        self.parallelFindPointHeights(self.checkPointList, obstacleCurves)
    
    def getFinalPointList(self):
        for gridPt in self.gridPoints:
            self.finalPointsList.Add(gridPt.buildFinalPoint())
        return self.finalPointsList
    def getPtsFromClosedCrv(self,srf,gridSize):
        regionMeshPar = Rhino.Geometry.MeshingParameters.Default
        regionMeshPar.MinimumEdgeLength = regionMeshPar.MaximumEdgeLength = gridSize/2
        regionMesh = Rhino.Geometry.Mesh.CreateFromBrep(srf, regionMeshPar)[0]
        vertices = regionMesh.Vertices
        self.checkPointList = []
        for item in vertices:
            self.checkPointList.append(Rhino.Geometry.Point3d(item))
class GridPt:
    def __init__(self, point, defaultHeight,mainRef):
        self.point = point
        self.defaultHeight = self.height = defaultHeight
        self.mainRef = mainRef
        self.isStart = False        
    #handle all the logic and return the z (height) of the relevant point for one specified obstacle line
    #if the z value is lower than what we had replace it (because the lowest one is the relevant one)
    def getPointHeight(self, bLine, singleSun):
        self.initialHeight = bLine.PointAtEnd.Z
        _checkPoint = Rhino.Geometry.Point2d(self.point[0],self.point[1])
        xAdd = - self.mainRef.lineExtention * math.sin(math.radians(singleSun.azimuth));
        yAdd = - self.mainRef.lineExtention * math.cos(math.radians(singleSun.azimuth)); 
        point1 = Rhino.Geometry.Point3d( self.point[0],self.point[1],self.initialHeight )
        point2 = Rhino.Geometry.Point3d( self.point[0] + xAdd,self.point[1] + yAdd,self.initialHeight)
        _sunLine = Rhino.Geometry.LineCurve(point1,point2)       
        _intersections = Rhino.Geometry.Intersect.Intersection.CurveCurve(_sunLine, bLine, 0.001, 0.0)
        if _intersections : 
            _intersectionPoint = Rhino.Geometry.Point2d(_intersections[0].PointA[0],_intersections[0].PointA[1])
            dist = (_intersectionPoint - _checkPoint).Length
            t = math.tan(math.radians(singleSun.alltitude))
            return dist * t + self.initialHeight
        else :
            #sun not relevant so no obstacles to look out for - return the heighest point defined
            return self.defaultHeight + self.initialHeight
    
    def buildFinalPoint(self):
        self.finalPoint = Rhino.Geometry.Point3d(self.point[0],self.point[1],self.height) 
        return self.finalPoint
#class to organize all the data in a single sun object
#properties for later use, when we'll get more comprehensive data from and epw file - hour, day, month, temperature, radiation
class SingleSun:
    def __init__(self, _alltitude, _azimuth):
        self.alltitude = _alltitude
        self.azimuth = _azimuth

if _runIt:
    #if we want to use it (for debugging externally with pydev we need to define and set the debug variable to True
    #if debug:
    #    import pydevd as py
    #    py.settrace()
    start = time.clock()
    azimuthAngles, alltitudeAngles = computeAzAltFromSunVec(_sunVectors)
    se = SolarEnvelope(_baseSrf,_gridSize,_obstacleCurves, azimuthAngles,alltitudeAngles)
    finalPointList =se.getFinalPointList()
    total_ms = time.clock() - start
    print "[Main] - starting solar envelope simulation"
else:
    print "not running"