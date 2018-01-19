# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
#
# This file is part of Ladybug.
#
# Copyright (c) 2013-2015, Byron Mardas <byronmardas@gmail.com>
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
Use this component to set the Rhino sun from grasshopper and coordinate your Rhino visualizations with the Ladybug weatherfile and other solar parameters.
-
Provided by Ladybug 0.0.66
    Args:
        _location: get location from Ladybug_Import epw component. This will update rhino solar system to the correct coordinates and timezone
        north_: North direction of the model. This can be either an number representing angle, or a vector. (by default North is set on the y axis)
        _month_: A number that represents the month you want to visualize
        _day_: A number that represents the Day you want to visualize
        _hour_: A number that represents the Hour you want to visualize
        _runIt: Set to True to run the component and position the Rhino Sun.
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Ladybug_Set Rhino Sun"
ghenv.Component.NickName = 'rhinoSun'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
import Rhino
import Rhino.Render.Sun as sun
import ghpythonlib.components as ghp
import scriptcontext as sc
import math

def checkTheInputs():
    if (_month_ <= 12 and _month_ >= 1) or _month_ == None:
        pass
    else:
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "_month_ has to be a number between 1 and 12")
        return -1
    
    if (_day_ <= 31 and _day_ >= 1) or _day_ == None:
        pass
    else:
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "_day_ has to be a number between 1 and 31")
        return -1
    
    if (_hour_ <= 24 and _hour_ >= 0) or _hour_ == None:
        if _hour_ == 24:
            hour = 0
        else:
            hour = _hour_
    else:
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "_hour_ has to be a number between 1 and 24")
        return -1
    
    return hour


def main(location, month, day, hour, north, lb_preparation):
    # Set defaults
    if month == None:
        month = 12
    if day == None:
        day = 21
    if hour == None:
        hour = 12
    
    # From _location split and referense latitude, longitude and timezone
    lat = (location.split("\n"))[2]
    latitude = lat.split(",")[0]
    long = (location.split("\n"))[3]
    longitude = long.split(",")[0]
    off = (location.split("\n"))[4]
    offset = off.split(",")[0]
    offset = int(math.ceil(float(offset)))
    
    h = int(math.modf(hour)[1])
    m = int(60*(math.modf(hour)[0]))
    date = ghp.ConstructDate(2017,month,day,h,m,0)
    sunPosition = Rhino.RhinoDoc.ActiveDoc.Lights.Sun
    sun.Enabled.SetValue(sunPosition,True)
    sun.TimeZone.SetValue(sunPosition,offset)
    sun.SetPosition(sunPosition, date, float(latitude), float(longitude)) #Adjust _location and Date of Rhino Sun
    
    print "Sun position latitude / longitude set to: " + str(latitude) + " / " + longitude
    print "Sun position date set to: " + str(date)
    
    if sun.Altitude.Info.GetValue(sunPosition) > 0:
        #set Orientation
        if north == None:
            sun.North.SetValue(sunPosition, 90)
        else:
            northAngle, northVector = lb_preparation.angle2north(north)
            sun.North.SetValue(sunPosition, (90+math.degrees(northAngle)))
            print "North angle set to : " + str(math.degrees(northAngle))


#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True
w = gh.GH_RuntimeMessageLevel.Warning
#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
        lb_preparation = sc.sticky["ladybug_Preparation"]()
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


#If the intital check is good, run the component.
if initCheck and _runIt == True:
    hour = checkTheInputs()
    if hour != -1:
        main(_location, _month_, _day_, hour, north_, lb_preparation)
elif _runIt == False or _runIt == None:
    Rhino.RhinoDoc.ActiveDoc.Lights.Sun.Enabled = False
