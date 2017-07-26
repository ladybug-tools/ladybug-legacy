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
Use this component to calculate the day of the year and hour of the year from an input date with a day of the month, month of the year and hour of the day.
-
Provided by Ladybug 0.0.65
    
    Args:
        _days_: A number (or list of numbers) between 1 and 31 that represents the day(s) of the month.
        _months_: A number (or list of numbers) between 1 and 12 that represents the month(s) of the year.
        _hours_: A number (or list of numbers) between 1 and 24 that represents the hour(s) of the day.
    
    Returns:
        DOY: The day of the year on which the input date falls.
        HOY: The hour of the year on which the input date and time fall.
        date: The input information written out as a full date and time text string.
"""

ghenv.Component.Name = "Ladybug_DOY_HOY"
ghenv.Component.NickName = 'DOY/HOY'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

def main(days, months, hours):
    DOY = []
    HOY = []
    date = []
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        for m in months:
            for d in days:
                for h in hours:
                    hour = lb_preparation.checkHour(float(h))
                    month  = lb_preparation.checkMonth(int(m))
                    day = lb_preparation.checkDay(int(d), m, ghenv.Component)
                    HOY.append(lb_preparation.date2Hour(month, day, hour))
                    DOY.append(int(lb_preparation.getJD(month, day)))
                    date.append(lb_preparation.hour2Date(lb_preparation.date2Hour(month, day, hour)))
        return HOY, DOY, date
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1

result = main(_days_, _months_, _hours_)
if result!= -1: HOY, DOY, date = result
