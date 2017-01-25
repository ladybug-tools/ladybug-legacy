# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
#
# This file is part of Ladybug.
#
# Copyright (c) 2013-2015, ....(YOUR NAME).... <....(YOUR EMAIL)....>
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
Use this component to calculate view factors from a point or plane to a set of surfaces.  View factors are used in many thermal comfort calculations such as mean radiant temperture (MRT) or discomfort from radiant assymetry. 
-
Provided by Ladybug 0.0.63

    Args:
        _testPtsOrPlanes: A point or plane from which view vectors will be pojected.  Note that, if a point is connected, all view vectors will be weighted evenly (assuming no directional bias).  However, if a plane is connected, vectors will be weighted based on their angle to the plane normal, producing view factors for a surface in the connected plane.  The first is useful for MRT calculations while the latter is needed for radiant assymetry calculations.  This input can also be a list of points or planes.
        _testSrfs: A list of breps, surfaces, or meshes to which you want to compute view factors.  Note that by meshing and joining several goemtries together, you can calculate the combined view factor to these geometries.
        context_: Optional context geometry as breps, surfaces, or meshes that can block the view to the _testSrfs.
        _viewResolution_: An interger, which sets the number of times that the tergenza skyview patches are split.  A higher number will ensure a greater accuracy but will take longer.  The default is set to 1 for a quick calculation.
        parallel_: Set to "True" to run the calculation in parallel and set to "False" to run it with a single core.  The default is set to "False."
        _runIt: Set to 'True' to run the component and claculate view factors.
    Returns:
        readMe!: ...
        srfViewFactors: A list of view factors that describe the fraction of sperical view taken up by the input surfaces.  These values range from 0 (no view) to 1 (full view).  If multiple _testPtsOrPlanes have been connected, this output will be a data tree with one list for each point.
        viewVecSrfIndex: The index of the surface that each view vector hit.  This can be used to identify which view pathces are intersected by each surface.  If no surfaces are intersected, this value will be -1.
        viewVectors: The view vectors that were projected from each testPtOrPlane.
        viewPatches: The patches of the sphere that each view vector correspond to.
        viewPatchBasePt: The center of the viewPatches sphere. This can be used to move the view patches between the testPts.
