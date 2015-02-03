# Outdoor Comfort Calculator - Univeral Thermal Climate Index(UTCI)
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate the Universal Thermal Climate Index (UTCI) for a set of input climate conditions.  Perhaps the most familiar application of Univeral Thermal Climate Index (UTCI) is the temperature given by TV weathermen and women when they say that, "even though the dry bulb temperature outside is a certain value, the temperature actually "feels like" something higher or lower."
UTCI is this temperature of what the weather "feels like" and it takes into account the radiant temperature (sometimes including solar radiation), relative humidity, and wind speed.  UTCI uses these variables in a human energy balance model to give a temperature value that is indicative of the heat stress or cold stress felt by a human body in the outdoors.
_
A UTCI between 9 and 26 degrees Celcius indicates no thermal stress or comfortable conditions outdoors.
_
A UTCI between 26 and 28 degrees Celcius indicates slight heat stress (comfortable for short periods of time). Between 28 and 32 degrees, UTCI indicates moderate heat stress (hot but not dangerous).  Between 32 and 38 degrees, UTCI indicates strong heat stress (dangerous beyond short periods of time). Above 38, UTCI indicates very strong to extreme heat stress (very dangerous).
_
A UTCI between 0 and 9 degrees Celcius indicates slight cold stress (comfortable for short periods of time). Between 0 and -13 degrees, UTCI indicates moderate cold stress (cold but not dangerous).  Between -13 and -27 degrees, UTCI indicates strong cold stress (dangerous beyond short periods of time).  Below -27, UTCI indicates very stong to extreme cold stress (very dangerous).
_
_
UTCI is result of the world's leading comfort specailists' attempt to make an interational standard of outdoor temperature sensation that fills the follwoing requirements:
1)	Thermo-physiological significance in the whole range of heat exchange conditions of existing thermal environments
2)	Valid in all climates, seasons, and scales
3)	Useful for key applications in human biometeorology.
_
_
The code that makes this component possible is a Python version of the original Fortran code for calculating UTCI.  Information on UTCI and the original Fortran code can be found here: http://www.utci.org/.
-
Provided by Ladybug 0.0.59
    
    Args:
        _dryBulbTemperature: A number representing the dry bulb temperature of the air in degrees Celcius.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        meanRadiantTemperature_: A number representing the mean radiant temperature of the surrounding surfaces in degrees Celcius.  If no value is plugged in here, this component will assume that the mean radiant temperature is equal to air temperature value above.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        windSpeed_tenMeters: A number representing the wind speed of the air in meters per second at 10 meters off the ground (note that all wind readings for EPW data are 10m off the ground).  If no value is plugged in here, this component will assume a very low wind speed of 0.05 m/s, characteristic of most indoor conditions.  This input can also accept a list of wind speeds representing conditions at different times or the direct output of windSpeed from of the Import EPW component.
        _relativeHumidity: A number between 0 and 100 representing the relative humidity of the air in percentage.  This input can also accept a list of relative humidity values representing conditions at different times or the direct output of relativeHumidity from of the Import EPW component.
        ------------------------------: ...
        analysisPeriod_: An optional analysis period from the Analysis Period component.  If no Analysis period is given and epw data from the ImportEPW component has been connected, the analysis will be run for the enitre year.
    Returns:
        readMe!: ...
        ------------------------------: ...
        universalThermalClimateIndex: The UTCI of the input conditions in degrees Celcius. Perhaps the most familiar application of Univeral Thermal Climate Index (UTCI) is the temperature given by TV weathermen and women when they say that, even though the dry bulb temperature outside is a certain value, the temperature actually "feels like" something higher or lower. UTCI is this temperature of what the weather "feels like" and it takes into account radiant temperature (usually including solar radiation), relative humidity, wind speed and uses them in a human energy balance model to give a temperature value that is indicative of the heat stress or cold stress felt by the human body.
        comfortableOrNot: A stream of 0's and 1's (or "False" and "True" values) indicating whether a person outside is comfortable for each hour of the input conditions.  0 indicates that a person is not comfortable while 1 indicates that a person is comfortable.  A person is considered to be comfortable when he/she experiences no thermal stress (9 < UTCI < 26).
        thermalStress: A stream of interger values from -1 to +1 that indicate the following:
                       -1 - Cold Stress - cold conditions (UTCI < 9C).
                       0  - No Thermal Stress - comfortable conditions (9C < UTCI < 26C).
                       +1 - Heat Stress - hot conditions (UTCI > 26C).
        conditionOfPerson: A stream of interger values from -3 to +3 that indicate the following:
                       -3 - Strong Cold Stress - potential public health hazard with higher-than-normal mortality rates (UTCI < -13C).
                       -2 - Moderate Cold Stress - cold but no public health hazard (-13C < UTCI < 0C).
                       -1 - Slight Cold Stress - cool but comfortable for short periods of time (0C < UTCI < 9C)
                       0  - No Thermal Stress  - comfortable conditions (9C < UTCI < 26C).
                       +1 - Slight Heat Stress - warm but comfortable for short periods of time (26C < UTCI < 28C).
                       +2 - Moderate Heat Stress - hot but no public health hazard (28C < UTCI < 32C).
                       +3 - Strong Heat Stress - potential public health hazard with higher-than-normal mortality rates (UTCI > 32C).
        ------------------------------: ...
        percentOfTimeComfortable: The percent of the input data for which the UTCI indicates no thermal stress (comfortable conditions).  Comfortable conditions are when the UTCI is between 9 and 26 degrees Celcius.
        percentComfForShortPeriod: The percent of the input data for which the UTCI indicates slight heat/cold stress.  This indicates conditions that are comfortable for short periods of time with proper attire.  This includes all conditions when the UTCI is between 0 and 9 degrees Celcius or between 26 and 28 degrees Celcius.
        percentHeatStress: The percent of the input data for which the UTCI indicates moderate-to-extreme heat stress.  This indicates conditions that are not comfortable.  This includes all conditions are when the UTCI is above 28 degrees Celcius.
        percentColdStress: The percent of the input data for which the UTCI indicates moderate-to-extreme cold stress.  This indicates conditions that are not comfortable.  This includes all conditions are when the UTCI is below 0 degrees Celcius.

