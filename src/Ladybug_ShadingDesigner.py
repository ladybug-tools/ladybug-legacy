# This is a revision for shading designer
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Shading Designer
Warning: WIP!

-
Provided by Ladybug 0.0.52
    
    Args:
        _glzSrf: A base glazed surface to be used for shading design or a list of glazed surfaces.
        _depthOrVector: Depth of the shade or a sun vector to be shaded.  You can also input lists of depths, which will assign different depths based on cardinal direction.  For example, inputing 4 values for depths will assign each value of the list as follows: item 0 = north depth, item 1 = west depth, item 2 = south depth, item 3 = east depth.  Lists of vectors to be shaded can also be input and shades can be joined together with the mergeVectors_ input.
        _numOfShds: The number of shades to generate for each glazed surface.
        _distBetween: An alternate option for _numOfShds.
        optionalShdSrf_: Optional shade surface to draw shading curves on (this input can only be used with the sun vector method).
        optionalPlanes_: Optional planes to draw shading curves on (this input can only be used with the sun vector method).
        mergeVectors_: Set to "True" to merge all the shades generated from a list of sun vectors into a single shade.
        _horOrVertical_: Set to "True" to generate horizontal shades or "False" to generate vertical shades (this input can only be used with the depth method). You can also input lists of _horOrVertical_ input, which will assign different orientations based on cardinal direction.
        _shdAngle_: If you have vertical shades, use this to rotate them towards the South by a certain value in degrees, which, if applied in the East-West direction will let in more winter sun than summer sun.  If you have horizontal shades, use this to angle shades downward, as in some versions of the brise soleil.  (This input can only be used with the depth method).  You an also put in lists of angles to assign different shade angles to different directions.
        north_: Input a vector to set north; default is set to the Y-axis.
        _runIt: Set to true to run the study.
    Returns:
        readMe!:...
        shadingCrvs: Shading geometries as a list of curves
