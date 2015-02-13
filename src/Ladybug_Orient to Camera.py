# This component return a list of planes which are oriented to camera and centered at initPosition
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to generate a plane that is oriented perpendicular to the active Rhino viewport camera direction and centered at an input _initPosition point.
This is useful for orienting geometry Grasshopper to the Rhino viewport camera, which may help in presenting certain Ladybug visualizations in Rhino.
Connect a Grasshopper "Timer" component to the refresh_ input of this component in order to get a real time update of the oriented plane based on the Rhino viewport camera direction.
-
Provided by Ladybug 0.0.59
    
    Args:
        _initPosition: A point or list of points that will act as the origin9s0 of the plane(s) that will be generated.
        refresh_: Connect either a Grasshopper "button" component that will allow you to refresh the plane orientation upon hitting the button or a Grasshopper "Timer" component to see the plane update in real time as you navigate through the Rhino viewport.
    Returns:
        orientedToCam: A plane (or list of planes) for each _initPosition connected. All planes are oriented perpendicular to the active Rhino viewport camera direction and are centered at initPosition points.
"""

ghenv.Component.Name = "Ladybug_Orient to Camera"
ghenv.Component.NickName = 'Orient2Camera'
ghenv.Component.Message = 'VER 0.0.59\nFEB_01_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
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
