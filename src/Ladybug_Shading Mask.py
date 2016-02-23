#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> and Chris Mackey <Chris@MackeyArchitecture.com> 
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
-output
Provided by Ladybug 0.0.62
    
    Args:
        _testPt: A view point for which one wants to see the portion of the sky masked by the context geometry surrounding this point.
        _context: Context geometry surrounding the _testPt that could block the view to the sky.  Geometry must be a Brep or list of Breps.
        _skyDensity_: An integer that is greater than or equal to 0, which to sets the number of times that the Tergenza sky patches are split.  Set to 0 to view a sky mask with the typical Tregenza sky, which will divide up the sky with a coarse density of 145 sky patches.  Higher numbers input here will ensure a greater accuracy but will also take longer. The default is set to 3 to give you an error that is usually less than 1% sky view.  It is recommended that you use values of 3 or above for accurate results.
        _exposureOrView_: Set to 'True' to have the component calculate sky exposure (hemispherical view from a point) and set to 'False' to have the component calculate sky view (planar view from a surface).  The default is set to 'True' for sky exposure.
        scale_: Use this input to change the scale of the sky dome.  The default is set to 1.
    Returns:
        maskedMesh: A mesh of the portion of the sky dome masked by the _context geometry.
        visibleMesh: A mesh of the portion of the sky dome visible by the _testPt through the _context geometry.
        maskedExposure: The percentage of the hemispherical sky dome masked by the _context geometry at the _testPt.
        skyExposure: The percentage of the hemispherical sky dome visible by the _testPt through the _context geometry.
