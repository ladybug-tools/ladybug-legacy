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
        _glzSrf: Base glazing surface for shading design
        optionalShdSrf_: Optional shading form as a surface
        optionalPlanes_: Optional planes for shading design
        _depthOrVector: Depth of the shading or sun vector
        mergeVectors_: Merge all the shadings into a single shade
        _numOfShds: Number of shades for each test surface
        _distBetween: Alternate option for _numOfShds
        _runIt: Set to true to run the study
    Returns:
        readMe!:...
        shadingCrvs: Shading geometries as a list of curves
"""
ghenv.Component.Name = 'Ladybug_ShdingDesigner'
ghenv.Component.NickName = 'SHDDesigner'
ghenv.Component.Message = 'Proof of concept\nNOV_01_2013'

import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

import math

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
        depth = float(_depthOrVector[0])
        # shading based on depth and not vectors
        # this method only works when there is no optional shaidng geometries
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

def analyzeGlz(glzSrf, distBetween, numOfShds, horOrVertical, lb_visualization):
    
    # find the bounding box
    bbox = glzSrf.GetBoundingBox(True)
    if horOrVertical == 1:
        # horizontal
        minZPt = bbox.Corner(False, True, True)
        maxZPt = bbox.Corner(False, True, False)
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

def main(method, depth, sunVectors):
    # for now horizontal shadings are automated
    # for vertical shadings the user can use optional planes
    _horOrVertical_ = True
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
            # depth method
            # generate the planes
            planes = analyzeGlz(_glzSrf, _distBetween, _numOfShds, _horOrVertical_, lb_visualization)
            # find the intersection crvs as the base for shadings
            intCrvs =[]
            for plane in planes:
                try: intCrvs.append(rc.Geometry.Brep.CreateContourCurves(_glzSrf, plane)[0])
                except: print "one intersection failed"
            
            if normalVector != rc.Geometry.Vector3d.ZAxis:
                normalVector = rc.Geometry.Vector3d(normalVector.X, normalVector.Y, 0)
            
            if intCrvs !=[]:
                for c in intCrvs:
                    shdSrf = rc.Geometry.Surface.CreateExtrusion(c, depth * normalVector).ToBrep()
                    edges = shdSrf.DuplicateEdgeCurves(True)
                    border = rc.Geometry.Curve.JoinCurves(edges)[0]
                    unionedProjectedCrvs.append(border)
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
                else: planes = analyzeGlz(_glzSrf, _distBetween, _numOfShds, _horOrVertical_, lb_visualization)
                # return planes
                # split base surface with planes
                baseSrfs = splitSrf(_glzSrf, planes)
                #print len(baseSrfs), len(planes)
                # create shading surfaces
                shadingCrvs = createShadings(baseSrfs, planes, sunVectors, mergeVectors_, rotationAngle_, lb_preparation)
                
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
    shadingCrvs = main(method, depth, sunVectors)
    if shadingCrvs!=-1:
        print "Shading Calculation is done!"