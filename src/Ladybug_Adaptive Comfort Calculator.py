# Adaptive Comfort Calculator
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

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
Provided by Ladybug 0.0.57
    
    Args:
        _dryBulbTemperature: A number representing the dry bulb temperature of the air in degrees Celcius.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        meanRadiantTemperature_: A number representing the mean radiant temperature of the surrounding surfaces in degrees Celcius.  If no value is plugged in here, this component will assume that the mean radiant temperature is equal to air temperature value above.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        _prevailingOutdoorTemp: A number representing the average monthly outdoor temperature in degrees Celcius.  This average monthly outdoor temperature is the temperature that occupants in naturally ventilated buildings tend to adapt themselves to. For this reason, this input can also accept the direct output of dryBulbTemperature from the Import EPW component if houlry values for the full year are connected for the other inputs of this component.
        windSpeed_: A number representing the wind speed of the air in meters per second.  If no value is plugged in here, this component will assume a very low wind speed of 0.3 m/s, characteristic of most naturally ventilated buildings.  This input can also accept a list of wind speeds representing conditions at different times or the direct output of windSpeed from of the Import EPW component.
        ------------------------------: ...
        eightyPercentComfortable_: Set to "True" to have the comfort standard be 80 percent of occupants comfortable and set to "False" to have the comfort standard be 90 percent of all occupants comfortable.  The default is set to "True" for 80 percent, which is what most members of the building industry aim for.  However some projects will occasionally use 90%.
        analysisPeriod_: An optional analysis period from the Analysis Period component.  If no Analysis period is given and epw data from the ImportEPW component has been connected, the analysis will be run for the enitre year.
        _runIt: Set to "True" to run the component and calculate the adaptive comfort metrics.
    Returns:
        readMe!: ...
        ------------------------------: ...
        comfortableOrNot: A stream of 0's and 1's (or "False" and "True" values) indicating whether occupants are comfortable under the input conditions given the fact that these occupants tend to adapt themselves to the prevailing mean monthly temperature. 0 indicates that a person is not comfortable while 1 indicates that a person is comfortable.
        conditionOfPerson: A stream of interger values from -1 to +2 that correspond to each hour of the input data and indicate the following: -1 = The average monthly temperature is too extreme for the adaptive model. 0 = The input conditions are too cold for occupants. 1 = The input conditions are comfortable for occupants. 2 = The input conditions are too hot for occupants.
        upperTemperatureBound: A stream of temperature values in degrees Celcius indicating the highest possible temperature in the comfort range for each hour of the input conditions.  
        lowerTemperatureBound: A stream of temperature values in degrees Celcius indicating the lowest possible temperature in the comfort range for each hour of the input conditions.
        ------------------------------: ...
        percentOfTimeComfortable: The percent of the input data for which the occupants are comfortable.  Comfortable conditions are when the indoor temperature is within the comfort range determined by the prevailing outdoor temperature.
        percentHotColdAndExtreme: A list of 3 numerical values indicating the following: 0) The percent of the input data for which the occupants are too hot.  1) The percent of the input data for which the occupants are too cold. 2) The percent of the input data falling in a month where the prevailing mean temperature is below 10 C or above 33.5 C and is therefore not suitable for the adaptive comfort method.
        
