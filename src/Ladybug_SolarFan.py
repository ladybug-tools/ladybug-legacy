# Solar Fan
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2020, Mostapha Sadeghipour Roudsari and Chris Mackey <mostapha@ladybug.tools and Chris@MackeyArchitecture.com> 
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
Use this component to generate a solar fan for a given test surface and set of solar vectors.  Solar fans essentially illustrate the volume that should be clear of shading in order to provide solar access to a test surface for a given set of sun vectors.
Solar fans are typically used to ensure solar access for park vegetation in the midst of large developments constructed around it.  It can be also used to ensure solar access for windows that might want to use the sun for heating for ceratin hours of the year.

-
Provided by Ladybug 0.0.68
    
    Args:
        _baseSrf: A surface representing a piece of land (such as a park) or a window for which solar access is desired.
        _sunVectors: Sun vectors representing hours of the year when sun should be accessible to the baseSrf. sunVectors can be generated using the Ladybug sunPath component.
        _size_: Input a number here to change how far the solar fan extends from the _baseSrf.  The default is set to 1, which will produce a solar fan that is half as tall as the longest side of the _baseSrf. Note that increasing the height too high can cause the fan to break up into multiple fans due to the resolution of the solar vectors.
        _runIt: Set to "True" to run the analysis and generate a solar fan. Note that, for more than 500 sunVectors, calculation times can take more than a half-minute.
        noUnion_: By default this component will attempt to boolean union all the solar fans created, sometimes the underlying boolean union rhino operation fails and as a result only some of the solar fans are created.
        When this happens you can set this input to false and the boolean union operation will not be performed on the solar fans ensuring that all solar fans will be created.
    Returns:
        readMe!:...
        solarFan: Brep representing a solar fan that should be clear of shading in order to ensure solar access to the _baseSrf for the given _sunVectors.
