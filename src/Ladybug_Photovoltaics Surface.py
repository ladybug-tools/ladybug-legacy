# Photovoltaics surface
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Djordje Spasic and Jason Sensibaugh <djordjedspasic@gmail.com and sensij@yahoo.com> 
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
Use this component to calculate amount of electrical energy that can be produced by a surface
if a certain percentage of it is covered with Photovoltaics.
Component based on NREL PVWatts v1 fixed tilt calculator for crystalline silicon (c-Si) photovoltaics.
-
Sources:
http://www.nrel.gov/docs/fy14osti/60272.pdf
https://pvpmc.sandia.gov
-
Provided by Ladybug 0.0.62
    
    input:
        _epwFile: Input .epw file path by using the "File Path" parameter, or Ladybug's "Open EPW And STAT Weather Files" component.
        _PVsurface: - Input planar Grasshopper/Rhino Surface (not a polysurface) on which the PV modules will be applied. If you have a polysurface, explode it (using "Deconstruct Brep" component) and then feed its Faces(F) output to _PVsurface. Surface normal should be faced towards the sun.
                    - Or create the Surface based on initial PV system size by using "PV SWH system size" component.
        PVsurfacePercent_: The percentage of surface which will be used for PV modules (range 0-100).
                           -
                           Some countries and states, have local codes which limit the portion of the roof, which can be covered by crystalline silicon modules. For example, this may include having setbacks(distances) of approximatelly 90cm from side and top edges of a roof, as a fire safety regulation.
                           -
                           If not supplied, default value of 100 (all surface area will be covered in PV modules) is used.
                           -
                           In percent (%).
        DCtoACderateFactor_: Factor which accounts for various locations and instances in a PV system where power is lost from DC system nameplate to AC power. It ranges from 0 to 1.
                             It can be calculated with Ladybug's "DC to AC derate factor" component.
                             -
                             If not supplied, default value of 0.85 will be used.
        PVmoduleSettings_: A list of PV module settings. Use the "Photovoltaics module" component to generate them.
                           -
                           If not supplied, the following PV module settings will be used by default:
                           - moduleType: Close (flush) roof mount
                           - moduleEfficiency: 15 %
                           - temperatureCoefficient: -0.5 %/C
                           - moduleActiveAreaPercent: 90 %
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
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
        conditionalStatement_: This input allows users to calculate the Photovoltaics surface component results only for those annualHourlyData_ values which fit specific conditions or criteria. To use this input correctly, hourly data, such as dryBulbTemperature or windSpeed, must be plugged into the "annualHourlyData_" input. The conditional statement input here should be a valid condition statement in Python, such as "a>25" or "b<3" (without the quotation marks).
                               conditionalStatement_ accepts "and" and "or" operators. To visualize the hourly data, English letters should be used as variables, and each letter alphabetically corresponds to each of the lists (in their respective order): "a" always represents the 1st list, "b" always represents the 2nd list, etc.
                               -
                               For example, if you have an hourly dryBulbTemperature connected as the first list, and windSpeed connected as the second list (both to the annualHourlyData_ input), and you want to plot the data for the time period when temperature is between 18C and 23C, and windSpeed is larger than 3m/s, the conditionalStatement_ should be written as "18<a<23 and b>3" (without the quotation marks).
        _runIt: ...
        
    output:
        readMe!: ...
        ACenergyPerHour: AC power output for each hour during a year.
                         -
                         In kWh.
        ACenergyPerYear: Total AC power output for a whole year.
                         -
                         In kWh.
        averageDailyACenergyPerYear: An average AC power output per day for a whole year.
                                     -
                                     In kWh/day.
        DCenergyPerHour: DC power output of the PV array for each hour during a year.
                         -
                         In kWh.
        totalRadiationPerHour: Total Incident POA (Plane of array) irradiance for each hour during a year.
                               -
                               In kWh/m2.
        moduleTemperaturePerHour: Module's back surface temperature for each hour during year.
                                  -
                                  In C.
        cellTemperaturePerHour: Cell temperature for each hour during year.
                                -
                                In C.
        PVsurfaceTiltAngle: The angle from horizontal of the inclination of the PVsurface. Example: 0 = horizontal, 90 = vertical.
                            It ranges from 0-180.
                            -
                            In degrees.
        PVsurfaceAzimuthAngle: The orientation angle (clockwise from the true north) of the PVsurface normal vector.
                               It ranges from 0-360.
                               -
                               In degrees.
        systemSize: DC rating of the PV system.
                    -
                    In kW.
