# Solar water heating surface
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Dr. Chengchu Yan and Djordje Spasic <ycc05ster@gmail.com, djordjedspasic@gmail.com> 
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
Use this component to calculate amount of thermal energy that can be produced by a surface
if a certain percentage of it is covered with Solar water heating liquid collectors.
The thermal energy can then be used for domestic hot water, space heating or space cooling.
-
Component based on:
"Solar Engineering of Thermal Processes", John Wiley and Sons, J. Duffie, W. Beckman, 4th ed., 2013.
"Technical Manual for the SAM Solar Water Heating Model", NREL, N. DiOrio, C. Christensen, J. Burch, A. Dobos, 2014.
"A simplified method for optimal design of solar water heating systems based on life-cycle energy analysis", Renewable Energy journal, Yan, Wang, Ma, Shi, Vol 74, Feb 2015
-
http://www.wiley.com/WileyCDA/WileyTitle/productCd-0470873663.html
https://sam.nrel.gov/system/tdf/SimpleSolarWaterHeatingModel_SAM_0.pdf?file=1&type=node&id=69521
http://www.sciencedirect.com/science/article/pii/S0960148114004807
-
Provided by Ladybug 0.0.62
    
    input:
        _epwFile: Input .epw file path by using the "File Path" parameter, or Ladybug's "Open EPW And STAT Weather Files" component.
        _heatingLoadPerHour: Heating load in electrical energy for each hour during a year. In kWh.
                             It represents domestic hot water heating load.
                             With added space heating and/or space cooling heating loads.
                             -
                             To calculate domestic hot water heating load, use Ladybug "Residential Hot Water" or "Commercial Public Apartment Hot Water" components.
                             -
                             Space heating and space cooling loads can be inputted from Honeybee's "Read EP Result" component.
                             Divide each value of space heating load with 0.7, to account for COP(coefficient of performance) of the heating system.
                             Space cooling values do not need to be divided with anything (COP = 1.0).
        _SWHsurface: - Input planar Surface (not polysurface) on which the SWH collectors will be applied. If you have a polysurface, explode it (using "Deconstruct Brep" component) and then feed its Faces(F) output to _SWHsurface. Surface normal should be faced towards the sun.
                     - Or create the Surface based on initial SWH system size by using "PV SWH system size" component.
        SWHsurfacePercent_: The percentage of surface which will be used for SWH collectors (range 0-100).
                            -
                            There are no general rules or codes which would limit the percentage of the roof(surface) covered with SWH collectors.
                            -
                            If not supplied, default value of 100 (all surface area will be covered with SWH collectors) is used.
        SWHsystemSettings_: A list of all Solar water heating system settings. Use the "Solar Water Heating System" or "Solar Water Heating System Detailed" components to generate them.
                            -
                            If not supplied, the following swh system settings will be used by default:
                            - glazed flat plate collectors
                            - active
                            - closed loop
                            - pipe length: 20 meters
                            - unshaded
        north_: Input a vector to be used as a true North direction for the sun path, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis to make North.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        albedo_: A list of 8767 (with header) or 8760 (without the header) albedo values for each hour during a year.
                 Albedo (or Reflection coefficient) is an average ratio of the global incident solar radiation reflected from the area surrounding the PV surface.
                 It ranges from 0 to 1.
                 -
                 It depends on the time of the year/day, surface type, temperature, vegetation, presence of water, ice and snow etc.
                 -
                 If no list supplied, default value of 0.20 will be used, corrected(increased) for the presence of snow (if any).
                 -
                 Unitless.
        annualHourlyData_: An optional list of hourly data from Ladybug's "Import epw" component (e.g. dryBulbTemperature), which will be used for "conditionalStatement_".
        conditionalStatement_: This input allows users to calculate the Solar water heating surface component results only for those annualHourlyData_ values which fit specific conditions or criteria.
                               To use this input correctly, hourly data, such as dryBulbTemperature or windSpeed, must be plugged into the "annualHourlyData_" input. The conditional statement input here should be a valid condition statement in Python, such as "a>25" or "b<3" (without the quotation marks).
                               conditionalStatement_ accepts "and" and "or" operators. To visualize the hourly data, English letters should be used as variables, and each letter alphabetically corresponds to each of the lists (in their respective order): "a" always represents the 1st list, "b" always represents the 2nd list, etc.
                               -
                               For example, if you have an hourly dryBulbTemperature connected as the first list, and windSpeed connected as the second list (both to the annualHourlyData_ input), and you want to plot the data for the time period when temperature is between 18C and 23C, and windSpeed is larger than 3m/s, the conditionalStatement_ should be written as "18<a<23 and b>3" (without the quotation marks).
                               -
                               This input can also be used for analysis of drainback systems. Input a "dryBulbTemperature" data from "Import epw" component into upper "annualHourlyData_" input. Then input "a>5" to this ("conditionalStatement_") input.
        _runIt: ...
        
    output:
        readMe!: ...
        heatFromTankPerHour: Thermal energy provided by the storage tank per each hour during a year.
                             -
                             In kWh.
        heatFromTankPerYear: Total thermal energy provided by the storage tank for a whole year.
                             -
                             In kWh.
        avrDailyheatFromTankPerYear: An average thermal energy provided by the storage tank per day for a whole year.
                                     -
                                     In kWh/day.
        heatFromAuxiliaryHeaterPerHour: Thermal energy provided and Electrical energy spent by an auxiliary heater per each hour during a year.
                                        Electric auxiliary heater used.
                                        -
                                        In kWh.
        dischargedHeatPerHour: Discharged surplus energy ("heat dump") per each hour during a year.
                               It can be used to heat a pool, hot tub, greenhouse or as snow-melt system (by using radiant floor tubing bellow sidewalks, or radiatior beneath the entrance stairs).
                               -
                               In kWh.
        pumpEnergyPerHour: Electrical energy spent by the circulation pump(s) per hour during a year.
                           -
                           In kWh.
        tankWaterTemperaturePerHour: Tank water temperature per each hour during a year.
                                     -
                                     In C.
        SWHsurfaceTiltAngle: The angle from horizontal of the inclination of the SWHsurface. Example: 0 = horizontal, 90 = vertical.
                             It ranges from 0-180.
                             -
                             In degrees.
        SWHsurfaceAzimuthAngle: The orientation angle (clockwise from the true north) of the SWHsurface normal vector.
                                It ranges from 0-360.
                                -
                                In degrees.
        systemSize: Rated SWH system size. 
                    -
                    In kWt.
