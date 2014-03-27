# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to get a sense of how sunlight is reflected by a set of context geometries by tracing sun rays forwards through this geometry.
Examples where this component might be useful include the evaluation of the diffusion of light by a light shelf, or testing to see whether a parabolic building geometry (like a Ghery building) might focus sunlight to dangerous levels at certain times of the year.
Note that this component assumes that all sun light is reflected off of these geometries specularly (as if they were a mirror) and, for more detailed raytrace analysis, the Honeybee daylight components should be used.
-
Provided by Ladybug 0.0.57
    
    Args:
        _startPts: Points from which the sun rays will be cast towards the _context geometry.  You may want to connect a grid of points here to mimic the fact that direct sun will be streaming evenly from the sky.
        _startVectors: A sun vector from the sunPath component or a list of sun vectors to be forward ray-traced.
        _context: Breps of conext geometry that will reflect the sun rays.
        _numOfBounce_: An interger representing the number of ray bounces to trace the sun rays forward.
    Returns:
        readMe!: Read erros, comments, suggestions here.
        rays: The rays traced forward through the geometry.
"""

ghenv.Component.Name = "Ladybug_Forward Raytracing"
ghenv.Component.NickName = 'forwardRaytracing'
ghenv.Component.Message = 'VER 0.0.55\nFEB_24_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc

def main(startPts, startVectors, context, numOfBounce):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
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
            ray = rc.Geometry.Ray3d(testPt, vector)
            if numOfBounce>0:
                intPts = rc.Geometry.Intersect.Intersection.RayShoot(ray, [cleanBrep], numOfBounce)
                #print intPts
                if intPts:
                    ptList = [testPt]
                    ptList.extend(intPts)
                    rays.append(rc.Geometry.Polyline(ptList).ToNurbsCurve())
    if len(rays) == 0:
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "No reflection!")
    return rays

if (_startPts and _startPts[0]!=None) and (_startVectors and _startVectors[0]!=None) and (_context and _context[0]!=None):
    rays = main(_startPts, _startVectors, _context, _numOfBounce_)
elif _startPts == [] and _startVectors == [] and _context == []:
    print "Provide start points, start vectors and context."
else:
    print _startPts
    print "Provide valid start points, start vectors and context..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Provide start points, start vectors and context...")
