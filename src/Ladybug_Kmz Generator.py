# Kmz Generator
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2020, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Use this component to export geometries into an Google Earth file.
It requires Google Earth. You can download it at this link: https://www.google.it/earth/download/ge/agree.html
Once you open kmz file you can continue to update it. This is useful when you change geometries or you want to compare different scenarios.
.
Updating: Just setting again to "True" _writeKmz, after that right click and select "update" on Google Earth.
-
Special thanks goes to Google and the authors of gHowl.
-
Provided by Ladybug 0.0.68
    
    Args:
        _geometry: A list of Breps, Meshes and Surfaces to export.
        _basePoint_: Input a point here to georeference the model. Default value is origin point.
        _location: It accepts two type of inputs. 
        a) latitude, longitude and elevation that represent WSG84 coordinates of the base point. You can achieve these type of coordinates from Google Maps or similar.
        e.g. 40.821796, 14.426439, 990
        -
        b) location, you can obtain this type of input from "Ladybug_Construct Location", "Ladybug_Location Finder", "Ladybug_Import epw", "Ladybug_Import Location".
        _terrain: Connect the terrain output of "Ladybug_Terrain Generator" to move the geometries in the right altitude automatically.
        ---------------: ---------------
        _folder_: The folder into which you would like to write the kmz file.  This should be a complete file path to the folder.  If no folder is provided, the images will be written to Ladybug default folder.
        name_: Name of kmz file.
        material_: Connect Create Material component of Grasshopper, it is part of Display tab. If not supplied it will be default material.
        _bakeIt: Connect a Grasshopper button. Set to "True" to bake the geometries for Google Earth.
        _writeKmz: Connect a Boolean Toggle. After the baking, set it to "True" to export from Rhino Model to KMZ format.
    Returns:
        readMe!: ...
        kmzPath: Complete path of kmz file.
        pointOnTerrain: basePoint projected on terrain.
        geometry : Geometries on the ground.
