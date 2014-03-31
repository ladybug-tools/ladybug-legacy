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
        _sourceSrfs: A list of Breps as surfaces to bounce from.
        _gridSizeOrPoints: A number in Rhino model units that represents the average size of a grid cell to generate the points, or list of points itself.
        context_: Breps or meshes of conext geometry that will reflect the sun rays.  Note that, for curved surfaces, smooth meshes of the geometry will be more accurate than inputing a Brep.
        _numOfBounce_: An interger representing the number of ray bounces to trace the sun rays forward.
        firstBounceLen_: A number representing the length of the first bounce. If empty the length of diagonal of bounding box of geometries will be used.
        _lastBounceLen_: A number representing the length of the last bounce. 
    Returns:
        bouncePts: The generated base points. The preview is set to hidden by default.
        rays: The rays traced forward through the geometry.
"""

ghenv.Component.Name = "Ladybug_Bounce from Surface"
ghenv.Component.NickName = 'bounceFromSurface'
ghenv.Component.Message = 'VER 0.0.57\nMAR_31_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Grasshopper.Kernel as gh
import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math

def main(sourceSrfs, gridSizeOrPoints, sunVectors, context, numOfBounce, firstBounceLen, lastBounceLen):
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
        return -1, -1
    
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
                    
    if len(rays) == 0:
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "No reflection!")
    return rays, initialTestPoints

if (_sourceSrfs and _sourceSrfs[0]!=None) and (_sunVectors and _sunVectors[0]!=None) and (_gridSizeOrPoints and _gridSizeOrPoints[0]!=None):
    rays, bouncePts = main(_sourceSrfs, _gridSizeOrPoints, _sunVectors, context_, _numOfBounce_, firstBounceLen_, _lastBounceLen_)
    ghenv.Component.Params.Output[1].Hidden= True
    
elif _sourceSrfs == [] and _gridSizeOrPoints == [] and _sunVectors == []:
    print "Provide start points, start vectors and context."
else:
    #print _startPts
    print "Provide valid start points, start vectors and context..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "Provide start points, start vectors and context...")
