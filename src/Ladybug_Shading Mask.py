#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Byron Mardas <byronmardas@gmail.com>, Chris Mackey <Chris@MackeyArchitecture.com>, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools>
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
Use this component to see the portion of the sky dome that is masked by context geometry around a given point.
The component will generate separate meshs for the portions of the sky dome that are masked and visible.
The component will also calculate the percentage of the sky that is masked by the context geometry and the percentage that is visible (the sky view factor).
-output
Provided by Ladybug 0.0.68
    
    Args:
        _centerPtOrPlane_: A point or plane from which the visible portion of the sky will be evaluated.  If a point is input here, the component will calculate Sky Exposure (or the fraction of the sky hemisphere that is visible from the point).  If a plane is input here, the component will calculate Sky View (or the fraction of the sky visible from a surface in this plane).  If no value is input here, the component will assume a point (Sky Exposure) at the Rhino origin.
        context_: Context geometry surrounding the _centerPtOrPlane_ that could block the view to the sky.  Geometry can be either a list of surfaces, breps, or meshes (this component converts everything to a mesh for a fast calculation).
        orientation_: A number between 0 and 360 that sets the orientation of a vertically-oriented surface for which you want to visualize the sky view.  Alternatively, this input can just be the words "north", "east", "south" or "west."  This will block out the portion of the sky that is not visible from a vertical surface with this orientation. Note that an input here will project the patches into the plane of this vertical orientation to calculate a Sky View result (overriding any plane input to the _centerPtOrPlane_).  The default is set to have no orientation.
        overhangProject_: A number between 0 and 90 that sets the angle between the _centerPtOrPlane_ and the edge of an imagined horizontal overhang projecting past the point.  Note that this option is only available when there is an input for orientation_ above. This allows one to visualise the portion of the sky blocked by an overhang with this projection anle.
        leftFinProject_: A number between 0 and 180 that sets the angle between the _centerPtOrPlane_ and the edge of an imagined vertical fin projecting past the left side of the point.  Note that this option is only available when there is an input for orientation_ above. This allows one to visualise the portion of the sky blocked by vertical fin on the left side of the point with this projection anle.
        rightFinProject_: A number between 0 and 180 that sets the angle between the _centerPtOrPlane_ and the edge of an imagined vertical fin projecting past the right side of the point.  Note that this option is only available when there is an input for orientation_ above. This allows one to visualise the portion of the sky blocked by vertical fin on the right side of the point with this projection anle.
        ----------:. ...
        _skyDensity_: An integer that is greater than or equal to 0, which to sets the number of times that the Tergenza sky patches are split.  Set to 0 to view a sky mask with the typical Tregenza sky, which will divide up the sky with a coarse density of 145 sky patches.  Higher numbers input here will ensure a greater accuracy but will also take longer. The default is set to 3 to give you an error that is usually less than 1% sky view.  It is recommended that you use values of 3 or above for accurate results.
        _projection_: A number to set the projection of the sky hemisphere.  The default is set to draw a 3D hemisphere.  Choose from the following options:
            0 = 3D hemisphere
            1 = Orthographic (straight projection to the XY Plane)
            2 = Stereographic (equi-angular projection to the XY Plane)
        _scale_: Use this input to change the scale of the sky dome.  The default is set to 1.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
    Returns:
        contextMask: A mesh of the portion of the sky dome masked by the context_ geometry.
        skyMask: A mesh of the portion of the sky dome visible by the _centerPtOrPlane_ through the context_ geometry.
        ----------: ...
        contextExposure: The percentage of the hemispherical sky dome masked by the context_ geometry at the _centerPtOrPlane_.
        skyExposure: The percentage of the hemispherical sky dome visible by the _centerPtOrPlane_ through the context_ geometry.
