# By Mostapha Sadeghipour Roudsari and Chris Mackey
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to see the portion of the sky dome that is masked by context geometry around a given viewpoint.
The component will generate separate meshs for the portions of the sky dome that are masked and visible.
The component will also calculate the percentage of the sky that is masked by the context geometry and the percentage that is visible (the sky view factor).
-
Provided by Ladybug 0.0.58
    
    Args:
        _testPt: A view point for which one wants to see the portion of the sky masked by the context geometry surrounding this point.
        _context: Context geometry surrounding the _testPt that could block the view to the sky.  Geometry must be a Brep or list of Breps.
        _skyDensity_: An integer that is greater than or equal to 0, which to sets the number of times that the Tergenza sky patches are split.  Set to 0 to view a sky mask with the typical Tregenza sky, which will divide up the sky with a coarse density of 145 sky patches.  Set to 1 to view a sky mask of a Reinhart sky, which will divide up each of these Tergenza patches into 4 patches to make a sky with a total of 580 sky patches. Higher numbers input here will ensure a greater accuracy but will also take longer. The default is set to 3 to give you a high accuracy.
        scale: Use this input to change the scale of the sky dome.  The default is set to 1.
        
    Returns:
        masked: A mesh of the portion of the sky dome masked by the _context geometry.
        visible: A mesh of the portion of the sky dome visible by the _testPt through the _context geometry.
        percMasked: The percentage of the sky masked by the _context geometry at the _testPt.
        skyView: The percentage of the sky visible by the _testPt through the _context geometry.
"""

ghenv.Component.Name = "Ladybug_Shading Mask"
ghenv.Component.NickName = 'shadingMask'
ghenv.Component.Message = 'VER 0.0.58\nOCT_01_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Grasshopper.Kernel as gh
import Rhino as rc
import math
import System
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
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
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
        unmaskedSrfs = []
        testPtProjected = rc.Geometry.Point3d(testPt.X, testPt.Y, 0)
        skyPatches = generateSkyGeo(testPtProjected, skyDensity, scale)
        for i, isMasked in enumerate(masked):
            if isMasked==1:
                maskedSrfs.append(skyPatches[i])
            else:
                unmaskedSrfs.append(skyPatches[i])
        
        # mesh the patches and calculate the area
        skyMeshed = meshAndJoin(skyPatches)
        maskedMesh = meshAndJoin(maskedSrfs)
        # change the color to black so the user don't get confused
        #maskedMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
        
        # unmasked area output is added by William Haviland
        unmaskedMesh = meshAndJoin(unmaskedSrfs)
        
        # color the meshes for masked and visible differently.
        meshColor = []
        for face in maskedMesh.Faces:
            meshColor.append(1.0)
        colors = lb_visualization.gradientColor(meshColor, 0, 2, [System.Drawing.Color.FromArgb(1,1,1), System.Drawing.Color.FromArgb(1,1,1)])
        maskedMesh = lb_visualization.colorMesh(colors, maskedMesh)
        
        meshColor = []
        for face in unmaskedMesh.Faces:
            meshColor.append(1.0)
        colors = lb_visualization.gradientColor(meshColor, 0, 2, [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(200,200,255)])
        unmaskedMesh = lb_visualization.colorMesh(colors, unmaskedMesh)
        
        maskedArea = rc.Geometry.AreaMassProperties.Compute(maskedMesh).Area
        skyArea = rc.Geometry.AreaMassProperties.Compute(skyMeshed).Area
        
        percentageArea = (maskedArea/skyArea) * 100
        percentageSky = 100 - percentageArea
        return maskedMesh, "%.2f"%percentageArea, unmaskedMesh, "%.2f"%percentageSky
    else:
        print "You should let the Ladybug fly first..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")
        return -1, -1, -1, -1

if _testPt and _context and scale_:
    results = main(_testPt, _skyDensity_, _context, 200*scale_)
    if results!=-1:
        masked, percMasked, visible, skyView = results
elif _testPt == None and _context == []:
    print "Connect a test point and context geometry."
else:
    print "Either the testPt or the context is missing"
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Either testPt or context is missing")