"""

ghenv.Component.Name = "Ladybug_Kmz Generator"
ghenv.Component.NickName = 'KmzGenerator'
ghenv.Component.Message = 'VER 0.0.68\nFEB_06_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = 'LB-Legacy'
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import System
import os

def checkInputs(location, geometry,  bakeIt, writeKmz, terrain):
    if location == None or geometry == [] or bakeIt == None or writeKmz == None or terrain == None:
        return False
    elif location and geometry and terrain:
        return True


def findEarthPoint(terrain, basePoint):
    vector = rc.Geometry.Vector3d.ZAxis
    try:
        pointOnTerrain = rc.Geometry.Intersect.Intersection.ProjectPointsToMeshes([terrain], [basePoint], vector, sc.doc.ModelAbsoluteTolerance)
    except:
        pointOnTerrain = rc.Geometry.Intersect.Intersection.ProjectPointsToBreps([terrain], [basePoint], vector, sc.doc.ModelAbsoluteTolerance)
    return pointOnTerrain


def moveGeometry(geometry, terrain, basePoint):
    centroid = rc.Geometry.AreaMassProperties.Compute(geometry).Centroid
    pointOnPlane = rc.Geometry.Point3d(centroid.X, centroid.Y, basePoint.Z)
    
    try:
        pointOnTerrain_geometry = findEarthPoint(terrain, pointOnPlane)[0]
    except IndexError:
        pointOnTerrain_geometry = rc.Geometry.Point3d(centroid.X, centroid.Y, basePoint.Z)
        warning = "Some geometries are outside the terrain area.\n" + \
        "You should move them manually after the baking."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    vec1 = rc.Geometry.Vector3d(pointOnTerrain_geometry)
    vec2 = rc.Geometry.Vector3d(pointOnPlane)
    vec3 = rc.Geometry.Vector3d.Add(vec1, -vec2)
    
    geometry.Translate(vec3)
    
    return geometry


def setReferencePoint(pointOnTerrain, latitude, longitude, elevation):
    p = rc.DocObjects.EarthAnchorPoint()
    p.EarthBasepointLatitude = latitude
    p.EarthBasepointLongitude = longitude
    p.EarthBasepointElevation = elevation
    p.ModelBasePoint = pointOnTerrain
    p.ModelEast = rc.Geometry.Vector3d.XAxis
    p.ModelNorth = rc.Geometry.Vector3d.YAxis
    
    rc.RhinoDoc.ActiveDoc.EarthAnchorPoint = p


def bakeGeometry(geometries, materialFromUser):
    layerName = 'buildings'
    layerIndex, l = lb_visualization.setupLayers(layerName, "LADYBUG", projectName = "GEOMETRY", studyLayerName = "LB_TERRAIN") # here I have to understand how to enable all sublayers
    for i, obj in enumerate(geometries):
        attr = rc.DocObjects.ObjectAttributes()
        attr.LayerIndex = layerIndex
        attr.ColorSource = rc.DocObjects.ObjectColorSource.ColorFromObject
        attr.ObjectColor = System.Drawing.Color.GreenYellow
        
        # user's material
        if materialFromUser != None:
            materialIndex = sc.doc.Materials.Add()
            material = sc.doc.Materials[materialIndex]
            
            material.AmbientColor = materialFromUser.Ambient
            material.DiffuseColor = materialFromUser.Diffuse
            material.EmissionColor = materialFromUser.Emission
            material.SpecularColor = materialFromUser.Specular
            material.Transparency = materialFromUser.Transparency
            material.Shine = materialFromUser.Shine
            
            material.CommitChanges()
            attr.MaterialSource = rc.DocObjects.ObjectMaterialSource.MaterialFromObject
            attr.MaterialIndex = materialIndex
        
        id = rc.RhinoDoc.ActiveDoc.Objects.Add(obj, attr)


def mdPath(folder):
    # make a folder for the images
    if folder != None:
        directory = folder + '\\' # it work also with Desktop as folder
        if not os.path.exists(folder):
            try:
                os.mkdir(directory)
            except Exception:
                appdata = os.getenv("APPDATA")
                directory = os.path.join(appdata, "Ladybug\LB_Kmz\\")
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Invalid Folder, you can find images here: {}".format(directory))
    else:
        appdata = os.getenv("APPDATA")
        directory = os.path.join(appdata, "Ladybug\LB_Kmz\\")
        if not os.path.exists(directory): os.makedirs(directory)
    
    return directory


def main():
    
    # default values
    if _basePoint_ == None:
        basePoint = rc.Geometry.Point3d.Origin
    else:
        basePoint = _basePoint_
    
    if _folder_ == None:
        path = mdPath(_folder_)
    else:
        path = _folder_
    
    if name_ == None:
        name = "Ladybug_GoogleEarth.kmz"
    else:
        name = name_
    
    fullPath = os.path.join(path, name)
    
    
    # file!
    fileName = '!-Save "{}"'.format(fullPath)
    
    if material_ == None: materialFromUser = None
    else: materialFromUser = material_
    sc.doc = rc.RhinoDoc.ActiveDoc
    
    
    # location or point3d
    try:
        latitude, longitude, elevation = eval(_location)
        location = rc.Geometry.Point3d(latitude, longitude, elevation)
    except:
        locationName, latitude, longitude, timeZone, elevation = lb_preparation.decomposeLocation(_location)
        location = rc.Geometry.Point3d(latitude, longitude, elevation)
    
    
    pointOnTerrain = findEarthPoint(_terrain, basePoint)
    setReferencePoint(pointOnTerrain[0], latitude, longitude, 0)
    geometryOnTerrain = [moveGeometry(geo, _terrain, basePoint) for geo in _geometry]
    
    # avoid bakeIt
    if _writeKmz == True and _bakeIt == True: bakeIt = None
    else: bakeIt = _bakeIt
    
    if bakeIt:
        bakeGeometry(geometryOnTerrain, materialFromUser)
    if _writeKmz:
        # remark for users
        w = gh.GH_RuntimeMessageLevel.Remark
        ghenv.Component.AddRuntimeMessage(w, "if you want to bake again you have to switch '_writeKmz' to False")
        rs.Command(fileName)
        
        return geometryOnTerrain, pointOnTerrain, fullPath
    
    return geometryOnTerrain, pointOnTerrain, None


initCheck = False
if sc.sticky.has_key('ladybug_release'):
    initCheck = True
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = True
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")

check = checkInputs(_location, _geometry, _bakeIt, _writeKmz, _terrain)
if check and initCheck:
    buttonTest = ghenv.Component.Params.Input[8].Sources[0]
    if buttonTest.Name == 'Button':
        result = main()
        if result != -1:
            geometry, pointOnTerrain, kmzPath = result
            if _writeKmz: print("kmz done! Check on your Desktop.")
    else:
        warning = "_bakeIt should be a Button. You can find it in Params/Input."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else:
    pass
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "Please provide all inputs.")
    #print("Please provide all inputs.")