"""

ghenv.Component.Name = "Ladybug_Photovoltaics Surface"
ghenv.Component.NickName = "PhotovoltaicsSurface"
ghenv.Component.Message = 'VER 0.0.62\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.61\nDEC_05_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
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
            ws = windSpeed[7:]
            DNI = directNormalRadiation[7:]
            DHI = diffuseHorizontalRadiation[7:]
            
            if (len(albedo) == 0) or (albedo[0] is ""):
                albedoL = lb_photovoltaics.calculateAlbedo(Ta)  # default
            elif (len(albedo) == 8767):
                albedoL = albedo[7:]
            elif (len(albedo) == 8760):
                albedoL = albedo
            else:
                locationName = latitude = longitude = timeZone = Ta = ws = DNI = DHI = yearsHOY = monthsHOY = daysHOY = hoursHOY = HOYs = albedoL = None
                validEpwData = False
                printMsg = "Something is wrong with your \"albedo_\" list input.\n\"albedo_\" input accepts a list of 8767 (with header) or 8760 (without the header) abledo values."
                
                return locationName, latitude, longitude, timeZone, Ta, ws, DNI, DHI, yearsHOY, monthsHOY, daysHOY, hoursHOY, HOYs, albedoL, validEpwData, printMsg
            
            yearsHOY = modelYear[7:]
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
            
            return locationName, float(latitude), float(longitude), float(timeZone), Ta, ws, DNI, DHI, yearsHOY, monthsHOY, daysHOY, hoursHOY, HOYs, albedoL, validEpwData, printMsg
        
        except Exception, e:
            # something is wrong with "_epwFile" input
            locationName = latitude = longitude = timeZone = Ta = ws = DNI = DHI = yearsHOY = monthsHOY = daysHOY = hoursHOY = HOYs = albedoL = None
            validEpwData = False
            printMsg = "Something is wrong with \"_epwFile\" input."
    else:
        locationName = latitude = longitude = timeZone = Ta = ws = DNI = DHI = yearsHOY = monthsHOY = daysHOY = hoursHOY = HOYs = albedoL = None
        validEpwData = False
        printMsg = "Please supply .epw file path to \"_epwFile\" input."
    
    return locationName, latitude, longitude, timeZone, Ta, ws, DNI, DHI, yearsHOY, monthsHOY, daysHOY, hoursHOY, HOYs, albedoL, validEpwData, printMsg


def PVsurfaceInputData(PVsurface, PVsurfacePercent, unitAreaConversionFactor, DCtoACderateFactor, PVmoduleSettings):
    
    if (PVsurface == None):
        PVsurfaceInputType = nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = DCtoACderateFactor = moduleType = moduleEfficiency = temperatureCoefficientFraction = moduleActiveAreaPercent = None
        validPVsurfaceData = False
        printMsg = "Please input planar Surface (not a polysurface) on which the PV modules will be applied.\n" + \
                   "Or create a Surface based on initial PV system size by using \"PV SWH system size\" component."
        
        return PVsurfaceInputType, nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, DCtoACderateFactor, moduleType, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, validPVsurfaceData, printMsg
    
    if (PVsurfacePercent == None) or (PVsurfacePercent < 0) or (PVsurfacePercent > 100):
        PVsurfacePercent = 100  # default value 100%
    
    if (DCtoACderateFactor == None) or (DCtoACderateFactor < 0) or (DCtoACderateFactor > 1):
        DCtoACderateFactor = 0.85  # default value (corresponds to 11.42% of PVWatts v5 Total Losses)
    
    # PV module settings inputs
    if (len(PVmoduleSettings) != 4) and (len(PVmoduleSettings) != 0):
        PVsurfaceInputType = nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = DCtoACderateFactor = moduleType = moduleEfficiency = temperatureCoefficientFraction = moduleActiveAreaPercent = None
        validSWHsurfaceSystemData = False
        printMsg = "Your \"PVmoduleSettings_\" input is incorrect. Please use \"PVmoduleSettings\" output from \"Photovoltaics module\" component."
        
        return PVsurfaceInputType, nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, DCtoACderateFactor, moduleType, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, validPVsurfaceData, printMsg
    
    elif (len(PVmoduleSettings) == 0) or (PVmoduleSettings[0] is ""):
        # nothing inputted into "PVmoduleSettings_", use default PVmoduleSettings values
        moduleType = 1  # Glass/cell/glass, Close (flush) roof mount
        moduleEfficiency = 15  # for crystalline silicon
        temperatureCoefficientPercent = -0.5  # in %, for crystalline silicon
        moduleActiveAreaPercent = 90  # default value in %
    
    elif (len(PVmoduleSettings) == 4):
        # 4 items inputted into "PVmoduleSettings_"
        moduleType = PVmoduleSettings[0]
        moduleEfficiency = PVmoduleSettings[1]
        temperatureCoefficientPercent = PVmoduleSettings[2]
        moduleActiveAreaPercent = PVmoduleSettings[3]
    
    temperatureCoefficientFraction = temperatureCoefficientPercent/100  # unitless
    
    
    # check PVsurface input
    PVsurfaceInputType = "brep"
    facesCount = PVsurface.Faces.Count
    if facesCount > 1:
        # inputted polysurface
        PVsurfaceInputType = nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = DCtoACderateFactor = moduleType = moduleEfficiency = temperatureCoefficientFraction = moduleActiveAreaPercent = None
        validPVsurfaceData = False
        printMsg = "The brep you supplied to \"_PVsurface\" is a polysurface. Please supply a surface"
        
        return PVsurfaceInputType, nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, DCtoACderateFactor, moduleType, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, validPVsurfaceData, printMsg
    else:
        # inputted brep with a single surface
        srfArea = Rhino.Geometry.AreaMassProperties.Compute(PVsurface).Area * (PVsurfacePercent/100)  # area in document units
        srfArea = srfArea * unitAreaConversionFactor  # area in m2
        activeArea = srfArea * (moduleActiveAreaPercent/100)  # in m2
        nameplateDCpowerRating = activeArea * (1 * (moduleEfficiency/100))  # in kW
        validPVsurfaceData = True
        printMsg = "ok"
        
        return PVsurfaceInputType, nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, DCtoACderateFactor, moduleType, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, validPVsurfaceData, printMsg


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


def main(latitude, longitude, timeZone, locationName, years, months, days, hours, HOYs, nameplateDCpowerRating, DCtoACderateFactor, srfArea, srfTiltD, srfAzimuthD, moduleType, moduleEfficiency, temperatureCoefficientFraction, dryBulbTemperature, windSpeed, directNormalRadiation, diffuseHorizontalRadiation, albedoL, conditionalStatementForFinalPrint):
    # solar radiation, AC,DC power output, module temperature, cell temperature
    ACenergyPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "AC power output", "kWh", "Hourly", (1, 1, 1), (12, 31, 24)]
    DCenergyPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "DC power output", "kWh", "Hourly", (1, 1, 1), (12, 31, 24)]
    totalRadiationPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Total POA irradiance", "kWh/m2", "Hourly", (1, 1, 1), (12, 31, 24)]
    moduleTemperaturePerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Module temperature", "C", "Hourly", (1, 1, 1), (12, 31, 24)]
    cellTemperaturePerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Cell temperature", "C", "Hourly", (1, 1, 1), (12, 31, 24)]
    beamRadiationPerHour = []
    diffuseRadiationPerHour = []
    groundRadiationPerHour = []
    AOI_RL = []
    
    for i,hoy in enumerate(HOYs):
        sunZenithD, sunAzimuthD, sunAltitudeD = lb_photovoltaics.NRELsunPosition(latitude, longitude, timeZone, years[i], months[i], days[i], hours[i]-1)
        Epoa, Eb, Ed_sky, Eground, AOI_R = lb_photovoltaics.POAirradiance(sunZenithD, sunAzimuthD, srfTiltD, srfAzimuthD, directNormalRadiation[i], diffuseHorizontalRadiation[i], albedoL[i])
        Tm, Tcell, Pdc_, Pac = lb_photovoltaics.pvwatts(nameplateDCpowerRating, DCtoACderateFactor, AOI_R, Epoa, Eb, Ed_sky, Eground, moduleType, temperatureCoefficientFraction, dryBulbTemperature[i], windSpeed[i], directNormalRadiation[i], diffuseHorizontalRadiation[i])
        Epoa = Epoa/1000 # to kWh/m2
        ACenergyPerHour.append(Pac)
        DCenergyPerHour.append(Pdc_)
        totalRadiationPerHour.append(Epoa)
        moduleTemperaturePerHour.append(Tm)
        cellTemperaturePerHour.append(Tcell)
        beamRadiationPerHour.append(Eb)
        diffuseRadiationPerHour.append(Ed_sky)
        groundRadiationPerHour.append(Eground)
        AOI_RL.append(AOI_R)
    
    ACenergyPerYear = sum(ACenergyPerHour[7:])  # in kWh
    averageDailyACenergyPerYear = ACenergyPerYear/365  # in kWh/day
    
    # optimal pv surface initial data
    pv_inputData = [conditionalStatementForFinalPrint, DCtoACderateFactor, moduleType, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, AOI_RL, [Epoa*1000 for index,Epoa in enumerate(totalRadiationPerHour) if index >= 7], beamRadiationPerHour, diffuseRadiationPerHour, groundRadiationPerHour, dryBulbTemperature, windSpeed, directNormalRadiation, diffuseHorizontalRadiation]
    sc.sticky["pv_inputData"] = pv_inputData
    
    return ACenergyPerHour, ACenergyPerYear, averageDailyACenergyPerYear, DCenergyPerHour, totalRadiationPerHour, moduleTemperaturePerHour, cellTemperaturePerHour


def printOutput(unitAreaConversionFactor, locationName, latitude, longitude, northDeg, albedoL, nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, DCtoACderateFactor, srfTiltD, srfAzimuthD, moduleType, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, conditionalStatementForFinalPrint):
    resultsCompletedMsg = "PVsurface component results successfully completed!"
    moduleTypesL = ["Glass/cell/polymer sheet Insulated back", "Glass/cell/glass Close (flush) roof mount", "Glass/cell/polymer sheet Open rack", "Glass/cell/glass Open rack"]
    model = moduleTypesL[moduleType]
    printOutputMsg = \
    """
