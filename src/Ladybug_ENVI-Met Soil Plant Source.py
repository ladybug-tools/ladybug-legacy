# ENVI-Met Soil Plant Source
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Use this component to generate ENVI-Met inputs for "LB ENVI-Met Spaces".
-
Some 'plant3Did_' could not work properly.
-
Provided by Ladybug 0.0.67
    
    Args:
        basePoint_: Input a point here to move ENVI-Met grid. If no input is provided it will be origin point.
        _soil_: Geometry that represent ENVI-Met soil.  Geometry must be a Surface or Brep on xy plane.
        _plant2D_: Geometry that represent ENVI-Met plant 2d.  Geometry must be a Surface or Brep on xy plane.
        _plant3D_: Geometry that represent ENVI-Met plant 3d.  Geometry must be a Surface or Brep on xy plane.
        _source_: Geometry that represent ENVI-Met plant 3d.  Geometry must be a Surface or Brep on xy plane.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        -------------: (...)
        _soilId_: ENVI-Met profile id. You can use "id outputs" which comes from "LB ENVI-Met Read Library".
        -
        E.g. L0
        _plantId_: ENVI-Met plant id. You can use "id outputs" which comes from "LB ENVI-Met Read Library".
        -
        E.g. XX
        _plant3Did_: ENVI-Met plant3D id. You can use "id outputs" which comes from "LB ENVI-Met Read Library".
        -
        E.g. PI,.Pinus Pinea
        _sourceId_: ENVI-Met source id. You can use "id outputs" which comes from "LB ENVI-Met Read Library".
        -
        E.g. FT
    Returns:
        readMe!: ...
        envimetPlants: Connect this output to "ENVI-Met Spaces" in order to add plants to ENVI-Met model.
        envimetSoils: Connect this output to "ENVI-Met Spaces" in order to add soils to ENVI-Met model.
        envimetSources: Connect this output to "ENVI-Met Spaces" in order to add sources to ENVI-Met model.
"""

ghenv.Component.Name = "Ladybug_ENVI-Met Soil Plant Source"
ghenv.Component.NickName = 'ENVI-MetSoilPlantSource'
ghenv.Component.Message = 'VER 0.0.67\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh


def setMaterialsPlant(data, dataId, defaultMat, flag, name):
    
    # default materials
    if len(dataId) != len(data) and dataId != []:
        dataMat = [defaultMat]*len(data)
        w = gh.GH_RuntimeMessageLevel.Warning
        message = "Please provide {0} materials for {1}. Otherwise will be used {2}.".format(len(data), name, defaultMat)
        ghenv.Component.AddRuntimeMessage(w, message)
    elif len(dataId) == 0: dataMat = [defaultMat]*len(data)
    else:
        dataMat = dataId
    
    envimetPlants = [(geo, mat, flag) for geo, mat in zip(data, dataMat)]
    
    return envimetPlants


def flatGeometry(geoList, plane):
    xprj = rc.Geometry.Transform.PlanarProjection(plane)
    
    projectedGeo = []
    for geo in geoList:
        if type(geo) == type(rc.Geometry.Brep()):
            rc.Geometry.Brep.ObjectType
            geo.Transform(xprj)
            projectedGeo.append(geo)
        else:
            w = gh.GH_RuntimeMessageLevel.Warning
            message = "Please provide valid breps."
            ghenv.Component.AddRuntimeMessage(w, message)
            return -1
    return projectedGeo


def main():
    
    # default basePoint
    if basePoint_ == None:
        basePoint = rc.Geometry.Point3d.Origin
    else:
        basePoint = basePoint_
    
    plane = rc.Geometry.Plane(basePoint, rc.Geometry.Vector3d.ZAxis)
    
    # run
    plantsTwoD = plantsThreeD = soilD = sourceD = []
    if _plant2D_:
        plant2Dgeometry = flatGeometry(_plant2D_, plane)
        if plant2Dgeometry != -1:
            name = ghenv.Component.Params.Input[1].Name
            plantsTwoD = setMaterialsPlant(plant2Dgeometry, _plantId_, 'XX', 0, name)
    if _plant3D_:
        plant3Dgeometry = flatGeometry(_plant3D_, plane)
        if plant3Dgeometry != -1:
            name = ghenv.Component.Params.Input[2].Name
            plantsThreeD = setMaterialsPlant(plant3Dgeometry, _plant3Did_, 'PI,.Pinus Pinea', 1, name)
    if _soil_:
        soilGeometry = flatGeometry(_soil_, plane)
        if soilGeometry != -1:
            name = ghenv.Component.Params.Input[0].Name
            soilD = setMaterialsPlant(soilGeometry, _soilId_, 'LO', 0, name)
    if _source_:
        sourceGeometry = flatGeometry(_source_, plane)
        if sourceGeometry != -1:
            name = ghenv.Component.Params.Input[3].Name
            sourceD = setMaterialsPlant(sourceGeometry, _sourceId_, 'FT', 0, name)
    
    
    envimetPlants = plantsTwoD + plantsThreeD
    
    return envimetPlants, soilD, sourceD


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
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")


if initCheck:
    result = main()
    if result != -1:
        envimetPlants, envimetSoils, envimetSources = result
        print("There are {} plant objects.".format(str(len(envimetPlants))))
        print("There are {} soil objects.".format(str(len(envimetSoils))))
        print("There are {} source objects.".format(str(len(envimetSources))))