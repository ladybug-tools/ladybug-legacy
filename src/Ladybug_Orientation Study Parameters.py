# This is a simple script that export orintation study parameters as a string
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component sets up the parameters for orientation study
-
Provided by Ladybug 0.0.52
    
    Args:
        divisionAngle: A number that indicates the division angle
        totalAngle: A number that indicates the study range. Total angle should be larger and divisible by the division angle
        basePoint: A Point that indicates rotation base point. Default will be the center of the test geometry
        rotateContext: Boolean or geometry. If set to True context will also rotate with the test geometry
                       If you connect geometries these geometries will be rotated with the test geometries
        runTheStudy: [Boolean or GeometryBase] Since orientation study may take a long time, this is an extra
                     confirmation request to make sure that you really want to run the oriantation study!
                     [courtesy of Windows Vista...;)] If you want part of the context to roatate with the test geometry the connect it here!
    Returns:
        orientationStudyPar: Orientation study parameters as a list
"""

ghenv.Component.Name = "Ladybug_Orientation Study Parameters"
ghenv.Component.NickName = 'orientationStudyPar'
ghenv.Component.Message = 'VER 0.0.52\nNOV_01_2013'

import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

def orientaionStr(divisionAngle, totalAngle):
    divisionAngle = float(divisionAngle)
    totalAngle = float(totalAngle)
    # check the numbers
    if divisionAngle> totalAngle:
        print "Division angle cannot be bigger than the total angle!"
        w = gh.GH_RuntimeMessageLevel.Error
        ghenv.Component.AddRuntimeMessage(w, "Division angle cannot be bigger than the total angle!")
        return 0
    elif totalAngle%divisionAngle!=0:
        print "Total angle should be divisible by the division angle!"
        w = gh.GH_RuntimeMessageLevel.Error
        ghenv.Component.AddRuntimeMessage(w, "Total angle should be divisible by the division angle!")
        return 0
    else:
        return [0] + rs.frange(0, totalAngle, divisionAngle)


# import the classes
if sc.sticky.has_key('ladybug_release'):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    if rotateContext_==[] or rotateContext_[0]==False: rotateContext_ = False
    elif rotateContext_[0]==True: rotateContext_ = True
    else:
        # just carry the geometries to next component
        contextMesh, contextBrep = lb_preparation.cleanAndCoerceList(rotateContext_)
        rotateContext_ = contextMesh, contextBrep
    
    if not _runTheStudy!=None: _runTheStudy = False
    # if not basePoint!=None: basePoint = rc.Geometry.Point3d(0,0,0)
    if (_divisionAngle and _totalAngle):
        if orientaionStr(_divisionAngle, _totalAngle)!=0:
            orientationStudyPar = _runTheStudy, rotateContext_, basePoint_, orientaionStr(_divisionAngle, _totalAngle)
        ghenv.Component.Params.Output[0].Hidden = True
    else:
        print "Please provide both division angle and total angle."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please provide both division angle and total angle.")
else:
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