"""
ghenv.Component.Name = 'Ladybug_ShadingDesigner'
ghenv.Component.NickName = 'SHDDesigner'
ghenv.Component.Message = 'Proof of concept\nJAN_08_2014'

import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math

inputsDict = {
     
0 : ["_glzSrf", "A base glazed surface to be used for shading design or a list of glazed surfaces."],
1: ["_depthOrVector", "Depth of the shade or a sun vector to be shaded.  You can also input lists of depths, which will assign different depths based on cardinal direction.  For example, inputing 4 values for depths will assign each value of the list as follows: item 0 = north depth, item 1 = west depth, item 2 = south depth, item 3 = east depth.  Lists of vectors to be shaded can also be input and shades can be joined together with the mergeVectors_ input."],
2: ["_numOfShds", "The number of shades to generate for each glazed surface."],
3: ["_distBetween:", "An alternate option for _numOfShds."],
4: ["---------------", "---------------"],
5: ["optionalShdSrf_", "Optional shade surface to draw shading curves on (this input can only be used with the sun vector method)."],
6: ["optionalPlanes_", "Optional planes to draw shading curves on (this input can only be used with the sun vector method)."],
7: ["mergeVectors_", "Set to True to merge all the shades generated from a list of sun vectors into a single shade."],
8: ["---------------", "---------------"],
9: ["_horOrVertical_", "Set to True to generate horizontal shades or False to generate vertical shades (this input can only be used with the depth method). You can also input lists of _horOrVertical_ input, which will assign different orientations based on cardinal direction."],
10: ["_shdAngle_", "If you have vertical shades, use this to rotate them towards the South by a certain value in degrees, which, if applied in the East-West direction will let in more winter sun than summer sun.  If you have horizontal shades, use this to angle shades downward, as in some versions of the brise soleil.  (This input can only be used with the depth method).  You an also put in lists of angles to assign different shade angles to different directions."],
11: ["---------------", "---------------"],
12: ["north_", "Input a vector to set north; default is set to the Y-axis"],
13: ["_runIt", "Set to true to run the study."]
}

# manage component inputs

numInputs = ghenv.Component.Params.Input.Count
try:
    depthTest = float(_depthOrVector[0])
    method = 0
    
except:
 method = 1

if method == 1:
    if input == 12:
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
    
    if optionalShdSrf_ and method == 0:
        print "You need to provide the sun vector to generate the shadings on an optional shading surface"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You need to provide the sun vector to generate the shadings on an optional shading surface")
        return False, [], [], []
    
    
    # additional check for method 0
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
    
    if numOfShds == 0 or distBetween == 0:
        sortedPlanes = []
    
    elif horOrVertical == True:
        # Horizontal
        #Define a bounding box for use in calculating the number of shades to generate
        minZPt = bbox.Corner(False, True, True)
        maxZPt = bbox.Corner(False, True, False)
        maxZPt = rc.Geometry.Point3d(maxZPt.X, maxZPt.Y, maxZPt.Z - sc.doc.ModelAbsoluteTolerance)
        centerPt = bbox.Center 
        #glazing hieghts
        glzHeight = minZPt.DistanceTo(maxZPt)
        
        # find number of shadings
        try: numOfShd = int(numOfShds)
        except: numOfShd = math.ceil(glzHeight/distBetween)
        shadingHeight = glzHeight/numOfShd
        
        # find shading base planes
        planeOrigins = []
        planes = []
        X, Y, z = minZPt.X, minZPt.Y, minZPt.Z
        try:
            for Z in rs.frange(minZPt.Z + shadingHeight , maxZPt.Z, shadingHeight):
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
        maxXYPt = bbox.Corner(False, False, True)
        centerPt = bbox.Center 
        #glazing distance
        glzHeight = minXYPt.DistanceTo(maxXYPt)
        
        # find number of shadings
        try: numOfShd = int(numOfShds)
        except: numOfShd = math.ceil(glzHeight/distBetween)
        
        shadingHeight = glzHeight/numOfShd
        # find shading base planes
        planeOrigins = []
        planes = []
        pointCurve = rc.Geometry.Curve.CreateControlPointCurve([minXYPt, maxXYPt])
        divisionParams = pointCurve.DivideByLength(shadingHeight, True)
        divisionPoints = []
        for param in divisionParams:
            divisionPoints.append(pointCurve.PointAt(param))
        planePoints = divisionPoints[1:]
        try:
            for point in planePoints:
                planes.append(rc.Geometry.Plane(point, planeVec))
        except:
            # single shading
            planes.append(rc.Geometry.Plane(rc.Geometry.Point3d(maxXYPt), planeVec))
        # sort the planes
        try: sortedPlanes = sorted(planes, key=lambda a: a.Origin.X)
        except: sortedPlanes = sorted(planes, key=lambda a: a.Origin.Y)
    
    # return planes
    return sortedPlanes
    
def splitSrf(brep, cuttingPlanes):
    # find the intersection crvs as the base for shadings
    intCrvs =[]
    for plane in cuttingPlanes:
        try:
            intCrvs.append(rc.Geometry.Brep.CreateContourCurves(brep, plane)[0])
        except:
            print "one intersection failed"
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "one intersection failed")
            
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
            if angle > math.pi/2: srf.Filp()
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
            if projectedCrv:
                try: projectedCrvs.extend(projectedCrv)
                except: projectedCrvs.append(projectedCrv)
        
        # find the union the curves with the boundary of the shading
        if mergeVectors_ == True:
            unionedProjectedCrvs =rc.Geometry.Curve.CreateBooleanUnion(projectedCrvs)
            if unionedProjectedCrvs == []: unionedProjectedCrvs = rc.Geometry.Curve.JoinCurves(projectedCrvs)
        else:
            unionedProjectedCrvs = projectedCrvs
        
        unionedProjectedCrvsCollection.extend(unionedProjectedCrvs)
    
    return unionedProjectedCrvsCollection

def main(method, depth, sunVectors, numShds, distBtwn):
    # for now horizontal shadings are automated
    # for vertical shadings the user can use optional planes
    # for now there is no rotation Option
    # I will apply this later
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
        
        unionedProjectedCrvs =[]
        
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
                except: print "one intersection failed"
            
            if normalVector != rc.Geometry.Vector3d.ZAxis:
                normalVectorPerp = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
            
            #If an shdAngle is provided, use it to rotate the planes by that angle
            if shdAngle != None:
                if horOrVertical == True:
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
                        edges = shdSrf.DuplicateEdgeCurves(True)
                        border = rc.Geometry.Curve.JoinCurves(edges)[0]
                        unionedProjectedCrvs.append(border)
                    except:
                        pass
                return unionedProjectedCrvs
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
                        if unionedProjectedCrvs == []: unionedProjectedCrvs = rc.Geometry.Curve.JoinCurves(projectedCrvs)
                    else:
                        #unionedProjectedCrvs = rc.Geometry.Curve.JoinCurves(projectedCrvs)
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
                                print "Merging the vectors failed. The component will output the curves. You may want to set mergeVectors_ to False!"
                                projectedCrv = None
                            if projectedCrv: pProjectedCrvs.append(projectedCrv)
                            
                        try:
                            pUnionedProjectedCrvs =rc.Geometry.Curve.CreateBooleanUnion(pProjectedCrvs)[0]
                            unionedProjectedCrvs = rc.Geometry.Curve.ProjectToBrep(pUnionedProjectedCrvs, optionalShdSrf_, rc.Geometry.Vector3d.ZAxis, sc.doc.ModelAbsoluteTolerance)
                        except:
                            print "Merging the vectors failed. The component will output the curves so you can take care of the rest!"
                            pass
                        if unionedProjectedCrvs == []:
                            unionedProjectedCrvs = rc.Geometry.Curve.JoinCurves(pProjectedCrvs)
                    else:
                        # join the curves and return
                        unionedProjectedCrvs = rc.Geometry.Curve.JoinCurves(projectedCrvs)
                
                return unionedProjectedCrvs
            
            else:
                #case 1: there is no geometry so it should be generated
                # generate the planes
                if len(optionalPlanes_)!=0: planes = optionalPlanes_
                else: planes = analyzeGlz(_glzSrf, _distBetween, _numOfShds, _horOrVertical_, lb_visualization, normalVector)
                # return planes
                # split base surface with planes
                baseSrfs = splitSrf(_glzSrf, planes)
                #print len(baseSrfs), len(planes)
                # create shading surfaces
                shadingCrvs = createShadings(baseSrfs, planes, sunVectors, mergeVectors_, rotationAngle_, lb_preparation, normalVector)
                
                return shadingCrvs
                
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
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Set _runIt to True!")
    checkList = False

if checkList:
    shadingCrvs = main(method, depth, sunVectors, _numOfShds, _distBetween)
    if shadingCrvs!=-1:
        print "Shading Calculation is done!"