"""
ghenv.Component.Name = "Ladybug_Outdoor Comfort Calculator"
ghenv.Component.NickName = 'OutdoorComfortCalculator'
ghenv.Component.Message = 'VER 0.0.59\nFEB_01_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import Grasshopper.Kernel as gh
import math
import scriptcontext as sc




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
            if 'Temperature' in _dryBulbTemperature[2]:
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
            if 'Temperature' in meanRadiantTemperature_[2]:
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
    
    #Check lenth of the windSpeed_tenMeters_ list and evaluate the contents.
    checkData3 = False
    windSpeed = []
    windMultVal = False
    nonPositive = True
    if len(windSpeed_tenMeters_) != 0:
        try:
            if windSpeed_tenMeters_[2] == 'Wind Speed':
                windSpeed = windSpeed_tenMeters_[7:]
                checkData3 = True
                epwData = True
                epwStr = windSpeed_tenMeters_[0:7]
        except: pass
        if checkData3 == False:
            for item in windSpeed_tenMeters_:
                try:
                    if float(item) >= 0:
                        windSpeed.append(float(item))
                        checkData3 = True
                    else: nonPositive = False
                except: checkData3 = False
        if nonPositive == False: checkData3 = False
        if len(windSpeed) > 1: windMultVal = True
        if checkData3 == False:
            warning = 'windSpeed_tenMeters_ input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData3 = True
        windSpeed = [0.05]
        print 'No value connected for windSpeed_tenMeters_.  It will be assumed that the wind speed is a low 0.05 m/s.'
    
    #Check lenth of the _relativeHumidity list and evaluate the contents.
    checkData4 = False
    relHumid = []
    humidMultVal = False
    nonValue = True
    if len(_relativeHumidity) != 0:
        try:
            if _relativeHumidity[2] == 'Relative Humidity':
                relHumid = _relativeHumidity[7:]
                checkData4 = True
                epwData = True
                epwStr = _relativeHumidity[0:7]
        except: pass
        if checkData4 == False:
            for item in _relativeHumidity:
                try:
                    if 0 <= float(item) <= 100:
                        relHumid.append(float(item))
                        checkData4 = True
                    else: nonValue = False
                except:checkData4 = False
        if nonValue == False: checkData4 = False
        if len(relHumid) > 1: humidMultVal = True
        if checkData4 == False:
            warning = '_relativeHumidity input does not contain valid value.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'Connect a value for _relativeHumidity.'
    
    #Finally, for those lists of length greater than 1, check to make sure that they are all the same length.
    checkData5 = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True:
        if airMultVal == True or radMultVal == True or windMultVal == True or humidMultVal == True:
            listLenCheck = []
            if airMultVal == True: listLenCheck.append(len(airTemp))
            if radMultVal == True: listLenCheck.append(len(radTemp))
            if windMultVal == True: listLenCheck.append(len(windSpeed))
            if humidMultVal == True: listLenCheck.append(len(relHumid))
            
            if all(x == listLenCheck[0] for x in listLenCheck) == True:
                checkData5 = True
                calcLength = listLenCheck[0]
                
                if airMultVal == False: airTemp = duplicateData(airTemp, calcLength)
                if radMultVal == False: radTemp = duplicateData(radTemp, calcLength)
                if windMultVal == False: windSpeed = duplicateData(windSpeed, calcLength)
                if humidMultVal == False: relHumid = duplicateData(relHumid, calcLength)
                
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
    return checkData, epwData, epwStr, calcLength, airTemp, radTemp, windSpeed, relHumid


def main():
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
            
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        
        #Check the inputs and organize the incoming data into streams that can be run throught the comfort model.
        checkData = False
        checkData, epwData, epwStr, calcLength, airTemp, radTemp, windSpeed, relHumid = checkTheInputs()
        
        #Check if there is an analysisPeriod_ connected and, if not, run it for the whole year.
        if calcLength == 8760 and len(analysisPeriod_)!=0 and epwData == True:
            HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod_, 1)
            runPeriod = analysisPeriod_
            calcLength = len(HOYS)
        elif len(analysisPeriod_)==0 and epwData == True:
            HOYS = range(calcLength)
            runPeriod = [epwStr[5], epwStr[6]]
        else:
            HOYS = range(calcLength)
            runPeriod = [(1,1,1), (12,31,24)]
        
        #If things are good, run it through the comfort model.
        universalThermalClimateIndex = []
        comfortableOrNot = []
        thermalStressType = []
        coldStressComfortableHeatStress = []
        percentOfTimeComfortable = None
        percentComfForShortPeriod = None
        percentHeatStress = None
        percentColdStress = None
        if checkData == True and epwData == True:
            universalThermalClimateIndex.extend([epwStr[0], epwStr[1], 'Universal Thermal Climate Index', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
            comfortableOrNot.extend([epwStr[0], epwStr[1], 'Comfort or Not', 'Boolean Value', epwStr[4], runPeriod[0], runPeriod[1]])
            thermalStressType.extend([epwStr[0], epwStr[1], 'Thermal Stress', '-1 = Cold | 0 = Comfort | 1 = Hot', epwStr[4], runPeriod[0], runPeriod[1]])
            coldStressComfortableHeatStress.extend([epwStr[0], epwStr[1], 'Outdoor Comfort', '-3 = Extreme Cold | -2 = Cold | -1 = Cool | 0 = Comfort | 1 = Warm | 2 = Hot | 3 = Extreme Heat', epwStr[4], runPeriod[0], runPeriod[1]])
        elif checkData == True and epwData == True and 'for' in epwStr[2]:
            universalThermalClimateIndex.extend([epwStr[0], epwStr[1], 'Universal Thermal Climate Index' + ' for ' + epwStr[2].split('for ')[-1], 'C', epwStr[4], runPeriod[0], runPeriod[1]])
            comfortableOrNot.extend([epwStr[0], epwStr[1], 'Comfort or Not' + ' for ' + epwStr[2].split('for ')[-1], 'Boolean Value', epwStr[4], runPeriod[0], runPeriod[1]])
            thermalStressType.extend([epwStr[0], epwStr[1], 'Thermal Stress', '-1 = Cold | 0 = Comfort | 1 = Hot', epwStr[4], runPeriod[0], runPeriod[1]])
            coldStressComfortableHeatStress.extend([epwStr[0], epwStr[1], 'Outdoor Comfort' + ' for ' + epwStr[2].split('for ')[-1], '-3 = Extreme Cold | -2 = Cold | -1 = Cool | 0 = Comfort | 1 = Warm | 2 = Hot | 3 = Extreme Heat', epwStr[4], runPeriod[0], runPeriod[1]])
        if checkData == True:
            try:
                utciList = []
                comfOrNot = []
                thermalStr = []
                coldComfHot = []
                for count in HOYS:
                    # let the user cancel the process
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    
                    #If the difference between the air and rad temperatures is greater than 70 (because of solar radiation), move each closer to the average of the two.
                    if radTemp[count] - airTemp[count] >= 70.0:
                        distToMove = ((radTemp[count] - airTemp[count]) - 69.0)/2
                        radTemp[count] = radTemp[count]-distToMove
                        airTemp[count] = airTemp[count]+distToMove
                        print "Index " + str(count) + " had a difference between air temperature and radiant temperature greater than 70.  Both temperatures wee moved closer to their average to prevent the comfort model from failing."
                    utci, comf, condition, stressVal = lb_comfortModels.comfUTCI(airTemp[count], radTemp[count], windSpeed[count], relHumid[count])
                    if utci != None:
                        utciList.append(utci)
                        comfOrNot.append(comf)
                        thermalStr.append(stressVal)
                        coldComfHot.append(condition)
                    else:
                        utciList.append(50)
                        comfOrNot.append(0)
                        thermalStr.append(1)
                        coldComfHot.append(3)
                comfTime = []
                for item in comfOrNot:
                    if item == 1: comfTime.append(1.0)
                    else: pass
                percentOfTimeComfortable = ((sum(comfTime))/calcLength)*100
                short = []
                hot = []
                cold = []
                for item in coldComfHot:
                    if item == -1 or item == 1: short.append(1.0)
                    elif item == -2 or item == -3: cold.append(1.0)
                    elif item == 2 or item == 3: hot.append(1.0)
                    else: pass
                percentHeatStress = ((sum(hot))/calcLength)*100
                percentColdStress = ((sum(cold))/calcLength)*100
                percentComfForShortPeriod = ((sum(short))/calcLength)*100
                universalThermalClimateIndex.extend(utciList)
                comfortableOrNot.extend(comfOrNot)
                thermalStressType.extend(thermalStr)
                coldStressComfortableHeatStress.extend(coldComfHot)
            except:
                universalThermalClimateIndex = []
                comfortableOrNot = []
                thermalStressType = []
                coldStressComfortableHeatStress = []
                percentOfTimeComfortable = None
                percentComfForShortPeriod = None
                percentHeatStress = None
                percentColdStress = None
                print "The calculation has been terminated by the user!"
                e = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
        
        #Return all of the info.
        return universalThermalClimateIndex, comfortableOrNot, thermalStressType, coldStressComfortableHeatStress, percentOfTimeComfortable, percentComfForShortPeriod, percentHeatStress, percentColdStress
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return [None, None, None, None, None, None]




if _runIt == True:
    
    results = main()
    
    if results != -1:
        universalThermalClimateIndex, comfortableOrNot, thermalStress, conditionOfPerson, \
        percentOfTimeComfortable, percentComfForShortPeriod, percentHeatStress, \
        percentColdStress = results





