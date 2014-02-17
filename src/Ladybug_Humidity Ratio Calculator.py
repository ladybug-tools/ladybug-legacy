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
Provided by Ladybug 0.0.54
    
    Args:
        _dryBulbTemperature: The dry bulb temperature from the Import EPW component
        _relativeHumidity: The relative humidity from the Import EPW component
        _barometricPressure: The barometric pressure from the Import EPW component
    Returns:
        readMe!: ...
        humidityRatio: The hourly humidity ratio in (kg water / kg air)
        enthalpy: The hourly enthalpy of the air in (kJ/kg)
        partialPressure: The partial pressure of water vapor in the atmosphere.
        saturationPressure: The saturation pressure of water vapor in the atmosphere.
"""

ghenv.Component.Name = "Ladybug_Humidity Ratio Calculator"
ghenv.Component.NickName = 'CalcHumidityRatio'
ghenv.Component.Message = 'VER 0.0.54\nFEB_16_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import math


#Check the data to make sure it is the correct type
try:
   hourlyDBTemp = _dryBulbTemperature
   if hourlyDBTemp[2] == 'Dry Bulb Temperature' and hourlyDBTemp[4] == 'Hourly': checkData1 = True
   else: checkData1 = False
   
   hourlyRH = _relativeHumidity
   if hourlyRH[2] == 'Relative Humidity' and hourlyRH[4] == 'Hourly': checkData2 = True
   else: checkData2 = False
   
   barPress = _barometricPressure
   if barPress[2] == 'Barometric Pressure' and barPress[4] == 'Hourly': checkData3 = True
   else: checkData3 = False
   
   if checkData1 == True and checkData2 == True and checkData3 == True: checkData = True
except: checkData = False

if checkData == True:
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
   
   #Convert Temperature to Kelvin
   TKelvin = []
   for item in Tnumbers:
       TKelvin.append(item+273)
   
   #Calculate saturation vapor pressure above freezing
   Sigma = []
   for item in TKelvin:
       if item >= 273:
          Sigma.append(1-(item/647.096))
       else:
           Sigma.append(0)
   
   ExpressResult = []
   for item in Sigma:
       ExpressResult.append(((item)*(-7.85951783))+((item**1.5)*1.84408259)+((item**3)*(-11.7866487))+((item**3.5)*22.6807411)+((item**4)*(-15.9618719))+((item**7.5)*1.80122502))
   
   CritTemp = []
   for item in TKelvin:
       CritTemp.append(647.096/item)
   
   Exponent = [a*b for a,b in zip(CritTemp,ExpressResult)]
   
   Power = []
   for item in Exponent:
       Power.append(math.exp(item))
   
   SatPress1 = []
   for item in Power:
       if item != 1:
           SatPress1.append(item*22064000)
       else:
           SatPress1.append(0)
   
   #Calculate saturation vapor pressure below freezing
   Theta = []
   for item in TKelvin:
       if item < 273:
          Theta.append(item/273.16)
       else:
           Theta.append(1)
   
   Exponent2 = []
   for x in Theta:
       Exponent2.append(((1-(x**(-1.5)))*(-13.928169))+((1-(x**(-1.25)))*34.707823))
   
   Power = []
   for item in Exponent2:
       Power.append(math.exp(item))
   
   SatPress2 = []
   for item in Power:
       if item != 1:
           SatPress2.append(item*611.657)
       else:
           SatPress2.append(0)
   
   #Combine into final saturation vapor pressure
   satPress = [a+b for a,b in zip(SatPress1,SatPress2)]
   
   #Calculate hourly water vapor pressure
   DecRH = []
   for item in Rnumbers:
       DecRH.append(item*0.01)
   
   vapPress = [a*b for a,b in zip(DecRH,satPress)]
   
   #Calculate hourly humidity ratio
   PressDiffer = [a-b for a,b in zip(Bnumbers,vapPress)]
   
   Constant = []
   for item in vapPress:
       Constant.append(item*0.621991)
   
   HRCalc = [a/b for a,b in zip(Constant,PressDiffer)]
   
   #Calculate hourly enthalpy
   EnVariable1 = []
   for item in HRCalc:
       EnVariable1.append(1.01+(1.89*item))
   
   EnVariable2 = [a*b for a,b in zip(EnVariable1,Tnumbers)]
   
   EnVariable3 = []
   for item in HRCalc:
       EnVariable3.append(2500*item)
   
   EnVariable4 = [a+b for a,b in zip(EnVariable2,EnVariable3)]
   
   ENCalc = []
   for x in EnVariable4:
       if x >= 0:
           ENCalc.append(x)
       else:
           ENCalc.append(0)
   
   #Build the strings and add it to the final calculation outputs
   HR = []
   
   HR.append(Tstr[0])
   HR.append(Tstr[1])
   HR.append('Humidity Ratio')
   HR.append('kg water / kg air')
   HR.append('Hourly')
   HR.append(Tstr[5])
   HR.append(Tstr[6])
   
   for item in HRCalc:
       HR.append(item)
   
   EN = []
   
   EN.append(Tstr[0])
   EN.append(Tstr[1])
   EN.append('Enthalpy')
   EN.append('kJ/kg')
   EN.append('Hourly')
   EN.append(Tstr[5])
   EN.append(Tstr[6])
   
   for item in ENCalc:
       EN.append(item)
   
   
   SP = []
   
   SP.append(Tstr[0])
   SP.append(Tstr[1])
   SP.append('Saturation Pressure')
   SP.append('Pa')
   SP.append('Hourly')
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
   
   
   
   #Output the final results!
   humidityRatio = HR
   enthalpy = EN
   partialPressure = VP
   saturationPressure = SP
   
   print 'Humidity ratio calculation completed successfully!'
else:
    print 'Please provide all of the required annual data inputs.'
