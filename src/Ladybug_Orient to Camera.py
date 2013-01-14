# This component return a list of planes which are oriented to camera and centered at initPosition
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component return a list of planes which are oriented to camera and centered at initPosition for a better presentation.
Connect a timer to the component for real time update.
-
Provided by Ladybug 0.0.35
    
    Args:
        initPosition: A list of initial base points
        
    Returns:
        report: Report!!!
        orientedToCam: a list of planes which are oriented to camera and centered at initPosition
"""

ghenv.Component.Name = "Ladybug_Orient to Camera"
ghenv.Component.NickName = 'Orient2Camera'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'

import scriptcontext as sc
import Rhino as rc

def main(initPosition):
    cameraX = sc.doc.Views.ActiveView.ActiveViewport.CameraX
    cameraY = sc.doc.Views.ActiveView.ActiveViewport.CameraY
    orientedToCam = rc.Geometry.Plane(initPosition, cameraX, cameraY)
    return orientedToCam

if initPosition: orientedToCam = main(initPosition)