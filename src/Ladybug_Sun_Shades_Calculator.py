# Sun Shades Calculator
# Copyright (c) 2017, Abraham Yezioro <ayez@technion.ac.il> and Antonello Di Nunzio <antonellodinunzio@gmail.com> 
# Sun Shades Calculator is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Sun Shades Calculator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# See <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to generate shading devices, either surface or pergola, for any glazed surface or list of glazed surfaces.  
The component first culls all sun vectors obstructed by the context, if provided.
By default it calculates the device as a "new brand" one but it also can calculate the cut profile for a given surface.
The default it will generate an overhang over the window (or multiple overhangs if the _numOfShds is increased).  
References:
Shaviv E., 1975. "A Method for the Design of Fixed External Sun-Shades". "Build International"  (8), Applied Science Publishers LTD, England, (pp.121-150).
Shaviv E., 1984. "A Design Tool for Determining the Form of Fixed & Movable Sun-Shades".  "ASHRAE Trans." Vol. 90, AT-84-18 No. 4, Atlanta (pp.1-14).

-
Provided by Ladybug 0.0.65
    
    Args:
        _SurfaceOrPergola_: 0= Device optimised for period, will give the horizontal or tilted surface over the top of the window, or the cut profile device on a provided shading surface. 1= Pergola with fins. Default is 0.
        _window: A Surface or Brep representing a window to be used for shading design.  This can also be a list of Surfaces of Breps.
        _numOfShds_: The number of shades to generated for each window.
        _udiv_: Number of row divisions of the window. Used for choosing the lower and higher rows you want to protect. Default is 3.
        _sunVectors: Sun vectors from the sunPath component.
        context_: Breps/surfaces that you want to account for as blocking objects. Using it you'll get the shading shape needed for the specific situation.
        shadeSurface_: An optional shade surface representing a 2D area under consideration for shading. This input can only be used with the sun vector method.
        ---------------: ...
        _shdSrfAngle_: In case NO shadeSurface is provided a plane over the window will be used as base for the calculation. In this case you can provide the angle of this plane. Default is 0.0.
        _shdSrfShift_: In case NO shadeSurface is provided a plane over the window will be used as base for the calculation. n this case you can provide a shift distance from top of the window. Default is 0.01
        _numPergolaFins_: "Number of pergola fins. Default is 10.
        _finsAngle_: "Angle for pergola fins. Default is 45.
        ---------------: ...
        _delaunayHeight_: Distance from base curve and top intersection points. Used by the Delauney Mesh component. Default is 5.
        _offsetFactor_: VERY important input!! The offset factor for the ConvexHull curve. Will be used for the Delauneay mesh. Default is 40.
        _res_: Divide the offset curve for the Delaunay operation.
    Returns:
        readMe!: ...
        pointsOnWindow: Net of points on window
        uPoints: Net of points on window
        ptsContext: Show the intersection point of sun vectors with context
        cullPts: Show the points that define the contour of the shading device. Pay attention to those more/less dense areas covered by these points.
        finalSrf: Surface representing the shape of the shading device.