"""

ghenv.Component.Name = "Ladybug_Shading Mask"
ghenv.Component.NickName = 'shadingMask'
ghenv.Component.Message = 'VER 0.0.68\nJAN_01_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import Grasshopper.Kernel as gh
import Rhino as rc
import rhinoscriptsyntax as rs
import math
import System
import scriptcontext as sc
import System.Threading.Tasks as tasks
import copy

outputsDict = {
0: ["contextMask", "A mesh of the portion of the sky dome masked by the context_ geometry."],
1: ["orientationMask", "A mesh of the portion of the sky dome masked by the fact that a surface is facing a given orientation."],
2: ["strategyMask", "A mesh of the portion of the sky dome masked by the overhang, left fin, and right fin projections."],
3: ["skyMask", "A mesh of the portion of the sky dome visible by the _centerPtOrPlane_ through the context_ geometry."],
4: ["----------", "..."],
5: ["contextExposure", "The percentage of the hemispherical sky dome masked by the context_ geometry."],
6: ["orientExposure", "The percentage of the hemispherical sky dome masked by the fact that a surface is facing a given orientation."],
7: ["strategyExposure", "The percentage of the hemispherical sky dome masked by the overhang, left fin, and right fin projections."],
8: ["skyExposure", "The percentage of the hemispherical sky dome visible through the context_ geometry and the strategy geometry."]
}


def setComponentOutputs():
    for output in range(9):
        if output == 5:
            ghenv.Component.Params.Output[output].NickName = 'contextView'
            ghenv.Component.Params.Output[output].Name = 'contextView'
            ghenv.Component.Params.Output[output].Description = 'The percentage of the sky masked by the context_ for a surface at the _centerPtOrPlane_.' 
        elif output == 6:
            ghenv.Component.Params.Output[output].NickName = 'orientView'
            ghenv.Component.Params.Output[output].Name = 'orientView'
            ghenv.Component.Params.Output[output].Description = 'The percentage of the sky masked by the fact that a surface is facing a given orientation.' 
        elif output == 7:
            ghenv.Component.Params.Output[output].NickName = 'strategyView'
            ghenv.Component.Params.Output[output].Name = 'strategyView'
            ghenv.Component.Params.Output[output].Description = 'The percentage of the sky masked by the overhang, left fin, and right fin projections for a surface at the _centerPtOrPlane_.' 
        elif output == 8:
            ghenv.Component.Params.Output[output].NickName = 'skyView'
            ghenv.Component.Params.Output[output].Name = 'skyView'
            ghenv.Component.Params.Output[output].Description = 'The percentage of the sky seen by a surface at the _centerPtOrPlane_.' 
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]

def restoreComponentOutputs():
    for output in range(9):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]

def checkTheInputs():
    # Set default scale.
    scale = 1
    if _scale_ != None:
        if _scale_ > 0: scale = _scale_
        else:
            warning = "_scale_ must be greater than 0."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    
    # Set default sky density.
    if _skyDensity_ != None:
        if _skyDensity_ >= 0:
            skyDensity = int(_skyDensity_*100)
        else:
            warning = "skyDensity_ must be greater than 0."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    else: skyDensity = 100
    
    # Check the view point or plane.
    viewMethod = 0
    viewPlane = None
    if _centerPtOrPlane_ == None:
        centerPt = rc.Geometry.Point3d.Origin
    else:
        try:
            #The user has connected planes.
            centerPt = _centerPtOrPlane_.Origin
            viewPlane = rc.Geometry.Plane(_centerPtOrPlane_)
            viewMethod = 1
        except:
            #The user has connected points.
            try:
                centerPt = rc.Geometry.Point3d(_centerPtOrPlane_)
            except:
                try:
                    centerPt = rc.Geometry.Point3d(rs.coerce3dpoint(_centerPtOrPlane_))
                except:
                    warning = "_centerPtOrPlane_ is neither a point or a plane."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                    return -1
    
    # Check the orientation.
    if orientation_ != None:
        if orientation_.lower() == "north":
            orientVector = rc.Geometry.Vector3d(0,1,0)
        elif orientation_.lower() == "east":
            orientVector = rc.Geometry.Vector3d(1,0,0)
        elif orientation_.lower() == "south":
            orientVector = rc.Geometry.Vector3d(0,-1,0)
        elif orientation_.lower() == "west":
            orientVector = rc.Geometry.Vector3d(-1,0,0)
        else:
            try:
                orientAngle = float(orientation_)
                if orientAngle > 360 or orientAngle < 0:
                    warning = "orientation_ must be between 0 and 360."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                    return -1
                orientVector = rc.Geometry.Vector3d(0,1,0)
                orientVector.Rotate(math.radians(-orientAngle), rc.Geometry.Vector3d.ZAxis)
            except:
                warning = "orientation_ input is not valid."
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1
        viewMethod = 1
        viewPlane = rc.Geometry.Plane(centerPt, orientVector)
    
    # Check the overhang, left fin, and right fin projections.
    if overhangProject_ != None:
        if overhangProject_ < 0 or overhangProject_ > 90:
            warning = "overhangProject_ should be between 0 and 90."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    if leftFinProject_ != None:
        if leftFinProject_ < 0 or leftFinProject_ > 180:
            warning = "leftFinProject_ should be between 0 and 180."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    if rightFinProject_ != None:
        if rightFinProject_ < 0 or rightFinProject_ > 180:
            warning = "rightFinProject_ should be between 0 and 180."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    
    return viewMethod, centerPt, viewPlane, scale, skyDensity

def orientCalc(fullRays, planeNormal):
    masked = []
    unmasked = []
    visibleRays = []
    
    for i, ray in enumerate(fullRays):
        rayAng = rc.Geometry.Vector3d.VectorAngle(ray.Direction, planeNormal)
        if rayAng > math.pi/2:
            masked.append(-1)
            unmasked.append(i)
        else:
            masked.append(i)
            unmasked.append(-1)
            visibleRays.append(ray)
    
    return masked, unmasked, visibleRays

def overhangCalc(fullRays, planeNormal):
    masked = []
    unmasked = []
    visibleRays = []
    
    for i, ray in enumerate(fullRays):
        rayAng = rc.Geometry.Vector3d.VectorAngle(ray.Direction, planeNormal)
        if rayAng < math.pi/2:
            masked.append(-1)
            unmasked.append(i)
        else:
            masked.append(i)
            unmasked.append(-1)
            visibleRays.append(ray)
    
    return masked, unmasked, visibleRays

def finCalc(fullRays, acceptAngleMin, acceptAngleMax):
    masked = []
    unmasked = []
    visibleRays = []
    
    for i, ray in enumerate(fullRays):
        projectedRay = rc.Geometry.Vector3d(ray.Direction.X, ray.Direction.Y, 0)
        rayAng = math.degrees(rc.Geometry.Vector3d.VectorAngle(projectedRay, rc.Geometry.Vector3d.YAxis))
        if ray.Direction.X > 0:
            rayAng = 180 + (180-rayAng)
        if acceptAngleMin > 0:
            if rayAng > acceptAngleMax or rayAng < acceptAngleMin:
                masked.append(-1)
                unmasked.append(i)
            else:
                masked.append(i)
                unmasked.append(-1)
                visibleRays.append(ray)
        else:
            if rayAng < acceptAngleMax or rayAng > acceptAngleMin + 360:
                masked.append(i)
                unmasked.append(-1)
                visibleRays.append(ray)
            else:
                masked.append(-1)
                unmasked.append(i)
    
    return masked, unmasked, visibleRays

def parallelIntersection(rays, joinedContext):
    numOfRays = len(rays)
    masked = range(numOfRays)
    unmasked = range(numOfRays)
    
    # run the intersection
    def intersect(i):
        try:
            ray = rays[i]
            # run the intersection
            if rc.Geometry.Intersect.Intersection.MeshRay(joinedContext, ray) >= 0.0:
                masked[i] = -1
                unmasked[i] = i
            else:
                masked[i] = i
                unmasked[i] = -1
        except Exception, e:
            print `e`
    
    tasks.Parallel.ForEach(range(numOfRays), intersect)
    
    return masked, unmasked

def joinMesh(meshList):
    joinedMesh = rc.Geometry.Mesh()
    for m in meshList: joinedMesh.Append(m)
    return joinedMesh

# Generate the vectors.
def Centroids(hemisphere):
    centroids = []
    for i in range(hemisphere.Faces.Count):
        centroids.append(hemisphere.Faces.GetFaceCenter(i))
    return centroids

def Rays(testPt, hemisphere):
    rays = []
    for i in Centroids(hemisphere):
        direction = rc.Geometry.Vector3d(i.X-testPt.X, i.Y-testPt.Y, i.Z-testPt.Z)
        ray = rc.Geometry.Ray3d(testPt,direction)
        rays.append(ray)
    return rays

def main(viewMethod, testPt, viewPlane, skyDensity, contextMesh, scale, projection, overhangProject, leftFinProject, rightFinProject):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    # Generate the sky hemisphere.
    sphere = rc.Geometry.Sphere(testPt,scale)
    meshSphere = rc.Geometry.Mesh.CreateFromSphere(sphere,int(skyDensity),int(skyDensity))
    groundPlane = rc.Geometry.Plane(testPt, rc.Geometry.Vector3d.ZAxis)
    hemisphere = rc.Geometry.Mesh.Split(meshSphere,groundPlane)[0]
    
    # Generate the rays and take out those that are not within the viewPlane.
    fullRays = Rays(testPt, hemisphere)
    orientMask = None
    strategyMask = None
    orientView = 0
    if viewPlane != None:
        planeNormal = viewPlane.Normal
        orientMasked, orientUnmasked, visibleRays = orientCalc(fullRays, planeNormal)
        orientRemoveIndices = filter(lambda a: a != -1, orientMasked)
        visibleRemoveIndices = filter(lambda a: a != -1, orientUnmasked)
        orientMask = copy.copy(hemisphere)
        orientMask.Faces.DeleteFaces(orientRemoveIndices)
        
        maskedMesh = copy.copy(hemisphere)
        maskedMesh.Faces.DeleteFaces(visibleRemoveIndices)
        
        if overhangProject != None:
            overhangNorm = copy.copy(planeNormal)
            overhangNorm.Reverse()
            rotationAxis = copy.copy(overhangNorm)
            rotationAxis.Rotate(-math.pi/2, rc.Geometry.Vector3d.ZAxis)
            rotationAxis = rc.Geometry.Vector3d(rotationAxis.X, rotationAxis.Y, 0)
            overhangNorm.Rotate(math.radians(overhangProject), rotationAxis)
            strategyMasked, strategyUnmasked, visibleRays = overhangCalc(visibleRays, overhangNorm)
            strategyRemoveIndices = filter(lambda a: a != -1, strategyMasked)
            visibleRemoveIndices = filter(lambda a: a != -1, strategyUnmasked)
            strategyMask = copy.copy(maskedMesh)
            strategyMask.Faces.DeleteFaces(strategyRemoveIndices)
            maskedMesh.Faces.DeleteFaces(visibleRemoveIndices)
        if leftFinProject != None or rightFinProject != None:
            surfaceNorm = rc.Geometry.Vector3d(planeNormal.X, planeNormal.Y, 0)
            srfAngle = math.degrees(rc.Geometry.Vector3d.VectorAngle(surfaceNorm, rc.Geometry.Vector3d.YAxis))
            if surfaceNorm.X > 0:
                srfAngle = 180 + (180-srfAngle)
            if rightFinProject != None: acceptAngleMin = srfAngle - 90 + rightFinProject
            else: acceptAngleMin = srfAngle - 90
            if leftFinProject != None: acceptAngleMax = srfAngle + 90 - leftFinProject
            else: acceptAngleMax = srfAngle + 90
            if acceptAngleMax > 360:
                acceptAngleMax = acceptAngleMax - 360
                acceptAngleMin = acceptAngleMin - 360
            if acceptAngleMax < 0:
                acceptAngleMax = acceptAngleMax + 360
                acceptAngleMin = acceptAngleMin + 360
            
            strategyMasked, strategyUnmasked, visibleRays = finCalc(visibleRays, acceptAngleMin, acceptAngleMax)
            strategyRemoveIndices = filter(lambda a: a != -1, strategyMasked)
            visibleRemoveIndices = filter(lambda a: a != -1, strategyUnmasked)
            finMask = copy.copy(maskedMesh)
            finMask.Faces.DeleteFaces(strategyRemoveIndices)
            try:
                newStrategyMask = rc.Geometry.Mesh()
                newStrategyMask.Append(strategyMask)
                newStrategyMask.Append(finMask)
                strategyMask = newStrategyMask
            except:
                strategyMask = finMask
            maskedMesh.Faces.DeleteFaces(visibleRemoveIndices)
        
        unmaskedMesh = copy.copy(maskedMesh)
    else:
        visibleRays = fullRays
        maskedMesh = copy.copy(hemisphere)
        unmaskedMesh = copy.copy(hemisphere)
    
    
    # join context mesh for fast calculation
    joinedContextMesh = joinMesh(contextMesh)
    
    # run parallel intersection and create a masked/unmasked meshes.
    masked, unmasked = parallelIntersection(visibleRays, joinedContextMesh)
    maskRemoveIndices = filter(lambda a: a != -1, masked)
    unmaskRemoveIndices = filter(lambda a: a != -1, unmasked)
    maskedMesh.Faces.DeleteFaces(maskRemoveIndices)
    unmaskedMesh.Faces.DeleteFaces(unmaskRemoveIndices)
    
    # Color the masked and umasked meshes.
    maskedMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
    unmaskedMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.FromArgb(240,240,240))
    if orientMask != None:
        orientMask.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
    if strategyMask != None:
        strategyMask.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
    
    # If the calculation is for sky view instead of sky exposure, project everything to the plane of the surface.
    if viewPlane == None:
        maskedAreaMesh = maskedMesh
    else:
        planarProject = rc.Geometry.Transform.PlanarProjection(viewPlane)
        maskedAreaMesh = copy.copy(maskedMesh)
        maskedAreaMesh.Transform(planarProject)
        orientMaskAreaMesh = copy.copy(orientMask)
        orientMaskAreaMesh.Transform(planarProject)
        if strategyMask != None:
            strategyMaskAreaMesh = copy.copy(strategyMask)
            strategyMaskAreaMesh.Transform(planarProject)
        hemisphere.Transform(planarProject)
    
    # Compute sky view or exposure.
    skyArea = rc.Geometry.AreaMassProperties.Compute(hemisphere).Area
    
    maskedArea = rc.Geometry.AreaMassProperties.Compute(maskedAreaMesh).Area
    percentageArea = (maskedArea/skyArea) * 100
    if orientMask != None:
        orientArea = rc.Geometry.AreaMassProperties.Compute(orientMaskAreaMesh).Area
        orientAreaPercent = (orientArea/skyArea) * 100
    else:
        orientAreaPercent = 0
    if strategyMask != None:
        strategyArea = rc.Geometry.AreaMassProperties.Compute(strategyMaskAreaMesh).Area
        strategyAreaPercent = (strategyArea/skyArea) * 100
    else:
        strategyAreaPercent = 0
    
    percentageSky = 100 - percentageArea - orientAreaPercent - strategyAreaPercent
    
    # Project the meshes if a projection is specified.
    if projection == 1 or projection == 2:
        maskedMesh  = lb_visualization.projectGeo([maskedMesh], projection, testPt, scale)[0]
        unmaskedMesh = lb_visualization.projectGeo([unmaskedMesh], projection, testPt, scale)[0]
        zTransform = rc.Geometry.Transform.Translation(0,0,-sc.doc.ModelAbsoluteTolerance*5)
        maskedMesh.Transform(zTransform)
        unmaskedMesh.Transform(zTransform)
        if orientMask != None:
            orientMask = lb_visualization.projectGeo([orientMask], projection, testPt, scale)[0]
            orientMask.Transform(zTransform)
        if strategyMask != None:
            strategyMask = lb_visualization.projectGeo([strategyMask], projection, testPt, scale)[0]
            strategyMask.Transform(zTransform)
    
    #If the user has set bakeIt to true, bake the geometry.
    if bakeIt_ > 0:
        #Set up the new layer.
        layerT = rc.RhinoDoc.ActiveDoc.Layers #layer table
        parentLayer = rc.DocObjects.Layer()
        parentLayer.Name = 'SKY_MASK'
        parentLayerIndex = rc.DocObjects.Tables.LayerTable.Find(layerT, 'SKY_MASK', True)
        if parentLayerIndex < 0:
            parentLayerIndex = layerT.Add(parentLayer)
        # Buil list of all meshes.
        allMeshes = [unmaskedMesh]
        if maskedMesh.IsValid:
            allMeshes.append(maskedMesh)
        if orientMask != None:
            allMeshes.append(orientMask)
        if strategyMask != None:
            allMeshes.append(strategyMask)
        # Bake the objects.
        if bakeIt_ == 1:
            lb_visualization.mesh2Hatch(allMeshes, parentLayerIndex)
        else:
            attr = rc.DocObjects.ObjectAttributes()
            attr.LayerIndex = parentLayerIndex
            attr.ColorSource = rc.DocObjects.ObjectColorSource.ColorFromObject
            attr.PlotColorSource = rc.DocObjects.ObjectPlotColorSource.PlotColorFromObject
            for mesh in allMeshes:
                rc.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh, attr)
    
    return maskedMesh, orientMask, strategyMask, unmaskedMesh, "%.2f"%percentageArea, "%.2f"%orientAreaPercent, "%.2f"%strategyAreaPercent, "%.2f"%percentageSky



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




if initCheck == True:
    check = checkTheInputs()
    if check != -1:
        viewMethod, centerPt, viewPlane, scale, skyDensity = check
        #Check exposure or view.
        if viewMethod == 1: setComponentOutputs()
        else: restoreComponentOutputs()
        
        results = main(viewMethod, centerPt, viewPlane, skyDensity, context_, 200*scale, _projection_, overhangProject_, leftFinProject_, rightFinProject_)
        if results!=-1:
            if viewMethod == 1: contextMask, orientationMask, strategyMask, skyMask, contextView, orientView, strategyView, skyView = results
            else: contextMask, orientationMask, strategyMask, skyMask, contextExposure, orientExposure, strategyExposure, skyExposure = results
