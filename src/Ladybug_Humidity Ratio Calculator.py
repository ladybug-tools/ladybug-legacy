# This component calculates the humidity ratio from the ladybug weather file import parameters
# By Chris Mackey
# chris@mackeyarchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
#Conversion formulas are taken from the following publications:
#Vaisala. (2013) Humidity Conversion Formulas: Calculation Formulas for Humidity. www.vaisala.com/Vaisala%20Documents/Application%20notes/Humidity_Conversion_Formulas_B210973EN-F.pdf
#W. Wagner and A. Pru:" The IAPWS Formulation 1995 for the Thermodynamic Properties of Ordinary Water Substance for General and Scientific Use ", Journal of Physical and Chemical Reference Data, June 2002 ,Volume 31, Issue 2, pp. 387535

"""
Calculates the humidity ratio from the ladybug weather file import parameters
Conversion formulas are taken from the following publications:
Vaisala. (2013) Humidity Conversion Formulas: Calculation Formulas for Humidity. www.vaisala.com/Vaisala%20Documents/Application%20notes/Humidity_Conversion_Formulas_B210973EN-F.pdf
W. Wagner and A. Pru:" The IAPWS Formulation 1995 for the Thermodynamic Properties of Ordinary Water Substance for General and Scientific Use ", Journal of Physical and Chemical Reference Data, June 2002 ,Volume 31, Issue 2, pp. 387535

-
Provided by Ladybug 0.0.57
    
    Args:
        _dryBulbTemperature: The dry bulb temperature from the Import epw component.
        _relativeHumidity: The relative humidity from the Import epw component.
        _barometricPressure: The barometric pressure from the Import epw component.
    Returns:
        readMe!: ...
        humidityRatio: The hourly humidity ratio (kg water / kg air).
        enthalpy: The hourly enthalpy of the air (kJ / kg).
        partialPressure: The hourly partial pressure of water vapor in the atmosphere (Pa).
        saturationPressure: The saturation pressure of water vapor in the atmosphere (Pa).
"""

ghenv.Component.Name = "Ladybug_Humidity Ratio Calculator"
ghenv.Component.NickName = 'CalcHumidityRatio'
ghenv.Component.Message = 'VER 0.0.57\nJUL_13_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import math
import scriptcontext as sc

def checkTheData():
    try:
       hourlyDBTemp = _dryBulbTemperature
       if 'Temperature' in hourlyDBTemp[2] and hourlyDBTemp[4] == 'Hourly': checkData1 = True
       else: checkData1 = False
       
       hourlyRH = _relativeHumidity
       if 'Relative Humidity' in hourlyRH[2] and hourlyRH[4] == 'Hourly': checkData2 = True
       else: checkData2 = False
       
       barPress = _barometricPressure
       if 'Barometric Pressure' in barPress[2] and barPress[4] == 'Hourly': checkData3 = True
       else: checkData3 = False
       
       if checkData1 == True and checkData2 == True and checkData3 == True: checkData = True
    except: checkData = False
    
    return checkData


def main():
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        
        #Separate the numbers from the header strings
        Tnumbers = []
        Tstr = []
        for item in _dryBulbTemperature:
           try: Tnumbers.append(float(item))
           except: Tstr.append(item)
        
        Rnumbers = []
        Rstr = []
        for item in _relativeHumidity:
           try: Rnumbers.append(float(item))
           except: Rstr.append(item)
        
        Bnumbers = []
        Bstr = []
        for item in _barometricPressure:
           try: Bnumbers.append(float(item))
           except: Bstr.append(item)
        
        #Calculate the Humidity Ratio.
        HRCalc, ENCalc, vapPress, satPress = lb_comfortModels.calcHumidRatio(Tnumbers, Rnumbers, Bnumbers)
        
        #Build the strings and add it to the final calculation outputs
        HR = []
        
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
checkData = checkTheData()

if checkData == True:
    humidityRatio, enthalpy, partialPressure, saturationPressure = main()
    print 'Humidity ratio calculation completed successfully!'
else:
    print 'Please provide all of the required annual data inputs.'
