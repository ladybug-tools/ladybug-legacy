#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to get a sense of how direct sunlight is reflected off of an initial _sourceSrf and subsequently to a set of context_ geometries by tracing sun rays forwards through this geometry.
Examples where this component might be useful include the evaluation of the diffusion of light by a light shelf, or testing to see whether a parabolic building geometry (like a Ghery building) might focus sunlight to dangerous levels at certain times of the year.
Note that this component assumes that all sun light is reflected off of these geometries specularly (as if they were a mirror) and, for more detailed raytrace analysis, the Honeybee daylight components should be used.
-
Provided by Ladybug 0.0.65
    
    Args:
        _sourceSrfs: A brep or mesh representing a surface that you are interested in seeing direct sunlight bounce off of.  You can also put in lists of breps or meshes. These surfaces will be used to generate the initial sun rays in a grid-like pattern.  Note that, for curved surfaces, smooth meshes of the geometry will be more accurate than inputing a Brep.
        _gridSizeOrPoints: A number in Rhino model units that represents the average size of a grid cell to generate the points, or list of points itself.  Note that, if you put in meshes for the input above, the _gridSize number option of this input will not work as this component will use the vertices of the mesh to generate the sun rays.
        context_: Breps or meshes of conext geometry, which will reflect the sun rays after they bounce off of the _sourceSrfs.  Note that, for curved surfaces, smooth meshes of the geometry will be more accurate than inputing a Brep.
        _numOfBounce_: An interger representing the number of ray bounces to trace the sun rays forward.
        firstBounceLen_: A number representing the length of the sun ray before the first bounce. If left empty, this length will be the diagonal of the bounding box surrounding all input geometries.
        _lastBounceLen_: A number representing the length of the sun ray after the last bounce. If left empty, this length will be the diagonal of the bounding box surrounding all input geometries.
    Returns:
        bouncePts: The generated base points on the _sourceSrfs to which the sun rays will be directed. The preview of this output is set to be hidden by default.  Connect to a Grasshopper "Point" component to visualize.
        rays: The sun rays traced forward through the geometry.
        _runIt: Set to True to run the reflection study.
"""

ghenv.Component.Name = "Ladybug_Bounce from Surface"
ghenv.Component.NickName = 'bounceFromSurface'
ghenv.Component.Message = 'VER 0.0.65\nJAN_10_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import Grasshopper.Kernel as gh
import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math

def main(sourceSrfs, gridSizeOrPoints, sunVectors, context, numOfBounce, firstBounceLen, lastBounceLen):
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
    
    # Check the geometry
    
    if len(context)==0: context = sourceSrfs
    else: context = context + sourceSrfs
    ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
    contextMesh, contextBrep = lb_preparation.cleanAndCoerceList(context)
    ## mesh Brep
    contextMeshedBrep = lb_mesh.parallel_makeContextMesh(contextBrep)
    
    ## Flatten the list of surfaces
    contextMeshedBrep = lb_preparation.flattenList(contextMeshedBrep)
    contextSrfs = contextMesh + contextMeshedBrep
    joinedContext = lb_mesh.joinMesh(contextSrfs)
    
    # Get rid of trimmed parts
    cleanBrep = rc.Geometry.Brep.CreateFromMesh(joinedContext, False)
    
    try:
        gridSize = float(gridSizeOrPoints[0])
        basedOnGrid = True
    except:
        basedOnGrid = False
        initialTestPoints = rs.coerce3dpointlist(gridSizeOrPoints)
        ptsNormals = [cleanBrep.ClosestPoint(intPt, sc.doc.ModelAbsoluteTolerance)[5] for intPt in initialTestPoints]
        
    
    # generate the test points
    if basedOnGrid:
        ## mesh Brep
        analysisMesh, analysisBrep = lb_preparation.cleanAndCoerceList(sourceSrfs)
        
        analysisMeshedBrep = lb_mesh.parallel_makeSurfaceMesh(analysisBrep, float(gridSize))
            
        ## Flatten the list of surfaces
        analysisMeshedBrep = lb_preparation.flattenList(analysisMeshedBrep)
        analysisSrfs = analysisMesh + analysisMeshedBrep
            
        initialTestPoints, ptsNormals, meshSrfAreas = lb_mesh.parallel_testPointCalculator(analysisSrfs, 0, False)
        initialTestPoints = lb_preparation.flattenList(initialTestPoints)
        ptsNormals = lb_preparation.flattenList(ptsNormals)
        
    
    # find the distance for moving the points backward
    try:
        firstBounceLen = float(firstBounceLen)
    except:
        maxPt =joinedContext.GetBoundingBox(True).Max
        minPt = joinedContext.GetBoundingBox(True).Min
        firstBounceLen = maxPt.DistanceTo(minPt)
        
    rays = []
    for ptCount, testPt in enumerate(initialTestPoints):
        for vector in sunVectors:
            vector.Unitize()
            testPt = rc.Geometry.Point3d.Add(testPt, -vector * firstBounceLen)
            ray = rc.Geometry.Ray3d(testPt, vector)
            
            if numOfBounce>0 and rc.Geometry.Vector3d.VectorAngle(vector, ptsNormals[ptCount]) < math.pi/2:
                intPts = rc.Geometry.Intersect.Intersection.RayShoot(ray, [cleanBrep], numOfBounce)
                #print intPts
                if intPts:
                    ptList = [testPt]
                    ptList.extend(intPts)
                    ray = rc.Geometry.Polyline(ptList).ToNurbsCurve()
                    
                    try:
                        # create last ray
                        # calculate plane at intersection
                        intNormal = cleanBrep.ClosestPoint(intPts[-1], sc.doc.ModelAbsoluteTolerance)[5]
                        
                        lastVector = rc.Geometry.Vector3d(ptList[-2] - ptList[-1])
                        lastVector.Unitize()
                        
                        crossProductNormal = rc.Geometry.Vector3d.CrossProduct(intNormal, lastVector)
                        
                        plane = rc.Geometry.Plane(intPts[-1], intNormal, crossProductNormal)
                        
                        mirrorT = rc.Geometry.Transform.Mirror(intPts[-1], plane.Normal)
                        
                        lastRay = rc.Geometry.Line(intPts[-1], lastBounceLen * lastVector).ToNurbsCurve()
                        lastRay.Transform(mirrorT)
                        
                        ray = rc.Geometry.Curve.JoinCurves([ray, lastRay])[0]
                    except:
                        pass
                        
                    rays.append(ray)
                else:
                    # no bounce so let's just create a line form the point
                    firstRay = rc.Geometry.Line(testPt, lastBounceLen * vector).ToNurbsCurve()
                    rays.append(firstRay)
            else:
                rays.append(None)
    
    return rays, initialTestPoints

if (_sourceSrfs and _sourceSrfs[0]!=None) and (_sunVectors and _sunVectors[0]!=None) and (_gridSizeOrPoints and _gridSizeOrPoints[0]!=None) and _runIt == True:
    results = main(_sourceSrfs, _gridSizeOrPoints, _sunVectors, context_, _numOfBounce_, firstBounceLen_, _lastBounceLen_)
    if results!=-1:
        rays, bouncePts = results
        
    ghenv.Component.Params.Output[1].Hidden= True
    
elif _sourceSrfs == [] and _gridSizeOrPoints == [] and _sunVectors == []:
    print "Provide start points, start vectors and context."
else:
    #print _startPts
    print "Provide valid start points, start vectors and context..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Provide start points, start vectors and context...")
