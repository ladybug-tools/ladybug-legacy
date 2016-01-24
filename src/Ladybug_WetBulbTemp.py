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
Provided by Ladybug 0.0.61
    
    Args:
        _dryBulbTemperature: The dry bulb temperature [C] from Import epw component and Ladybug_Average Data or generic lists of numbers.
        _relativeHumidity: The relative humidity [%] from Import epw component and Ladybug_Average Data or generic lists of numbers.
        _barometricPressure: The barometric pressure [Pa] from Import epw component and Ladybug_Average Data or generic lists of numbers.
    Returns:
        readMe!: ...
        wetBulbTemp : The lowest temperature that can be reached by evaporating water into the air.
        dewPointTemp : The temperature at which the water vapor contained in a volume of air at a given atmospheric pressure reaches saturation and condenses to form dew.
"""

ghenv.Component.Name = "Ladybug_WetBulbTemp"
ghenv.Component.NickName = 'WetBulbTemp & DewPointTemp'
ghenv.Component.Message = 'VER 0.0.61\nJAN_24_2016'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

import math



def checkTheData(_dryBulbTemperature, _relativeHumidity, _barometricPressure):
    if _dryBulbTemperature == None \
    and _relativeHumidity == None \
    and _barometricPressure == None:
        checkData = False
    elif _dryBulbTemperature and _relativeHumidity and _barometricPressure:
        checkData = False
    else: checkData = True
    return checkData



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


def main():
    
    w = gh.GH_RuntimeMessageLevel.Warning
    # check number of element of lists and data type
    try:
        if len(_dryBulbTemperature) != len(_relativeHumidity) or \
        len(_dryBulbTemperature) != len(_barometricPressure) or \
        len(_relativeHumidity) != len(_barometricPressure):
            warning = "All lists must have the same number of elements."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    except: pass
        
    # declare the lists
    wetBulbTemp =[]
    dewPointTemp =[]
    
    # calculate data from EPW or from generic data
    try:
       # check data type are the same
        if _dryBulbTemperature[0] == float() or _relativeHumidity[0] == float() or _relativeHumidity[0] == float():
            warning = "Please, choose whether EPW data or lists of numbers"
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        # calculation
        dryBulbTemperature = []
        relativeHumidity = []
        barometricPressure = []
        for item in _dryBulbTemperature:
         dryBulbTemperature.append(float(item))
        for item in _relativeHumidity:
            relativeHumidity.append(float(item))
        for item in _barometricPressure:
            barometricPressure.append(float(item))
        for i in range(0, len(dryBulbTemperature)):
            wbTemp = WBFUNC(dryBulbTemperature[i], relativeHumidity[i], barometricPressure[i])
            wetBulbTemp.append(float(wbTemp))
            dpTemp = DPTFUNC(dryBulbTemperature[i], relativeHumidity[i])
            dewPointTemp.append(float(dpTemp))
        print "Congratulation! now you have wet-bulb temperatures from generic weather data."
    except:
        # check data type are the same
        if _relativeHumidity[0] != _barometricPressure[0] or \
        _dryBulbTemperature[0] != _relativeHumidity[0] or \
        _dryBulbTemperature[0] != _barometricPressure [0]:
            warning = "Please, choose whether EPW data or lists of numbers"
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        # calculation
        dryBulbTemperature = _dryBulbTemperature[7:]
        relativeHumidity   = _relativeHumidity[7:]
        barometricPressure = _barometricPressure[7:]
        for i in range(0, len(dryBulbTemperature)):
            wbTemp = WBFUNC(dryBulbTemperature[i], relativeHumidity[i], barometricPressure[i])
            wetBulbTemp.append(wbTemp)
            dpTemp = DPTFUNC(dryBulbTemperature[i], relativeHumidity[i])
            dewPointTemp.append(dpTemp)
        _dryBulbTemperature[2] = "Wet Bulb Temperature"
        wetBulbTemp = _dryBulbTemperature[:7] + wetBulbTemp
        _dryBulbTemperature[2] = "Dew Point Temperature"
        dewPointTemp = _dryBulbTemperature[:7] + dewPointTemp
        print "Congratulation! now you have EPW wet-bulb temperatures from EPW file."
        
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
checkData = False
if initCheck == True:
    checkData = checkTheData(_dryBulbTemperature, _relativeHumidity, _barometricPressure)

    if checkData == False :
        result = main()
        if result != -1:
            wetBulbTemp, dewPointTemp = result
            print 'Temperature calculation completed successfully!'
    else:
        print 'Please provide all _inputs'