"""

ghenv.Component.Name = "Ladybug_Shading Mask"
ghenv.Component.NickName = 'shadingMask'
ghenv.Component.Message = 'VER 0.0.62\nFEB_15_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Grasshopper.Kernel as gh
import Rhino as rc
import math
import System
import scriptcontext as sc
import System.Threading.Tasks as tasks

outputsDict = {
0: ["maskedMesh", "A mesh of the portion of the sky dome masked by the _context geometry."],
1: ["visibleMesh", "A mesh of the portion of the sky dome visible by the _testPt through the _context geometry."],
2: ["maskedExposure", "The percentage of the hemispherical sky dome masked by the _context geometry at the _testPt."],
3: ["skyExposure", "The percentage of the hemispherical sky dome visible by the _testPt through the _context geometry."],
}


def setComponentOutputs():
    for output in range(4):
        if output == 2:
            ghenv.Component.Params.Output[output].NickName = 'maskedView'
            ghenv.Component.Params.Output[output].Name = 'maskedView'
            ghenv.Component.Params.Output[output].Description = 'The percentage of the sky NOT seen by a surface at the _testPt.' 
        elif output == 3:
            ghenv.Component.Params.Output[output].NickName = 'skyView'
            ghenv.Component.Params.Output[output].Name = 'skyView'
            ghenv.Component.Params.Output[output].Description = 'The percentage of the sky seen by a surface at the _testPt.' 
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]

def restoreComponentOutputs():
    for output in range(4):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]

def checkTheInputs():
    scale = 1
    if scale_ != None:
        if scale_ > 0: scale = scale_
        else:
            warning = "scale_ must be greater than 0."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    skyDensity = 3
    if _skyDensity_ != None:
        if _skyDensity_ >= 0: skyDensity = _skyDensity_
        else:
            warning = "skyDensity_ must be greater than 0."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    return scale, skyDensity


def parallelIntersection(testPt, joinedContext, testSurfaces):
    """
    testPt: center point
    context: context as a joined mesh
    testSurfaces: in this case sky patches are used to find the vectors
    it could be replaces by test vectors
    """
    
    def getRayVector(brep, testPt):
        MP = rc.Geometry.AreaMassProperties.Compute(brep)
        centerPt = MP.Centroid
        vector = rc.Geometry.Vector3d(centerPt - testPt)
        return vector
    
    
    numOfSrf = len(testSurfaces)
    masked = range(numOfSrf)
    
    # run the intersection
    def intersect(i):
        try:
            # find centerPoint and normal
            normalVector = getRayVector(testSurfaces[i], testPt)
            # create the meshRay
            ray = rc.Geometry.Ray3d(testPt, normalVector)
            # run the intersection
            if rc.Geometry.Intersect.Intersection.MeshRay(joinedContext, ray) >= 0.0:
                masked[i] = 1
            else:
                masked[i] = 0
        except Exception, e:
            print `e`
    
    tasks.Parallel.ForEach(range(numOfSrf), intersect)
    

    # return intersection result
    return masked

def joinMesh(meshList):
    joinedMesh = rc.Geometry.Mesh()
    for m in meshList: joinedMesh.Append(m)
    return joinedMesh

def meshAndJoin(brepList):
    joinedMesh = rc.Geometry.Mesh()
    for brep in brepList:
        meshList = rc.Geometry.Mesh.CreateFromBrep(brep, rc.Geometry.MeshingParameters.Smooth)
        for m in meshList: joinedMesh.Append(m)
    return joinedMesh
    

def main(testPt, skyDensity, contextMesh, scale):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    # generate sky patches
    skyPatches = lb_preparation.generateSkyGeo(testPt, skyDensity, scale)
    
    #return skyPatches
    if skyPatches == -1: return
    # join mesh
    joinedContextMesh = joinMesh(contextMesh)
    
    # run parallel intersections
    masked = parallelIntersection(testPt, joinedContextMesh, skyPatches)
    
    # filter breps based on the result
    # the reason I do it separately is to have the dome always on z = 0
    maskedSrfs = []
    unmaskedSrfs = []
    testPtProjected = rc.Geometry.Point3d(testPt.X, testPt.Y, 0)
    skyPatches = lb_preparation.generateSkyGeo(testPtProjected, skyDensity, scale)
    if _exposureOrView_ == False:
        skyPatchProjection = rc.Geometry.Transform.PlanarProjection(rc.Geometry.Plane(testPtProjected, rc.Geometry.Vector3d.ZAxis))
        for patch in skyPatches:
            patch.Transform(skyPatchProjection)
    for i, isMasked in enumerate(masked):
        if isMasked==1: maskedSrfs.append(skyPatches[i])
        else: unmaskedSrfs.append(skyPatches[i])
    
    # mesh the patches and calculate the area
    skyMeshed = meshAndJoin(skyPatches)
    maskedMesh = meshAndJoin(maskedSrfs)
    # change the color to black so the user don't get confused
    #maskedMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
    
    # unmasked area output is added by William Haviland
    unmaskedMesh = meshAndJoin(unmaskedSrfs)
    
    # color the meshes for masked and visible differently.
    meshColor = []
    for face in maskedMesh.Faces:
        meshColor.append(1.0)
    colors = lb_visualization.gradientColor(meshColor, 0, 2, [System.Drawing.Color.FromArgb(1,1,1), System.Drawing.Color.FromArgb(1,1,1)])
    maskedMesh = lb_visualization.colorMesh(colors, maskedMesh)
    
    meshColor = []
    for face in unmaskedMesh.Faces:
        meshColor.append(1.0)
    colors = lb_visualization.gradientColor(meshColor, 0, 2, [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(200,200,255)])
    unmaskedMesh = lb_visualization.colorMesh(colors, unmaskedMesh)
    
    #Compute sky view or exposure.
    maskedArea = rc.Geometry.AreaMassProperties.Compute(maskedMesh).Area
    skyArea = rc.Geometry.AreaMassProperties.Compute(skyMeshed).Area
    
    percentageArea = (maskedArea/skyArea) * 100
    percentageSky = 100 - percentageArea
    
    
    return maskedMesh, unmaskedMesh, "%.2f"%percentageArea, "%.2f"%percentageSky



#If Ladybug is not flying or is an older version, give a warning.
initCheck = True
w = gh.GH_RuntimeMessageLevel.Warning
#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)

#Check exposure or view.
if _exposureOrView_ == False: setComponentOutputs()
else: restoreComponentOutputs()


if _testPt and _context and initCheck == True:
    scale, skyDensity = checkTheInputs()
    results = main(_testPt, skyDensity, _context, 200*scale)
    if results!=-1:
        if _exposureOrView_ == False:maskedMesh, visibleMesh, maskedView, skyView = results
        else: maskedMesh, visibleMesh, maskedExposure, skyExposure = results
