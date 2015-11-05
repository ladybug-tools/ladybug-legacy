# Photovoltaics performance metrics
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Djordje Spasic <djordjedspasic@gmail.com> 
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
Use this component to calculate various Photovoltaics performance metrics

-
Provided by Ladybug 0.0.61
    
    input:
        _PVsurface: - Input planar Surface (not polysurface) on which the PV modules will be applied. If you have a polysurface, explode it (using "Deconstruct Brep" component) and then feed its Faces(F) output to _PVsurface. Surface normal should be faced towards the sun.
                    - Or input surface Area, in square meters (example: "100").
                    - Or input PV system size (nameplate DC power rating), in kiloWatts at standard test conditions (example: "4 kw").
        PVsurfacePercent_: The percentage of surface which will be used for PV modules (range 0-100).
                           -
                           Some countries and states, have local codes which limit the portion of the roof, which can be covered by crystalline silicon modules. For example, this may include having setbacks(distances) of approximatelly 90cm from side and top edges of a roof, as a fire safety regulation.
                           -
                           If not supplied, default value of 100 (all surface area will be covered in PV modules) is used.
        moduleActiveAreaPercent_: Percentage of the module's area excluding module framing and gaps between cells. 
                                  -
                                  If not supplied, default value of 90(%) will be used.
        moduleEfficiency_: The ratio of energy output from the PV module to input energy from the sun. It ranges from 0 to 100 (%).
                           -
                           If not defined, default value of 15(%) will be used.
        lifetime_: Life expectancy of a PV module. In years.
                   -
                   If not supplied default value of 30 (years) will be used.
        _ACenergyPerHour: Import "ACenergyPerYear" output data from "Photovoltaics surface" component.
                          In kWh.
        _totalRadiationPerHour: Import "totalRadiationPerHour" output data from "Photovoltaics surface" component.
                                In kWh/m2.
        _cellTemperaturePerHour: Import "cellTemperaturePerHour" output data from "Photovoltaics surface" component.
                                 In C.
        ACenergyDemandPerHour_: Required electrical energy used for any kind of load: heating, cooling, electric lights, solar water heating circulation pump etc.
                                For example, any of the Honeybee's "Read EP Result" outputs can be inputted in here. Either separately or summed.
                                -
                                If nothing inputted, this input will be neglected (there is no required electrical energy).
                                In kWh.
        energyCostPerKWh_: The cost of one kilowatt hour in any currency unit (dollar, euro, yuan...)
                           -
                           If not supplied, 0.15 $/kWh will be used as default value.
        embodiedEnergyPerM2_: Energy necessary for an entire product life-cycle of PV module per square meter.
                             In MJ/m2 (megajoules per square meter).
                             -
                             If not supplied default value of 4410 (MJ/m2) will be used.
        embodiedCO2PerM2_: Carbon emissions produced during PV module's life-cycle per square meter..
                          In kg CO2/m2 (kilogram of CO2 per square meter).
                          -
                          If not supplied default value of 225 (kg CO2/m2) will be used.
        gridEfficiency_: An average primary energy to electricity conversion efficiency.
                        -
                        If not supplied default value of 29 (%) will be used.
        _runIt: ...
        
    output:
        readMe!: ...
        CUFperYear: Capacity Utilization Factor (sometimes called Plant Load Factor (PLF)) - ratio of the annual AC power output and maximum possible output under ideal conditions if the sun shone throughout the day and throughout the year.
                    It is sometimes used by investors or developers for Financial and Maintenance analysis of the PV systems, instead of "basicPRperYear" (e.g. in India).
                    -
                    In percent (%).
        basicPRperYear: Basic Performance Ratio - ratio of the actual and theoretically possible annual energy output.
                        It is worldwide accepted standard metric for measuring the performance of the PV system, therefor it is used for Maintenance analysis of PV systems.
                        Used for Maintenance analysis of PV systems.
                        -
                        basicPR is more precise than upper "CUF" and should be used instead of it, unless "CUF" is specifically required.
                        -
                        In percent(%).
        temperatureCorrectedPRperMonth: Temperature corrected Performance Ratio - ratio of the actual and theoretically possible energy output per month, corrected for PV module's Cell temperature. Mid-day hours (solarRadiation > 0.6 kWh/m2) only taken into account.
                                        -
                                        It is more precise than upper "basicPR" and should be used instead of it, unless "basicPR" is specifically required.
                                        -
                                        In percent(%).
        temperatureCorrectedPRperYear: Temperature corrected Performance Ratio - ratio of the actual and theoretically possible annual energy output, corrected for PV module's Cell temperature. Mid-day hours (solarRadiation > 0.6 kWh/m2) only taken into account.
                                       -
                                       It is more precise than upper "basicPR" and should be used instead of it, unless "basicPR" is specifically required.
                                       -
                                       In percent(%).
        energyOffsetPerMonth: Percentage of the electricity demand covered by Photovoltaics system for each month.
                              -
                              It is used for Financial and Maintenance analysis of the PV system.
                              -
                              In percent(%).
        energyOffsetPerYear: Percentage of the total annual electricity demand covered by Photovoltaics system for a whole year.
                             -
                             It is used for Financial and Maintenance analysis of the PV system.
                             -
                             In percent(%).
        energyValuePerMonth: Total Energy value for each month in currency unit (dollars, euros, yuans...)
                             -
                             It is used for Financial analysis of the PV system.
        energyValuePerYear: Total Energy value for whole year in currency unit (dollars, euros, yuans...)
                            -
                            It is used for Financial analysis of the PV system.
        Yield: Ratio of annual AC power output and nameplate DC power rating.
               It is used for Financial analysis of the PV systems.
               -
               In hours (h).
        EROI: Energy Return On Investment - a comparison of the generated electricity to the amount of primary energy used throughout the PV module's product life-cycle.
              -
              It is used for Financial analysis of the PV system.
              -
              Unitless.
        embodiedEnergy: Total energy necessary for an entire product life-cycle of PV modules.
                        -
                        It used for the Life Cycle analysis of the PV system.
                        -
                        In GJ (gigajoules).
        embodiedCO2: Total carbon emissions produced during PV module's life-cycle.
                     -
                     It used for the Life Cycle analysis of the PV system.
                     -
                     In tCO2 (tons of CO2).
        CO2emissionRate: An index which shows how effective a PV system is in terms of global warming.
                         It is used in comparison with other fuels and technologies (Hydroelectricity(15), Wind(21), Nuclear(60), Geothermal power(91), Natural gas(577), Oil(893), Coal(955) ...)
                         -
                         It is part of the Life Cycle analysis of the PV system.
                         -
                         In gCO2/kWh.
        EPBT: Energy PayBack Time - time it takes for PV modules to produce all the energy used through-out its product life-cycle.
              After that period, they start producing zero-emissions energy.
              -
              It is used for Life Cycle analysis of the PV system.
              -
              In years.
