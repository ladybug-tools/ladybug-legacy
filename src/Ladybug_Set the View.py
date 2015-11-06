# This component helps you to set and control the view from Grasshopper
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Use this component to set the camera location and direction for the Rhino "Perspective" viewport.
Here is the video that shows how it works: http://www.youtube.com/watch?v=7Mmhz867zY8
-
Provided by Ladybug 0.0.61
    
    Args:
        _cameraLocation: A point representing the location of the viewport camera.
        _cameraDirection: A vector that represents the direction that the viewport camera should face.
        uvLookAround_: Optional UV coordinates to tilt the viewport camera off from from the input _cameraDirection. Values for UV coordinates must be between -1 and 1 and these correspond to a tilt of 180 degrees in either direction.  It is recommended that you use a Grasshopper sliderMD comonent for input.
        lensLength_: An optional float number that sets the lens length of the viewport camera.
        
    Returns:
        readMe!: ...
"""
ghenv.Component.Name = "Ladybug_Set the View"
ghenv.Component.NickName = 'setTheView'
ghenv.Component.Message = 'VER 0.0.61\nNOV_05_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import Rhino as rc
import math
import Grasshopper.Kernel as gh

PI = math.pi

def setCamera(cameraLocation, cameraDirection, uvLookAround, lensLength):
    distance = 100
    if uvLookAround!=None:
        # +1 is 180 degrees clockwise
        # -1 is 180 degrees anti clockwise
        u= -uvLookAround.X * PI
        v= uvLookAround.Y * PI
        cameraDirection.Rotate(u, rc.Geometry.Vector3d.ZAxis)
        cameraDirection.Rotate(v, rc.Geometry.Vector3d.CrossProduct(cameraDirection, rc.Geometry.Vector3d.ZAxis))
        
    target = rc.Geometry.Point3d.Add(cameraLocation, distance * cameraDirection)
    sc.doc.Views.ActiveView.ActiveViewport.SetCameraLocation(cameraLocation, True)
    sc.doc.Views.ActiveView.ActiveViewport.SetCameraDirection(cameraDirection, False)
    sc.doc.Views.ActiveView.ActiveViewport.SetCameraTarget(target, False)
    
    if lensLength!=None:
        sc.doc.Views.ActiveView.ActiveViewport.Camera35mmLensLength = lensLength
    
    sc.doc.Views.ActiveView.Redraw()

if _cameraLocation and _cameraDirection:
    setCamera(_cameraLocation, _cameraDirection, uvLookAround_, lensLength_)
elif _cameraLocation == None and _cameraDirection == None:
    print "Connect a _cameraLocation and _cameraDirection."
else:
    msg = "Either the _cameraLocation or _cameraDirection is missing."
    print msg
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
