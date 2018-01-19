# This component return a list of planes which are oriented to camera and centered at initPosition
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to generate a plane that is oriented perpendicular to the active Rhino viewport camera direction and centered at an input _initPosition point.
This is useful for orienting geometry Grasshopper to the Rhino viewport camera, which may help in presenting certain Ladybug visualizations in Rhino.
Connect a Grasshopper "Timer" component to the refresh_ input of this component in order to get a real time update of the oriented plane based on the Rhino viewport camera direction.
-
Provided by Ladybug 0.0.66
    
    Args:
        _initPosition: A point or list of points that will act as the origin9s0 of the plane(s) that will be generated.
        refresh_: Connect either a Grasshopper "button" component that will allow you to refresh the plane orientation upon hitting the button or a Grasshopper "Timer" component to see the plane update in real time as you navigate through the Rhino viewport.
    Returns:
        orientedToCam: A plane (or list of planes) for each _initPosition connected. All planes are oriented perpendicular to the active Rhino viewport camera direction and are centered at initPosition points.
"""

ghenv.Component.Name = "Ladybug_Orient to Camera"
ghenv.Component.NickName = 'Orient2Camera'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Rhino as rc

def main(initPosition):
    cameraX = sc.doc.Views.ActiveView.ActiveViewport.CameraX
    cameraY = sc.doc.Views.ActiveView.ActiveViewport.CameraY
    orientedToCam = rc.Geometry.Plane(initPosition, cameraX, cameraY)
    return orientedToCam

if _initPosition:
    orientedToCam = main(_initPosition)
    ghenv.Component.Params.Output[0].Hidden = True