"""

ghenv.Component.Name = "Ladybug_Photovoltaics Performance Metrics"
ghenv.Component.NickName = "PhotovoltaicsPerformanceMetrics"
ghenv.Component.Message = 'VER 0.0.61\nNOV_05_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nMAY_26_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino


def PVinputData(PVsurface, PVsurfacePercent, unitConversionFactor, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHour, totalRadiationPerHour, cellTemperaturePerHour, ACenergyDemandPerHour, energyCostPerKWh, embodiedEnergyPerMJ_M2, embodiedCO2PerKg_M2, gridEfficiency):
    
    if (PVsurface == None):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHourData = totalRadiationPerHourData = cellTemperaturePerHourData = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input Surface (not polysurface) to \"_PVsurface\".\nOr input surface Area in square meters (example: \"100\").\nOr input Nameplate DC power rating in kiloWatts (example: \"4 kw\")."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg
    
    if (len(ACenergyPerHour) == 8767):
        ACenergyPerHourData = ACenergyPerHour[7:]
        locationName = ACenergyPerHour[1]
    elif (len(ACenergyPerHour) == 8760):
        ACenergyPerHourData = ACenergyPerHour
        locationName = "unknown location"
    elif (len(ACenergyPerHour) == 0) or (ACenergyPerHour[0] is "") or (ACenergyPerHour[0] is None) or ((len(ACenergyPerHour) != 8767) and (len(ACenergyPerHour) != 8760)):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHourData = totalRadiationPerHourData = cellTemperaturePerHourData = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input \"_ACenergyPerHour\" from Ladybug \"Photovoltaics surface\" component."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg
    
    if (len(totalRadiationPerHour) == 8767):
        totalRadiationPerHourData = totalRadiationPerHour[7:]
    elif (len(totalRadiationPerHour) == 8760):
        totalRadiationPerHourData = totalRadiationPerHour
    elif (len(totalRadiationPerHour) == 0) or (totalRadiationPerHour[0] is "") or (totalRadiationPerHour[0] is None) or ((len(totalRadiationPerHour) != 8767) and (len(totalRadiationPerHour) != 8760)):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHourData = totalRadiationPerHourData = cellTemperaturePerHourData = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input \"_totalRadiationPerHour\" from Ladybug \"Photovoltaics surface\" component."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg
    
    if (len(cellTemperaturePerHour) == 8767):
        cellTemperaturePerHourData = cellTemperaturePerHour[7:]
    elif (len(cellTemperaturePerHour) == 8760):
        cellTemperaturePerHourData = cellTemperaturePerHour
    elif (len(cellTemperaturePerHour) == 0) or (cellTemperaturePerHour[0] is "") or (cellTemperaturePerHour[0] is None) or ((len(cellTemperaturePerHour) != 8767) and (len(cellTemperaturePerHour) != 8760)):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHourData = totalRadiationPerHourData = cellTemperaturePerHourData = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input \"_cellTemperaturePerHour\" from Ladybug \"Photovoltaics surface\" component."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg
    
    if (len(ACenergyDemandPerHour) == 0) or (ACenergyDemandPerHour[0] is "") or (ACenergyDemandPerHour[0] is None):
        ACenergyDemandPerHourData = [0 for i in range(8760)]
    elif (len(ACenergyDemandPerHour) == 8767):
        ACenergyDemandPerHourData = ACenergyDemandPerHour[7:]
    elif (len(ACenergyDemandPerHour) == 8760):
        ACenergyDemandPerHourData = ACenergyDemandPerHour
    elif ((len(ACenergyDemandPerHour) != 8767) and (len(ACenergyDemandPerHour) != 8760)):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHourData = totalRadiationPerHourData = cellTemperaturePerHourData = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Your \"ACenergyDemandPerHour_\" input needs to contain 8760 values or 8767 items (8760 values + 7 heading strings)."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg
    
    if (PVsurfacePercent == None) or (PVsurfacePercent < 0) or (PVsurfacePercent > 100):
        PVsurfacePercent = 100  # default value 100%
    
    if (moduleActiveAreaPercent == None) or (moduleActiveAreaPercent < 0) or (moduleActiveAreaPercent > 100):
        moduleActiveAreaPercent = 90  # default value in %
    
    if (moduleEfficiency == None) or (moduleEfficiency <= 0) or (moduleEfficiency > 100):
        moduleEfficiency = 15  # default for crystalline silicon, in %
    
    if (lifetime == None) or (lifetime <= 0):
        lifetime = 30  # default, in years
    
    if (energyCostPerKWh == None) or (energyCostPerKWh < 0):
        energyCostPerKWh = 0.15  # dollars per kWh
    
    if (embodiedEnergyPerMJ_M2 == None) or (embodiedEnergyPerMJ_M2 <= 0):
        embodiedEnergyPerGJ_M2 = 4410/1000  # default, in GJ/m2
    else:
        embodiedEnergyPerGJ_M2 = embodiedEnergyPerMJ_M2/1000  # in in GJ/m2
    
    if (embodiedCO2PerKg_M2 == None) or (embodiedCO2PerKg_M2 <= 0):
        embodiedCO2PerT_M2 = 225/1000  # default, in t CO2/m2
    else:
        embodiedCO2PerT_M2 = embodiedCO2PerKg_M2/1000  # in t CO2/m2
    
    if (gridEfficiency == None) or (gridEfficiency < 0) or (gridEfficiency > 100):
        gridEfficiency = 29  # default, in %
    
    # check PVsurface input
    obj = rs.coercegeometry(PVsurface)
    
    # input is surface
    if isinstance(obj,Rhino.Geometry.Brep):
        PVsurfaceInputType = "brep"
        facesCount = obj.Faces.Count
        if facesCount > 1:
            # inputted polysurface
            nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHour = totalRadiationPerHour = cellTemperaturePerHour = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = None
            validInputData = False
            printMsg = "The brep you supplied to \"_PVsurface\" is a polysurface. Please supply a surface"
            
            return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg
        else:
            # inputted brep with a single surface
            srfArea = Rhino.Geometry.AreaMassProperties.Compute(obj).Area * (PVsurfacePercent/100)  # in m2
            srfArea = srfArea * unitConversionFactor  # in m2
            activeArea = srfArea * (moduleActiveAreaPercent/100)  # in m2
            nameplateDCpowerRating = activeArea * (1 * (moduleEfficiency/100))  # in kW
            validInputData = True
            printMsg = "ok"
            
            return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg
    else:
        PVsurfaceInputType = "number"
        try:
            # input is number (pv surface area in m2)
            srfArea = float(PVsurface) * (PVsurfacePercent/100)  # in m2
            srfArea = srfArea * unitConversionFactor  # in m2
            activeArea = srfArea * (moduleActiveAreaPercent/100)  # in m2
            nameplateDCpowerRating = activeArea * (1 * (moduleEfficiency/100))  # in kW
            validInputData = True
            printMsg = "ok"
            
            return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg
        except Exception, e:
            pass
        
        # input is string (nameplateDCpowerRating in kW)
        lowerString = PVsurface.lower()
        
        if "kw" in lowerString:
            nameplateDCpowerRating = float(lowerString.replace("kw","")) * (PVsurfacePercent/100)  # in kW
            activeArea = nameplateDCpowerRating / (1 * (moduleEfficiency/100))  # in m2
            srfArea = activeArea * (100/moduleActiveAreaPercent)  # in m2
            validInputData = True
            printMsg = "ok"
            
            return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg
        else:
            nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHour = totalRadiationPerHour = cellTemperaturePerHour = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = None
            validInputData = False
            printMsg = "Something is wrong with your \"PVsurface\" input data"
            
            return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg


def monthlyYearlyPacEpoaTmTcell(ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHour, energyCostPerKWh):
    
    HOYs = range(1,8761)
    hoyForMonths = [0, 744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296, 8016, 8760, 9000]
    numberOfDaysInThatMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
    monthsOfYearHoyPac = [[],[],[],[],[],[],[],[],[],[],[],[]]
    monthsOfYearHoyPacFiltered = [[],[],[],[],[],[],[],[],[],[],[],[]]
    monthsOfYearHoyEpoa = [[],[],[],[],[],[],[],[],[],[],[],[]]
    monthsOfYearHoyEpoaFiltered = [[],[],[],[],[],[],[],[],[],[],[],[]]
    monthsOfYearHoyTcellFiltered = [[],[],[],[],[],[],[],[],[],[],[],[]]
    monthsOfYearHoyPacDemand = [[],[],[],[],[],[],[],[],[],[],[],[]]
    for i,hoy in enumerate(HOYs):
        Pac = ACenergyPerHourData[i]
        PacDemand = ACenergyDemandPerHour[i]
        Epoa = totalRadiationPerHourData[i]
        Tcell = cellTemperaturePerHourData[i]
        for k,item in enumerate(hoyForMonths):
            if hoy >= hoyForMonths[k]+1 and hoy <= hoyForMonths[k+1]:
                #if ACenergyPerHourData[i] > 0:
                if totalRadiationPerHourData[i] > 0.6:  # mid-day hours (Epoa > 0.6 kWh/m2) filter. Required for temperatureCorrectedPRperMonth and temperatureCorrectedPRperYear outputs
                    monthsOfYearHoyTcellFiltered[k].append(Tcell)
                    monthsOfYearHoyEpoaFiltered[k].append(Epoa)
                    monthsOfYearHoyPacFiltered[k].append(Pac)
                monthsOfYearHoyPacDemand[k].append(PacDemand)
                monthsOfYearHoyEpoa[k].append(Epoa)
                monthsOfYearHoyPac[k].append(Pac)
    # correction for if Epoa per some month = 0 (if conditionalStatement_ from "Photovoltaics surface" component has been used, too high (positive or negative) latitude):
    for i,monthSumTcellFiltered in enumerate(monthsOfYearHoyTcellFiltered):
        if len(monthSumTcellFiltered) == 0:
            monthsOfYearHoyTcellFiltered[i] = [0]
    for i,monthSumEpoaFiltered in enumerate(monthsOfYearHoyEpoaFiltered):
        if len(monthSumEpoaFiltered) == 0:
            monthsOfYearHoyEpoaFiltered[i] = [0]
    for i,monthSumPacFiltered in enumerate(monthsOfYearHoyPacFiltered):
        if len(monthSumPacFiltered) == 0:
            monthsOfYearHoyPacFiltered[i] = [0]
    
    cellTemperaturePerMonthAverageFiltered = [sum(monthTcell)/len(monthTcell) for monthTcell in monthsOfYearHoyTcellFiltered]  # in C
    cellTemperaturePerYearAverageFiltered = sum(cellTemperaturePerMonthAverageFiltered)/len(cellTemperaturePerMonthAverageFiltered)  # in C
    
    solarRadiationPerMonth = [sum(monthEpoa) for monthEpoa in monthsOfYearHoyEpoa]  # in kWh/m2
    solarRadiationPerYear = sum(solarRadiationPerMonth)  # in kWh/m2
    solarRadiationPerMonthAverageFiltered = [sum(monthEpoa2) for monthEpoa2 in monthsOfYearHoyEpoaFiltered]  # in kWh/m2
    
    ACenergyPerMonth = [sum(monthPac) for monthPac in monthsOfYearHoyPac]  # in kWh
    ACenergyPerYear = sum(ACenergyPerMonth)  # in kWh
    ACenergyPerMonthAverageFiltered = [sum(monthPac2) for monthPac2 in monthsOfYearHoyPacFiltered]  # in kWh
    
    ACenergyDemandPerMonth = [sum(monthPacDemand) for monthPacDemand in monthsOfYearHoyPacDemand]  # in kWh
    ACenergyDemandPerYear = sum(ACenergyDemandPerMonth)  # in kWh
    
    energyValuePerMonth = [month*energyCostPerKWh for month in ACenergyPerMonth]
    energyValuePerYear = sum(energyValuePerMonth)
    
    return ACenergyPerMonth, ACenergyPerYear, ACenergyPerMonthAverageFiltered, energyValuePerMonth, energyValuePerYear, solarRadiationPerMonth, solarRadiationPerYear, solarRadiationPerMonthAverageFiltered, cellTemperaturePerMonthAverageFiltered, cellTemperaturePerYearAverageFiltered, ACenergyDemandPerMonth, ACenergyDemandPerYear


def main(ACenergyPerMonth, ACenergyPerYear, ACenergyPerMonthAverageFiltered, solarRadiationPerMonth, solarRadiationPerYear, solarRadiationPerMonthAverageFiltered, cellTemperaturePerMonthAverageFiltered, cellTemperaturePerYearAverageFiltered, ACenergyDemandPerMonth, ACenergyDemandPerYear, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency):
    
    Yield = ACenergyPerYear/nameplateDCpowerRating  # in hours
    
    CUFperYear = ACenergyPerYear/(nameplateDCpowerRating * 8760) * 100  # in %
    
    basicPRperYear = (ACenergyPerYear / (srfArea*(moduleEfficiency/100)*solarRadiationPerYear)) * 100  # in %
    
    gamma = -0.005   # default temperature coefficient for crystalline silicon PV modules
    temperatureCorrectedPRperMonth = []
    for i,Epoa in enumerate(solarRadiationPerMonthAverageFiltered):
        Ktemp = 1+gamma*(cellTemperaturePerMonthAverageFiltered[i]-cellTemperaturePerYearAverageFiltered)
        if Epoa == 0:  # correction for if Epoa per some month = 0 (if conditionalStatement_ from "Photovoltaics surface" component has been used, too high (positive or negative) latitude):
            TaCorrectedPR = 0
        else:
            TaCorrectedPR = (ACenergyPerMonthAverageFiltered[i]/nameplateDCpowerRating*Ktemp) / ((Epoa)/1)*100
        temperatureCorrectedPRperMonth.append(TaCorrectedPR)  # in %
    temperatureCorrectedPRperYear = sum(temperatureCorrectedPRperMonth)/len(temperatureCorrectedPRperMonth)  # in %
    
    energyOffsetPerMonth = []
    for i,monthPacDemand in enumerate(ACenergyDemandPerMonth):
        if monthPacDemand == 0:  # correction if PacDemand per some month = 0
            energyOffsetPM = 100
        else:
            energyOffsetPM = (ACenergyPerMonth[i]/ACenergyDemandPerMonth[i])*100
        energyOffsetPerMonth.append(energyOffsetPM)
    if ACenergyDemandPerYear == 0:  # correction if PacDemand for all months = 0
        energyOffsetPerYear = 100
    else:
        energyOffsetPerYear = ACenergyPerYear/ACenergyDemandPerYear*100
    #averageEnergyOffsetPerMonth = sum(energyOffsetPerMonth)/12
    
    embodiedEnergy = embodiedEnergyPerGJ_M2 * srfArea  # in GigaJoules
    embodiedCO2 = embodiedCO2PerT_M2 * srfArea   # in tCO2
    
    CO2emissionRate = (embodiedCO2*1000000)/(ACenergyPerYear*lifetime)  # in gCO2/kWh
    CO2emissionRate2 = (embodiedCO2*1000000)/(solarRadiationPerYear*(moduleEfficiency/100)*basicPRperYear*lifetime*srfArea)  # in gCO2/kWh
    
    embodiedEnergy_kWh_m2 = embodiedEnergyPerGJ_M2 * (1000/3.6) * (gridEfficiency/100)  # to kWh/m2
    
    EPBT = (embodiedEnergy_kWh_m2) / (solarRadiationPerYear*(moduleEfficiency/100)*(basicPRperYear/100))  # in years
    
    EROI = lifetime / EPBT  # formula by Hall, 2008; Heinberg, 2009; Lloyd and Forest, 2010
    
    return Yield, CUFperYear, basicPRperYear, temperatureCorrectedPRperMonth, temperatureCorrectedPRperYear, energyOffsetPerMonth, energyOffsetPerYear, embodiedEnergy, embodiedCO2, CO2emissionRate, EPBT, EROI


def printOutput(locationName, PVsurfacePercent, moduleActiveAreaPercent, srfArea, activeArea, nameplateDCpowerRating, moduleEfficiency, lifetime, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency):
    resultsCompletedMsg = "Photovoltaics performance metrics successfully calculated!"
    
    embodiedEnergyPerMJ_M2 = embodiedEnergyPerGJ_M2*1000
    embodiedCO2PerKg_M2 = embodiedCO2PerT_M2*1000
    
    printOutputMsg = \
    """
