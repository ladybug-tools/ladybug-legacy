# Commercial, public, apartment hot water
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Djordje Spasic <djordjedspasic@gmail.com> 
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
Use this component to calculate domestic hot water consumption for each hour during a year, for Commercial, Public and Apartment buildings.
The following types of buildings are supported:
-
- office
- apartment house or multifamily building
- hotel/motel
- restaurants, cafeterias
- drive-ins, grilles, luncheonettes, sandwich, snack shops
- primary school
- junior and senior high school
- men's dormitory
- women's dormitory
- hospital
- nursing home
- factory
-
Component based on paper: ASHRAE 2003 Applications Handbook (SI), Chapter 49, Service water heating:
https://cours.etsmtl.ca/mec735/Documents/Notes_de_cours/2012/Hiver_2012/Service_Water_heating_ASHRAE.pdf
-
Provided by Ladybug 0.0.65
    
    input:
        _epwFile: Input .epw file path by using grasshopper's "File Path" component.
        _buildingType: Choose the building type for which hot water consumption will be calculated:
                       -
                       0 - office
                       1 - apartment house, with 20 or less apartments
                       2 - apartment house, from 21 to 49 apartments
                       3 - apartment house, from 50 to 74 apartments
                       4 - apartment house, from 75 to 99 apartments
                       5 - apartment house, from 100 to 199 apartments
                       6 - apartment house, more than 200 apartments
                       7 - hotel/motel with 20 or less rooms
                       8 - hotel/motel from 21 to 60 rooms 
                       9 - hotel/motel from 61 to 99 rooms
                       10 - hotel/motel more than 100 rooms
                       11 - (full meal) restaurants, cafeterias
                       12 - drive-ins, grilles, luncheonettes, sandwich, snack shops
                       13 - primary school
                       14 - junior and senior high school
                       15 - men's dormitory
                       16 - women's dormitory
                       17 - hospital
                       18 - nursing home
                       19 - factory
        _numberOfUnits: Number of units for upper chosen "_buildingType". Represents the number of:
                        -
                        - apartment units:  apartment houses
                        - rooms: hotel/motel
                        - occupants:  offices, elementary, junior, senior high schools, dormitories , hospitals, factories
                        - meals per day:  (full meal) restaurants, cafeterias; drive-ins, grilles, luncheonettes, sandwich, snack shops
                        - beds:  nursing homes
        litersPerUnitPerDay_: Number of liters for a single unit and day, based on _buidlingType
                              -
                              office -  3.8 l/day/occupant
                              apartment house, with 20 or less apartments -  170 l/day/apartment
                              apartment house, from 21 to 49 apartments -  159.2 l/day/apartment
                              apartment house, from 50 to 74 apartments -  151.6 l/day/apartment
                              apartment house, from 75 to 99 apartments -  144 l/day/apartment
                              apartment house, from 100 to 199 apartments -  140.2 l/day/apartment
                              apartment house, more than 200 apartments -  132.7 l/day/apartment
                              hotel/motel with 20 or less rooms -  98 l/day/room
                              hotel/motel from 21 to 59 rooms -  75.8 l/day/room
                              hotel/motel from 60 to 99 rooms -  53.1 l/day/room
                              hotel/motel more than 100 rooms -  37.9 l/day/room
                              (full meal) restaurants, cafeterias -  9.1 l/day/meal
                              drive-in, grille, luncheonette, sandwich, snack shop - 2.6 l/day/meal
                              primary school -  2.3 l/day/pupil
                              junior and senior high school -  6.8 l/day/pupil
                              men's dormitory -  49.7 l/day/student
                              women's dormitory -  46.6 l/day/student
                              hospital -  160 l/day/patient
                              nursing home -  69.7 l/day/bed
                              factory -  45 l/day/worker
                              -
                              If not supplied, it will be picked based on chosen "_buildingType" and "_numberOfUnits" inputs.
        occupancyStartingHour_: An hour (from 1 to 24) during a day at which the occupancy of the chosen _buildingType starts:
                                -
                                office -  9
                                apartment house 7
                                hotel/motel 7
                                (full meal) restaurant, cafeteria -  7
                                drive-in, grill, luncheonette, sandwich, snack shop - 7
                                primary school -  9
                                junior and senior high school -  9
                                men's dormitory -  8
                                women's dormitory -  8
                                hospital -  1
                                nursing home -  1
                                factory -  1
                                -
                                If not supplied, it will be picked based on chosen "_buildingType" input.
        occupancyDuration_: Total number of hours in a single day during which the chosen _buildingType will be used.
                            It can not be less than 1 nor larger than 24. Also it can not exceed the 24 when summed with occupancyStartingHour_.
                            -
                            office -  9
                            apartment house -  15
                            hotel/motel -  8
                            (full meal) restaurant, cafeteria -  12
                            drive-in, grill, luncheonette, sandwich, snack shop - 17
                            primary school -  7
                            junior and senior high school -  7
                            men's dormitory -  15
                            women's dormitory -  15
                            hospital -  24
                            nursing home -  24
                            factory -  24
                            -
                            If not supplied, it will be picked based on chosen "_buildingType" input.
        firstWeekStartDay_: Week day on which a year starts (1 - Monday, 2 - Tuesday, 3 - Wednesday...)
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
                      If not supplied, no holiday days will be used, with exception of "school" (_buildingType: 13 and 14) where summer, winter and spring/autumn holidays will be applied.
                      For northern hemisphere, USA school holidays schedules have been taken as a default.
                      For southern hemisphere, Australian school holidays schedule have been taken as a default.
        deliveryWaterTemperature_: Required water temperature. In Celsius
                                   It is recommended for delivery water temperature to not be lower than 60C (140F) to avoid the risk of Legionella pneumophila bacteria appearance.
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

