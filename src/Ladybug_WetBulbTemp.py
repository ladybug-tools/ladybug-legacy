# Wet Bulb Temperature
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Use this component to calculate Wet Bulb Temperature and Dew Point Temperature
-
This component uses the "Method for obtaining wet-bulb temperatures by modifying the psychrometric formula"
created by J. Sullivan and L. D. Sanders (Center for Experiment Design and Data Analysis).
NOAA - National Oceanic and Atmospheric Administration
Special thanks goes to the authors of the online wet-bulb temperature calculator 
http://www.srh.noaa.gov/epz/?n=wxcalc_rh
-
Provided by Ladybug 0.0.64
    
    Args:
        _dryBulbTemperature: The dry bulb temperature [C] from Import epw component and Ladybug_Average Data or generic lists of numbers.
        _relativeHumidity: The relative humidity [%] from Import epw component and Ladybug_Average Data or generic lists of numbers.
        _barometricPressure_: The barometric pressure [Pa] from Import epw component and Ladybug_Average Data or generic lists of numbers. If no value is connected here, the default pressure will be 101325 Pa, which is air pressure at sea level.
    Returns:
        readMe!: ...
        wetBulbTemp : The lowest temperature that can be reached by evaporating water into the air.
        dewPointTemp : The temperature at which the water vapor contained in a volume of air at a given atmospheric pressure reaches saturation and condenses to form dew.
"""

ghenv.Component.Name = "Ladybug_WetBulbTemp"
ghenv.Component.NickName = 'WetBulbTemp & DewPointTemp'
ghenv.Component.Message = 'VER 0.0.64\nFEB_05_2017'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

import math




def checkTheData():
    #Define a value that will indicate whether someone has hooked up epw data.
    epwData = False
    epwStr = []
    
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
    
    #Check lenth of the _relativeHumidity list and evaluate the contents.
    checkData4 = False
    relHumid = []
    humidMultVal = False
    nonValue = True
    if len(_relativeHumidity) != 0:
        try:
            if "Humidity" in _relativeHumidity[2]:
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
    
    #Check lenth of the _barometricPressure_ list and evaluate the contents.
    checkData3 = False
    barPress = []
    pressMultVal = False
    nonPositive = True
    if len(_barometricPressure_) != 0:
        try:
            if _barometricPressure_[2] == 'Wind Speed':
                barPress = _barometricPressure_[7:]
                checkData3 = True
                epwData = True
                epwStr = _barometricPressure_[0:7]
        except: pass
        if checkData3 == False:
            for item in _barometricPressure_:
                try:
                    if float(item) >= 0:
                        barPress.append(float(item))
                        checkData3 = True
                    else: nonPositive = False
                except: checkData3 = False
        if nonPositive == False: checkData3 = False
        if len(barPress) > 1: pressMultVal = True
        if checkData3 == False:
            warning = '_barometricPressure_ input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData3 = True
        barPress = [0.05]
        print 'No value connected for _barometricPressure_.  It will be assumed that the pressure is at seal level.'
    
    
    #Finally, for those lists of length greater than 1, check to make sure that they are all the same length.
    checkData2 = False
    if checkData1 == True and checkData3 == True and checkData4 == True:
        if airMultVal == True or pressMultVal == True or humidMultVal == True:
            listLenCheck = []
            if airMultVal == True: listLenCheck.append(len(airTemp))
            if pressMultVal == True: listLenCheck.append(len(barPress))
            if humidMultVal == True: listLenCheck.append(len(relHumid))
            
            if all(x == listLenCheck[0] for x in listLenCheck) == True:
                checkData2 = True
                calcLength = listLenCheck[0]
                
                def duplicateData(data, calcLength):
                    dupData = []
                    for count in range(calcLength):
                        dupData.append(data[0])
                    return dupData
                
                if airMultVal == False: airTemp = duplicateData(airTemp, calcLength)
                if humidMultVal == False: relHumid = duplicateData(relHumid, calcLength)
                if pressMultVal == False: barPress = duplicateData(barPress, calcLength)
            else:
                calcLength = None
                warning = 'If you have put in lists with multiple values, the lengths of these lists must match across the parameters or you have a single value for a given parameter to be applied to all values in the list.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData2 = True
            calcLength = 1
    else:
        calcLength = 0
    
    checkData = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True: checkData = True
    
    return checkData, airTemp, relHumid, barPress, epwStr


#dbTemp [Celsius], RH [%], Psta [Pa]
def WBFUNC(dbTemp, RH, Psta):
    es = 6.112 * math.e**((17.67 * dbTemp) / (dbTemp + 243.5))
    
    e = (es * RH) / 100
    
    
    Tw = 0
    increse = 10
    previoussign = 1
    Ed = 1
    
    while math.fabs(Ed) > 0.005:
        Ewg = 6.112 * math.e**((17.67 * Tw) / (Tw + 243.5))
        eg = Ewg - (Psta/100) * (dbTemp - Tw) * 0.00066 * (1 + (0.00155 * Tw))
        Ed = e - eg
        if Ed ==0:
            break
        else:
            if Ed <0:
                cursign = -1
                if cursign != previoussign:
                    previoussign = cursign
                    increse = increse/10
                else:
                    increse = increse
            else:
                cursign = 1
                if cursign != previoussign:
                    previoussign = cursign
                    increse = increse/10
                else:
                    increse = increse
        Tw = Tw + increse * previoussign
    wbTemp = round(Tw,2)
    return wbTemp



def DPTFUNC(dbTemp, RH):
    es = 6.112 * math.e**((17.67 * dbTemp) / (dbTemp + 243.5))
    
    e = (es * RH) / 100
    
    Td = (243.5 * math.log(e / 6.112)) / (17.67 - math.log(e / 6.112))
    
    dpTemp = round(Td,2)
    return dpTemp


def main(dryBulbTemperature, relativeHumidity, barometricPressure, epwStr):
    # declare the lists
    if epwStr == []:
        wetBulbTemp =[]
        dewPointTemp =[]
    else:
        epwStr[2] = "Wet Bulb Temperature"
        wetBulbTemp = epwStr[:]
        epwStr[2] = "Dew Point Temperature"
        dewPointTemp = epwStr[:]
    
    for i in range(0, len(dryBulbTemperature)):
        wbTemp = WBFUNC(dryBulbTemperature[i], relativeHumidity[i], barometricPressure[i])
        wetBulbTemp.append(float(wbTemp))
        dpTemp = DPTFUNC(dryBulbTemperature[i], relativeHumidity[i])
        dewPointTemp.append(float(dpTemp))
    print "Congratulations! Now you have wet-bulb temperatures."
    
    # return the values
    return wetBulbTemp, dewPointTemp 


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
    lb_preparation = sc.sticky["ladybug_Preparation"]()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
    lb_wind = None


#Check the data to make sure it is the correct type
if initCheck == True and len(_dryBulbTemperature) > 0 and len(_relativeHumidity) > 0 and _dryBulbTemperature[0] != None and _relativeHumidity[0] != None:
    checkData, airTemp, relHumid, barPress, epwStr = checkTheData()
    
    if checkData == True:
        result = main(airTemp, relHumid, barPress, epwStr)
        if result != -1:
            wetBulbTemp, dewPointTemp = result
            print 'Calculation completed successfully!'