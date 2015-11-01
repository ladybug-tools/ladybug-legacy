# Adaptive Comfort Calculator
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to calculate the adaptive comfort for a given set of input conditions.
This component will output a stream of 0's and 1's indicating whether certain conditions are comfortable given the prevailing mean monthly temperature that ocuppants tend to adapt themselves to.
This component will also output a series of interger numbers that indicate the following: -1 = The average monthly temperature is too extreme for the adaptive model. 0 = The input conditions are too cold for occupants. 1 = The input conditions are comfortable for occupants. 2 = The input conditions are too hot for occupants.
Lastly, this component outputs the percent of time comfortable, hot, cold and monthly extreme as well as a lit of numbers indicating the upper temperature of comfort and lower temperature of comfort.
_
The adaptive comfort model was created in response to the shortcomings of the PMV model that became apparent when it was applied to buildings without air conditioning.  Namely, the PMV model was over-estimating the discomfort of occupants in warm conditions of nautrally ventilated buildings.
Accordingly, the adaptive comfort model was built on the work of hundreds of field studies in which people in naturally ventilated buildings were asked asked about how comfortable they were.
Results showed that users tended to adapt themselves to the monthly mean temperature and would be comfortable in buildings so long as the building temperature remained around a value close to that monthly mean.  This situation held true so long as the monthly mean temperature remained above 10 C and below 33.5 C.
_
The comfort models that make this component possible were translated to python from a series of validated javascript comfort models coded at the Berkely Center for the Built Environment (CBE).  The Adaptive model used by both the CBE Tool and this component was originally published in ASHARAE 55.
Special thanks goes to the authors of the online CBE Thermal Comfort Tool who first coded the javascript: Hoyt Tyler, Schiavon Stefano, Piccioli Alberto, Moon Dustin, and Steinfeld Kyle. http://cbe.berkeley.edu/comforttool/
-
Provided by Ladybug 0.0.59
    
    Args:
        _dryBulbTemperature: A number representing the dry bulb temperature of the air in degrees Celcius.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        meanRadiantTemperature_: A number representing the mean radiant temperature of the surrounding surfaces in degrees Celcius.  If no value is plugged in here, this component will assume that the mean radiant temperature is equal to air temperature value above.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        _prevailingOutdoorTemp: A number representing the average monthly outdoor temperature in degrees Celcius.  This average monthly outdoor temperature is the temperature that occupants in naturally ventilated buildings tend to adapt themselves to. For this reason, this input can also accept the direct output of dryBulbTemperature from the Import EPW component if houlry values for the full year are connected for the other inputs of this component.
        windSpeed_: A number representing the wind speed of the air in meters per second.  If no value is plugged in here, this component will assume a very low wind speed of 0.3 m/s, characteristic of most naturally ventilated buildings.  This input can also accept a list of wind speeds representing conditions at different times or the direct output of windSpeed from of the Import EPW component.
        ------------------------------: ...
        comfortPar_: Optional comfort parameters from the "Ladybug_Adaptive Comfort Parameters" component.  Use this to select either the US or European comfort model, set the threshold of acceptibility for comfort or compute prevailing outdoor temperature by a monthly average or running mean.  These comfortPar can also be used to set a levelOfConditioning, which makes use of research outside of the official published standards that surveyed people in air conditioned buildings.
        analysisPeriod_: An optional analysis period from the Analysis Period component.  If no Analysis period is given and epw data from the ImportEPW component has been connected, the analysis will be run for the enitre year.
        _runIt: Set to "True" to run the component and calculate the adaptive comfort metrics.
    Returns:
        readMe!: ...
        ------------------------------: ...
        comfortableOrNot: A stream of 0's and 1's (or "False" and "True" values) indicating whether occupants are comfortable under the input conditions given the fact that these occupants tend to adapt themselves to the prevailing mean monthly temperature. 0 indicates that a person is not comfortable while 1 indicates that a person is comfortable.
        conditionOfPerson: A stream of interger values from -1 to +1 that correspond to each hour of the input data and indicate the following: -1 = The input conditions are too cold for occupants. 0 = The input conditions are comfortable for occupants. +1 = The input conditions are too hot for occupants.
        degreesFromTarget: A stream of temperature values in degrees Celcius indicating how far from the target temperature the conditions of the people are.  Positive values indicate conditions hotter than the target temperature while negative values indicate degrees below the target temperture.
        ------------------------------: ...
        targetTemperature: A stream of temperature values in degrees Celcius indicating the mean target temperture or neutral temperature that the most people will find comfortable.
        upperTemperatureBound: A stream of temperature values in degrees Celcius indicating the highest possible temperature in the comfort range for each hour of the input conditions.
        lowerTemperatureBound: A stream of temperature values in degrees Celcius indicating the lowest possible temperature in the comfort range for each hour of the input conditions.
        ------------------------------: ...
        percentOfTimeComfortable: The percent of the input data for which the occupants are comfortable.  Comfortable conditions are when the indoor temperature is within the comfort range determined by the prevailing outdoor temperature.
        percentHotCold: A list of 2 numerical values indicating the following: 0) The percent of the input data for which the occupants are too hot.  1) The percent of the input data for which the occupants are too cold.
        
