# Adaptive Comfort Chart
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Provided by Ladybug 0.0.66
    
    Args:
        _dryBulbTemperature: A number representing the dry bulb temperature of the air in degrees Celcius.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the 'Read EP Result' or 'Import EPW' component.
        meanRadiantTemperature_: A number representing the mean radiant temperature of the surrounding surfaces in degrees Celcius.  If no value is plugged in here, this component will assume that the mean radiant temperature is equal to air temperature value above.  This input can also accept a list of temperatures representing conditions at different times or the direct output from the 'Read EP Result' or 'Import EPW' component.
        _outdoorTemperature: The direct output of dryBulbTemperature from the Import EPW component.  Alternatively, this can be a number representing the prevailing outdoor temperature in degrees Celcius. It can also be a list of prevailing outdoor temperatures that corresponds with the number of values connected above.  Note that, when putting in values without a header like this, the values are meant to be the PREVAILING temperature (not the actual hourly outdoor temperature).
        windSpeed_: A number representing the wind speed of the air in meters per second.  If no value is plugged in here, this component will assume a low wind speed of < 0.2 m/s, characteristic of most naturally ventilated buildings without fans.  This input can also accept several wind speeds to generate multiple comfort polygons.  Lastly, this component can accept the direct output of windSpeed from of the Import EPW component and, from this data, two comfort polygons will be drawn representing the maximum and minumu wind speed.
        ------------------------------: ...
        comfortPar_: Optional comfort parameters from the "Ladybug_Adaptive Comfort Parameters" component.  Use this to select either the US or European comfort model, set the threshold of acceptibility for comfort or compute prevailing outdoor temperature by a monthly average or running mean.  These comfortPar can also be used to set a levelOfConditioning, which makes use of research outside of the official published standards that surveyed people in air conditioned buildings.
        includeColdTime_: Set to "True" to have the component include the time period where the outdoor temperature is too cold for the official ASHRAE or European standard and set to "False" to exclude it.  When the outdoor temperatue is too cold for these standards, a correlation from recent research is used.  The default is set to "True" to include the cold period in the visualization and output.
        ------------------------------: ...
        analysisPeriod_: An optional analysis period from the Analysis Period component.  If no Analysis period is given and epw or energy simulation data has been connected, the analysis will be run for the enitre year.
        annualHourlyData_: An optional list of hourly data from the 'Import EPW' component, which will be used to create hourPointColors that correspond to the hours of the data (e.g. windSpeed).  You can connect up several different annualHourly data here.
        conditionalStatement_: This input allows users to remove data that does not fit specific conditions or criteria from the adaptive chart. The conditional statement input here should be a valid condition statement in Python, such as "a>25" or "b<80" (without quotation marks).
                              The current version of this component accepts "and" and "or" operators. To visualize the hourly data, only lowercase English letters should be used as variables, and each letter alphabetically corresponds to each of the lists (in their respective order): "a" always represents the 1st list plugged into annualHourlyData_, "b" always represents the 2nd list plugged into annualHourlyData_, "c" always represents the 3rd list plugged into annualHourlyData_, etc.
                              For example, if you want to plot the data for the time period when temperature is between 18C and 23C, and humidity is less than 80%, the conditional statement should be written as 18<a<23 and b<80 (without quotation marks).
        basePoint_: An optional base point that will be used to place the adaptive chart in the Rhino scene.  If no base point is provided, the base point will be the Rhino model origin.
        scale_: An optional number to change the scale of the adaptive chart in the Rhino scene.  By default, this value is set to 1.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
        _runIt: Set to "True" to run the component and generate an Adaptive comfort chart.
    Returns:
        readMe!: ...
        --------------------------: ...
        comfPercentOfTime: The percent of the input data for which the occupants are comfortable.  Comfortable conditions are when the indoor temperature is within the comfort range determined by the prevailing outdoor temperature.
        percentHotCold: A list of 2 numerical values indicating the following: 0) The percent of the input data for which the occupants are too hot.  1) The percent of the input data for which the occupants are too cold.
        comfortableOrNot: A stream of 0's and 1's (or "False" and "True" values) indicating whether occupants are comfortable under the input conditions given the fact that these occupants tend to adapt themselves to the prevailing mean monthly temperature. 0 indicates that a person is not comfortable while 1 indicates that a person is comfortable.
        conditionOfPerson: A stream of interger values from -1 to +1 that correspond to each hour of the input data and indicate the following: -1 = The input conditions are too cold for occupants. 0 = The input conditions are comfortable for occupants. +1 = The input conditions are too hot for occupants.
        degreesFromTarget: A stream of temperature values in degrees Celcius indicating how far from the target temperature the conditions of the people are.  Positive values indicate conditions hotter than the target temperature while negative values indicate degrees below the target temperture.
        prevailingTemp: A stream of temperature values in degrees Celcius indicating the prevailing outdoor temperature.  This is the temperture that determines the conditions occupants find comfortable and is either a monthly average temperature or a running mean of outdoor temperature.
        targetTemperature: A stream of temperature values in degrees Celcius indicating the mean target temperture (or neutral temperature) that the most people will find most comfortable.
        --------------------------: ...
        chartCurvesAndTxt: The chart curves and text labels of the adaptive chart.
        adaptiveChartMesh: A colored mesh showing the number of input hours happen in each part of the adaptive chart.
        legend: A colored legend showing the number of hours that correspond to each color.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the chart with the grasshopper "move" component.
        comfortPolygons: A brep representing the range of comfort for.
        --------------------------: ...
        chartHourPoints: Points representing each of the hours of input temperature and opTemperity ratio.  By default, this ouput is hidden and, to see it, you should connect it to a Grasshopper preview component.
        hourPointColors: Colors that correspond to the chartHourPoints above and can be hooked up to the "Swatch" input of a Grasshopper Preview component that has the hour points above connected as geometry.  By default, points are colored red if they lie inside comfort polygon and are colored blue if they do not meet such comfort criteria.  In the event that you have hooked up annualHourlyData_ this output will be a grafted list of colors.  The first list corresponds to the comfort conditions while the second list colors points based on the annualHourlyData.
        hourPointLegend: A legend that corresponds to the hour point colors above.  In the event that annualHourlyData_ is connected, this output will be a grafted list of legends that each correspond to the grafted lists of colors.
