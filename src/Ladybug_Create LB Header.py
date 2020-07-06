# This component generates a Ladybug Header that can be combined with any raw data in order to format it for use with the Ladybug/Honeybee components
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2020, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to generates a Ladybug Header that can be combined with any raw data in order to format it for use with the Ladybug/Honeybee components.
_

This component is particularly useful if you are bringing in data from other plugins or from instrumental measurements and you want to visualize it or analyze it with the Ladybug and Honeybee components.  It is also useful if you want to replace the header on Ladybug data.
-
Provided by Ladybug 0.0.69
    
    Args:
        location_: A text string that represents the name of the location where the data was collected.  If no value is connected here, the default will be "Somewhere."
        dataType_: A text string that represents the type of data that the header corresponds to.  This can be "Temperature", "Wind", etc.  If no value is connected here, the default will be "Some Data."
        units_: A text string that represents the units of the data. This can be "C", "m/s", etc.  If no value is connected here, the default will be "Some Units."
        timeStep_:  A text string that represents the time step of the data.  Acceptable values include "Hourly", "Daily", "Monthly", or "Annually."  If no value is connected here, the default will be "Hourly."
        analysisPeriod_: An optional analysis period from the Analysis Period component.  If no analysis period is given, the default will be for the enitre year: (1,1,1)(12,31,24).
        rawData_: A list of data that you want to add/modify Ladybug Header
    Returns:
        LBHEader: A Ladybug header that can be combined with any raw data in order to format it for the Ladybug and Honeybee components.
        dataWithHeader: A list of data with added/modified Ladybug header
"""

ghenv.Component.Name = "Ladybug_Create LB Header"
ghenv.Component.NickName = 'CreateHeader'
ghenv.Component.Message = 'VER 0.0.69\nJUL_07_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "LB-Legacy"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning


def setDefaults(Header):
    checkData = True
    defaultHeader = ['key:location/dataType/units/frequency/startsAt/endsAt', 'Somewhere', 'Some Data', 'Some Units', 'Hourly', (1, 1, 1), (12, 31, 24)]

    if (len(Header) == 7):
        defaultHeader = Header
    
    #Set a default location.
    if location_ == None: location = defaultHeader[1]
    else:location = location_
    
    
    #Set a default dataType.
    if dataType_ == None: dataType = defaultHeader[2]
    else: dataType = dataType_
    
    #Set a default units.
    if units_ == None: units = defaultHeader[3]
    else: units = units_
    
    #Set a default analysis period.
    if analysisPeriod_ == []: analysisPeriod = [defaultHeader[5], defaultHeader[6]]
    else:
        if len(analysisPeriod_) == 2: analysisPeriod = analysisPeriod_
        else:
            analysisPeriod = None
            checkData = False
            warning = "analysisPeriod_ is not valid."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the timpeStep_.
    if timeStep_ == None: timeStep = defaultHeader[4]
    else:
        if timeStep_ == "Hourly" or timeStep_ == "Daily" or timeStep_ == "Monthly" or timeStep_ == "Annually": timeStep = timeStep_
        else:
            timeStep = None
            checkData = False
            warning = "timeStep_ is not valid."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    
    return checkData, location, dataType, units, timeStep, analysisPeriod

def checkRawData(rawD):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    indexList, oldHeader = lb_preparation.separateList(rawD, lb_preparation.strToBeFound)
    separatedLists = rawD[indexList[0]+7:indexList[1]]
    return separatedLists, oldHeader[0]

def main(location, dataType, units, timeStep, analysisPeriod):
    header = ['key:location/dataType/units/frequency/startsAt/endsAt', location, dataType, units, timeStep]
    header.extend(analysisPeriod)
    
    return header

dataList, oldHeader = checkRawData(rawData_)
checkData, location, dataType, units, timeStep, analysisPeriod = setDefaults(oldHeader)
newData = []

if checkData == True:
    LBHeader = main(location, dataType, units, timeStep, analysisPeriod)
    newData.extend(LBHeader)
    newData.extend(dataList)
    dataWithHeader=newData