#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2020, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to get a sense of how sunlight is reflected by a set of context geometries by tracing sun rays forwards through this geometry.
Examples where this component might be useful include the evaluation of the diffusion of light by a light shelf, or testing to see whether a parabolic building geometry (like a Ghery building) might focus sunlight to dangerous levels at certain times of the year.
Note that this component assumes that all sun light is reflected off of these geometries specularly (as if they were a mirror) and, for more detailed raytrace analysis, the Honeybee daylight components should be used.
-
Provided by Ladybug 0.0.69
    
    Args:
        _startPts: Points from which the sun rays will be cast towards the _context geometry.  You may want to connect a grid of points here to mimic the fact that direct sun will be streaming evenly from the sky.
        _startVectors: A sun vector from the sunPath component or a list of sun vectors to be forward ray-traced.
        _context: Breps or meshes of conext geometry that will reflect the sun rays.  Note that, for curved surfaces, smooth meshes of the geometry will be more accurate than inputing a Brep.
        _numOfBounce_: An interger representing the number of ray bounces to trace the sun rays forward.
        _lastBounceLen_: A float number representing the length in Rhino model units of the light ray after the last bounce.
    Returns:
        readMe!: Read erros, comments, suggestions here.
        rays: A series of line curves representing light rays traced forward through the geometry.
"""

ghenv.Component.Name = "Ladybug_Forward Raytracing"
ghenv.Component.NickName = 'forwardRaytracing'
ghenv.Component.Message = 'VER 0.0.69\nJUL_07_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "LB-Legacy"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc

def main(startPts, startVectors, context, numOfBounce, lastBounceLen):
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
    
    # A failed attampt to use mesh instead of brep so the component could work with trimmed surfaces
    if len(context)!=0:
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
    
    rays = []
    for testPt in startPts:
        for vector in startVectors:
            vector.Unitize()
            ray = rc.Geometry.Ray3d(testPt, vector)
            if numOfBounce>0:
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
                    
    if len(rays) == 0:
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "No reflection!")
    return rays

if (_startPts and _startPts[0]!=None) and (_startVectors and _startVectors[0]!=None) and (_context and _context[0]!=None):
    rays = main(_startPts, _startVectors, _context, _numOfBounce_, _lastBounceLen_)
elif _startPts == [] and _startVectors == [] and _context == []:
    print "Provide start points, start vectors and context."
else:
    #print _startPts
    print "Provide valid start points, start vectors and context..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Provide start points, start vectors and context...")