"""
ghenv.Component.Name = "Ladybug_Adaptive Comfort Chart"
ghenv.Component.NickName = 'AdaptiveChart'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.59\nJAN_24_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Grasshopper.Kernel as gh
import math
import scriptcontext as sc
import Rhino as rc
import System
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import copy

w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


def C2F(temper):
    newTemper = []
    for num in temper: newTemper.append(num*9/5 + 32)
    return newTemper

def F2C(temper):
    newTemper = []
    for num in temper: newTemper.append((num-32) * 5 / 9)
    return newTemper


def checkTheInputs():
    #Define a value that will indicate whether someone has hooked up epw data.
    epwData = False
    epwStr = []
    epwPrevailTemp = False
    epwPrevailStr = []
    coldTimes = []
    IPTrigger = False
    farenheitAirVals = []
    farenheitRadVals = []
    farenheitPrevailVals = []
    
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
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
    
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
                if epwStr[3] == 'F' or epwStr[3] == 'F':
                    IPTrigger = True
        except: pass
        if checkData1 == False:
            for item in _dryBulbTemperature:
                try:
                    airTemp.append(float(item))
                    checkData1 = True
                except:
                    if item == 'F' or item == 'F': IPTrigger = True
                    else: checkData1 = False
        if IPTrigger == True:
            farenheitAirVals = airTemp[:]
            airTemp = F2C(airTemp)
        if len(airTemp) > 1: airMultVal = True
        if checkData1 == False:
            warning = '_dryBulbTemperature input does not contain valid temperature values in degrees Celcius.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
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
                if epwStr[3] == 'F' or epwStr[3] == 'F' and IPTrigger == True:
                    farenheitRadVals = radTemp[:]
                    radTemp = F2C(radTemp)
                elif IPTrigger == False and epwStr[3] == 'C' or epwStr[3] == 'C': pass
                elif IPTrigger == True:
                    farenheitRadVals = C2F(radTemp)
                    print  "Radiant Temperature has been aoutmatically converted to Farenheit because your connected dry bulb temperature is in Farenheit."
                else:
                    radTemp = F2C(radTemp)
                    print  "Radiant Temperature has been aoutmatically converted to Celcius because your connected dry bulb temperature is in Celcius."
        except: pass
        if checkData2 == False:
            for item in meanRadiantTemperature_:
                try:
                    radTemp.append(float(item))
                    checkData2 = True
                except: checkData2 = False
            if checkData2 == True and IPTrigger == True:
                farenheitRadVals = radTemp[:]
                radTemp = F2C(radTemp)
                print  "Radiant Temperature has been assumed to be in Farenheit because your connected dry bulb temperature is in Farenheit."
        if len(radTemp) > 1: radMultVal = True
        if checkData2 == False:
            warning = 'meanRadiantTemperature_ input does not contain valid temperature values.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
    else:
        checkData2 = True
        radTemp = airTemp
        farenheitRadVals = farenheitAirVals
        if len (radTemp) > 1: radMultVal = True
        print 'No value connected for meanRadiantTemperature_.  It will be assumed that the radiant temperature is the same as the air temperature.'
    
    #Check lenth of the _outdoorTemperature list and evaluate the contents.
    checkData3 = False
    prevailTemp = []
    prevailMultVal = False
    if len(_outdoorTemperature) != 0:
        try:
            if 'Temperature' in _outdoorTemperature[2] and _outdoorTemperature[4] == 'Hourly' and _outdoorTemperature[5] == (1, 1, 1) and _outdoorTemperature[6] == (12, 31, 24):
                if avgMonthOrRunMean == True:
                    #Calculate the monthly average temperatures.
                    monthPrevailList = [float(sum(_outdoorTemperature[7:751])/744), float(sum(_outdoorTemperature[751:1423])/672), float(sum(_outdoorTemperature[1423:2167])/744), float(sum(_outdoorTemperature[2167:2887])/720), float(sum(_outdoorTemperature[2887:3631])/744), float(sum(_outdoorTemperature[3631:4351])/720), float(sum(_outdoorTemperature[4351:5095])/744), float(sum(_outdoorTemperature[5095:5839])/744), float(sum(_outdoorTemperature[5839:6559])/720), float(sum(_outdoorTemperature[6559:7303])/744), float(sum(_outdoorTemperature[7303:8023])/720), float(sum(_outdoorTemperature[8023:])/744)]
                    hoursInMonth = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
                    for monthCount, monthPrevailTemp in enumerate(monthPrevailList):
                        prevailTemp.extend(duplicateData([monthPrevailTemp], hoursInMonth[monthCount]))
                        if monthPrevailTemp < 10: coldTimes.append(monthCount+1)
                else:
                    #Calculate a running mean temperature.
                    alpha = 0.8
                    divisor = 1 + alpha + math.pow(alpha,2) + math.pow(alpha,3) + math.pow(alpha,4) + math.pow(alpha,5)
                    dividend = (sum(_outdoorTemperature[-24:-1] + [_outdoorTemperature[-1]])/24) + (alpha*(sum(_outdoorTemperature[-48:-24])/24)) + (math.pow(alpha,2)*(sum(_outdoorTemperature[-72:-48])/24)) + (math.pow(alpha,3)*(sum(_outdoorTemperature[-96:-72])/24)) + (math.pow(alpha,4)*(sum(_outdoorTemperature[-120:-96])/24)) + (math.pow(alpha,5)*(sum(_outdoorTemperature[-144:-120])/24))
                    startingTemp = dividend/divisor
                    if startingTemp < 10: coldTimes.append(0)
                    outdoorTemp = _outdoorTemperature[7:]
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
                epwData = True
                epwStr = _outdoorTemperature[0:7]
                if epwStr[3] == 'F' or epwStr[3] == 'F' and IPTrigger == True:
                    farenheitPrevailVals = prevailTemp[:]
                    prevailTemp = F2C(prevailTemp)
                elif IPTrigger == False and epwStr[3] == 'C' or epwStr[3] == 'C': pass
                elif IPTrigger == True:
                    farenheitPrevailVals = C2F(prevailTemp)
                    print  "Prevailing Outdoor Temperature has been aoutmatically converted to Farenheit because your connected dry bulb temperature is in Farenheit."
                else:
                    prevailTemp = F2C(prevailTemp)
                    print  "Prevailing Outdoor Temperature has been aoutmatically converted to Celcius because your connected dry bulb temperature is in Celcius."
        except: pass
        if checkData3 == False:
            checkData3 = True
            for item in _outdoorTemperature:
                try:
                    prevailTemp.append(float(item))
                except: checkData3 = False
            if checkData3 == True and IPTrigger == True:
                farenheitPrevailVals = prevailTemp[:]
                prevailTemp = F2C(prevailTemp)
                print  "Prevailing Outdoor Temperature has been assumed to be in Farenheit because your connected dry bulb temperature is in Farenheit."
        if len(prevailTemp) > 1: prevailMultVal = True
        if checkData3 == False:
            warning = '_outdoorTemperature input does not contain valid temperature values.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
    else:
        print 'Connect a temperature in degrees celcius for _outdoorTemperature'
    
    #Check lenth of the windSpeed_ list and evaluate the contents.
    checkData4 = False
    windSpeed = []
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
            checkData4 = True
            for item in windSpeed_:
                try:
                    if float(item) >= 0:
                        windSpeed.append(float(item))
                    else: nonPositive = False
                except: checkData4 = False
        if nonPositive == False: checkData4 = False
        if len(windSpeed) > 1: windMultVal = True
        if checkData4 == False:
            warning = 'windSpeed_ input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
    else:
        checkData4 = True
        windSpeed = [0.0]
        print 'No value connected for windSpeed_.  It will be assumed that the wind speed is a low and below 0.20 m/s.'
    
    #Finally, for those lists of length greater than 1, check to make sure that they are all the same length.
    checkData5 = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True:
        if airMultVal == True or radMultVal == True or prevailMultVal == True:
            listLenCheck = []
            if airMultVal == True: listLenCheck.append(len(airTemp))
            if radMultVal == True: listLenCheck.append(len(radTemp))
            if prevailMultVal == True: listLenCheck.append(len(prevailTemp))
            
            if all(x == listLenCheck[0] for x in listLenCheck) == True:
                checkData5 = True
                calcLength = listLenCheck[0]
                
                if airMultVal == False: airTemp = duplicateData(airTemp, calcLength)
                if radMultVal == False: radTemp = duplicateData(radTemp, calcLength)
                if prevailMultVal == False: prevailTemp = duplicateData(prevailTemp, calcLength)
                
            else:
                calcLength = None
                warning = 'If you have put in lists with multiple values, the lengths of these lists must match across the parameters or you have a single value for a given parameter to be applied to all values in the list.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
        else:
            checkData5 = True
            calcLength = 1
    else:
        calcLength = 0
    
    #Check the annualhourly data and conditional statement
    checkData6 = True
    annualHourlyData = annualHourlyData_
    if epwData == True and len(_dryBulbTemperature) >= 8760 and conditionalStatement_:
        titleStatement, patternList = checkConditionalStatement(annualHourlyData, conditionalStatement_)
        if titleStatement == -1 or patternList == -1:
            checkData6 = False
    else:
        titleStatement = None
        patternList = []
    
    #Set the default to automatically include cold times in the chart if thre are any.
    if includeColdTime_ == None: includeColdTimes = True
    else: includeColdTimes = includeColdTime_
    
    #If all of the checkDatas have been good to go, let's give a final go ahead.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True:
        checkData = True
    else:
        checkData = False
    
    #Let's return everything we need.
    return checkData, epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed, ASHRAEorEN, comfClass, avgMonthOrRunMean, coldTimes, levelOfConditioning, includeColdTimes, titleStatement, patternList, IPTrigger, farenheitAirVals, farenheitRadVals, farenheitPrevailVals


def outlineCurve(curve):
    try:
        offsetCrv = curve.Offset(rc.Geometry.Plane.WorldXY, 0.15, sc.doc.ModelAbsoluteTolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
        finalBrep = (rc.Geometry.Brep.CreatePlanarBreps([curve, offsetCrv])[0])
        if finalBrep.Edges.Count < 3:
            finalBrep = curve
    except:
        finalBrep = curve
        warning = "Creating an outline of one of the comfort or strategy curves failed.  Component will return a single polyline."
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    return finalBrep


def checkConditionalStatement(annualHourlyData, conditionalStatement):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        indexList, listInfo = lb_preparation.separateList(annualHourlyData, lb_preparation.strToBeFound)
        
        letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
        # remove 'and' and 'or' from conditional statements
        csCleaned = conditionalStatement.replace('and', '',20000)
        csCleaned = csCleaned.replace('or', '',20000)
        
        # find the number of the lists that have assigned conditional statements
        listNum = []
        for count, let in enumerate(letters):
            if csCleaned.find(let)!= -1: listNum.append(count)
        
        # check if all the conditions are actually applicable
        for num in listNum:
            if num>len(listInfo) - 1:
                warning = 'A conditional statement is assigned for list number ' + `num + 1` + '  which is not existed!\n' + \
                          'Please remove the letter "' + letters[num] + '" from the statements to solve this problem!\n' + \
                          'Number of lists are ' + `len(listInfo)` + '. Please fix this issue and try again.'
                          
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1, -1
        
        selList = [[]] * len(listInfo)
        for i in range(len(listInfo)):
            selList[i] = annualHourlyData[indexList[i]+7:indexList[i+1]]
            if listInfo[i][4]!='Hourly' or listInfo[i][5]!=(1,1,1) or  listInfo[i][6]!=(12,31,24) or len(selList[i])!=8760:
                warning = 'At least one of the input data lists is not a valis ladybug hourly data! Please fix this issue and try again!\n List number = '+ `i+1`
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1, -1
        
        # replace the right list in the conditional statement
        statement = conditionalStatement.split(' ')
        finalStatement = 'pattern = '
        titleStatement = '...                         ...                         ...\n' +\
                         'Conditional Selection Applied:\n'
        
        for statemntPart in statement:
            statementCopy = str.Copy(statemntPart)
            if statemntPart!='and' and statemntPart!='or':
                for num in listNum:
                    toBeReplacedWith = 'selList[this][HOY]'.replace('this', `num`)
                    titleToBeReplacedWith = listInfo[num][2]
                    statemntPart = statemntPart.replace(letters[num], toBeReplacedWith, 20000)
                    statementCopy = statementCopy.replace(letters[num], titleToBeReplacedWith, 20000)
                    if statementCopy.find(letters[num])!=-1: break
                    
                titleStatement = titleStatement + ' ' + statementCopy
            else:
                titleStatement = titleStatement + '\n' + statementCopy 
            finalStatement = finalStatement + ' ' + statemntPart
        print titleStatement
        
        # check for the pattern
        patternList = []
        try:
            for HOY in range(8760):
                exec(finalStatement)
                patternList.append(pattern)
        except Exception,e:
            warning = 'There is an error in the conditional statement:\n' + `e`
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1, -1
        
        return titleStatement, patternList


def drawAdaptChart(prevailTemp, windSpeed, legendFont, legendFontSize, legendBold, epwData, epwStr, ASHRAEorEN, comfClass, levelOfConditioning, includeColdTimes, IPTrigger, lb_visualization, lb_comfortModels):
    #Define lists to be filled.
    chartCrvAndText = []
    finalComfortPolygons = []
    allText = []
    allTextPt = []
    
    #Set a default text height if the user has not provided one.
    if legendFontSize == None:
        if IPTrigger == False: legendFontSize = 0.6
        else: legendFontSize = 0.8
    
    #Check to see if any of the prevailing outdoor temperatures are below 10 C.
    belowTen = False
    for number in prevailTemp:
        if number < 10: belowTen = True
    
    #Generate a list of temperatures that will be used to make the chart lines.
    if belowTen == False or includeColdTimes == False:
        if IPTrigger == False:
            tempNum = range(10, 40, 2)
            prevailTempNum = range(10, 33, 2)
            boundRect = rc.Geometry.Rectangle3d(rc.Geometry.Plane(rc.Geometry.Point3d(10, 10, 0), rc.Geometry.Vector3d.ZAxis), 23, 30)
        else:
            tempNum = range(50, 104, 2)
            prevailTempNum = range(50, 92, 2)
            boundRect = rc.Geometry.Rectangle3d(rc.Geometry.Plane(rc.Geometry.Point3d(50, 50, 0), rc.Geometry.Vector3d.ZAxis), 42, 54)
    else:
        if IPTrigger == False:
            tempNum = range(0, 40, 2)
            prevailTempNum = range(-20, 33, 2)
            boundRect = rc.Geometry.Rectangle3d(rc.Geometry.Plane(rc.Geometry.Point3d(-20, 0, 0), rc.Geometry.Vector3d.ZAxis), 53, 40)
        else:
            tempNum = range(32, 104, 2)
            prevailTempNum = range(-4, 92, 2)
            boundRect = rc.Geometry.Rectangle3d(rc.Geometry.Plane(rc.Geometry.Point3d(-4, 32, 0), rc.Geometry.Vector3d.ZAxis), 96, 72)
    boundRect = boundRect.ToPolyline()
    chartCrvAndText.append(boundRect)
    
    #Use the dry bulb temperatures to create coordinates for the operative temp lines.
    tempNumLines = []
    tempLabelBasePts = []
    tempText = []
    for count in tempNum:
        if belowTen == False or includeColdTimes == False:
            if IPTrigger == False:
                point1 = rc.Geometry.Point3d(10, count, 0)
                tempLabelBasePts.append(rc.Geometry.Point3d(8.5, count-0.25, 0))
            else:
                point1 = rc.Geometry.Point3d(50, count, 0)
                tempLabelBasePts.append(rc.Geometry.Point3d(47, count-0.25, 0))
        else:
            if IPTrigger == False:
                point1 = rc.Geometry.Point3d(-20, count, 0)
                tempLabelBasePts.append(rc.Geometry.Point3d(-21.5, count-0.25, 0))
            else:
                point1 = rc.Geometry.Point3d(-4, count, 0)
                tempLabelBasePts.append(rc.Geometry.Point3d(-6.5, count-0.25, 0))
        if IPTrigger == False: point2 = rc.Geometry.Point3d(33, count, 0)
        else: point2 = rc.Geometry.Point3d(92, count, 0)
        
        tempLine = rc.Geometry.LineCurve(point1, point2)
        tempNumLines.append(tempLine)
        tempText.append(str(count))
    if belowTen == False or includeColdTimes == False:
        if IPTrigger == False: tempLabelBasePts.append(rc.Geometry.Point3d(8.5, 40, 0))
        else: tempLabelBasePts.append(rc.Geometry.Point3d(47, 104, 0))
    else:
        if IPTrigger == False: tempLabelBasePts.append(rc.Geometry.Point3d(-21.5, 40, 0))
        else: tempLabelBasePts.append(rc.Geometry.Point3d(-6.5, 104, 0))
    if IPTrigger == False: tempText.append("40")
    else: tempText.append("104")
    
    #Use the dry bulb temperatures to create coordinates for the operative temp lines.
    prevailTempNumLines = []
    prevailLabelBasePts = []
    prevailText = []
    for count in prevailTempNum:
        if belowTen == False or includeColdTimes == False:
            if IPTrigger == False: point1 = rc.Geometry.Point3d(count, 10, 0)
            else: point1 = rc.Geometry.Point3d(count, 50, 0)
        else:
            if IPTrigger == False: point1 = rc.Geometry.Point3d(count, 0, 0)
            else: point1 = rc.Geometry.Point3d(count, 32, 0)
        if IPTrigger == False: point2 = rc.Geometry.Point3d(count, 40, 0)
        else: point2 = rc.Geometry.Point3d(count, 104, 0)
        
        tempLine = rc.Geometry.LineCurve(point1, point2)
        prevailTempNumLines.append(tempLine)
        
        prevailLabelBasePts.append(rc.Geometry.Point3d(point1.X-(legendFontSize*.75), point1.Y-(legendFontSize*2), 0))
        prevailText.append(str(count))
    
    for winSpd in windSpeed:
        comfortPolygons = []
        #Get the values to draw the adaptive comfort polygon.
        if ASHRAEorEN == True:
            if winSpd >= 0.6:
                opBases = [20, 26, 26]
                prevailOutBases = [10, 12, 33]
            else:
                opBases = [20, 20]
                prevailOutBases = [10, 33]
        else:
            if comfClass > 1:
                opBases = [26, 26, 26]
                prevailOutBases = [10, 15, 30]
            else:
                opBases = [20, 26, 26, 26]
                prevailOutBases = [10, 12.74, 15, 30]
        opTempBases = []
        opTempMax = []
        opTempMin = []
        
        for tempCount, startTemp in enumerate(prevailOutBases):
            if ASHRAEorEN == True: comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(opBases[tempCount], opBases[tempCount], startTemp, winSpd, comfClass, levelOfConditioning)
            else: comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortEN15251(opBases[tempCount], opBases[tempCount], startTemp, winSpd, comfClass, levelOfConditioning)
            
            opTempBases.append(comfTemp)
            opTempMax.append(upTemp)
            opTempMin.append(lowTemp)
        
        #If the chart is in IP, convert the values to Farenheit.
        if IPTrigger == True:
            prevailOutBases = C2F(prevailOutBases)
            opTempBases = C2F(opTempBases)
            opTempMax = C2F(opTempMax)
            opTempMin = C2F(opTempMin)
        
        #Draw the middle line of the comfort polygon.
        point1 = rc.Geometry.Point3d(prevailOutBases[0], opTempBases[0], 0)
        point2 = rc.Geometry.Point3d(prevailOutBases[-1], opTempBases[-1], 0)
        centerLine = rc.Geometry.LineCurve(point1, point2)
        comfortPolygons.append(centerLine)
        
        #Draw the comfort polygon.
        point1 = rc.Geometry.Point3d(prevailOutBases[0], opTempMin[0], 0)
        point2 = rc.Geometry.Point3d(prevailOutBases[0], opTempMax[0], 0)
        point3 = rc.Geometry.Point3d(prevailOutBases[-1], opTempMax[-1], 0)
        point4 = rc.Geometry.Point3d(prevailOutBases[-1], opTempMin[-1], 0)
        if ASHRAEorEN == True:
            if winSpd >= 0.6:
                point5 = rc.Geometry.Point3d(prevailOutBases[1], opTempMax[1], 0)
                point6 = rc.Geometry.Point3d(prevailOutBases[1], lb_comfortModels.comfAdaptiveComfortASH55(20, 20, 12, 0.0, comfClass, levelOfConditioning)[3], 0)
                if IPTrigger == True: point6 = rc.Geometry.Point3d(point6.X, C2F([point6.Y])[0], 0)
                polygon = rc.Geometry.PolylineCurve([point1, point2, point6, point5, point3, point4, point1])
            else: polygon = rc.Geometry.PolylineCurve([point1, point2, point3, point4, point1])
        else:
            point7 = rc.Geometry.Point3d(prevailOutBases[-2], opTempMin[-2], 0)
            if winSpd >= 0.2 and comfClass == 1:
                point5 = rc.Geometry.Point3d(prevailOutBases[1], opTempMax[1], 0)
                point6 = rc.Geometry.Point3d(prevailOutBases[1], lb_comfortModels.comfAdaptiveComfortEN15251(20, 20, 12.74, 0.0, comfClass, levelOfConditioning)[3], 0)
                if IPTrigger == True: point6 = rc.Geometry.Point3d(point6.X, C2F([point6.Y])[0], 0)
                polygon = rc.Geometry.PolylineCurve([point1, point2, point6, point5, point3, point4, point7, point1])
            else:
                polygon = rc.Geometry.PolylineCurve([point1, point2, point3, point4, point7, point1])
        finalComfBrep = outlineCurve(polygon)
        comfortPolygons.append(finalComfBrep)
        
        #If the temperatures are below 10C, draw the heated comfort polygon.
        if belowTen == True and includeColdTimes == True:
            coldPrevailTempVals = range(-20, 10, 2)
            coldPrevailTempVals.append(9.999999)
            coldNeutralTempPts = []
            coldUpTempPts = []
            coldLowTempPts = []
            
            for val in coldPrevailTempVals:
                if ASHRAEorEN == True: Tn, distFromTarget, TnLow, TnUp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(20, 20, val, winSpd, comfClass, levelOfConditioning)
                else: Tn, distFromTarget, TnLow, TnUp, comf, condition = lb_comfortModels.comfAdaptiveComfortEN15251(20, 20, val, winSpd, comfClass, levelOfConditioning)
                if IPTrigger == False:
                    coldNeutralTempPts.append(rc.Geometry.Point3d(val, Tn, 0))
                    coldUpTempPts.append(rc.Geometry.Point3d(val, TnUp, 0))
                    coldLowTempPts.append(rc.Geometry.Point3d(val, TnLow, 0))
                else:
                    coldNeutralTempPts.append(rc.Geometry.Point3d(C2F([val])[0], C2F([Tn])[0], 0))
                    coldUpTempPts.append(rc.Geometry.Point3d(C2F([val])[0], C2F([TnUp])[0], 0))
                    coldLowTempPts.append(rc.Geometry.Point3d(C2F([val])[0], C2F([TnLow])[0], 0))
            
            neurtalCold = rc.Geometry.Curve.CreateInterpolatedCurve(coldNeutralTempPts, 3)
            comfortPolygons.append(neurtalCold)
            
            upCold = rc.Geometry.Curve.CreateInterpolatedCurve(coldUpTempPts, 3)
            downCold = rc.Geometry.Curve.CreateInterpolatedCurve(coldLowTempPts, 3)
            lineRight = rc.Geometry.LineCurve(upCold.PointAtEnd, downCold.PointAtEnd)
            lineLeft = rc.Geometry.LineCurve(upCold.PointAtStart, downCold.PointAtStart)
            coldComfortPolygon = rc.Geometry.Curve.JoinCurves([upCold, lineRight, downCold, lineLeft], tol)[0]
            finalComfBrep = outlineCurve(coldComfortPolygon)
            comfortPolygons.append(finalComfBrep)
        
        #If we are using the European standard, be sure to draw a polygon for very hot times.
        if ASHRAEorEN == False:
            hotTempBases = []
            hotTempMax = []
            hotTempMin = []
            prevailHotBases = [30.00001, 33]
            for startTemp in prevailHotBases:
                comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortEN15251(26, 26, startTemp, winSpd, comfClass, levelOfConditioning)
                
                hotTempBases.append(comfTemp)
                hotTempMax.append(upTemp)
                hotTempMin.append(lowTemp)
            
            #If the chart is in IP, convert the values to Farenheit.
            if IPTrigger == True:
                prevailHotBases = C2F(prevailHotBases)
                hotTempBases = C2F(hotTempBases)
                hotTempMax = C2F(hotTempMax)
                hotTempMin = C2F(hotTempMin)
            
            #Draw the middle line of the comfort polygon.
            point1 = rc.Geometry.Point3d(prevailHotBases[0], hotTempBases[0], 0)
            point2 = rc.Geometry.Point3d(prevailHotBases[-1], hotTempBases[-1], 0)
            centerLine = rc.Geometry.LineCurve(point1, point2)
            comfortPolygons.append(centerLine)
            #Draw the comfort polygon.
            point1 = rc.Geometry.Point3d(prevailHotBases[0], hotTempMin[0], 0)
            point2 = rc.Geometry.Point3d(prevailHotBases[0], hotTempMax[0], 0)
            point3 = rc.Geometry.Point3d(prevailHotBases[-1], hotTempMax[-1], 0)
            point4 = rc.Geometry.Point3d(prevailHotBases[-1], hotTempMin[-1], 0)
            polygon = rc.Geometry.PolylineCurve([point1, point2, point3, point4, point1])
            finalHotBrep = outlineCurve(polygon)
            comfortPolygons.append(finalHotBrep)
        
        #Append the polygon to the whole list of polygons.
        finalComfortPolygons.append(comfortPolygons)
    
    
    # Make the temperature value text for the chart.
    tempLabels = []
    for count, text in enumerate(tempText):
        tempLabels.extend(lb_visualization.text2srf([text], [tempLabelBasePts[count]], legendFont, legendFontSize, legendBold)[0])
    allText.extend(tempText)
    allTextPt.extend(tempLabelBasePts)
    prevailLabels = []
    for count, text in enumerate(prevailText):
        tempLabels.extend(lb_visualization.text2srf([text], [prevailLabelBasePts[count]], legendFont, legendFontSize, legendBold)[0])
    allText.extend(prevailText)
    allTextPt.extend(prevailLabelBasePts)
    
    #Bump up the text size for Farenheit.
    if IPTrigger == True: legendFontSize = 1
    
    #Make axis labels for the chart.
    xAxisLabels = []
    if IPTrigger == False: xAxisTxt = ["Prevailing Outdoor Temperature (C)"]
    else: xAxisTxt = ["Prevailing Outdoor Temperature (F)"]
    if IPTrigger == False:
        if belowTen == False or includeColdTimes == False: xAxisPt = [rc.Geometry.Point3d(12, 10 -(5*legendFontSize), 0)]
        else: xAxisPt = [rc.Geometry.Point3d(-3, -(5*legendFontSize), 0)]
    else:
        if belowTen == False or includeColdTimes == False: xAxisPt = [rc.Geometry.Point3d(55, 50 -(5*legendFontSize), 0)]
        else: xAxisPt = [rc.Geometry.Point3d(30, 32-(5*legendFontSize), 0)]
    tempLabels.extend(lb_visualization.text2srf(xAxisTxt, xAxisPt, legendFont, legendFontSize*1.25, legendBold)[0])
    allText.extend(xAxisTxt)
    allTextPt.extend(xAxisPt)
    
    yAxisLabels = []
    if IPTrigger == False: yAxisTxt = ["Indoor Operative Temperature (C)"]
    else: yAxisTxt = ["Indoor Operative Temperature (F)"]
    if IPTrigger == False:
        if belowTen == False or includeColdTimes == False:  yAxisPt = [rc.Geometry.Point3d(7, 17, 0)]
        else: yAxisPt = [rc.Geometry.Point3d(-23, 11, 0)]
    else:
        if belowTen == False or includeColdTimes == False:  yAxisPt = [rc.Geometry.Point3d(45, 67, 0)]
        else: yAxisPt = [rc.Geometry.Point3d(-8, 56, 0)]
    yAxisLabels.extend(lb_visualization.text2srf(yAxisTxt, yAxisPt, legendFont, legendFontSize*1.25, legendBold)[0])
    rotateTransf = rc.Geometry.Transform.Rotation(1.57079633, yAxisPt[0])
    for geo in yAxisLabels:
        geo.Transform(rotateTransf)
    tempLabels.extend(yAxisLabels)
    allText.extend(yAxisTxt)
    allTextPt.extend(yAxisPt)
    
    #Make the chart title.
    def getDateStr(start, end):
        stMonth, stDay, stHour, endMonth, endDay, endHour = lb_visualization.readRunPeriod((start, end), False)
        period = `stDay`+ ' ' + lb_visualization.monthList[stMonth-1] + ' ' + `stHour` + ':00' + \
                 " - " + `endDay`+ ' ' + lb_visualization.monthList[endMonth-1] + ' ' + `endHour` + ':00'
        return period
    
    titleLabels = []
    if epwData == True:
        titleTxt = ["Adaptive Chart", epwStr[1]]
        if analysisPeriod_ == []:
            titleTxt.append(getDateStr(epwStr[5], epwStr[6]))
        else:
            titleTxt.append(getDateStr(analysisPeriod_[0], analysisPeriod_[1]))
    else: titleTxt = ["Adaptive Chart", "Unkown Location", "Unknown Time Period"]
    if IPTrigger == False:
        if belowTen == False or includeColdTimes == False: titlePt = [rc.Geometry.Point3d(10, 4, 0), rc.Geometry.Point3d(10, (4)-(legendFontSize*2.5), 0),  rc.Geometry.Point3d(10, (4)-(legendFontSize*5), 0)]
        else: titlePt = [rc.Geometry.Point3d(-20, -6, 0), rc.Geometry.Point3d(-20, (-6)-(legendFontSize*2.5), 0),  rc.Geometry.Point3d(-20, (-6)-(legendFontSize*5), 0)]
    else:
        if belowTen == False or includeColdTimes == False: titlePt = [rc.Geometry.Point3d(45, 42, 0), rc.Geometry.Point3d(45, (42)-(legendFontSize*2.5), 0),  rc.Geometry.Point3d(45, (42)-(legendFontSize*5), 0)]
        else: titlePt = [rc.Geometry.Point3d(-7, 22, 0), rc.Geometry.Point3d(-7, (22)-(legendFontSize*2.5), 0),  rc.Geometry.Point3d(-7, (22)-(legendFontSize*5), 0)]
    for count, text in enumerate(titleTxt):
        titleLabels.extend(lb_visualization.text2srf([text], [titlePt[count]], legendFont, legendFontSize*1.5, legendBold)[0])
    allText.extend(titleTxt)
    allTextPt.extend(titlePt)
    
    #Bring all text and curves together in one list.
    for item in tempNumLines:
        chartCrvAndText.append(item)
    for item in prevailTempNumLines:
        chartCrvAndText.append(item)
    allCrvs = copy.copy(chartCrvAndText)
    for polylist in finalComfortPolygons:
        allCrvs.extend(polylist)
    for item in tempLabels:
        chartCrvAndText.append(item)
    for item in titleLabels:
        chartCrvAndText.append(item)
    
    if IPTrigger == False: bound = tempNumLines[0:8]
    else: bound = tempNumLines[0:15]
    
    return chartCrvAndText, finalComfortPolygons, belowTen, bound, allCrvs, allText, allTextPt


def colorMesh(airTemp, radTemp, prevailTemp, lb_preparation, lb_comfortModels, lb_visualization, lowB, highB, customColors, belowTen, includeColdTimes, IPTrigger, farenheitAirVals, farenheitRadVals, farenheitPrevailVals):
    # Make the full chart mesh
    #Generate a list of temperatures that will be used to make the mesh.
    if belowTen == False or includeColdTimes == False:
        if IPTrigger == False:
            tempNumMesh = range(10, 41, 1)
            prevailNumMesh = range(10, 34, 1)
        else:
            tempNumMesh = range(50, 106, 2)
            prevailNumMesh = range(50, 94, 2)
    else:
        if IPTrigger == False:
            tempNumMesh = range(0, 41, 1)
            prevailNumMesh = range(-20, 34, 1)
        else:
            tempNumMesh = range(32, 106, 2)
            prevailNumMesh = range(-4, 94, 2)
    
    #Make a matrix
    tempNumMeshFinal =[]
    for temp in tempNumMesh:
        tempNumMeshInit = []
        for item in prevailNumMesh:
            tempNumMeshInit.append(temp)
        tempNumMeshFinal.append(tempNumMeshInit)
    
    #Make the mesh faces.
    chartMesh = rc.Geometry.Mesh()
    meshFacePts = []
    
    for listCount, list in enumerate(tempNumMeshFinal[:-1]):
        for tempCount, temp in enumerate(prevailNumMesh[:-1]):
            facePt1 = rc.Geometry.Point3d(temp, list[tempCount], 0)
            facePt2 = rc.Geometry.Point3d(temp, tempNumMeshFinal[listCount+1][tempCount], 0)
            facePt3 = rc.Geometry.Point3d(prevailNumMesh[tempCount+1], tempNumMeshFinal[listCount+1][tempCount+1], 0)
            facePt4 = rc.Geometry.Point3d(prevailNumMesh[tempCount+1], list[tempCount+1], 0)
            
            meshFacePts.append([facePt1, facePt2, facePt3, facePt4])
    
    for list in  meshFacePts:
        mesh = rc.Geometry.Mesh()
        for point in list:
            mesh.Vertices.Add(point)
        
        mesh.Faces.AddFace(0, 1, 2, 3)
        chartMesh.Append(mesh)
    uncoloredMesh = chartMesh
    
    #Calculate the opTemper for each of the hours of the year and use this to make points for the chart.
    hourPts = []
    operativeTemps = []
    if IPTrigger == False:
        for count, temp in enumerate(prevailTemp):
            operTemp = (airTemp[count]+radTemp[count])/2
            hourPts.append(rc.Geometry.Point3d(temp, operTemp, 0))
            operativeTemps.append(operTemp)
    else:
        for count, temp in enumerate(farenheitPrevailVals):
            operTemp = (farenheitAirVals[count]+farenheitRadVals[count])/2
            hourPts.append(rc.Geometry.Point3d(temp, operTemp, 0))
            operativeTemps.append(operTemp)
    
    #Make a list to hold values for all of the mesh faces.
    meshFrequency = []
    for count, value in enumerate(tempNumMesh[:-1]):
        meshFrequency.append([])
        for face in prevailNumMesh[:-1]:
            meshFrequency[count].append([])
    
    #Bin the input prevail and temperatures into categories that correspond to the mesh faces.
    def getTempIndex(hour):
        if belowTen == False or includeColdTimes == False:
            if prevailTemp[hour] > 10 and prevailTemp[hour] < 33.0:
                index  = int(round(prevailTemp[hour]-10.5))
            elif prevailTemp[hour] > 33.0: index = -1
            else: index = -2
        else:
            if prevailTemp[hour] > -20 and prevailTemp[hour] < 33.0:
                index  = int(round(prevailTemp[hour]+19.5))
            elif prevailTemp[hour] > 33.0: index = -1
            else: index = -2
        return index
    
    def getTempIndexFaren(hour):
        if belowTen == False or includeColdTimes == False:
            if farenheitPrevailVals[hour] > 50 and farenheitPrevailVals[hour] < 92:
                index  = int(round((farenheitPrevailVals[hour]-51)/2))
            elif farenheitPrevailVals[hour] > 92: index = -1
            else: index = -2
        else:
            if farenheitPrevailVals[hour] > -4 and farenheitPrevailVals[hour] < 92:
                index  = int(round((farenheitPrevailVals[hour]+3)/2))
            elif farenheitPrevailVals[hour] > 92: index = -1
            else: index = -2
        return index
    
    
    #Make a list to keep track of how many values are too hot for the chart.
    tooHotVals = []
    tooColdVals = []
    
    if IPTrigger == False:
        for hour, opTemper in enumerate(operativeTemps):
            tempIndex = getTempIndex(hour)
            if tempIndex != -1 and tempIndex != -2:
                if belowTen == False or includeColdTimes == False:
                    if opTemper < 10: pass
                    elif opTemper < 11: meshFrequency[0][tempIndex].append(1)
                    elif opTemper < 12: meshFrequency[1][tempIndex].append(1)
                    elif opTemper < 13:meshFrequency[2][tempIndex].append(1)
                    elif opTemper < 14:meshFrequency[3][tempIndex].append(1)
                    elif opTemper < 15:meshFrequency[4][tempIndex].append(1)
                    elif opTemper < 16:meshFrequency[5][tempIndex].append(1)
                    elif opTemper < 17:meshFrequency[6][tempIndex].append(1)
                    elif opTemper < 18:meshFrequency[7][tempIndex].append(1)
                    elif opTemper < 19:meshFrequency[8][tempIndex].append(1)
                    elif opTemper < 20:meshFrequency[9][tempIndex].append(1)
                    elif opTemper < 21:meshFrequency[10][tempIndex].append(1)
                    elif opTemper < 22:meshFrequency[11][tempIndex].append(1)
                    elif opTemper < 23:meshFrequency[12][tempIndex].append(1)
                    elif opTemper < 24:meshFrequency[13][tempIndex].append(1)
                    elif opTemper < 25:meshFrequency[14][tempIndex].append(1)
                    elif opTemper < 26:meshFrequency[15][tempIndex].append(1)
                    elif opTemper < 27:meshFrequency[16][tempIndex].append(1)
                    elif opTemper < 28:meshFrequency[17][tempIndex].append(1)
                    elif opTemper < 29:meshFrequency[18][tempIndex].append(1)
                    elif opTemper < 30:meshFrequency[19][tempIndex].append(1)
                    elif opTemper < 31:meshFrequency[20][tempIndex].append(1)
                    elif opTemper < 32:meshFrequency[21][tempIndex].append(1)
                    elif opTemper < 33:meshFrequency[22][tempIndex].append(1)
                    elif opTemper < 34:meshFrequency[23][tempIndex].append(1)
                    elif opTemper < 35:meshFrequency[24][tempIndex].append(1)
                    elif opTemper < 36:meshFrequency[25][tempIndex].append(1)
                    elif opTemper < 37:meshFrequency[26][tempIndex].append(1)
                    elif opTemper < 38:meshFrequency[27][tempIndex].append(1)
                    elif opTemper < 39:meshFrequency[28][tempIndex].append(1)
                    else: meshFrequency[29][tempIndex].append(1)
                else:
                    if opTemper < 0: pass
                    elif opTemper < 1: meshFrequency[0][tempIndex].append(1)
                    elif opTemper < 2: meshFrequency[1][tempIndex].append(1)
                    elif opTemper < 3:meshFrequency[2][tempIndex].append(1)
                    elif opTemper < 4:meshFrequency[3][tempIndex].append(1)
                    elif opTemper < 5:meshFrequency[4][tempIndex].append(1)
                    elif opTemper < 6:meshFrequency[5][tempIndex].append(1)
                    elif opTemper < 7:meshFrequency[6][tempIndex].append(1)
                    elif opTemper < 8:meshFrequency[7][tempIndex].append(1)
                    elif opTemper < 9:meshFrequency[8][tempIndex].append(1)
                    elif opTemper < 10:meshFrequency[9][tempIndex].append(1)
                    elif opTemper < 11:meshFrequency[10][tempIndex].append(1)
                    elif opTemper < 12:meshFrequency[11][tempIndex].append(1)
                    elif opTemper < 13:meshFrequency[12][tempIndex].append(1)
                    elif opTemper < 14:meshFrequency[13][tempIndex].append(1)
                    elif opTemper < 15:meshFrequency[14][tempIndex].append(1)
                    elif opTemper < 16:meshFrequency[15][tempIndex].append(1)
                    elif opTemper < 17:meshFrequency[16][tempIndex].append(1)
                    elif opTemper < 18:meshFrequency[17][tempIndex].append(1)
                    elif opTemper < 19:meshFrequency[18][tempIndex].append(1)
                    elif opTemper < 20:meshFrequency[19][tempIndex].append(1)
                    elif opTemper < 21:meshFrequency[20][tempIndex].append(1)
                    elif opTemper < 22:meshFrequency[21][tempIndex].append(1)
                    elif opTemper < 23:meshFrequency[22][tempIndex].append(1)
                    elif opTemper < 24:meshFrequency[23][tempIndex].append(1)
                    elif opTemper < 25:meshFrequency[24][tempIndex].append(1)
                    elif opTemper < 26:meshFrequency[25][tempIndex].append(1)
                    elif opTemper < 27:meshFrequency[26][tempIndex].append(1)
                    elif opTemper < 28:meshFrequency[27][tempIndex].append(1)
                    elif opTemper < 29:meshFrequency[28][tempIndex].append(1)
                    elif opTemper < 30:meshFrequency[29][tempIndex].append(1)
                    elif opTemper < 31:meshFrequency[30][tempIndex].append(1)
                    elif opTemper < 32:meshFrequency[31][tempIndex].append(1)
                    elif opTemper < 33:meshFrequency[32][tempIndex].append(1)
                    elif opTemper < 34:meshFrequency[33][tempIndex].append(1)
                    elif opTemper < 35:meshFrequency[34][tempIndex].append(1)
                    elif opTemper < 36:meshFrequency[35][tempIndex].append(1)
                    elif opTemper < 37:meshFrequency[36][tempIndex].append(1)
                    elif opTemper < 38:meshFrequency[37][tempIndex].append(1)
                    elif opTemper < 39:meshFrequency[38][tempIndex].append(1)
                    else: meshFrequency[39][tempIndex].append(1)
            elif tempIndex == -1: tooHotVals.append(1)
            else: tooColdVals.append(1)
    else:
        for hour, opTemper in enumerate(operativeTemps):
            tempIndex = getTempIndexFaren(hour)
            if tempIndex != -1 and tempIndex != -2:
                if belowTen == False or includeColdTimes == False:
                    if opTemper < 50: pass
                    elif opTemper < 52: meshFrequency[0][tempIndex].append(1)
                    elif opTemper < 54: meshFrequency[1][tempIndex].append(1)
                    elif opTemper < 56:meshFrequency[2][tempIndex].append(1)
                    elif opTemper < 58:meshFrequency[3][tempIndex].append(1)
                    elif opTemper < 60:meshFrequency[4][tempIndex].append(1)
                    elif opTemper < 62:meshFrequency[5][tempIndex].append(1)
                    elif opTemper < 64:meshFrequency[6][tempIndex].append(1)
                    elif opTemper < 66:meshFrequency[7][tempIndex].append(1)
                    elif opTemper < 68:meshFrequency[8][tempIndex].append(1)
                    elif opTemper < 70:meshFrequency[9][tempIndex].append(1)
                    elif opTemper < 72:meshFrequency[10][tempIndex].append(1)
                    elif opTemper < 74:meshFrequency[11][tempIndex].append(1)
                    elif opTemper < 76:meshFrequency[12][tempIndex].append(1)
                    elif opTemper < 78:meshFrequency[13][tempIndex].append(1)
                    elif opTemper < 80:meshFrequency[14][tempIndex].append(1)
                    elif opTemper < 82:meshFrequency[15][tempIndex].append(1)
                    elif opTemper < 84:meshFrequency[16][tempIndex].append(1)
                    elif opTemper < 86:meshFrequency[17][tempIndex].append(1)
                    elif opTemper < 88:meshFrequency[18][tempIndex].append(1)
                    elif opTemper < 90:meshFrequency[19][tempIndex].append(1)
                    elif opTemper < 92:meshFrequency[20][tempIndex].append(1)
                    elif opTemper < 94:meshFrequency[21][tempIndex].append(1)
                    elif opTemper < 96:meshFrequency[22][tempIndex].append(1)
                    elif opTemper < 98:meshFrequency[23][tempIndex].append(1)
                    elif opTemper < 100:meshFrequency[24][tempIndex].append(1)
                    elif opTemper < 102:meshFrequency[25][tempIndex].append(1)
                    else: meshFrequency[26][tempIndex].append(1)
                else:
                    if opTemper < 32: pass
                    elif opTemper < 34: meshFrequency[0][tempIndex].append(1)
                    elif opTemper < 36: meshFrequency[1][tempIndex].append(1)
                    elif opTemper < 38:meshFrequency[2][tempIndex].append(1)
                    elif opTemper < 40:meshFrequency[3][tempIndex].append(1)
                    elif opTemper < 42:meshFrequency[4][tempIndex].append(1)
                    elif opTemper < 44:meshFrequency[5][tempIndex].append(1)
                    elif opTemper < 46:meshFrequency[6][tempIndex].append(1)
                    elif opTemper < 48:meshFrequency[7][tempIndex].append(1)
                    elif opTemper < 50:meshFrequency[8][tempIndex].append(1)
                    elif opTemper < 52:meshFrequency[9][tempIndex].append(1)
                    elif opTemper < 54:meshFrequency[10][tempIndex].append(1)
                    elif opTemper < 56:meshFrequency[11][tempIndex].append(1)
                    elif opTemper < 58:meshFrequency[12][tempIndex].append(1)
                    elif opTemper < 60:meshFrequency[13][tempIndex].append(1)
                    elif opTemper < 62:meshFrequency[14][tempIndex].append(1)
                    elif opTemper < 64:meshFrequency[15][tempIndex].append(1)
                    elif opTemper < 66:meshFrequency[16][tempIndex].append(1)
                    elif opTemper < 68:meshFrequency[17][tempIndex].append(1)
                    elif opTemper < 70:meshFrequency[18][tempIndex].append(1)
                    elif opTemper < 72:meshFrequency[19][tempIndex].append(1)
                    elif opTemper < 74:meshFrequency[20][tempIndex].append(1)
                    elif opTemper < 76:meshFrequency[21][tempIndex].append(1)
                    elif opTemper < 78:meshFrequency[22][tempIndex].append(1)
                    elif opTemper < 80:meshFrequency[23][tempIndex].append(1)
                    elif opTemper < 82:meshFrequency[24][tempIndex].append(1)
                    elif opTemper < 84:meshFrequency[25][tempIndex].append(1)
                    elif opTemper < 86:meshFrequency[26][tempIndex].append(1)
                    elif opTemper < 88:meshFrequency[27][tempIndex].append(1)
                    elif opTemper < 90:meshFrequency[28][tempIndex].append(1)
                    elif opTemper < 92:meshFrequency[29][tempIndex].append(1)
                    elif opTemper < 94:meshFrequency[30][tempIndex].append(1)
                    elif opTemper < 96:meshFrequency[31][tempIndex].append(1)
                    elif opTemper < 98:meshFrequency[32][tempIndex].append(1)
                    elif opTemper < 100:meshFrequency[33][tempIndex].append(1)
                    elif opTemper < 102:meshFrequency[34][tempIndex].append(1)
                    else: meshFrequency[35][tempIndex].append(1)
            elif tempIndex == -1: tooHotVals.append(1)
            else: tooColdVals.append(1)
    
    
    #Give a remark if there are values that are not being displayed on the chart.
    if tooHotVals != []:
        comment = "There were " + str(len(tooHotVals)) + " cases where the prevaling outdoor temperature was so hot that it could not fit on the chart. \nThese values are still taken into account in the non-visual outputs."
        print comment
    if tooColdVals != []:
        comment = "There were " + str(len(tooColdVals)) + " cases where the prevaling outdoor temperature was so cold that it could not fit on the chart. \nThese values are still taken into account in the non-visual outputs."
        print comment
    
    #Sum all of the lists together to get the frequency.
    finalMeshFrequency = []
    for opTemperlist in meshFrequency:
        for prevailTemplist in opTemperlist:
            finalMeshFrequency.append(sum(prevailTemplist))
    
    #Get a list of colors
    colors = lb_visualization.gradientColor(finalMeshFrequency, lowB, highB, customColors)
    
    # color the mesh faces.
    uncoloredMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Gray)
    
    for srfNum in range (uncoloredMesh.Faces.Count):
        uncoloredMesh.VertexColors[4 * srfNum + 0] = colors[srfNum]
        uncoloredMesh.VertexColors[4 * srfNum + 1] = colors[srfNum]
        uncoloredMesh.VertexColors[4 * srfNum + 3] = colors[srfNum]
        uncoloredMesh.VertexColors[4 * srfNum + 2] = colors[srfNum]
    
    # Remove the mesh faces that do not have any hour associated with them.
    cullFaceIndices = []
    for count, freq in enumerate(finalMeshFrequency):
        if freq == 0:
            cullFaceIndices.append(count)
    uncoloredMesh.Faces.DeleteFaces(cullFaceIndices)
    
    #Flip the mesh to be sure that it always displays correctly.
    uncoloredMesh.Flip(True, True, True)
    
    
    #Return everything that's useful.
    return hourPts, uncoloredMesh, finalMeshFrequency


def getPointColors(totalComfOrNot, annualHourlyDataSplit, annualDataStr, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan, lb_visualization):
    #Define the lists.
    pointColors = []
    colorLegends = []
    
    #Get the colors for comfort.
    if str(totalComfOrNot[0]) == "key:location/dataType/units/frequency/startsAt/endsAt":
        totalComfOrNot = totalComfOrNot[7:]
    pointColors.append(lb_visualization.gradientColor(totalComfOrNot, 0, 1, customColors))
    
    #Get the colors for annualHourly Data.
    for list in annualHourlyDataSplit:
        if len(list) != 0:
            pointColors.append(lb_visualization.gradientColor(list, "min", "max", customColors))
    
    try:
        #Generate a legend for comfort.
        legend = []
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(totalComfOrNot, 0, 1, 2, "Comfort", lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
        legendColors = lb_visualization.gradientColor(legendText[:-1], 0, 1, customColors)
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
        legend.append(legendSrfs)
        for list in legendTextCrv:
            for item in list:
                legend.append(item)
        colorLegends.append(legend)
        
        #Generate legends for annualHourly Data.
        for listCount, list in enumerate(annualHourlyDataSplit):
            if len(list) != 0:
                legend = []
                legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(list, "min", "max", numSeg, annualDataStr[listCount][3], lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
                legendColors = lb_visualization.gradientColor(legendText[:-1], "min", "max", customColors)
                legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
                legend.append(legendSrfs)
                for list in legendTextCrv:
                    for item in list:
                        legend.append(item)
                colorLegends.append(legend)
        
        return pointColors, colorLegends
    except:
        return pointColors, []


def main(epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed, ASHRAEorEN, comfClass, avgMonthOrRunMean, coldTimes, levelOfConditioning, includeColdTimes, titleStatement, patternList, IPTrigger, farenheitAirVals, farenheitRadVals, farenheitPrevailVals, lb_preparation, lb_comfortModels, lb_visualization):
    #Create lists to be filled.
    comfortableOrNotInit = []
    conditionOfPersonInit = []
    degreesFromTargetInit = []
    prevailTempInit = []
    targetTempInit = []
    comfPercentOfTimeInit = []
    percentHotColdInit = []
    legend = []
    legendBasePt = None
    
    
    # Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar_, False)
    
    #If annual data is connected and there is an anlysis period or conditional statement, select out the right data.
    #If there is annual hourly data, split it up.
    if annualHourlyData_ != []:
        def chunks(l, n):
            finalList = []
            for i in range(0, len(l), n):
                finalList.append(l[i:i+n])
            return finalList
        annualHourlyDataSplit = chunks(annualHourlyData_, 8767)
    else: annualHourlyDataSplit = [[]]
    annualDataStr = []
    if annualHourlyDataSplit != [[]]:
        for list in annualHourlyDataSplit:
            annualDataStr.append(list[:7])
    
    # If an analysis period is selected, use that to select out the data.
    if analysisPeriod_ != [] and epwData == True and calcLength == 8760:
        airTemp = lb_preparation.selectHourlyData(airTemp, analysisPeriod_)[7:]
        radTemp = lb_preparation.selectHourlyData(radTemp, analysisPeriod_)[7:]
        prevailTemp = lb_preparation.selectHourlyData(prevailTemp, analysisPeriod_)[7:]
        if len(windSpeed) == calcLength: windSpeed = lb_preparation.selectHourlyData(windSpeed, analysisPeriod_)[7:]
        if IPTrigger == True:
            farenheitAirVals = lb_preparation.selectHourlyData(farenheitAirVals, analysisPeriod_)[7:]
            farenheitRadVals = lb_preparation.selectHourlyData(farenheitRadVals, analysisPeriod_)[7:]
            farenheitPrevailVals = lb_preparation.selectHourlyData(farenheitPrevailVals, analysisPeriod_)[7:]
        daysForMonths = lb_preparation.numOfDays
        dayNums = []
        if len(patternList) == 8760:
            HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod_, 1)
            newPatternList = []
            for hour in HOYS:
                newPatternList.append(patternList[hour-1])
            patternList = newPatternList
            for month in months:
                if days[0] == 1 and days[-1] == 31: dayNums.extend(range(daysForMonths[month-1], daysForMonths[month]))
                elif days[0] == 1 and days[-1] != 31: dayNums.extend(range(daysForMonths[month-1], daysForMonths[month-1]+days[-1]))
                elif days[0] != 1 and days[-1] == 31: dayNums.extend(range(daysForMonths[month-1]+days[0], daysForMonths[month]))
                else: dayNums.extend(range(daysForMonths[month-1]+days[0], daysForMonths[month-1]+days[-1]))
        else:
            HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod_, 1)
            for month in months:
                if days[0] == 1 and days[-1] == 31: dayNums.extend(range(daysForMonths[month-1], daysForMonths[month]))
                elif days[0] == 1 and days[-1] != 31: dayNums.extend(range(daysForMonths[month-1], daysForMonths[month-1]+days[-1]))
                elif days[0] != 1 and days[-1] == 31: dayNums.extend(range(daysForMonths[month-1]+days[0], daysForMonths[month]))
                else: dayNums.extend(range(daysForMonths[month-1]+days[0], daysForMonths[month-1]+days[-1]))
    else:
        months = [1,2,3,4,5,6,7,8,9,10,11,12]
        dayNums = range(365)
    if annualHourlyDataSplit != [[]]:
        annualHourlyDataSplitNew = []
        for annList in annualHourlyDataSplit:
            annualHourlyDataSplitNew.append(lb_preparation.selectHourlyData(annList, analysisPeriod_)[7:])
        annualHourlyDataSplit = annualHourlyDataSplitNew
    
    #If a conditional statement is applied, use it to select out data.
    if patternList != []:
        newAirTemp = []
        newRadTemp = []
        newPrevailTemp = []
        newWindSpeed = []
        newfarenheitAirVals = []
        newfarenheitRadVals = []
        newfarenheitPrevailVals = []
        newAnnualHourlyDataSplit = []
        for list in annualHourlyDataSplit:
            newAnnualHourlyDataSplit.append([])
        for count, bool in enumerate(patternList):
            if bool == True:
                newAirTemp.append(airTemp[count])
                newRadTemp.append(radTemp[count])
                newPrevailTemp.append(prevailTemp[count])
                if len(windSpeed) == calcLength: newWindSpeed.append(windSpeed[count])
                if IPTrigger == True:
                    newfarenheitAirVals.append(farenheitAirVals[count])
                    newfarenheitRadVals.append(farenheitRadVals[count])
                    newfarenheitPrevailVals.append(farenheitPrevailVals[count])
                for listCount in range(len(annualHourlyDataSplit)):
                    newAnnualHourlyDataSplit[listCount].append(annualHourlyDataSplit[listCount][count])
        airTemp = newAirTemp
        radTemp = newRadTemp
        prevailTemp = newPrevailTemp
        if len(windSpeed) == calcLength: windSpeed = newWindSpeed
        annualHourlyDataSplit = newAnnualHourlyDataSplit
        if IPTrigger == True:
            newfarenheitAirVals = farenheitAirVals
            newfarenheitRadVals = farenheitRadVals
            newfarenheitPrevailVals = farenheitPrevailVals
    
    #If the user has set incluse cold times to True, remove them from the list and give a comment.
    monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if ASHRAEorEN == True: modelName = "ASHRAE 55"
    else: modelName = "EN-15251"
    if coldTimes != []:
        coldThere = False
        if avgMonthOrRunMean == True:
            if includeColdTimes == False: coldMsg = "The following months were too cold for the official " + modelName + " standard and have been removed from the analysis:"
            else: coldMsg = "The following months were too cold for the official " + modelName + " standard and a correlation from recent research has been used in these cases:"
            for month in months:
                if month in coldTimes:
                    coldThere = True
                    coldMsg += '\n'
                    coldMsg += monthNames[month-1]
            if coldThere == True:
                print coldMsg
        else:
            totalColdInPeriod = []
            for day in dayNums:
                if day in coldTimes: totalColdInPeriod.append(day)
            if totalColdInPeriod != []:
                if includeColdTimes == True: coldMsg = "There were " + str(len(totalColdInPeriod)) + " days of the analysis period when the outdoor temperatures were too cold for the official " + modelName + " standard. \n A correlation from recent research has been used in these cases."
                else: coldMsg = "There were " + str(len(totalColdInPeriod)) + " days of the analysis period when the outdoor temperatures were too cold for the official " + modelName + " standard. \n These cases have been removed from the analysis."
                print coldMsg
    else:
        totalColdInPeriod = []
        for temp in prevailTemp:
            if temp < 10: totalColdInPeriod.append(temp)
        if totalColdInPeriod != []:
            if includeColdTimes == True: coldMsg = "There were " + str(len(totalColdInPeriod)) + " cases when the prevailing outdoor temperatures were too cold for the official " + modelName + " standard. \n A correlation from recent research has been used in these cases."
            else: coldMsg = "There were " + str(len(totalColdInPeriod)) + " cases when the prevailing outdoor temperatures were too cold for the official " + modelName + " standard. \n These cases have been removed from the analysis."
            print coldMsg
    if includeColdTimes == False:
        newAirTemp = []
        newRadTemp = []
        newPrevailTemp = []
        newWindSpeed = []
        newfarenheitAirVals = []
        newfarenheitRadVals = []
        newfarenheitPrevailVals = []
        newAnnualHourlyDataSplit = []
        for list in annualHourlyDataSplit:
            newAnnualHourlyDataSplit.append([])
        for count, preTemp in enumerate(prevailTemp):
            if preTemp > 10:
                newPrevailTemp.append(preTemp)
                newRadTemp.append(radTemp[count])
                newAirTemp.append(airTemp[count])
                if len(windSpeed) == calcLength: newWindSpeed.append(windSpeed[count])
                if IPTrigger == True:
                    newfarenheitAirVals.append(farenheitAirVals[count])
                    newfarenheitRadVals.append(farenheitRadVals[count])
                    newfarenheitPrevailVals.append(farenheitPrevailVals[count])
                if patternList != []:
                    for listCount in range(len(annualHourlyDataSplit)):
                        newAnnualHourlyDataSplit[listCount].append(annualHourlyDataSplit[listCount][count])
        airTemp = newAirTemp
        radTemp = newRadTemp
        prevailTemp = newPrevailTemp
        if len(windSpeed) == calcLength: windSpeed = newWindSpeed
        if IPTrigger == True:
            newfarenheitAirVals = farenheitAirVals
            newfarenheitRadVals = farenheitRadVals
            newfarenheitPrevailVals = farenheitPrevailVals
        if patternList != []: annualHourlyDataSplit = newAnnualHourlyDataSplit
    
    if windSpeed == []: windSpeed = [0]
    
    windSpeedForChart = []
    if len(windSpeed)== calcLength:
        windSpeedInit = windSpeed[:]
        windSpeedInit.sort()
        windSpeedForChart.append(windSpeedInit[0])
        windSpeedForChart.append(windSpeedInit[-1])
    else: windSpeedForChart = windSpeed
    
    # Generate the chart curves.
    chartCurvesAndTxt, finalComfortPolygons, belowTen, bound, allCurves, allText, allTextPt = drawAdaptChart(prevailTemp, windSpeedForChart, legendFont, legendFontSize, legendBold, epwData, epwStr, ASHRAEorEN, comfClass, levelOfConditioning, includeColdTimes, IPTrigger, lb_visualization, lb_comfortModels)
    
    #Generate the colored mesh.
    #As long as the calculation length is more than 1, make a colored mesh and get chart points for the input data.
    legend = []
    legendSrfs = None
    if legendFontSize != None: textSize = legendFontSize
    else: textSize = 0.5
    if calcLength > 1:
        chartHourPoints, adaptiveChartMesh, meshFaceValues = colorMesh(airTemp, radTemp, prevailTemp, lb_preparation, lb_comfortModels, lb_visualization, lowB, highB, customColors, belowTen, includeColdTimes, IPTrigger, farenheitAirVals, farenheitRadVals, farenheitPrevailVals)
        legendTitle = "Hours"
        lb_visualization.calculateBB(bound, True)
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(meshFaceValues, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
        legend.append(legendSrfs)
        for list in legendTextCrv:
            for item in list:
                legend.append(item)
        if legendBasePoint == None:
            legendBasePoint = lb_visualization.BoundingBoxPar[0]
        #Compile all text into one list.
        finalLegNum = []
        formatString = "%."+str(decimalPlaces)+"f"
        for num in legendText:
            try: finalLegNum.append(formatString % num)
            except: finalLegNum.append(num)
        if removeLessThan: pass
        else:
            finalLegNum[0] = "<=" + finalLegNum[0]
            finalLegNum[-2] = finalLegNum[-2] + "<="
        allText.extend(finalLegNum)
        allTextPt.extend(textPt)
    else:
        chartHourPoints = [rc.Geometry.Point3d(prevailTemp[0], (airTemp[0]+radTemp[0])/2, 0)]
        adaptiveChartMesh = None
        meshFaceValues = []
        legendBasePoint = None
    
    def runComfortModel(airTemp, radTemp, prevailTemp, winSpd, comfClass, levelOfConditioning):
        comfOr = []
        conditPer = []
        degTar = []
        prevTemp = []
        targTemp = []
        percHot = []
        perComf = []
        percCol = []
        if epwData == True and patternList == []:
            if analysisPeriod_ != []: runPeriod = analysisPeriod_
            else: runPeriod = [epwStr[5], epwStr[6]]
            degTar.extend([epwStr[0], epwStr[1], 'Degrees from Target Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
            comfOr.extend([epwStr[0], epwStr[1], 'Comfortable Or Not', 'Boolean', epwStr[4], runPeriod[0], runPeriod[1]])
            conditPer.extend([epwStr[0], epwStr[1], 'Adaptive Comfort', '-1 = Cold, 0 = Comfortable, 1 = Hot', epwStr[4], runPeriod[0], runPeriod[1]])
            prevTemp.extend([epwStr[0], epwStr[1], 'Prevailing Outdoor Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
            targTemp.extend([epwStr[0], epwStr[1], 'Adaptive Targer Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
        
        for count, atemp in enumerate(airTemp):
            if ASHRAEorEN == True: comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(atemp, radTemp[count], prevailTemp[count], winSpd[count], comfClass, levelOfConditioning)
            else: comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortEN15251(atemp, radTemp[count], prevailTemp[count], winSpd[count], comfClass, levelOfConditioning)
            comfOr.append(int(comf))
            conditPer.append(condition)
            degTar.append(distFromTarget)
            prevTemp.append(prevailTemp[count])
            targTemp.append(comfTemp)
            if condition == 1:
                percHot.append(1)
                perComf.append(0)
            elif condition == 0: perComf.append(1)
            else:
                percCol.append(1)
                perComf.append(0)
            
        
        return comfOr, conditPer, degTar, percHot, perComf, percCol, prevTemp, targTemp
    
    #Run each of the cases through the model to get a percentage of time comfortable.
    if len(windSpeed) != calcLength:
        for winSpd in windSpeed:
            winSpdList = [winSpd] * calcLength
            comfOr, conditPer, degTar, percHot, perComf, percCol, prevTemp, targTemp = runComfortModel(airTemp, radTemp, prevailTemp, winSpdList, comfClass, levelOfConditioning)
            comfortableOrNotInit.append(comfOr)
            conditionOfPersonInit.append(conditPer)
            degreesFromTargetInit.append(degTar)
            prevailTempInit.append(prevTemp)
            targetTempInit.append(targTemp)
            comfPercentOfTimeInit.append(sum(perComf)*100/len(airTemp))
            percentHotColdInit.append([sum(percHot)*100/len(airTemp), sum(percCol)*100/len(airTemp)])
    else:
        comfOr, conditPer, degTar, percHot, perComf, percCol, prevTemp, targTemp = runComfortModel(airTemp, radTemp, prevailTemp, windSpeed, comfClass, levelOfConditioning)
        comfortableOrNotInit.append(comfOr)
        conditionOfPersonInit.append(conditPer)
        degreesFromTargetInit.append(degTar)
        prevailTempInit.append(prevTemp)
        targetTempInit.append(targTemp)
        comfPercentOfTimeInit.append(sum(perComf)*100/len(airTemp))
        percentHotColdInit.append([sum(percHot)*100/len(airTemp), sum(percCol)*100/len(airTemp)])
    
    #Get the point colors and point color legends.
    pointColors, colorLegends = getPointColors(perComf, annualHourlyDataSplit, annualDataStr, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan, lb_visualization)
    
    #If the user has selected to scale or move the geometry, scale it all and/or move it all.
    if basePoint_ != None:
        transformMtx = rc.Geometry.Transform.Translation(basePoint_.X, basePoint_.Y, basePoint_.Z)
        for geo in chartCurvesAndTxt: geo.Transform(transformMtx)
        adaptiveChartMesh.Transform(transformMtx)
        for geo in legend: geo.Transform(transformMtx)
        legendBasePoint.Transform(transformMtx)
        for geoList in finalComfortPolygons:
            for geo in geoList: geo.Transform(transformMtx)
        for geo in chartHourPoints: geo.Transform(transformMtx)
        for geoList in colorLegends:
            for geo in geoList: geo.Transform(transformMtx)
        for geo in allTextPt: geo.Transform(transformMtx)
        basePoint = basePoint_
    else: basePoint = rc.Geometry.Point3d(0,0,0)
    
    if scale_ != None:
        transformMtx = rc.Geometry.Transform.Scale(basePoint, scale_)
        for geo in chartCurvesAndTxt: geo.Transform(transformMtx)
        adaptiveChartMesh.Transform(transformMtx)
        for geo in legend: geo.Transform(transformMtx)
        legendBasePoint.Transform(transformMtx)
        for geoList in finalComfortPolygons:
            for geo in geoList: geo.Transform(transformMtx)
        for geo in chartHourPoints: geo.Transform(transformMtx)
        for geoList in colorLegends:
            for geo in geoList: geo.Transform(transformMtx)
        for geo in allTextPt: geo.Transform(transformMtx)
    
    #If the user has set bakeIt to true, bake the geometry.
    if bakeIt_ > 0:
        #Set up the new layer.
        studyLayerName = 'ADAPTIVE_CHARTS'
        try:
            if 'Temperature' in _outdoorTemperature[2]: placeName = _outdoorTemperature[1]
            elif 'Temperature' in _dryBulbTemperature[2]: placeName = _dryBulbTemperature[1]
            else: placeName = 'alternateLayerName'
        except: placeName = 'alternateLayerName'
        newLayerIndex, l = lb_visualization.setupLayers(None, 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
        #Bake the objects.
        if bakeIt_ == 1: lb_visualization.bakeObjects(newLayerIndex, adaptiveChartMesh, legendSrfs, allText, allTextPt, textSize, legendFont, allCurves, decimalPlaces, True)
        else: lb_visualization.bakeObjects(newLayerIndex, adaptiveChartMesh, legendSrfs, allText, allTextPt, textSize, legendFont, allCurves, decimalPlaces, False)
    
    return comfortableOrNotInit, conditionOfPersonInit, degreesFromTargetInit, prevailTempInit, targetTempInit, comfPercentOfTimeInit, percentHotColdInit, chartCurvesAndTxt, adaptiveChartMesh, legend, legendBasePt, finalComfortPolygons, chartHourPoints, pointColors, colorLegends




#Check to be sure Ladybug is flying.
initCheck = False
if sc.sticky.has_key('ladybug_release'):
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): pass
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): pass
        initCheck = True
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    if initCheck == True:
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
else:
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")




#Check the inputs and organize the incoming data into streams that can be run throught the comfort model.
if initCheck == True:
    checkData = False
    checkData, epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed, ASHRAEorEN, comfClass, avgMonthOrRunMean, coldTimes, levelOfConditioning, includeColdTimes, titleStatement, patternList, IPTrigger, farenheitAirVals, farenheitRadVals, farenheitPrevailVals = checkTheInputs()


if checkData == True and _runIt == True:
    results = main(epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed, ASHRAEorEN, comfClass, avgMonthOrRunMean, coldTimes, levelOfConditioning, includeColdTimes, titleStatement, patternList, IPTrigger, farenheitAirVals, farenheitRadVals, farenheitPrevailVals, lb_preparation, lb_comfortModels, lb_visualization)
    if results != -1:
        comfortableOrNotInit, conditionOfPersonInit, degreesFromTargetInit, prevailTempInit, targetTempInit, comfPercentOfTime, percentHotColdInit, chartCurvesAndTxt, adaptiveChartMesh, legend, legendBasePt, finalComfortPolygons, chartHourPoints, pointColorsInit, colorLegendsInit = results
        
        #Unpack the data tree of comfort polygons.
        comfortPolygons = DataTree[Object]()
        comfortableOrNot = DataTree[Object]()
        conditionOfPerson = DataTree[Object]()
        degreesFromTarget = DataTree[Object]()
        prevailingTemp = DataTree[Object]()
        targetTemperature = DataTree[Object]()
        percentHotCold = DataTree[Object]()
        hourPointColors = DataTree[Object]()
        hourPointLegend = DataTree[Object]()
        for listCount, dataList in enumerate(finalComfortPolygons):
            for item in dataList: comfortPolygons.Add(item, GH_Path(listCount))
        for listCount, dataList in enumerate(comfortableOrNotInit):
            for item in dataList: comfortableOrNot.Add(item, GH_Path(listCount))
        for listCount, dataList in enumerate(conditionOfPersonInit):
            for item in dataList: conditionOfPerson.Add(item, GH_Path(listCount))
        for listCount, dataList in enumerate(degreesFromTargetInit):
            for item in dataList: degreesFromTarget.Add(item, GH_Path(listCount))
        for listCount, dataList in enumerate(prevailTempInit):
            for item in dataList: prevailingTemp.Add(item, GH_Path(listCount))
        for listCount, dataList in enumerate(targetTempInit):
            for item in dataList: targetTemperature.Add(item, GH_Path(listCount))
        for listCount, dataList in enumerate(percentHotColdInit):
            for item in dataList: percentHotCold.Add(item, GH_Path(listCount))
        for listCount, dataList in enumerate(pointColorsInit):
            for item in dataList: hourPointColors.Add(item, GH_Path(listCount))
        for listCount, dataList in enumerate(colorLegendsInit):
            for item in dataList: hourPointLegend.Add(item, GH_Path(listCount))

ghenv.Component.Params.Output[15].Hidden = True
ghenv.Component.Params.Output[17].Hidden = True