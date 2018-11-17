# ENVI-Met Display
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
Use this component to visualize ENVI-Met v4.0 3D geometry models.
-
Provided by Ladybug 0.0.67
    
    Args:
        basePoint_: Input a point here to move ENVI-Met grid. If no input is provided it will be origin point.
        _INXfileAddress: Output which comes from "ENVI-Met Spaces" or a complete file path of a INX file on your machine.
    Returns:
        readMe!: ...
        buildings: ENVI-Met buildings preview.
        terrain: ENVI-Met terrain preview.
"""

ghenv.Component.Name = "Ladybug_ENVI-Met Display"
ghenv.Component.NickName = 'ENVI-MetDisplay'
ghenv.Component.Message = 'VER 0.0.67\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import os
import re
import clr
import Rhino as rc
import Grasshopper.Kernel as gh

clr.AddReference("System.Xml")
import System.Xml
import scriptcontext as sc


def checkPath():
    if _INXfileAddress[-3:] != 'INX':
        INXfileAddress = _INXfileAddress + '.INX'
    else:
        INXfileAddress = _INXfileAddress
    return INXfileAddress


def makeFolder(subFolder):
    # make a folder
    subFolder = subFolder + '\\'
    appdata = os.getenv("APPDATA")
    try:
        directory = os.path.join(appdata, "Ladybug\ENVIbug", subFolder)
        if not os.path.exists(directory):
            os.makedirs(directory)
    except:
        directory = os.path.join(appdata[:3], "Ladybug\ENVIbug", subFolder)
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    return directory


def ENVIGeometryParser(INXfileAddress):
    
    def generateLists(root, key):
        nestedList = []
        for element in root.GetElementsByTagName(key):
            childs = []
            for child in element.ChildNodes:
                childs.append(child.InnerText[1:-1])
            nestedList.append(childs)
        return nestedList
    
    
    def findTxt(mf, key):
        return mf.GetElementsByTagName(key)[0].InnerText
    
    def cubeProduction(key, dx, dy, dz, basePoint):
        
        # grid dimension
        dimX = rc.Geometry.Interval(-dx/2, dx/2)
        dimY = rc.Geometry.Interval(-dy/2, dy/2)
        
        cubes = []
        for element in root.GetElementsByTagName(key):
            for child in element.ChildNodes:
                cleanText = re.sub('[ \r]', '', child.InnerText)
                cleanLine = cleanText.split('\n')
                for line in cleanLine:
                    if len(line) > 0:
                        numbers = line.split(',')
                        integers = map(float, numbers)
                        if integers[2]<5:
                            plane = rc.Geometry.Plane(rc.Geometry.Point3d((integers[0]*dx+dx/2) + basePoint.X, (integers[1]*dy+dy/2) + basePoint.Y, (integers[2]*dz/5+dz/10) + basePoint.Z), rc.Geometry.Vector3d.ZAxis)
                            cube = rc.Geometry.Box(plane, dimX, dimY, rc.Geometry.Interval(-dz/10, dz/10))
                        else:
                            plane = rc.Geometry.Plane(rc.Geometry.Point3d((integers[0]*dx+dx/2) + basePoint.X, (integers[1]*dy+dy/2) + basePoint.Y, ((integers[2]-4)*dz+dz/2) + basePoint.Z), rc.Geometry.Vector3d.ZAxis)
                            cube = rc.Geometry.Box(plane, dimX, dimY, rc.Geometry.Interval(-dz/2, dz/2))
                        cubes.append(cube)
        return cubes
    
    
    if basePoint_ == None:
        basePoint = rc.Geometry.Point3d.Origin
    else:
        basePoint = basePoint_
    
    
    # path and folder
    folder = makeFolder('Geometry')
    
    metafile = open(INXfileAddress, 'r')
    metainfo = re.sub('3Dplants', 'plants3d', metafile.read())
    metainfo = re.sub('<Enter', '', metainfo)
    
    
    fileCopy = os.path.join(folder, "geoData.xml")
    with open(fileCopy, 'w+') as f:
        f.write(metainfo.encode('utf-8'))
    
    metaXml = System.Xml.XmlDocument()
    
    metaXml.Load(fileCopy)
    root = metaXml.DocumentElement
    
    # dimensions
    dx, dy, dz = float(findTxt(root, "dx"))/unitConversionFactor, float(findTxt(root, "dy"))/unitConversionFactor, float(findTxt(root, "dz-base"))/unitConversionFactor
    
    buildings = cubeProduction("buildings3D", dx, dy, dz, basePoint)
    terrain = cubeProduction("terrainflag", dx, dy, dz, basePoint)
    
    return buildings, terrain


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
    if _INXfileAddress:
        INXfileAddress = checkPath()
        unitConversionFactor = lb_preparation.checkUnits()
        buildings, terrain = ENVIGeometryParser(INXfileAddress)