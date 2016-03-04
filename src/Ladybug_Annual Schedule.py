# Sun Path values
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Use this component to generate values for Honeybee_Create CSV Schedule
-
Use this component to write schedules for EnergyPlus using LB_schedules as inputs.
-
Provided by Ladybug 0.0.62
    
    Args:
        _sun: Sunday. Connect a LB_schedule.
        _mon: Monday. Connect a LB_schedule.
        _tue: Tuesday. Connect a LB_schedule.
        _wed: Wednesday. Connect a LB_schedule.
        _thu: Thursday. Connect an LB_schedule.
        _fri: Friday. Connect a LB_schedule.
        _sat: Saturday. Connect a LB_schedule.
        ------------: ...
        _epwFile: An .epw file path on your system as a string.
        _runIt: Set to "True" to run the component
        holiday_: Optional input. Connect a LB_schedule for the holidays.
        analysisPeriod_: If your input units do not represent a full year, use this input to specify the period of the year that the schedule applies to.
    Returns:
        readMe!: ...
        scheduleValues: The values to be written into the .csv schedule. Connect it to "_values/Honeybee_Create CSV Schedule". 
"""

ghenv.Component.Name = "Ladybug_Annual Schedule"
ghenv.Component.NickName = 'AnnualSchedule'
ghenv.Component.Message = 'VER 0.0.62\nFEB_08_2016'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

def checkTheData(sun, mon, tue, wed, thu, fri, sat, epw, run):
    if run == False:
        run = "off"
    elif run == True:
        run = "on"
    if sun == None \
    and mon == None and tue == None and wed == None \
    and thu == None and fri == None and sat == None \
    and epw == None and run == None:
        checkData = False
    elif sun and mon and tue and wed and thu and fri and sat and epw and run:
        checkData = False
    else: checkData = True
    return checkData

def weekFormula(year, hoy):
    
    dayWeek = (year + (year-1) % 4 - (year-1) % 100 + (year-1) % 400 + hoy) % 7
    return dayWeek

def flatten(container):
    for i in container:
        if isinstance(i, list) or isinstance(i, tuple):
            for j in flatten(i):
                yield j
        else:
            yield i

def main():
    if _runIt == True:
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        locationData = lb_preparation.epwLocation(_epwFile)
        yearEpw = lb_preparation.epwDataReader(_epwFile, locationData[0])[14]
        year = int(yearEpw[8])
        print "The year from which the hourly data has been extracted is: %s" %year
        
        dayWeekList = []
        
        for day in range(365):
            dayWeekList.append(weekFormula(year, day))
        
        if holiday_:
            holidays = [0, 1, 42, 102, 105, 126, 154, 217, 358, 359]
            for index in sorted(holidays, reverse=True):
                dayWeekList[index] = 7
        
        try:
            for n,i in enumerate(dayWeekList):
                if i==0:
                    dayWeekList[n]=_sat
                elif i ==1:
                    dayWeekList[n]=_sun
                elif i ==2:
                    dayWeekList[n]=_mon
                elif i ==3:
                    dayWeekList[n]=_tue
                elif i ==4:
                    dayWeekList[n]=_wed
                elif i ==5:
                    dayWeekList[n]=_thu
                elif i ==6:
                    dayWeekList[n]=_fri
                elif i ==7:
                    dayWeekList[n]= holiday_
                    
        except: pass
        annualSchedule = list(flatten(dayWeekList))
        
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod_, 1)
        max = HOYS[len(HOYS)-1]
        min = HOYS[0]-1
        
        scheduleValues = annualSchedule[min:max]
        return scheduleValues
    else:
        return-1



# import the classes
initCheck = False
if sc.sticky.has_key('ladybug_release'):
    initCheck = True
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = True
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")

#Check the data to make sure it is the correct type
checkData = False
if initCheck == True:
    checkData = checkTheData(_sun, _mon, _tue, _wed, _thu, _fri, _sat, _epwFile, _runIt)
    
    if checkData == False:
        result = main()
        if result != -1:
            scheduleValues = result
            print 'scheduleValues completed!'
    else:
        print 'Please provide all _inputs'