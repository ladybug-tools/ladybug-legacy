# This component calculates the humidity ratio from the ladybug weather file import parameters
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Chris Mackey <chris@mackeyarchitecture.com> 
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

#Conversion formulas are taken from the following publications:
#Vaisala. (2013) Humidity Conversion Formulas: Calculation Formulas for Humidity. www.vaisala.com/Vaisala%20Documents/Application%20notes/Humidity_Conversion_Formulas_B210973EN-F.pdf
#W. Wagner and A. Pru:" The IAPWS Formulation 1995 for the Thermodynamic Properties of Ordinary Water Substance for General and Scientific Use ", Journal of Physical and Chemical Reference Data, June 2002 ,Volume 31, Issue 2, pp. 387535

"""
Calculates the humidity ratio from the ladybug weather file import parameters
Conversion formulas are taken from the following publications:
Vaisala. (2013) Humidity Conversion Formulas: Calculation Formulas for Humidity. www.vaisala.com/Vaisala%20Documents/Application%20notes/Humidity_Conversion_Formulas_B210973EN-F.pdf
W. Wagner and A. Pru:" The IAPWS Formulation 1995 for the Thermodynamic Properties of Ordinary Water Substance for General and Scientific Use ", Journal of Physical and Chemical Reference Data, June 2002 ,Volume 31, Issue 2, pp. 387535

-
Provided by Ladybug 0.0.66
    
    Args:
        _dryBulbTemperature: The dry bulb temperature from the Import epw component.
        _relativeHumidity: The relative humidity from the Import epw component.
        _barometricPressure: A number representing the barometric pressure in Pascals.  If no value is connected here, the default pressure will be 101325 Pa, which is air pressure at sea level.  It is recommended that you connect the barometric pressure from the Import epw component here as the air pressure at sea level can cause some misleading results for cities at higher elevations.
    Returns:
        readMe!: ...
        humidityRatio: The hourly humidity ratio (kg water / kg air).
        enthalpy: The hourly enthalpy of the air (kJ / kg).
        partialPressure: The hourly partial pressure of water vapor in the atmosphere (Pa).
        saturationPressure: The saturation pressure of water vapor in the atmosphere (Pa).
"""

ghenv.Component.Name = "Ladybug_Humidity Ratio Calculator"
ghenv.Component.NickName = 'CalcHumidityRatio'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import math
import scriptcontext as sc
import Grasshopper.Kernel as gh

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
    
    #Check lenth of the barometricPressure_ list and evaluate the contents.
    checkData3 = False
    barPress = []
    pressMultVal = False
    nonPositive = True
    if len(barometricPressure_) != 0:
        try:
            if barometricPressure_[2] == 'Wind Speed':
                barPress = barometricPressure_[7:]
                checkData3 = True
                epwData = True
                epwStr = barometricPressure_[0:7]
        except: pass
        if checkData3 == False:
            for item in barometricPressure_:
                try:
                    if float(item) >= 0:
                        barPress.append(float(item))
                        checkData3 = True
                    else: nonPositive = False
                except: checkData3 = False
        if nonPositive == False: checkData3 = False
        if len(barPress) > 1: pressMultVal = True
        if checkData3 == False:
            warning = 'barometricPressure_ input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData3 = True
        barPress = [101325]
        print 'No value connected for barometricPressure_.  It will be assumed that the pressure is at seal level.'
    
    
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



def main(Tnumbers, Rnumbers, Bnumbers, Tstr):
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
            
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        
        #Calculate the Humidity Ratio.
        HRCalc, ENCalc, vapPress, satPress = lb_comfortModels.calcHumidRatio(Tnumbers, Rnumbers, Bnumbers)
        
        #Build the strings and add it to the final calculation outputs
        HR = []
        
        if Tstr != []:
            HR.append(Tstr[0])
            HR.append(Tstr[1])
            HR.append('Humidity Ratio')
            HR.append('kg water / kg air')
            HR.append(Tstr[4])
            HR.append(Tstr[5])
            HR.append(Tstr[6])
        
        for item in HRCalc:
           HR.append(item)
        
        EN = []
        if Tstr != []:
            EN.append(Tstr[0])
            EN.append(Tstr[1])
            EN.append('Enthalpy')
            EN.append('kJ/kg')
            EN.append(Tstr[4])
            EN.append(Tstr[5])
            EN.append(Tstr[6])
        
        for item in ENCalc:
           EN.append(item)
        
        
        SP = []
        if Tstr != []:
            SP.append(Tstr[0])
            SP.append(Tstr[1])
            SP.append('Saturation Pressure')
            SP.append('Pa')
            SP.append(Tstr[4])
            SP.append(Tstr[5])
            SP.append(Tstr[6])
        
        satPress100 = []
        for item in satPress:
           satPress100.append(item*100)
        
        for item in satPress100:
           SP.append(item)
        
        VP = []
        if Tstr != []:
            VP.append(Tstr[0])
            VP.append(Tstr[1])
            VP.append('Vapor Pressure')
            VP.append('Pa')
            VP.append('Hourly')
            VP.append(Tstr[5])
            VP.append(Tstr[6])
        
        vapPress100 = []
        for item in vapPress:
           vapPress100.append(item*100)
        
        for item in vapPress100:
           VP.append(item)
        
        return HR, EN, VP, SP
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return None, None, None, None


#Check the data to make sure it is the correct type
checkData, airTemp, relHumid, barPress, epwStr = checkTheData()

if checkData == True:
    res = main(airTemp, relHumid, barPress, epwStr)
    if res!=-1:
        humidityRatio, enthalpy, partialPressure, saturationPressure = res
        print 'Humidity ratio calculation completed successfully!'
else:
    print 'Please provide all of the required annual data inputs.'
