#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to convert any list of annual data into a data tree branched by day of the year, month of the year, or hour of the day. If the data is not 8760 value sof each hour, the number of _data items should match number of items in HOY_.
-
Provided by Ladybug 0.0.66
    
    Args:
        _data: A list of data to be branched for each month, day and hour.  Note that this can be either a list of 8760 values for each hour of the year, the output of the "Import EPW" component, or a custom list of data that is matched by the data in the HOY_ input.
        HOY_: A list of numbers between 1 and 8760 that represents an hour of the year.
    Returns:
        dataEachDayOfYear: The input data that has been branched data for each day of the year. The paths of the branches are in the following format {month ; dayOfMonth}.
        dataEachMonth: The input data that has been branched for each month of the year. Branch paths are from 0 to 11.
        dataEachHourOfDay: The input data that has been branched for each hour of the day. Branches are from 0 to 23.
"""

ghenv.Component.Name = "Ladybug_Branch Data"
ghenv.Component.NickName = 'branchDataDailyMonthlyHourly'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def checkTheInputs(data, HOY, lb_preparation):
    checkData = True
    try:
        if len(data) == len(HOY): pass
        elif len(data) == 8760:
            #We are pretty sure that the user just wants to branch annual hourly data so HOY is not required.
            if HOY == []: HOY = range(1,8761)
            else:
                checkData = False
                warning = "Number of items in _data should match the number of hours."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        elif 'key:location/dataType/units/frequency/startsAt/endsAt' in data[0] and 'Hourly' in data[4]:
            #The user just wants to branch epw data and we should pull the HOYs from the analysis period of the data.
            if len(data) == 8767: HOY = range(1,8761)
            else:
                analysisPeriod = [data[5], data[6]]
                HOY, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
            data = data[7:]
        else:
            checkData = False
            warning = "The connected _data is not recognized as annual data. \n Plug in values for HOY_ that correspond to input _data."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    except:
        checkData = False
        warning = "The connected _data is not recognized as annual data. \n Plug in values for HOY_ that correspond to input _data."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    return checkData, data, HOY

def main(data, HOY, lb_preparation):
    # prepare empty lists
    dataEachDayOfYear = DataTree[Object]()
    dataEachMonth = DataTree[Object]()
    dataEachHourOfDay = DataTree[Object]()
    #for day in range(365): dataEachDayOfYear.AddRange([], GH_Path(day))
    for month in range(12): dataEachMonth.AddRange([], GH_Path(month))
    for hour in range(24): dataEachHourOfDay.AddRange([], GH_Path(hour))
    
    for dd, hoy in zip(data, HOY):
        d, m, t = lb_preparation.hour2Date(hoy, True)
        dataEachDayOfYear.Add(dd, GH_Path(m,d-1))
        dataEachMonth.Add(dd, GH_Path(m))
        dataEachHourOfDay.Add(dd, GH_Path(t-1))
            
    return dataEachDayOfYear, dataEachMonth, dataEachHourOfDay


# import the classes
lb_preparation = []
initCheck = True
if sc.sticky.has_key('ladybug_release'):
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        initCheck = False
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")


if len(_data) > 0 and initCheck == True:
    checkData, data, HOY = checkTheInputs(_data, HOY_, lb_preparation)
    if checkData:
        result = main(data, HOY, lb_preparation)
        if result!=-1: dataEachDayOfYear, dataEachMonth, dataEachHourOfDay = result
