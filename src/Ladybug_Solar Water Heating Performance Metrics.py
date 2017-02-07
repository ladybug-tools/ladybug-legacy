# Solar water heating performance metrics
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Dr. Chengchu Yan and Djordje Spasic <ycc05ster@gmail.com, djordjedspasic@gmail.com> 
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
# along with Ladybug; If not, see <http://www.gnu.org/licenses>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to calculate various Solar water heating performance metrics.
Also use it to calculate the optimal SWH system size and tank storage volume.
-
Provided by Ladybug 0.0.64
    
    input:
        _SWHsurface: Use the same "_SWHsurface" you supplied to the "Solar Water Heating Surface" component.
        SWHsurfacePercent_: The percentage of surface which will be used for SWH collectors (range 0-100).
                            -
                            There are no general rules or codes which would limit the percentage of the roof(surface) covered with SWH collectors.
                            -
                            If not supplied, default value of 100 (all surface area will be covered in SWH collectors) is used.
                            -
                            In percent (%).
        SWHsystemSettings_: A list of all Solar water heating system settings. Use the same "SWHsystemSettings_" you supplied to the "Solar Water Heating Surface" component.
                            -
                            If not supplied, the following swh system settings will be used by default:
                            - glazed flat plate collectors
                            - active
                            - closed loop
                            - pipe length: 20 meters
                            - unshaded
        _heatingLoadPerHour: Use the same "_heatingLoadHour" you supplied to the "Solar Water Heating Surface" component.
                             -
                             In kWh.
        _heatFromTankPerHour: Import "heatFromTankPerHour" output data from "Solar water heating surface" component.
                              -
                              In kWh.
        _heatFromAuxiliaryHeaterPerHour: Import "heatFromAuxiliaryHeaterPerHour" output data from "Solar water heating surface" component.
                               -
                               In kWh.
        _pumpEnergyPerHour: Import "pumpEnergyPerHour" output data from "Solar water heating surface" component.
                               -
                               In kWh.
        energyCostPerKWh_: The cost of one kilowatt hour in any currency unit (dollar, euro, yuan...)
                           -
                           If not supplied, 0.15 $/kWh will be used as default value.
                           -
                           In currency/kWh.
        collectorEmbodiedEnergyPerM2_: Energy necessary for product life-cycle of SWH collector per square meter.
                                       -
                                       If not supplied default value of 1135 (MJ/m2) for unglazed or glazed flat plate collector will be used.
                                       -
                                       In MJ/m2 (megajoules per square meter).
        tankEmbodiedEnergyPerL_: Energy necessary for product life-cycle of storage tank per liter.
                                 -
                                 If not supplied default value of 20 (MJ/l) will be used.
                                 -
                                 In MJ/l (megajoules per liter).
        collectorEmbodiedCO2PerM2_: Carbon emissions produced during SWH collector's life-cycle per square meter..
                                    -
                                    If not supplied default value of 65.5 (kg CO2/m2) for unglazed or glazed flat plate collector will be used.
                                    -
                                    In kg CO2/m2 (kilogram of CO2 per square meter).
        tankEmbodiedCO2PerL_: Carbon emissions produced during storage tank's life-cycle per liter.
                              -
                              If not supplied default value of 0.14 (kg CO2/l) for unglazed or glazed flat plate collector will be used.
                              -
                              In kg CO2/l (kilogram of CO2 per liter).
        collectorLifetime_: Life expectancy of a SWH collector.
                            -
                            If not supplied default value of 15 (years) will be used.
                            -
                            In years.
        tankLifetime_: Life expectancy of a storage tank.
                       -
                       If not supplied default value of 10 (years) will be used.
                       -
                       In years.
        optimal_: Set to "True" to calculate optimal system size and tank storage volume.
                               -
                               Larger system sizes and tank volumes produce more energy, therefor cover more initial heating load, which results in less usage of auxiliary energy. However, the larger the system size and tank volume, more embodied energy is spent.
                               In order to find an optimal system size (total size of all collectors) and storage tank volume, life-cycle energy analysis is used to acheive the maximal net energy saving of the swh system. The net energy saving of swh system is the energy saving in kWh remained after an annualized embodied energy (of collectors or storage tank) has been deducted from the operating energy saving of swh system.
                               This method of optimization is superior in comparison with other simulation-based methods due to consideration of all energy performance stages (production, operation, maintenance...).
                               -
                               This optimization method can be used to account for capital costs, instead of embodied energy. This would account only for operation performance stage.
                               In this case capital costs of collector/per square meter, and tank/per liter would need to be inputted into: "collectorEmbodiedEnergyPerM2_" and "tankEmbodiedEnergyPerL_" inputs.
                               -
                               Optimization analysis based on the law of diminishing marginal utility:
                               "A simplified method for optimal design of solar water heating systems based on life-cycle energy analysis", Renewable Energy journal, Yan, Wang, Ma, Shi, Vol 74, Feb 2015
                               www.sciencedirect.com/science/article/pii/S0960148114004807
        _runIt: ...
        
    output:
        readMe!: ...
        optimalSystemSize: Optimal SWH system size (optimal total size of SWH collector's array) for a given SWHsurface's tilt, array and "_heatingLoadHour".
                           Minimum SWH system size is 0.15 kWt.
                           Input it to "systemSize_" input of "PV SWH system size" component to see how much area it would require.
                           -
                           To calculate it, set the "optimal_" input to "True".
                           -
                           In thermal kiloWatts (kWt).
        optimalTankSize: Solar water heating storage tank optimal size (volume). Minimum size is 100 liters.
                         To calculate it, set the "optimal_" input to "True".
                         -
                         In liters.
        SEF: Solar Energy Factor - ratio of total energy provided by the swh system to auxiliary plus parasitic (circulation pump) energy for a whole year.
             -
             Unitless.
        SolarFractionPerMonth: Solar Fraction (or Solar Savings Fraction) - percentage of the heating load requirement that is provided by a swh system for each month during a year.
                               It ranges from 0 to 100%.
                               -
                               In percent (%).
        SolarFractionPerYear: Solar Fraction (or Solar Savings Fraction) - percentage of the total heating load requirement that is provided by a swh system for a whole year.
                              It ranges from 0 to 100%.
                              -
                              In percent (%).
        energyValue: Total Energy value generated by SWH system for a whole year in currency unit (dollars, euros, yuans...)
        EROI: Energy Return On Investment - a comparison of the generated electricity to the amount of primary energy used throughout the SWH collector's product life-cycle.
              -
              Unitless.
        embodiedEnergy: Total energy necessary for an entire product life-cycle of SWH collectors and storage tank.
                        -
                        In GJ (gigajoules).
        embodiedCO2: Total carbon emissions produced during SWH collector and storage tank life-cycle.
                     -
                     In tCO2 (tons of CO2).
        CO2emissionRate: Also called Embodied GHG emissions or GHGEmissions. An index which shows how effective a SWH system is in terms of global warming.
                         It is used in comparison with other fuels and technologies (Hydroelectricity(15), Wind(21), Nuclear(60), Geothermal power(91), Natural gas(577), Oil(893), Coal(955) ...)
                         -
                         In gCO2/kWh.
        EPBT: Energy PayBack Time - time it takes for SWH system to produce all the energy used through-out its collector's product life-cycle.
              -
              In years.
"""

ghenv.Component.Name = "Ladybug_Solar Water Heating Performance Metrics"
ghenv.Component.NickName = "SolarWaterHeatingPerformanceMetrics"
ghenv.Component.Message = 'VER 0.0.64\nFEB_05_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Renewables"
#compatibleLBVersion = VER 0.0.62\nMAR_11_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import math


def SWHinputData(SWHsurface, SWHsurfacePercent, SWHsystemSettings, collectorLifetime, tankLifetime, heatingLoadPerHour, heatFromTankPerHour, heatFromAuxiliaryHeaterPerHour, pumpEnergyPerHour, energyCostPerKWh, collectorEmbodiedEnergyPerMJ_M2, tankEmbodiedEnergyPerMJ_L, collectorEmbodiedCO2PerKg_M2, tankEmbodiedCO2PerKg_L):
    
    if (SWHsurface == None):
        srfArea = activeArea = SWHsurfacePercent = collectorActiveAreaPercent = collectorLifetime = tankLifetime = heatingLoadPerHourData = heatFromTankPerHourData = heatFromAuxiliaryHeaterPerHourData = pumpEnergyPerHourData = energyCostPerKWh = collectorEmbodiedEnergyPerGJ_M2 = tankEmbodiedEnergyPerGJ_M3 = collectorEmbodiedCO2PerT_M2 = tankEmbodiedCO2PerT_M3 = locationName = None
        validInputData = False
        printMsg = "Please input a Surface (not polysurface) to \"_SWHsurface\". The same Surface you inputted to \"Solar Water Heating Surface\" component."
        
        return srfArea, activeArea, SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName, validInputData, printMsg
    
    if (len(heatingLoadPerHour) == 0) or (heatingLoadPerHour[0] is "") or (heatingLoadPerHour[0] is None):
        srfArea = activeArea = SWHsurfacePercent = collectorActiveAreaPercent = collectorLifetime = tankLifetime = heatingLoadPerHourData = heatFromTankPerHourData = heatFromAuxiliaryHeaterPerHourData = pumpEnergyPerHourData = energyCostPerKWh = collectorEmbodiedEnergyPerGJ_M2 = tankEmbodiedEnergyPerGJ_M3 = collectorEmbodiedCO2PerT_M2 = tankEmbodiedCO2PerT_M3 = locationName = None
        validInputData = False
        printMsg = "Please input \"_heatingLoadPerHour\". The same data you inputted to \"Solar Water Heating Surface\" component."
        
        return srfArea, activeArea, SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName, validInputData, printMsg
    else:
        if (len(heatingLoadPerHour) == 8767):
            heatingLoadPerHourData = heatingLoadPerHour[7:]
            locationName = heatingLoadPerHour[1]
        elif (len(heatingLoadPerHour) == 8760):
            heatingLoadPerHourData = heatingLoadPerHour
        else:
            srfArea = activeArea = SWHsurfacePercent = collectorActiveAreaPercent = collectorLifetime = tankLifetime = heatingLoadPerHourData = heatFromTankPerHourData = heatFromAuxiliaryHeaterPerHourData = pumpEnergyPerHourData = energyCostPerKWh = collectorEmbodiedEnergyPerGJ_M2 = tankEmbodiedEnergyPerGJ_M3 = collectorEmbodiedCO2PerT_M2 = tankEmbodiedCO2PerT_M3 = locationName = None
            validInputData = False
            printMsg = "Inputted \"_heatingLoadPerHour\" list does not have required length.\n\"_heatingLoadPerHour\" needs to be a list of either 8767 (heading plus values) or 8760 (only values) items.\nUse Ladybug's \"Residential Hot Water\" or \"Commercial Public Apartment Hot Water\" components to input domestic hot water heating load.\nAdditionally, for space heating and/or space cooling loads, use Honeybee's \"Read EP Result\" component."
            
            return srfArea, activeArea, SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName, validInputData, printMsg
    
    if (len(heatFromTankPerHour) == 0) or (heatFromTankPerHour[0] is "") or (heatFromTankPerHour[0] is None):
        srfArea = activeArea = SWHsurfacePercent = collectorActiveAreaPercent = collectorLifetime = tankLifetime = heatingLoadPerHourData = heatFromTankPerHourData = heatFromAuxiliaryHeaterPerHourData = pumpEnergyPerHourData = energyCostPerKWh = collectorEmbodiedEnergyPerGJ_M2 = tankEmbodiedEnergyPerGJ_M3 = collectorEmbodiedCO2PerT_M2 = tankEmbodiedCO2PerT_M3 = locationName = None
        validInputData = False
        printMsg = "Please input \"_heatFromTankPerHour\" from Ladybug \"Solar Water Heating Surface\" component."
        
        return srfArea, activeArea, SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName, validInputData, printMsg
    else:
        if (len(heatFromTankPerHour) == 8767):
            heatFromTankPerHourData = heatFromTankPerHour[7:]
        elif (len(heatFromTankPerHour) == 8760):
            heatFromTankPerHourData = heatFromTankPerHour
    
    if (len(heatFromAuxiliaryHeaterPerHour) == 0) or (heatFromAuxiliaryHeaterPerHour[0] is "") or (heatFromAuxiliaryHeaterPerHour[0] is None):
        srfArea = activeArea = SWHsurfacePercent = collectorActiveAreaPercent = collectorLifetime = tankLifetime = heatingLoadPerHourData = heatFromTankPerHourData = heatFromAuxiliaryHeaterPerHourData = pumpEnergyPerHourData = energyCostPerKWh = collectorEmbodiedEnergyPerGJ_M2 = tankEmbodiedEnergyPerGJ_M3 = collectorEmbodiedCO2PerT_M2 = tankEmbodiedCO2PerT_M3 = locationName = None
        validInputData = False
        printMsg = "Please input \"_heatFromAuxiliaryHeaterPerHour\" from Ladybug \"Solar Water Heating Surface\" component."
        
        return srfArea, activeArea, SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName, validInputData, printMsg
    else:
        if (len(heatFromAuxiliaryHeaterPerHour) == 8767):
            heatFromAuxiliaryHeaterPerHourData = heatFromAuxiliaryHeaterPerHour[7:]
        elif (len(heatFromAuxiliaryHeaterPerHour) == 8760):
            heatFromAuxiliaryHeaterPerHourData = heatFromAuxiliaryHeaterPerHour
    
    if (len(pumpEnergyPerHour) == 0) or (pumpEnergyPerHour[0] is "") or (pumpEnergyPerHour[0] is None):
        srfArea = activeArea = SWHsurfacePercent = collectorActiveAreaPercent = collectorLifetime = tankLifetime = heatingLoadPerHourData = heatFromTankPerHourData = heatFromAuxiliaryHeaterPerHourData = pumpEnergyPerHourData = energyCostPerKWh = collectorEmbodiedEnergyPerGJ_M2 = tankEmbodiedEnergyPerGJ_M3 = collectorEmbodiedCO2PerT_M2 = tankEmbodiedCO2PerT_M3 = locationName = None
        validInputData = False
        printMsg = "Please input \"_pumpEnergyPerHour\" from Ladybug \"Solar Water Heating Surface\" component."
        
        return srfArea, activeArea, SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName, validInputData, printMsg
    else:
        if (len(pumpEnergyPerHour) == 8767):
            pumpEnergyPerHourData = pumpEnergyPerHour[7:]
        elif (len(pumpEnergyPerHour) == 8760):
            pumpEnergyPerHourData = pumpEnergyPerHour
    
    
    if (len(heatingLoadPerHour) == 8760) and (len(heatFromTankPerHour) == 8760) and (len(heatFromAuxiliaryHeaterPerHour) == 8760) and (len(pumpEnergyPerHour) == 8760):
        locationName = "unknown location"
    elif len(heatFromTankPerHour) == 8767:
        locationName = heatFromTankPerHour[1]
    
    if (SWHsurfacePercent == None) or (SWHsurfacePercent < 0) or (SWHsurfacePercent > 100):
        SWHsurfacePercent = 100  # default value 100%
    
    # SWH system inputs
    if (len(SWHsystemSettings) != 23) and (len(SWHsystemSettings) != 0):
        srfArea = activeArea = SWHsurfacePercent = collectorActiveAreaPercent = collectorLifetime = tankLifetime = heatingLoadPerHourData = heatFromTankPerHourData = heatFromAuxiliaryHeaterPerHourData = pumpEnergyPerHourData = energyCostPerKWh = collectorEmbodiedEnergyPerGJ_M2 = tankEmbodiedEnergyPerGJ_M3 = collectorEmbodiedCO2PerT_M2 = tankEmbodiedCO2PerT_M3 = locationName = None
        validInputData = False
        printMsg = "Your \"SWHsystemSettings_\" input is incorrect. Please use \"SWHsystemSettings\" output from \"Solar Water Heating System\" or \"Solar Water Heating System Detailed\" components."
        
        return srfArea, activeArea, SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName, validInputData, printMsg
    
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
        dischargeTemperature = 93
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
    
    if (collectorLifetime == None) or (collectorLifetime < 0):
        collectorLifetime = 15  # default, in years
    
    if (tankLifetime == None) or (tankLifetime < 0):
        tankLifetime = 15  # default, in years
    
    if (energyCostPerKWh == None) or (energyCostPerKWh < 0):
        energyCostPerKWh = 0.15  # dollars per kWh
    
    if (collectorEmbodiedEnergyPerMJ_M2 == None) or (collectorEmbodiedEnergyPerMJ_M2 <= 0):
        collectorEmbodiedEnergyPerGJ_M2 = 1135/1000  # default for flate plate (unglazed and glazed) collectors, in GJ/m2
    else:
        collectorEmbodiedEnergyPerGJ_M2 = collectorEmbodiedEnergyPerMJ_M2/1000  # in in GJ/m2
    
    if (tankEmbodiedEnergyPerMJ_L == None) or (tankEmbodiedEnergyPerMJ_L <= 0):
        tankEmbodiedEnergyPerMJ_L = 20  # default, in MJ/Liter
        tankEmbodiedEnergyPerMJ_M3 = tankEmbodiedEnergyPerMJ_L/1000  # to MJ/m3
        tankEmbodiedEnergyPerGJ_M3 = tankEmbodiedEnergyPerMJ_M3/1000  # to GJ/m3
    else:
        tankEmbodiedEnergyPerMJ_M3 = tankEmbodiedEnergyPerMJ_L/1000  # to MJ/m3
        tankEmbodiedEnergyPerGJ_M3 = tankEmbodiedEnergyPerMJ_M3/1000  # to GJ/m3
    
    if (collectorEmbodiedCO2PerKg_M2 == None) or (collectorEmbodiedCO2PerKg_M2 <= 0):
        collectorEmbodiedCO2PerT_M2 = 65.5/1000  # default, in t CO2/m2
    else:
        collectorEmbodiedCO2PerT_M2 = collectorEmbodiedCO2PerKg_M2/1000  # in t CO2/m2
    
    if (tankEmbodiedCO2PerKg_L == None) or (tankEmbodiedCO2PerKg_L <= 0):
        tankEmbodiedCO2PerT_L = 0.14/1000  # default, in t CO2/liter
        tankEmbodiedCO2PerT_M3 = tankEmbodiedCO2PerT_L/1000  # to t CO2/m3
    else:
        tankEmbodiedCO2PerT_L = tankEmbodiedCO2PerKg_L/1000  # in t CO2/liter
        tankEmbodiedCO2PerT_M3 = tankEmbodiedCO2PerT_L/1000  # to t CO2/m3
    
    
    # check SWHsurface input
    SWHsurfaceInputType = "brep"
    facesCount = SWHsurface.Faces.Count
    if facesCount > 1:
        # inputted polysurface
        srfArea = activeArea = SWHsurfacePercent = collectorActiveAreaPercent = collectorLifetime = tankLifetime = heatingLoadPerHourData = heatFromTankPerHourData = heatFromAuxiliaryHeaterPerHourData = pumpEnergyPerHourData = energyCostPerKWh = collectorEmbodiedEnergyPerGJ_M2 = tankEmbodiedEnergyPerGJ_M3 = collectorEmbodiedCO2PerT_M2 = tankEmbodiedCO2PerT_M3 = locationName = None
        validInputData = False
        printMsg = "The brep you supplied to \"_SWHsurface\" is a polysurface. Please supply a surface"
        
        return srfArea, activeArea, SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName, validInputData, printMsg
    else:
        # inputted brep with a single surface
        srfArea = Rhino.Geometry.AreaMassProperties.Compute(SWHsurface).Area * (SWHsurfacePercent/100)  # in m2
        srfArea = srfArea * unitAreaConversionFactor  # in m2
        activeArea = srfArea * (collectorActiveAreaPercent/100)  # in m2
        validInputData = True
        printMsg = "ok"
        
        return srfArea, activeArea, SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName, validInputData, printMsg


def optimizeCollectorTank(step, embodiedEnergyAnnualized_kWh_m2, srfTiltD, AOI_RL, heatingLoadPerHour, beamRadiationPerHour, diffuseRadiationPerHour, groundRadiationPerHour, dryBulbTemperature, coldWaterTemperaturePerHour, Fr, FrUL, dummycollectorActiveAreaPercent, Cp, mDot, bo, TmaxW, TdischargeW, TdeliveryW, TcoldJanuaryW, TmechRoomL, L, Di, insulT, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankLoss, heightDiameterTankRatio, epsilon, activeArea=None, tankSizeM3=None):
    
    activeAreaL = [0]
    tankSizeM3L = [0]
    heatFromTankPerYearL = [0]
    marginalEnergySavingCostsL = [0]
    for k in range(1,1000,1):
        heatFromTankPerHour2 = [0]
        tankWaterTemperaturePerHour2 = [TcoldJanuaryW]
        for i in range(1,8760):
            if activeArea == None:
                activeArea2 = k*step
            else:
                activeArea2 = activeArea
            if tankSizeM3 == None:
                tankSizeM3_2 = k*step
            else:
                tankSizeM3_2 = tankSizeM3
            tankArea2 = 2 * (((tankSizeM3_2**2)*math.pi*2*heightDiameterTankRatio) ** (1/3)) * (1+1/(2*heightDiameterTankRatio))
            collectorHeatLoss, collectorEfficiency, Qsolar, Qloss, Qsupply, Qaux, Qdis, Qpump, dQ, dt, Tw = lb_photovoltaics.swhdesign(activeArea2, srfTiltD, AOI_RL[i-1], bo, Fr, FrUL, beamRadiationPerHour[i], diffuseRadiationPerHour[i], groundRadiationPerHour[i], heatingLoadPerHour[i], Cp, mDot, dryBulbTemperature[i], coldWaterTemperaturePerHour[i], tankWaterTemperaturePerHour2[i-1], TdeliveryW, TmaxW, TdischargeW, TmechRoomL[i], L, Di, insulT, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeM3_2, tankArea2, tankLoss, epsilon)
            heatFromTankPerHour2.append(Qsupply)
            tankWaterTemperaturePerHour2.append(Tw)
        activeAreaL.append(activeArea2)
        tankSizeM3L.append(tankSizeM3_2)
        heatFromTankPerYear = sum(heatFromTankPerHour2)
        heatFromTankPerYearL.append(heatFromTankPerYear)
        if activeArea == None:
            marginalEnergySavingCosts = (heatFromTankPerYearL[k]-heatFromTankPerYearL[k-1])/(activeAreaL[k]-activeAreaL[k-1])
        if tankSizeM3 == None: 
            marginalEnergySavingCosts = (heatFromTankPerYearL[k]-heatFromTankPerYearL[k-1])/(tankSizeM3L[k]-tankSizeM3L[k-1])
        marginalEnergySavingCostsL.append(marginalEnergySavingCosts)
        if (marginalEnergySavingCosts < embodiedEnergyAnnualized_kWh_m2):
            marginalEnergySavingCostsLplusIndices = [(mesc,i) for i,mesc in enumerate(marginalEnergySavingCostsL[1:])]
            marginalEnergySavingCostsLplusIndices.sort()
            lowestIndex = marginalEnergySavingCostsLplusIndices[0][1]
            
            if activeArea == None:
                return activeAreaL[lowestIndex], "tankSizeM3Dummy"
            if tankSizeM3 == None: 
                return activeAreaL[lowestIndex], tankSizeM3L[lowestIndex]
    else:
        return None, None


def main(SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_L, locationName):
    
    # monthly heatingLoad, heatFromTank
    HOYs = range(1,8761)
    hoyForMonths = [0, 744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296, 8016, 8760, 9000]
    numberOfDaysInThatMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
    monthsOfYearHoyQload = [[],[],[],[],[],[],[],[],[],[],[],[]]
    monthsOfYearHoyQsupply = [[],[],[],[],[],[],[],[],[],[],[],[]]
    for i,hoy in enumerate(HOYs):
        Qload = heatingLoadPerHourData[i]
        Qsupply = heatFromTankPerHourData[i]
        for k,item in enumerate(hoyForMonths):
            if hoy >= hoyForMonths[k]+1 and hoy <= hoyForMonths[k+1]:
                monthsOfYearHoyQload[k].append(Qload)
                monthsOfYearHoyQsupply[k].append(Qsupply)
    # correction if Qload/Qsupply per some month = 0
    for i,monthSumQload in enumerate(monthsOfYearHoyQload):
        if len(monthsOfYearHoyQload[i]) == 0:
            monthsOfYearHoyQload[i] = [0]
        if len(monthsOfYearHoyQsupply[i]) == 0:
            monthsOfYearHoyQsupply[i] = [0]
    
    heatingLoadPerMonth = [sum(monthQload) for monthQload in monthsOfYearHoyQload]  # in kWh
    heatFromTankPerMonth = [sum(monthQsupply) for monthQsupply in monthsOfYearHoyQsupply]  # in kWh
    heatFromTankPerYear = sum(heatFromTankPerHourData)
    
    
    SEF = sum(heatingLoadPerHourData)/(sum(heatFromAuxiliaryHeaterPerHourData) + sum(pumpEnergyPerHourData))  # unitless, per year
    SolarFractionPerMonth = [heatFromTankPerMonth[i]/heatingLoadPerMonth[i]*100 if (heatingLoadPerMonth[i] != 0) else 0 for i in range(len(heatFromTankPerMonth))]  # in percent, per month
    SolarFractionPerMonth = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "SWH system Solar Fraction", "%", "Monthly-> total", (1, 1, 1), (12, 31, 24)] + SolarFractionPerMonth
    SolarFractionPerYear = heatFromTankPerYear/sum(heatingLoadPerHourData)*100  # in percent, per year
    energyValue = energyCostPerKWh * sum(heatingLoadPerHourData)
    
    
    collectorEmbodiedEnergyGJ = collectorEmbodiedEnergyPerGJ_M2 * srfArea  # in GigaJoules
    collectorEmbodiedCO2PerT = collectorEmbodiedCO2PerT_M2 * srfArea   # in tCO2
    collectorCO2emissionRate = (collectorEmbodiedCO2PerT*1000000)/(heatFromTankPerYear*collectorLifetime)  # in gCO2/kWh
    
    tankEmbodiedEnergyGJ = tankEmbodiedCO2PerT_L * srfArea  # in GigaJoules
    tankEmbodiedCO2PerT = tankEmbodiedCO2PerT_L * srfArea   # in tCO2
    tankCO2emissionRate = (tankEmbodiedCO2PerT*1000000)/(heatFromTankPerYear*tankLifetime)  # in gCO2/kWh
    
    embodiedEnergyGJ = collectorEmbodiedEnergyGJ + tankEmbodiedEnergyGJ
    embodiedCO2PerT = collectorEmbodiedCO2PerT + tankEmbodiedCO2PerT
    CO2emissionRate = collectorCO2emissionRate + tankCO2emissionRate
    
    collectorEmbodiedEnergy_kWh_m2 = collectorEmbodiedEnergyPerGJ_M2 * (1000/3.6)  # to kWh/m2
    tankEmbodiedEnergy_kWh_m3 = tankEmbodiedEnergyPerGJ_M3 * (1000/3.6)  # to kWh/m3
    
    if heatFromTankPerYear == 0:
        EPBT = EROI = 0
    else:
        EPBT_collector = collectorEmbodiedEnergy_kWh_m2/(heatFromTankPerYear/srfArea)  # in years
        
        swh_inputData = sc.sticky["swh_inputData"]
        conditionalStatementForFinalPrint, activeArea, srfTiltD, AOI_RL, heatingLoadPerHour, beamRadiationPerHour, diffuseRadiationPerHour, groundRadiationPerHour, dryBulbTemperature, coldWaterTemperaturePerHour, Fr, FrUL, dummycollectorActiveAreaPercent, Cp, mDot, IAMcoefficient, dummySVF, dummyBeamIndexPerHourData, TmaxW, TdischargeW, TdeliveryW, TcoldJanuaryW, TmechRoomL, L, Di, insulT, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeDummy, tankLoss, heightDiameterTankRatio, epsilon = swh_inputData
        
        EPBT_tank = tankEmbodiedEnergy_kWh_m3/(heatFromTankPerYear/tankSizeDummy )  # in years
        EPBT = EPBT_collector + EPBT_tank
        
        EROI_collector = collectorLifetime / EPBT  # formula by Hall, 2008; Heinberg, 2009; Lloyd and Forest, 2010
        EROI_tank = tankLifetime / EPBT  # formula by Hall, 2008; Heinberg, 2009; Lloyd and Forest, 2010
        EROI = EROI_collector + EROI_tank
    
    
    # optimal collector area, storage tank volume
    if optimal_:
        if (conditionalStatementForFinalPrint != "No condition") and (conditionalStatementForFinalPrint != "Dry Bulb Temperature>5"):
            optimalSystemSize = optimalTankSizeLiter = SEF = SolarFractionPerMonth = SolarFractionPerYear = energyValue = embodiedEnergyGJ = embodiedCO2PerT = CO2emissionRate = EPBT = EROI = None
            validWeatherData = False
            printMsg = "Optimal system size and storage tank can not be calculated from conditioned weather data. The only exception is the following condition: \"Dry Bulb Temperature>5\", which is used for drain back systems.\nPlease disconnect the \"annualHourlyData_\" and \"conditionalStatement_\" inputs of \"SWH surface\" component."
            
            return optimalSystemSize, optimalTankSizeLiter, SEF, SolarFractionPerMonth, SolarFractionPerYear, energyValue, embodiedEnergyGJ, embodiedCO2PerT, CO2emissionRate, EPBT, EROI, validWeatherData, printMsg
        
        collectorEmbodiedEnergyAnnualized_kWh_m2 = collectorEmbodiedEnergy_kWh_m2/collectorLifetime  # to kWh/m2/year
        
        tankEmbodiedEnergyAnnualized_kWh_m3 = tankEmbodiedEnergy_kWh_m3/tankLifetime  # to kWh/m3/year
        
        # minimal tank volume
        tankSizeM3_fromHWC = sc.sticky["swh_tankSizeM3_fromHWC"]  # in liters
        # steps based on: tankSizeM3_fromHWC = 1.5*(heatingLoadPerYear/365)
        if (tankSizeM3_fromHWC < 1):
            stepCollector = 2  # in m2
            stepTank = 0.1  # in m3
        elif (tankSizeM3_fromHWC >= 1) and (tankSizeM3_fromHWC < 2.5):
            stepCollector = 4  # in m2
            stepTank = 0.25  # in m3
        elif (tankSizeM3_fromHWC >= 2.5) and (tankSizeM3_fromHWC < 10):
            stepCollector = 4  # in m2
            stepTank = 0.5  # in m3
        elif (tankSizeM3_fromHWC >= 10) and (tankSizeM3_fromHWC < 60):
            stepCollector = 6  # in m2
            stepTank = 1  # in m3 
        elif (tankSizeM3_fromHWC >= 60):
            stepCollector = 10  # in m2
            stepTank = 5  # in m3
        
        optimalActiveArea, tankSizeM3 = optimizeCollectorTank(stepCollector, collectorEmbodiedEnergyAnnualized_kWh_m2, srfTiltD, AOI_RL, heatingLoadPerHour, beamRadiationPerHour, diffuseRadiationPerHour, groundRadiationPerHour, dryBulbTemperature, coldWaterTemperaturePerHour, Fr, FrUL, dummycollectorActiveAreaPercent, Cp, mDot, IAMcoefficient, TmaxW, TdischargeW, TdeliveryW, TcoldJanuaryW, TmechRoomL, L, Di, insulT, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankLoss, heightDiameterTankRatio, epsilon, None, tankSizeM3_fromHWC)
        
        if (optimalActiveArea == 0):
            # use minimal SWHsurface and storage tank
            #optimalSWHsurface = 2
            optimalSystemSize = 0.15  # in kWt, for evacuated tube: Fr = 0.25, FrUL = 0.95, activeArea = 1.18m2, collectorActiveArea = 60% => nameplateThermalCapacity = 0.1485 kWt approximatelly: 0.15 kWt
            optimalTankSizeLiter = 100
            print "Minimal SWHsurface area and storage tank volume will be used as optimal ones."
        elif (optimalActiveArea != None) and (tankSizeM3 != None):
            optimalActiveAreaDummy, optimalTankSizeM3 = optimizeCollectorTank(stepTank, tankEmbodiedEnergyAnnualized_kWh_m3, srfTiltD, AOI_RL, heatingLoadPerHour, beamRadiationPerHour, diffuseRadiationPerHour, groundRadiationPerHour, dryBulbTemperature, coldWaterTemperaturePerHour, Fr, FrUL, dummycollectorActiveAreaPercent, Cp, mDot, IAMcoefficient, TmaxW, TdischargeW, TdeliveryW, TcoldJanuaryW, TmechRoomL, L, Di, insulT, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankLoss, heightDiameterTankRatio, epsilon, optimalActiveArea, None)
            
            #optimalSWHsurface = optimalActiveArea /((SWHsurfacePercent/100) * (collectorActiveAreaPercent/100))
            optimalSystemSize = (optimalActiveArea * Fr) - (FrUL * 30/1000)
            optimalTankSizeLiter = int(optimalTankSizeM3 * 1000)  # from m3 to liters
        else:
            print "Optimal collector area and storage volume are larger than component's security boundaries. Increase the step of \"1\" in line 380 of the component's code. Example: Line 380 changed to: \"(1,1000,10)\", means step \"1\" increased to \"10\"."
            optimalSystemSize = optimalTankSizeLiter = None
    else:
        optimalSystemSize = optimalTankSizeLiter = None
    
    validWeatherData = True
    printMsg = "ok"
    
    return optimalSystemSize, optimalTankSizeLiter, SEF, SolarFractionPerMonth, SolarFractionPerYear, energyValue, embodiedEnergyGJ, embodiedCO2PerT, CO2emissionRate, EPBT, EROI, validWeatherData, printMsg


def printOutput(locationName, SWHsurfacePercent, collectorActiveAreaPercent, srfArea, activeArea, collectorLifetime, tankLifetime, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3):
    
    collectorEmbodiedEnergyPerMJ_M2 = collectorEmbodiedEnergyPerGJ_M2 * 1000  # in MJ/m2
    tankEmbodiedEnergyPerMJ_L = tankEmbodiedEnergyPerGJ_M3 * 1000 * 1000  # in MJ/m2
    collectorEmbodiedCO2PerKg_M2 = collectorEmbodiedCO2PerT_M2 * 1000  # in kg CO2/m2
    tankEmbodiedCO2PerKg_L = tankEmbodiedCO2PerT_M3 * 1000 * 1000  # in kg CO2/liter
    
    resultsCompletedMsg = "Solar water heating performance metrics successfully calculated!"
    printOutputMsg = \
    """
Input data:

Location: %s

Surface percentage used for SWH modules: %0.2f
Active area Percentage: %0.2f
Surface area (m2): %0.2f
Surface active area (m2): %0.2f
Collector lifetime: %s
Tank lifetime: %s

Energy cost per KWh: %s
Collector embodied energy/m2 (MJ/m2): %0.2f
Tank embodied energy/liter (MJ/l): %0.2f
Collector embodied CO2/m2 (kg CO2/m2): %0.2f
Tank embodied CO2/liter (kg CO2/l): %0.2f
    """ % (locationName, SWHsurfacePercent, collectorActiveAreaPercent, srfArea, activeArea, collectorLifetime, tankLifetime, energyCostPerKWh, collectorEmbodiedEnergyPerMJ_M2, tankEmbodiedEnergyPerMJ_L, collectorEmbodiedCO2PerKg_M2, tankEmbodiedCO2PerKg_L)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        if _SWHsurface:
            unitConversionFactor = lb_preparation.checkUnits()
            unitAreaConversionFactor = unitConversionFactor**2
            srfArea, activeArea, SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName, validInputData, printMsg = SWHinputData(_SWHsurface, SWHsurfacePercent_, SWHsystemSettings_, collectorLifetime_, tankLifetime_, _heatingLoadPerHour, _heatFromTankPerHour, _heatFromAuxiliaryHeaterPerHour, _pumpEnergyPerHour, energyCostPerKWh_, collectorEmbodiedEnergyPerM2_, tankEmbodiedEnergyPerL_, collectorEmbodiedCO2PerM2_, tankEmbodiedCO2PerL_)
            if validInputData:
                # all inputs ok
                if _runIt:
                    optimalSystemSize, optimalTankSize, SEF, SolarFractionPerMonth, SolarFractionPerYear, energyValue, embodiedEnergy, embodiedCO2, CO2emissionRate, EPBT, EROI, validWeatherData, printMsg = main(SWHsurfacePercent, collectorActiveAreaPercent, collectorLifetime, tankLifetime, heatingLoadPerHourData, heatFromTankPerHourData, heatFromAuxiliaryHeaterPerHourData, pumpEnergyPerHourData, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3, locationName)
                    if validWeatherData:
                        printOutput(locationName, SWHsurfacePercent, collectorActiveAreaPercent, srfArea, activeArea, collectorLifetime, tankLifetime, energyCostPerKWh, collectorEmbodiedEnergyPerGJ_M2, tankEmbodiedEnergyPerGJ_M3, collectorEmbodiedCO2PerT_M2, tankEmbodiedCO2PerT_M3)
                    else:
                        print printMsg
                        ghenv.Component.AddRuntimeMessage(level, printMsg)
                else:
                    print "All inputs are ok. Please set the \"_runIt\" to True, in order to run the Solar water heating performance metrics"
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please input a Surface (not polysurface) to \"_SWHsurface\". The same Surface you inputted to \"Solar Water Heating Surface\" component."
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        printMsg = "You need a newer version of Ladybug to use this component." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag the Ladybug_Ladybug component " + \
            "into the canvas and try again."
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please let the Ladybug fly..."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)