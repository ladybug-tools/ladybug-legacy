# This is a revision for shading designer as of January 22 2014
# By Mostapha Sadeghipour Roudsari and Chris Mackey
# Sadeghipour@gmail.com and Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to generate shading breps for any glazed surface or list of glazed surfaces.  The component supports two methods for shading generation.  The first is a simple depth method, which will generate an overhang of the speficied depth (or multiple overhangs if the _numOfShds is increased).  The second method is to input a set of solar vectors from the Sunpath component that should be blocked by the shade.

-
Provided by Ladybug 0.0.57
    
    Args:
        _glzSrf: A Surface or Brep representing a window to be used for shading design.  This can also be a list of Surfaces of Breps.
        _depthOrVector: A number representing the depth of the shade to be generated or a sun vector to be shaded from the _glzSrf.  You can also input lists of depths, which will assign different depths based on cardinal direction.  For example, inputing 4 values for depths will assign each value of the list as follows: item 0 = north depth, item 1 = west depth, item 2 = south depth, item 3 = east depth.  Lists of vectors to be shaded can also be input and shades can be joined together with the mergeVectors_ input.
        _numOfShds: The number of shades to generated for each glazed surface.
        _distBetween: An alternate option to _numOfShds where the input here is the distance in Rhino units between each shade.
        _runIt: Set to "True" to run the component and generate shades.
        optionalShdSrf_: An optional shade surface representing a 2D area under consideration for shading. This input can only be used with the sun vector method.
        optionalPlanes_: An optional plane (or list of planes) representing a 2D area under consideration for shading.  This input can only be used with the sun vector method.
        mergeVectors_: Set to "True" to merge all the shades generated from a list of sun vectors into a single shade. This input can only be used with the sun vector method.
        _horOrVertical_: Set to "True" to generate horizontal shades or "False" to generate vertical shades. You can also input lists of _horOrVertical_ input, which will assign different orientations based on cardinal direction.
        _shdAngle_: A number between -90 and 90 that represents an angle in degrees to rotate the shades.  The default is set to "0" for no rotation.  If you have vertical shades, use this to rotate them towards the South by a certain value in degrees.  If applied to windows facing East or West, tilting the shades like this will let in more winter sun than summer sun.  If you have horizontal shades, use this input to angle shades downward.  You can also put in lists of angles to assign different shade angles to different cardinal directions.
        north_: Input a vector to be used as a true North direction or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
    Returns:
        readMe!:...
        shadingSrfs: Shading surfaces that were generated based on the inputs.