ghenv.Component.Name = "Ladybug_Commercial Public Apartment Hot Water"
ghenv.Component.NickName = "CommercialPublicApartmentHotWater"
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
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


def checkInputData(buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, holidayDays, deliveryWaterTemperature, dryBulbTemperatureData, coldWaterTemperaturePerHour):
    
    if (buildingType == None):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
        validInputData = False
        printMsg = "Please input \"_buildingType\"."
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    
    elif (buildingType < 0) or (buildingType > 19):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
        validInputData = False
        printMsg = "\"_buildingType\" input can not be less than 0 or larger than 19. Please input a number between 0 and 19."
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    
    
    if (numberOfUnits == None):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
        validInputData = False
        printMsg = "Please input \"_numberOfUnits\"."
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    
    elif (numberOfUnits <= 0):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
        validInputData = False
        printMsg = "\"_numberOfUnits\" input can not be equal or less than 0. Please input a number of units larger than 0."
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    
    
    if (litersPerUnitPerDay == None):
        litersPerUnitPerDay_per_buildingType = [3.8, 170, 159.2, 151.6, 144, 140.2, 132.7, 98, 75.8, 53.1, 37.9, 9.1, 2.6, 2.3, 6.8, 49.7, 46.6, 160, 69.7, 45]  # in liters/unit per day
        litersPerUnitPerDay = litersPerUnitPerDay_per_buildingType[buildingType]
    
    elif (litersPerUnitPerDay <= 0):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
        validInputData = False
        printMsg = "\"litersPerUnitPerDay_\" input can not be equal or less than 0. Please input a number of liters larger than 0."
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    
    
    if (occupancyStartingHour == None):
        occupancyStartingHour_per_buildingType = [9, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 9, 9, 8, 8, 1, 1, 1]
        occupancyStartingHour = occupancyStartingHour_per_buildingType[buildingType]
    
    elif (occupancyStartingHour < 1) or (occupancyStartingHour > 24):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
        validInputData = False
        printMsg = "\"occupancyStartingHour_\" input can not be less than 1 or larger than 24. Please input an occupancyStartingHour from 1 to 24."
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    
    
    if (occupancyDuration == None):
        occupancyDuration_per_buildingType = [9, 15, 15, 15, 15, 15, 15, 8, 8, 8, 8, 12, 17, 7, 7, 15, 15, 24, 24, 24]
        occupancyDuration = occupancyDuration_per_buildingType[buildingType]
    
    elif (occupancyDuration <= 0) or (occupancyStartingHour + occupancyDuration > 24):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
        validInputData = False
        printMsg = "\"occupancyDuration_\" input can not be less than 1 and can not exceed 24 hours."
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    
    
    if (firstWeekStartDay == None):
        firstWeekStartDay = 1  # default, Monday
    
    elif (firstWeekStartDay < 1) or (firstWeekStartDay > 7):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
        validInputData = False
        printMsg = "\"weekendDays_\" input can not be less than 1 or larger than 7. Please input two weekendDays_ numbers from 1 to 7."
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    
    if (len(weekendDays) == 0):
        weekendDays = [6,7]  # default, Saturday, Sunday
        firstWeekSubtractWeekends = 0
    elif (len(weekendDays) != 2):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
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
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    elif (weekendDays[0] < 1) or (weekendDays[1] < 1) or (weekendDays[0] > 7) or (weekendDays[1] > 7):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
        validInputData = False
        printMsg = "\"weekendDays_\" input can not be less than 1 or larger than 7. Please input two weekendDays_ numbers from 1 to 7."
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
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
            buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
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
            
            return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    
    
    if (len(holidayDays) == 0):
        if (buildingType == 13) or (buildingType == 14):
            if latitude >= 0:
                # northern hemisphere
                holidayDays = [1, 2, 3, 84, 85, 86, 87, 88, 89, 90, 91, 92, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 358, 359, 360, 361, 362, 363, 364, 365]  # default for US primary school; junior and senior high school
            elif latitude < 0:
                # southern hemishere
                holidayDays = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365]  # default for New Sout Wales primary school; junior and senior high school
        else:
            #for all other buildingType:
            holidayDays = []  # default
    elif (holidayDays[0] < 1) or (holidayDays[1] < 1) or (holidayDays[0] > 365) or (holidayDays[1] > 365):
        buildingType = numberOfUnits = litersPerUnitPerDay = occupancyStartingHour = occupancyDuration = firstWeekStartDay = weekendDays = firstWeekSubtractWeekends =  holidayDays = deliveryWaterTemperature = coldWaterTemperature = None
        validInputData = False
        printMsg = "\"holidayDays_\" input can not be less than 1 or larger than 365. Please input a holidayDays_ number from 1 to 365."
        
        return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg
    
    
    if (deliveryWaterTemperature == None) or (deliveryWaterTemperature < 0):
        deliveryWaterTemperature = 60  # default
    
    if (len(coldWaterTemperaturePerHour) == 0) or (coldWaterTemperaturePerHour[0] is ""):
        method = 1; minimalTemperature = 1  # default: method 1 (Christensen and Burch), with fixed pipes depth from 0.3 to 1 meters, and unknown soil type.
        coldWaterTemperature, coldWaterTemperaturePerYear, TcoldHOYminimal, TcoldHOYmaximal = lb_photovoltaics.inletWaterTemperature(dryBulbTemperatureData, method, minimalTemperature)
    elif (len(coldWaterTemperaturePerHour) == 8767):
        coldWaterTemperature = coldWaterTemperaturePerHour[7:]
    elif (len(coldWaterTemperaturePerHour) == 8760):
        coldWaterTemperature = coldWaterTemperaturePerHour
    
    validInputData = True
    printMsg = "ok"
    
    return buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg


def main(buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, daysHOY, hoursHOY, latitude):
    
    hotWaterPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Domestic hot water load", "L/h", "Hourly", (1, 1, 1), (12, 31, 24)]
    heatingLoadPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Domestic hot water heating load", "kWh", "Hourly", (1, 1, 1), (12, 31, 24)]
    hotWaterPerDays = [[] for i in range(365)]
    firstWeekLength = (8 - firstWeekSubtractWeekends) - firstWeekStartDay
    epwFileHour = occupancyStartingHour + 1
    workingHours = range(epwFileHour, epwFileHour + occupancyDuration)
    
    for i,day in enumerate(daysHOY):  # len 8760
        hour = hoursHOY[i]
        if day in holidayDays:
            # it's holiday day
            HWC = 0
            Qload = 0
        elif ((day-firstWeekLength+1)%7 == 0) or ((day-firstWeekLength)%7 == 0):
            # it's weekend day
            HWC = 0
            Qload = 0
        else:
            # it's week day
            if hour in workingHours:
                # working hour
                HWC = (litersPerUnitPerDay/occupancyDuration) * numberOfUnits  # liters/hour
            else:
                # non working hour
                HWC = 0
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
    
    hotWaterPerYear = sum(hotWaterPerHour[7:])
    averageDailyHotWaterPerYear = sum(hotWaterPerHour[7:])/365
    
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


def printOutput(locationName, buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, holidayDays, deliveryWaterTemperature, coldWaterTemperature):
    units = ["occupant", "apartment", "apartment", "apartment", "apartment", "apartment", "apartment", "room", "room", "room", "room", "meal", "meal", "pupil", "pupil", "student", "student", "patient", "bed", "worker"]
    TinletAverageAnnual_C = sum(coldWaterTemperature)/len(coldWaterTemperature)
    resultsCompletedMsg = "Hot water results successfully calculated!"
    printOutputMsg = \
    """
Input data:

Location: %s

Building type: %s
Number of units: %s
Liters/%s/day: %s
Occupancy starting hour: %s
Occupancy duration: %s

First week start day: %s
Weekend days: %s
Holiday days: %s
Delivery water temperature (C): %0.2f
Annual average cold water temperature (C): %0.2f
    """ % (locationName, buildingType, numberOfUnits, units[buildingType], litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, holidayDays, deliveryWaterTemperature, TinletAverageAnnual_C)
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
                buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, validInputData, printMsg = checkInputData(_buildingType, _numberOfUnits, litersPerUnitPerDay_, occupancyStartingHour_, occupancyDuration_, firstWeekStartDay_, weekendDays_, holidayDays_, deliveryWaterTemperature_, dryBulbTemperatureData, coldWaterTemperaturePerHour_)
                if validInputData:
                    # all inputs ok
                    if _runIt:
                        heatingLoadPerHour, hotWaterPerHour, hotWaterPerYear, averageDailyHotWaterPerYear, maximumDailyConsumption, maximumConsumptionDay, minimumDailyConsumption, minimumConsumptionDay = main(buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, firstWeekSubtractWeekends, holidayDays, deliveryWaterTemperature, coldWaterTemperature, daysHOY, hoursHOY, latitude)
                        printOutput(locationName, buildingType, numberOfUnits, litersPerUnitPerDay, occupancyStartingHour, occupancyDuration, firstWeekStartDay, weekendDays, holidayDays, deliveryWaterTemperature, coldWaterTemperature)
                    else:
                        print "All inputs are ok. Please set the \"_runIt\" to True, to run the Hot water component."
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