"""

ghenv.Component.Name = "Ladybug_Solar Water Heating Surface"
ghenv.Component.NickName = "SolarWaterHeatingSurface"
ghenv.Component.Message = 'VER 0.0.62\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleLBVersion = VER 0.0.61\nDEC_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import math
import re


def getEpwData(epwFile, albedo):
    
    if epwFile:
        try:
            # location data
            locationName, latitude, longitude, timeZone, elevation, locationString = lb_preparation.epwLocation(epwFile)
            # weather data
            weatherData = lb_preparation.epwDataReader(epwFile, locationName)
            dryBulbTemperature, dewPointTemperature, relativeHumidity, windSpeed, windDirection, directNormalRadiation, diffuseHorizontalRadiation, globalHorizontalRadiation, directNormalIlluminance, diffuseHorizontalIlluminance, globalHorizontalIlluminance, totalSkyCover, liquidPrecipitationDepth, barometricPressure, modelYear = weatherData
            
            Ta = dryBulbTemperature[7:]
            DNI = directNormalRadiation[7:]
            DHI = diffuseHorizontalRadiation[7:]
            yearsHOY = modelYear[7:]
            
            if (len(albedo) == 0) or (albedo[0] is ""):
                albedoL = lb_photovoltaics.calculateAlbedo(Ta)  # default
            elif (len(albedo) == 8767):
                albedoL = albedo[7:]
            elif (len(albedo) == 8760):
                albedoL = albedo
            else:
                locationName = latitude = longitude = timeZone = Ta = DNI = DHI = albedoL = yearsHOY = monthsHOY = daysHOY = hoursHOY = HOYs = None
                validEpwData = False
                printMsg = "Something is wrong with your \"albedo_\" list input.\n\"albedo_\" input accepts a list of 8767 (with header) or 8760 (without the header) abledo values."
                
                return locationName, latitude, longitude, timeZone, Ta, DNI, DHI, albedoL, yearsHOY, monthsHOY, daysHOY, hoursHOY, HOYs, validEpwData, printMsg
            
            monthsHOY = [1 for i in range(744)] + [2 for i in range(672)] + [3 for i in range(744)] + [4 for i in range(720)] + [5 for i in range(744)] + [6 for i in range(720)] + [7 for i in range(744)] + [8 for i in range(744)] + [9 for i in range(720)] + [10 for i in range(744)] + [11 for i in range(720)] + [12 for i in range(744)]
            
            numberOfDaysMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
            daysHOY = []
            day = 1
            for i,item in enumerate(numberOfDaysMonth):
                for k in range(item):
                    for g in range(24):
                        daysHOY.append(day)
                    day += 1
                day = 1
            
            hoursHOY = []
            hour = 1
            for i in range(365):
                for k in range(24):
                    hoursHOY.append(hour)
                    hour += 1
                hour = 1
            
            HOYs = range(1,8761)
            
            validEpwData = True
            printMsg = "ok"
            
            return locationName, float(latitude), float(longitude), float(timeZone), Ta, DNI, DHI, albedoL, yearsHOY, monthsHOY, daysHOY, hoursHOY, HOYs, validEpwData, printMsg
        
        except Exception, e:
            # something is wrong with "_epwFile" input
            locationName = latitude = longitude = timeZone = Ta = DNI = DHI = albedoL = yearsHOY = monthsHOY = daysHOY = hoursHOY = HOYs = None
            validEpwData = False
            printMsg = "Something is wrong with \"_epwFile\" input."
    else:
        locationName = latitude = longitude = timeZone = Ta = DNI = DHI = albedoL = yearsHOY = monthsHOY = daysHOY = hoursHOY = HOYs = None
        validEpwData = False
        printMsg = "Please supply .epw file path to \"_epwFile\" input."
    
    return locationName, latitude, longitude, timeZone, Ta, DNI, DHI, albedoL, yearsHOY, monthsHOY, daysHOY, hoursHOY, HOYs, validEpwData, printMsg


def heatingLoadSWHsurfaceInputData(heatingLoadPerHour, SWHsurface, SWHsurfacePercent, unitAreaConversionFactor):
    
    if (len(heatingLoadPerHour) == 0) or (heatingLoadPerHour[0] is ""):
        heatingLoadPerHourData = srfArea = SWHsurfacePercent = None
        validHeatingLoadSWHsurface = False
        printMsg = "Please input \"_heatingLoadPerHour\" data.\nUse Ladybug's \"Residential Hot Water\" or \"Commercial Public Apartment Hot Water\" components if you want to input domestic hot water heating load.\nFor space heating or cooling loads of a room or entire building, use Honeybee's \"Read EP Result\" component.\nYou call also use all three of these heating load types, or their combinations."
        
        return heatingLoadPerHourData, srfArea, SWHsurfacePercent, validHeatingLoadSWHsurface, printMsg
    elif (heatingLoadPerHour[0] == None):
        heatingLoadPerHourData = srfArea = SWHsurfacePercent = None
        validHeatingLoadSWHsurface = False
        printMsg = "Inputted \"_heatingLoadPerHour\" data's annual output is 0 kWh.\nPlease input the \"_heatingLoadPerHour\" which annual's output is higher than 0kwh.\nUse Ladybug's \"Residential Hot Water\" or \"Commercial Public Apartment Hot Water\" components to input domestic hot water heating load.\nAdditionally, for space heating and/or space cooling loads, use Honeybee's \"Read EP Result\" component."
        
        return heatingLoadPerHourData, srfArea, SWHsurfacePercent, validHeatingLoadSWHsurface, printMsg
    elif len(heatingLoadPerHour) == 8767:
        heatingLoadPerHourData = heatingLoadPerHour[7:]  # in kWh
    elif len(heatingLoadPerHour) == 8760:
        heatingLoadPerHourData = heatingLoadPerHour  # in kWh
    else:
        heatingLoadPerHourData = srfArea = SWHsurfacePercent = None
        validHeatingLoadSWHsurface = False
        printMsg = "Inputted \"_heatingLoadPerHour\" list does not have required length.\n\"_heatingLoadPerHour\" needs to be a list of either 8767 (heading plus values) or 8760 (only values) items.\nUse Ladybug's \"Residential Hot Water\" or \"Commercial Public Apartment Hot Water\" components to input domestic hot water heating load.\nAdditionally, for space heating and/or space cooling loads, use Honeybee's \"Read EP Result\" component."
        
        return heatingLoadPerHourData, srfArea, SWHsurfacePercent, validHeatingLoadSWHsurface, printMsg
    
    
    if (SWHsurface == None):
        heatingLoadPerHourData = srfArea = SWHsurfacePercent = None
        validHeatingLoadSWHsurface = False
        printMsg = "Please input planar Surface (not a polysurface) on which the SWH collectors will be applied.\n" + \
                   "Or create a Surface based on initial SWH system size by using \"PV SWH system size\" component."
        
        return heatingLoadPerHourData, srfArea, SWHsurfacePercent, validHeatingLoadSWHsurface, printMsg
    
    if (SWHsurfacePercent == None) or (SWHsurfacePercent < 0) or (SWHsurfacePercent > 100):
        SWHsurfacePercent = 100  # default value 100%
    
    # check SWHsurface input
    facesCount = SWHsurface.Faces.Count
    if facesCount > 1:
        # inputted polysurface
        heatingLoadPerHourData = srfArea = SWHsurfacePercent = None
        validHeatingLoadSWHsurface = False
        printMsg = "The brep you supplied to \"SWHsurface_\" is a polysurface. Please supply a surface."
        
        return heatingLoadPerHourData, srfArea, SWHsurfacePercent, validHeatingLoadSWHsurface, printMsg
    else:
        # inputted brep with a single surface
        srfArea = Rhino.Geometry.AreaMassProperties.Compute(SWHsurface).Area * (SWHsurfacePercent/100)  # area in document units
        srfArea = srfArea * unitAreaConversionFactor  # area in m2
        
        validHeatingLoadSWHsurface = True
        printMsg = "ok"
        
        return heatingLoadPerHourData, srfArea, SWHsurfacePercent, validHeatingLoadSWHsurface, printMsg


def SWHsystemSettingsInput(heatingLoadPerHourData, SWHsystemSettings, srfArea, dryBulbTemperature):
    
    # SWH system inputs
    if (len(SWHsystemSettings) != 23) and (len(SWHsystemSettings) != 0):
        coldWaterTemperaturePerHour = activeArea = nameplateThermalCapacity = SWHsystemSettings = None
        validSWHsystemSettings = False
        printMsg = "Your \"SWHsystemSettings_\" input is incorrect. Please use \"SWHsystemSettings\" output from \"Solar Water Heating System\" or \"Solar Water Heating System Detailed\" components."
        
        return coldWaterTemperaturePerHour, activeArea, nameplateThermalCapacity, SWHsystemSettings, validSWHsystemSettings, printMsg
    
    elif (len(SWHsystemSettings) == 0) or (SWHsystemSettings[0] is ""):
        # nothing inputted into "SWHsystemSettings_", use default SWHsystemSettings values
        collectorOpticalEfficiency = 0.70
        collectorThermalLoss = 4
        collectorActiveAreaPercent = 90
        workingFluidHeatCapacity = 3840
        flowRatePerM2 = 0.012
        IAMcoefficient = 0.1
        skyViewFactor = 1  # default - no shading
        beamIndexPerHourData = [1 for i in range(0,8760)]  # default - no shading
        maxWorkingTemperature = 95
        dischargeTemperature = 92
        deliveryWaterTemperature = 60
        avrJanuaryColdWaterTemperature = None
        mechanicalRoomTemperatureData = [20 for i in range(0,8760)]  # default 20C
        pipeLength = 20
        pipeDiameterMM = None  #math.sqrt((4 * (flowRatePerM2*collectorActiveArea)/0.7) / math.pi)
        pipeInsulationThicknessMM = None
        pipeInsulationConductivity = 0.027
        pumpPower = None
        pumpEfficiency = 0.85
        tankSizeLiters = None
        tankLoss = 0.30
        heightDiameterTankRatio = 2.6
        heatExchangerEffectiveness = 0.8
    elif (len(SWHsystemSettings) == 23):
        # 23 items inputted into "SWHsystemSettings_"
        collectorOpticalEfficiency = SWHsystemSettings[0]
        collectorThermalLoss = SWHsystemSettings[1]
        collectorActiveAreaPercent = SWHsystemSettings[2]
        workingFluidHeatCapacity = SWHsystemSettings[3]
        flowRatePerM2 = SWHsystemSettings[4]
        IAMcoefficient = SWHsystemSettings[5]
        skyViewFactor = SWHsystemSettings[6]
        beamIndexPerHourData = SWHsystemSettings[7]
        maxWorkingTemperature = SWHsystemSettings[8]
        dischargeTemperature = SWHsystemSettings[9]
        deliveryWaterTemperature = SWHsystemSettings[10]
        avrJanuaryColdWaterTemperature = SWHsystemSettings[11]
        mechanicalRoomTemperatureData = SWHsystemSettings[12]
        pipeLength = SWHsystemSettings[13]
        pipeDiameterMM = SWHsystemSettings[14]
        pipeInsulationThicknessMM = SWHsystemSettings[15]
        pipeInsulationConductivity = SWHsystemSettings[16]
        pumpPower = SWHsystemSettings[17]
        pumpEfficiency = SWHsystemSettings[18]
        tankSizeLiters = SWHsystemSettings[19]
        tankLoss = SWHsystemSettings[20]
        heightDiameterTankRatio = SWHsystemSettings[21]
        heatExchangerEffectiveness = SWHsystemSettings[22]
    
    # srfArea, activeArea, nameplateThermalCapacity
    activeArea = srfArea * (collectorActiveAreaPercent/100)  # in m2
    nameplateThermalCapacity = (activeArea*collectorOpticalEfficiency) - (collectorThermalLoss * 30/1000)  # in kWt
    
    try:
        # check the used coldWater_inputData for calculation of domestic hot water, from "Cold water temperature" component
        coldWater_inputData = sc.sticky["swh_coldWater_inputData"]
        method, minimalTemperature, pipesDepth, soilThermalDiffusivity = coldWater_inputData
    except:
        # domestic hot water is not included in "_heatingLoadPerHour" input, so by default:
        # method 1 (Christensen and Burch) is used to calculate the initial (tankSizeLiters_fromHWC) tank size
        method = 1; minimalTemperature = 1  # default: method 1 (Christensen and Burch), pipes depth from 0.3 to 1 meters, unknown soil type
    coldWaterTemperaturePerHour, coldWaterTemperaturePerYear, TcoldHOYminimal, TcoldHOYmaximal = lb_photovoltaics.inletWaterTemperature(dryBulbTemperature, method, minimalTemperature)
    if (avrJanuaryColdWaterTemperature == None):
        avrJanuaryColdWaterTemperature = sum(coldWaterTemperaturePerHour[:(31*24)])/(31*24)
    
    if (mechanicalRoomTemperatureData[0] == "air temperature"):
        mechanicalRoomTemperatureData = dryBulbTemperature
    
    if (pipeDiameterMM == None) or (pipeDiameterMM <= 0):
        # based on: Planning & Installing Solar Thermal Systems, Earthscan, 2nd edition
        flowSpeed = 0.7  # default in l/sec
        volumetricFlow = flowRatePerM2*activeArea * 3600  # in l/h
        pipeDiameterMM = math.sqrt((4 * volumetricFlow/flowSpeed) / math.pi)  # in mm
    pipeDiameterMM = math.ceil(pipeDiameterMM*10)/10  # round to 0.1 mm
    
    if (pipeInsulationThicknessMM == None) or (pipeInsulationThicknessMM < 0):
        # based on: EN 12976-2 standard
        if (pipeDiameterMM <= 22):
            pipeInsulationThicknessMM = 20
        elif (pipeDiameterMM > 22) and (pipeDiameterMM <= 28):
            pipeInsulationThicknessMM = 25
        elif (pipeDiameterMM > 28) and (pipeDiameterMM <= 42):
            pipeInsulationThicknessMM = 30
        elif (pipeDiameterMM > 42) and (pipeDiameterMM <= 100):
            pipeInsulationThicknessMM = pipeDiameterMM
        elif (pipeDiameterMM > 100):
            pipeInsulationThicknessMM = 100
    pipeInsulationThicknessM = pipeInsulationThicknessMM/1000  # convert to meters
    pipeDiameterM = pipeDiameterMM/1000  # convert from mm to m
    
    if (pumpPower == None) or (pumpPower < 0):
        # based on: Planning & Installing Solar Thermal Systems, Earthscan, 2nd edition
        if activeArea < 6:
            activeAreaCategory = 0
        elif (activeArea >= 6) and (activeArea < 13):
            activeAreaCategory = 1
        elif (activeArea >= 13) and (activeArea < 17):
            activeAreaCategory = 2
        elif (activeArea >= 17) and (activeArea < 21):
            activeAreaCategory = 3
        elif (activeArea >= 21) and (activeArea < 26):
            activeAreaCategory = 4
        elif (activeArea >= 26) and (activeArea < 30):
            activeAreaCategory = 5
        # RETscreen recommendation
        elif (activeArea >= 30) and (activeArea < 35):
            pumpPower = 185
        elif (activeArea >= 35) and (activeArea < 60):
            pumpPower = 205
        elif (activeArea > 60):
            pumpPower = 205 + 2*(round(activeArea)-60)
        
        if activeArea < 30:
            pumpPowerFromPipeLengthL = [[30, 36, 42, 49, 55, 55], [32, 39, 46, 53, 60], [37, 43, 49, 54, 60], [45, 49, 53, 57, 60], [45, 50, 56, 61, 67], [61, 67, 75, 82, 90]]
            pumpPowerFromPipeLengthSubItem = pumpPowerFromPipeLengthL[activeAreaCategory]
            if (pipeLength <= 10):
                pipeLengthIndex = 0
            elif (pipeLength > 10) and (pipeLength <= 20):
                pipeLengthIndex = 1
            elif (pipeLength > 20) and (pipeLength <= 30):
                pipeLengthIndex = 2
            elif (pipeLength > 30) and (pipeLength <= 40):
                pipeLengthIndex = 3
            elif (pipeLength > 40) and (pipeLength <= 50):
                pipeLengthIndex = 4
            
            if pipeLength <= 50:
                pumpPower = pumpPowerFromPipeLengthSubItem[pipeLengthIndex]
            else:
                pumpPower = int(pumpPowerFromPipeLengthSubItem[4] + math.ceil(6*(pipeLength-50)/10))
    
    # larger diameters for passive systems
    elif (pumpPower == 0):
        pipeDiameterM = 1.5 * pipeDiameterM
    
    # tank size based on HWCdailyAveragePerYear
    HWCL = []
    for i in range(1,8760):
        HWC = (heatingLoadPerHourData[i] * 859.8456)/(deliveryWaterTemperature - coldWaterTemperaturePerHour[i])  # in liters/hr
        HWCL.append(HWC)
    HWCdailyAveragePerYear = sum(HWCL)/365  # in liters
    tankSizeLiters_fromHWC = 1.5 * HWCdailyAveragePerYear # default (in liters)
    tankSizeLiters_fromHWC = math.ceil(tankSizeLiters_fromHWC/10)*10  # round to 10 liters
    
    if (tankSizeLiters == None) or (tankSizeLiters <= 0):
        tankSizeLiters = tankSizeLiters_fromHWC
    else:
        # some value has been inputted into the "tankSize_" input of the "SolarWaterHeting system" component
        pass
    
    if tankSizeLiters < 100:  # 100 liters, minimal tank size
        tankSizeLiters = 100  # in liters
    tankSizeM3 = tankSizeLiters/1000  # in m3
    
    if tankSizeLiters_fromHWC < 100:  # 100 liters, minimal tank size
        tankSizeLiters_fromHWC = 100  # in liters
    sc.sticky["swh_tankSizeM3_fromHWC"] = tankSizeLiters_fromHWC/1000
    
    SWHsystemSettings = [collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, workingFluidHeatCapacity, flowRatePerM2, IAMcoefficient, skyViewFactor, beamIndexPerHourData, maxWorkingTemperature, dischargeTemperature, deliveryWaterTemperature, avrJanuaryColdWaterTemperature, mechanicalRoomTemperatureData, pipeLength, pipeDiameterM, pipeInsulationThicknessM, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeM3, tankLoss, heightDiameterTankRatio, heatExchangerEffectiveness]
    
    validSWHsystemSettings = True
    printMsg = "ok"
    
    return coldWaterTemperaturePerHour, activeArea, nameplateThermalCapacity, SWHsystemSettings, validSWHsystemSettings, printMsg


def checkAnnualHourlyInputData(annualHourlyData):
    
    if annualHourlyData == []:
        annualHourlyDataLists = []
        annualHourlyDataListsEpwNames = []
        validAnnualHourlyData = True
        printMsg = "ok"
        return validAnnualHourlyData, annualHourlyDataLists, annualHourlyDataListsEpwNames, printMsg
    elif len(annualHourlyData) % 8767 != 0:
        annualHourlyDataLists = annualHourlyDataListsEpwNames = None
        validAnnualHourlyData = False
        printMsg = "Your annualHourlyData_ input is not correct. Please input complete 8767 items long list(s) from \"Ladybug_Import epw\" component"
        return annualHourlyDataLists, validAnnualHourlyData, annualHourlyDataListsEpwNames, printMsg
    else:
        annualHourlyDataLists = []
        annualHourlyDataListsEpwNames = []
        startIndex = 0
        endIndex = 8767
        for i in range(int(len(annualHourlyData)/8767)):
            untrimmedList = annualHourlyData[startIndex:endIndex]
            trimmedList = untrimmedList[7:]
            annualHourlyDataListsName = untrimmedList[2]
            annualHourlyDataLists.append(trimmedList)
            annualHourlyDataListsEpwNames.append(annualHourlyDataListsName)
            startIndex += 8767
            endIndex += 8767
        
        validAnnualHourlyData = True
        printMsg = "ok"
        return validAnnualHourlyData, annualHourlyDataLists, annualHourlyDataListsEpwNames, printMsg


def checkConditionalStatement(conditionalStatement, annualHourlyDataLists, annualHourlyDataListsEpwNames, weatherPerHourDataSubLists, addZero):
    
    if conditionalStatement == None and len(annualHourlyDataLists) > 0: # conditionalStatement_ not inputted, annualHourlyData_ inputted
        validConditionalStatement = False
        weatherPerHourDataConditionalStatementSubLists = conditionalStatementForFinalPrint = None
        printMsg = "Please supply \"conditionalStatement_\" for inputted \"annualHourlyData_\" data."
        return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg
    elif conditionalStatement == None and len(annualHourlyDataLists) == 0:  # conditionalStatement_ not inputted, annualHourlyData_ not inputted
        conditionalStatement = "True"
    else:  # conditionalStatement_ inputted, annualHourlyData_ not
        if annualHourlyDataLists == []:
            validConditionalStatement = False
            weatherPerHourDataConditionalStatementSubLists = conditionalStatementForFinalPrint = None
            printMsg = "Please supply \"annualHourlyData_\" data for inputted \"conditionalStatement_\"."
            return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg
        else:  # both conditionalStatement_ and annualHourlyData_ inputted
            conditionalStatement = conditionalStatement.lower()
            conditionalStatement = re.sub(r"\b([a-z])\b", r"\1[i]", conditionalStatement)
    
    annualHourlyDataListsNames = map(chr, range(97, 123))
    
    # finalPrint conditonal statements for "printOutput" function
    if conditionalStatement != "True":  # conditionalStatement_ not inputted
        # replace conditionalStatement annualHourlyDataListsNames[i] names with annualHourlyDataListsEpwNames:
        conditionalStatementForFinalPrint = conditionalStatement[:]
        for i in range(len(annualHourlyDataLists)):
            conditionalStatementForFinalPrint = conditionalStatementForFinalPrint.replace(annualHourlyDataListsNames[i]+"[i]", annualHourlyDataListsEpwNames[i])
    else:
        conditionalStatementForFinalPrint = "No condition"
    
    annualHourlyDataListsNames = map(chr, range(97, 123))
    numberOfLetters = 0
    
    for letter in annualHourlyDataListsNames:
        changedLetter = letter+"[i]"
        if changedLetter in conditionalStatement:
            numberOfLetters += 1
    if numberOfLetters > len(annualHourlyDataLists):
        validConditionalStatement = False
        weatherPerHourDataConditionalStatementSubLists = conditionalStatementForFinalPrint = None
        printMsg = "The number of a,b,c... variables you supplied in \"conditionalStatement_\" is larger than the number of \"annualHourlyData_\" lists you inputted. Please make the numbers of these two equal or less."
        return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg
    else:
        for i in range(len(annualHourlyDataLists)):
            exec("%s = %s" % (annualHourlyDataListsNames[i],annualHourlyDataLists[i]))
        
        try:
            weatherPerHourDataConditionalStatementSubLists = []
            for i in range(len(weatherPerHourDataSubLists)):
                weatherPerHourDataConditionalStatementSubLists.append([])
            for i in range(len(weatherPerHourDataSubLists[0])):
                exec("conditionalSt = %s" % conditionalStatement)
                if addZero == True:  # add 0 if conditionalStatement == False
                    if conditionalSt:
                        for k in range(len(weatherPerHourDataConditionalStatementSubLists)):
                            weatherPerHourDataConditionalStatementSubLists[k].append(weatherPerHourDataSubLists[k][i])
                    else:
                        for k in range(len(weatherPerHourDataConditionalStatementSubLists)):
                            weatherPerHourDataConditionalStatementSubLists[k].append(0)
                else:  # skip the value
                    if conditionalSt:
                        for k in range(len(weatherPerHourDataConditionalStatementSubLists)):
                            weatherPerHourDataConditionalStatementSubLists[k].append(weatherPerHourDataSubLists[k][i])
        except Exception, e:
            validConditionalStatement = False
            weatherPerHourDataConditionalStatementSubLists = conditionalStatementForFinalPrint = None
            printMsg = "Your \"conditionalStatement_\" is incorrect. Please provide a valid conditional statement in Python, such as \"a>25 and b<80\" (without the quotation marks)"
            return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg
        
        if len(weatherPerHourDataConditionalStatementSubLists[0]) == 0:
            validConditionalStatement = False
            weatherPerHourDataConditionalStatementSubLists = conditionalStatementForFinalPrint = None
            printMsg = "No \"annualHourlyData_\" coresponds to \"conditionalStatement_\". Please edit your \"conditionalStatement_\""
            return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg
        else:
            validConditionalStatement = True
            printMsg = "ok"
            return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg


def main(latitude, longitude, timeZone, locationName, years, months, days, hours, heatingLoadPerHour, coldWaterTemperaturePerHour, activeArea, srfTiltD, correctedSrfAzimuthD, dryBulbTemperature, directNormalRadiation, diffuseHorizontalRadiation, albedoL, SWHsystemSettings, conditionalStatementForFinalPrint):
    
    Fr, FrUL, dummycollectorActiveAreaPercent, Cp, mDot, bo, SVF, beamIndexPerHourData, TmaxW, TdischargeW, TdeliveryW, TcoldJanuaryW, TmechRoomL, L, Di, insulT, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeM3, tankLoss, heightDiameterTankRatio, epsilon = SWHsystemSettings
    heatFromTankPerHour = [0]
    heatFromAuxiliaryHeaterPerHour = [0]
    dischargedHeatPerHour = [0]
    pumpEnergyPerHour = [0]
    tankWaterTemperaturePerHour = [TcoldJanuaryW]
    beamRadiationPerHour = [0]
    diffuseRadiationPerHour = [0]
    groundRadiationPerHour = [0]
    AOI_RL = []
    
    tankArea = 2 * (((tankSizeM3**2)*math.pi*2*heightDiameterTankRatio) ** (1/3)) * (1+1/(2*heightDiameterTankRatio))
    
    for i in range(1,8760):
        sunZenithD, sunAzimuthD, sunAltitudeD = lb_photovoltaics.NRELsunPosition(latitude, longitude, timeZone, years[i], months[i], days[i], hours[i]-1)
        Epoa_shaded, Eb_shaded, Ed_sky, Eground, AOI_R = lb_photovoltaics.POAirradiance(sunZenithD, sunAzimuthD, srfTiltD, srfAzimuthD, directNormalRadiation[i], diffuseHorizontalRadiation[i], albedoL[i], beamIndexPerHourData[i], SVF)
        collectorHeatLoss, collectorEfficiency, Qsolar, Qloss, Qsupply, Qaux, Qdis, Qpump, dQ, dt, Tw = lb_photovoltaics.swhdesign(activeArea, srfTiltD, AOI_R, bo, Fr, FrUL, Eb_shaded, Ed_sky, Eground, heatingLoadPerHour[i], Cp, mDot, dryBulbTemperature[i], coldWaterTemperaturePerHour[i], tankWaterTemperaturePerHour[i-1], TdeliveryW, TmaxW, TdischargeW, TmechRoomL[i], L, Di, insulT, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeM3, tankArea, tankLoss, epsilon)
        heatFromTankPerHour.append(Qsupply)
        heatFromAuxiliaryHeaterPerHour.append(Qaux)
        dischargedHeatPerHour.append(Qdis)
        pumpEnergyPerHour.append(Qpump)
        tankWaterTemperaturePerHour.append(Tw)
        beamRadiationPerHour.append(Eb_shaded)
        diffuseRadiationPerHour.append(Ed_sky)
        groundRadiationPerHour.append(Eground)
        AOI_RL.append(AOI_R)
    
    heatFromTankPerYear = sum(heatFromTankPerHour)
    avrDailyheatFromTankPerYear = sum(heatFromTankPerHour)/365
    
    # adding headings to hourly and monthly lists
    heatFromTankPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Thermal energy from storage tank", "kWh", "Hourly", (1, 1, 1), (12, 31, 24)] + heatFromTankPerHour
    heatFromAuxiliaryHeaterPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Thermal energy from auxiliary heater", "kWh", "Hourly", (1, 1, 1), (12, 31, 24)] + heatFromAuxiliaryHeaterPerHour
    dischargedHeatPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Discharged thermal energy from storage tank", "kWh", "Hourly", (1, 1, 1), (12, 31, 24)] + dischargedHeatPerHour
    tankWaterTemperaturePerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Storage tank water temperature", "C", "Hourly", (1, 1, 1), (12, 31, 24)] + tankWaterTemperaturePerHour
    pumpEnergyPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Circulation pumps electricity consumption", "kWh", "Hourly", (1, 1, 1), (12, 31, 24)] + pumpEnergyPerHour
    
    # optimal collector area, tank storage volume initial data
    swh_inputData = [conditionalStatementForFinalPrint, activeArea, srfTiltD, AOI_RL, heatingLoadPerHour, beamRadiationPerHour, diffuseRadiationPerHour, groundRadiationPerHour, dryBulbTemperature, coldWaterTemperaturePerHour]+SWHsystemSettings
    sc.sticky["swh_inputData"] = swh_inputData
    
    return heatFromTankPerHour, heatFromTankPerYear, avrDailyheatFromTankPerYear, heatFromAuxiliaryHeaterPerHour, dischargedHeatPerHour, pumpEnergyPerHour, tankWaterTemperaturePerHour


def printOutput(locationName, latitude, longitude, north, albedoL, heatingLoadPerHourData, SWHsurfacePercent, srfArea, activeArea, nameplateThermalCapacity, srfAzimuthD, srfTiltD, SWHsystemSettings, conditionalStatementForFinalPrint):
    
    collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, workingFluidHeatCapacity, flowRatePerM2, IAMcoefficient, skyViewFactor, beamIndexPerHourData, maxWorkingTemperature, dischargeTemperature, deliveryWaterTemperature, avrJanuaryColdWaterTemperature, mechanicalRoomTemperatureData, pipeLength, pipeDiameterM, pipeInsulationThicknessM, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeM3, tankLoss, heightDiameterTankRatio, heatExchangerEffectiveness = SWHsystemSettings
    resultsCompletedMsg = "SWHsurface component results successfully completed!"
    printOutputMsg = \
    """
