# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component draws shading mask for a test point
The component is intented to be used with sunPath
-
Provided by Ladybug 0.0.52
    
    Args:
        pt: Test point
        context: Context buildings
        scale: Scale of the sky dome
        
    Returns:
        masked: Shadow mask
        percMasked: Percentage of the sky masked
"""

ghenv.Component.Name = "Ladybug_Shading Mask"
ghenv.Component.NickName = 'shadingMask'
ghenv.Component.Message = 'VER 0.0.52\nNOV_01_2013'

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import Rhino as rc
import math
import scriptcontext as sc
import System.Threading.Tasks as tasks

def generateSkyGeo(cenPt, skyType = 2, scale = 200):
    # this script is based of the Treganza 
    
    # number of segments in each row of the sky
    # 15 rows - total 580
    
    originalNumSeg = 7 * [48]
    
    if skyType==0: numSeg = originalNumSeg + [1]
    else:
        numSeg =[]
        for numOfSeg in originalNumSeg:
            for i in range(skyType+1):
                numSeg.append(numOfSeg * (skyType+1))
        numSeg = numSeg + [1]
    
    # rotation line axis
    lineVector = rc.Geometry.Vector3d.ZAxis
    lineVector.Reverse()
    lineAxis = rc.Geometry.Line(cenPt, lineVector)
    
    # base plane to draw the arcs
    basePlane = rc.Geometry.Plane(cenPt, rc.Geometry.Vector3d.XAxis)
    baseVector = rc.Geometry.Vector3d.YAxis
    
    # 29 is the total number of devisions 14 + 1 + 14
    eachSegVerticalAngle = (math.pi)/ (2 * len(numSeg) - 1)/2
    
    skyPatches = []
    for row in range(len(numSeg)):
        # create the base arc
        stPt = rc.Geometry.Point3d.Add(cenPt, scale* baseVector)
        
        if row == len(numSeg)-1:
            eachSegVerticalAngle = eachSegVerticalAngle/2
            
        baseVector.Rotate(eachSegVerticalAngle, rc.Geometry.Vector3d.XAxis)
        midPt = rc.Geometry.Point3d.Add(cenPt, scale* baseVector) 
        
        baseVector.Rotate(eachSegVerticalAngle, rc.Geometry.Vector3d.XAxis)
        endPt = rc.Geometry.Point3d.Add(cenPt, scale* baseVector) 
        
        baseArc = rc.Geometry.Arc(stPt, midPt, endPt).ToNurbsCurve()
        
        # create the row
        numOfSeg = numSeg[row]
        angleDiv = 2 * math.pi / numOfSeg
        
        for patchNum in range(numOfSeg):
            start_angle = (patchNum * angleDiv) #-(angleDiv/2)
            end_angle = ((patchNum + 1) * angleDiv) #- (angleDiv/2)
                
            patch = rc.Geometry.RevSurface.Create(baseArc, lineAxis, start_angle, end_angle).ToBrep()
            skyPatches.append(patch)
        
    return skyPatches


def parallelIntersection(testPt, joinedContext, testSurfaces):
    """
    testPt: center point
    context: context as a joined mesh
    testSurfaces: in this case sky patches are used to find the vectors
    it could be replaces by test vectors
    """
    
    def getRayVector(brep, testPt):
        MP = rc.Geometry.AreaMassProperties.Compute(brep)
        centerPt = MP.Centroid
        vector = rc.Geometry.Vector3d(centerPt - testPt)
        return vector
    
    
    numOfSrf = len(testSurfaces)
    masked = range(numOfSrf)
    
    # run the intersection
    def intersect(i):
        try:
            # find centerPoint and normal
            normalVector = getRayVector(testSurfaces[i], testPt)
            # create the meshRay
            ray = rc.Geometry.Ray3d(testPt, normalVector)
            # run the intersection
            if rc.Geometry.Intersect.Intersection.MeshRay(joinedContext, ray) >= 0.0:
                masked[i] = 1
            else:
                masked[i] = 0
        except Exception, e:
            print `e`
    
    tasks.Parallel.ForEach(range(numOfSrf), intersect)
    
    #lines = []
    #for i, testSurface in enumerate(testSurfaces):
    #    # find centerPoint and normal
    #    normalVector = getRayVector(testSurface, testPt)
    #    lines.append(rc.Geometry.Line(testPt, rc.Geometry.Point3d.Add(testPt, 200* normalVector)))
    #    # create the meshRay
    #    ray = rc.Geometry.Ray3d(testPt, normalVector)
    #    # run the intersection
    #    if rc.Geometry.Intersect.Intersection.MeshRay(joinedContext, ray) < 0.0:
    #        masked[i] = 0
    #    else:
    #        masked[i] = 1
    
    # return intersection result
    return masked
    
    

def joinMesh(meshList):
    joinedMesh = rc.Geometry.Mesh()
    for m in meshList: joinedMesh.Append(m)
    return joinedMesh

def meshAndJoin(brepList):
    joinedMesh = rc.Geometry.Mesh()
    for brep in brepList:
        meshList = rc.Geometry.Mesh.CreateFromBrep(brep, rc.Geometry.MeshingParameters.Smooth)
        for m in meshList: joinedMesh.Append(m)
    return joinedMesh

def main(testPt, skyDensity, contextMesh, scale):
    
    # generate sky patches
    skyPatches = generateSkyGeo(testPt, skyDensity, scale)
    
    #return skyPatches
    if skyPatches == -1: return
    # join mesh
    joinedContextMesh = joinMesh(contextMesh)
    
    # run parallel intersections
    masked = parallelIntersection(testPt, joinedContextMesh, skyPatches)
    
    # filter breps based on the result
    # the reason I do it separately is to have the dome always on z = 0
    maskedSrfs = []
    testPtProjected = rc.Geometry.Point3d(testPt.X, testPt.Y, 0)
    skyPatches = generateSkyGeo(testPtProjected, skyDensity, scale)
    for i, isMasked in enumerate(masked):
        if isMasked==1:
            maskedSrfs.append(skyPatches[i])
    
    # mesh the patches and calculate the area
    skyMeshed = meshAndJoin(skyPatches)
    maskedMesh = meshAndJoin(maskedSrfs)
    
    maskedArea = rc.Geometry.AreaMassProperties.Compute(maskedMesh).Area
    skyArea = rc.Geometry.AreaMassProperties.Compute(skyMeshed).Area
    
    percentageArea = (maskedArea/skyArea) * 100
    return maskedMesh, "%.2f"%percentageArea

if _testPt and _context and scale_:
    masked, percMasked = main(_testPt, _skyDensity_, _context, 200*scale_)
else:
    print "Either testPt or context is missing"
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Either testPt or context is missing")