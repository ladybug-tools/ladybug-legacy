# Residential hot water
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Djordje Spasic <djordjedspasic@gmail.com> 
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
Use this component to calculate domestic hot water consumption for each hour during a year, for a single family household (house).
-
Component based on paper: "Modeling patterns of hot water use in households", Ernest Orlando Lawrence Berkeley National Laboratory; Lutz, Liu, McMahon, Dunham, Shown, McGrue; Nov 1996:
http://ees.lbl.gov/sites/all/files/modeling_patterns_of_hot_water_use_in_households_lbl-37805_rev.pdf
-
Provided by Ladybug 0.0.67
    
    input:
        _epwFile: Input .epw file path by using the "File Path" parameter, or Ladybug's "Open EPW And STAT Weather Files" component.
        _totalNumberOfPersons: Total number of persons in a household.
        numberOfPreSchoolChildren_: Number of preschool children(0-5) in household.
                                    -
                                    If not supplied, default value: 0 (no preschool children) will be used.
        numberOfSchoolChildren_: Number of school age(6-13) children in household.
                                 -
                                 If not supplied, default value: 0 (no school children) will be used.
        numberOfAdults_: Number of adults (14 years and older) in household.
                         -
                         If not supplied, it will be equal to _totalNumberOfPersons.
        numberOfAdultsAtHome_: Number of adults that stay at home during a day.
                               -
                               If not supplied, default value: 0 (no adults at home) will be used.
        seniorOnly_: Senior only household.
                     -
                     If not supplied, default value: False (not senior only household) will be used.
        dishWasher_: A household owns a dish washer.
                     -
                     If not supplied, default value: True (a household owns a dish washer) will be used.
        clothsWasher_: A household owns a cloths washer.
                       -
                       If not supplied, default value: True (a household owns a cloths washer) will be used.
        payUtilityBill_: Household occupants pay a utility bill.
                         Tenants who pay their own utility bills in general, tend to spend less, then those who do not.
                         -
                         If not supplied, default value: True (household occupants pay their utility bill) will be used.
        firstWeekStartDay_: A day of week on which a year starts (1 - Monday, 2 - Tuesday, 3 - Wednesday...)
                            -
                            If not supplied, default value: 1 will be used (year starts on Monday, 1st January).
        weekendDays_: Define a list of two weekend (nonworking) days. Through out the World, countries have different days as their weekend days:
                      -
                      Thursday and Friday (4,5)
                      Friday and Saturday (5,6)
                      Saturday and Sunday (6,7)
                      -
                      If not supplied, Saturday and Sunday (6,7) will be taken as a default weekend days.
        holidayDays_: List of days (1 to 365) which are holiday (nonworking) days.
                      -
                      Here is an example holiday days list for August:
                      213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243
                      -
                      If not supplied, no holiday days will be used.
        deliveryWaterTemperature_: Required (set) water temperature.
                                   It is recommended for delivery water temperature to not be lower than 60C (140F) to avoid the risk of propagation of Legionella pneumophila bacteria.
                                   -
                                   Electric water heater used as a default.
                                   -
                                   If not supplied, default value: 60C (140F) will be used.
                                   -
                                   In Celsius degrees.
        coldWaterTemperaturePerHour_: Cold (inlet) water temperature supplied from public water system, for each hour during a year. In Celsius.
                                      To calculate it, use the "coldWaterTemperaturePerHour" output of the Ladybug "Cold Water Temperature" component.
                                      -
                                      If not supplied, it will be calculated based on Christensen and Burch method (method 1 from "Cold Water Temperature" component), with pipes depth from 0.3 to 1 meters, and unknown soil type.
                                      -
                                      In Celsius degrees.
        _runIt: ...
        
    output:
        readMe!: ...
        heatingLoadPerHour: Thermal energy (or electrical energy) required to heat the domestic hot water consumption for each hour during a year.
                            -
                            In kWh.
        hotWaterPerHour: Domestic hot water consumption for each hour during a year.
                         -
                         In L/h (Liters/hour).
        hotWaterPerYear: Domestic hot water consumption for a whole year.
                         -
                         In L (Liters).
        averageDailyHotWaterPerYear: Average daily hot water consumption for a whole year.
                                     -
                                     In L/day (Liters/day).
        maximumDailyConsumption: Maximal hot water consumption per day during a year.
                                 -
                                 In (L/day) Liters/day.
        maximumConsumptionDay: Day with maximal hot water consumption.
        minimumDailyConsumption: Minimal hot water consumption per day during a year.
                                 -
                                 In (L/day) Liters/day.
        minimumConsumptionDay: Day with minimal hot water consumption.