Input data:

Location: %s
Latitude (): %s
Longitude (): %s
North (): %s
Average annual albedo(-): %0.2f

Average heating load per day (kWh/day): %0.2f
Surface percentage used for SWH collectors (percent): %0.2f
Surface area (m2): %0.2f
Surface active area (m2): %0.2f
Nameplate thermal capacity (kWt): %0.2f
Surface azimuth angle (): %0.2f
Surface tilt angle (): %0.2f


SWH system:

Collector optical efficiency (-): %0.2f
Collector thermal loss (W/m2/C): %0.2f
Collector active area percent (percent): %0.2f
Working fluid heat capacity (J/kg/C): %0.2f
Flow rate per M2 (kg/s/m2): %0.3f
IAM modifier coefficient (-): %0.2f
Sky View Factor: %0.2f
Average annual Transmission index of beam irradiance (-): %0.2f
-----
Max working temperature (C): %0.2f
Discharge temperature (C): %0.2f
Delivery water temperature (C): %0.2f
Average January cold water temperature (C): %0.2f
Average mechanical room temperature (C): %0.2f
-----
Pipe length (m): %0.2f
Pipe diameter (mm): %0.2f
Pipe insulation thickness (mm): %0.2f
Pipe insulation conductivity (W/m/C): %0.2f
Pump power (W): %0.2f
Pump efficiency (-): %0.2f
-----
Tank size (l): %0.2f
Tank loss (W/m2/C): %0.2f
Height-diameter tank ratio (-): %0.2f
Heat exchanger effectiveness (-): %0.2f

