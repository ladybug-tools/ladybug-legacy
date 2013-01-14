# This is a simple script that export orintation study parameters as a string
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component sets up the parameters for orientation study
-
Provided by Ladybug 0.0.35
    
    Args:
        divisionAngle: A number that indicates the division angle
        totalAngle: A number that indicates the study range. Total angle should be larger and divisible by the division angle
        basePoint: A Point that indicates rotation base point. Default will be the center of the test geometry
        rotateContext: [Boolean] If set to True context will also rotate with the test geometry  
        runTheStudy: [Boolean] Since orientation study may take a long time, this is an extra
                     confirmation request to make sure that you really want to run the oriantation study!
                     [courtesy of windows Vista...;)]
    Returns:
        report: Report!!!
        orientationStudyPar: Orientation study parameters as a list
"""

ghenv.Component.Name = "Ladybug_Orientation Study Parameters"
ghenv.Component.NickName = 'orientationStudyPar'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'

import Rhino as rc
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

if not rotateContext!=None: rotateContext = False
if not runTheStudy!=None: runTheStudy = False
# if not basePoint!=None: basePoint = rc.Geometry.Point3d(0,0,0)
if (divisionAngle and totalAngle):
    if orientaionStr(divisionAngle, totalAngle)!=0:
        orientationStudyPar = runTheStudy, rotateContext, basePoint, orientaionStr(divisionAngle, totalAngle)
else:
    print "Please provide both division angle and total angle."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "Please provide both division angle and total angle.")