"""

ghenv.Component.Name = "Ladybug_Residential Hot Water"
ghenv.Component.NickName = "ResidentialHotWater"
ghenv.Component.Message = 'VER 0.0.67\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Renewables"
#compatibleLBVersion = VER 0.0.61\nDEC_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
import math


def getEpwData(epwFile):
    
    if epwFile:
        try:
            # location data
            locationName, latitude, longitude, timeZone, elevation, locationString = lb_preparation.epwLocation(epwFile)
            # weather data
            weatherData = lb_preparation.epwDataReader(epwFile, locationName)
            dryBulbTemperature, dewPointTemperature, relativeHumidity, windSpeed, windDirection, directNormalRadiation, diffuseHorizontalRadiation, globalHorizontalRadiation, directNormalIlluminance, diffuseHorizontalIlluminance, globalHorizontalIlluminance, totalSkyCover, liquidPrecipitationDepth, barometricPressure, modelYear = weatherData
            dryBulbTemperatureData = dryBulbTemperature[7:]
            
            daysHOY = []
            day = 1
            for i in range(365):
                for k in range(24):
                    daysHOY.append(day)
                day += 1
            
            hoursHOY = []
            hour = 1
            for i in range(365):
                for k in range(24):
                    hoursHOY.append(hour)
                    hour += 1
                hour = 1
            
            validEpwData = True
            printMsg = "ok"
            
            return locationName, float(latitude), dryBulbTemperatureData, daysHOY, hoursHOY, validEpwData, printMsg
        
        except Exception, e:
            # something is wrong with "_epwFile" input
            locationName = latitude = dryBulbTemperatureData = daysHOY = hoursHOY = None
            validEpwData = False
            printMsg = "Something is wrong with \"_epwFile\" input."
    else:
        locationName = latitude = dryBulbTemperatureData = daysHOY = hoursHOY = None
        validEpwData = False
        printMsg = "Please supply .epw file path to \"_epwFile\" input"
    
    return locationName, latitude, dryBulbTemperatureData, daysHOY, hoursHOY, validEpwData, printMsg


def checkInputData(totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, holidayDays, deliveryWaterTemperature, coldWaterTemperaturePerHour, dryBulbTemperatureData):
    
    if (totalNumberOfPersons == None):
        totalNumberOfPersons = numberOfPreSchoolChildren = numberOfSchoolChildren = numberOfAdults = numberOfAdultsAtHome = seniorOnly = dishWasher = clothsWasher = payUtilityBill = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends = holidayDays = deliveryWaterTemperature = coldWaterTemperature = tankSize = None
        validInputData = False
        printMsg = "Please input \"_totalNumberOfPersons\"."
        
        return totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, tankSize, validInputData, printMsg
    
    elif (totalNumberOfPersons == 0) or (totalNumberOfPersons < 0):
        totalNumberOfPersons = numberOfPreSchoolChildren = numberOfSchoolChildren = numberOfAdults = numberOfAdultsAtHome = seniorOnly = dishWasher = clothsWasher = payUtilityBill = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends = holidayDays = deliveryWaterTemperature = coldWaterTemperature = tankSize = None
        validInputData = False
        printMsg = "\"totalNumberOfPersons\" input can not be equal or less than 0. Please input a number of persons larger than 0."
        
        return totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, tankSize, validInputData, printMsg
    
    if (numberOfPreSchoolChildren == None) or (numberOfPreSchoolChildren < 0) or (numberOfSchoolChildren > totalNumberOfPersons):
        numberOfPreSchoolChildren = 0  # default
    
    if (numberOfSchoolChildren == None) or (numberOfSchoolChildren < 0) or (numberOfSchoolChildren > totalNumberOfPersons):
        numberOfSchoolChildren = 0  # default
    
    if (numberOfAdults == None) or (numberOfAdults < 0) or (numberOfAdults > totalNumberOfPersons):
        numberOfAdults = totalNumberOfPersons  # default
    
    if (numberOfAdultsAtHome == None) or (numberOfAdultsAtHome < 0) or (numberOfAdultsAtHome > totalNumberOfPersons):
        numberOfAdultsAtHome = 0  # default
    
    if (seniorOnly == None):
        seniorOnly = False  # default
    
    if (dishWasher == None):
        dishWasher = True  # default
    
    if (clothsWasher == None):
        clothsWasher = True  # default
    
    if (payUtilityBill == None):
        payUtilityBill = True  # default
    
    if (firstWeekStartDay == None) or (firstWeekStartDay < 1) or (firstWeekStartDay > 7):
        firstWeekStartDay = 1  # default, Monday
    
    if (len(weekendDays) == 0):
        weekendDays = [6,7]  # default, Saturday, Sunday
        firstWeekSubtractWeekends = 0
    elif (len(weekendDays) != 2):
        totalNumberOfPersons = numberOfPreSchoolChildren = numberOfSchoolChildren = numberOfAdults = numberOfAdultsAtHome = seniorOnly = dishWasher = clothsWasher = payUtilityBill = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends = holidayDays = deliveryWaterTemperature = coldWaterTemperature = tankSize = None
        validInputData = False
        printMsg = "\"weekendDays_\" input can only include two consecutive values(days).\n" + \
                   "These are the allowed combinations:\n-\n" + \
                   "Monday, Tuesday (1,2)\n" + \
                   "Tuesday, Wednesday (2,3)\n" + \
                   "Wednesday, Thursday (3,4)\n" + \
                   "Thursday, Friday (4,5)\n" + \
                   "Friday, Saturday (5,6)\n" + \
                   "Saturday, Sunday (6,7)\n" + \
                   "Sunday, Monday (7,1)"
        
        return totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, tankSize, validInputData, printMsg
    elif (weekendDays[0] < 1) or (weekendDays[1] < 1) or (weekendDays[0] > 7) or (weekendDays[1] > 7):
        totalNumberOfPersons = numberOfPreSchoolChildren = numberOfSchoolChildren = numberOfAdults = numberOfAdultsAtHome = seniorOnly = dishWasher = clothsWasher = payUtilityBill = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends = holidayDays = deliveryWaterTemperature = coldWaterTemperature = tankSize = None
        validInputData = False
        printMsg = "\"weekendDays_\" input can not be less than 1 or larger than 7. Please input two weekendDays_ numbers from 1 to 7."
        
        return totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, tankSize, validInputData, printMsg
    else:
        if (6 in weekendDays) and (7 in weekendDays):
            firstWeekSubtractWeekends = 0
        elif (5 in weekendDays) and (6 in weekendDays):
            firstWeekSubtractWeekends = 1
        elif (4 in weekendDays) and (5 in weekendDays):
            firstWeekSubtractWeekends = 2
        elif (3 in weekendDays) and (4 in weekendDays):
            firstWeekSubtractWeekends = 3
        elif (2 in weekendDays) and (3 in weekendDays):
            firstWeekSubtractWeekends = 4
        elif (1 in weekendDays) and (2 in weekendDays):
            firstWeekSubtractWeekends = 5
        elif (1 in weekendDays) and (7 in weekendDays):
            firstWeekSubtractWeekends = 6
        else:
            totalNumberOfPersons = numberOfPreSchoolChildren = numberOfSchoolChildren = numberOfAdults = numberOfAdultsAtHome = seniorOnly = dishWasher = clothsWasher = payUtilityBill = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends = holidayDays = deliveryWaterTemperature = coldWaterTemperature = tankSize = None
            validInputData = False
            printMsg = "\"weekendDays_\" input can only include two consecutive values(days).\n" + \
                       "These are the allowed combinations:\n-\n" + \
                       "Monday, Tuesday (1,2)\n" + \
                       "Tuesday, Wednesday (2,3)\n" + \
                       "Wednesday, Thursday (3,4)\n" + \
                       "Thursday, Friday (4,5)\n" + \
                       "Friday, Saturday (5,6)\n" + \
                       "Saturday, Sunday (6,7)\n" + \
                       "Sunday, Monday (7,1)"
            
            return totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, tankSize, validInputData, printMsg
    
    
    if (len(holidayDays) == 0):
        holidayDays = []  # default
    elif (holidayDays[0] < 1) or (holidayDays[1] < 1) or (holidayDays[0] > 365) or (holidayDays[1] > 365):
        totalNumberOfPersons = numberOfPreSchoolChildren = numberOfSchoolChildren = numberOfAdults = numberOfAdultsAtHome = seniorOnly = dishWasher = clothsWasher = payUtilityBill = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends = holidayDays = deliveryWaterTemperature = coldWaterTemperature = tankSize = None
        validInputData = False
        printMsg = "\"holidayDays_\" input can not be less than 1 or larger than 365. Please input a holidayDays_ number from 1 to 365."
        
        return totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, tankSize, validInputData, printMsg
    
    
    if (deliveryWaterTemperature == None) or (deliveryWaterTemperature < 0):
        deliveryWaterTemperature = 60  # default
    
    if (len(coldWaterTemperaturePerHour) == 0) or (coldWaterTemperaturePerHour[0] is ""):
        method = 1; minimalTemperature = 1  # default: method 1 (Christensen and Burch), with fixed pipes depth from 0.3 to 1 meters, and unknown soil type.
        coldWaterTemperature, coldWaterTemperaturePerYear, TcoldHOYminimal, TcoldHOYmaximal = lb_photovoltaics.inletWaterTemperature(dryBulbTemperatureData, method, minimalTemperature)
    elif (len(coldWaterTemperaturePerHour) == 8767):
        coldWaterTemperature = coldWaterTemperaturePerHour[7:]
    elif (len(coldWaterTemperaturePerHour) == 8760):
        coldWaterTemperature = coldWaterTemperaturePerHour
    
    
    # ASHRAE 20 gallons (75.7082 liters) per day per person
    tankSize = totalNumberOfPersons * 75.7082  # in Liters
    
    validInputData = True
    printMsg = "ok"
    
    return totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, tankSize, validInputData, printMsg


def weekdayConsumptionCoefficients(hour, dishWasherCoeff2, clothsWasherCoeff2, latitude):
    #hot water seasonal consumption coefficients for individual households on weekdays:
    if (hour > 23) or (hour <= 6):
        coefficients = [0, 0.6163, 0, 0, 0, 0, -0.0017, 0, 0, 0, 0, 0]
        if latitude >= 0:
            # northern hemisphere
            seasonCoeff = [0.5523, 0, 0, 0]  # winter, spring, summer, autumn
        else:
            # southern hemisphere
            seasonCoeff = [0, 0, 0.5523, 0]  # winter, spring, summer, autumn
    elif (hour > 6) and (hour <= 8):
        coefficients = [2.0956, 0, 0, 3.4830, 7.9861, 0, 0.0269, -0.5424, 0.6603, -3.6609, 0, 0]
        if latitude >= 0:
            seasonCoeff = [0, 0, -13.6010, 0]
        else:
            seasonCoeff = [-13.6010, 0, 0, 0]
    elif (hour > 8) and (hour <= 11):
        coefficients = [0, 0, 1.0853, 1.5331, 2.4972, 0, 0, 0, 0, 9.0418, 0, 0]
        if latitude >= 0:
            seasonCoeff = [2.1403, 0, 0, -1.6353]
        else:
            seasonCoeff = [0, -1.6353, 2.1403, 0]
    elif (hour > 11) and (hour <= 13):
        coefficients = [-0.3876, 0, 0.9668, 1.0849, 2.0956, -0.0218, 0, 0, 0, 6.1986, 0, 0]
        if latitude >= 0:
            seasonCoeff = [1.5187, 0, 0, -1.6834]
        else:
            seasonCoeff = [0, -1.6834, 1.5187, 0]
    elif (hour > 13) and (hour <= 17):
        coefficients = [-0.2907, 0, 1.9790, 1.2, 2.3072, -0.0906, 0.0083, 0, 0.0743, 4.0228, 0, 0]
        if latitude >= 0:
            seasonCoeff = [2.5854, 0 , 0, 0]
        else:
            seasonCoeff = [0, 0, 2.5854, 0]
    elif (hour > 17) and (hour <= 19):
        coefficients = [0.7753, 0, 1.5679, 2.0415, 3.6018, 0, 0, -0.3134, 0.3570, 5.3492, dishWasherCoeff2/4, 0]
        if latitude >= 0:
            seasonCoeff = [3.656, 0, -3.6855, 0]
        else:
            seasonCoeff = [-3.6855, 0, 3.656, 0]
    elif (hour > 19) and (hour <= 21):
        coefficients = [4.4577, 0, 2.7456, 4.4092, 3.3455, -0.1015, 0.0187, 0, 0.3523, 0, dishWasherCoeff2/4, clothsWasherCoeff2/3]
        if latitude >= 0:
            seasonCoeff = [0, 0, -8.0527, -3.2509]
        else:
            seasonCoeff = [-8.0527, -3.2509, 0, 0]
    elif (hour > 21) and (hour <= 23):
        coefficients = [4.2881, 0, 1.4434, 3.4394, 2.5135, -0.0436, 0, 0, 0.2848, -2.4166, 0, 0]
        if latitude >= 0:
            seasonCoeff = [0, 0, -3.3773, -3.5511]
        else:
            seasonCoeff = [-3.3773, -3.5511, 0, 0]
    
    return coefficients, seasonCoeff


def weekendConsumptionCoefficients(hour, dishWasherCoeff2, clothsWasherCoeff2, latitude):
    #hot water seasonal consumption coefficients for individual households on weekends:
    if (hour > 23) or (hour <= 6):
        coefficients = [0, 0.3036, 0, 0, 0, 0, -0.0017, 0, 0, 0, 0, 0]
        if latitude >= 0:
            # northern hemisphere
            seasonCoeff = [0.642, 0.3433, 0.6341, 0]  # winter, spring, summer, autumn
        else:
            # southern hemisphere
            seasonCoeff = [0.6341, 0, 0.642, 0.3433]  # winter, spring, summer, autumn
    elif (hour > 6) and (hour <= 8):
        coefficients = [3.8036, 0, 0, 1.1515, 1.3389, 0, 0.0269, 0, 0.2140, 0, 0, 0]
        if latitude >= 0:
            seasonCoeff = [0, 0, -5.9393, -2.4806]
        else:
            seasonCoeff = [-5.9393, -2.4806, 0, 0]
    elif (hour > 8) and (hour <= 11):
        coefficients = [0, 0, 1.3045, 2.7796, 5.6808, 0, 0, 0, 0, 0, 0, clothsWasherCoeff2/3]
        if latitude >= 0:
            seasonCoeff = [5.1164, 4.7598, 0, 0]
        else:
            seasonCoeff = [0, 0, 5.1164, 4.7598]
    elif (hour > 11) and (hour <= 13):
        coefficients = [2.5923, 0, 0.9009, 2.007, 5.4181, -0.1833, 0, 0, 0.3291, 0, 0, 0]
        if latitude >= 0:
            seasonCoeff = [5.6039, 0, -4.784, 0]
        else:
            seasonCoeff = [-4.784, 0, 5.6039, 0]
    elif (hour > 13) and (hour <= 17):
        coefficients = [1.817, 0, 1.7303, 1.7201, 3.8043, -0.1445, 0.0083, 0, 0.2467, 0, 0, 0]
        if latitude >= 0:
            seasonCoeff = [4.4501, 0, -3.5602, 0]
        else:
            seasonCoeff = [-3.5602, 0, 4.4501, 0]
    elif (hour > 17) and (hour <= 19):
        coefficients = [3.1616, 0, 2.1596, 2.9693, 3.8607, -0.1806, 0, 0, 0.3584, 0, dishWasherCoeff2/4, 0]
        if latitude >= 0:
            seasonCoeff = [6.202, 0, -5.6168, 0]
        else:
            seasonCoeff = [-5.6168, 0, 6.202, 0]
    elif (hour > 19) and (hour <= 21):
        coefficients = [3.5007, 0, 1.2038, 4.9574, 2.3144, 0, 0.0187, 0, 0.1969, 0, dishWasherCoeff2/4, 0]
        if latitude >= 0:
            seasonCoeff = [0, 3.1275, -3.6961, 0]
        else:
            seasonCoeff = [-3.6961, 0, 0, 3.1275]
    elif (hour > 21) and (hour <= 23):
        coefficients = [0, 0, 1.8965, 3.0862, 2.5695, 0, 0, 0, 0, 0, 0, 0]
        if latitude >= 0:
            seasonCoeff = [0, 0, 0, -1.4339]
        else:
            seasonCoeff = [0, -1.4339, 0, 0]
    
    return coefficients, seasonCoeff


def seasonIndices(day):
    if day <= 80 or (day > 355):  # < 21st March or > 21st December
        winter = 1
        spring = 0
        summer = 0
        autumn = 0
    elif (day > 80) and (day <= 172):  # 21st March to 21st June
        winter = 0
        spring = 1
        summer = 0
        autumn = 0
    elif (day > 172) and (day <= 264):  # 21st June to 21st September
        winter = 0
        spring = 0
        summer = 1
        autumn = 0
    elif (day > 264) and (day <= 355):  # 21st September to 21st December
        winter = 0
        spring = 0
        summer = 0
        autumn = 1
    
    return winter, spring, summer, autumn


def main(totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, tankSize, dryBulbTemperatureData, coldWaterTemperature, daysHOY, hoursHOY, latitude):
    
    # dishWasher, clothsWasher, senior, utility bill coefficients
    if dishWasher == True:
        dishWasherCoeff2 = 0
        dishWasherAnnualCoeff = 0
    else:
        dishWasherCoeff2 = (2.620*totalNumberOfPersons + 5.054*math.sqrt(totalNumberOfPersons))
        dishWasherAnnualCoeff = (2.620*totalNumberOfPersons + 5.054*math.sqrt(totalNumberOfPersons))
    
    if clothsWasher == True:
        clothsWasherCoeff2 = 0
        clothsWasherAnnualCoeff = 0
    else:
        clothsWasherCoeff2 = (4.424*totalNumberOfPersons + 18.070*math.sqrt(totalNumberOfPersons))
        clothsWasherAnnualCoeff = (4.424*totalNumberOfPersons + 18.070*math.sqrt(totalNumberOfPersons))
    
    if seniorOnly == True:
        seniorCoeff = 0.379   # if senior only
    else:
        seniorCoeff = 1.0   # if not senior only
    
    if payUtilityBill == True:
        payUtilityBillCoeff = 1.0   # if pay
    else:
        payUtilityBillCoeff = 1.3625   # if do not pay
    
    
    hotWaterPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Domestic hot water load", "L/h", "Hourly", (1, 1, 1), (12, 31, 24)]
    heatingLoadPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Domestic hot water heating load", "kWh", "Hourly", (1, 1, 1), (12, 31, 24)]
    hotWaterPerDays = [[] for i in range(365)]
    firstWeekLength = (8 - firstWeekSubtractWeekends) - firstWeekStartDay
    
    for i,day in enumerate(daysHOY):
        hour = hoursHOY[i]
        if day in holidayDays:
            # it's holiday day
            HWC = 0
            Qload_kWh = 0
        else:
            # not a holiday day
            if ((day-firstWeekLength+1)%7 == 0) or ((day-firstWeekLength)%7 == 0):
                # it's weekend day
                coefficients, seasonCoeff = weekendConsumptionCoefficients(hour, dishWasherCoeff2, clothsWasherCoeff2, latitude)
            else:
                # it's week day
                coefficients, seasonCoeff = weekdayConsumptionCoefficients(hour, dishWasherCoeff2, clothsWasherCoeff2, latitude)
            constantCoeff, numOfPersonsCoeff, age1Coeff, age2Coeff, age3Coeff, ThotCoeff, tankSizeCoeff, TinletCoeff, TaCoeff, atHomeCoeff, dishWasherCoeff, clothsWasherCoeff = coefficients
            winterCoeff, springCoeff, summerCoeff, autumnCoeff = seasonCoeff
            winter, spring, summer, autumn = seasonIndices(day)
            
            #hot water consumption per hour
            HWC = (constantCoeff + numOfPersonsCoeff*totalNumberOfPersons + age1Coeff*numberOfPreSchoolChildren + age2Coeff*numberOfSchoolChildren + age3Coeff*numberOfAdults + ThotCoeff*deliveryWaterTemperature + tankSizeCoeff*tankSize + TinletCoeff*coldWaterTemperature[i] + TaCoeff*dryBulbTemperatureData[i] + atHomeCoeff*numberOfAdultsAtHome + winterCoeff*winter + springCoeff*spring + summerCoeff*summer + autumnCoeff*autumn - dishWasherCoeff - clothsWasherCoeff) * seniorCoeff * payUtilityBillCoeff  # in liters/hour
            if HWC < 0:
                HWC = 0
            # thermal energy (or electric energy) per hour
            HWC_m3 = HWC/1000  # m3(per hour)
            waterSpecificHeat = 4.18  # kJ/(kg*C)
            waterDensity = 1000  # kg/m3
            Qload_kJ = HWC_m3 * waterDensity * waterSpecificHeat * (deliveryWaterTemperature-coldWaterTemperature[i])  #kJ
            Qload_kWh = Qload_kJ/3600  # kWh
        
        hotWaterPerHour.append(HWC)  # in liters/hour
        heatingLoadPerHour.append(Qload_kWh)  # in kWh
        hotWaterPerDays[day-1].append(HWC)
    
    hotWaterPerYear = sum(hotWaterPerHour[7:])  # in liters
    averageDailyHotWaterPerYear = sum(hotWaterPerHour[7:])/365  # in liters/day
    
    # maximumDailyConsumption, maximumConsumptionDay, minimumDailyConsumption, minimumConsumptionDay
    dayForMonths = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365, 700]
    hotWaterPerDaySum = [(sum(monthDays),i+1) for i,monthDays in enumerate(hotWaterPerDays)]
    hotWaterPerDaySum.sort()
    maximumDailyConsumption = hotWaterPerDaySum[-1][0]
    maximumDayInYear = hotWaterPerDaySum[-1][1]
    minimumDailyConsumption = hotWaterPerDaySum[0][0]
    minimumDayInYear = hotWaterPerDaySum[0][1]
    
    for i,day in enumerate([maximumDayInYear, minimumDayInYear]):
        for k,item in enumerate(dayForMonths):
            if day >= dayForMonths[k]+1 and day <= dayForMonths[k+1]:
                if i == 0:
                    maximumDay = day - dayForMonths[k]
                    maximumMonth = k+1
                if i == 1:
                    minimumDay = day - dayForMonths[k]
                    minimumMonth = k+1
    
    dayMonthHourMaximum = lb_preparation.hour2Date(lb_preparation.date2Hour(maximumMonth, maximumDay, 1))
    splittedDayMonthHour = dayMonthHourMaximum.split(" ")
    maximumConsumptionDay = splittedDayMonthHour[0] + " " + splittedDayMonthHour[1]
    dayMonthHourminimum = lb_preparation.hour2Date(lb_preparation.date2Hour(minimumMonth, minimumDay, 1))
    splittedDayMonthHour = dayMonthHourminimum.split(" ")
    minimumConsumptionDay = splittedDayMonthHour[0] + " " + splittedDayMonthHour[1]
    
    return heatingLoadPerHour, hotWaterPerHour, hotWaterPerYear, averageDailyHotWaterPerYear, maximumDailyConsumption, maximumConsumptionDay, minimumDailyConsumption, minimumConsumptionDay


def printOutput(locationName, totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, holidayDays, deliveryWaterTemperature, coldWaterTemperature):
    TinletAverageAnnual_C = sum(coldWaterTemperature)/len(coldWaterTemperature)
    resultsCompletedMsg = "Residential hot water results successfully calculated!"
    printOutputMsg = \
    """