Input data:

Location: %s

Surface percentage used for PV modules: %0.2f
Active area Percentage: %0.2f
Surface area (m2): %0.2f
Surface active area (m2): %0.2f
Nameplate DC power rating (kW): %0.2f
Module efficiency: %s
Lifetime: %s

Energy cost per KWh: %s
Embodied energy/m2 (MJ/m2): %0.2f
Embodied CO2/m2 (kg CO2/m2): %0.2f
gridEfficiency: %s
    """ % (locationName, PVsurfacePercent, moduleActiveAreaPercent, srfArea, activeArea, nameplateDCpowerRating, moduleEfficiency, lifetime, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerKg_M2, gridEfficiency)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        if _PVsurface:
            unitConversionFactor = lb_preparation.checkUnits()
            unitAreaConversionFactor = unitConversionFactor**2
            nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency, locationName, validInputData, printMsg = PVinputData(_PVsurface, PVsurfacePercent_, unitConversionFactor, moduleActiveAreaPercent_, moduleEfficiency_, lifetime_, _ACenergyPerHour, _totalRadiationPerHour, _cellTemperaturePerHour, ACenergyDemandPerHour_, energyCostPerKWh_, embodiedEnergyPerM2_, embodiedCO2PerM2_, gridEfficiency_)
            if validInputData:
                # all inputs ok
                if _runIt:
                    ACenergyPerMonth, ACenergyPerYear, ACenergyPerMonthAverageFiltered, energyValuePerMonth, energyValuePerYear, solarRadiationPerMonth, solarRadiationPerYear, solarRadiationPerMonthAverageFiltered, cellTemperaturePerMonthAverageFiltered, cellTemperaturePerYearAverageFiltered, ACenergyDemandPerMonth, ACenergyDemandPerYear = monthlyYearlyPacEpoaTmTcell(ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, ACenergyDemandPerHourData, energyCostPerKWh)
                    Yield, CUFperYear, basicPRperYear, temperatureCorrectedPRperMonth, temperatureCorrectedPRperYear, energyOffsetPerMonth, energyOffsetPerYear, embodiedEnergy, embodiedCO2, CO2emissionRate, EPBT, EROI = main(ACenergyPerMonth, ACenergyPerYear, ACenergyPerMonthAverageFiltered, solarRadiationPerMonth, solarRadiationPerYear, solarRadiationPerMonthAverageFiltered, cellTemperaturePerMonthAverageFiltered, cellTemperaturePerYearAverageFiltered, ACenergyDemandPerMonth, ACenergyDemandPerYear, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency)
                    printOutput(locationName, PVsurfacePercent, moduleActiveAreaPercent, srfArea, activeArea, nameplateDCpowerRating, moduleEfficiency, lifetime, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency)
                else:
                    print "All inputs are ok. Please set the \"_runIt\" to True, in order to run the Photovoltaics performance metrics"
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please input Surface (not polysurface) to \"_PVsurface\".\nOr input surface Area in square meters (example: \"100\").\nOr input Nameplate DC power rating in kiloWatts (example: \"4 kw\")."
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