"""

ghenv.Component.Name = "Ladybug_Surface View Analysis"
ghenv.Component.NickName = 'srfViewFactors'
ghenv.Component.Message = 'VER 0.0.63\nAUG_12_2016'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import operator
import Grasshopper.Kernel as gh
import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math
import System.Threading.Tasks as tasks
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

w = gh.GH_RuntimeMessageLevel.Warning


def checkInputs():
    #Set a default view resolution.
    if _viewResolution_ == None: viewRes = 1
    else: viewRes = _viewResolution_
    
    #Set a default parallel.
    if parallel_ == None: parallel = False
    else: parallel = parallel_
    
    #Check to to see if the connected _testPts are points or planes.
    checkData = True
    viewMethod = 0
    viewPoints = []
    viewPtNormals = []
    for point in _testPtsOrPlanes:
        try:
            #The user has connected planes.
            viewPoints.append(point.Origin)
            viewPtNormals.append(point.Normal)
            viewMethod = 1
        except:
            #The user has connected points.
            try:
                viewPoints.append(rc.Geometry.Point3d(point))
                if viewMethod ==  1: checkData = False
            except:
                try:
                    viewPoints.append(rc.Geometry.Point3d(rs.coerce3dpoint(point)))
                except:
                    checkData = False
    
    if checkData == False:
        warning = "_testPtsOrPlanes can be either points or planes but not both."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    return checkData, viewRes, viewMethod, viewPoints, viewPtNormals, parallel

def checkViewResolution(viewResolution, centPt, lb_preparation):
    #Set lists to be filled.
    newVecs = []
    viewPatches = []
    patchAreaFacs = []
    patchAreas = []
    
    #Set up some transformations.
    skyPtachTranslation = rc.Geometry.Transform.Translation(centPt.X, centPt.Y, centPt.Z)
    patchReflectTrans = rc.Geometry.Transform.Mirror(rc.Geometry.Plane(centPt, rc.Geometry.Vector3d.XAxis, rc.Geometry.Vector3d.YAxis))
    patchRotateTrans = rc.Geometry.Transform.Rotation(math.pi, rc.Geometry.Vector3d.ZAxis, centPt)
    
    #Generate sky patches.
    skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, viewResolution, 1)
    
    #Extract info from the patches.
    for patch in skyPatches:
        #Add to the area list.
        patchAreaProps = rc.Geometry.AreaMassProperties.Compute(patch)
        patchAreas.extend([patchAreaProps.Area, patchAreaProps.Area])
        
        #Add to the vector list.
        patchPt = patchAreaProps.Centroid
        Vec = rc.Geometry.Vector3d(patchPt.X, patchPt.Y, patchPt.Z)
        revVec = rc.Geometry.Vector3d(-patchPt.X, -patchPt.Y, -patchPt.Z)
        newVecs.append(Vec)
        newVecs.append(revVec)
        
        #Add to the viewPatches list.
        patch.Transform(skyPtachTranslation)
        viewPatches.append(patch)
        newPatch = rc.Geometry.Brep.CreateTrimmedSurface(patch.Faces[0], patch.Faces[0])
        newPatch.Transform(patchReflectTrans)
        newPatch.Transform(patchRotateTrans)
        viewPatches.append(newPatch)
    
    #Convert patch areas to factors that will be multiplied by the 0/1 values.
    normPatArea = sum(patchAreas)/len(patchAreas)
    for patArea in patchAreas:
        patchAreaFacs.append(patArea/normPatArea)
    
    return newVecs, viewPatches, patchAreaFacs

def allZero(items):
    return all(x == "N" for x in items)

def main(zoneSrfsMesh, context, viewVectors, patchAreaFacs, testPts, viewPtNormals, viewMethod, parallel = False):
    #Make the list that will eventually hold the view factors of each surface.
    testPtViewFactor = []
    vecSrfIndices = []
    for pointCount, point in enumerate(testPts):
        testPtViewFactor.append([])
        vecSrfIndices.append([])
        divisor = len(viewVectors)
    totalSrfsMesh = zoneSrfsMesh + context
    
    def intRays(i):
        #Create the rays to be projected from each point.
        pointRays = []
        for vec in viewVectors: pointRays.append(rc.Geometry.Ray3d(testPts[i], vec))
        
        #Create a list that will hold the intersection hits of each surface
        srfHits = []
        for srf in totalSrfsMesh: srfHits.append([])
        
        #Perform the intersection of the rays with the mesh.
        pointIntersectList = []
        for rayCount, ray in enumerate(pointRays):
            pointIntersectList.append([])
            for srf in totalSrfsMesh:
                intersect = rc.Geometry.Intersect.Intersection.MeshRay(srf, ray)
                if intersect == -1: intersect = "N"
                pointIntersectList[rayCount].append(intersect)
        
        #Find the intersection that was the closest for each ray (in case one ray intersects 2 surfaces)
        for rayCount, intList in enumerate(pointIntersectList):
            if allZero(intList) == False:
                minIndex, minValue = min(enumerate(intList), key=operator.itemgetter(1))
                if minIndex > len(zoneSrfsMesh)-1:
                    vecSrfIndices[i].append(-1)
                else:
                    vecSrfIndices[i].append(minIndex)
                    if viewMethod == 0: srfHits[minIndex].append(patchAreaFacs[rayCount])
                    else:
                        # calculate the angle between the surface and the vector to project the view into the plane.
                        vecAngle = rc.Geometry.Vector3d.VectorAngle(viewVectors[rayCount], viewPtNormals[i])
                        srfHits[minIndex].append(patchAreaFacs[rayCount]* 2 * abs(math.cos(vecAngle)))
            else:
                vecSrfIndices[i].append(-1)
        
        #Sum up the lists and divide by the total rays to get the view factor.
        for hitList in srfHits:
            testPtViewFactor[i].append(sum(hitList)/divisor)
    
    if parallel:
        tasks.Parallel.ForEach(range(len(testPts)), intRays)
    else:
        for count in range(len(testPts)):
            intRays(count)
    
    
    return testPtViewFactor, vecSrfIndices


#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
        lb_preparation = sc.sticky["ladybug_Preparation"]()
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)




if initCheck == True:
    checkData, viewRes, viewMethod, viewPoints, viewPtNormals, parallel = checkInputs()
    if checkData == True and _runIt == True:
        viewPatchBasePt = viewPoints[0]
        viewVectors, viewPatches, patchAreaFacs = checkViewResolution(viewRes, viewPatchBasePt, lb_preparation)
        srfViewFactorsInit, viewVecSrfIndexInit = main(_testSrfs, context_, viewVectors, patchAreaFacs, viewPoints, viewPtNormals, viewMethod, parallel)
        
        srfViewFactors = DataTree[Object]()
        viewVecSrfIndex = DataTree[Object]()
        for count, dataList in enumerate(srfViewFactorsInit):
            for item in dataList: srfViewFactors.Add(item, GH_Path(count))
        for count, dataList in enumerate(viewVecSrfIndexInit):
            for item in dataList: viewVecSrfIndex.Add(item, GH_Path(count))

ghenv.Component.Params.Output[4].Hidden= True
ghenv.Component.Params.Output[5].Hidden= True