"""
ghenv.Component.Name = 'Ladybug_ShadingDesigner'
ghenv.Component.NickName = 'SHDDesigner'
ghenv.Component.Message = 'VER 0.0.57\nJUL_16_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math

inputsDict = {
     
0: ["_glzSrf", "A Surface or Brep representing a window to be used for shading design.  This can also be a list of Surfaces of Breps."],
1: ["_depthOrVector", "A number representing the depth of the shade to be generated or a sun vector to be shaded from the _glzSrf.  You can also input lists of depths, which will assign different depths based on cardinal direction.  For example, inputing 4 values for depths will assign each value of the list as follows: item 0 = north depth, item 1 = west depth, item 2 = south depth, item 3 = east depth.  Lists of vectors to be shaded can also be input and shades can be joined together with the mergeVectors_ input."],
2: ["_numOfShds", "The number of shades to generated for each glazed surface."],
3: ["_distBetween", "An alternate option to _numOfShds where the input here is the distance in Rhino units between each shade."],
4: ["_runIt", "Set to 'True' to run the component and generate shades."],
5: ["---------------", "---------------"],
6: ["optionalShdSrf_", "An optional shade surface representing a 2D area under consideration for shading. This input can only be used with the sun vector method."],
7: ["optionalPlanes_", "An optional plane (or list of planes) representing a 2D area under consideration for shading.  This input can only be used with the sun vector method."],
8: ["mergeVectors_", "Set to 'True' to merge all the shades generated from a list of sun vectors into a single shade. This input can only be used with the sun vector method."],
9: ["---------------", "---------------"],
10: ["_horOrVertical_", "Set to 'True' to generate horizontal shades or 'False' to generate vertical shades. You can also input lists of _horOrVertical_ input, which will assign different orientations based on cardinal direction."],
11: ["_shdAngle_", "A number between -90 and 90 that represents an angle in degrees to rotate the shades.  The default is set to '0' for no rotation.  If you have vertical shades, use this to rotate them towards the South by a certain value in degrees.  If applied to windows facing East or West, tilting the shades like this will let in more winter sun than summer sun.  If you have horizontal shades, use this input to angle shades downward.  You can also put in lists of angles to assign different shade angles to different cardinal directions."],
12: ["north_", "Input a vector to be used as a true North direction or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees)."]
}

# manage component inputs

numInputs = ghenv.Component.Params.Input.Count
try:
    depthTest = float(_depthOrVector[0])
    method = 0
    
except:
 method = 1

if method == 0:
    for input in range(numInputs):
        if input == 6 or input == 7 or input == 8:
            ghenv.Component.Params.Input[input].NickName = "............................"
            ghenv.Component.Params.Input[input].Name = "............................"
            ghenv.Component.Params.Input[input].Description = " "
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
else:
    for input in range(numInputs):
        if input == 11 or input == 12:
            ghenv.Component.Params.Input[input].NickName = "............................"
            ghenv.Component.Params.Input[input].Name = "............................"
            ghenv.Component.Params.Input[input].Description = " "
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    
ghenv.Component.Attributes.Owner.OnPingDocument()


def checkTheInputs():
    
    if not _glzSrf!=None:
        print "_glzSrf is missing"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "_glzSrf is missing")
        
        return False, [], [], []
    elif not (_depthOrVector and _depthOrVector[0]!=None):
        print " _depthOrVector is missing. You need to either provide a number as a depth or a vector as a sun vector."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, " _depthOrVector is missing. You need to either provide a number as a depth or a vector as a sun vector.")
        return False, [], [], []
    
    try:
        depthTest = float(_depthOrVector[0])
        # If this works, shading is based on depth and not vectors
        # This method only works when there is no optional shading geometries
        depth = _depthOrVector
        method = 0
        sunVectors = []
        
    except:
        # vector are provided
        sunVectors = []
        # create vectors from generic type object
        for v in _depthOrVector:
            sunV = rc.Geometry.Vector3d(v)
            #sunV.Reverse()
            sunVectors.append(sunV)
        method = 1
        depth = None
    
    # check for method 0
    if method == 0 or optionalShdSrf_ or (not optionalShdSrf_ and len(optionalPlanes_)==0) :
        if _distBetween == None and _numOfShds == None:
            print "You need to either provide the distance between the shadings or number of the shadings."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You need to either provide the distance between the shadings or number of the shadings.")
            return False, [], [], []

    return True, method, depth, sunVectors

def projectToPlane(geometry, plane, vector):
    
    def getTransform():
        if plane.ZAxis.IsParallelTo(vector)**2 == 1:
            x = rc.Geometry.Transform.PlanarProjection(plane)
            return x
        elif math.sin(rc.Geometry.Vector3d.VectorAngle(plane.ZAxis,vector)) == 1:
            x = rc.Geometry.Transform.Unset
            return x
        
        originalPlane = plane
        newPlane = rc.Geometry.Plane(originalPlane.Origin, -vector)
    
        z0 = originalPlane.ZAxis
        z1 = newPlane.ZAxis
        angle = rc.Geometry.Vector3d.VectorAngle(z0, z1)
        
        intersect, axis = rc.Geometry.Intersect.Intersection.PlanePlane(originalPlane, newPlane)
        
        if intersect:
            P2 = rc.Geometry.Plane(originalPlane)
            P2.XAxis = axis.UnitTangent
            P2.YAxis = rc.Geometry.Vector3d.CrossProduct(P2.XAxis, P2.ZAxis)
            
            beta = 0.5 * math.pi - angle
            factor = 1.0 / math.sin(beta)
            project = rc.Geometry.Transform.PlanarProjection(newPlane)
            rotate = rc.Geometry.Transform.Rotation(z1, z0, originalPlane.Origin)
            scale = rc.Geometry.Transform.Scale(P2, 1.0, factor, 1.0)
            x = scale * rotate * project
            return x
    
    geometry.Transform(getTransform())
    return geometry

def getOutlineCrvFromSun (geometry, sunVector):
    planeFromSun = rc.Geometry.Plane(rc.Geometry.Point3d.Origin, sunVector)
    
    outlineCrvFromSun = []
    polylines = geometry.GetOutlines(planeFromSun)
    [outlineCrvFromSun.append(pl.ToNurbsCurve()) for pl in polylines]
    
    return outlineCrvFromSun

def isShadingPossible(shadingBorder, baseSurfacePlane, sunVector, lb_preparation, printOut = True):
    # find the points of shadingFace
    crvPoints = lb_preparation.findDiscontinuity(shadingBorder, style = 4)
    
    shadingPts = []
    nonShadingPts = []
    thereIsMorePoint = True
    while len(shadingPts) * len(nonShadingPts) == 0 and thereIsMorePoint:
        # project to point
        for pt in crvPoints:
            projectedPt = projectToPlane(rc.Geometry.Point3d(pt), baseSurfacePlane, sunVector)
            pVector = rc.Geometry.Vector3d(projectedPt - pt)
            if pVector != rc.Geometry.Vector3d(0, 0, 0):
                #print int(math.degrees(rc.Geometry.Vector3d.VectorAngle(sunVector, pVector)))
                if int(round(math.degrees(rc.Geometry.Vector3d.VectorAngle(sunVector, pVector)))) == 0 or pVector.Length < sc.doc.ModelAbsoluteTolerance:
                    shadingPts.append(pt)
                else:
                    nonShadingPts.append(pt)
        
        thereIsMorePoint = False
    
    if len(shadingPts) * len(nonShadingPts) != 0:
        # this is a mixed situation, I need to subdivide toBeShadedFace
        # and run the study for each part of the surface
        # the function ideally can be written as a recursive function
        # but I need to fix the rest of the code and the way I wrote the class
        # for faces which I'll do later
        if printOut:
            print "The shading surface is on both sides of the glazing surface" + \
                "\nMove it to one of the sides and try again!"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "The shading surface is on both sides of the glazing surface\nMove it to one of the sides and try again!")
        return False
        
    elif len(shadingPts)!= 0: return True
    
    elif len(nonShadingPts)!=0: return False


def getSrfPlane(brep):
    cenPt = rc.Geometry.AreaMassProperties.Compute(brep).Centroid
    # sometimes the center point is not in the right place
    cenPt = brep.ClosestPoint(cenPt)
    bool, centerPtU, centerPtV = brep.Faces[0].ClosestPoint(cenPt)
    normalVector = brep.Faces[0].NormalAt(centerPtU, centerPtV)
    return rc.Geometry.Plane(cenPt, normalVector)

def isSrfFacingTheVector(sunV, normalVector):
    sunVRev = rc.Geometry.Vector3d(sunV)
    sunVRev.Reverse()
    #print math.degrees(rc.Geometry.Vector3d.VectorAngle(sunVRev, normalVector))
    if rc.Geometry.Vector3d.VectorAngle(sunVRev, normalVector) < math.pi/2: return True
    else: return False
#mesh the input glazing

def analyzeGlz(glzSrf, distBetween, numOfShds, horOrVertical, lb_visualization, normalVector):
    # find the bounding box
    bbox = glzSrf.GetBoundingBox(True)
    if horOrVertical == None:
        horOrVertical = True
    if numOfShds == None and distBetween == None:
        numOfShds = 1
    
    if numOfShds == 0 or distBetween == 0:
        sortedPlanes = []
    
    elif horOrVertical == True:
        # Horizontal
        #Define a bounding box for use in calculating the number of shades to generate
        minZPt = bbox.Corner(False, True, True)
        minZPt = rc.Geometry.Point3d(minZPt.X, minZPt.Y, minZPt.Z)
        maxZPt = bbox.Corner(False, True, False)
        maxZPt = rc.Geometry.Point3d(maxZPt.X, maxZPt.Y, maxZPt.Z - sc.doc.ModelAbsoluteTolerance)
        centerPt = bbox.Center 
        #glazing hieghts
        glzHeight = minZPt.DistanceTo(maxZPt)
        
        # find number of shadings
        try:
            numOfShd = int(numOfShds)
            shadingHeight = glzHeight/numOfShd
            shadingRemainder = shadingHeight
        except:
            shadingHeight = distBetween
            shadingRemainder = (((glzHeight/distBetween) - math.floor(glzHeight/distBetween))*distBetween)
            if shadingRemainder == 0:
                shadingRemainder = shadingHeight
        
        # find shading base planes
        planeOrigins = []
        planes = []
        X, Y, z = minZPt.X, minZPt.Y, minZPt.Z
        zHeights = rs.frange(minZPt.Z + shadingRemainder, maxZPt.Z + 0.5*sc.doc.ModelAbsoluteTolerance, shadingHeight)
        try:
            for Z in zHeights:
                planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(X, Y, Z), rc.Geometry.Vector3d.ZAxis))
        except:
            # single shading
            planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(maxZPt), rc.Geometry.Vector3d.ZAxis))
        # sort the planes
        sortedPlanes = sorted(planes, key=lambda a: a.Origin.Z)
    
    elif horOrVertical == False:
        # Vertical
        # Define a vector to be used to generate the planes
        planeVec = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
        planeVec.Rotate(1.570796, rc.Geometry.Vector3d.ZAxis)
        
        
        #Define a bounding box for use in calculating the number of shades to generate
        minXYPt = bbox.Corner(True, True, True)
        minXYPt = rc.Geometry.Point3d(minXYPt.X, minXYPt.Y, minXYPt.Z)
        maxXYPt = bbox.Corner(False, False, True)
        maxXYPt = rc.Geometry.Point3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z)
        centerPt = bbox.Center
        
        #Test to be sure that the values are parallel to the correct vector.
        testVec = rc.Geometry.Vector3d.Subtract(rc.Geometry.Vector3d(minXYPt.X, minXYPt.Y, minXYPt.Z), rc.Geometry.Vector3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z))
        if testVec.IsParallelTo(planeVec) == 0:
            minXYPt = bbox.Corner(False, True, True)
            minXYPt = rc.Geometry.Point3d(minXYPt.X, minXYPt.Y, minXYPt.Z)
            maxXYPt = bbox.Corner(True, False, True)
            maxXYPt = rc.Geometry.Point3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z)
        
        #Adjust the points to ensure the creation of the correct number of shades starting from the northernmost side of the window.
        tolVec = rc.Geometry.Vector3d.Subtract(rc.Geometry.Vector3d(minXYPt.X, minXYPt.Y, minXYPt.Z), rc.Geometry.Vector3d(maxXYPt.X, maxXYPt.Y, maxXYPt.Z))
        tolVec.Unitize()
        tolVec = rc.Geometry.Vector3d.Multiply(sc.doc.ModelAbsoluteTolerance*2, tolVec)
        
        if tolVec.X > 0 and  tolVec.Y > 0:
            tolVec = rc.Geometry.Vector3d.Multiply(1, tolVec)
            norOrient = False
        if tolVec.X < 0 and  tolVec.Y > 0:
            tolVec = rc.Geometry.Vector3d.Multiply(1, tolVec)
            norOrient = False
        if tolVec.X < 0 and  tolVec.Y < 0:
            tolVec = rc.Geometry.Vector3d.Multiply(-1, tolVec)
            norOrient = True
        else:
            tolVec = rc.Geometry.Vector3d.Multiply(-1, tolVec)
            norOrient = True
        
        maxXYPt = rc.Geometry.Point3d.Subtract(maxXYPt, tolVec)
        minXYPt = rc.Geometry.Point3d.Subtract(minXYPt, tolVec)
        
        #glazing distance
        glzHeight = minXYPt.DistanceTo(maxXYPt)
        
        # find number of shadings
        try:
            numOfShd = int(numOfShds)
            shadingHeight = glzHeight/numOfShd
            shadingRemainder = shadingHeight
        except:
            shadingHeight = distBetween
            shadingRemainder = (((glzHeight/distBetween) - math.floor(glzHeight/distBetween))*distBetween)
            if shadingRemainder == 0:
                shadingRemainder = shadingHeight
        
        # find shading base planes
        planeOrigins = []
        planes = []
        
        pointCurve = rc.Geometry.Curve.CreateControlPointCurve([maxXYPt, minXYPt])
        divisionParams = pointCurve.DivideByLength(shadingHeight, True)
        divisionPoints = []
        for param in divisionParams:
            divisionPoints.append(pointCurve.PointAt(param))
        
        planePoints = divisionPoints
        try:
            for point in planePoints:
                planes.append(rc.Geometry.Plane(point, planeVec))
        except:
            # single shading
            planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(minXYPt), planeVec))
        sortedPlanes = planes
    
    
    return sortedPlanes

def unionAllCurves(Curves):
    res = []
    
    for curveCount in range(0, len(Curves), 2):
        try:
            sc.doc = rc.RhinoDoc.ActiveDoc #change target document
            
            rs.EnableRedraw(False)
            
            guid1 = sc.doc.Objects.AddCurve(Curves[curveCount])
            guid2 = sc.doc.Objects.AddCurve(Curves[curveCount + 1])
            all = rs.CurveBooleanUnion([guid1, guid2])
            rs.DeleteObjects(guid1)
            rs.DeleteObjects(guid2)
            if all:
                a = [rs.coercegeometry(a) for a in all]
                for g in a: g.EnsurePrivateCopy() #must ensure copy if we delete from doc
            
            rs.DeleteObjects(all)
            
            sc.doc = ghdoc #put back document
            rs.EnableRedraw()
            
            if a == None:
                a = [Curves[curveCount], Curves[curveCount + 1]]
        except:
            rs.DeleteObjects(guid1)
            sc.doc = ghdoc #put back document
            rs.EnableRedraw()
            a = [Curves[curveCount]]
        
        if a:
            res.extend(a)
    return res


def splitSrf(brep, cuttingPlanes):
    # find the intersection crvs as the base for shadings
    intCrvs =[]
    for plane in cuttingPlanes:
        try:
            intCrvs.append(rc.Geometry.Brep.CreateContourCurves(brep, plane)[0])
        except:
            print "One intersection failed.  One of your vectors might be parallel to the _glzSrf."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "One intersection failed.  One of your vectors might be parallel to the _glzSrf.")
            
    if len(intCrvs) <= 1: return [brep] # only one shading/surface
    else: splitBrep = brep.Faces[0].Split(intCrvs, sc.doc.ModelAbsoluteTolerance)
    
    # make untrimmed surfaces from the trimmed surfaces
    splitBrep.Faces.ShrinkFaces()
    splittedFaces = []
    
    # convert faces to breps
    for face in splitBrep.Faces:
        splittedFaces.append(face.ToBrep())
    
    # create curve from origin of the planes to be used for sorting th
    originPts = []
    for pln in cuttingPlanes: originPts.append(pln.Origin)
    try: intCrv = rc.Geometry.Curve.CreateInterpolatedCurve(originPts, 3)
    except: intCrv = None
    
    if len(optionalPlanes_)!=0:
        #sort the surfaces based on the planes
        sortedFaces = sorted(splittedFaces, key=lambda a: intCrv.ClosestPoint(rc.Geometry.AreaMassProperties.Compute(a).Centroid)[1])
    else:
        # sort the breps base on Z
        sortedFaces = sorted(splittedFaces, key=lambda a: rc.Geometry.AreaMassProperties.Compute(a).Centroid.Z )
    
    # check the normal direction of the splitted surfaces to the base surface to make sure it's not reversed
    if brep.Faces[0].IsPlanar():
        brepNormal = getSrfPlane(brep).Normal
        for srf in sortedFaces:
            angle = rc.Geometry.Vector3d.VectorAngle(getSrfPlane(srf).Normal, brepNormal)
            if angle > math.pi/2: srf.Flip()
    elif len(optionalPlanes_)!=0:
        tangantVec = intCrv.TangentAt(intCrv.ClosestPoint(intCrv.PointAtNormalizedLength(0.5))[1])
        if tangantVec!= rc.Geometry.Vector3d.ZAxis:
            cVector = rc.Geometry.Vector3d.ZAxis
            refVector = rc.Geometry.Vector3d.CrossProduct(tangantVec, rc.Geometry.Vector3d.ZAxis)
        elif tangantVec!= rc.Geometry.Vector3d.YAxis:
            cVector = rc.Geometry.Vector3d.YAxis
            refVector = rc.Geometry.Vector3d.CrossProduct(tangantVec, rc.Geometry.Vector3d.YAxis)
        elif tangantVec!= rc.Geometry.Vector3d.XAxis:
            cVector = rc.Geometry.Vector3d.XAxis
            refVector = rc.Geometry.Vector3d.CrossProduct(tangantVec, rc.Geometry.Vector3d.XAxis)
        
        refAngle = rc.Geometry.Vector3d.VectorAngle(getSrfPlane(brep).Normal, refVector)
        
        for srf in sortedFaces:
            localTangantVec = intCrv.TangentAt(intCrv.ClosestPoint(getSrfPlane(srf).Origin)[1])
            localRefVector = rc.Geometry.Vector3d.CrossProduct(localTangantVec, cVector)
            localRefAngle = rc.Geometry.Vector3d.VectorAngle(getSrfPlane(srf).Normal, localRefVector)
            #print rc.Geometry.Vector3d.VectorAngle(refVector, localRefVector)
            
            if abs(localRefAngle - refAngle) > math.pi/2:
                #print "Flip one of the sub surface"
                try:
                    #print math.degrees(abs(localRefAngle - refAngle))
                    #print "flip"
                    srf.Flip()
                except:
                    pass
                
    return sortedFaces


def createShadings(baseSrfs, planes, sunVectors, mergeCrvs, rotationAngle_, lb_preparation):
    # create shading on planes
    unionedProjectedCrvsCollection = []
    firsTime = True
    for brepCount, brep in enumerate(baseSrfs):
        unionedProjectedCrvs = []
        projectedCrvs = []
        # find the normal of each surface
        brepPlane = getSrfPlane(brep)
        normalVector = brepPlane.Normal
        # mesh the base surface
        meshedBrep = rc.Geometry.Mesh.CreateFromBrep(brep, rc.Geometry.MeshingParameters.Smooth)[0]
        for sunV in sunVectors:
            projectedCrv = None
            #check if the window facing the sun vector
            isFacingTheSun = isSrfFacingTheVector(sunV, normalVector)
            if isFacingTheSun:
                # get the view from sun
                outline = getOutlineCrvFromSun(meshedBrep, sunV)[0]
                # project the outline to the plane
                try:
                    if len(optionalPlanes_)==0:
                        projectedCrv = projectToPlane(outline.DuplicateCurve(), planes[brepCount], sunV)
                    else:
                        # check if the brep is in the correct order
                        projectedCrv = projectToPlane(outline.DuplicateCurve(), planes[brepCount], sunV)
                        
                        # for cases the the surface is not planar the brepPlane should be located in the point
                        # that has the max distance from the sun vector
                        # if nonplanar
                        if not lb_preparation.checkPlanarity(brep):
                            # find the edges and find the points
                            # create a vector between origin of brepPlane and the point
                            borderPts = brep.Vertices
                            for borderVer in borderPts:
                                borderPt = borderVer.Location
                                # if angle with normal > pi/2:
                                refVector = rc.Geometry.Vector3d(borderPt - brepPlane.Origin)
                                if rc.Geometry.Vector3d.VectorAngle(brepPlane.Normal, refVector)> math.pi/2:
                                    #place the plane in that point
                                    brepPlane.Origin = borderPt
                                    
                        if not isShadingPossible(projectedCrv, brepPlane, sunV, lb_preparation, False):
                            #if brepCount== len(baseSrfs)-1: i = -1
                            #else: i = 1
                            i = 1
                            # try + 1
                            #if brepCount!= len(baseSrfs)-1:
                            projectedCrv = projectToPlane(outline.DuplicateCurve(), planes[brepCount + i], sunV)
                            
                            #double check
                            if not isShadingPossible(projectedCrv, brepPlane, sunV, lb_preparation, False):
                                # print brepCount
                                projectedCrv = None
                                
                                if brepCount == len(baseSrfs)-1: projectedCrv = None
                                #else:
                                #    print brepCount
                                # try -1
                                # projectedCrv = projectToPlane(outline.DuplicateCurve(), planes[brepCount - i], sunV)
                except Exception, e:
                    #print `e`
                    pass
                    print "Number of planes doesn't match the number of surfaces." + \
                          "\nOne of the shadings won't be created. You can generate the planes manually" + \
                          "\nand use optionalPlanes option."
            else:
                projectedCrvs.extend("N")
            if projectedCrv:
                try: projectedCrvs.extend(projectedCrv)
                except: projectedCrvs.append(projectedCrv)
        
        #Calculate the number of vectors that are behind the glazing surface.
        vecInFront = []
        for curve in projectedCrvs:
            if curve != "N": vecInFront.append(1)
            else: pass
        
        # If merge vectors is true, find the union the curves with the boundary of the shading.
        if mergeVectors_ == True:
            justVecShading = []
            for curve in projectedCrvs:
                if curve != "N":
                    justVecShading.append(curve)
                else: pass
            
            if len(justVecShading) > 1:
                listLength = len(justVecShading)
                mergedShadingFinal = justVecShading
                count  = 0
                while len(mergedShadingFinal) > 1 and count < int(listLength/2) + 1:
                    mergedShadingFinal = unionAllCurves(mergedShadingFinal)
                    count += 1
                
                if mergedShadingFinal == None:
                    mergedShadingFinal = justVecShading
                    print "Attempt to merge shadings failed.  Component will return multiple shadings." 
            else:
                mergedShadingFinal = justVecShading
            
            unionedProjectedCrvs = mergedShadingFinal
            if len(unionedProjectedCrvs) == 0:
                unionedProjectedCrvs = rc.Geometry.Curve.JoinCurves(justVecShading)
                print "Merging of vectors into a single shade failed. Component will return multiple shadings."
        else:
            unionedProjectedCrvs = projectedCrvs
        
        #Collect all of the curves together and add them to the list.
        unionedProjectedCrvsCollection.extend(unionedProjectedCrvs)
        
        finalShdSrfs = []
        for curve in unionedProjectedCrvsCollection:
            if curve != "N":
                try: finalShdSrfs.extend(rc.Geometry.Brep.CreatePlanarBreps(curve))
                except: finalShdSrfs.extend(curve)
            else: finalShdSrfs.append(None)
    
    #Give an output that states the number of sun vectors behind the glazing for which no shading was generated.
    vecBehind = len(sunVectors) - len(vecInFront)
    if vecBehind != 0:
        print str(vecBehind) + " sun vectors were angled behind the _glzSrf for which no shading was generated."
    
    return finalShdSrfs

def main(method, depth, sunVectors, numShds, distBtwn, horOrVert):
    rotationAngle_ = 0
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        # find the normal of the surface in the center
        # note2developer: there might be cases that the surface is not planar and
        # the normal is changing from point to point, then I should sample the test surface
        # and test the normal direction for more point
        baseSrfCenPt = rc.Geometry.AreaMassProperties.Compute(_glzSrf).Centroid
        # sometimes the center point is not located on the surface
        baseSrfCenPt = _glzSrf.ClosestPoint(baseSrfCenPt)
        
        bool, centerPtU, centerPtV = _glzSrf.Faces[0].ClosestPoint(baseSrfCenPt)
        if bool:
            normalVector = _glzSrf.Faces[0].NormalAt(centerPtU, centerPtV)
            #return rc.Geometry.Plane(baseSrfCenPt,normalVector)
        else:
            print "Couldn't find the normal of the shading surface." + \
                  "\nRebuild the surface and try again!"
            return -1
        
        # mesh the glazing surface
        _glzSrfMeshed = rc.Geometry.Mesh.CreateFromBrep(_glzSrf, rc.Geometry.MeshingParameters.Smooth)[0]
        
        shadingSurfaces =[]
        
        if method == 0:
            #Depth method
            #Define a function that can get the angle to North of any surface.
            def getAngle2North(normalVector):
                if north_ != None and north_.IsValid():
                    northVector = north_
                else:northVector = rc.Geometry.Vector3d.YAxis
                angle =  rc.Geometry.Vector3d.VectorAngle(northVector, normalVector, rc.Geometry.Plane.WorldXY)
                finalAngle = math.degrees(angle)
                return finalAngle
            
            # Define a function that can split up a list of values and assign it to different cardinal directions.
            def getValueBasedOnOrientation(valueList):
                angles = []
                if valueList == None or len(valueList) == 0: value = None
                if len(valueList) == 1:
                    value = valueList[0]
                elif len(valueList) > 1:
                    initAngles = rs.frange(0, 360, 360/len(valueList))
                    for an in initAngles: angles.append(an-(360/(2*len(valueList))))
                    angles.append(360)
                    for angleCount in range(len(angles)-1):
                        if angles[angleCount] <= (getAngle2North(normalVector))%360 <= angles[angleCount +1]:
                            targetValue = valueList[angleCount%len(valueList)]
                    value = targetValue
                return value
            
            # If multiple shading depths are given, use it to split up the glazing by cardinal direction and assign different depths to different directions.
            depth = getValueBasedOnOrientation(depth)
            
            # If multiple number of shade inputs are given, use it to split up the glazing by cardinal direction and assign different numbers of shades to different directions.
            numShds = getValueBasedOnOrientation(numShds)
            
            # If multiple distances between shade inputs are given, use it to split up the glazing by cardinal direction and assign different distances of shades to different directions.
            distBtwn = getValueBasedOnOrientation(distBtwn)
            
            # If multiple horizontal or vertical inputs are given, use it to split up the glazing by cardinal direction and assign different horizontal or vertical to different directions.
            horOrVertical = getValueBasedOnOrientation(_horOrVertical_)
            
            # If multiple _shdAngle_ inputs are given, use it to split up the glazing by cardinal direction and assign different _shdAngle_ to different directions.
            shdAngle = getValueBasedOnOrientation(_shdAngle_)
            
            # generate the planes
            planes = analyzeGlz(_glzSrf, distBtwn, numShds, horOrVertical, lb_visualization, normalVector)
            
            # find the intersection crvs as the base for shadings
            intCrvs =[]
            for plane in planes:
                try: intCrvs.append(rc.Geometry.Brep.CreateContourCurves(_glzSrf, plane)[0])
                except: print "One intersection failed."
            
            if normalVector != rc.Geometry.Vector3d.ZAxis:
                normalVectorPerp = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
            
            #If an shdAngle is provided, use it to rotate the planes by that angle
            if shdAngle != None:
                if horOrVertical == True or horOrVertical == None:
                    planeVec = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
                    planeVec.Rotate(1.570796, rc.Geometry.Vector3d.ZAxis)
                    normalVectorPerp.Rotate((shdAngle*0.01745329), planeVec)
                elif horOrVertical == False:
                    planeVec = rc.Geometry.Vector3d.ZAxis
                    if getAngle2North(normalVectorPerp) < 180:
                        normalVectorPerp.Rotate((shdAngle*0.01745329), planeVec)
                    else: normalVectorPerp.Rotate((shdAngle*-0.01745329), planeVec)
            
            #Generate the shade curves based on the planes and extrusion vectors
            if intCrvs !=[]:
                for c in intCrvs:
                    try:
                        shdSrf = rc.Geometry.Surface.CreateExtrusion(c, float(depth) * normalVectorPerp).ToBrep()
                        shadingSurfaces.append(shdSrf)
                    except:
                        pass
                return shadingSurfaces
        elif method == 1:
            # there are two cases for method 1. There is a geometry or there is not a geometrty
            if optionalShdSrf_:
                isShdPlanar = lb_preparation.checkPlanarity(optionalShdSrf_)
                
                # find the border
                shdOutlineCrvs = optionalShdSrf_.DuplicateEdgeCurves(True)
                shadingBorder = rc.Geometry.Curve.JoinCurves(shdOutlineCrvs)[0]
                
                # get the plane in the center
                shdSrfPlane = getSrfPlane(optionalShdSrf_)
                
                #let's solve it for case 0
                # case 0: there is an optional input for shading surface
                projectedCrvs =[]
                for sunV in sunVectors:
                    #check if the window facing the sun vector
                    isFacingTheSun = isSrfFacingTheVector(sunV, normalVector)
                    
                    # and check if this shading surface possibally cast shadow on the window (is not behind the window)
                    if isFacingTheSun:
                        shadingPossibility = isShadingPossible(shadingBorder, getSrfPlane(_glzSrf), sunV, lb_preparation)
                    # create the shading
                    if isFacingTheSun and shadingPossibility:
                        # get the view from sun
                        outline = getOutlineCrvFromSun(_glzSrfMeshed, sunV)[0]
                        # project the outline back to the shading geometry
                        # if shading surface is planar, create the plane and use the plane
                        if isShdPlanar:
                            projectedCrvToPlane = projectToPlane(outline.DuplicateCurve(), shdSrfPlane, sunV)
                            # find the intersection
                            try:
                                projectedCrv = rc.Geometry.Curve.CreateBooleanIntersection(shadingBorder, projectedCrvToPlane)[0]
                            except:
                                projectedCrv = None
                            #    pass
                        else:
                            projectedCrv = rc.Geometry.Curve.ProjectToBrep(outline, optionalShdSrf_, sunV, sc.doc.ModelAbsoluteTolerance)
                            # collect the curves
                        
                        if projectedCrv:
                            try: projectedCrvs.extend(projectedCrv)
                            except: projectedCrvs.append(projectedCrv)
                    
                if isShdPlanar:
                    # find the union the curves with the boundary of the shading
                    if mergeVectors_ == True:
                        unionedProjectedCrvs =rc.Geometry.Curve.CreateBooleanUnion(projectedCrvs)
                        if len(unionedProjectedCrvs) == 0:
                            unionedProjectedCrvs = rc.Geometry.Curve.JoinCurves(projectedCrvs)
                            print "Merging of vectors into a single shade failed (most likely due to issues of model tolerance). Try increasing model tolerance or using fewer input sun vectors."
                    else:
                        unionedProjectedCrvs = projectedCrvs
                elif not isShdPlanar:
                    if mergeVectors_ == True:
                        pProjectedCrvs = []
                        #pShadingBorder = rc.Geometry.Curve.ProjectToPlane(shadingBorder, shdSrfPlane)
                        pShadingBorder = rc.Geometry.Curve.ProjectToPlane(shadingBorder, rc.Geometry.Plane.WorldXY)
                        
                        for c in projectedCrvs:
                            # project the curve to the plane
                            #c = rc.Geometry.Curve.ProjectToPlane(c, shdSrfPlane)
                            c = rc.Geometry.Curve.ProjectToPlane(c, rc.Geometry.Plane.WorldXY)
                            
                            # close the curve
                            if not c.IsClosed:
                                line = rc.Geometry.Line(c.PointAtStart, c.PointAtEnd).ToNurbsCurve()
                                c = rc.Geometry.Curve.JoinCurves([c, line])[0]
                            # find the intersection
                            try:
                                projectedCrv = rc.Geometry.Curve.CreateBooleanIntersection(pShadingBorder, c)[0]
                            except:
                                print "Merging of vectors into a single shade failed (most likely due to issues of model tolerance). Try increasing model tolerance or using fewer input sun vectors."
                                projectedCrv = None
                            if projectedCrv: pProjectedCrvs.append(projectedCrv)
                            
                        try:
                            pUnionedProjectedCrvs =rc.Geometry.Curve.CreateBooleanUnion(pProjectedCrvs)[0]
                            unionedProjectedCrvs = rc.Geometry.Curve.ProjectToBrep(pUnionedProjectedCrvs, optionalShdSrf_, rc.Geometry.Vector3d.ZAxis, sc.doc.ModelAbsoluteTolerance)
                        except:
                            print "Merging of vectors into a single shade failed (most likely due to issues of model tolerance). Try increasing model tolerance or using fewer input sun vectors."
                            pass
                        if unionedProjectedCrvs == []:
                            unionedProjectedCrvs = rc.Geometry.Curve.JoinCurves(pProjectedCrvs)
                    else:
                        # Return the original curves
                        unionedProjectedCrvs = projectedCrvs
                
                for curve in unionedProjectedCrvs:
                    try:
                        splitShades = rc.Geometry.Brep.Split(optionalShdSrf_, rc.Geometry.Brep.CreateFromSurface(rc.Geometry.Surface.CreateExtrusion(curve, rc.Geometry.Vector3d.ZAxis)), sc.doc.ModelAbsoluteTolerance)
                        #shadingSurfaces.append(splitShades[1])
                        cenDist = []
                        for shade in splitShades:
                            shadeBBox = shade.GetBoundingBox(False)
                            shadeBBoxCen = shadeBBox.Center
                            curveBBox = curve.GetBoundingBox(False)
                            curveBBoxCen = curveBBox.Center
                            cenDist.append(rc.Geometry.Point3d.DistanceTo(shadeBBoxCen, curveBBoxCen))
                        cenDist1, splitShades1 = (list(t) for t in zip(*sorted(zip(cenDist, splitShades))))
                        if mergeVectors_ == True:
                            shadingSurfaces.append(splitShades1[0])
                        else:
                            shadingSurfaces.append(splitShades1[-1])
                    except:
                        shadingSurfaces.append(curve)
                
                return shadingSurfaces
            
            else:
                #case 1: there is no geometry so it should be generated
                # generate the planes
                if len(optionalPlanes_)!=0: planes = optionalPlanes_
                else:
                    if len(distBtwn) == 0:
                        distBtwn = None
                    else: distBtwn = distBtwn[0]
                    if len(numShds) == 0:
                        numShds = None
                    else: numShds = numShds[0]
                    if len(horOrVert) == 0:
                        horOrVert = True
                    else: horOrVert = horOrVert[0]
                    planes = analyzeGlz(_glzSrf, distBtwn, numShds, horOrVert, lb_visualization, normalVector)
                # split base surface with planes
                baseSrfs = splitSrf(_glzSrf, planes)
                
                # create shading surfaces
                shadingSrfs = createShadings(baseSrfs, planes, sunVectors, mergeVectors_, rotationAngle_, lb_preparation)
                
                return shadingSrfs
                
                pass
    else:
        print "You should first let Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
        return -1

def giveWarning(warningMsg):
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, warningMsg)

# checkList

if _runIt:
    checkList, method, depth, sunVectors = checkTheInputs()
else:
    print "Set _runIt to True!"
    checkList = False

if checkList:
    shadingSrfs = main(method, depth, sunVectors, _numOfShds, _distBetween, _horOrVertical_)
    if shadingSrfs!=-1:
        print "Shading Calculation is done!"
