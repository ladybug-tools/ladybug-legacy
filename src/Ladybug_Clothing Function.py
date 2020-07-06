# Clothing Schedule
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
Use this component to generate a list of values representing a clothing schedule based on outdoor air temperature.  This schedule can be plugged into the clothingLevel_ input of the PMV Comfort Calculator component.
By default, this function used to derive clothing levels based on outside temperature was developed by Schiavon, Stefano and implemented on the CBE comfort tool (http://smap.cbe.berkeley.edu/comforttool/).
This version of the component allows users to change the maximum and minimum clothing levels, which Schiavon set at 1 and 0.46 respectively, and the temperatures at which these clothing levels occur, which Schiavon set at 26C and -5 C respectively.
Note that Schiavon did not endorse the changing of these values but they are provided here to allow users an additional level of freedom.
-
Provided by Ladybug 0.0.69
    
    Args:
        _outdoorAirTemperature: A number or list of numbers representing the dry bulb temperature of the air in degrees Celcius.  This input can also accept the direct output of dryBulbTemperature from the Import EPW component and this is recommended for hourly comfort analysis.
        analysisPeriod_: If you have hooked up annual temperatures from the importEPW component, use this input to 
        maxClo_: An optional number representing the maximum clo value that someone will wear on the coldest days of the outdoorAirTemperature input.  The default is set to 1 clo, which corresponds to a 3-piece suit.
        maxCloTemp_: An optional number representing the temperature at which the maxClo_ value will be applied.  The default is set to -5C, which means that any lower temperature will get the maxClo_ value.
        minClo_: An optional number representing the minimum clo value that someone will wear on the hotest days of the outdoorAirTemperature input.  The default is set to 0.46 clo, which corresponds to shorts and a T-shirt.
        minCloTemp_: An optional number representing the temperature at which the minClo_ value will be applied.  The default is set to 26C, which means that any higher temperature will get the minClo_ value.
    Returns:
        readMe!: ...
        cloValues: A list of numbers representing the clothing that would be worn at each hour of the _outdoorAirTemperature.  Note that, if the component senses that you have hooked up a stream of hourly data, the clothing levels will alternate on a 12-hour basis.

"""
ghenv.Component.Name = "Ladybug_Clothing Function"
ghenv.Component.NickName = 'CloFunction'
ghenv.Component.Message = 'VER 0.0.69\nJUL_07_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "LB-Legacy"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Grasshopper.Kernel as gh
import math
import scriptcontext as sc


def checkTheInputs(lb_preparation):
    #Define a value that will indicate whether someone has hooked up epw data.
    epwData = False
    epwStr = []
    
    #Check lenth of the _outdoorAirTemperature list and evaluate the contents.
    checkData = False
    airTemp = []
    airMultVal = False
    if len(_outdoorAirTemperature) != 0:
        try:
            if "Temperature" in _outdoorAirTemperature[2]:
                airTemp = _outdoorAirTemperature[7:]
                checkData = True
                epwData = True
                epwStr = _outdoorAirTemperature[0:7]
        except: pass
        if checkData == False:
            for item in _outdoorAirTemperature:
                try:
                    airTemp.append(float(item))
                    checkData = True
                except: checkData = False
        if len(airTemp) > 1: airMultVal = True
        if checkData == False:
            warning = '_outdoorAirTemperature input does not contain valid temperature values in degrees Celcius.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'Connect a temperature in degrees celcius for _outdoorAirTemperature'
    
    #Check to see if the user has connected anything for max and min clos and temperatures and, if not, set defaults.
    if maxClo_ == None:
        maxClo = 1
        print "No value connected for maxClo_.  The default will be set to 1 clo."
    else: maxClo = maxClo_
    
    if maxCloTemp_ == None:
        maxCloTemp = -5
        print "No value connected for maxCloTemp_.  The default will be set to -5C."
    else: maxCloTemp = maxCloTemp_
    
    if minClo_ == None:
        minClo = 0.46
        print "No value connected for minClo_.  The default will be set to 0.46 clo."
    else: minClo = minClo_
    
    if minCloTemp_ == None:
        minCloTemp = 26
        print "No value connected for minCloTemp_.  The default will be set to 26C."
    else: minCloTemp = minCloTemp_
    
    #Check to make sure that the difference between the max and min clo temps is greater than 10.
    if minCloTemp - maxCloTemp < 10:
        checkData = False
        warning = 'The difference between the _minCloTemp and _maxCloTemp must be at least 10C in order for the function to work correctly.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Define a function to split up the hours into 12-hour periods.
    def chunks(l, n):
        if n < 1:
            n = 1
        return [l[i:i + n] for i in range(0, len(l), n)]
    
    #Define a function to duplicate data.
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    # If the user has input EPW data, format it so that we get the average temperature for each 12-hour period.
    if epwData == True:
        chunksList = chunks(airTemp[6:], 12)
        avgAirTemps = []
        avgAirTemps.extend(duplicateData([sum(airTemp[:6])/6], 6))
        for list in chunksList:
            listAvg = sum(list)/len(list)
            avgAirTemps.extend(duplicateData([listAvg], len(list)))
    
    # Check to see if the user has connected an analysis period along with outdoor air temperatures.
    if epwData == True and len(analysisPeriod_) > 0:
        HOYS, months, days =  getHOYsBasedOnPeriod(analysisPeriod_, 1, lb_preparation)
        finalAirTemps = []
        for hoy in HOYS:
            finalAirTemps.append(avgAirTemps[hoy-1])
    elif epwData == True:
        finalAirTemps = avgAirTemps
    else: finalAirTemps = airTemp
    
    calcLength = len(finalAirTemps)
    
    #Let's return everything we need.
    return checkData, epwData, epwStr, calcLength, finalAirTemps, maxClo, maxCloTemp,  minClo, minCloTemp


def getHOYs(hours, days, months, timeStep, lb_preparation, method = 0):
    
    if method == 1: stDay, endDay = days
        
    numberOfDaysEachMonth = lb_preparation.numOfDaysEachMonth
    
    if timeStep != 1: hours = rs.frange(hours[0], hours[-1] + 1 - 1/timeStep, 1/timeStep)
    
    HOYS = []
    
    for monthCount, m in enumerate(months):
        # just a single day
        if method == 1 and len(months) == 1 and stDay - endDay == 0:
            days = [stDay]
        # few days in a single month
        
        elif method == 1 and len(months) == 1:
            days = range(stDay, endDay + 1)
        
        elif method == 1:
            #based on analysis period
            if monthCount == 0:
                # first month
                days = range(stDay, numberOfDaysEachMonth[monthCount] + 1)
            elif monthCount == len(months) - 1:
                # last month
                days = range(1, lb_preparation.checkDay(endDay, m) + 1)
            else:
                #rest of the months
                days = range(1, numberOfDaysEachMonth[monthCount] + 1)
        
        for d in days:
            for h in hours:
                h = lb_preparation.checkHour(float(h))
                m  = lb_preparation.checkMonth(int(m))
                d = lb_preparation.checkDay(int(d), m)
                HOY = lb_preparation.date2Hour(m, d, h)
                if HOY not in HOYS: HOYS.append(int(HOY))
    
    return HOYS

def getHOYsBasedOnPeriod(analysisPeriod, timeStep, lb_preparation):
    
    stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, True, False)
    
    if stMonth > endMonth:
        months = range(stMonth, 13) + range(1, endMonth + 1)
    else:
        months = range(stMonth, endMonth + 1)
    
    # end hour shouldn't be included
    hours  = range(stHour, endHour + 1)
    
    days = stDay, endDay
    
    HOYS = getHOYs(hours, days, months, timeStep, lb_preparation, method = 1)
    
    return HOYS, months, days


def schiavonClo(airTemp, maxClo, maxCloTemp,  minClo, minCloTemp, f1Slope, f1yInt, f2Slope, f2yInt):
    if airTemp <= maxCloTemp:
        cloVal = maxClo
    elif airTemp > maxCloTemp and airTemp < maxCloTemp+10:
        cloVal = airTemp*f1Slope + f1yInt
    elif airTemp > maxCloTemp and airTemp < minCloTemp:
        cloVal = airTemp*f2Slope + f2yInt
    else: cloVal = minClo
    
    return cloVal


def main():
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
    
    #Check the inputs and organize the incoming data into streams that can be run throught the comfort model.
        checkData = False
        checkData, epwData, epwStr, calcLength, finalAirTemps, maxClo, maxCloTemp,  minClo, minCloTemp = checkTheInputs(lb_preparation)
        
        #If everything looks good, run the results through the clo function.
        if checkData == True:
            finalCloValues = []
            
            cloDifference = maxClo-minClo
            f1Slope = ((maxClo - cloDifference*.75) - maxClo)/10
            f1yInt = maxClo - (f1Slope*maxCloTemp)
            try:
                f2Slope = (minClo - (maxClo - cloDifference*.75))/(minCloTemp - (maxCloTemp+10))
            except:
                f2Slope = 0
            f2yInt = minClo - (f2Slope*minCloTemp)
            
            for temperature in finalAirTemps:
                finalCloValues.append(schiavonClo(temperature, maxClo, maxCloTemp,  minClo, minCloTemp, f1Slope, f1yInt, f2Slope, f2yInt))
        else: finalCloValues = []
        
        return finalCloValues
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return []



if _outdoorAirTemperature:
    cloValues = main()
    if cloValues == -1:
        cloValues = []
