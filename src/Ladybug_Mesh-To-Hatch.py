# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to bake a clored mesh into the Rhino scene as a series of colored hatches.  This is particularly useful if you are trying to export ladybug graphics from Rhino to vector-based programs like Inkscape or Illustrator.
-
Provided by Ladybug 0.0.65
    
    Args:
        _mesh: A colored mesh (or list of colored meshes) that you would like to bake into the Rhino scene as a series of colored hatches.
        _runIt: Set to 'True' to run to run the component and bake the mesh into the scene as a series of hatches.
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Ladybug_Mesh-To-Hatch"
ghenv.Component.NickName = 'Mesh2Hatch'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nNOV_05_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Rhino as rc
import System
import scriptcontext as sc

def main():
    #Create a layer to hold the hatches.
    if layerName_ == None:
        parentLayerName = 'LADYBUG_Hatch'
    else:
        parentLayerName = str(layerName_)
    layerT = rc.RhinoDoc.ActiveDoc.Layers #layer table
    parentLayer = rc.DocObjects.Layer()
    parentLayer.Name = parentLayerName
    if visible_ == True:
        parentLayer.IsVisible = True
    else:
        parentLayer.IsVisible = False
    parentLayer.Color =  System.Drawing.Color.Pink
    # Add Parent layer if it's not already created
    parentLayerIndex = rc.DocObjects.Tables.LayerTable.Find(layerT, parentLayerName, True)
    if parentLayerIndex < 0: parentLayerIndex = layerT.Add(parentLayer)
    
    
    #Convert the mesh to a colored hatch.
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    lb_visualization.mesh2Hatch(_mesh, parentLayerIndex)
    
    print "Mesh successfully converted to hatches."


#If Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): pass
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): pass
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck == True and _runIt and len(_mesh) != 0:
    main()