#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to see the portion of the sky dome that is masked by context geometry around a given viewpoint.
The component will generate separate meshs for the portions of the sky dome that are masked and visible.
The component will also calculate the percentage of the sky that is masked by the context geometry and the percentage that is visible (the sky view factor).
-
Provided by Ladybug 0.0.68
    
    Args:
        _testPt: A view point for which one wants to see the portion of the sky masked by the context geometry surrounding this point.
        _context: Context geometry surrounding the _testPt that could block the view to the sky.  Geometry must be a Brep or list of Breps. You are also advised to provide surfaces instead of solid objects. Providing surfces will make the calculation faster and accurate. So if you are using this component to check the percent of sky visible from a courtyard, please only provide surfaces immediate to the couryard and the not the whole building as a brep.
        skyDensity_: An integer, that is greater than or equal to 0. This value is used to generate test points on skyDome. from which the maskedSky surfaces are derived. The default value is set to 1. Incresing this value will increase the calculation time. You are adviced to increase this number only if you are trying to analyze too many shading surfaces.
        radius_: A float, that controls the radius of skyDome.
        merge_: A boolean. Set it to True to merge maskedSky surfaces
    Returns:
        maskedSrfOnGround: A list of surfaces. These are masked horizontal projections of maskedSky surfaces. They're useful when the skyDome is viewed from the top.
        maskedCrvsOnSky: A list of Curves. These are edge curves for maskedSky surfaces.
        maskedSkyDome: A list of surfaces. The portion of sky not blocked by the context geometry
        unmaskedSkyDome: A list of surfaces. The portion of sky blocked by the context geometry
        percMasked: Percentage of the sky blocked by the context geometry
"""

ghenv.Component.Name = "Ladybug_Shading Mask_II"
ghenv.Component.NickName = 'shadingMaskII'
ghenv.Component.Message = 'VER 0.0.68\nJAN_01_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import Rhino as rc
import math
import System
import scriptcontext as sc
import System.Threading.Tasks as tasks
import operator

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
    lineVector = rc.Geometry.Vector3d.XAxis
#    lineVector.Reverse()
    lineAxis = rc.Geometry.Line(cenPt, lineVector)
    
    # base plane to draw the arc
    basePlane = rc.Geometry.Plane(cenPt, rc.Geometry.Vector3d.ZAxis)
    baseVector = rc.Geometry.Vector3d.YAxis
        
    sectionCrv = rc.Geometry.Arc(basePlane, radius, math.pi).ToNurbsCurve()
    sky = rc.Geometry.RevSurface.Create(sectionCrv, lineAxis, 0 , math.pi).ToBrep()

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
        
        if len(intPts) >= 1: visiblePts.append(pt)
    
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


def checkTheInputs():
    skyDensity = 1
    if skyDensity_ != None:
        if skyDensity_ >= 0: skyDensity = skyDensity_
        else:
            warning = "skyDensity_ must be equal to or greater than 0."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            
    return skyDensity


def main(cenPt, context, skyDensity, radius, merge):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
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
    surfaceList = []  
    for faceCount in range(skyDome.Faces.Count):
        surface = skyDome.Faces.ExtractFace(faceCount)
        srfCenPt = rc.Geometry.AreaMassProperties.Compute(surface).Centroid
        if not surface.IsValid:
            surface = surface.Faces.ExtractFace(0)
        surfaceList.append(surface) 
              
    # Using skypatches to generate vectors for intersection with all skyDome surfaces
    skyPatches = lb_preparation.generateSkyGeo(cenPt, skyDensity, radius)
    vectorList = []
    pointList = []
    for patch in skyPatches:
        center = rc.Geometry.AreaMassProperties.Compute(patch)
        centerPt = center.Centroid
        vector = rc.Geometry.Vector3d(centerPt - cenPt)
        point = rc.Geometry.Point3d.Add(cenPt , vector)
        line = rc.Geometry.Line(cenPt, point)
        vectorList.append(vector)
    
    # Generating intersection points for all skyDome surfaces from vectors generated above
    surfacePoints = []
    for surface in surfaceList:
        catchList = []
        for vector in vectorList:
            catch = []
            catch = rc.Geometry.Intersect.Intersection.ProjectPointsToBreps([surface],[cenPt], vector, sc.doc.ModelAbsoluteTolerance)
            if len(catch) > 0:
                #print catch[0]
                catchList.append(catch[0])
            else:
                pass
        surfacePoints.append(catchList)
    
    # Making lines from all the intersecton points on skyDome surfaces and the testPt
    lineList = []
    for item in surfacePoints:
        lines = []
        for point in item:
            line = rc.Geometry.Line(point, cenPt)
            lines.append(line)
        lineList.append(lines)
    
    # Calculating the number of points per skyDome surface that intersect with the context geometry
    total = []
    for item in lineList:
        counter = 0
        for line in item:
            catch = []
            catch = rc.Geometry.Intersect.Intersection.MeshLine(joinedContext, line)
            if len(catch[0]) > 0:
                #print catch[0]
                counter += 1
        total.append(counter)
        
    # Making a dictionary of skyDome surfaces : number of points on skyDome surfaces that intersects the context geometry
    brepDict = dict(zip(surfaceList, total))
    # Sorting the dictionary to that surface with the least number of point that intersect with the context geometry remains
    # first on the list
    sortedDict = sorted(brepDict.items(), key = operator.itemgetter(1))
    # The surface on the skyDome with the least number of points that intersect with the context geometry are unmaskedSkyDome surfaces
    unmaskedSkyDome.append(sortedDict[0][0])
    # The rest are maskedSkyDome surfaces
    i = 1
    while i < len(sortedDict):
        maskedSkyDome.append(sortedDict[i][0])
        i += 1
    
    # Calculating percent of masked sky
    skyArea = 0
    for surface in surfaceList:
        area = rc.Geometry.AreaMassProperties.Compute(surface).Area
        skyArea += area
        
    maskedArea = 0
    for surface in maskedSkyDome:
        area = rc.Geometry.AreaMassProperties.Compute(surface).Area 
        maskedArea += area
        
    coveredPercent = (maskedArea*100) / skyArea
    coveredPercent = round(coveredPercent, 2)
    
    # scale everything
    scaleT = rc.Geometry.Transform.Scale(cenPt, radius/BBRadius)
    for geo in planarSrfs + list(crvsOnSky) + maskedSkyDome + unmaskedSkyDome:
        geo.Transform(scaleT)
    
    return planarSrfs, crvsOnSky, maskedSkyDome, unmaskedSkyDome, coveredPercent


if _testPt and len(_context)!=0 and _context[0]!=None:
    skyDensity = checkTheInputs()
    results = main(_testPt, _context, skyDensity, radius_, merge_)

    if results!=-1:
        maskedSrfOnGround, maskedCrvsOnSky, maskedSkyDome, unmaskedSkyDome, percMasked = results