"""
ghenv.Component.Name = "Ladybug_Adaptive Comfort Calculator"
ghenv.Component.NickName = 'AdaptiveComfortCalculator'
ghenv.Component.Message = 'VER 0.0.60\nOCT_30_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.60\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import Grasshopper.Kernel as gh
import math
import scriptcontext as sc


# Give people proper warning if they hook up data directly from the Import EPW component.
outdoorConditions = False
try:
    if _dryBulbTemperature[2] == "Dry Bulb Temperature":
        outdoorConditions = True
except: pass
try:
    if meanRadiantTemperature_[2] == "Dry Bulb Temperature" or meanRadiantTemperature_[2] == "Solar-Adjusted Mean Radiant Temperature":
        outdoorConditions = True
except: pass
try:
    if windSpeed_[2] == "Wind Speed":
        outdoorConditions = True
except: pass

if outdoorConditions == True:
    message1 = "Because the adaptive comfort model is derived from indoor comfort studies and you have hooked up outdoor data, the values out of this component only indicate how much\n" + \
    "the outdoor condtions should be changed in order to make indoor conditions comfortable. They do not idicate whether someone will actually be comfortable outdoors.\n" + \
    "If you are interested in whether the outdoors are actually comfortable, you should use the Ladybug Outdoor Comfort Calculator."
    print message1
    m = gh.GH_RuntimeMessageLevel.Remark
    ghenv.Component.AddRuntimeMessage(m, message1)

ghenv.Component.Attributes.Owner.OnPingDocument()


def checkTheInputs():
    #Define a value that will indicate whether someone has hooked up epw data.
    epwData = False
    epwStr = []
    epwPrevailTemp = False
    epwPrevailStr = []
    coldTimes = []
    
    #Check to see if there are any comfortPar connected and, if not, set the defaults to ASHRAE.
    checkData6 = True
    ASHRAEorEN = True
    comfClass = False
    avgMonthOrRunMean = True
    levelOfConditioning = 0
    if comfortPar_ != []:
        try:
            ASHRAEorEN = comfortPar_[0]
            comfClass = comfortPar_[1]
            avgMonthOrRunMean = comfortPar_[2]
            levelOfConditioning = comfortPar_[3]
        except:
            checkData6 = False
            warning = 'The connected comfortPar_ are not valid comfort parameters from the "Ladybug_Adaptive Comfort Parameters" component.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Define a function to duplicate data
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    #Check lenth of the _dryBulbTemperature list and evaluate the contents.
    checkData1 = False
    airTemp = []
    airMultVal = False
    if len(_dryBulbTemperature) != 0:
        try:
            if "Temperature" in _dryBulbTemperature[2]:
                airTemp = _dryBulbTemperature[7:]
                checkData1 = True
                epwData = True
                epwStr = _dryBulbTemperature[0:7]
        except: pass
        if checkData1 == False:
            for item in _dryBulbTemperature:
                try:
                    airTemp.append(float(item))
                    checkData1 = True
                except: checkData1 = False
        if len(airTemp) > 1: airMultVal = True
        if checkData1 == False:
            warning = '_dryBulbTemperature input does not contain valid temperature values in degrees Celcius.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'Connect a temperature in degrees celcius for _dryBulbTemperature'
    
    #Check lenth of the meanRadiantTemperature_ list and evaluate the contents.
    checkData2 = False
    radTemp = []
    radMultVal = False
    if len(meanRadiantTemperature_) != 0:
        try:
            if "Temperature" in meanRadiantTemperature_[2]:
                radTemp = meanRadiantTemperature_[7:]
                checkData2 = True
                epwData = True
                epwStr = meanRadiantTemperature_[0:7]
        except: pass
        if checkData2 == False:
            for item in meanRadiantTemperature_:
                try:
                    radTemp.append(float(item))
                    checkData2 = True
                except: checkData2 = False
        if len(radTemp) > 1: radMultVal = True
        if checkData2 == False:
            warning = 'meanRadiantTemperature_ input does not contain valid temperature values in degrees Celcius.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData2 = True
        radTemp = airTemp
        if len (radTemp) > 1: radMultVal = True
        print 'No value connected for meanRadiantTemperature_.  It will be assumed that the radiant temperature is the same as the air temperature.'
    
    #Check lenth of the _prevailingOutdoorTemp list and evaluate the contents.
    checkData3 = False
    prevailTemp = []
    prevailMultVal = False
    if len(_prevailingOutdoorTemp) != 0:
        try:
            if _prevailingOutdoorTemp[2] == 'Dry Bulb Temperature' and _prevailingOutdoorTemp[3] == 'C' and _prevailingOutdoorTemp[4] == 'Hourly' and _prevailingOutdoorTemp[5] == (1, 1, 1) and _prevailingOutdoorTemp[6] == (12, 31, 24):
                if avgMonthOrRunMean == True:
                    #Calculate the monthly average temperatures.
                    monthPrevailList = [float(sum(_prevailingOutdoorTemp[7:751])/744), float(sum(_prevailingOutdoorTemp[751:1423])/672), float(sum(_prevailingOutdoorTemp[1423:2167])/744), float(sum(_prevailingOutdoorTemp[2167:2887])/720), float(sum(_prevailingOutdoorTemp[2887:3631])/744), float(sum(_prevailingOutdoorTemp[3631:4351])/720), float(sum(_prevailingOutdoorTemp[4351:5095])/744), float(sum(_prevailingOutdoorTemp[5095:5839])/744), float(sum(_prevailingOutdoorTemp[5839:6559])/720), float(sum(_prevailingOutdoorTemp[6559:7303])/744), float(sum(_prevailingOutdoorTemp[7303:8023])/720), float(sum(_prevailingOutdoorTemp[8023:])/744)]
                    hoursInMonth = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
                    for monthCount, monthPrevailTemp in enumerate(monthPrevailList):
                        prevailTemp.extend(duplicateData([monthPrevailTemp], hoursInMonth[monthCount]))
                        if monthPrevailTemp < 10: coldTimes.append(monthCount+1)
                else:
                    #Calculate a running mean temperature.
                    alpha = 0.8
                    divisor = 1 + alpha + math.pow(alpha,2) + math.pow(alpha,3) + math.pow(alpha,4) + math.pow(alpha,5)
                    dividend = (sum(_prevailingOutdoorTemp[-24:-1] + [_prevailingOutdoorTemp[-1]])/24) + (alpha*(sum(_prevailingOutdoorTemp[-48:-24])/24)) + (math.pow(alpha,2)*(sum(_prevailingOutdoorTemp[-72:-48])/24)) + (math.pow(alpha,3)*(sum(_prevailingOutdoorTemp[-96:-72])/24)) + (math.pow(alpha,4)*(sum(_prevailingOutdoorTemp[-120:-96])/24)) + (math.pow(alpha,5)*(sum(_prevailingOutdoorTemp[-144:-120])/24))
                    startingTemp = dividend/divisor
                    if startingTemp < 10: coldTimes.append(0)
                    outdoorTemp = _prevailingOutdoorTemp[7:]
                    startingMean = sum(outdoorTemp[:24])/24
                    dailyRunMeans = [startingTemp]
                    dailyMeans = [startingMean]
                    prevailTemp.extend(duplicateData([startingTemp], 24))
                    startHour = 24
                    for count in range(364):
                        dailyMean = sum(outdoorTemp[startHour:startHour+24])/24
                        dailyRunMeanTemp = ((1-alpha)*dailyMeans[-1]) + alpha*dailyRunMeans[-1]
                        if dailyRunMeanTemp < 10: coldTimes.append(count+1)
                        prevailTemp.extend(duplicateData([dailyRunMeanTemp], 24))
                        dailyRunMeans.append(dailyRunMeanTemp)
                        dailyMeans.append(dailyMean)
                        startHour +=24
                checkData3 = True
                epwPrevailTemp = True
                epwPrevailStr = _prevailingOutdoorTemp[0:7]
        except: pass
        if checkData3 == False:
            checkData3 = True
            for item in _prevailingOutdoorTemp:
                try:
                    prevailTemp.append(float(item))
                except: checkData3 = False
        if len(prevailTemp) > 1: prevailMultVal = True
        if checkData3 == False:
            warning = '_prevailingOutdoorTemp input must either be the annual hourly dryBulbTemperature from the ImportEPW component, a list of temperature values that matches the length other inputs or a single temperature to be used for all cases.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'Connect a temperature in degrees celcius for _prevailingOutdoorTemp'
    
    #Check lenth of the windSpeed_ list and evaluate the contents.
    checkData4 = False
    windSpeed = []
    windMultVal = False
    nonPositive = True
    if len(windSpeed_) != 0:
        try:
            if windSpeed_[2] == 'Wind Speed':
                windSpeed = windSpeed_[7:]
                checkData4 = True
                epwData = True
                if epwStr == []:
                    epwStr = windSpeed_[0:7]
        except: pass
        if checkData4 == False:
            for item in windSpeed_:
                try:
                    if float(item) >= 0:
                        windSpeed.append(float(item))
                        checkData4 = True
                    else: nonPositive = False
                except: checkData4 = False
        if nonPositive == False: checkData4 = False
        if len(windSpeed) > 1: windMultVal = True
        if checkData4 == False:
            warning = 'windSpeed_ input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData4 = True
        windSpeed = [0.05]
        print 'No value connected for windSpeed_.  It will be assumed that the wind speed is a low 0.05 m/s.'
    
    #Finally, for those lists of length greater than 1, check to make sure that they are all the same length.
    checkData5 = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True:
        if airMultVal == True or radMultVal == True or prevailMultVal == True or windMultVal == True:
            listLenCheck = []
            secondListLenCheck = []
            if airMultVal == True:
                listLenCheck.append(len(airTemp))
                secondListLenCheck.append(len(airTemp))
            if radMultVal == True:
                listLenCheck.append(len(radTemp))
                secondListLenCheck.append(len(radTemp))
            if prevailMultVal == True: listLenCheck.append(len(prevailTemp))
            if windMultVal == True:
                listLenCheck.append(len(windSpeed))
                secondListLenCheck.append(len(windSpeed))
            
            if all(x == listLenCheck[0] for x in listLenCheck) == True:
                checkData5 = True
                calcLength = listLenCheck[0]
                
                if airMultVal == False: airTemp = duplicateData(airTemp, calcLength)
                if radMultVal == False: radTemp = duplicateData(radTemp, calcLength)
                if prevailMultVal == False: prevailTemp = duplicateData(prevailTemp, calcLength)
                if windMultVal == False: windSpeed = duplicateData(windSpeed, calcLength)
            elif all(x == secondListLenCheck[0] for x in secondListLenCheck) == True and epwPrevailTemp == True and epwData == True and epwPrevailStr[5] == (1,1,1) and epwPrevailStr[6] == (12,31,24):
                checkData5 = True
                calcLength = listLenCheck[0]
                
                if airMultVal == False: airTemp = duplicateData(airTemp, calcLength)
                if radMultVal == False: radTemp = duplicateData(radTemp, calcLength)
                if windMultVal == False: windSpeed = duplicateData(windSpeed, calcLength)
                HOYs, mon, days = lb_preparation.getHOYsBasedOnPeriod([epwStr[5], epwStr[6]], 1)
                newPrevailTemp = []
                for hour in HOYs:
                    newPrevailTemp.append(prevailTemp[hour-1])
                prevailTemp = newPrevailTemp
            else:
                calcLength = None
                warning = 'If you have put in lists with multiple values, the lengths of these lists must match across the parameters or you have a single value for a given parameter to be applied to all values in the list.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData5 = True
            calcLength = 1
    else:
        calcLength = 0
    
    #If all of the checkDatas have been good to go, let's give a final go ahead.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True:
        checkData = True
    else:
        checkData = False
    
    #Let's return everything we need.
    return checkData, epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed, ASHRAEorEN, comfClass, avgMonthOrRunMean, coldTimes, levelOfConditioning


def main(checkData, epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed, ASHRAEorEN, comfClass, avgMonthOrRunMean, coldTimes, levelOfConditioning, lb_preparation, lb_comfortModels):
    #Check if there is an analysisPeriod_ connected and, if not, run it for the whole year.
    individualCases = False
    daysForMonths = lb_preparation.numOfDays
    if calcLength == 8760 and len(analysisPeriod_)!=0 and epwData == True:
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod_, 1)
        runPeriod = analysisPeriod_
        calcLength = len(HOYS)
        dayNums = []
        for month in months:
            if days[0] == 1 and days[-1] == 31: dayNums.extend(range(daysForMonths[month-1], daysForMonths[month]))
            elif days[0] == 1 and days[-1] != 31: dayNums.extend(range(daysForMonths[month-1], daysForMonths[month-1]+days[-1]))
            elif days[0] != 1 and days[-1] == 31: dayNums.extend(range(daysForMonths[month-1]+days[0], daysForMonths[month]))
            else: dayNums.extend(range(daysForMonths[month-1]+days[0], daysForMonths[month-1]+days[-1]))
    elif len(analysisPeriod_)==0 and epwData == True:
        HOYS = range(calcLength)[1:] + [calcLength]
        runPeriod = [epwStr[5], epwStr[6]]
        months = [1,2,3,4,5,6,7,8,9,10,11,12]
        dayNums = range(365)
    else:
        HOYS = range(calcLength)[1:] + [calcLength]
        runPeriod = [(1,1,1), (12,31,24)]
        months = []
        days = []
        individualCases = True
    
    #Check to see if there are any times when the prevailing temperature is too cold and give a comment that we are using a non-standard model.
    monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if ASHRAEorEN == True: modelName = "ASHRAE 55"
    else: modelName = "EN-15251"
    if coldTimes != []:
        coldThere = False
        if avgMonthOrRunMean == True:
            coldMsg = "The following months were too cold for the official " + modelName + " standard and have used a correlation from recent research:"
            for month in months:
                if month in coldTimes:
                    coldThere = True
                    coldMsg += '\n'
                    coldMsg += monthNames[month-1]
            if coldThere == True:
                print coldMsg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, coldMsg)
        else:
            totalColdInPeriod = []
            for day in dayNums:
                if day in coldTimes: totalColdInPeriod.append(day)
            if totalColdInPeriod != []:
                coldMsg = "There were " + str(len(totalColdInPeriod)) + " days of the analysis period when the outdoor temperatures were too cold for the official " + modelName + " standard. \n A correlation from recent research has been used in these cases."
                print coldMsg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, coldMsg)
    elif individualCases:
        totalColdInPeriod = []
        for temp in prevailTemp:
            if temp < 10: totalColdInPeriod.append(temp)
        if totalColdInPeriod != []:
            coldMsg = "There were " + str(len(totalColdInPeriod)) + " cases when the prevailing outdoor temperatures were too cold for the official " + modelName + " standard. \n A correlation from recent research has been used in these cases."
            print coldMsg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, coldMsg)
    
    #If things are good, run it through the comfort model.
    comfortableOrNot = []
    extremeColdComfortableHot = []
    upperTemperatureBound = []
    lowerTemperatureBound = []
    targetTemperature = []
    degreesFromTarget = []
    percentOfTimeComfortable = None
    percentHotColdAndExtreme = []
    if checkData == True and epwData == True and 'for' not in epwStr[2]:
        targetTemperature.extend([epwStr[0], epwStr[1], 'Adaptive Target Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
        degreesFromTarget.extend([epwStr[0], epwStr[1], 'Degrees from Target Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
        comfortableOrNot.extend([epwStr[0], epwStr[1], 'Comfortable Or Not', 'Boolean', epwStr[4], runPeriod[0], runPeriod[1]])
        extremeColdComfortableHot.extend([epwStr[0], epwStr[1], 'Adaptive Comfort', '-1 = Cold, 0 = Comfortable, 1 = Hot', epwStr[4], runPeriod[0], runPeriod[1]])
        upperTemperatureBound.extend([epwStr[0], epwStr[1], 'Adaptive Upper Comfort Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
        lowerTemperatureBound.extend([epwStr[0], epwStr[1], 'Adaptive Lower Comfort Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
    elif checkData == True and epwData == True and 'for' in epwStr[2]:
        targetTemperature.extend([epwStr[0], epwStr[1], 'Adaptive Target Temperature' + ' for ' + epwStr[2].split('for ')[-1], 'C', epwStr[4], runPeriod[0], runPeriod[1]])
        degreesFromTarget.extend([epwStr[0], epwStr[1], 'Degrees from Target Temperature' + ' for ' + epwStr[2].split('for ')[-1], 'C', epwStr[4], runPeriod[0], runPeriod[1]])
        comfortableOrNot.extend([epwStr[0], epwStr[1], 'Comfortable Or Not' + ' for ' + epwStr[2].split('for ')[-1], 'Boolean', epwStr[4], runPeriod[0], runPeriod[1]])
        extremeColdComfortableHot.extend([epwStr[0], epwStr[1], 'Adaptive Comfort' + ' for ' + epwStr[2].split('for ')[-1], '-1 = Cold, 0 = Comfortable, 1 = Hot', epwStr[4], runPeriod[0], runPeriod[1]])
        upperTemperatureBound.extend([epwStr[0], epwStr[1], 'Adaptive Upper Comfort Temperature' + ' for ' + epwStr[2].split('for ')[-1], 'C', epwStr[4], runPeriod[0], runPeriod[1]])
        lowerTemperatureBound.extend([epwStr[0], epwStr[1], 'Adaptive Lower Comfort Temperature' + ' for ' + epwStr[2].split('for ')[-1], 'C', epwStr[4], runPeriod[0], runPeriod[1]])
    if checkData == True:
        try:
            comfOrNot = []
            extColdComfHot = []
            upperTemp = []
            lowerTemp = []
            comfortTemp = []
            degreesTarget = []
            for count in HOYS:
                # let the user cancel the process
                if gh.GH_Document.IsEscapeKeyDown(): assert False
                
                if ASHRAEorEN == True: comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(airTemp[count-1], radTemp[count-1], prevailTemp[count-1], windSpeed[count-1], comfClass, levelOfConditioning)
                else: comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortEN15251(airTemp[count-1], radTemp[count-1], prevailTemp[count-1], windSpeed[count-1], comfClass, levelOfConditioning)
                
                if comf == True:comfOrNot.append(1)
                else: comfOrNot.append(0)
                extColdComfHot.append(condition)
                upperTemp.append(upTemp)
                lowerTemp.append(lowTemp)
                comfortTemp.append(comfTemp)
                degreesTarget.append(distFromTarget)
            percentOfTimeComfortable = [((sum(comfOrNot))/calcLength)*100]
            extreme = []
            hot = []
            cold = []
            for item in extColdComfHot:
                if item == -1: cold.append(1.0)
                elif item == 1: hot.append(1.0)
                else: pass
            percentHot = ((sum(hot))/calcLength)*100
            percentCold = ((sum(cold))/calcLength)*100
            percentHotCold = [percentHot, percentCold]
            comfortableOrNot.extend(comfOrNot)
            extremeColdComfortableHot.extend(extColdComfHot)
            upperTemperatureBound.extend(upperTemp)
            lowerTemperatureBound.extend(lowerTemp)
            targetTemperature.extend(comfortTemp)
            degreesFromTarget.extend(degreesTarget)
        except:
            comfortableOrNot = []
            extremeColdComfortableHot = []
            upperTemperatureBound = []
            lowerTemperatureBound = []
            targetTemperature = []
            degreesFromTarget = []
            percentOfTimeComfortable = []
            percentHotCold = []
            print "The calculation has been terminated by the user!"
            e = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
    
    #Return all of the info.
    return comfortableOrNot, extremeColdComfortableHot, percentOfTimeComfortable, percentHotCold, upperTemperatureBound, lowerTemperatureBound, targetTemperature, degreesFromTarget



checkData = False
if sc.sticky.has_key('ladybug_release'):
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): pass
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
    
    #Check the inputs and organize the incoming data into streams that can be run throught the comfort model.
    checkData, epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed, ASHRAEorEN, comfClass, avgMonthOrRunMean, coldTimes, levelOfConditioning = checkTheInputs()
else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")


if _runIt == True and checkData == True:
    results = main(checkData, epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed, ASHRAEorEN, comfClass, avgMonthOrRunMean, coldTimes, levelOfConditioning, lb_preparation, lb_comfortModels)
    if results!=-1:
        comfortableOrNot, conditionOfPerson, percentOfTimeComfortable, \
        percentHotCold, upperTemperatureBound, lowerTemperatureBound, targetTemperature, degreesFromTarget = results



