# Solar Fan
# By Mostapha Sadeghipour Roudsari and Chris Mackey
# Sadeghipour@gmail.com and Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to generate a solar fan for a given test surface and set of solar vectors.  Solar fans essentially illustrate the volume that should be clear of shading in order to provide solar access for the given set of sun vectors.

-
Provided by Ladybug 0.0.53
    
    Args:
        _baseSrf: A surface representing a piece of land (such as a park) or a window for which solar access is desired.
        _sunVectors: Sun vectors that should be accessible to the baseSrf.
        _size_: Default scale of 1 produces a solar fan that is half as tall as the longest side of the _baseSrf.  Increase or decrease this value to extend the fan higher or lower.  Note that increasing the height too high can cause the fan to break up into multiple fans due to the resolution of the solar vectors.
        _runIt: Set to "True" to generate a solar fan.
    Returns:
        readMe!:...
        solarFan: Brep representing a solar fan (or list of breps in the event that sun vectors are too far from one another).
"""
ghenv.Component.Name = 'Ladybug_SolarFan'
ghenv.Component.NickName = 'SolarFan'
ghenv.Component.Message = 'VER 0.0.53\nJan_22_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math



def checkTheInputs():
    
    if not _baseSrf!=None:
        print "_baseSrf is missing"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "_baseSrf is missing")
        
        return False, []
    elif not (_sunVectors and _sunVectors[0]!=None):
        print " _sunVectors is missing. You need to either provide a number as a depth or a vector as a sun vector."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, " _sunVectors is missing. You need to either provide a number as a depth or a vector as a sun vector.")
        return False, []
        
    sunVectors = []
    # create vectors from generic type object
    for v in _sunVectors:
        sunV = rc.Geometry.Vector3d(v)
        #sunV.Reverse()
        sunVectors.append(sunV)
    
    
    return True, sunVectors

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


def createShadings(baseSrfs, planes, sunVectors, mergeCrvs, lb_preparation):
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
                    projectedCrv = projectToPlane(outline.DuplicateCurve(), planes[brepCount], sunV)
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
        if mergeCrvs == True:
            unionedProjectedCrvs =rc.Geometry.Curve.CreateBooleanUnion(projectedCrvs)
            if len(unionedProjectedCrvs) == 0:
                unionedProjectedCrvs = rc.Geometry.Curve.JoinCurves(projectedCrvs)
        else:
            unionedProjectedCrvs = projectedCrvs
        
        unionedProjectedCrvsCollection.extend(unionedProjectedCrvs)
    
    return unionedProjectedCrvsCollection

def unionAllFans(solarFans):
    res = []
    for fanCount in range(0, len(solarFans), 2):
        try:
            sc.doc = rc.RhinoDoc.ActiveDoc #change target document
            rs.EnableRedraw(False)
            
            guid1 = sc.doc.Objects.AddBrep(solarFans[fanCount])
            guid2 = sc.doc.Objects.AddBrep(solarFans[fanCount + 1])
            all = rs.BooleanUnion([guid1, guid2], True)
            
            if all:
                a = [rs.coercegeometry(a) for a in all]
                for g in a: g.EnsurePrivateCopy() #must ensure copy if we delete from doc
            
            rs.DeleteObjects(all)
            
            sc.doc = ghdoc #put back document
            rs.EnableRedraw()
            
            if a == None:
                a = [solarFans[fanCount], solarFans[fanCount + 1]]
        except:
            rs.DeleteObjects(guid1)
            sc.doc = ghdoc #put back document
            rs.EnableRedraw()
            a = [solarFans[fanCount]]
        
        if a:
            res.extend(a)
    return res

def main(sunVectors):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        # get the genter of the base surface.
        baseSrfCenPt = rc.Geometry.AreaMassProperties.Compute(_baseSrf).Centroid
        # mesh the base surface to ensure that we can get vertices all around the object for the bounding box.
        _baseSrfMeshed = rc.Geometry.Mesh.CreateFromBrep(_baseSrf, rc.Geometry.MeshingParameters.Smooth)[0]
        # generate a bounding box around the base surfaces and extract dimensions for use with generating the plane to project to.
        points = []
        for point in _baseSrfMeshed.Vertices:
            points.append(rc.Geometry.Point3d(point))
        baseSrfBBox = rc.Geometry.BoundingBox(points)
        baseSrfBox = rc.Geometry.Box(baseSrfBBox)
        # from the bounding box dimnesions, deriva a point to be used to generate the intersection plane.
        X = baseSrfBox.X[1] - baseSrfBox.X[0]
        Y = baseSrfBox.Y[1] - baseSrfBox.Y[0]
        if X>Y:planeHeight = 0.5*X
        else: planeHeight = 0.5*Y
        try: Z = ((float(_size_))*planeHeight) + baseSrfBox.Z[1]
        except: Z = planeHeight + baseSrfBox.Z[1]
        planePt = rc.Geometry.Point3d(baseSrfCenPt.X, baseSrfCenPt.Y, Z)
        # generate the intersection plane
        plane = [rc.Geometry.Plane(planePt, rc.Geometry.Vector3d.ZAxis)]
        
        # create the outline curve shaded by the solar vectors. 
        shadingCrvs = createShadings([_baseSrf], plane, sunVectors, True, lb_preparation)
        if len(shadingCrvs) == 0:
            try:
                _baseSrf.Flip()
                shadingCrvs = createShadings([_baseSrf], plane, sunVectors, True, lb_preparation)
            except: pass
        
        # if one of the shading curves is cintained inside the other, it can be deleted from the solar fan and can speed up the calculation down the line.
        shdCrv2 = []
        for curve in shadingCrvs:
            if rc.Geometry.AreaMassProperties.Compute(curve).Area > rc.Geometry.AreaMassProperties.Compute(_baseSrf).Area:
                shdCrv2.append(curve)
        sortedCrvs = sorted(shdCrv2, key=lambda curve: rc.Geometry.AreaMassProperties.Compute(curve).Area)
        largestCrv = sortedCrvs[-1]
        finalShdCrvs =[]
        for curve in sortedCrvs:
            if str(rc.Geometry.Curve.PlanarClosedCurveRelationship(largestCrv, curve, plane[0], sc.doc.ModelAbsoluteTolerance)) != 'BInsideA':
                finalShdCrvs.append(curve)
            else: pass
        
        # dublicate the border around the base surface, which will be used to loft the solar fan
        baseSrfCrv = rc.Geometry.Curve.JoinCurves(_baseSrf.DuplicateEdgeCurves())[0]
        # get a point from the center of the shading curve to a new seam to adjust the seam on the shading curve.
        seamVectorPt = rc.Geometry.Vector3d((baseSrfCrv.PointAtStart.X - baseSrfCenPt.X)*planeHeight, (baseSrfCrv.PointAtStart.Y - baseSrfCenPt.Y)*planeHeight, 0)
        # adjust the seam of the shading curves.
        for curve in finalShdCrvs:
            curve.Reverse()
            curve.ChangeClosedCurveSeam(curve.ClosestPoint(rc.Geometry.Intersect.Intersection.CurveCurve(curve, rc.Geometry.Line(rc.Geometry.AreaMassProperties.Compute(curve).Centroid, seamVectorPt).ToNurbsCurve(), sc.doc.ModelAbsoluteTolerance, sc.doc.ModelAbsoluteTolerance)[0].PointA)[1])
        
        # loft the shading curves with the base curve and generate a surface to cap the loft.
        solarFanInit = []
        shadingSrfs =[]
        for curve in finalShdCrvs:
            try:
                solarFanInit.append(rc.Geometry.Brep.CreateFromLoft([curve, baseSrfCrv], rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0])
                shadingSrfs.append(rc.Geometry.Brep.CreatePlanarBreps(curve)[0])
            except: pass
        
        # close the brep of the solar fan
        for brepCount, brep in enumerate(solarFanInit):
            brep.Join(_baseSrf, sc.doc.ModelAbsoluteTolerance, True)
            brep.Join(shadingSrfs[brepCount], sc.doc.ModelAbsoluteTolerance, True)
        
        # if more than one solar fan solids have been produced, resulting from multiple shading curves being produced, try to boolean union them together into one solar fan.
        if len(solarFanInit) > 1:
            listLength = len(solarFanInit)
            solarFanFinal = solarFanInit
            count  = 0
            while len(solarFanFinal) > 1 and count < int(listLength/2) + 1:
                solarFanFinal = unionAllFans(solarFanFinal)
                count += 1
            
            if solarFanFinal == None:
                solarFanFinal = solarFanInit
                print "Attempt to Boolean Union multiple solar fans into one failed.  Component will return multiple solar fans.  Try decreasing the '_adjustScale' parameter or using a greater timestep of solar vectors if a single solar fan is desired." 
        else:
            solarFanFinal = solarFanInit
        
        return solarFanFinal
        
    else:
        print "You should first let Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
        return -1

def giveWarning(warningMsg):
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, warningMsg)


if _runIt:
    checkList, sunVectors = checkTheInputs()
else:
    print "Set _runIt to True!"
    checkList = False

if checkList:
    solarFan = main(sunVectors)
    if solarFan!=-1:
        print "Solar fan calculation is done!"