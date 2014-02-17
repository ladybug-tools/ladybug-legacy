# This component helps you to set and control the view from Grasshopper
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Set the view
Here is the video that shows how it works: http://www.youtube.com/watch?v=7Mmhz867zY8
-
Provided by Ladybug 0.0.54
    
    Args:
        _cameraLocation: A Point3D for the location of camera
        _cameraDirection: A Vector3D that shows the direction of the camera
        sunViewPt_: Optional input for sun position as a point3D
        uvLookAround_: Optional tilt from the camera direction. Use a Point3D or sliderMD for input. The range is between -1 and 1 (-180 to 180 Degrees).
        lensLength_: Optional float number to set the lens length
        
    Returns:
        readMe!: ...
"""
ghenv.Component.Name = "Ladybug_Set the View"
ghenv.Component.NickName = 'setTheView'
ghenv.Component.Message = 'VER 0.0.54\nFEB_16_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

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
else:
    msg = "Either _cameraLocation or _cameraDirection is missing."
    print msg
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
