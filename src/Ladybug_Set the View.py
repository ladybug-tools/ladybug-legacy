# This component helps you to set and control the view from Grasshopper
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to set the camera location and direction for the Rhino "Perspective" viewport.
Here is the video that shows how it works: http://www.youtube.com/watch?v=7Mmhz867zY8
-
Provided by Ladybug 0.0.57
    
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
ghenv.Component.Message = 'VER 0.0.57\nMAR_26_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
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