Caclulation based on the following condition:
%s
    """ % (locationName, latitude, longitude, north, sum(albedoL)/8760, sum(heatingLoadPerHourData)/365, SWHsurfacePercent, srfArea, activeArea, nameplateThermalCapacity, srfAzimuthD, srfTiltD, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, workingFluidHeatCapacity, flowRatePerM2, IAMcoefficient, skyViewFactor, sum(beamIndexPerHourData)/len(beamIndexPerHourData), maxWorkingTemperature, dischargeTemperature, deliveryWaterTemperature, avrJanuaryColdWaterTemperature, sum(mechanicalRoomTemperatureData)/len(mechanicalRoomTemperatureData), pipeLength, pipeDiameterM*1000, pipeInsulationThicknessM, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeM3*1000, tankLoss, heightDiameterTankRatio, heatExchangerEffectiveness, conditionalStatementForFinalPrint)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        if _epwFile:
            locationName, latitude, longitude, timeZone, dryBulbTemperature, directNormalRadiation, diffuseHorizontalRadiation, albedoL, years, months, days, hours, HOYs, validEpwData, printMsg = getEpwData(_epwFile, albedo_)
            if validEpwData:
                unitConversionFactor = lb_preparation.checkUnits()
                unitAreaConversionFactor = unitConversionFactor**2
                heatingLoadPerHourData, srfArea, SWHsurfacePercent, validHeatingLoadSWHsurface, printMsg = heatingLoadSWHsurfaceInputData(_heatingLoadPerHour, _SWHsurface, SWHsurfacePercent_, unitAreaConversionFactor)
                if validHeatingLoadSWHsurface:
                    coldWaterTemperaturePerHour, activeArea, nameplateThermalCapacity, SWHsystemSettings, validSWHsystemSettings, printMsg = SWHsystemSettingsInput(heatingLoadPerHourData, SWHsystemSettings_, srfArea, dryBulbTemperature)
                    if validSWHsystemSettings:
                        validAnnualHourlyData, annualHourlyDataLists, annualHourlyDataListsEpwNames, printMsg = checkAnnualHourlyInputData(annualHourlyData_)
                        if validAnnualHourlyData:
                            validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg = checkConditionalStatement(conditionalStatement_, annualHourlyDataLists, annualHourlyDataListsEpwNames, [directNormalRadiation, diffuseHorizontalRadiation], True)
                            if validConditionalStatement:
                                directNormalRadiationCondStat, diffuseHorizontalRadiationCondStat = weatherPerHourDataConditionalStatementSubLists
                                # all inputs ok
                                if _runIt:
                                    SWHsurfaceTiltAngle_ = None; SWHsurfaceAzimuthAngle_ = None; SWHsurfaceInputType = "brep"
                                    srfAzimuthD, surfaceTiltDCalculated = lb_photovoltaics.srfAzimuthAngle(SWHsurfaceAzimuthAngle_, SWHsurfaceInputType, rs.coercegeometry(_SWHsurface), latitude)
                                    correctedSrfAzimuthD, northDeg, validNorth, printMsg = lb_photovoltaics.correctSrfAzimuthDforNorth(north_, srfAzimuthD)
                                    srfTiltD = lb_photovoltaics.srfTiltAngle(SWHsurfaceTiltAngle_, surfaceTiltDCalculated, SWHsurfaceInputType, rs.coercegeometry(_SWHsurface), latitude)
                                    heatFromTankPerHour, heatFromTankPerYear, avrDailyheatFromTankPerYear, heatFromAuxiliaryHeaterPerHour, dischargedHeatPerHour, pumpEnergyPerHour, tankWaterTemperaturePerHour = main(latitude, longitude, timeZone, locationName, years, months, days, hours, heatingLoadPerHourData, coldWaterTemperaturePerHour, activeArea, srfTiltD, correctedSrfAzimuthD, dryBulbTemperature, directNormalRadiationCondStat, diffuseHorizontalRadiationCondStat, albedoL, SWHsystemSettings, conditionalStatementForFinalPrint)
                                    printOutput(locationName, latitude, longitude, northDeg, albedoL, heatingLoadPerHourData, SWHsurfacePercent, srfArea, activeArea, nameplateThermalCapacity, srfAzimuthD, srfTiltD, SWHsystemSettings, conditionalStatementForFinalPrint)
                                    SWHsurfaceTiltAngle = srfTiltD; SWHsurfaceAzimuthAngle = correctedSrfAzimuthD; systemSize = nameplateThermalCapacity
                                else:
                                    print "All inputs are ok. Please set the \"_runIt\" to True, in order to run the Solar water heating surface component"
                            else:
                                print printMsg
                                ghenv.Component.AddRuntimeMessage(level, printMsg)
                        else:
                            print printMsg
                            ghenv.Component.AddRuntimeMessage(level, printMsg)
                    else:
                        print printMsg
                        ghenv.Component.AddRuntimeMessage(level, printMsg)
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