"""
##print 'In sunShades'
ghenv.Component.Name = "Ladybug_Sun_Shades_Calculator"
ghenv.Component.NickName = 'SunShades_Calc'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


# modules
import Rhino as rc
import scriptcontext as sc
import ghpythonlib.components as ghc

import math as m

# For accesssing GH classes
# #########################################
import System
from System import Object
import clr
clr.AddReference("Grasshopper")
import Grasshopper.Kernel as gh
from Grasshopper.Kernel.Data import GH_Path                     # For creating Path for Data Tree
from Grasshopper import DataTree                                # For creating Data Tree
# #########################################

inputsDict = {
     
0:  ["_SurfaceOrPergola_", "0= Device optimised for period, will give the horizontal or tilted surface over the top of the window,"\
    " or the cut profile device on a provided shading surface. 1= Pergola with fins. Default is 0."],
1:  ["_window", "A Surface or Brep representing a window to be used for shading design.  This can also be a list of Surfaces of Breps."],
2:  ["_numOfShds_", "The number of shades to generated for each glazed surface."],
3:  ["_udiv_", "Number of row divisions of the window. Used for choosing the lower and higher rows you want to protect. Default is 1."],
4:  ["_sunVectors", "Output of Ladybug sunPath component."],
5:  ["context_", "Breps/surfaces that you want to account for as blocking objects. "],
6:  ["shadeSurface_", "An optional shade surface representing a 2D area under consideration for shading. "],
7:  ["---------------", "---------------"],
8:  ["_shdSrfAngle_", "In case NO shadeSurface is provided a plane over the window will be used as base for the calculation. " \
    "In this case you can provide the angle of this plane. Default is 0.0."],
9: ["_shdSrfShift_", "In case NO shadeSurface is provided a plane over the window will be used as base for the calculation. " \
    "In this case you can provide a shift distance from top of the window. Default is 0.01" ],
10:  ["_numPergolaFins_", "Number of pergola fins. Default is 10."],
11: ["_finsAngle_", "Angle for pergola fins. Default is 45."],
12: ["---------------", "---------------"],
13: ["_delaunayHeight_", "Distance from base curve and top intersection points. Used by the Delauney Mesh component. Default is 5."],
14: ["_offsetFactor_", "VERY important input!! The offset factor for the ConvexHull curve. Will be used for the Delauneay mesh. Default is 40."],
15: ["_res_", "Divide the offset curve for the Delaunay operation."],
}

# manage component inputs

if _SurfaceOrPergola_ == None: _SurfaceOrPergola_ = 0
numInputs = ghenv.Component.Params.Input.Count

if _SurfaceOrPergola_ == 0 and shadeSurface_ == None:
    for input in range(numInputs):
        if input == 9 or input == 10:
            ghenv.Component.Params.Input[input].NickName = "."
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
            ghenv.Component.Attributes.Owner.OnPingDocument()
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
elif _SurfaceOrPergola_ == 1 and shadeSurface_ == None:
    for input in range(numInputs):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
elif (_SurfaceOrPergola_ == 0 or _SurfaceOrPergola_ == 2) and shadeSurface_ != None:
    for input in range(numInputs):
        if input == 7 or input == 8 or input == 9 or input == 10:
            ghenv.Component.Params.Input[input].NickName = "."
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
elif _SurfaceOrPergola_ == 1 and shadeSurface_ != None:
    for input in range(numInputs):
        if input == 7 or input == 8:
            ghenv.Component.Params.Input[input].NickName = "."
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
else:
    for input in range(numInputs):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
            
ghenv.Component.Attributes.Owner.OnPingDocument()

# functions
def giveWarning(warningMsg):
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, warningMsg)
    print warningMsg
    return -1

def checkTheData(window, sunVectors, context):
    contextFlag = True
    if context:
        for i in range(len(context)):
            if context[i] == None:
                warning = "Context has Null items. Please clean them and try again"
                giveWarning(warning)
                contextFlag = False
    if not window or not sunVectors or (context and contextFlag == False):
        checkData = False
    elif window and sunVectors:
        checkData = True
    else: checkData = True
    return checkData


def identifyRectangularWindow(window):
    pts = rc.Geometry.Brep.DuplicateVertices(window)
    
    if len(pts) == 4:
        points = rc.Collections.Point3dList(pts)
        points_Sort = rc.Geometry.Point3d.SortAndCullPointList(points, sc.doc.ModelAbsoluteTolerance)
        if points_Sort[0][0] == points_Sort[1][0] and points_Sort[0][1] == points_Sort[1][1] and \
           points_Sort[2][0] == points_Sort[3][0] and points_Sort[2][1] == points_Sort[3][1] and \
           points_Sort[0][2] == points_Sort[3][2] and points_Sort[1][2] == points_Sort[2][2]:
           rectangularWindow = True
        else:
            rectangularWindow = False
    else:
        rectangularWindow = False
    return rectangularWindow

def pointsOfWindow(window, udiv, numOfShds):
    rectangularWindow = identifyRectangularWindow(window)
    if rectangularWindow == False:
        print 'NO rectangular window'
        pointsOnWindow = []
        edges = window.DuplicateEdgeCurves()
        if len(edges) == 1:
            t_vals = edges[0].DivideByCount(udiv + 10, True)
            for t in t_vals:
                pointsOnWindow.append(edges[0].PointAt(t))
            
        else:
            points = []
            for edge in edges:
                t_vals = edge.DivideByCount(udiv, True)
                for t in t_vals:
                    points.append(edge.PointAt(t))
            
            pointsOnWindow = rc.Geometry.Point3d.CullDuplicates(points, sc.doc.ModelAbsoluteTolerance)
    else:
        #print 'YES rectangular window'
        pts = rc.Geometry.Brep.DuplicateVertices(window)
        
        points = rc.Collections.Point3dList(pts)
        points_Sort = rc.Geometry.Point3d.SortAndCullPointList(points, sc.doc.ModelAbsoluteTolerance)
        
    
        frame = []
        frame.append(rc.Geometry.LineCurve( points_Sort[1], points_Sort[0]) )    # in RS the order was 0 and 1
        frame.append(rc.Geometry.LineCurve( points_Sort[0], points_Sort[3]) )
        
        ##vCol = rc.Geometry.Curve.DivideByCount(frame[0], udiv, True)
        vCol = rc.Geometry.Curve.DivideByCount(frame[0], numOfShds, True)
        uRow = rc.Geometry.Curve.DivideByCount(frame[1], udiv, True)
        verP = []
        horP = []
        for t in vCol:
            verP.append(frame[0].PointAt(t))
        for t in uRow:
            horP.append(frame[1].PointAt(t))
        
        vPoints = []
        uPoints = []
        for i in range(0, len(verP) + 0, 1): #vdiv or numOfShds
            for j in range(0, len(horP) + 0, 1):
                newPt = ( rc.Geometry.Point3d(horP[j][0], horP[j][1], verP[i][2]) )
                uPoints.append(newPt)   # This is the full grid of point on window
        row1 = 0                        # First row of points. Usually the bottom line
        row2 = numOfShds #vdiv               # Top row of points. Usually the top line
        rowsOfWindows = 2               # Number of rows to calculate later on. Should be 2
        pointsOnWindow = []
        start = row1 * udiv +row1
        end = start + udiv
        #print start, end
        start1 = row2 * udiv +row2
        end1 = start1 + udiv
        #print start1, end1
        
        for i in range(start, end +1, 1):
            pointsOnWindow.append( uPoints[i] )
        for i in range(start1, end1 +1, 1):
            pointsOnWindow.append( uPoints[i] )
    
    return pointsOnWindow, uPoints

def loopRowPoints(uPoints, udiv, numOfShds):
    row1 = 0               # First row of points. Usually the bottom line
    start = row1 * udiv
    end   = start + udiv
    groupPoints = []
    rowPoints   = []
    for i in range(1, numOfShds + 1, 1): # Start from row 1. Row 0 is the bottom one.
        start1 = i * udiv + i
        end1 = start1 + udiv
        groupPoints.append((start, end, start1, end1))
        start = start1# + udiv + 1
        end   = end1#   + udiv + 1
    
    for i in range(len(groupPoints)):
        tmpPts = []
        for j in range(groupPoints[i][0], groupPoints[i][1] + 1, 1):
            tmpPts.append( uPoints[j] )
        for j in range(groupPoints[i][2], groupPoints[i][3] + 1, 1):
            tmpPts.append( uPoints[j] )
        rowPoints.append(tmpPts)
    return rowPoints, groupPoints

def isSrfFacingTheVector(sunV, normalVector):
    sunVRev = rc.Geometry.Vector3d(sunV)
    sunVRev.Reverse()
    #print math.degrees(rc.Geometry.Vector3d.VectorAngle(sunVRev, normalVector))
    if rc.Geometry.Vector3d.VectorAngle(sunVRev, normalVector) < m.pi/2: return True
    else: return False

def getSrfPlane(brep):
    cenPt = rc.Geometry.AreaMassProperties.Compute(brep).Centroid
    # sometimes the center point is not in the right place
    cenPt = brep.ClosestPoint(cenPt)
    bool, centerPtU, centerPtV = brep.Faces[0].ClosestPoint(cenPt)
    normalVector = brep.Faces[0].NormalAt(centerPtU, centerPtV)
    return rc.Geometry.Plane(cenPt, normalVector), cenPt

def raysIntersection(rays, shade):
    if   sc.doc.ModelAbsoluteTolerance * 1000 <=   5: tolFactor = 100   #0.001
    elif sc.doc.ModelAbsoluteTolerance * 1000 <=  50: tolFactor = 10    #0.01
    elif sc.doc.ModelAbsoluteTolerance * 1000 <= 500: tolFactor = 1     #0.1
    points_on_ShdSrf = []
    for i, ray in enumerate(rays):
        # ShdSrf intersection
        int = rc.Geometry.Intersect.Intersection.RayShoot(ray, shade, 1)
        if int != None:
            points_on_ShdSrf.extend(int)
    points = rc.Geometry.Point3d.CullDuplicates(points_on_ShdSrf, sc.doc.ModelAbsoluteTolerance * tolFactor) # Rhino Tolerance is too low that no point are culled

    return points

def fromPlaneToSrf(plane):
    # This because rays method doesn't work with plane
    rectangle = rc.Geometry.Rectangle3d(plane, 100, 100)
    segments = rectangle.ToNurbsCurve().DuplicateSegments()
    shadeSurface = rc.Geometry.Brep.CreateEdgeSurface(segments)
    
    # generate vector
    cenPt = rc.Geometry.AreaMassProperties.Compute(shadeSurface).Centroid
    linea_plane = rc.Geometry.Line(cenPt, plane.Origin)
    vector_plane_scale = linea_plane.Direction
    
    # move it in the right place
    shadeSurface.Translate(vector_plane_scale)
    
    return shadeSurface

def calcIntersections(shadeSurface, pointsOnWindow, grPt, sunVectors, shdSrfShift, shdSrfAngle, window, context):
    ##################################################################### WINDOW
    # from Brep to surface
    surface_window = window.Surfaces[0]
    
    # find the normal of each surface
    brepPlane, cenPt = getSrfPlane(window)
    normalVector = brepPlane.Normal
    
    ######################################################### PLANE IF NO SHDSRF
    
    if shadeSurface: # for very complex pergola shades
        # tangents vectors
        vec = rc.Geometry.Surface.Evaluate(surface_window, 0.5, 0.5, 1)[2]
        
        # select the normal vector for the plane
        z_vectors = []
        for v in vec:
            z_vectors.append(abs(v[2]))
        vector_p = vec[z_vectors.index(min(z_vectors))]
    
    else:
    #if not shadeSurface:
        # find the point with the maximum z
        z_values = []
        for pt in pointsOnWindow:
            z_values.append(pt[2])
        
        base_point = pointsOnWindow[z_values.index(max(z_values))]
        
        # tangents vectors
        vec = rc.Geometry.Surface.Evaluate(surface_window, 0.5, 0.5, 1)[2]
        
        # select the normal vector for the plane
        z_vectors = []
        for v in vec:
            z_vectors.append(abs(v[2]))
        vector_p = vec[z_vectors.index(min(z_vectors))]
        
        # set the translation and rotation of the plane
        vector_movePlane = rc.Geometry.Vector3d(0, 0, shdSrfShift)
        xtrans = rc.Geometry.Transform.Translation(vector_movePlane)
        base_point.Transform(xtrans)
        
        # make the plane
        plane = rc.Geometry.Plane(base_point, vector_p, normalVector)
        plane.Rotate(m.radians(shdSrfAngle), vector_p, base_point)
        
        # compatible rotation with the sun rays direction
        bool, linea_test = rc.Geometry.Intersect.Intersection.PlanePlane(plane, rc.Geometry.Plane.WorldXY)
        point_test = linea_test.PointAt(0.5)
        line_from_point = rc.Geometry.Line(point_test, cenPt)
        direction_test = line_from_point.Direction
        if isSrfFacingTheVector(direction_test, normalVector) == False:
            plane.Rotate(m.radians(-shdSrfAngle * 2), vector_p, base_point)
            
    ############################################################## INTERSECTIONS
    # generate rays
    sun_lines = []
    sun_rays = []
    length_vector = 50   ### Check for a better definition!!!
    for point in pointsOnWindow:
        for sunV in sunVectors:
            if isSrfFacingTheVector(sunV, normalVector):
                sun_lines.append(rc.Geometry.Line(point, -sunV * length_vector))
                sun_rays.append(rc.Geometry.Ray3d(point, -sunV))
    lines = sun_lines
    
    # effect of the context
    ptsContext = []
    contextVectors  = []
    noContextVectors = []
    if context:
        rays = []
        # intersection
        for i, ray in enumerate(sun_rays):
            intersection = rc.Geometry.Intersect.Intersection.RayShoot(ray, context, 1)
            if intersection == None:
                noContextVectors.append(sun_lines[i])
                rays.append(sun_rays[i])
            else:
                contextVectors.append(sun_lines[i])
                for p in intersection:
                    ptsContext.append( p )
        sun_rays = rays
    
    # intersections
    if shadeSurface:
        cullPts = raysIntersection(sun_rays, [shadeSurface])
    else:
        shadeSurface = fromPlaneToSrf(plane)
        cullPts = raysIntersection(sun_rays, [shadeSurface])
    
    return cullPts, ptsContext, normalVector, cenPt, vector_p

def finalSurfStuff(cullPts, delaunayHeight, offsetFactor, shadeSurface):
    
    worldPlane = rc.Geometry.Plane.WorldXY
    if shadeSurface == None:    # In case no shading surface was provided
        planeFromPoints = rc.Geometry.Plane.FitPlaneToPoints(cullPts)
    else:    # In case shading surface was provided
        points_surface = ghc.SurfacePoints(shadeSurface).points
        
        planeFromPoints = rc.Geometry.Plane.FitPlaneToPoints(points_surface)[1]##
        #planeFromPoints = rc.Geometry.Plane.FitPlaneToPoints(points_surface)[1]##

    if planeFromPoints:
        wp  = worldPlane.Normal
        if shadeSurface == None:    # In case no shading surface was provided
            pfp = rc.Geometry.Plane.Normal.GetValue(planeFromPoints[1])
        else:    # In case shading surface was provided
            pfp = rc.Geometry.Plane.Normal.GetValue(planeFromPoints)
        
        vectorAngle = rc.Geometry.Vector3d.VectorAngle(pfp, wp)
        tolAngle = 70       # Tolerance angle. Right now I set it to 70 but this should be followed up
        if ((vectorAngle >= tolAngle) and (vectorAngle <= 90)) or (vectorAngle >= tolAngle and (vectorAngle < (90 + (90 - tolAngle)))):
            flag = 0        #0 is for VERTICAL shading surface
        elif(vectorAngle < tolAngle) or (vectorAngle > (90 + (90 - tolAngle))):
            flag = 1        #1 is for NON VERTICAL shading surface
            
        if flag == 0:
            worldZXPlane = rc.Geometry.Plane.WorldZX
            worldYZPlane = rc.Geometry.Plane.WorldYZ
            
            wp_ZX = worldZXPlane.Normal * -(1)
            wp_YZ = worldYZPlane.Normal * -(1)
            
            vectorAngle_ZX = rc.Geometry.Vector3d.VectorAngle(pfp, wp_ZX)
            vectorAngle_YZ = rc.Geometry.Vector3d.VectorAngle(pfp, wp_YZ)
            
            if vectorAngle_ZX <=45 or vectorAngle_ZX >=135 and worldYZPlane <= 225:
                basePlane = worldZXPlane
                convexHullPlane = cutPlane = rc.Geometry.Plane.WorldZX
                
                convexHullPlane = rc.Geometry.Plane.Translate(convexHullPlane, worldZXPlane.Normal * -delaunayHeight)

                convex_Trim_Plane = convexHullPlane
                cutPlane = rc.Geometry.Plane.Translate(cutPlane, worldZXPlane.Normal * -(delaunayHeight - .01))
                
                directionPlane = cutPlane
            else:
                basePlane = worldYZPlane
            
            G, X = ghc.MoveToPlane(cullPts, convexHullPlane, True, True)
            delaunayPoints1 = G
            flatPts = [ rc.Geometry.Point3d( p ) for p in delaunayPoints1 ]
       
        elif flag == 1:
            convex_Trim_Plane = rc.Geometry.Plane.WorldXY        # Connect to ConvexHull and MeshPlaneSec
            
            convexHullPlane = convex_Trim_Plane
            p1 = rc.Geometry.Point3d( 0, 0, delaunayHeight - 0.01)
            v1 = rc.Geometry.Vector3d(1, 0, 0)
            v2 = rc.Geometry.Vector3d(0, 1, 0)
            directionPlane    = rc.Geometry.Plane( p1, v1, v2 )        # Connect to Direction input of Project

            direction  =  rc.Geometry.Vector3d.Add( rc.Geometry.Vector3d(0, 0, 0), rc.Geometry.Vector3d(0, 0, delaunayHeight))        # Connect to Direction input of Project     
            #Using RS the direction is 0,0,5. Using RC direction is 0,0,-5. Be aware of this, maybe we need to multiply by (-1) 
           
            flatPts = [ rc.Geometry.Point3d( p ) for p in cullPts ]
            
            for i in range(len(cullPts)):               # Flat Z axis point to some height for the DelaunayMesh action
                flatPts[i][2] = delaunayHeight
                
            trimPlanePoint = rc.Geometry.Point3d(0,0, delaunayHeight - 0.01)
        
    ###################    
    spans = 20
    flexibility = 1
    points_CULL = [rc.Geometry.Point(pt) for pt in cullPts]
    patch = ghc.Patch(None, cullPts, spans, flexibility, True) 
    if flag == 0:
        H, Hz, I = ghc.ConvexHull(cullPts, rc.Geometry.Plane.WorldZX)       # CHECK THIS LATER FOR OTHER CASES or UNIFY WITH FLAG 1
    elif flag == 1:
        H, Hz, I = ghc.ConvexHull(cullPts, convexHullPlane)

    points_PV = []
    count = H.PointCount
    for i in range(count):
        points_PV.append(H.Point(i))
    
    H_alt     = rc.Geometry.PolylineCurve(points_PV)
    areaH     = rc.Geometry.AreaMassProperties.Compute(H).Area
    centH_alt = rc.Geometry.AreaMassProperties.Compute(H).Centroid

    scaleH    = rc.Geometry.Transform.Scale(centH_alt, offsetFactor)
    dupH_alt  = rc.Geometry.PolylineCurve.Duplicate(H_alt)
    dupH_alt.Transform(scaleH)
    offsetCrv = [dupH_alt]
    
    areaHalt      = rc.Geometry.AreaMassProperties.Compute(H_alt).Area
    areaoffsetCrv = rc.Geometry.AreaMassProperties.Compute(offsetCrv[0]).Area
    
    if (areaHalt > areaoffsetCrv):
        print "Case BAD offset"
        scaleH    = rc.Geometry.Transform.Scale(centH_alt, offsetFactor * (-1))
        dupH_alt  = rc.Geometry.PolylineCurve.Duplicate(H_alt)
        dupH_alt.Transform(scaleH)
        offsetCrv = [dupH_alt]

    delaunayPoints = []
    for i in range(len(cullPts)):               # Flat Z axis point to some height for the DelaunayMesh action
        delaunayPoints.append(flatPts[i])
        
    res = 40
    divCrv = offsetCrv[0].DivideByCount(res, True)
    
    for p in divCrv:
        delaunayPoints.append(offsetCrv[0].PointAt(p))
        
    delaunayMesh = ghc.DelaunayMesh(delaunayPoints, convex_Trim_Plane)
    M = delaunayMesh 
    trimCurve = ghc.MeshXPlane(delaunayMesh, directionPlane) 
    projectedCrv = ghc.Project(trimCurve, patch, directionPlane)
    splitSrf = ghc.SurfaceSplit(patch, projectedCrv)
    

    H1, Hz1, I1 = ghc.ConvexHull(cullPts, planeFromPoints)
    cen = rc.Geometry.AreaMassProperties.Compute(H1).Centroid
    centerH = rc.Geometry.Point3d(cen)
    #print centerH
    
    distances = []
    for srf in splitSrf:
        cent = rc.Geometry.AreaMassProperties.Compute(srf).Centroid
        distance = centerH.DistanceTo(cent)
        #print distance
        distances.append(distance)
        
    finalSrf = splitSrf[distances.index(min(distances))]
    
    """
    # Below the original way to solve the issue ##
    if shadeSurface:
        H1, Hz1, I1 = ghc.ConvexHull(cullPts, planeFromPoints)
        cen = rc.Geometry.AreaMassProperties.Compute(H1).Centroid
        centerH = rc.Geometry.Point3d(cen)
        #print centerH

        uv = rc.Geometry.Surface.ClosestPoint(shadeSurface, centerH)
        point = rc.Geometry.Surface.Evaluate(shadeSurface, uv[0], uv[1], 10)

    s0 = splitSrf[0]
    s1 = splitSrf[1]
    
    swapFinalSrf = False
    if swapFinalSrf ==False:
        finalSrf = splitSrf[1]
    else:
        finalSrf = splitSrf[0]
    """

    return finalSrf


def calculatePergola(finalSrf, vectorP, normalVector, cenPt, numPergolaFins, finsAngle, sunVectors):
    ##################################################################### CURVES
    # use Untrimmed surface (Domain shape)
    flat_srf = finalSrf.Surfaces[0].ToBrep()
    
    # boudary box & center
    bbox = finalSrf.GetBoundingBox(True)
    center = bbox.Center
    
    
    # cutter plane
    cut_plane = rc.Geometry.Plane(center, vectorP)
    
    
    # make a line where to put all planes
    curves_for_planes = rc.Geometry.Intersect.Intersection.BrepPlane(flat_srf, cut_plane, sc.doc.ModelAbsoluteTolerance)[1]# attention! sometimes the intersections are multiple
    if len(curves_for_planes) > 1:
        curve = rc.Geometry.Curve.JoinCurves(curves_for_planes, 1) # I'm not sure this tolerance can works for all cases, we need a big tolerance value to join difficult curves
        curve_for_planes = curve[0]
    else:
        curve_for_planes = curves_for_planes[0]
    if cenPt.DistanceTo(curve_for_planes.PointAtStart) < cenPt.DistanceTo(curve_for_planes.PointAtEnd):
        curve_for_planes.Reverse()
    
    
    # if curve for planes is not horizontal
    start_point = curve_for_planes.PointAtStart
    end_point = curve_for_planes.PointAtEnd
    
    if  start_point[2] != end_point[2]:
        end_point_updated = rc.Geometry.Point3d(end_point[0], end_point[1], start_point[2])
        line_base = rc.Geometry.Line(start_point, end_point_updated)
        curve_for_planes_straight = line_base.ToNurbsCurve()
    else: curve_for_planes_straight = curve_for_planes.ToNurbsCurve()
    
    
    # find the brep points
    finalSrf_crv = rc.Geometry.Brep.DuplicateEdgeCurves(finalSrf)
    
    point_finalSrf = []
    test = []
    for crv in finalSrf_crv:
        segments = crv.DuplicateSegments()
        for segment in segments:
            point_finalSrf.append(segment.PointAtStart)
            point_finalSrf.append(segment.PointAtEnd)
    point_finalSrf = rc.Geometry.Point3d.CullDuplicates(point_finalSrf, sc.doc.ModelAbsoluteTolerance)
    
    
    # find the best size of the curve_for_planes_straight
    if point_finalSrf == None or point_finalSrf == 1: # when you connect Ladybug_ShadingDesigner or Rhino surface
        rc.Geometry.Curve.Domain.SetValue(curve_for_planes_straight, rc.Geometry.Interval(0, 1.00))
        
    else:
        parameters_on_strcrv = []
        
        for point in point_finalSrf:
            bool, t = rc.Geometry.NurbsCurve.ClosestPoint(curve_for_planes_straight, point)
            if bool:
                parameters_on_strcrv.append(t)
        start_point_size = curve_for_planes_straight.PointAt(min(parameters_on_strcrv))
        end_point_size = curve_for_planes_straight.PointAt(max(parameters_on_strcrv))
        
        curve_for_planes_straight = rc.Geometry.Line(start_point_size, end_point_size).ToNurbsCurve()
    
    # check01- num_division
    if numPergolaFins <= 1:
        warning = "Please set a number of division greater or equals than 2"
        giveWarning(warning)
        return -1
        
    # make multiple planes & find the intersection curves
    curves = []
    planes = []
    points = []
    for i in range(numPergolaFins + 1): # (+1)to generate also the last plane.. I have to check if it works for all cases
        plane = rc.Geometry.NurbsCurve.PerpendicularFrameAt(curve_for_planes_straight, i / numPergolaFins)[1]
        point = curve_for_planes_straight.PointAt(i / numPergolaFins)
        
        points.append(point)
        planes.append(plane)
        
        bool, curve_points, a = rc.Geometry.Intersect.Intersection.BrepPlane(finalSrf, plane, sc.doc.ModelAbsoluteTolerance * 0.1) # we need some factors, sometimes pergola could disappear
        if bool:
            curves.extend(curve_points)
    
    ##################################################################### HEIGHT
    
     # find the right height
    distances = []
    point_on_shd = []
    for point in points:
        distances.append(point.DistanceTo(cenPt))
        point_on_shd.append(flat_srf.ClosestPoint(point))
    if distances[0] > distances[len(distances)-1]:
        ###print('all reverse')
        curves.reverse()
        planes.reverse()
    
    
    # generate vectors to move the planes
    pointsOnSurface = rc.Geometry.Intersect.Intersection.ProjectPointsToBreps([flat_srf], points, rc.Geometry.Vector3d.ZAxis, sc.doc.ModelAbsoluteTolerance * 0.1)
    for i, p in enumerate(points):
        vec = rc.Geometry.Vector3d.Add(rc.Geometry.Vector3d(pointsOnSurface[i]), -rc.Geometry.Vector3d(p))
        rc.Geometry.Plane.Translate(planes[i], vec)
        rc.Geometry.Plane.Rotate(planes[i], m.radians(-finsAngle), vectorP, planes[i].Origin)
    
    # point useful to find the right height
    gen_point = planes[0].Origin

    ############################################################## INTERSECTIONS
    
    # it comes from 'Ladybug_ShadingDesigner'
    def isSrfFacingTheVector_TRSH(sunV, normalVector):
        sunVRev = rc.Geometry.Vector3d(sunV)
        sunVRev.Reverse()
        if rc.Geometry.Vector3d.VectorAngle(sunVRev, normalVector) < m.pi/2: return True
        else: return False
    
    
    # generate lines
    sun_lines = []
    for sunV in sunVectors:
        if isSrfFacingTheVector(sunV, normalVector):
            sun_lines.append(rc.Geometry.Line(gen_point, -sunV, 1000))
    
    # select a plane and find intersection point
    pp = planes[1]
    useful_points = []
    for line in sun_lines:
        t = rc.Geometry.Intersect.Intersection.LinePlane(line, pp)[1]
        point = line.PointAt(t)
        useful_points.append(point)
    
    # make a long line to project points onto it
    def lineForHeight(plane_dist, bool, factor):
        distances_point_gen = []
        points_projected = []
        asse = plane_dist.YAxis
        long_line = rc.Geometry.Line(plane_dist.Origin, asse, 1000)
        for point in useful_points:
            points_on_line = rc.Geometry.Line.ClosestPoint(long_line, point, bool) #True
            points_projected.append(points_on_line)
            distance = points_on_line.DistanceTo(plane_dist.Origin)
            distances_point_gen.append(distance)
        # make the vector for the extrusion
        max_point = points_projected[distances_point_gen.index(max(distances_point_gen))]
        
        vec_extrude = factor * rc.Geometry.Vector3d.Add(-rc.Geometry.Vector3d(plane_dist.Origin), rc.Geometry.Vector3d(max_point)) #+
        
        return vec_extrude, max_point
    
    vec_extrude, max_point = lineForHeight(pp, True, 1)
    
    if max_point == pp.Origin:
        vec_extrude, max_point = lineForHeight(pp, False, -1)
        
    pergola = []
    for crv in curves:
        pergola.append(rc.Geometry.Extrusion.CreateExtrusion(crv, vec_extrude))

    return pergola

def main():
    
    # inputs
    window = _window
    sunVectors = _sunVectors
    try:
        _numPergolaFins_
        _shdSrfShift_
    except:
        _numPergolaFins_ =  None
        _shdSrfShift_    = None


    if _numOfShds_       == None:                         numOfShds         = 1
    else:                                                 numOfShds         = _numOfShds_
    if _numPergolaFins_  == None:                         numPergolaFins    = 10
    else:                                                 numPergolaFins    = _numPergolaFins_
    if _finsAngle_       == None:                         finsAngle         = 45
    else:                                                 finsAngle         = _finsAngle_
    if _shdSrfShift_     == None or _shdSrfShift_ == 0.0: shdSrfShift       = 0.01
    else:                                                 shdSrfShift       = _shdSrfShift_
    if _shdSrfAngle_     == None:                         shdSrfAngle       = 0.0
    else:                                                 shdSrfAngle       = _shdSrfAngle_
    if _delaunayHeight_  == None:                         delaunayHeight    = 5.0
    else:                                                 delaunayHeight    = _delaunayHeight_
    if _udiv_            == None:                         udiv              = 6
    else:                                                 udiv              = _udiv_ 
    if _offsetFactor_    == None:                         offsetFactor      = 40
    else:                                                 offsetFactor      = _offsetFactor_
    
    # points
    pointsOnWindow, uPoints = pointsOfWindow(window, udiv, numOfShds)

    rowPoints, groupPoints = loopRowPoints(uPoints, udiv, numOfShds)  # rowPoints is a list of lists. The output looks like IronPython.Runtime.List

    finalSrf      = []
    allCullPts    = []
    allptsContext = []
    for i in range(len(rowPoints)):    # List or pair of rows index points (Upoints) to be analysed later on
        # intersections
        cullPts, ptsContext, normalVector, cenPt, vector_p = calcIntersections(shadeSurface_, rowPoints[i], groupPoints[i], sunVectors, shdSrfShift, shdSrfAngle, window, context_)
        
        allptsContext.extend(ptsContext)
        
        if cullPts == None:   # Some special cases there are point but no surface is created. SO just to be on the safe side
            warning = "No enough intersection points to calculate the shading surface"
            giveWarning(warning)
            finalSrf = None
        elif len(cullPts) < 4:   # Some special cases there are point but no surface is created. SO just to be on the safe side
            warning = "No enough intersection points to calculate the shading surface"
            giveWarning(warning)
            finalSrf = None
        else:
            allCullPts.extend(cullPts)
            finalSrf_TMP = finalSurfStuff(cullPts, delaunayHeight, offsetFactor, shadeSurface_)
            if finalSrf_TMP != -1: 
                print "Shading Calculation is done!"
                if _SurfaceOrPergola_ == 1:
                    finalSrf.extend( calculatePergola(finalSrf_TMP, vector_p, normalVector, cenPt, numPergolaFins, finsAngle, sunVectors) )
                else:
                    finalSrf.append( finalSurfStuff(cullPts, delaunayHeight, offsetFactor, shadeSurface_) )
    return finalSrf, allCullPts, allptsContext, pointsOnWindow, uPoints


#Check the data
#checkData = False
checkData = checkTheData(_window, _sunVectors, context_)
if checkData == True:
    result = main()
    if result != -1:
        ##finalSrf, cullPts, ptsContext = result
        finalSrf, cullPts, ptsContext, pointsOnWindow, uPoints = result
else:
    warning = 'Please provide all _inputs'
    giveWarning(warning)
    
    
"""    
#Hide(True)/Show(False) outputs
ghenv.Component.Params.Output[1].Hidden   = True     # pointsOnWindow
ghenv.Component.Params.Output[2].Hidden   = True     # uPoints
ghenv.Component.Params.Output[3].Hidden   = True     # PtsContext
ghenv.Component.Params.Output[4].Hidden   = True     # cullPts
ghenv.Component.Params.Output[5].Hidden   = False    # finalSrf
"""
ghenv.Component.Params.Output[1].Hidden   = True     # pointsOnWindow
ghenv.Component.Params.Output[2].Hidden   = True     # uPoints
ghenv.Component.Params.Output[3].Hidden   = True     # PtsContext
ghenv.Component.Params.Output[4].Hidden   = True     # cullPts
ghenv.Component.Params.Output[5].Hidden   = False    # finalSrf
    