"""
ghenv.Component.Name = "Ladybug_Adaptive Comfort Calculator"
ghenv.Component.NickName = 'AdaptiveComfortCalculator'
ghenv.Component.Message = 'VER 0.0.57\nJUL_01_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
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
    if meanRadiantTemperature_[2] == "Dry Bulb Temperature":
        outdoorConditions = True
except: pass
try:
    if windSpeed_[2] == "Wind Speed":
        outdoorConditions = True
except: pass

if outdoorConditions == True:
    message1 = "Because the adaptive comfort model is derived from indoor comfort studies and you have hooked up outdoor data, the values out of this component only indicate how much the outdoor condtions should be changed in order to make indoor conditions comfortable."
    message2 = "They do not idicate whether someone will actually be comfortable outdoors."
    message3 = "If you are interested in whether the outdoors are actually comfortable, you should use the Ladybug Outdoor Comfort Calculator."
    print message1, message2, message3
    m = gh.GH_RuntimeMessageLevel.Remark
    ghenv.Component.AddRuntimeMessage(m, message1)
    ghenv.Component.AddRuntimeMessage(m, message2)
    ghenv.Component.AddRuntimeMessage(m, message3)

ghenv.Component.Attributes.Owner.OnPingDocument()


def checkTheInputs():
    #Define a value that will indicate whether someone has hooked up epw data.
    epwData = False
    epwStr = []
    
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
            if _prevailingOutdoorTemp[2] == 'Dry Bulb Temperature' and (len(airTemp) == 8760 or len(airTemp) == 1):
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[7:751])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[751:1423])/672)], 672))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[1423:2167])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[2167:2887])/720)], 720))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[2887:3631])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[3631:4351])/720)], 720))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[4351:5095])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[5095:5839])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[5839:6559])/720)], 720))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[6559:7303])/744)], 744))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[7303:8023])/720)], 720))
                prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[8023:])/744)], 744))
                checkData3 = True
                epwData = True
                epwStr = _prevailingOutdoorTemp[0:7]
        except: pass
        if checkData3 == False:
            for item in _prevailingOutdoorTemp:
                try:
                    prevailTemp.append(float(item))
                    checkData3 = True
                except: checkData3 = False
        if len(prevailTemp) > 1: prevailMultVal = True
        if checkData3 == False:
            warning = '_prevailingOutdoorTemp input does not contain valid temperature values in degrees Celcius.'
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
            if airMultVal == True: listLenCheck.append(len(airTemp))
            if radMultVal == True: listLenCheck.append(len(radTemp))
            if prevailMultVal == True: listLenCheck.append(len(prevailTemp))
            if windMultVal == True: listLenCheck.append(len(windSpeed))
            
            if all(x == listLenCheck[0] for x in listLenCheck) == True:
                checkData5 = True
                calcLength = listLenCheck[0]
                
                if airMultVal == False: airTemp = duplicateData(airTemp, calcLength)
                if radMultVal == False: radTemp = duplicateData(radTemp, calcLength)
                if prevailMultVal == False: prevailTemp = duplicateData(prevailTemp, calcLength)
                if windMultVal == False: windSpeed = duplicateData(windSpeed, calcLength)
                
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
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True:
        checkData = True
    else:
        checkData = False
    
    #Let's return everything we need.
    return checkData, epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed



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


def main():
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        
        #Check the inputs and organize the incoming data into streams that can be run throught the comfort model.
        checkData = False
        checkData, epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed = checkTheInputs()
        
        #Check if there is an analysisPeriod_ connected and, if not, run it for the whole year.
        if calcLength == 8760 and len(analysisPeriod_)!=0 and epwData == True:
            HOYS, months, days = getHOYsBasedOnPeriod(analysisPeriod_, 1, lb_preparation)
            runPeriod = analysisPeriod_
            calcLength = len(HOYS)
        elif len(analysisPeriod_)==0 and epwData == True:
            HOYS = range(calcLength)
            runPeriod = [epwStr[5], epwStr[6]]
        else:
            HOYS = range(calcLength)
            runPeriod = [(1,1,1), (12,31,24)]
        
        #If things are good, run it through the comfort model.
        comfortableOrNot = []
        extremeColdComfortableHot = []
        upperTemperatureBound = []
        lowerTemperatureBound = []
        percentOfTimeComfortable = None
        percentHotColdAndExtreme = []
        if checkData == True and epwData == True:
            comfortableOrNot.extend([epwStr[0], epwStr[1], 'Adaptive Comofortable Or Not', 'Boolean', epwStr[4], runPeriod[0], runPeriod[1]])
            extremeColdComfortableHot.extend([epwStr[0], epwStr[1], 'Adaptive Comfort', '-1 = Extreme Prevailing, 0 = Cold, 1 = Comfortable, 2 = Hot', epwStr[4], runPeriod[0], runPeriod[1]])
            upperTemperatureBound.extend([epwStr[0], epwStr[1], 'Adaptive Upper Comfort Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
            lowerTemperatureBound.extend([epwStr[0], epwStr[1], 'Adaptive Lower Comfort Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
        if checkData == True:
            try:
                comfOrNot = []
                extColdComfHot = []
                upperTemp = []
                lowerTemp = []
                for count in HOYS:
                    # let the user cancel the process
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    
                    lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(airTemp[count], radTemp[count], prevailTemp[count], windSpeed[count], eightyPercentComfortable_)
                    if comf == True:comfOrNot.append(1)
                    else: comfOrNot.append(0)
                    extColdComfHot.append(condition)
                    upperTemp.append(upTemp)
                    lowerTemp.append(lowTemp)
                percentOfTimeComfortable = ((sum(comfOrNot))/calcLength)*100
                extreme = []
                hot = []
                cold = []
                for item in extColdComfHot:
                    if item == -1: extreme.append(1.0)
                    elif item == 0: cold.append(1.0)
                    elif item == 2: hot.append(1.0)
                    else: pass
                percentHot = ((sum(hot))/calcLength)*100
                percentCold = ((sum(cold))/calcLength)*100
                percentExtreme = ((sum(extreme))/calcLength)*100
                percentHotColdAndExtreme = [percentHot, percentCold, percentExtreme]
                comfortableOrNot.extend(comfOrNot)
                extremeColdComfortableHot.extend(extColdComfHot)
                upperTemperatureBound.extend(upperTemp)
                lowerTemperatureBound.extend(lowerTemp)
            except:
                comfortableOrNot = []
                extremeColdComfortableHot = []
                upperTemperatureBound = []
                lowerTemperatureBound = []
                percentOfTimeComfortable = None
                percentHotColdAndExtreme = []
                print "The calculation has been terminated by the user!"
                e = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
        
        #Return all of the info.
        return comfortableOrNot, extremeColdComfortableHot, percentOfTimeComfortable, percentHotColdAndExtreme, upperTemperatureBound, lowerTemperatureBound
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return [None, None, None, None, None, None]




if _runIt == True:
    comfortableOrNot, conditionOfPerson, percentOfTimeComfortable, percentHotColdAndExtreme, upperTemperatureBound, lowerTemperatureBound = main()



