# thermal comfort indices
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Djordje Spasic <djordjedspasic@gmail.com>
# with assistance of Dr. Krzysztof Blazejczyk <k.blaz@twarda.pan.pl>
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
Use this component to calculate various thermal comfort indices:
------
- HI (Heat Index)
- humidex (humidity index)
- DI (Discomfort Index)
- WCI (Wind Chill Index)
- WCT (Wind Chill Temperature)
- WBGT (Wet-Bulb Globe Temperature) indoors
- WBGT (Wet-Bulb Globe Temperature) outdoors
- TE (Effective Temperature)
- AT (Apparent Temperature)
- TS (Thermal Sensation)
- ASV (Actual Sensation Vote)
- MRT (Mean Radiant Temperature)
- Iclp (Predicted Insulation Index Of Clothing)
- HR (Heart Rate)
- DhRa (Dehydration Risk)
- PET (Physiological Equivalent Temperature)
- THI (Temperature Humidity Index)
- PHS (Predicted Heat Strain)
-
Provided by Ladybug 0.0.63
    
    input:
        _comfortIndex: Choose one of the comfort indices:
                       0 - HI (Heat Index)
                       1 - humidex (humidity index)
                       2 - DI (Discomfort Index)
                       3 - WCI (Wind Chill Index)
                       4 - WCT (Wind Chill Temperature)
                       5 - WBGT (Wet-Bulb Globe Temperature) indoors
                       6 - WBGT (Wet-Bulb Globe Temperature) outdoors
                       7 - TE (Effective Temperature)
                       8 - AT (Apparent Temperature)
                       9 - TS (Thermal Sensation)
                       10 - ASV (Actual Sensation Vote)
                       11 - MRT (Mean Radiant Temperature)
                       12 - Iclp (Predicted Insulation Index Of Clothing)
                       13 - HR (Heart Rate)
                       14 - DhRa (Dehydration Risk)
                       15 - PET (Physiological Equivalent Temperature) for temperate climates
                       16 - PET (Physiological Equivalent Temperature) for tropical and subtropical humid climates
                       17 - THI (Temperature Humidity Index)
                       18 - PHS (Predicted Heat Strain)
        _location: Input data from Ladybug's "Import epw" "location" output, or create your own location data with Ladybug's "Construct Location" component.
        _dryBulbTemperature: Air temperature.
                             Input a single value or a whole list from "Import epw" component's "dryBulbTemperature" output.
                             -
                             In Celsius degrees (C).
        meanRadiantTemperature_: An average temperature of the surfaces that surround the analysis location.
                                 For indoor conditions or outdoor in-shade, it should be equal to air temperature. So just input the same data you inputted to "_dryBulbTemperature".
                                 -
                                 If nothing supplied, it will be calculated for outdoor conditions (both in-shade and out-shade).
                                 -
                                 In Celsius degrees (C).
        dewPointTemperature_: Dew point temperature.
                              Input a single value or a whole list from "Import epw" component's "dewPointTemperature" output.
                              -
                              If not supplied, it will be calculated from _dryBulbTemperature and relativeHumidity_ data.
                              -
                              In Celsius degrees (C).
        relativeHumidity_: Relative humidity.
                           Input a single value or a whole list from "Import epw" component's "relativeHumidity" output.
                           -
                           If not supplied 50% will be used as a default (indoor conditions).
                           -
                           In percent (from 0% to 110%).
        windSpeed_: Wind speed at 1.1 meters height from analysis surface (height of standing person’s gravity center). It can be a single value or a list of values.
                    Take the "windSpeed" output from "Import epw" component and plug it to "Wind Speed Calculator" component's "_windSpeed_tenMeters" input. Set the "heightAboveGround_" input to "1.1". Then plug in the data from "Wind Speed Calculator" component's "windSpeedAtHeight" output to this component's "windSpeed_" input.
                    In this way we converted the 10 meter wind speed from the .epw file to required 1.1m.
                    -
                    If not supplied, default value of 0.3 m/s is used (meaning: the analysis is conducted in outdoor no wind conditions, or indoor conditions).
                    -
                    In meters/second.
        totalSkyCover_: Amount of sky dome covered by clouds.
                        Input a single value or a whole list from "Import epw" component's "totalSkyCover" output.
                        It ranges from from 1 to 10. For example: 1 is 1/10 covered. 10 is total coverage (10/10).
                        -
                        If not supplied 6/10 will be used (cloud coverage of temperate humid climate).
                        -
                        In tenths of sky cover.
        solarRadiationPerHour_:  Amount of solar radiation that an analysis person received.
                                 -
                                 1) If you would like to do an analysis accounted for shading (more precise) use the "Sunpath shading" component and its "shadedSolarRadiationPerHour" output.
                                 Or use "Radiation Analysis" component's "radiationResult" output. Be sure to scale the "radiationResult" output data 1000 times (to convert it from kW/m2 to W/m2).
                                 The "Sunpath shading" component will account for partial shading from the trees, while "Radiation Analysis" will not.
                                 -
                                 2) If you would not like to do an analysis accounted for shading (because it's quicker that way), then you can simply supply the data from "Import epw" component's "diffuseHorizontalRadiation" output. In this way it will be assumed that an analysis is being conducted in outdoor in-shade conditions, or indoor conditions.
                                 -
                                 If nothing supplied, default value of 0 Wh/m2 will be used (no solar radiation at all).
                                 -
                                 In Wh/m2.
        bodyCharacteristics_: A list of body characteristics in the following order: age, sex, height, weight, bodyPosition, clothingInsulation, acclimated, metabolicRate, activityDuration.
                              Use Ladybug's "Body Characteristics" component to generate it.
                              -
                              If not supplied, the following default values will be used:
                              --
                              35 - age
                              "male" - sex
                              175 - height in centimeters
                              75 - weight in kilograms
                              "standing" - bodyPosition
                              None (clothingInsulation - "None" means that it will be calculated based on air temperature)
                              37 - clothingAlbedo in % (for medium colored clothes)
                              "unacclimated" - acclimated
                              2.32 - metabolicRate in mets (2.32 corresponds to walking 4km/h)
                              480 - activityDuration in minutes
        HOY_: An hour (or hours) of the year for which you would like to calculate thermal indices. These hours must be a value between 1 and 8760.
              This input will override the analysisPeriod_ input below.
              -
              If not supplied, this input will be ignored.
        analysisPeriod_: An optional analysis period from the "Analysis Period" component.
                         -
                         If not supplied, the whole year period will be used as an analysis period.
        _runIt: ...
        
    output:
        readMe!: ...
        comfortIndexValue: The value of the chosen comfort.
        comfortIndexLevel: The level (category, sensation) of the chosen index.
        comfortableOrNot: Indication of whether that person is comfortable (1) or not (0) at particular hour.
        percentComfortable: Percentage of time, during which chosen index falls into the comfortable category.
        percentHotExtreme: Percentage of time, during which chosen index falls into the hot extreme category.
        percentColdExtreme: Percentage of time, during which chosen index falls into the cold extreme category.
"""

ghenv.Component.Name = "Ladybug_Thermal Comfort Indices"
ghenv.Component.NickName = "ThermalComfortIndices"
ghenv.Component.Message = "VER 0.0.64\nFEB_12_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.64\nFEB_12_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
import math


def getLocationData(location):
    
    if location:
        try:
            locationName, latitude, longitude, timeZone, elevation = lb_preparation.decomposeLocation(location)
            latitude, longitude, timeZone = float(latitude), float(longitude), float(timeZone)
            
            validLocationData = True
            printMsg = "ok"
        
        except:
            # something is wrong with "_location" input (the input is not from Ladybug "Import epw" component's "location" ouput)
            locationName = latitude = longitude = timeZone = None
            validLocationData = False
            printMsg = "Something is wrong with \"_location\" input."
    else:
        locationName = latitude = longitude = timeZone = None
        validLocationData = False
        printMsg = "Please input \"location\" ouput from Ladybug \"Import epw\" component, or make your own location data by using Ladybug's \"Contruct Location\" and plug it into \"_location\" input of this component."
    
    return locationName, latitude, longitude, timeZone, validLocationData, printMsg


def averageWeatherData(hourlyData, activityDuration):
    # average weather data for the last activityDuration hours
    activityDurationHours = int(activityDuration/60)
    activityDurationValues = activityDurationHours - 1
    hourlyDataShifted = hourlyData[-activityDurationValues:] + hourlyData[:]
    
    lastActivityDurationHoursAverageL = [sum(hourlyDataShifted[i:activityDurationHours+i])/activityDurationHours for i in range(8760)]
    
    return lastActivityDurationHoursAverageL


def getWeatherData(latitude, longitude, timeZone, Ta, mrt, Tdp, rh, ws, SR, N, bodyCharacteristics, HOY, analysisPeriod):
    
    # required input: Ta
    if (len(Ta) == 0) or (Ta[0] is ""):
        TaL = mrtL_calculated = TdpL = rhL = wsL = SRL = NL = TgroundL = RprimL = vapourPressureL = EpotL = HOYs = date = newAnalysisPeriod = age = sex = heightCM = heightM = weight = bodyPosition = IclL = ac = acclimated = ML = activityDuration = None
        printMsg = "Please input _dryBulbTemperature. As a single value, or as a list from \"Import EPW\" component."
        validWeatherData = False
        return TaL, mrtL_calculated, TdpL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, ac, acclimated, ML, activityDuration, validWeatherData, printMsg
    elif (len(Ta) == 8767):
        TaL = Ta[7:]
    elif (len(Ta) == 8760):
        TaL = Ta
    elif (len(Ta) == 1):
        TaL = [float(Ta[0]) for i in range(8760)]
    else:
        TaL = mrtL_calculated = TdpL = rhL = wsL = SRL = NL = TgroundL = RprimL = vapourPressureL = EpotL = HOYs = date = newAnalysisPeriod = age = sex = heightCM = heightM = weight = bodyPosition = IclL = ac = acclimated = ML = activityDuration = None
        printMsg = "_dryBulbTemperature input can only be a single value, or a list of 8760 (without the Ladybug header) or 8767 (with Ladybug header) values.\nSo input a single value, or the \"dryBulbTemperature\" list from \"Import EPW\" component."
        validWeatherData = False
        return TaL, mrtL_calculated, TdpL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, ac, acclimated, ML, activityDuration, validWeatherData, printMsg
    
    
    if (len(mrt) == 0) or (mrt[0] is ""):
        mrtL = ["calculate_MRT"]  # calculate mrtL
    elif (len(mrt) == 8767):
        mrtL = mrt[7:]
    elif (len(mrt) == 8760):
        mrtL = mrt
    elif (len(mrt) == 1):
        mrtL = [float(mrt[0]) for i in range(8760)]
    else:
        TaL = mrtL = mrtL = rhL = wsL = SRL = NL = TgroundL = RprimL = vapourPressureL = EpotL = HOYs = date = newAnalysisPeriod = age = sex = heightCM = heightM = weight = bodyPosition = IclL = acclimated = ML = activityDuration = None
        printMsg = "meanRadiantTemperature_ input can only be a single value, or a list of 8760 (without the Ladybug header) or 8767 (with Ladybug header) values.\nSo input a single value, or the list.\nIf nothing supplied, it will be calculated automatically."
        validWeatherData = False
        return TaL, mrtL, mrtL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, acclimated, ML, activityDuration, validWeatherData, printMsg
    
    
    if (len(rh) == 0) or (rh[0] is ""):
        rhL = [50 for i in range(8760)]  # default 50%, indoor condition
    elif (len(rh) == 8767):
        rhL = rh[7:]
    elif (len(rh) == 8760):
        rhL = rh
    elif (len(rh) == 1):
        rhL = [float(rh[0]) for i in range(8760)]
    else:
        TaL = mrtL_calculated = TdpL = rhL = wsL = SRL = NL = TgroundL = RprimL = vapourPressureL = EpotL = HOYs = date = newAnalysisPeriod = age = sex = heightCM = heightM = weight = bodyPosition = IclL = ac = acclimated = ML = activityDuration = None
        printMsg = "relativeHumidity_ input can only be a single value, or a list of 8760 (without the Ladybug header) or 8767 (with Ladybug header) values.\nSo input a single value, or the \"relativeHumidity\" list from \"Import EPW\" component."
        validWeatherData = False
        return TaL, mrtL_calculated, TdpL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, ac, acclimated, ML, activityDuration, validWeatherData, printMsg
    
    
    if (len(Tdp) == 0) or (Tdp[0] is ""):
        TdpL = [dewPointTemperature(TaL[i],rhL[i]) for i in range(8760)]  # calculate TdpL
    elif (len(Tdp) == 8767):
        TdpL = Tdp[7:]
    elif (len(Tdp) == 8760):
        TdpL = Tdp
    elif (len(Tdp) == 1):
        TdpL = [float(Tdp[0]) for i in range(8760)]
    else:
        TaL = mrtL_calculated = TdpL = rhL = wsL = SRL = NL = TgroundL = RprimL = vapourPressureL = EpotL = HOYs = date = newAnalysisPeriod = age = sex = heightCM = heightM = weight = bodyPosition = IclL = ac = acclimated = ML = activityDuration = None
        printMsg = "dewPointTemperature_ input can only be a single value, or a list of 8760 (without the Ladybug header) or 8767 (with Ladybug header) values.\nSo input a single value, or the \"dewPointTemperature\" list from \"Import EPW\" component."
        validWeatherData = False
        return TaL, mrtL_calculated, TdpL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, ac, acclimated, ML, activityDuration, validWeatherData, printMsg
    
    
    if (len(ws) == 0) or (ws[0] is ""):
        wsL = [0.3 for i in range(8760)]  # default 0.3 m/s: no wind
    elif (len(ws) == 8767):
        wsL = ws[7:]
    elif (len(ws) == 8760):
        wsL = ws
    elif (len(ws) == 1):
        wsL = [float(ws[0]) for i in range(8760)]
    else:
        TaL = mrtL_calculated = TdpL = rhL = wsL = SRL = NL = TgroundL = RprimL = vapourPressureL = EpotL = HOYs = date = newAnalysisPeriod = age = sex = heightCM = heightM = weight = bodyPosition = IclL = ac = acclimated = ML = activityDuration = None
        printMsg = "windSpeed_ input can only be a single value, or a list of 8760 (without the Ladybug header) or 8767 (with Ladybug header) values.\nSo input a single value, or the \"windSpeed\" list from \"Import EPW\" component."
        validWeatherData = False
        return TaL, mrtL_calculated, TdpL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, ac, acclimated, ML, activityDuration, validWeatherData, printMsg
    
    
    if (len(N) == 0) or (N[0] is ""):
        NL = [6 for i in range(8760)]  # default 6 tens, continental humid climate
    elif (len(N) == 8767):
        NL = N[7:]
    elif (len(N) == 8760):
        NL = N
    elif (len(N) == 1):
        NL = [float(N[0]) for i in range(8760)]
    else:
        TaL = mrtL_calculated = TdpL = rhL = wsL = SRL = NL = TgroundL = RprimL = vapourPressureL = EpotL = HOYs = date = newAnalysisPeriod = age = sex = heightCM = heightM = weight = bodyPosition = IclL = ac = acclimated = ML = activityDuration = None
        printMsg = "totalSkyCover_ input can only be a single value, or a list of 8760 (without the Ladybug header) or 8767 (with Ladybug header) values.\nSo input a single value, or the \"totalSkyCover\" list from \"Import EPW\" component."
        validWeatherData = False
        return TaL, mrtL_calculated, TdpL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, ac, acclimated, ML, activityDuration, validWeatherData, printMsg
    
    
    if (len(SR) == 0) or (SR[0] is "") or (SR[0] is None):
        SRL = [0 for i in range(8760)]  # default 0 Wh/m2: no solar radiation
    elif (len(SR) == 8767):
        SRL = SR[7:]
    elif (len(SR) == 8760):
        SRL = SR
    elif (len(SR) == 1):
        SRL = [float(SR[0]) for i in range(8760)]
    else:
        TaL = mrtL_calculated = TdpL = rhL = wsL = SRL = NL = TgroundL = RprimL = vapourPressureL = EpotL = HOYs = date = newAnalysisPeriod = age = sex = heightCM = heightM = weight = bodyPosition = IclL = ac = acclimated = ML = activityDuration = None
        printMsg = "solarRadiationPerHour_ input can only be a single value, or a list of 8760 (without the Ladybug header) or 8767 (with Ladybug header) values.\nSo either input a single value, or:\n" + \
                   " \n" + \
                   "1) If you would like to do an analysis accounted for shading (more precise) use the \"Sunpath shading\" component and its \"shadedSolarRadiationPerHour\" output.\n" + \
                   " \n" + \
                   "2) If you would not like to do an analysis accounted for shading (because it's quicker that way), then you can supply the data from \"Import epw\" component's \"diffuseHorizontalRadiation\" output.\n" + \
                   "In this simplified way it will be assumed that an analysis is being conducted in outdoor in-shade conditions, or indoor conditions."
        validWeatherData = False
        return TaL, mrtL_calculated, TdpL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, ac, acclimated, ML, activityDuration, validWeatherData, printMsg
    
    
    # bodyCharacteristics
    if (len(bodyCharacteristics) != 10) and (len(bodyCharacteristics) != 0):
        TaL = mrtL_calculated = TdpL = rhL = wsL = SRL = NL = TgroundL = RprimL = vapourPressureL = EpotL = HOYs = date = newAnalysisPeriod = age = sex = heightCM = heightM = weight = bodyPosition = IclL = ac = acclimated = ML = activityDuration = None
        validWeatherData = False
        printMsg = "Your \"bodyCharacteristics_\" input is incorrect. Please use the \"bodyCharacteristics\" output from Ladybug's \"Body Characteristics\" component."
        return TaL, mrtL_calculated, TdpL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, ac, acclimated, ML, activityDuration, validWeatherData, printMsg
        
    elif (len(bodyCharacteristics) == 0) or (bodyCharacteristics[0] is ""):
        # nothing inputted into "bodyCharacteristics_", use default bodyCharacteristics values
        age = 35
        sex = "male"
        heightCM = 175  # in centimeters
        heightM = 1.75  # in meters
        weight = 75  # in kg
        bodyPosition = "standing"
        Icl = None  # it will be calculated based on air temperature
        ac = 37  # default in %, medium colored clothes
        acclimated = "unacclimated"
        Mmets = 2.32  # default value: 2.32 met = 135 W/m2
        activityDuration = 480  # in minutes
    elif (len(bodyCharacteristics) == 10):
        # 9 items inputted into "bodyCharacteristics_"
        age = bodyCharacteristics[0]
        sex = bodyCharacteristics[1]
        heightCM = bodyCharacteristics[2]
        heightM = heightCM/100
        weight = bodyCharacteristics[3]
        bodyPosition = bodyCharacteristics[4]
        Icl = bodyCharacteristics[5]
        ac = bodyCharacteristics[6]
        acclimated = bodyCharacteristics[7]
        Mmets = bodyCharacteristics[8]
        activityDuration = bodyCharacteristics[9]
    
    # check Icl and M from bodyCharacteristics
    if (Icl != None):
        # use "clothingInsulation" defined in "bodyCharacteristics_"
        IclL = [Icl for i in range(8760)]
    else:
        # nothing inputted to "bodyCharacteristics_" or something inputted to "bodyCharacteristics_" but "clothingInsulation" is not defined (equals to: None)
        IclL = [clothingInsulation(Ta) for Ta in TaL]
    
    if (Mmets == None) or (Mmets <= 0):
        Mmets = 2.32
    ML = [Mmets * 58.2 for i in range(8760)]  # convert mets to W/m2 (2.32 met = 2.32 * 58.2 = 135 W/m2)
    
    
    if _comfortIndex == 18:
        # for PHS, replace weather data with average weather data for the last activityDuration hours
        TaL = averageWeatherData(TaL, activityDuration)
        if mrtL[0] != "calculate_MRT":  # if meanRadiantTemperature_ inputted: average it
            mrtL = averageWeatherData(mrtL, activityDuration)
        else:
            pass
            # it will be averaged by using averaged data (TaL, rhL, SRL, NL)
        rhL = averageWeatherData(rhL, activityDuration)
        TdpL = averageWeatherData(TdpL, activityDuration)
        wsL = averageWeatherData(wsL, activityDuration)
        SRL = averageWeatherData(SRL, activityDuration)
        NL = averageWeatherData(NL, activityDuration)
        IclL = averageWeatherData(IclL, activityDuration)
    
    
    TgroundL = []; RprimL = []; vapourPressureL = []; EpotL = []; mrtL_calculated = []
    HOYs, daysDummy, monthsDummy, hoursDummy, date, newAnalysisPeriod = HOYsDaysMonthsHoursFromHOY_analysisPeriod(HOY, analysisPeriod)
    HOYsDummy, days, months, hours, dateDummy, newAnalysisPeriodDummy = HOYsDaysMonthsHoursFromHOY_analysisPeriod(None, [(1, 1, 1),(12, 31, 24)])
    for i in range(8760):
        Tground = groundTemperature(TaL[i], NL[i])  # in C
        solarZenithD, solarAzimuthD, solarAltitudeD = noaaSolarCalculator(latitude, longitude, timeZone, months[i], days[i], hours[i])  # in degrees
        Rprim = solarRadiationNudeMan(SRL[i], solarAltitudeD, ac)  # in W/m2
        vapourPressure = VapourPressure(TaL[i], rhL[i])  # in hPa
        if mrtL[0] == "calculate_MRT":
            mrt = meanRadiantTemperature(TaL[i], Tground, Rprim, vapourPressure, NL[i])  # in C
        else:
            mrt = mrtL[i]  # in C
        Ts = meanSkinTemperature(TaL[i], wsL[i], rhL[i], mrt, IclL[i], ML[i])  # in C
        e_ = VapourPressure(TaL[i], 5)  # in hPa
        Epot = turbulentExchangeOfLatentHeat(TaL[i], wsL[i], Ts, IclL[i], e_, ML[i])  # in W/m2
        TgroundL.append(Tground)
        RprimL.append(Rprim)
        vapourPressureL.append(vapourPressure)
        mrtL_calculated.append(mrt)
        EpotL.append(Epot)
    
    printMsg = "ok"
    validWeatherData = True
    
    return TaL, mrtL_calculated, TdpL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, ac, acclimated, ML, activityDuration, validWeatherData, printMsg


#angle units conversion
def degreesToRadians(deg):
    return deg*0.0174532925 

def radiansToDegrees(R):
    return R*57.2957795

# temperature units conversion
def celsiusToFahrenheit(Tc):
    Tf = (Tc * (9/5)) + 32
    return Tf

def fahrenheitToCelsius(Tf):
    Tc = (Tf-32)*(5/9)
    return Tc
    
def celsiusToKelvin(Tc):
    Tk = Tc + 273.15
    return Tk


# thermal comfort indices
def heatIndex(Ta, rh):
    # formula by (NWS) National Weather Service
    Tf = celsiusToFahrenheit(Ta)
    
    if Tf < 80:
        HI_f = 0.5 * (Tf + 61.0 + ((Tf-68.0)*1.2) + (rh*0.094))
    else:
        HI_f = -42.379 + 2.04901523*Tf + 10.14333127*rh - \
             0.22475541*Tf*rh -6.83783*(10**(-3))*(Tf**(2)) - \
             5.481717*(10**(-2))*(rh**(2)) + \
             1.22874*(10**(-3))*(Tf**(2))*(rh) + 8.5282*(10**(-4))*(Tf)*(rh**(2)) - \
             1.99*(10**(-6))*(Tf**(2))*(rh**(2))
        if (Tf >= 80) and (Tf <= 112) and (rh < 13):
            adjust = ((13-rh)/4) * math.sqrt((17-abs(Tf-95))/17)
            HI_f = HI_f-adjust
        elif (Tf >= 80) and (Tf <= 87) and (rh > 85):
            adjust = ((rh-85)/10) * ((87-Tf)/5)
            HI_f = HI_f+adjust
    
    if HI_f < 80:
        effectHI = 0
        comfortable = 1
    elif HI_f >= 80 and HI_f < 90:
        effectHI = 1
        comfortable = 0
    elif HI_f >= 90 and HI_f < 105:
        effectHI = 2
        comfortable = 0
    elif HI_f >= 105 and HI_f < 130:
        effectHI = 3
        comfortable = 0
    elif HI_f >= 130:
        effectHI = 4
        comfortable = 0
    
    HI_c = fahrenheitToCelsius(HI_f)
    
    return HI_c, effectHI, comfortable


def dewPointTemperature(Ta, rh):
    # MET4 and MET4A calculation of dew point temperature.
    # limits:
    # uncertainty in the calculated dew point temperature: +/- 0.4C
    # for Tc in range:  0C < Tc < 60C  
    # for Tdp in range:  0C < Tdp < 50C   
    a = 17.27
    b = 237.7
    rh = rh/100  # 0.01 < rh < 1.00
    Tdp = (b * ( ((a*Ta)/(b+Ta))+math.log(rh) ))/(a-( ((a*Ta)/(b+Ta))+math.log(rh) ))  # in Celius degrees
    
    return Tdp


def Humidex(Ta, Tdp):
    # formula by Environment Canada
    dewpointK = celsiusToKelvin(Tdp)  # to Kelvin
    e = 6.11 * math.exp(5417.7530 * ((1/273.16) - (1/dewpointK)))
    h = (0.5555)*(e - 10.0)
    humidex = Ta + h
    
    if humidex < 30:
        effectHumidex = 0
        comfortable = 1
    elif humidex >= 30 and humidex < 35:
        effectHumidex = 1
        comfortable = 0
    elif humidex >= 35 and humidex < 40:
        effectHumidex = 2
        comfortable = 0
    elif humidex >= 40 and humidex < 45:
        effectHumidex = 3
        comfortable = 0
    elif humidex >= 45 and humidex < 54:
        effectHumidex = 4
        comfortable = 0
    elif humidex >= 54:
        effectHumidex = 5
        comfortable = 0
    
    return humidex, effectHumidex, comfortable


def discomfortIndex(Ta, rh):
    # also called "Thom's Index"
    # formula from: Thom, E.C. (1959): The discomfort index. Weather wise, 12: 5760.
    DI = Ta - (0.55 - 0.0055*rh)*(Ta - 14.5)
    
    # categories by Kyle, 1994 in Unger, 1999
    if DI < -40:
        effectDI = -6
        comfortable = 0
    elif DI >= -40 and DI < -20:
        effectDI = -5
        comfortable = 0
    elif DI >= -20 and DI < -10:
        effectDI = -4
        comfortable = 0
    elif DI >= -10 and DI < -1.8:
        effectDI = -3
        comfortable = 0
    elif DI >= -1.8 and DI < 13:
        effectDI = -2
        comfortable = 0
    elif DI >= 13 and DI < 15:
        effectDI = -1
        comfortable = 0
    elif DI >= 15 and DI < 20:
        effectDI = 0
        comfortable = 1
    elif DI >= 20 and DI < 26.5:
        effectDI = 1
        comfortable = 0
    elif DI >= 26.5 and DI < 30:
        effectDI = 2
        comfortable = 0
    elif DI >= 30:
        effectDI = 3
        comfortable = 0
    
    return DI, effectDI, comfortable


def windChillIndex(Ta, ws):
    # formula by Gregorczuk 1976
    WCI = (10*math.sqrt(ws) + 10.45 - ws)*(33 - Ta)*1.163
    
    # Thermal sensations of man wearing clothing with insulation of 4 clo (heavy polar equipment):
    if WCI >= 2326:
        effectWCI = -4
        comfortable = 0
    elif WCI < 2326 and WCI >= 1628.2:
        effectWCI = -3
        comfortable = 0
    elif WCI < 1628.2 and WCI >= 930.4:
        effectWCI = -2
        comfortable = 0
    elif WCI < 930.4 and WCI >= 581.5:
        effectWCI = -1
        comfortable = 0
    elif WCI < 581.5 and WCI >= 232.6:
        effectWCI = 0
        comfortable = 1
    elif WCI < 232.6 and WCI >= 116.3:
        effectWCI = 1
        comfortable = 0
    elif WCI < 116.3 and WCI >= 58.3:
        effectWCI = 2
        comfortable = 0
    elif WCI < 58.3:
        effectWCI = 3
        comfortable = 0
    
    return WCI, effectWCI, comfortable


def windChillTemperature(Ta, ws):
    # formula by Environment Canada (corresponds to National Weather Service (NSW) Wind chill formula used in U.S.)
    ws_km_h = ws * 3.6   # convert m/s to km/h wind speed
    
    Twc = 13.12 + 0.6215*Ta - 11.37*(ws_km_h**0.16) + 0.3965*Ta*(ws_km_h**0.16)   # in Celius degrees
    
    if Twc >= 0:
        effectTwc = 0
        comfortable = 1
    elif Twc < 0 and Twc >= -9:
        effectTwc = -1
        comfortable = 0
    elif Twc < -9 and Twc >= -27:
        effectTwc = -2
        comfortable = 0
    elif Twc < -27 and Twc >= -39:
        effectTwc = -3
        comfortable = 0
    elif Twc < -39 and Twc >= -47:
        effectTwc = -4
        comfortable = 0
    elif Twc < -47 and Twc >= -54:
        effectTwc = -5
        comfortable = 0
    elif Twc < -54:
        effectTwc = -6
        comfortable = 0
    
    return Twc, effectTwc, comfortable


def effectiveTemperature(Ta, ws, rh, SR, ac):
    if ws <= 0.2:
        # formula by Missenard
        TE = Ta - 0.4*(Ta - 10)*(1-rh/100)
    elif ws > 0.2:
        # modified formula by Gregorczuk (WMO, 1972; Hentschel, 1987)
        TE = 37 - ( (37-Ta)/(0.68-(0.0014*rh)+(1/(1.76+1.4*(ws**0.75)))) ) - (0.29 * Ta * (1-0.01*rh))
    
    # Radiative-effective temperature
    TRE = TE + ((1 - 0.01*ac)*SR) * ((0.0155 - 0.00025*TE) - (0.0043 - 0.00011*TE))
    
    if TRE < 1:
        effectTE = -4
        comfortable = 0
    elif TRE >= 1 and TE < 9:
        effectTE = -3
        comfortable = 0
    elif TRE >= 9 and TE < 17:
        effectTE = -2
        comfortable = 0
    elif TRE >= 17 and TE < 21:
        effectTE = -1
        comfortable = 0
    elif TRE >= 21 and TE < 23:
        effectTE = 0
        comfortable = 1
    elif TRE >= 23 and TE < 27:
        effectTE = 1
        comfortable = 0
    elif TRE >= 27:
        effectTE = 2
        comfortable = 0
    
    return TRE, effectTE, comfortable


def apparentTemperature(Ta, ws, rh):
    
    e = (rh/100) * 6.105 * math.exp((17.27*Ta)/(237.7+Ta))
    AT = Ta + (0.33*e) - (0.70*ws) - 4.00
    
    # Apparel effects by: Norms of apparent temperature in Australia, Aust. Met. Mag., 1994, Vol 43, 1-16:
    if AT > 40:
        effectAT = 4
        comfortable = 0
    elif AT > 35 and AT <= 40:
        effectAT = 3
        comfortable = 0
    elif AT > 30 and AT <= 35:
        effectAT = 2
        comfortable = 0
    elif AT > 25 and AT <= 30:
        effectAT = 1
        comfortable = 0
    elif AT > 20 and AT <= 25:
        effectAT = 0
        comfortable = 1
    elif AT > 15 and AT <= 20:
        effectAT = -1
        comfortable = 0
    elif AT > 10 and AT <= 15:
        effectAT = -2
        comfortable = 0
    elif AT > 5 and AT <= 10:
        effectAT = -3
        comfortable = 0
    elif AT > 0 and AT <= 5:
        effectAT = -4
        comfortable = 0
    elif AT > -5 and AT <= 0:
        effectAT = -5
        comfortable = 0
    elif AT <= -5:
        effectAT = -6
        comfortable = 0
    
    return AT, effectAT, comfortable


def thermalSensation(Ta, ws, rh, SR, Tground):
    # formula from: Givoni, Noguchi, Issues and problems in outdoor comfort research, in: Proceedings of the PLEA2000 Conference, Cambridge, UK, July 2000
    TS=1.7+0.1118*Ta+0.0019*SR-0.322*ws-0.0073*rh+0.0054*Tground
    
    if TS < 2:
        effectTS = -3
        comfortable = 0
    elif TS >= 2 and TS < 3:
        effectTS = -2
        comfortable = 0
    elif TS >= 3 and TS < 4:
        effectTS = -1
        comfortable = 0
    elif TS >= 4 and TS < 5:
        effectTS = 0
        comfortable = 1
    elif TS >= 5 and TS < 6:
        effectTS = 1
        comfortable = 0
    elif TS >= 6 and TS < 7:
        effectTS = 2
        comfortable = 0
    elif TS >= 7:
        effectTS = 3
        comfortable = 0
    
    return TS, effectTS, comfortable


def actualSensationModel(Ta, ws, rh, SR):
    # Actual Sensation Model for whole Europe 
    # formula by RUROS project.
    ASV = 0.049*Ta + 0.001*SR - 0.051*ws + 0.014*rh - 2.079
    
    # Classification of human thermal sensation according to TS levels and ASV scale
    # Givoni and Noguchi, 2000; Nikolopoulou et al., 2004
    if ASV < -2:
        effectASV = -2
        comfortable = 0
    elif ASV >= -2 and ASV < -1:
        effectASV = -1
        comfortable = 0
    elif ASV >= -1 and ASV <= 1:
        effectASV = 0
        comfortable = 1
    elif ASV > 1 and ASV <= 2:
        effectASV = 1
        comfortable = 0
    elif ASV > 2:
        effectASV = 2
        comfortable = 0
    
    return ASV, effectASV, comfortable


def noaaSolarCalculator(latitude, longitude, timeZone, month, day, hour):
    # by NOAA Earth System Research Laboratory
    # NOAA defines longitude and time zone as positive to the west:
    timeZone = -timeZone
    longitude = -longitude
    DOY = int(lb_preparation.getJD(month, day))
    minute = 0  # default
    second = 0  # default
    gamma = (2*math.pi)/365*(DOY-1+((hour-12)/24))
    eqtime = 229.18*(0.000075 + 0.001868*math.cos(gamma) - 0.032077*math.sin(gamma) - 0.014615*math.cos(2*gamma) - 0.040849*math.sin(2*gamma))
    declAngle = 0.006918 - 0.399912*math.cos(gamma) + 0.070257*math.sin(gamma) - 0.006758*math.cos(2*gamma) + 0.000907*math.sin(2*gamma) - 0.002697*math.cos(3*gamma) + 0.00148*math.sin(3*gamma)
    time_offset = eqtime-4*longitude+60*timeZone
    tst = hour *60 + minute + second / 60 + time_offset
    solarHangle = (tst / 4) - 180
    
    # solar zenith angle
    solarZenithR = math.acos(math.sin(math.radians(latitude)) * math.sin(declAngle) + math.cos(math.radians(latitude)) * math.cos(declAngle) * math.cos(math.radians(solarHangle)))
    solarZenithD = math.degrees(solarZenithR)
    if solarZenithD > 90:
        solarZenithD = 90
    elif solarZenithD < 0:
        solarZenithD = 0
    
    # solar altitude angle
    solarAltitudeD = 90 - solarZenithD
    
    # solar azimuth angle
    solarAzimuthR = - (math.sin(math.radians(latitude)) * math.cos(solarZenithR) - math.sin(declAngle)) / (math.cos(math.radians(latitude)) * math.sin(solarZenithR))
    solarAzimuthR = math.acos(solarAzimuthR)
    solarAzimuthD = math.degrees(solarAzimuthR)
    
    return solarZenithD, solarAzimuthD, solarAltitudeD


def solarRadiationNudeMan(Kglob, hSl, ac):
    # formula from: Bioclimatic principles of recreation and tourism in Poland, 2nd edition, Blazejczyk, Kunert, 2011 (MENEX_2005 model)
    Kt = Kglob / (-0.0015*(hSl**3) + 0.1796*(hSl**2) + 9.6375*hSl - 11.9)
    
    ac_ = 1 - 0.01*ac
    
    # Rprim - solar radiation absorbed by nude man (W/m2)
    if hSl <= 12:
        Rprim = ac_*(0.0014*(Kglob**2) + 0.476*Kglob - 3.8)
    elif hSl > 12 and Kt <= 0.8:
        Rprim = 0.2467*ac_*(Kglob**0.9763)
    elif hSl > 12 and Kt >0.8 and Kt <=1.05:
        Rprim = 3.6922*ac_*(Kglob**0.5842)
    elif hSl > 12 and Kt > 1.05 and Kt <=1.2:
        Rprim = 43.426*ac_*(Kglob**0.2326)
    elif hSl > 12 and Kt >1.2:
        Rprim = 8.9281*ac_*(Kglob**0.4861)
        
    if Rprim < 0:
        Rprim = 0
    
    return Rprim


def groundTemperature(Ta, N):
    # formula from: Assessment of bioclimatic differentiation of Poland. Based on the human heat balance, Geographia Polonica, Matzarakis, Blazejczyk, 2007
    N100 = N *10 #converting weather data totalSkyCover from 0 to 10% to 0 to 100%
    
    if (N100 == None) or (N100 >= 80):
        Tground = Ta
    elif (N100 < 80) and (Ta >= 0):
        Tground = 1.25*Ta
    elif (N100 < 80) and (Ta < 0):
        Tground = 0.9*Ta
    
    return Tground


def VapourPressure(Ta, rh):
    # formula by ITS-90 formulations for vapor pressure, frostpoint temperature, dewpoint temperature, and enhancement factors in the range 100 to +100 c, Thunder Scientific Corporation, Albuquerque, NM, Bob Hardy
    TaK = Ta + 273.15   # convert to Kelvins
    
    TS90coefficients = [-2.8365744*(10**(3)), -6.028076559*(10**(3)), 1.954263612*(10**(1)), -2.737830188*(10**(-2)), 1.6261698*(10**(-5)), 7.0229056*(10**(-10)), -1.8680009*(10**(-13)), 2.7150305]
    e_s = TS90coefficients[7]*math.log(TaK)
    
    for i in range(7):
        e_s += TS90coefficients[i]*(TaK**(i-2))
    
    es = math.exp(e_s)  # in Pa
    
    es = (es*0.01*rh)/100  # convert to hPa
    
    return es


def meanRadiantTemperature(Ta, Tground, Rprim, e, N):
    # formula by Man-ENvironment heat EXchange model (MENEX_2005)
    
    La = 5.5*(10**(-8)) *((273 + Ta)**(4)) *(0.82 - 0.25*(10**(-0.094*0.75*e))) * (1 + 0.22*((N/10)**2.75))  # incoming long-wave radiation emitted from the sky hemisphere, in W/m2
    Lg = 5.5 *(10**(-8)) * ((273 + Tground)**(4))  # outgoing long-wave radiation emitted by the ground, in W/m2
    
    MRT = (((Rprim + 0.5*Lg + 0.5*La) / (0.95*5.667*(10**(-8))))**(0.25)) - 273  # in C
    
    return MRT


def wbgt_indoors(Ta, ws, rh, e, MRT, Tdp):
    # WBGT indoor formula by Bernard
    # formula from: "Calculating Workplace WBGT from Meteorological Data: A Tool for Climate Change Assessment", Lemke, Kjellstrom, 2012
    # natural wet bulb temperature based on code written by Nick Burns: https://github.com/nickb-/Calculating-WBGT/blob/master/relaxation_Tw/working_code/wbgt.R
    
    ed = 0.6106 * math.exp(17.27 * Tdp / (237.7 + Tdp))
    step = 0.02  # lowering the step value increases precision
    Tpwb = Tdp + step
    McPherson_1 = 1
    McPherson_2 = 1
    while Tpwb <= Ta and ((McPherson_1 > 0 and McPherson_2 > 0) or (McPherson_1 < 0 and McPherson_2 <0)):
        ew = 0.6106 * math.exp(17.27 * Tpwb / (237.7 + Tpwb))
        McPherson_1 = McPherson_2
        McPherson_2 = 1556*ed - 1.484*ed*Tpwb - 1556*ew + 1.484*ew*Tpwb + 101*(Ta - Tpwb)
        Tpwb = Tpwb + step
    
    if (ws > 3):
        WBGTid = 0.7*Tpwb + 0.3*Ta
    elif (ws >= 0.3) and (ws <= 3):
        WBGTid = 0.67 * Tpwb + 0.33 * Ta - 0.048*math.log10(ws) * (Ta - Tpwb)
    elif (ws < 0.3):
        ws = 0.3
        WBGTid = 0.67 * Tpwb + 0.33 * Ta - 0.048*math.log10(ws) * (Ta - Tpwb)
    WBGT_f = celsiusToFahrenheit(WBGTid)
    
    # Suggested actions and Impact Prevention by Environmental Health Section, Dwight D. Eisenhower Medical Center:
    if WBGT_f < 80:
        effectWBGT = 0
        comfortable = 1
    elif WBGT_f >= 80 and WBGT_f < 82:
        effectWBGT = 1
        comfortable = 0
    elif WBGT_f >= 82 and WBGT_f < 85:
        effectWBGT = 2
        comfortable = 0
    elif WBGT_f >=85 and WBGT_f < 88:
        effectWBGT = 3
        comfortable = 0
    elif WBGT_f >=88 and WBGT_f < 90:
        effectWBGT = 4
        comfortable = 0
    elif WBGT_f >= 90:
        effectWBGT = 5
        comfortable = 0
    
    return WBGTid, effectWBGT, comfortable


def wbgt_outdoors(Ta, ws, rh, e, MRT):
    # WBGT outdoor formula from Heat stress and occupational health and safety  spatial and temporal differentiation, K. Blazejczyk, J.Baranowski, A. Blazejczyk, Miscellanea geographica  regional studies on development, Vol. 18, No. 1, 2014, 
    Tw = 1.885 + 0.3704*Ta + 0.4492*e
    Tg = 2.098 - 2.561*ws + 0.5957*Ta + 0.4017*MRT
    WBGTout = 0.7*Tw + 0.2*Tg + 0.1*Ta
    WBGT_f = celsiusToFahrenheit(WBGTout)
    
    # Suggested actions and Impact Prevention by Environmental Health Section, Dwight D. Eisenhower Medical Center:
    if WBGT_f < 80:
        effectWBGT = 0
        comfortable = 1
    elif WBGT_f >= 80 and WBGT_f < 82:
        effectWBGT = 1
        comfortable = 0
    elif WBGT_f >= 82 and WBGT_f < 85:
        effectWBGT = 2
        comfortable = 0
    elif WBGT_f >=85 and WBGT_f < 88:
        effectWBGT = 3
        comfortable = 0
    elif WBGT_f >=88 and WBGT_f < 90:
        effectWBGT = 4
        comfortable = 0
    elif WBGT_f >= 90:
        effectWBGT = 5
        comfortable = 0
    
    return WBGTout, effectWBGT, comfortable


def predictedInsulationIndexOfClothing(Ta, ws, M):
    # total insulation of clothing and the surrounding air layer by Burton and Edholm (1955)
    It = (0.082*(91.4 - (1.8*Ta + 32)) / (0.01724*M))
    # insulation of the surrounded air layer by Fourt and Hollies (1970)
    Ia = 1/(0.61+1.9*(ws**0.5))
    
    Iclp = It - Ia  # in clo
    
    if Iclp > 4.0:
        effectIclp = -4
        comfortable = 1
    elif Iclp > 3.0 and Iclp <= 4.0:
        effectIclp = -3
        comfortable = 0
    elif Iclp > 2.0 and Iclp <= 3.0:
        effectIclp = -2
        comfortable = 0
    elif Iclp > 1.20 and Iclp <= 2.0:
        effectIclp = -1
        comfortable = 0
    elif Iclp > 0.80 and Iclp <= 1.20:
        effectIclp = 0
        comfortable = 1
    elif Iclp > 0.30 and Iclp <= 0.80:
        effectIclp = 1
        comfortable = 0
    elif Iclp <= 0.30:
        effectIclp = 2
        comfortable = 0
    
    if Iclp < 0.5: Iclp = 0.5  # summer clothes (light trousers, short sleeves or blouse)
    if Iclp > 4.1: Iclp = 4.1  # heavy polar outfit (fur pants, coat, hood, gloves...)
    
    return Iclp, effectIclp, comfortable


def heartRates(age, sex):
    #Resting Heart Rates for Man taken from: http://www.topendsports.com/testing/heart-rate-resting-chart.htm
    if sex == "male":
        if age <= 25:
            HRrates = [73,82,90]
        elif age > 25 and age <= 35:
            HRrates = [74,82,90]
        elif age > 35 and age <= 45:
            HRrates = [75,83,90]
        elif age > 45 and age <= 55:
            HRrates = [76,84,90]
        elif age > 55 and age <= 65:
            HRrates = [75,82,90]
        elif age > 65:
            HRrates = [73,80,90]
    elif sex == "female":
        if age <= 25:
            HRrates = [78,85,90]
        elif age > 25 and age <= 35:
            HRrates = [76,83,90]
        elif age > 35 and age <= 45:
            HRrates = [78,85,90]
        elif age > 45 and age <= 55:
            HRrates = [77,84,90]
        elif age > 55 and age <= 65:
            HRrates = [77,84,90]
        elif age > 65:
            HRrates = [76,84,90]
    elif sex == "average sex":
        # average values (("male" + "female")/2) have been taken
        if age <= 25:
            HRrates = [75.5, 83.5,90]
        elif age > 25 and age <= 35:
            HRrates = [75,82.5,90]
        elif age > 35 and age <= 45:
            HRrates = [76.5,84,90]
        elif age > 45 and age <= 55:
            HRrates = [76.5,84,90]
        elif age > 55 and age <= 65:
            HRrates = [76,83,90]
        elif age > 65:
            HRrates = [74.5,82,90]
    
    return HRrates


def heartRate(Ta, e, M, HRrates):
    #formula by Fuller, Brouha 1966
    HR = 22.4 + 0.18*M + 0.25*(5*Ta + 2.66*e)
    HR = int(round(HR))
    
    if HR < HRrates[0]:
        effectHR = 0
        comfortable = 1
    elif HR >= HRrates[0] and HR < HRrates[1]:
        effectHR = 1
        comfortable = 0
    elif HR >= HRrates[1] and HR < HRrates[2]:
        effectHR = 2
        comfortable = 0
    elif HR >= HRrates[2]:
        effectHR = 3
        comfortable = 0
    
    return HR, effectHR, comfortable


def clothingInsulation(Ta):
    # by MENEX_2005 model
    if Ta > 25:
        Icl = 0.5  # summer clothes
    else:
        Icl = 1.691 - 0.0436*Ta
    
    if Icl > 4:
        Icl = 4.1  # Heavy polar outfit
    
    return Icl


def meanSkinTemperature(Ta, ws, rh, MRT, Icl, M):
    
    Ts = (26.4 + 0.02138*MRT + 0.2095*Ta - 0.0185*rh - 0.009*ws) + 0.6*(Icl - 1) + 0.00128*M
    return Ts  # in C


def turbulentExchangeOfLatentHeat(Ta, ws, Ts, Icl, e_, M):
    # Turbulent exchange of latent heat (evaporation - mE) in W/m2
    
    p = 1000  # barometricpressure in hPa, default value
    he = Ta*(6*(10**(-5))*Ta - 2*(10**(-5))*p + 0.011) + 0.02*p - 0.773
    
    hc = 0.013*p - 0.04*Ta - 0.503
    
    vprim = 1.1 #m/s default value (for man movement 4km/h)
    d = math.sqrt(ws+vprim)
    
    if Ts < 22:
        w = 0.002
    elif Ts >= 22 and Ts <= 36.5:
        w = 1.031/(37.5-Ts)- 0.065
    elif Ts > 36.5:
        w = 1.0
    
    if ws >= 0.2:
        vcor = ws
    elif ws < 0.2:
        vcor = 0.2
    d_ = 0.53/ (Icl *(1-0.27*math.exp(0.4*math.log(vcor+vprim))))
    Ie = hc*d_ / (hc*(d + d_))
    
    esk = math.exp(0.058*Ts + 2.003)
    
    mE = he*d*w*Ie*(e_-esk) - 0.42*(M - 58.0) + 5.04
    
    return mE


def DehydrationRiskRates(acclimated):
    if acclimated == "acclimated":
        dehydrationRiskRates = [780,1040]
    elif acclimated == "unacclimated":
        dehydrationRiskRates = [520,650]
    
    return dehydrationRiskRates


def dehydrationRisk(Epot, dehydrationRiskRates):
    # formula from MENEX_2005 model
    # water loss
    SW = -2.6*Epot  # in g/hour
    
    if SW < dehydrationRiskRates[0]:
        effectSW = 0
        comfortable = 1
    elif SW >= dehydrationRiskRates[0] and SW <= dehydrationRiskRates[1]:
        effectSW = 1
        comfortable = 0
    elif SW > dehydrationRiskRates[1]:
        effectSW = 2
        comfortable = 0
    
    return SW, effectSW, comfortable


def physiologicalEquivalentTemperature(climate, Ta, ws, rh, MRT, age, sex, heightM, weight, bodyPosition, M, Icl):
    # based on: Peter Hoeppe PET fortran code, from:
    # "Urban climatic map and standards for wind environment - Feasibility study, Technical Input Report No.1",
    # The Chinese University of Hong Kong, Planning Department, Nov 2008
    
    petObj = lb_comfortModels.physiologicalEquivalentTemperature(Ta, MRT, rh, ws, age, sex, heightM, weight, bodyPosition, M, Icl)
    respiration = petObj.inkoerp()
    coreTemperature, radiationBalance, convection, waterVaporDiffusion = petObj.berech()
    petObj.pet()
    skinTemperature, totalHeatLoss, skinSweating, internalHeat, sweatEvaporation, PET = petObj.tsk, petObj.wsum, petObj.wetsk, petObj.h, petObj.esw, petObj.tx
    effectPET, comfortablePET = petObj.thermalCategories(climate)
    
    PETresults = [coreTemperature, skinTemperature, totalHeatLoss, skinSweating, internalHeat, radiationBalance, convection, waterVaporDiffusion, sweatEvaporation, respiration]
    
    return PET, effectPET, comfortablePET, PETresults


def temperatureHumidityIndex(Ta, Tdp):
    # formula and categories based on: Taiwan's Central Weather Bureau
    THI = Ta - 0.55 * (1-math.exp((17.269*Tdp)/(Tdp+237.3)-(17.269*Ta)/(Ta+237.3))) * (Ta-14)  # Taiwan's Central Weather Bureau Comfort Index
    
    if THI < 11:
        effectTHI = -3
        comfortable = 0
    elif THI >= 11 and THI < 16:
        effectTHI = -2
        comfortable = 0
    elif THI >= 16 and THI < 20:
        effectTHI = -1
        comfortable = 0
    elif THI >= 20 and THI < 27:
        effectTHI = 0
        comfortable = 1
    elif THI >= 27 and THI < 31:
        effectTHI = 1
        comfortable = 0
    elif THI >= 31:
        effectTHI = 2
        comfortable = 0
    
    return THI, effectTHI, comfortable


def predictedHeatStrain(Ta, mrt, ws, vapourPressure, heightM, weight, bodyPosition, Icl, acclimated, Met, activityDuration):
    # based on: Dr. Jacques Malchaire Quick Basic code from:
    # "Ergonomics of the thermal environment - Analytical determination and interpretation of heat stress using calculation of predicted heat strain", ISO 7933, 2004
    
    drink = 1  # if drink = 1: water replacement is sufficient, and workers can drink freely; otherwise: drink = 0
    if acclimated == "acclimated":  # 100 if acclimatised person, 0 if unacclimatised person
        accl = 100
    elif acclimated == "unacclimated":
        accl = 0
    
    # Effective radiating area of the body (1 = sitting, 2 = standing, 3 = crouching)
    if bodyPosition == "sitting":
        Ardu = 0.7  # dimensionless
    elif bodyPosition == "standing":
        Ardu = 0.77  # dimensionless
    elif bodyPosition == "crouching":
        Ardu = 0.67  # dimensionless
    
    Pa = vapourPressure * 0.1  # partial water vapour pressure, converted from hectopascals to kilopascals
    Work = 0  # effective mechanical power, in W/m2
    imst = 0.38  # static moisture permeability index, dimensionless
    Ap = 0.54  # fraction of the body surface covered by the reflective clothing, dimensionless
    Fr = 0.97  # emissivity of the reflective clothing, dimensionless
    # walking
    defspeed = 1  # 1 if walking speed entered, 0 otherwise
    Walksp = 0  # walking speed, in m/s
    defdir = 1  # 1 if walking direction entered, 0 otherwise
    THETA = 0  # angle between walking direction and wind direction degrees
    
    Adu = 0.202 * weight ** 0.425 * heightM ** 0.725  # body surface area in m2
    spHeat = 57.83 * weight / Adu
    
    SWp = 0
    SWtot = 0; Tre = 36.8; Tcr = 36.8; Tsk = 34.1; Tcreq = 36.8; TskTcrwg = 0.3
    Dlimtre = 0; Dlimloss50 = 0; Dlimloss95 = 0
    Dmax50 = 0.075 * weight * 1000
    Dmax95 = 0.05 * weight * 1000
    
    # EXPONENTIAL AVERAGING CONSTANTS
    # Core temperature as a function of the metabolic rate: time constant: 10 minutes
    ConstTeq = math.exp(-1 / 10)
    # Skin Temperature: time constant: 3 minutes
    ConstTsk = math.exp(-1 / 3)
    # Sweat rate: time constant: 10 minutes
    ConstSW = math.exp(-1 / 10)
    
    for time in range(1, activityDuration+1):  # activityDuration - the duration of the work sequence in minutes
        # INITIALISATION MIN PER MIN
        Tsk0 = Tsk; Tre0 = Tre; Tcr0 = Tcr; Tcreq0 = Tcreq; TskTcrwg0 = TskTcrwg
        
        # EVALUATION OF THE MAXIMUM SWEAT RATE AS A FUNCTION OF THE METABOLIC RATE
        SWmax = (Met - 32) * Adu
        if SWmax > 400: SWmax = 400
        if SWmax < 250: SWmax = 250
        # For acclimatised subjects (accl=100), the maximum Sweat Rate is greater by 25%
        if accl >= 50: SWmax = SWmax * 1.25
        if accl < 50: Wmax = 0.85
        else: Wmax = 1
        
        # EQUILIBRIUM CORE TEMPERATURE ASSOCIATED TO THE METABOLIC RATE
        Tcreqm = 0.0036 * Met + 36.6
        # Core temperature at this minute, by exponential averaging
        Tcreq = Tcreq0 * ConstTeq + Tcreqm * (1 - ConstTeq)
        # Heat storage associated with this core temperature increase during the last minute
        dStoreq = spHeat * (Tcreq - Tcreq0) * (1 - TskTcrwg0)
        
        # SKIN TEMPERATURE PREDICTION
        # Skin Temperature in equilibrium
        # Clothed model
        Tskeqcl = 12.165 + 0.02017 * Ta + 0.04361 * mrt + 0.19354 * Pa - 0.25315 * ws
        Tskeqcl = Tskeqcl + 0.005346 * Met + 0.51274 * Tre
        # Nude model
        Tskeqnu = 7.191 + 0.064 * Ta + 0.061 * mrt + 0.198 * Pa - 0.348 * ws
        Tskeqnu = Tskeqnu + 0.616 * Tre
        # Value at this minute, as a function of the clothing insulation
        if Icl >= 0.6: Tskeq = Tskeqcl
        else: Tskeq = Tskeqnu + 2.5 * (Tskeqcl - Tskeqnu) * (Icl - 0.2)  # Interpolation between the values for clothed and nude subjects, if  0.2 < clo < 0.6
        
        if Icl <= 0.2: Tskeq = Tskeqnu
        else: Tskeq = Tskeqnu + 2.5 * (Tskeqcl - Tskeqnu) * (Icl - 0.2)  # Interpolation between the values for clothed and nude subjects, if  0.2 < clo < 0.6
        
        # Skin Temperature at this minute, by exponential averaging
        Tsk = Tsk0 * ConstTsk + Tskeq * (1 - ConstTsk)
        # Saturated water vapour pressure at the surface of the skin
        Psk = 0.6105 * math.exp(17.27 * Tsk / (Tsk + 237.3))
        
        # CLOTHING INFLUENCE ON EXCHANGE COEFFICIENTS
        # Static clothing insulation
        Iclst = Icl * 0.155
        # Clothing area factor
        fcl = 1 + 0.3 * Icl
        # Static boundary layer thermal insulation in quiet air
        Iast = 0.111
        # Total static insulation
        Itotst = Iclst + Iast / fcl
        
        # Relative velocities due to air velocity and movements
        if defspeed > 0:
            if defdir == 1:
                # Unidirectional walking
                Var = abs(ws - Walksp * math.cos(3.14159 * THETA / 180))
            else:
                # Omni-directional walking
                if ws < Walksp:
                    Var = Walksp
                else: Var = ws
        else:
            # Stationary or undefined speed
            Walksp = 0.0052 * (Met - 58)
            if Walksp > 0.7:
                Walksp = 0.7
            Var = ws
        
        # Dynamic clothing insulation
        # Clothing insulation correction for wind (Var) and walking (Walksp) 
        Vaux = Var
        if Var > 3:
            Vaux = 3
        Waux = Walksp
        if Walksp > 1.5:
            Waux = 1.5
        CORcl = 1.044 * math.exp((.066 * Vaux - 0.398) * Vaux + (.094 * Waux - 0.378) * Waux)
        if CORcl > 1:
            CORcl = 1
        CORia = math.exp((.047 * Var - 0.472) * Var + (.117 * Waux - 0.342) * Waux)
        if CORia > 1:
            CORia = 1
         
        CORtot = CORcl
        if Icl <= 0.6:
            CORtot = ((.6 - Icl) * CORia + Icl * CORcl) / .6
        
        Itotdyn = Itotst * CORtot
        IAdyn = CORia * Iast
        Icldyn = Itotdyn - IAdyn / fcl
        
        # Permeability index
        # Correction for wind and walking
        CORe = (2.6 * CORtot - 6.5) * CORtot + 4.9
        imdyn = imst * CORe
        if imdyn > 0.9:
            imdyn = 0.9
        # Dynamic evaporative resistance
        Rtdyn = Itotdyn / imdyn / 16.7
        
        # HEAT EXCHANGES
        # Heat exchanges through respiratory convection and evaporation
        # temperature of the expired air
        Texp = 28.56 + 0.115 * Ta + 0.641 * Pa
        Cres = 0.001516 * Met * (Texp - Ta)
        Eres = 0.00127 * Met * (59.34 + 0.53 * Ta - 11.63 * Pa)
        
        # Mean temperature of the clothing: Tcl
        # Dynamic convection coefficient
        Z = 3.5 + 5.2 * Var
        if Var > 1:
            Z = 8.7 * Var ** 0.6
        Hcdyn = 2.38 * abs(Tsk - Ta) ** 0.25
        if Z > Hcdyn:
            Hcdyn = Z
        
        auxR = 5.67E-08 * Ardu
        FclR = (1 - Ap) * 0.97 + Ap * Fr
        Tcl = mrt + 0.1
        
        for k in range(100):
            # Radiation coefficient
            Hr = FclR * auxR * ((Tcl + 273) ** 4 - (mrt + 273) ** 4) / (Tcl - mrt)
            Tcl1 = ((fcl * (Hcdyn * Ta + Hr * mrt) + Tsk / Icldyn)) / (fcl * (Hcdyn + Hr) + 1 / Icldyn)
            
            if abs(Tcl - Tcl1) > 0.001:
                Tcl = (Tcl + Tcl1) / 2
                continue
            else:
                break
        
        # Convection and Radiation heat exchanges
        Conv = fcl * Hcdyn * (Tcl - Ta)
        Rad = fcl * Hr * (Tcl - mrt)
        # Maximum Evaporation Rate
        Emax = (Psk - Pa) / Rtdyn
        # Required Evaporation Rate
        Ereq = Met - dStoreq - Work - Cres - Eres - Conv - Rad
         
        # INTERPRETATION
        # Required wettedness
        wreq = Ereq / Emax
        
        # Required Sweat Rate
        #    If no evaporation required: no sweat rate
        if Ereq <= 0:
            Ereq = 0; SWreq = 0;
        else:
            #    If evaporation is not possible, sweat rate is maximum
            if Emax <= 0:
                Emax = 0; SWreq = SWmax;
            else:
                #    If required wettedness greater than 1.7: sweat rate is maximum
                if wreq >= 1.7:
                    wreq = 1.7; SWreq = SWmax;
                else:
                    #    Required evaporation efficiency
                    Eveff = (1 - wreq ** 2 / 2)
                    if wreq > 1:
                        Eveff = (2 - wreq) ** 2 / 2
                    SWreq = Ereq / Eveff
                    if SWreq > SWmax:
                        SWreq = SWmax
        
        # Predicted Sweat Rate, by exponential averaging
        SWp = SWp * ConstSW + SWreq * (1 - ConstSW)
        if SWp <= 0:
            Ep = 0; SWp = 0;
        else:
            # Predicted Evaporation Rate
            k = Emax / SWp
            wp = 1
            if k >= 0.5:
                wp = -k + math.sqrt(k * k + 2)
            if wp > Wmax:
                wp = Wmax
            Ep = wp * Emax
        
        # Heat Storage
        dStorage = Ereq - Ep + dStoreq
        
        # PREDICTION OF THE CORE TEMPERATURE
        Tcr1 = Tcr0
        for g in range(50):
            # Skin - Core weighting
            TskTcrwg = 0.3 - 0.09 * (Tcr1 - 36.8)
            if TskTcrwg > 0.3:
                TskTcrwg = 0.3
            if TskTcrwg < 0.1:
                TskTcrwg = 0.1
            
            Tcr = dStorage / spHeat + Tsk0 * TskTcrwg0 / 2 - Tsk * TskTcrwg / 2
            Tcr = (Tcr + Tcr0 * (1 - TskTcrwg0 / 2)) / (1 - TskTcrwg / 2)
            if abs(Tcr - Tcr1) > 0.001:
                Tcr1 = (Tcr1 + Tcr) / 2;
                continue
            else:
                break
        
        # PREDICTION OF THE CENTRAL (RECTAL) TEMPERATURE
        Tre = Tre0 + (2 * Tcr - 1.962 * Tre0 - 1.31) / 9  # in Celsius degrees
        
        if Dlimtre == 0 and Tre >= 38: Dlimtre = time
        # Total water loss rate during the minute (in W/m2)
        SWtot = SWtot + SWp + Eres
        SWtotg = SWtot * 2.67 * Adu / 1.8 / 60
        
        if Dlimloss50 == 0 and SWtotg >= Dmax50: Dlimloss50 = time
        if Dlimloss95 == 0 and SWtotg >= Dmax95: Dlimloss95 = time
        if drink == 0:
            Dlimloss95 = Dlimloss95 * 0.6;
            Dlimloss50 = Dlimloss95
        continue
    
    if Dlimloss50 == 0:
        Dlimloss50 = activityDuration
    if Dlimloss95 == 0:
        Dlimloss95 = activityDuration
    if Dlimtre == 0:
        Dlimtre = activityDuration
    
    PHSresults = [SWtotg, Dlimloss95, Dlimtre]
    
    
    if (Dlimloss95 >= activityDuration) and (Dlimtre >= activityDuration):
        effectPHS = 0
        comfortable = 1
    elif (Dlimtre <= 30) or (Dlimloss95 <= 30):
        effectPHS = 4
        comfortable = 0
    elif ((Dlimtre > 30) and (Dlimtre <= 120)) or ((Dlimloss95 > 30) and (Dlimloss95 <= 120)):
        effectPHS = 3
        comfortable = 0
    elif ((Dlimtre > 120) and (Dlimtre < (activityDuration - activityDuration*0.015))) or ((Dlimloss95 > 120) and (Dlimloss95 < (activityDuration - activityDuration*0.015))):
        effectPHS = 2
        comfortable = 0
    elif ((Dlimtre >= (activityDuration - activityDuration*0.015)) and (Dlimtre < activityDuration)) or ((Dlimloss95 >= (activityDuration - activityDuration*0.015)) and (Dlimloss95 < activityDuration)):
        effectPHS = 1
        comfortable = 0
    
    return Tre, effectPHS, comfortable


def HOYsDaysMonthsHoursFromHOY_analysisPeriod(HOY, analysisPeriod):
    if (HOY):
        HOYs = HOY
        HOYs.sort()
        startingDay, startingMonth, startingHour = lb_preparation.hour2Date(min(HOYs),True)
        endingDay, endingMonth, endingHour = lb_preparation.hour2Date(max(HOYs),True)
        
        newAnalysisPeriod = [(startingMonth+1, startingDay, startingHour),(endingMonth+1, endingDay, endingHour)]
    
    elif not (HOY) and (len(analysisPeriod)!=0) and (analysisPeriod[0]!=None):
        startingDate = analysisPeriod[0]
        endingDate = analysisPeriod[1]
        startingHOY = lb_preparation.date2Hour(startingDate[0], startingDate[1], startingDate[2])
        endingHOY = lb_preparation.date2Hour(endingDate[0], endingDate[1], endingDate[2])
        
        if (startingHOY < endingHOY):
            HOYs = range(startingHOY, endingHOY+1)
        elif (startingHOY > endingHOY):
            startingHOYs = range(startingHOY, 8760+1)
            endingHOYs = range(1,endingHOY+1)
            HOYs = startingHOYs + endingHOYs
        
        newAnalysisPeriod = analysisPeriod
    
    else:  # no "HOY_" nor "analysisPeriod_" inputted. Use annual data.
        HOYs = range(1,8761)
        newAnalysisPeriod = [(1, 1, 1),(12, 31, 24)]
    
    days = []
    months = []
    hours = []
    for hoy in HOYs:
        d, m, h = lb_preparation.hour2Date(hoy, True)
        days.append(d)
        months.append(m + 1)
        hours.append(h)
    
    startingDate = lb_preparation.hour2Date(lb_preparation.date2Hour(months[0], days[0], hours[0]))
    endingDate = lb_preparation.hour2Date(lb_preparation.date2Hour(months[-1], days[-1], hours[-1]))
    date = startingDate + " to " + endingDate
    
    return HOYs, days, months, hours, date, newAnalysisPeriod


def createHeaders(comfortIndex, locationName, newAnalysisPeriod, Ta, Tdp, rh, ws, SR, N, HRrates, dehydrationRiskRates, activityDuration):
    
    for data in Ta, Tdp, rh, ws, SR, N:
        if "key:location/dataType/units/frequency/startsAt/endsAt" in data:
            header = data[:7]
            break
        else:
            # default header
            header = ["key:location/dataType/units/frequency/startsAt/endsAt", "none", "none", "none", "Hourly", (1, 1, 1), (1, 1, 2)]
    
    # change (or just replace it with the same current) locationName
    header[1] = locationName
    
    comfortIndexValue = []
    comfortIndexCategory = []
    comfortableOrNot = []
    IndicesEmptyLists = [comfortIndexValue, comfortIndexCategory, comfortableOrNot]
    
    
    IndiceTitles = [
    ["Heat Index - values", "Heat Index - categories", "Heat Index - comfortable(1) or not(0)"],
    ["Humidex - values", "Humidex - categories", "Humidex - comfortable(1) or not(0)"],
    ["Discomfort Index - values", "Discomfort Index - categories", "Discomfort Index - comfortable(1) or not(0)"],
    ["Wind Chill Index - values", "Wind Chill Index - categories", "Wind Chill Index - comfortable(1) or not(0)"],
    ["Wind Chill Temperature - values", "Wind Chill Temperature - categories", "Wind Chill Temperature - comfortable(1) or not(0)"],
    ["Wet-Bulb Globe Temperature (indoors) - values", "Wet-Bulb Globe Temperature (indoors) - categories", "Wet-Bulb Globe Temperature (indoors) - comfortable(1) or not(0)"],
    ["Wet-Bulb Globe Temperature (outdoors) - values", "Wet-Bulb Globe Temperature (outdoors) - categories", "Wet-Bulb Globe Temperature (outdoors) - comfortable(1) or not(0)"],
    ["Effective Temperature - values", "Effective Temperature - categories", "Effective Temperature - comfortable(1) or not(0)"],
    ["Apparent Temperature - values", "Apparent Temperature - categories", "Apparent Temperature - comfortable(1) or not(0)"],
    ["Thermal Sensation - values", "Thermal Sensation - categories ", "Thermal Sensation - comfortable(1) or not(0)"],
    ["Actual Sensation Vote - values", "Actual Sensation Vote - categories", "Actual Sensation Vote - comfortable(1) or not(0)"],
    ["Mean Radiant Temperature - values"],
    ["Predicted Insulation Index Of Clothing - values", "Predicted Insulation Index Of Clothing - categories", "Predicted Insulation Index Of Clothing - comfortable(1) or not(0)"],
    ["Heart Rate - values", "Heart Rate - categories", "Heart Rate - comfortable(1) or not(0)"],
    ["Dehydration Risk - values", "Dehydration Risk - categories", "Dehydration Risk - comfortable(1) or not(0)"],
    ["Physiologically Equivalent Temperature (for temperate climates) - values", "Physiologically Equivalent Temperature (for temperate climates) - categories", "Physiologically Equivalent Temperature (for temperate climates) - comfortable(1) or not(0)"],
    ["Physiologically Equivalent Temperature (for (sub)tropical humid climates) - values", "Physiologically Equivalent Temperature (for (sub)tropical humid climates) - categories", "Physiologically Equivalent Temperature (for (sub)tropical humid climates) - comfortable(1) or not(0)"],
    ["Temperature Humidity Index - values", "Temperature Humidity Index - categories", "Temperature Humidity Index - comfortable(1) or not(0)"],
    ["Predicted Heat Strain - values", "Predicted Heat Strain - categories", "Predicted Heat Strain - comfortable(1) or not(0)"]
    ]
    
    IndiceUnitsCat = [
    ["C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot", "Boolean value"],
    ["C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"],
    ["C", "-6 = Hyper-glacial,  -5 = Glacial,  -4 = Extremely cold,  -3 = Very cold,  -2 = Cold,  -1 = Cool,  0 = Comfortable,  1 = Hot, 2 = Very hot, 3 = Torrid", "Boolean value"],
    ["W/m2", "-4 = Extreme frost,  -3 = Frosty,  -2 = Cold,  -1 = Cool,  0 = Comfortable,  1 = Warm, 2 = Hot, 3 = Extremely hot", "Boolean value"],
    ["C", "-6 = Extreme risk of frostbite,  -5 = Very high risk of frostbite,  -4 = High risk of frostbite,  -3 = Moderate risk of frostbite,  -2 = Low risk of frostbite,  -1 = Very low risk of frostbite, 0 = No risk of frostbite", "Boolean value"],
    ["C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"],
    ["C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"],
    ["C", "-4 = Very cold,  -3 = Cold,  -2 = Cool,  -1 = Fresh,  0 = Comfortable,  1 = Warm, 2 = Hot", "Boolean value"],
    ["C", "Appareal increments:\n-5 = Overcoat, cap,  -4 = Overcoat,  -3 = Coat and sweater,  -2 = Sweater,  -1 = Thin sweater,  0 = Normal office wear,  1 = Cotton pants,  2 = Light undershirt,  3 = Shirt, shorts,  4 = Minimal clothes. Sun protection as needed", "Boolean value"],
    ["unitless", "-3 = Very cold, -2 = Quite cold,  -1 = Cold,  0 = Comfortable,  1 = Hot,  2 = Quite hot,  3 = Very hot", "Boolean value"],
    ["unitless", "-2 = Very cold,  -1 = Cold,  0 = Comfortable,  1 = Hot,  2 = Very hot", "Boolean value"],
    ["C"],
    ["clo", "-4 = Arctic, -3 = Very cold,, -2 = Cold,  -1 = Cool,  0 = Comfortable,  1 = Warm,  2 = Very warm", "Boolean value"],
    ["beats per minute", "0 = Average,  1 = Below Average,  2 = Poor,  3 = Warning", "Boolean value"],
    ["g/hour", "0 = No risk,  1 = Dehydration warning,  2 = Dehydration hazard", "Boolean value"],
    ["C", "-4 = Very cold, -3 = Cold, -2 = Cool, -1 = Slightly cool, 0 = Comfortable,  1 = Slightly warm,  2 = Warm,  3 = Hot,  4 = Very hot", "Boolean value"],
    ["C", "-4 = Very cold, -3 = Cold, -2 = Cool, -1 = Slightly cool, 0 = Comfortable,  1 = Slightly warm,  2 = Warm,  3 = Hot,  4 = Very hot", "Boolean value"],
    ["C", "-3 = Extremely cold, -2 = Cold, -1 = Cool, 0 = Comfortable,  1 = Hot,  2 = Extremely hot", "Boolean value"],
    ["C", "0 = Comfortable,  1 = Discomfort without health risk,  2 = Long-term constraint,  3 = Short-term constraint,  4 = Immediate constraint", "Boolean value"]
    ]
    
    for i in range(len(IndiceTitles[comfortIndex])):
        for item in header:
            IndicesEmptyLists[i].append(item)
        IndicesEmptyLists[i][2] = IndiceTitles[comfortIndex][i]  # change header's title
        IndicesEmptyLists[i][3] = IndiceUnitsCat[comfortIndex][i]  # change header's units or categories
        IndicesEmptyLists[i][5] = newAnalysisPeriod[0]  # change header's from to date
        IndicesEmptyLists[i][6] = newAnalysisPeriod[1]  # change header's from to date

    outputNickNames = [
    ["HI", "HIlevel", "HIcomfortableOrNot", "HIpercentComfortable", "HIpercentHotExtreme", "_"],
    ["humidex", "humidexLevel", "humidexComfortableOrNot", "humidexPercentComfortable", "humidexPercentHotExtreme", "_"],
    ["DI", "DIlevel", "DIcomfortableOrNot", "DIpercentComfortable", "DIpercentHotExtreme", "DIpercentColdExtreme"],
    ["WCI", "WCIlevel", "WCIcomfortableOrNot", "WCIpercentComfortable", "WCIpercentHotExtreme", "WCTpercentColdExtreme"],
    ["WCT", "WCTlevel", "WCTcomfortableOrNot", "WCTpercentComfortable", "_", "WCTpercentColdExtreme"],
    ["WBGTindoor", "WBGTlevel", "WBGTcomfortableOrNot", "WBGTpercentComfortable", "WBGTpercentHotExtreme", "_"],
    ["WBGToutdoor", "WBGTlevel", "WBGTcomfortableOrNot", "WBGTpercentComfortable", "WBGTpercentHotExtreme", "_"],
    ["TE", "TElevel", "TEcomfortableOrNot", "TEpercentComfortable", "TEpercentHotExtreme", "TEpercentColdExtreme"],
    ["AT", "ATlevel", "ATcomfortableOrNot", "ATpercentComfortable", "ATpercentHotExtreme", "ATpercentColdExtreme"],
    ["TS", "TSlevel", "TScomfortableOrNot", "TSpercentComfortable", "TSpercentHotExtreme", "TSpercentColdExtreme"],
    ["ASV", "ASVlevel", "ASVcomfortableOrNot", "ASVpercentComfortable", "ASVpercentHotExtreme", "ASVpercentColdExtreme"],
    ["MRT", "_", "_", "_", "_", "_"],
    ["Iclp", "IclpLevel", "IclpComfortableOrNot", "IclpPercentComfortable", "IclpPercentHotExtreme", "IclpPercentColdExtreme"],
    ["HR", "HRlevel", "HRcomfortableOrNot", "HRpercentComfortable", "HRpercentHotExtreme", "_"],
    ["DhRa", "DhRaLevel", "DhRaComfortableOrNot", "DhRaPercentComfortable", "DhRaPercentHotExtreme", "_"],
    ["PET", "PETlevel", "PETcomfortableOrNot", "PETpercentComfortable", "PETpercentHotExtreme", "PETpercentColdExtreme"],
    ["PET", "PETlevel", "PETcomfortableOrNot", "PETpercentComfortable", "PETpercentHotExtreme", "PETpercentColdExtreme"],
    ["THI", "THIlevel", "THIcomfortableOrNot", "THIpercentComfortable", "THIpercentHotExtreme", "THIpercentColdExtreme"],
    ["PHS", "PHSlevel", "PHScomfortableOrNot", "PHSpercentComfortable", "PHSpercentHotExtreme", "_"]
    ] # outputNames = outputNickNames
    
    outputDescriptions = [
    ["Heat Index (C) - the human-perceived increase in air temperature due to humidity increase. It is used by National Weather Service (NSW).\nHeat Index is calculated for shade values. Exposure to full sunshine can increase heat index values by up to 8 C (14 F)",  #comfortIndexValues
    
    "Each number (from 0 to 4) represents a certain HI thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category 0 (<26.6 C): Satisfactory temperature. Can continue with activity.\n" + \
    "- category 1 (26.6-32.2 C): Caution: fatigue is possible with prolonged exposure and activity. Continuing activity could result in heat cramps.\n" + \
    "- category 2 (32.2-40.5 C): Extreme caution: heat cramps and heat exhaustion are possible. Continuing activity could result in heat stroke.\n" + \
    "- category 3 (40.5-54.4 C): Danger: heat cramps and heat exhaustion are likely; heat stroke is probable with continued activity.\n" + \
    "- category 4 (>54.4 C): Extreme danger: heat stroke is imminent.",  # comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning HI temperature is < 26.6 C)",  #comfortableOrNot
    
    "Percentage of time, during which HI is < 26.6 C",  #percentComfortable
    
    "Percentage of time, during which HI is > 54.4 C",  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Humidex (C) - the human-perceived increase in air temperature due to Dew point temperature increase. Used by Canadian Meteorologist service.",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain humidex thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category 0 (<30 C): Little or no discomfort\n" + \
    "- category 1 (30-35 C): Noticeable discomfort\n" + \
    "- category 2 (35-40 C): Evident discomfort\n" + \
    "- category 3 (40-45 C): Intense discomfort; avoid exertion\n" + \
    "- category 4 (45-54 C): Dangerous discomfort\n" + \
    "- category 5 (>54 C): Heat stroke probable",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning humidex is < 30 C)",  # comfortableOrNot
    
    "Percentage of time chosen for analysis period, during which humidex is < 26.6 C",  # percentComfortable
    
    "Percentage of time chosen for analysis period, during which humidex is > 54.4 C", # percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Discomfort Index (or Thom's Index)(C) - the human-perceived increase in air temperature due to himidity increase.",  #comfortIndexValues
    
    "Each number (from -6 to 3) represents a certain DI thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category -6 (<-40 C) Hyper-glacial\n" + \
    "- category -5 (-40-(-20) C) Glacial\n" + \
    "- category -4 (-20-(-10) C) Extremely cold\n" + \
    "- category -3 (-10-(-1.8) C) Very cold\n" + \
    "- category -2 (-1.8-(13) C): Cold\n" + \
    "- category -1 (13-15 C): Cool\n" + \
    "- category 0 (15-20 C): Comfortable\n" + \
    "- category 1 (20-26.5 C): Hot\n" + \
    "- category 2 (26.5-30 C): Very hot\n" + \
    "- category 3 (>30 C): Torrid",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning DI temperature is 15-20 C)",  #comfortableOrNot
    
    "Percentage of time chosen for analysis period, during which DI is 15-20 C",  #percentComfortable
    
    "Percentage of time chosen for analysis period, during which DI is > 30 C",  #percentHotExtreme
    
    "Percentage of time chosen for analysis period, during which DI is < -40 C"]  #percentColdExtreme
    
    ,
    
    ["Wind Chill Index (W/m2) - qualifies thermal sensations of man in wintertime. It is especially useful at low and very low air temperature and at high wind speed. WCI values are not equal to the actual heat loss from the human organism.",  #comfortIndexValues
    
    "Each number (from -4 to 3) represents a certain WCI thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category -4 (>=2326 W/m2) Extreme frost\n" + \
    "- category -3 (1628.2-2326 W/m2) Frosty\n" + \
    "- category -2 (930.4-1628.2 W/m2) Cold\n" + \
    "- category -1 (581.5-930.4 W/m2) Cool\n" + \
    "- category 0 (232.6-581.5 W/m2) Comfortable\n" + \
    "- category 1 (116.3-232.6 W/m2) Warm\n" + \
    "- category 2 (58.3-116.3 W/m2) Hot\n" + \
    "- category 3 (<58.3 W/m2) Extremely hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning WCI is in range: 232.6 to 581.5 W/m2)",  #comfortableOrNot
    
    "Percentage of time, during which WCI is < 232.6-581.5 W/m2",  #percentComfortable
    
    "Percentage of time, during which WCI is < 58.3 W/m2",  #percentHotExtreme
    
    "Percentage of time, during which WCI >= 2326 W/m2"]  #percentColdExtreme
    
    ,
    
    ["Wind Chill Temperature (C) - the perceived decrease in air temperature felt by the body on exposed skin due to the flow of air.\nIt's used by both National Weather Service (NSW) in US and Canadian Meteorologist service. This is new (2001 by JAG/TI) WCT.\nWind chill index does not take into account the effect of sunshine.\nBright sunshine may reduce the effect of wind chill (make it feel warmer) by 6 to 10 units(C or F)!\nWindchill temperature is defined only for temperatures at or below 10C (50F) and for wind speeds at and above 1.3 m/s (or 4.8 km/h or 3.0 mph)",  #comfortIndexValues
    
    "Each number (from -6 to 0) represents a certain WCT thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category 0 (>0 C) No discomfort. No risk of frostbite for most people\n" + \
    "- category -1 (0-(-9) C) Slight increase in discomfort. Low risk of frostbite for most people\n" + \
    "- category -2 (-9-(-27) C) Risk of hypothermia if outside for long periods without adequate protection. Low risk of frostbite for most people\n" + \
    "- category -3 (-27-(-39) C) Risk of hypothermia if outside for long periods without adequate clothing or shelter from wind and cold. Increasing risk of frostbite for most people in 10 to 30 minutes of exposure\n" + \
    "- category -4 (-39-(-47) C) Risk of hypothermia if outside for long periods without adequate clothing or shelter from wind and cold. High risk of frostbite for most people in 5 to 10 minutes of exposure\n" + \
    "- category -5 (-47-(-54) C) Serious risk of hypothermia if outside for long periods without adequate clothing or shelter from wind and cold. High risk of frostbite for most people in 2 to 5 minutes of exposure\n" + \
    "- category -6 (<-54 C) Danger! Outdoor conditions are hazardous. High risk of frostbite for most people in 2 minutes of exposure or less",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that there is danger of frostbite, 1 there is not danger of frostbite at that hour (meaning WCT temperature is in range: >-27 C)",  #comfortableOrNot
    
    "Percentage of time, during which there is low risk of frostbite (DI is > -27 C)",  #percentComfortable
    " ",  #percentHotExtreme
    
    "Percentage of time, during which there is high risk of frostbite (DI is < -54 C)"]  #percentColdExtreme
    
    ,
    
    ["Wet-Bulb Globe Temperature(C) - perceived indoor temperature.\nIt is used by the U.S. military and American Academy of Pediatrics and OSHA (Occupational Safety and Health Administration) to obtain measure of heat stress involved in manual labor jobs of soldiers, construction workers, steel mill workers, firefighters, law enforcement officers, athletes...",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain WBGT thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category 0 (<26 C): No change in activity is required.\n" + \
    "- category 1 (26-27.7 C): No change in activity is required. Use discretion when planning heavy activities for unacclimated person.\n" + \
    "- category 2 (27.7-29.4 C): Outdoor physical activities and strenuous exercise should be limited to 50 minutes per hour. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\n" + \
    "- category 3 (29.4-31.1 C): Outdoor physical activities and strenuous exercise should be limited to 40 minutes per hour. You should unblouse trouser legs. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\n" + \
    "- category 4 (31.1-32.2 C): Outdoor physical activities and strenuous exercise should be limited to 30 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\n" + \
    "- category 5 (>32.2 C): Outdoor physical activities and strenuous exercise should be limited to 20 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning WBGT temperature is in range: 29.4 to 31.1 C)",  #comfortableOrNot
    
    "Percentage of time, during which WBGT is < 26 C",  #percentComfortable
    
    "Percentage of time, during which WBGT is > 32.2 C",  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Wet-Bulb Globe Temperature(C) - perceived outdoor temperature.\nIt is used by the U.S. military, American Academy of Pediatrics and OSHA (Occupational Safety and Health Administration) to obtain measure of heat stress involved in manual labor jobs of soldiers, construction workers, steel mill workers, firefighters, law enforcement officers, athletes...",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain WBGT thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category 0 (<26 C): No change in activity is required.\n" + \
    "- category 1 (26-27.7 C): No change in activity is required. Use discretion when planning heavy activities for unacclimated person.\n" + \
    "- category 2 (27.7-29.4 C): Outdoor physical activities and strenuous exercise should be limited to 50 minutes per hour. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\n" + \
    "- category 3 (29.4-31.1 C): Outdoor physical activities and strenuous exercise should be limited to 40 minutes per hour. You should unblouse trouser legs. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\n" + \
    "- category 4 (31.1-32.2 C): Outdoor physical activities and strenuous exercise should be limited to 30 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\n" + \
    "- category 5 (>32.2 C): Outdoor physical activities and strenuous exercise should be limited to 20 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning WBGT temperature is in range: 29.4 to 31.1 C)",  #comfortableOrNot
    
    "Percentage of time, during which WBGT is < 26 C",  #percentComfortable
    
    "Percentage of time, during which WBGT is > 32.2 C",  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Effective Temperature (C) - influence of air temperature, wind speed, relative humidity of air, and solar radiation on man indoors and outdoors (both in shade and under the sun)",  #comfortIndexValues
    
    "Each number (from -4 to 2) represents a certain TE thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category -4 (<1 C): Very cold\n" + \
    "- category -3 (1-9 C): Cold\n" + \
    "- category -2 (9-17 C): Cool\n" + \
    "- category -1 (17-21 C): Fresh\n" + \
    "- category 0 (21-23 C): Comfortable\n" + \
    "- category 1 (23-27 C): Warm\n" + \
    "- category 2 (>27 C): Hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning TE temperature is in range: 21 to 23 C)",  #comfortableOrNot
    
    "Percentage of time, during which TE is < 21-23 C",  #percentComfortable
    
    "Percentage of time, during which TE is > 27 C",  #percentHotExtreme
    
    "Percentage of time, during which TE is < 1 C"]  #percentColdExtreme
    
    ,
    
    ["Apparent Temperature (C) - combines wind chill and heat index to give one single perceived outdoor temperature for Australian climate.\nNon-radiation formula from ABM(Australian Bureau of Meteorology).",  #comfortIndexValues
    
    "Each number (from -6 to 4) represents a certain AT thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "Appareal increments:\n" + \
    "- category 4 (>40 C): Minimal; sun protection required\n" + \
    "- category 3 (35-40 C): Minimal; sun protection as needed\n" + \
    "- category 2 (30-35 C): Short sleeve, shirt and shorts\n" + \
    "- category 1 (25-30 C): Light undershirt\n" + \
    "- category 0 (20-25 C): Cotton-type slacks (pants)\n" + \
    "- category -1 (15-20 C): Normal office wear\n" + \
    "- category -2 (10-15 C): Thin or sleeveless sweater\n" + \
    "- category -3 (5-10 C): Sweater. Thicker underwear\n" + \
    "- category -4 (0-5 C): Coat and sweater\n" + \
    "- category -5 (-5-0 C): Overcoat. Wind protection as needed\n" + \
    "- category -6 (<-5 C): Overcoat. Head insulation. Heavier footwear",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning AT temperature is in range: 20 to 25 C)",  #comfortableOrNot
    
    "Percentage of time, during which AT is < 20-25 C",  #percentComfortable
    
    "Percentage of time, during which AT is > 40 C",  #percentHotExtreme
    
    "Percentage of time, during which AT is < -5 C"]  #percentColdExtreme
    
    ,
    
    ["Thermal Sensation (index) (unit-less) - and index which predicts sensation of satisfaction/dissatisfaction under the prevailing outdoor climatic conditions.\nIt is applicable to Japan only (with exception of Hokaido and central parts of Honshu island).",  #comfortIndexValues
    
    "Each number (from -3 to 3) represents a certain TS thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category -3 (<2): Very cold\n" + \
    "- category -2 (2-3): Quite cold\n" + \
    "- category -1 (3-4): Cold\n" + \
    "- category 0 (4-5): Comfort\n" + \
    "- category 1 (5-6): Hot\n" + \
    "- category 2 (6-7): Quite Hot\n" + \
    "- category 3 (>7): Very hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning TS index is in range: 4 to 5)",  #comfortableOrNot
    
    "Percentage of time, during which TS is 4 to 5",  #percentComfortable
    
    "Percentage of time, during which TS is > 7",  #percentHotExtreme
    
    "Percentage of time, during which TS is < 2"]  #percentColdExtreme
    
    ,
    
    ["Actual Sensation Vote (unit-less) - is an index which estimates human thermal sensation based on the empirical data gathered from field and human surveys, interviews and questionnaires in 7 European cities (RUROS project: Cambridge, Sheffield, Milan, Fribourg, Kassel, Athens, Thessaloniki). ASV index is valid for Europe only.",  #comfortIndexValues
    
    "Each number (from -2 to 2) represents a certain ASV thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category -2 (<-2): Very cold\n" + \
    "- category -1 (-2-(-1)): Cold\n" + \
    "- category 0 (-1-1): Comfort\n" + \
    "- category 1 (1-2): Hot\n" + \
    "- category 2 (>2): Very Hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning ASV index is in range: -1 to 1)",  #comfortableOrNot
    
    "Percentage of time, during which ASV is -1 to 1",  #percentComfortable
    
    "Percentage of time, during which ASV is > 2",  #percentHotExtreme
    
    "Percentage of time, during which ASV is < -2"]  #percentColdExtreme
    
    ,
    
    ["Mean Radiant Temperature (C) - uniform temperature of an imaginary enclosure in which the radiant heat transfer from the human body is equal to the radiant heat transfer in the actual non-uniform enclosure.\nFor indoor conditions MRT equals the dry bulb (air) temperature.", #comfortIndexValues
    " ",
    " ",
    " ",
    " ",
    " "]
    
    ,
    
    ["Predicted Insulation Index Of Clothing (clo) - is approximated, predicted value of thermal insulation of clothing which is necessary to keep thermal comfort in man.\nIt is calculated based on air temperature, wind speed and metabolic rate.\nMinimal Iclp is restricted to 0.5 (summer clothes). Maximal Iclp to 4.1 (heavy polar outfit).",  #comfortIndexValues
    
    "Each number (from -4 to 2) represents a certain Iclp thermal sensation category. With categories being the following:\n" + \
    "--\n" + \
    "- category -4 (>4): Arctic\n" + \
    "- category -3 (3.0-4.0): Very cold\n" + \
    "- category -2 (2.0-3.0): Cold\n" + \
    "- category -1 (1.20-2.0): Cool\n" + \
    "- category 0 (0.80-1.20): Comfortable\n" + \
    "- category 1 (0.30-0.80): Warm\n" + \
    "- category 2 (0.30<): Very warm",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning Iclp index is in range: 0.80 to 1.20)",  #comfortableOrNot
    
    "Percentage of time, during which Iclp is 0.80 to 1.20",  #percentComfortable
    
    "Percentage of time, during which Iclp is < 0.30",  #percentHotExtreme
    
    "Percentage of time, during which Iclp is > 4"]  #percentColdExtreme
    
    ,
    
    ["Heart Rate (beats per minute) - is the number of heart beats per 1 minute.",  #comfortIndexValues
    
    "Each number (from 0 to 3) represents a certain HR beats per minute category. With categories being the following:\n" + \
    "--\n" + \
    "- category 0 (<%s  beats per minute): Average.\n" % HRrates[0] + \
    "- category 1 (%s-%s beats per minute): Below Average.\n" % (HRrates[0],HRrates[1]) + \
    "- category 2 (%s-%s  beats per minute): Poor.\n" % (HRrates[1], HRrates[2]) + \
    "- category 3 (>%s beats per minute): Warning." % HRrates[2], # comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning HR is < %s beaps per minute) " % HRrates[0], #comfortableOrNot
    
    "Percentage of time, during which HR is <%s beats per minute" % HRrates[0],  #percentComfortable
    
    "Percentage of time, during which HR is > %s beats per minute" % HRrates[2],  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Dehydration Risk (g/hour) - is the excessive loss of body water, with an accompanying disruption of metabolic processes.",  #comfortIndexValues
    
    "Each number (from 0 to 2) represents a certain Dehydration risk category. With categories being the following:\n" + \
    "--\n" + \
    "- category 0 (<%s g/hour): No risk.\n" % dehydrationRiskRates[0] + \
    "- category 1 (%s-%s g/hour): Dehydration warning.\n" % (dehydrationRiskRates[0],dehydrationRiskRates[1]) + \
    "- category 2 (>%s g/hour): Dehydration hazard." % dehydrationRiskRates[1],  # comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning HI temperature is < %s g/hour)" % dehydrationRiskRates[0],  #comfortableOrNot
    
    "Percentage of time, during which HI is < %s g/hour" % dehydrationRiskRates[0],  #percentComfortable
    
    "Percentage of time, during which HI is > %s g/hour" % dehydrationRiskRates[1],  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Physiologically Equivalent Temperature (C) for temperate climates - an air temperature at which, in a typical indoor conditions, the heat budget of the human body is balanced with the same core and skin temperature as under the complex outdoor conditions to be assessed. This way PET enables a layperson to compare the integral effects of complex thermal conditions outside with his or her own experience indoors.",  #comfortIndexValues
    
    "Each number (from -4 to 4) represents a certain PET level/category. With categories being the following:\n" + \
    "--\n" + \
    "- category -4 (<4 C) Very cold\n" + \
    "- category -3 (4-8 C) Cold\n" + \
    "- category -2 (8-13 C) Cool\n" + \
    "- category -1 (13-18 C) Slightly cool\n" + \
    "- category 0 (18-23 C) Comfortable\n" + \
    "- category 1 (23-29 C) Slightly warm\n" + \
    "- category 2 (29-35 C) Warm\n" + \
    "- category 2 (35-41 C) Hot\n" + \
    "- category 4 (>4 C) Very hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning PET is in range: 18 to 23 C)",  #comfortableOrNot
    
    "Percentage of time, during which PET is 18-23 C",  #percentComfortable
    
    "Percentage of time, during which PET is > 41 C",  #percentHotExtreme
    
    "Percentage of time, during which PET is < 4 C"]  #percentColdExtreme
    
    ,
    
    ["Physiologically Equivalent Temperature (C) for (sub)tropical climates - an air temperature at which, in a typical indoor conditions, the heat budget of the human body is balanced with the same core and skin temperature as under the complex outdoor conditions to be assessed. This way PET enables a layperson to compare the integral effects of complex thermal conditions outside with his or her own experience indoors.",  #comfortIndexValues
    
    "Each number (from -4 to 4) represents a certain PET level/category. With categories being the following:\n" + \
    "--\n" + \
    "- category -4 (<14 C) Very cold\n" + \
    "- category -3 (14-18 C) Cold\n" + \
    "- category -2 (18-22 C) Cool\n" + \
    "- category -1 (22-26 C) Slightly cool\n" + \
    "- category 0 (26-30 C) Comfortable\n" + \
    "- category 1 (30-34 C) Slightly warm\n" + \
    "- category 2 (34-38 C) Warm\n" + \
    "- category 2 (38-42 C) Hot\n" + \
    "- category 4 (>42 C) Very hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning PET is in range: 18 to 23 C)",  #comfortableOrNot
    
    "Percentage of time, during which PET is 26-30 C",  #percentComfortable
    
    "Percentage of time, during which PET is > 42 C",  #percentHotExtreme
    
    "Percentage of time, during which PET is < 14 C"]  #percentColdExtreme
    
    ,
    
    ["Temperature Humidity Index (C) - the human-perceived increase in air temperature due to humidity increase.\nIt is used by Central Weather Bureau of Taiwan. Essentially it represents the modified version of Discomfort Index (DI).\nIt is meant to be used in inshade, non windy conditions.",  #comfortIndexValues
    
    "Each number (from -3 to 2) represents a certain THI level/category. With categories being the following:\n" + \
    "--\n" + \
    "- category -3 (<11 C) Extremely cold\n" + \
    "- category -2 (11-16 C) Cold\n" + \
    "- category -1 (16-20 C) Cool\n" + \
    "- category 0 (20-27 C) Comfortable\n" + \
    "- category 1 (27-31 C) Hot\n" + \
    "- category 2 (>31 C) Extremely hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning THI is in range: 20 to 27 C)",  #comfortableOrNot
    
    "Percentage of time, during which THI is 20-27 C",  #percentComfortable
    
    "Percentage of time, during which THI is > 31 C",  #percentHotExtreme
    
    "Percentage of time, during which THI is < 11 C"]  #percentColdExtreme
    
    ,
    
    ["Predicted Heat Strain (C) - ISO 7933 model for evaluation of thermal stress experienced by a person/athlete/worker in a hot environment.",  #comfortIndexValues
    
    "Each number (from 0 to 4) represents a certain PHS level/category. With categories being the following:\n" + \
    "--\n" + \
    "- category 0:  Comfortable - no health risk\n" + \
    "  Excessive water loss happened at least %s minutes from the start of activity.\n" % activityDuration + \
    "  or Central (rectal) temperature of 38 C was exceeded at least %s minutes from the start of activity.\n" % activityDuration + \
    " \n" + \
    "- category 1:  Discomfort without health risk\n" + \
    "  Excessive water loss happened during %s to %s minutes from the start of activity.\n" % ((activityDuration - activityDuration*0.015), activityDuration) + \
    "  or Central (rectal) temperature of 38 C was exceeded during %s to %s minutes from the start of activity.\n" % ((activityDuration - activityDuration*0.015), activityDuration) + \
    " \n" + \
    "- category 2:  Long-term constraint - discomfort and risk of dehydration after several hours of exposure\n" + \
    "  Excessive water loss happened during 120 to %s minutes from the start of activity.\n" % (activityDuration - activityDuration*0.015) + \
    "  or Central (rectal) temperature of 38 C was exceeded during 120 to %s minutes from the start of activity.\n" % (activityDuration - activityDuration*0.015) + \
    " \n" + \
    "- category 3:  Short-term constraint - health risk after 30 to 120 minutes of exposure\n" + \
    "  Excessive water loss happened during 30 to 120 minutes from the start of activity.\n" + \
    "  or Central (rectal) temperature of 38 C was exceeded during 30 to 120 minutes from the start of activity.\n" + \
    " \n" + \
    "- category 4:  Immediate constraint - health risks even for exposures of very short durations (less than 30 minutes)\n"
    "  Excessive water loss happened 30 minutes or less from the start of activity.\n" + \
    "  or Central (rectal) temperature of 38 C was exceeded 30 minutes or less from the start of activity.\n",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour, meaning:\n" + \
    "  Excessive water loss happened at least %s minutes from the start of activity.\n" % activityDuration + \
    "  or Central (rectal) temperature of 38 C was exceeded at least %s minutes from the start of activity.\n" % activityDuration,  #comfortableOrNot
    
    "Percentage of time, during which:\n" + \
    "  Excessive water loss happened at least %s minutes from the start of activity.\n" % activityDuration + \
    "  or Central (rectal) temperature of 38 C was exceeded at least %s minutes from the start of activity.\n" % activityDuration,  #percentComfortable
    
    "Percentage of time, during which:\n" + \
    "  Excessive water loss happened 30 minutes or less from the start of activity.\n" + \
    "  or Central (rectal) temperature of 38 C was exceeded 30 minutes or less from the start of activity.",  #percentHotExtreme
    
    " "]  #percentColdExtreme
    ]
    
    return comfortIndexValue, comfortIndexCategory, comfortableOrNot, outputNickNames[comfortIndex], outputDescriptions[comfortIndex]


def printThermalComfortIndexName(comfortIndex, date, HOYs, PETresults):
    thermalComfortIndexName = ["HI (Heat Index)", "humidex (humidity index)", "DI (Discomfort Index)", "WCI (Wind Chill Index)", "WCT (Wind Chill Temperature)", "WBGT (Wet-Bulb Globe Temperature) indoors", "WBGT (Wet-Bulb Globe Temperature) outdoors", "TE (Effective Temperature)", "AT (Apparent Temperature)", "TS (Thermal Sensation)", "ASV (Actual Sensation Vote)", "MRT (Mean Radiant Temperature)", "Iclp (Predicted Insulation Index Of Clothing)", "HR (Heart Rate)", "DhRa (Dehydration Risk)", "PET (Physiologically Equivalent Temperature) for temperate climates", "PET (Physiologically Equivalent Temperature) for (sub)tropical humid climates", "THI (Temperature Humidity Index)", "PHS (Predicted Heat Strain)"]
    print "%s successfully calculated for %s period." % (thermalComfortIndexName[comfortIndex], date)
    
    # print PETresults or PHSresults only for HOY_ inputted:
    if PETresults and (len(HOYs) == 1):
        coreTemperature, skinTemperature, totalHeatLoss, skinSweating, internalHeat, radiationBalance, convection, waterVaporDiffusion, sweatEvaporation, respiration = PETresults
        print "\nBODY PARAMETERS\nCore temperature (C): %0.2f\nMean skin temperature (C): %0.2f\nTotal heat loss (g/h): %0.2f\nSkin wettedness (unitless): %0.2f\n\nHEAT FLUXES\nInternal heat (W): %0.2f\nRadiation balance (W): %0.2f\nConvection (W): %0.2f\nWater vapor diffusion (W): %0.2f\nSweat evaporation (W): %0.2f\nRespiration (W): %0.2f" % (coreTemperature, skinTemperature, totalHeatLoss, skinSweating, internalHeat, radiationBalance, convection, waterVaporDiffusion, sweatEvaporation, respiration)


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]
        
        if (_comfortIndex != None) and _comfortIndex in range(19):
            locationName, latitude, longitude, timeZone, validLocationData, printMsgLocation = getLocationData(_location)
            if validLocationData:
                TaL, mrtL, TdpL, rhL, wsL, SRL, NL, TgroundL, RprimL, vapourPressureL, EpotL, HOYs, date, newAnalysisPeriod, age, sex, heightCM, heightM, weight, bodyPosition, IclL, ac, acclimated, ML, activityDuration, validWeatherData, printMsgWeather = getWeatherData(latitude, longitude, timeZone, _dryBulbTemperature, meanRadiantTemperature_, dewPointTemperature_, relativeHumidity_, windSpeed_, solarRadiationPerHour_, totalSkyCover_, bodyCharacteristics_, HOY_, analysisPeriod_)
                if validWeatherData:
                    if _runIt:
                        HRrates = heartRates(age, sex)
                        dehydrationRiskRates = DehydrationRiskRates(acclimated)
                        comfortIndexValue, comfortIndexCategory, comfortableOrNot, outputNickNames, outputDescriptions = createHeaders(_comfortIndex, locationName, newAnalysisPeriod, _dryBulbTemperature, dewPointTemperature_, relativeHumidity_, windSpeed_, solarRadiationPerHour_, totalSkyCover_, HRrates, dehydrationRiskRates, activityDuration)
                        PETresults = None
                        for i,hoy in enumerate(HOYs):
                            listIndex = hoy - 1
                            if _comfortIndex == 0:
                                hi,cat,cnc = heatIndex(TaL[listIndex], rhL[listIndex]);  comfortIndexValue.append(hi);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 4
                            elif _comfortIndex == 1:
                                humi,cat,cnc = Humidex(TaL[listIndex], TdpL[listIndex]);  comfortIndexValue.append(humi);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 5
                            elif _comfortIndex == 2:
                                di,cat,cnc = discomfortIndex(TaL[listIndex], rhL[listIndex]);  comfortIndexValue.append(di);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 3
                                ColdExtremeCategory = -6
                            elif _comfortIndex == 3:
                                wci,cat,cnc = windChillIndex(TaL[listIndex], wsL[listIndex]);  comfortIndexValue.append(wci);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 3
                                ColdExtremeCategory = -4
                            elif _comfortIndex == 4:
                                wct,cat,cnc = windChillTemperature(TaL[listIndex], wsL[listIndex]);  comfortIndexValue.append(wct);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                ColdExtremeCategory = -4
                            elif _comfortIndex == 5:
                                wbgt,cat,cnc = wbgt_indoors(TaL[listIndex], wsL[listIndex], rhL[listIndex], vapourPressureL[listIndex], mrtL[listIndex], TdpL[listIndex]);  comfortIndexValue.append(wbgt);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 5
                            elif _comfortIndex == 6:
                                wbgt,cat,cnc = wbgt_outdoors(TaL[listIndex], wsL[listIndex], rhL[listIndex], vapourPressureL[listIndex], mrtL[listIndex]);  comfortIndexValue.append(wbgt);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 5
                            elif _comfortIndex == 7:
                                et,cat,cnc = effectiveTemperature(TaL[listIndex], wsL[listIndex], rhL[listIndex], SRL[listIndex], ac);  comfortIndexValue.append(et);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 2
                                ColdExtremeCategory = -4
                            elif _comfortIndex == 8:
                                at,cat,cnc = apparentTemperature(TaL[listIndex], wsL[listIndex], rhL[listIndex]);  comfortIndexValue.append(at);  comfortIndexCategory.append(cat); comfortableOrNot.append(cnc)
                                HotExtremeCategory = 4
                                ColdExtremeCategory = -6
                            elif _comfortIndex == 9:
                                ts,cat,cnc = thermalSensation(TaL[listIndex], wsL[listIndex], rhL[listIndex], SRL[listIndex], TgroundL[listIndex]);  comfortIndexValue.append(ts);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 3
                                ColdExtremeCategory = -3
                            elif _comfortIndex == 10:
                                asv,cat,cnc = actualSensationModel(TaL[listIndex], wsL[listIndex], rhL[listIndex], SRL[listIndex]);  comfortIndexValue.append(asv);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 2
                                ColdExtremeCategory = -2
                            elif _comfortIndex == 11:
                                mrt = meanRadiantTemperature(TaL[listIndex], TgroundL[listIndex], RprimL[listIndex], vapourPressureL[listIndex], NL[listIndex]);  comfortIndexValue.append(mrt)
                            elif _comfortIndex == 12:
                                iclp,cat,cnc = predictedInsulationIndexOfClothing(TaL[listIndex], wsL[listIndex], ML[listIndex]);  comfortIndexValue.append(iclp);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 2
                                ColdExtremeCategory = -4
                            elif _comfortIndex == 13:
                                hr,cat,cnc = heartRate(TaL[listIndex], vapourPressureL[listIndex], ML[listIndex], HRrates);  comfortIndexValue.append(hr);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 3
                            elif _comfortIndex == 14:
                                sw,cat,cnc = dehydrationRisk(EpotL[i], dehydrationRiskRates);  comfortIndexValue.append(sw);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 2
                            elif _comfortIndex == 15:
                                pet,cat,cnc,PETresults = physiologicalEquivalentTemperature("temperate", TaL[listIndex], wsL[listIndex], rhL[listIndex], mrtL[listIndex], age, sex, heightM, weight, bodyPosition, ML[listIndex], IclL[listIndex]);  comfortIndexValue.append(pet);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 4
                                ColdExtremeCategory = -4
                            elif _comfortIndex == 16:
                                pet,cat,cnc,PETresults = physiologicalEquivalentTemperature("humid", TaL[listIndex], wsL[listIndex], rhL[listIndex], mrtL[listIndex], age, sex, heightM, weight, bodyPosition, ML[listIndex], IclL[listIndex]);  comfortIndexValue.append(pet);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 4
                                ColdExtremeCategory = -4
                            elif _comfortIndex == 17:
                                thi,cat,cnc = temperatureHumidityIndex(TaL[listIndex], TdpL[listIndex]);  comfortIndexValue.append(thi);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 2
                                ColdExtremeCategory = -3
                            elif _comfortIndex == 18:
                                phs,cat,cnc = predictedHeatStrain(TaL[listIndex], mrtL[listIndex], wsL[listIndex], vapourPressureL[listIndex], heightM, weight, bodyPosition, IclL[listIndex], acclimated, ML[listIndex], activityDuration);  comfortIndexValue.append(phs);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                                HotExtremeCategory = 4
                        
                        if _comfortIndex != 11:  # not for MRT
                            percentComfortable = (comfortableOrNot[7:].count(1))/(len(comfortIndexValue[7:]))*100
                            if _comfortIndex != 4:
                                percentHotExtreme = (comfortIndexCategory[7:].count(HotExtremeCategory))/(len(comfortIndexCategory[7:]))*100
                            else: # remove percentHotExtreme for WCT
                                percentHotExtreme = []
                            if _comfortIndex not in [0,1,5,6,13,14,18]: # no Cold categories
                                percentColdExtreme = (comfortIndexCategory[7:].count(ColdExtremeCategory))/(len(comfortIndexCategory[7:]))*100
                            else:  # remove percentColdExtreme
                                percentColdExtreme = []
                        else:
                            percentComfortable = percentHotExtreme = percentColdExtreme = []
                    
                    if _runIt:
                        generalOutputLists = ["dummy", "comfortIndexValue", "comfortIndexCategory", "comfortableOrNot", "percentComfortable", "percentHotExtreme", "percentColdExtreme"]
                        for i in range(6):
                            ghenv.Component.Params.Output[i+1].Name = outputNickNames[i]
                            ghenv.Component.Params.Output[i+1].NickName = outputNickNames[i]
                            ghenv.Component.Params.Output[i+1].Description = outputDescriptions[i]
                            exec("%s = %s" % (outputNickNames[i], generalOutputLists[i+1]))
                        printThermalComfortIndexName(_comfortIndex, date, HOYs, PETresults)
                    else:
                        print "All inputs are ok. Please set \"_runIt\" to True, to calculate the chosen Thermal Comfort index"
                else:
                    print printMsgWeather
                    ghenv.Component.AddRuntimeMessage(level, printMsgWeather)
            else:
                print printMsgLocation
                ghenv.Component.AddRuntimeMessage(level, printMsgLocation)
        else:
            printMsgComfortIndex = "Please input the desired _comfortIndex integer from 0 to 18"
            print printMsgComfortIndex
            ghenv.Component.AddRuntimeMessage(level, printMsgComfortIndex)
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