"""
ghenv.Component.Name = 'Ladybug_SolarFan'
ghenv.Component.NickName = 'SolarFan'
ghenv.Component.Message = 'VER 0.0.68\nFEB_06_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = 'LB-Legacy'
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


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
            
            if (len(unionedProjectedCrvs) != len(projectedCrvs)) and (noUnion_ == True):
                # Unable to perform boolean union operation so just return the projectedCrvs

                return projectedCrvs
            
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
            x = solarFans[fanCount]
            y = solarFans[fanCount + 1]
            x.Faces.SplitKinkyFaces(rc.RhinoMath.DefaultAngleTolerance, False)
            y.Faces.SplitKinkyFaces(rc.RhinoMath.DefaultAngleTolerance, False)
            a = rc.Geometry.Brep.CreateBooleanUnion([x, y], sc.doc.ModelAbsoluteTolerance)
            if a == None:
                a = [solarFans[fanCount], solarFans[fanCount + 1]]
        except:
            a = [solarFans[fanCount]]
        
        if a:
            res.extend(a)
    return res

def main(sunVectors):
    
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
        
        if noUnion_ == False:
            # When a boolean union is conducted the following works well
            # if one of the shading curves is contained inside the other, it can be deleted from the solar fan and can speed up the calculation down the line.
            shdCrv2 = []
            for curve in shadingCrvs:
                if rc.Geometry.AreaMassProperties.Compute(curve).Area > rc.Geometry.AreaMassProperties.Compute(_baseSrf).Area:
                    shdCrv2.append(curve)
                
        else:
            # When a boolean union is not conducted the above code doesn't append anything to shdCrv2
            shdCrv2 = shadingCrvs
            
        sortedCrvs = sorted(shdCrv2, key=lambda curve: rc.Geometry.AreaMassProperties.Compute(curve).Area)
        largestCrv = sortedCrvs[-1]
        finalShdCrvs =[]
        
        for curve in sortedCrvs:
            if str(rc.Geometry.Curve.PlanarClosedCurveRelationship(largestCrv, curve, plane[0], sc.doc.ModelAbsoluteTolerance)) != 'BInsideA':
                finalShdCrvs.append(curve)
            else: pass
        
        # duplicate the border around the base surface, which will be used to loft the solar fan
        baseSrfCrv = rc.Geometry.Curve.JoinCurves(_baseSrf.DuplicateEdgeCurves())[0]
        # get a point from the center of the shading curve to a new seam to adjust the seam on the shading curve.
        seamVectorPt = rc.Geometry.Vector3d((baseSrfCrv.PointAtStart.X - baseSrfCenPt.X)*planeHeight, (baseSrfCrv.PointAtStart.Y - baseSrfCenPt.Y)*planeHeight, 0)
        # adjust the seam of the shading curves.
        shadingCrvAdjust = []
        for curve in finalShdCrvs:
            try:
                curve.Reverse()
                curveParameter = curve.ClosestPoint(rc.Geometry.Intersect.Intersection.CurveCurve(curve, rc.Geometry.Line(rc.Geometry.AreaMassProperties.Compute(curve).Centroid, seamVectorPt).ToNurbsCurve(), sc.doc.ModelAbsoluteTolerance, sc.doc.ModelAbsoluteTolerance)[0].PointA)[1]
                curveParameterRound = round(curveParameter)
                curveParameterTol = round(curveParameter, (len(list(str(sc.doc.ModelAbsoluteTolerance)))-2))
                if curveParameterRound + sc.doc.ModelAbsoluteTolerance > curveParameter and curveParameterRound - sc.doc.ModelAbsoluteTolerance < curveParameter:
                    curve.ChangeClosedCurveSeam(curveParameterRound)
                    shadingCrvAdjust.append(curve)
                else:
                    curve.ChangeClosedCurveSeam(curveParameterTol)
                    if curve.IsClosed == True:
                        shadingCrvAdjust.append(curve)
                    else:
                        curve.ChangeClosedCurveSeam(curveParameterTol+sc.doc.ModelAbsoluteTolerance)
                        if curve.IsClosed == True:
                            shadingCrvAdjust.append(curve)
                        else:
                            curve.ChangeClosedCurveSeam(curveParameterTol-sc.doc.ModelAbsoluteTolerance)
                            if curve.IsClosed == True:
                                shadingCrvAdjust.append(curve)
                            else:
                                curve.ChangeClosedCurveSeam(curveParameter)
                                curve.MakeClosed(sc.doc.ModelAbsoluteTolerance)
                                shadingCrvAdjust.append(curve)
            except: shadingCrvAdjust.append(curve)
        
        # loft the shading curves with the base curve and generate a surface to cap the loft.
        solarFanInit = []
        shadingSrfs =[]
        for curve in shadingCrvAdjust:
            try:
                solarFanInit.append(rc.Geometry.Brep.CreateFromLoft([curve, baseSrfCrv], rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0])
                shadingSrfs.append(rc.Geometry.Brep.CreatePlanarBreps(curve)[0])
            except: pass
        
        #See if the loft has failed for any of the vectors.  This can happen if vectors are too close to being parallel to the input surface.
        if len(solarFanInit) != len(shadingCrvAdjust):
            warning = "Some of your input solar vectors are almost parallel to your input _baseSrf and this is causing the operations in the component to fail.  Either get rid of the vectors that are nearly parallel to your _baseSrf, or drop down the size of the fan to a very small level to get a true fan."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        else:
            # close the brep of the solar fan
            for brepCount, brep in enumerate(solarFanInit):
                brep.Join(_baseSrf, sc.doc.ModelAbsoluteTolerance, True)
                brep.Join(shadingSrfs[brepCount], sc.doc.ModelAbsoluteTolerance, True)
            
            # if more than one solar fan solids have been produced, resulting from multiple shading curves being produced, try to boolean union them together into one solar fan.
            if len(solarFanInit) > 1:
                listLength = len(solarFanInit)
                solarFanFinal = solarFanInit
                count  = 0
                while len(solarFanFinal) > 1 and count < int(listLength/2) + 10:
                    solarFanFinal = unionAllFans(solarFanFinal)
                    count += 1
                
                if solarFanFinal == None or len(solarFanFinal) > 1:
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