Input data:

Location: %s
Latitude (): %s
Longitude (): %s
North (): %s
Average annual albedo(-): %0.2f

Surface percentage used for PV modules (percent): %0.2f
Surface area (m2): %0.2f
Surface active area (m2): %0.2f
Array type: fixed tilt
Surface tilt angle (): %0.2f
Surface azimuth angle (): %0.2f

Overall DC to AC derate factor (-): %0.3f

Module type and mounting: %0.2f (%s)
Module efficiency (percent): %0.2f
Module's temperature coefficient (percent/C): %0.2f
Module active area Percentage (percent): %0.2f

System size (kW): %0.2f

Caclulation based on the following condition:
%s
    """ % (locationName, latitude, longitude, northDeg, sum(albedoL)/8760, PVsurfacePercent, srfArea, activeArea, srfTiltD, srfAzimuthD, DCtoACderateFactor, moduleType, model, moduleEfficiency, temperatureCoefficientFraction*100, moduleActiveAreaPercent, nameplateDCpowerRating, conditionalStatementForFinalPrint)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        if _epwFile:
            locationName, latitude, longitude, timeZone, dryBulbTemperature, windSpeed, directNormalRadiation, diffuseHorizontalRadiation, years, months, days, hours, HOYs, albedoL, validEpwData, printMsg = getEpwData(_epwFile, albedo_)
            if validEpwData:
                moduleActiveAreaPercent_ = moduleType_ = moduleEfficiency_ = None
                unitConversionFactor = lb_preparation.checkUnits()
                unitAreaConversionFactor = unitConversionFactor**2
                PVsurfaceInputType, nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, DCtoACderateFactor, moduleType, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, validPVsurfaceData, printMsg = PVsurfaceInputData(_PVsurface, PVsurfacePercent_, unitAreaConversionFactor, DCtoACderateFactor_, PVmoduleSettings_)
                if validPVsurfaceData:
                    validAnnualHourlyData, annualHourlyDataLists, annualHourlyDataListsEpwNames, printMsg = checkAnnualHourlyInputData(annualHourlyData_)
                    if validAnnualHourlyData:
                        validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg = checkConditionalStatement(conditionalStatement_, annualHourlyDataLists, annualHourlyDataListsEpwNames, [dryBulbTemperature, windSpeed, directNormalRadiation, diffuseHorizontalRadiation], True)
                        if validConditionalStatement:
                            dryBulbTemperatureCondStat, windSpeedCondStat, directNormalRadiationCondStat, diffuseHorizontalRadiationCondStat = weatherPerHourDataConditionalStatementSubLists
                            # all inputs ok
                            if _runIt:
                                PVsurfaceTiltAngle_ = None; PVsurfaceAzimuthAngle_ = None
                                srfAzimuthD, surfaceTiltDCalculated = lb_photovoltaics.srfAzimuthAngle(PVsurfaceAzimuthAngle_, PVsurfaceInputType, _PVsurface, latitude)
                                correctedSrfAzimuthD, northDeg, validNorth, printMsg = lb_photovoltaics.correctSrfAzimuthDforNorth(north_, srfAzimuthD)
                                srfTiltD = lb_photovoltaics.srfTiltAngle(PVsurfaceTiltAngle_, surfaceTiltDCalculated, PVsurfaceInputType, _PVsurface, latitude)
                                ACenergyPerHour, ACenergyPerYear, averageDailyACenergyPerYear, DCenergyPerHour, totalRadiationPerHour, moduleTemperaturePerHour, cellTemperaturePerHour = main(latitude, longitude, timeZone, locationName, years, months, days, hours, HOYs, nameplateDCpowerRating, DCtoACderateFactor, srfArea, srfTiltD, correctedSrfAzimuthD, moduleType, moduleEfficiency, temperatureCoefficientFraction, dryBulbTemperatureCondStat, windSpeedCondStat, directNormalRadiationCondStat, diffuseHorizontalRadiationCondStat, albedoL, conditionalStatementForFinalPrint)
                                printOutput(unitAreaConversionFactor, locationName, latitude, longitude, northDeg, albedoL, nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, DCtoACderateFactor, srfTiltD, correctedSrfAzimuthD, moduleType, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, conditionalStatementForFinalPrint)
                                systemSize = nameplateDCpowerRating; PVsurfaceTiltAngle = srfTiltD; PVsurfaceAzimuthAngle = correctedSrfAzimuthD
                            else:
                                print "All inputs are ok. Please set the \"_runIt\" to True, in order to run the Photovoltaics surface component"
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