Input data:

Location: %s

Total number of persons: %s
Number of preschool children: %s
Number of school children: %s
Number of adults: %s
Number of adults at home: %s
Senior only: %s
Own dishwasher: %s
Own cloths washer: %s
Pay utility bill: %s

First week start day: %s
Weekend days: %s
Holiday days: %s
Delivery water temperature (C): %0.2f
Annual average cold water temperature (C): %0.2f
    """ % (locationName, totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, holidayDays, deliveryWaterTemperature, TinletAverageAnnual_C)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        if _epwFile:
            locationName, latitude, dryBulbTemperatureData, daysHOY, hoursHOY, validEpwData, printMsg = getEpwData(_epwFile)
            if validEpwData:
                totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, tankSize, validInputData, printMsg = checkInputData(_totalNumberOfPersons, numberOfPreSchoolChildren_, numberOfSchoolChildren_, numberOfAdults_, numberOfAdultsAtHome_, seniorOnly_, dishWasher_, clothsWasher_, payUtilityBill_, firstWeekStartDay_, weekendDays_, holidayDays_, deliveryWaterTemperature_, coldWaterTemperaturePerHour_, dryBulbTemperatureData)
                if validInputData:
                    # all inputs ok
                    if _runIt:
                        heatingLoadPerHour, hotWaterPerHour, hotWaterPerYear, averageDailyHotWaterPerYear, maximumDailyConsumption, maximumConsumptionDay, minimumDailyConsumption, minimumConsumptionDay = main(totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, tankSize, dryBulbTemperatureData, coldWaterTemperature, daysHOY, hoursHOY, latitude)
                        printOutput(locationName, totalNumberOfPersons, numberOfPreSchoolChildren, numberOfSchoolChildren, numberOfAdults, numberOfAdultsAtHome, seniorOnly, dishWasher, clothsWasher, payUtilityBill, firstWeekStartDay, weekendDays, holidayDays, deliveryWaterTemperature, coldWaterTemperature)
                    else:
                        print "All inputs are ok. Please set the \"_runIt\" to True, to run the Domestic hot water component."
                else:
                    print printMsg
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please supply .epw file path to \"_epwFile\" input."
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        printMsg = "You need a newer version of Ladybug to use this component." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag the Ladybug_Ladybug component " + \
            "into the canvas and try again."
        print printMsg
else:
    printMsg = "First please let the Ladybug fly..."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)