# By Mostapha Sadeghipour Roudsari
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
        scale: Use this input to change the scale of the sky dome.  The default is set to 1.
        
    Returns:
        masked: Shadow mask
        unmasked: Unmasked portion of the sky
        percMasked: Percentage of the sky masked
"""

ghenv.Component.Name = "Ladybug_Shading Mask_II"
ghenv.Component.NickName = 'shadingMaskII'
ghenv.Component.Message = 'VER 0.0.58\nSEP_11_2014'
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

def calculateBB(geometries, restricted = True):
    
    bbox = None
    plane = rc.Geometry.Plane.WorldXY
    if geometries:
        flattenGeo = []
        for geometry in geometries:
            #print geometry
            if isinstance(geometry, list):
                # geometry = list(chain.from_iterable(geometry)) # it gives me errors for
                [flattenGeo.append(g) for g in geometry]
                #geometry = flatten
            else:
                flattenGeo.append(geometry)
            #print flattenGeo
            for geo in flattenGeo:
                if(bbox==None ): bbox = geo.GetBoundingBox(restricted)
                else: bbox = rc.Geometry.BoundingBox.Union( bbox, geo.GetBoundingBox(restricted))
    
    return bbox

def generateSkyGeo(cenPt, context):
    
    # find the bounding box
    bbox = calculateBB(context)
    cornerPts = bbox.GetCorners()
    radius = 0
    for pt in cornerPts:
        if cenPt.DistanceTo(pt)> radius:
            radius = cenPt.DistanceTo(pt)
    
    # make sure the sphere is big enough
    radius = radius * 1.01
    
    # rotation line axis
    lineVector = rc.Geometry.Vector3d.ZAxis
    lineVector.Reverse()
    lineAxis = rc.Geometry.Line(cenPt, lineVector)
    
    # base plane to draw the arc
    basePlane = rc.Geometry.Plane(cenPt, rc.Geometry.Vector3d.XAxis)
    baseVector = rc.Geometry.Vector3d.YAxis
        
    sectionCrv = rc.Geometry.Arc(basePlane, radius, math.pi/2).ToNurbsCurve()
    
    sky  =rc.Geometry.RevSurface.Create(sectionCrv, lineAxis).ToBrep()
        
    return sky, radius

def joinMesh(meshList):
    joinedMesh = rc.Geometry.Mesh()
    for m in meshList: joinedMesh.Append(m)
    return joinedMesh

def getMeshFaceVertices(meshFace, vertices):
    
    # find face vertices
    pts = range(3)
    pts[0] = rc.Geometry.Point3d(vertices[meshFace.A])
    pts[1] = rc.Geometry.Point3d(vertices[meshFace.B])
    pts[2] = rc.Geometry.Point3d(vertices[meshFace.C])
    if meshFace.IsQuad:
        pts.append(rc.Geometry.Point3d(vertices[meshFace.D]))
    
    # movedPts the points inside so it won't be in the edge of geometry
    # find the average point
    if len(pts) == 3:  averagePt = (pts[0] + pts[1] + pts[2]) / 3
    elif len(pts) == 4:  averagePt = (pts[0] + pts[1] + pts[2] + pts[3]) / 4
    
    movedPts = []
    for pt in pts:
        translateVector = rc.Geometry.Vector3d(averagePt - pt)
        movedPt = rc.Geometry.Point3d.Add(pt, .01 * translateVector)
        movedPts.append(movedPt)
    return pts, movedPts

def isMeshFaceVisible(cenPt, pts, context):
    
    # check if the point is in the same plane as surface
    try:
        plane = rc.Geometry.Plane(pts[0], pts[1], pts[2])
        if abs(plane.DistanceTo(cenPt)) <= sc.doc.ModelAbsoluteTolerance:
            return 0
    except:
        pass #singlePt check
        
    visiblePts = []
    for pt in pts:
        line = rc.Geometry.Line(cenPt, pt)
        intPts, pattern = rc.Geometry.Intersect.Intersection.MeshLine(context, line)
        
        if len(intPts) <= 1: visiblePts.append(pt)
    
    if len(visiblePts)/len(pts) == 0: return False
    return True


def movePointsToSkyDome(visiblePts, cenPt, skyRadius):
    newPts = []
    lines = []
    for pt in visiblePts:
        movingVector = rc.Geometry.Vector3d(pt- cenPt)
        movingVector.Unitize()
        
        newPt = rc.Geometry.Point3d.Add(cenPt, skyRadius * movingVector)
        newPts.append(newPt)
    
    for ptCount, pt in enumerate(newPts):
        lines.append(rc.Geometry.Line(newPts[ptCount%len(newPts)], newPts[(ptCount + 1)%len(newPts)]).ToNurbsCurve())
    
    return lines

def projectToSkyAndXY(lines, centerPt, sky):
    projectLines = []
    for line in lines:
        direction = rc.Geometry.Vector3d(line.PointAtNormalizedLength(0.5) - centerPt)
        prjLines = rc.Geometry.Curve.ProjectToBrep(line, sky, direction, sc.doc.ModelAbsoluteTolerance)
        
        # I should probably check here for projection in wrong direction
        for prjLine in prjLines:
            midVector = rc.Geometry.Vector3d(prjLine.PointAtNormalizedLength(0.5) - centerPt)
            if rc.Geometry.Vector3d.VectorAngle(direction, midVector) < math.pi/2:
                
                # project to xy
                basePlane = rc.Geometry.Plane(centerPt, rc.Geometry.Vector3d.ZAxis)
                lineProjectedToXY = rc.Geometry.Curve.ProjectToPlane(prjLine, basePlane)
                projectLines.append(lineProjectedToXY)
        
    return projectLines
    
def getSkyMask(cenPt, context, sky, skyRadius, merge):

    # create joinedContext
    joinedContext = joinMesh(context)
    
    planarCurves = []
    
    # for each mesh
    for mesh in context:
        vertices = mesh.Vertices
        thisFaceCurves = []
        for meshFace in mesh.Faces:
            pts, movedPts = getMeshFaceVertices(meshFace, vertices)
            isVisible = isMeshFaceVisible(cenPt, movedPts, joinedContext)
            pts.append(pts[0])
            
            if isVisible == 1:
                # move the points toward the sky and create the lines
                lines = movePointsToSkyDome(pts, cenPt, skyRadius)
                
                # project the lines to sky dome and then to XY
                curvesOnSky = projectToSkyAndXY(lines, cenPt, sky)
                
                # join the curves and make sure it is a closed curve
                joinedCurve = rc.Geometry.Curve.JoinCurves(curvesOnSky)
                
                if len(joinedCurve)==1 and joinedCurve[0].IsClosed:
                    # collect curves for this mesh
                    thisFaceCurves.extend(joinedCurve)
                
                elif len(joinedCurve)==1:
                    leg1 = rc.Geometry.Vector3d(joinedCurve[0].PointAtStart - cenPt)
                    leg2 = rc.Geometry.Vector3d(joinedCurve[0].PointAtEnd - cenPt)
                    midLeg = rc.Geometry.Vector3d.Add(leg1, leg2)
                    midLeg.Unitize()
                    midPt = rc.Geometry.Point3d.Add(cenPt, skyRadius * midLeg)
                    
                    arcSeg = rc.Geometry.Arc(joinedCurve[0].PointAtStart, midPt, joinedCurve[0].PointAtEnd).ToNurbsCurve()
                    
                    joinedCurve = rc.Geometry.Curve.JoinCurves([joinedCurve[0], arcSeg])
                    if len(joinedCurve)==1 and joinedCurve[0].IsClosed:
                        thisFaceCurves.extend(joinedCurve)
        #print thisFaceCurves
        # union curves
        unionedCrv = rc.Geometry.Curve.CreateBooleanUnion(thisFaceCurves)
        #print unionedCrv
        if len(unionedCrv)> 0:
            # add them to the rest of the curves
            planarCurves.extend(unionedCrv)
        else:
            planarCurves.extend(thisFaceCurves)
    # merge all the curves
    if merge:
        mergedPlanarCurves = rc.Geometry.Curve.CreateBooleanUnion(planarCurves)
        if len(mergedPlanarCurves)!=0:
            planarCurves = mergedPlanarCurves
        
    # segment the curves to project
    segments = []
    planarSrfs = []
    for planarCurve in planarCurves:
        segments.extend(planarCurve.DuplicateSegments())
        try: planarSrfs.extend(rc.Geometry.Brep.CreatePlanarBreps(planarCurve))
        except Exception, e: print e
    
    
    # project back to the geometry and split
    crvsOnSky = rc.Geometry.Curve.ProjectToBrep(segments, [sky], rc.Geometry.Vector3d.ZAxis, sc.doc.ModelAbsoluteTolerance)
    
    crvsOnSky = rc.Geometry.Curve.JoinCurves(crvsOnSky)
    
    skyDome = sky.Faces[0].Split(crvsOnSky, sc.doc.ModelAbsoluteTolerance)
    if skyDome == None:
        print "Split failed!"
        skyDome = sky
    
    
    return planarSrfs, crvsOnSky, skyDome, joinedContext

def main(cenPt, context, radius, merge):
    # import the classes
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
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1
        
    # create the sky geometry based on context bounding box
    BBSky, BBRadius = generateSkyGeo(cenPt, context)
    
    # calculate the mask
    planarSrfs, crvsOnSky, skyDome, joinedContext = getSkyMask(cenPt, context, BBSky, BBRadius, merge)
    
    
    # separate sky components
    maskedSkyDome = []
    unmaskedSkyDome = []
    
    for faceCount in range(skyDome.Faces.Count):
        surface = skyDome.Faces.ExtractFace(faceCount)
        srfCenPt = rc.Geometry.AreaMassProperties.Compute(surface).Centroid
        srfCenPt = rc.Geometry.Point3d(surface.ClosestPoint(srfCenPt))
        
        if not surface.IsValid:
            surface = surface.Faces.ExtractFace(0)
            
        if isMeshFaceVisible(cenPt, [srfCenPt], joinedContext):
            unmaskedSkyDome.append(surface)
        else:
            maskedSkyDome.append(surface)
    
    # join!
    #maskedSkyDome = list(rc.Geometry.Brep.JoinBreps(maskedSkyDome, sc.doc.ModelAbsoluteTolerance))
    
    # scale everything
    scaleT = rc.Geometry.Transform.Scale(cenPt, radius/BBRadius)
    for geo in planarSrfs + list(crvsOnSky) + maskedSkyDome + unmaskedSkyDome:
        geo.Transform(scaleT)
    
    return planarSrfs, crvsOnSky, maskedSkyDome, unmaskedSkyDome


if _testPt and len(_context)!=0 and _context[0]!=None:
    results = main(_testPt, _context, radius_, merge_)

    if results!=-1:
        maskedSrfOnGound, maskedCrvsOnSky, maskedSkyDome, unmaskedSkyDome = results