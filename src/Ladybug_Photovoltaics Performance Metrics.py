# Photovoltaics performance metrics
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
Use this component to calculate various Photovoltaics performance metrics

-
Provided by Ladybug 0.0.64
    
    input:
        _PVsurface: - Input planar Grasshopper/Rhino Surface (not a polysurface) on which the PV modules will be applied. If you have a polysurface, explode it (using "Deconstruct Brep" component) and then feed its Faces(F) output to _PVsurface. Surface normal should be faced towards the sun.
                    - Or create the Surface based on initial PV system size by using "PV SWH system size" component.
        PVsurfacePercent_: The percentage of surface which will be used for PV modules (range 0-100).
                           -
                           Some countries and states, have local codes which limit the portion of the roof, which can be covered by crystalline silicon modules. For example, this may include having setbacks(distances) of approximatelly 90cm from side and top edges of a roof, as a fire safety regulation.
                           -
                           If not supplied, default value of 100 percent (all surface area will be covered in PV modules) is used.
                           -
                           In percent.
        PVmoduleSettings_: A list of PV module settings. Use the "Simplified Photovoltaics Module" or "Import Sandia Photovoltaics Module" or "Import CEC Photovoltaics Module" components to generate them.
                           -
                           If not supplied, the following PV module settings will be used by default:
                           - module material: crystalline silicon (c-Si)
                           - moduleType: Close (flush) roof mount
                           - moduleEfficiency: 15 %
                           - temperatureCoefficient: -0.5 %/C
                           - moduleActiveAreaPercent: 90 %
        _ACenergyPerHour: Import "ACenergyPerYear" output data from "Photovoltaics surface" component.
                          -
                          In kWh.
        _totalRadiationPerHour: Import "totalRadiationPerHour" output data from "Photovoltaics surface" component.
                                -
                                In kWh/m2.
        _cellTemperaturePerHour: Import "cellTemperaturePerHour" output data from "Photovoltaics surface" component.
                                 -
                                 In C.
        ACenergyDemandPerHour_: Required electrical energy used for any kind of load: heating, cooling, electric lights, solar water heating circulation pump etc.
                                For example, any of the Honeybee's "Read EP Result" outputs can be inputted in here. Either separately or summed.
                                -
                                If nothing inputted, this input will be neglected (there is no required electrical energy).
                                -
                                In kWh.
        energyCostPerKWh_: The cost of one kilowatt hour in any currency unit (dollar, euro, yuan...)
                           -
                           If not supplied, 0.15 $/kWh will be used as default value.
        embodiedEnergyPerM2_: Energy necessary for an entire product life-cycle of PV module per square meter.
                             -
                             If not supplied default value of 4410 (MJ/m2) will be used.
                             -
                             In MJ/m2 (megajoules per square meter).
        embodiedCO2PerM2_: Carbon emissions produced during PV module's life-cycle per square meter.
                          -
                          If not supplied default value of 225 (kg CO2/m2) will be used.
                          -
                          In kg CO2/m2 (kilogram of CO2 per square meter).
        lifetime_: Life expectancy of a PV module.
                   -
                   If not supplied default value of 30 (years) will be used.
                   -
                   In years.
        gridEfficiency_: An average primary energy to electricity conversion efficiency.
                        -
                        If not supplied default value of 29 (perc.) will be used.
                        -
                        In percent.
        optimal_: Set to "True" to calculate optimal PVsurface area.
                  An optimal PVsurface area will cover 100% of the of the annual electricity load ("ACenergyDemandPerHour_").
        _runIt: ...
        
    output:
        readMe!: ...
        optimalSystemSize: Optimal PV system size (optimal total size of the PV array) for a given PVsurface's tilt, array and "ACenergyDemandPerHour_".
                           Minimum system size is 0.01 kW.
                           Input it to "systemSize_" input of "PV SWH system size" component to see how much area it would require.
                           -
                           To calculate it, set the "optimal_" input to "True".
                           -
                           In thermal kiloWatts (kWt).
        CUFperYear: Capacity Utilization Factor (or Capacity Factor or sometimes evan called Plant Load Factor (PLF)) - ratio of the annual AC power output and maximum possible output under ideal conditions if the sun shone throughout the day and throughout the year.
                    It is sometimes used by investors or developers for Financial and Maintenance analysis of the PV systems, instead of "basicPRperYear".
                    -
                    In percent (%).
        basicPRperYear: Basic Performance Ratio - ratio of the actual and theoretically possible annual energy output.
                        It is worldwide accepted standard metric for measuring the performance of the PV system, therefor it is used for Maintenance analysis of PV systems.
                        Used for Maintenance analysis of PV systems.
                        -
                        basicPR is more precise than upper "CUF" and should be used instead of it, unless "CUF" is specifically required.
                        -
                        In percent(%).
        temperatureCorrectedPRperMonth: Temperature corrected Performance Ratio - ratio of the actual and theoretically possible energy output for each month during a year, corrected for PV module's Cell temperature.
                                        Mid-day hours (solarRadiation > 0.6 kWh/m2) only taken into account.
                                        Used for Maintenance analysis of PV systems.
                                        -
                                        In percent(%).
        temperatureCorrectedPRperYear: Temperature corrected Performance Ratio - ratio of the actual and theoretically possible annual energy output, corrected for PV module's Cell temperature. Mid-day hours (solarRadiation > 0.6 kWh/m2) only taken into account.
                                       Used for Maintenance analysis of PV systems.
                                       -
                                       It is more precise than upper "basicPR" and should be used instead of it, unless "basicPR" is specifically required.
                                       -
                                       In percent(%).
        energyOffsetPerMonth: Percentage of the electricity demand covered by Photovoltaics system for each month during a year.
                              -
                              It is used for Financial and Maintenance analysis of the PV system.
                              -
                              In percent(%).
        energyOffsetPerYear: Percentage of the total annual electricity demand covered by Photovoltaics system for a whole year.
                             -
                             It is used for Financial and Maintenance analysis of the PV system.
                             -
                             In percent(%).
        energyValue: Total Energy value for the whole year in currency unit (dollars, euros, yuans...)
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
ghenv.Component.Message = "VER 0.0.64\nAPR_12_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Renewables"
#compatibleLBVersion = VER 0.0.64\nAPR_12_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import math


def PVinputData(PVsurface, PVsurfacePercent, unitConversionFactor, PVmoduleSettings, ACenergyPerHour, totalRadiationPerHour, cellTemperaturePerHour, ACenergyDemandPerHour, energyCostPerKWh, embodiedEnergyPerMJ_M2, embodiedCO2PerKg_M2, lifetime, gridEfficiency):
    
    if (PVsurface == None):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleEfficiency = temperatureCoefficientFraction = moduleActiveAreaPercent = ACenergyPerHourData = ACenergyPerHourDataFiltered = totalRadiationPerHourData = totalRadiationPerHourDataFiltered = cellTemperaturePerHourData = cellTemperaturePerHourDataFiltered = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = lifetime = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input a Surface (not polysurface) to \"_PVsurface\". The same Surface you inputted to \"Photovoltaics Surface\" component."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency, locationName, validInputData, printMsg
    
    if (len(ACenergyPerHour) == 8767):
        ACenergyPerHourData = ACenergyPerHour[7:]
        locationName = ACenergyPerHour[1]
    elif (len(ACenergyPerHour) == 8760):
        ACenergyPerHourData = ACenergyPerHour
        locationName = "unknown location"
    elif (len(ACenergyPerHour) == 0) or (ACenergyPerHour[0] is "") or (ACenergyPerHour[0] is None) or ((len(ACenergyPerHour) != 8767) and (len(ACenergyPerHour) != 8760)):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleEfficiency = temperatureCoefficientFraction = moduleActiveAreaPercent = ACenergyPerHourData = ACenergyPerHourDataFiltered = totalRadiationPerHourData = totalRadiationPerHourDataFiltered = cellTemperaturePerHourData = cellTemperaturePerHourDataFiltered = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = lifetime = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input \"_ACenergyPerHour\" from Ladybug \"Photovoltaics surface\" component."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency, locationName, validInputData, printMsg
    
    if (len(totalRadiationPerHour) == 8767):
        totalRadiationPerHourData = totalRadiationPerHour[7:]
    elif (len(totalRadiationPerHour) == 8760):
        totalRadiationPerHourData = totalRadiationPerHour
    elif (len(totalRadiationPerHour) == 0) or (totalRadiationPerHour[0] is "") or (totalRadiationPerHour[0] is None) or ((len(totalRadiationPerHour) != 8767) and (len(totalRadiationPerHour) != 8760)):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleEfficiency = temperatureCoefficientFraction = moduleActiveAreaPercent = ACenergyPerHourData = ACenergyPerHourDataFiltered = totalRadiationPerHourData = totalRadiationPerHourDataFiltered = cellTemperaturePerHourData = cellTemperaturePerHourDataFiltered = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = lifetime = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input \"_totalRadiationPerHour\" from Ladybug \"Photovoltaics surface\" component."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency, locationName, validInputData, printMsg
    
    if (len(cellTemperaturePerHour) == 8767):
        cellTemperaturePerHourData = cellTemperaturePerHour[7:]
    elif (len(cellTemperaturePerHour) == 8760):
        cellTemperaturePerHourData = cellTemperaturePerHour
    elif (len(cellTemperaturePerHour) == 0) or (cellTemperaturePerHour[0] is "") or (cellTemperaturePerHour[0] is None) or ((len(cellTemperaturePerHour) != 8767) and (len(cellTemperaturePerHour) != 8760)):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleEfficiency = temperatureCoefficientFraction = moduleActiveAreaPercent = ACenergyPerHourData = ACenergyPerHourDataFiltered = totalRadiationPerHourData = totalRadiationPerHourDataFiltered = cellTemperaturePerHourData = cellTemperaturePerHourDataFiltered = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = lifetime = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input \"_cellTemperaturePerHour\" from Ladybug \"Photovoltaics surface\" component."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency, locationName, validInputData, printMsg
    
    if (len(ACenergyDemandPerHour) == 0) or (ACenergyDemandPerHour[0] is "") or (ACenergyDemandPerHour[0] is None):
        ACenergyDemandPerHourData = [0 for i in range(8760)]
    elif (len(ACenergyDemandPerHour) == 8767):
        ACenergyDemandPerHourData = ACenergyDemandPerHour[7:]
    elif (len(ACenergyDemandPerHour) == 8760):
        ACenergyDemandPerHourData = ACenergyDemandPerHour
    elif ((len(ACenergyDemandPerHour) != 8767) and (len(ACenergyDemandPerHour) != 8760)):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleEfficiency = temperatureCoefficientFraction = moduleActiveAreaPercent = ACenergyPerHourData = ACenergyPerHourDataFiltered = totalRadiationPerHourData = totalRadiationPerHourDataFiltered = cellTemperaturePerHourData = cellTemperaturePerHourDataFiltered = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = lifetime = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Your \"ACenergyDemandPerHour_\" input needs to contain 8760 values or 8767 items (8760 values + 7 heading strings)."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency, locationName, validInputData, printMsg
    
    ACenergyPerHourDataFiltered = []
    totalRadiationPerHourDataFiltered = []
    cellTemperaturePerHourDataFiltered = []
    for i,Epoa in enumerate(totalRadiationPerHourData):
        Pac = ACenergyPerHourData[i]
        Epoa = totalRadiationPerHourData[i]
        Tcell = cellTemperaturePerHourData[i]
        if totalRadiationPerHourData[i] > 0.6:  # mid-day hours (Epoa > 0.6 kWh/m2) filter. Required for temperatureCorrectedPRperMonth and temperatureCorrectedPRperYear outputs
            pass
        else:
            Pac = Epoa = Tcell = 0
        ACenergyPerHourDataFiltered.append(Pac)
        totalRadiationPerHourDataFiltered.append(Epoa)
        cellTemperaturePerHourDataFiltered.append(Tcell)
    
    
    if (PVsurfacePercent == None) or (PVsurfacePercent < 0) or (PVsurfacePercent > 100):
        PVsurfacePercent = 100  # default value 100%
    
    # PV module settings inputs
    if (len(PVmoduleSettings) != 9) and (len(PVmoduleSettings) != 23) and (len(PVmoduleSettings) != 36) and (len(PVmoduleSettings) != 0):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleEfficiency = temperatureCoefficientFraction = moduleActiveAreaPercent = ACenergyPerHourData = ACenergyPerHourDataFiltered = totalRadiationPerHourData = totalRadiationPerHourDataFiltered = cellTemperaturePerHourData = cellTemperaturePerHourDataFiltered = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = lifetime = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Your \"PVmoduleSettings_\" input is incorrect. Please use \"PVmoduleSettings\" output from \"Simplified Photovoltaics Module\" or \"Import Sandia Photovoltaics Module\" or \"Import CEC Photovoltaics Module\" components."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency, locationName, validInputData, printMsg
    
    elif (len(PVmoduleSettings) == 0) or (PVmoduleSettings[0] is ""):
        # nothing inputted into "PVmoduleSettings_", use default PVmoduleSettings values
        
        #mountTypeName = "close roof mount"  # Glass/cell/glass (moduleType_ = 1)
        #moduleActiveAreaPercent = 90  # default value in %
        #moduleEfficiency = 15  # for crystalline silicon
        #temperatureCoefficientPercent = -0.5  # in %, for crystalline silicon
        
        moduleModelName, mountTypeName, moduleMaterial, mountType, moduleActiveAreaPercent, moduleEfficiency, temperatureCoefficientFraction, a, b, deltaT = lb_photovoltaics.deconstruct_PVmoduleSettings(PVmoduleSettings)
    
    elif (len(PVmoduleSettings) == 9):
        # data from "Simplified Photovoltaics Module" component added to "PVmoduleSettings_" input
        moduleModelName, mountTypeName, moduleMaterial, mountType, moduleActiveAreaPercent, moduleEfficiency, temperatureCoefficientFraction, a, b, deltaT = lb_photovoltaics.deconstruct_PVmoduleSettings(PVmoduleSettings)
    
    elif (len(PVmoduleSettings) == 23):
        # data from "Import CEC Photovoltaics Module" component added to "PVmoduleSettings_" input
        moduleModelName, moduleName, material, moduleMountType, moduleAreaM, moduleActiveAreaPercent, nameplateDCpowerRating_m, moduleEfficiency, Vmp_ref, Imp_ref, Voc_ref, Isc_ref, alpha_sc_ref, beta_oc_ref, IL_ref, Io_ref, Rs_ref, Rsh_ref, A_ref, n_s, adjust, temperatureCoefficientPercent, ws_adjusted_factor, Tnoct_adj = lb_photovoltaics.deconstruct_PVmoduleSettings(PVmoduleSettings)
        temperatureCoefficientFraction = temperatureCoefficientPercent/100  # unitless
    
    elif (len(PVmoduleSettings) == 36):
        # data from "Import Sandia Photovoltaics Module" component added to "PVmoduleSettings_" input
        moduleModelName, moduleName, material, moduleMountType, moduleAreaM, moduleActiveAreaPercent, nameplateDCpowerRating_m, moduleEfficiency, Vmp_ref, Imp_ref, Voc_ref, Isc_ref, alpha_sc_ref, beta_oc_ref, beta_mp_ref, mu_betamp, s, n, Fd, a0, a1, a2, a3, a4, b0, b1, b2, b3, b4, b5, C0, C1, C2, C3, a, b, deltaT = lb_photovoltaics.deconstruct_PVmoduleSettings(PVmoduleSettings)
        temperatureCoefficientPercent = -0.5  # dummy value
        temperatureCoefficientFraction = temperatureCoefficientPercent/100  # unitless, dummy value
    
    
    if (energyCostPerKWh == None) or (energyCostPerKWh <= 0):
        energyCostPerKWh = 0.15  # dollars per kWh
    
    if (embodiedEnergyPerMJ_M2 == None) or (embodiedEnergyPerMJ_M2 <= 0):
        embodiedEnergyPerGJ_M2 = 4410/1000  # default, in GJ/m2
    else:
        embodiedEnergyPerGJ_M2 = embodiedEnergyPerMJ_M2/1000  # in in GJ/m2
    
    if (embodiedCO2PerKg_M2 == None) or (embodiedCO2PerKg_M2 <= 0):
        embodiedCO2PerT_M2 = 225/1000  # default, in t CO2/m2
    else:
        embodiedCO2PerT_M2 = embodiedCO2PerKg_M2/1000  # in t CO2/m2
    
    if (lifetime == None) or (lifetime <= 0):
        lifetime = 30  # default, in years
    
    if (gridEfficiency == None) or (gridEfficiency <= 0) or (gridEfficiency > 100):
        gridEfficiency = 29  # default, in %
    
    
    
    # check PVsurface input
    PVsurfaceInputType = "brep"
    facesCount = PVsurface.Faces.Count
    if facesCount > 1:
        # inputted polysurface
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleEfficiency = temperatureCoefficientFraction = moduleActiveAreaPercent = ACenergyPerHourData = ACenergyPerHourDataFiltered = totalRadiationPerHourData = totalRadiationPerHourDataFiltered = cellTemperaturePerHourData = cellTemperaturePerHourDataFiltered = ACenergyDemandPerHourData = energyCostPerKWh = embodiedEnergyPerGJ_M2 = embodiedCO2PerT_M2 = lifetime = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "The brep you supplied to \"_PVsurface\" is a polysurface. Please supply a surface"
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency, locationName, validInputData, printMsg
    else:
        # inputted brep with a single surface
        srfArea = Rhino.Geometry.AreaMassProperties.Compute(PVsurface).Area * (PVsurfacePercent/100)  # in m2
        srfArea = srfArea * unitConversionFactor  # in m2
        activeArea = srfArea * (moduleActiveAreaPercent/100)  # in m2
        nameplateDCpowerRating = activeArea * (1 * (moduleEfficiency/100))  # in kW
        validInputData = True
        printMsg = "ok"
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency, locationName, validInputData, printMsg


def optimizePVsurfaceArea(DCtoACderateFactor, PVmoduleSettings, elevationM, srfTiltD, sunZenithDL, AOI_RL, totalRadiationPerHour, beamRadiationPerHour, diffuseRadiationPerHour, groundRadiationPerHour, dryBulbTemperature, windSpeed, directNormalRadiation, diffuseHorizontalRadiation, ACenergyDemandPerYear):
    
    # initialOptimalNameplateDCpowerRating
    averageDailyACenergyDemandPerYear = ACenergyDemandPerYear/365
    averageDailyTotalRadiation = (sum(totalRadiationPerHour)/1000)/365  # converted from Watts to kiloWatts
    initialOptimalNameplateDCpowerRating = (averageDailyACenergyDemandPerYear/averageDailyTotalRadiation)/DCtoACderateFactor
    
    # stepNameplateDCpowerRating
    if (initialOptimalNameplateDCpowerRating < 4):
        stepNameplateDCpowerRating = 0.005  # 5 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 4) and (initialOptimalNameplateDCpowerRating < 10):
        stepNameplateDCpowerRating = 0.01  # 10 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 10) and (initialOptimalNameplateDCpowerRating < 20):
        stepNameplateDCpowerRating = 0.02  # 20 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 20) and (initialOptimalNameplateDCpowerRating < 35):
        stepNameplateDCpowerRating = 0.025  # 25 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 35) and (initialOptimalNameplateDCpowerRating < 50):
        stepNameplateDCpowerRating = 0.05  # 50 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 50) and (initialOptimalNameplateDCpowerRating < 75):
        stepNameplateDCpowerRating = 0.075  # 75 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 75) and (initialOptimalNameplateDCpowerRating < 100):
        stepNameplateDCpowerRating = 0.1  # 100 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 100) and (initialOptimalNameplateDCpowerRating < 200):
        stepNameplateDCpowerRating = 0.25  # 250 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 200) and (initialOptimalNameplateDCpowerRating < 300):
        stepNameplateDCpowerRating = 0.5  # 500 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 300) and (initialOptimalNameplateDCpowerRating < 750):
        stepNameplateDCpowerRating = 1  # 1000 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 750) and (initialOptimalNameplateDCpowerRating < 1000):
        stepNameplateDCpowerRating = 2.5  # 2500 Watts step
    elif (initialOptimalNameplateDCpowerRating >= 1000):
        stepNameplateDCpowerRating = 5 # 1000 Watts step
    optimalNameplateDCpowerRatingL = [initialOptimalNameplateDCpowerRating]
    for k in range(1,1000,1):
        ACenergyPerHour = []
        for i in range(8760):
            Tcell, Pdc_, Pac = lb_photovoltaics.pvwatts(optimalNameplateDCpowerRatingL[-1], DCtoACderateFactor, srfTiltD, sunZenithDL[i], AOI_RL[i], totalRadiationPerHour[i], beamRadiationPerHour[i], diffuseRadiationPerHour[i], groundRadiationPerHour[i], dryBulbTemperature[i], windSpeed[i], directNormalRadiation[i], diffuseHorizontalRadiation[i], PVmoduleSettings, elevationM)
            ACenergyPerHour.append(Pac)
        energyOffsetPerYear = sum(ACenergyPerHour)/ACenergyDemandPerYear*100
        nameplateDCpowerRatingStep = initialOptimalNameplateDCpowerRating + k * stepNameplateDCpowerRating  #0.5  # minimal step: 10 watts
        optimalNameplateDCpowerRatingL.append(nameplateDCpowerRatingStep)
        if energyOffsetPerYear > 100:
            optimalNameplateDCpowerRating = round(optimalNameplateDCpowerRatingL[-1],2)
            optimalNameplateDCpowerRating = math.ceil(optimalNameplateDCpowerRating/0.01)*0.01  # round to 10 Watts
            if optimalNameplateDCpowerRating < 0.01:
                optimalNameplateDCpowerRating = 0.01  # in kW (10 Watts)
            #optimalActiveArea = optimalNameplateDCpowerRating / (1 * (moduleEfficiency/100))  # in m2
            #optimalSrfArea = optimalActiveArea * (100/moduleActiveAreaPercent)  # in m2
            #if optimalSrfArea < 0.075:
                #optimalSrfArea = 0.075  # in m2, corresponds to 0.01 kW (10 Watts) systemSize, moduleEfficiency 15%, moduleActiveArea 90%
                #print "Minimal PVsurface area will be used as optimal one."
            
            return optimalNameplateDCpowerRating
    
    # no optimal pv surface area was found
    print "Optimal PV system size is larger than component's security boundaries. Increase the step of \"1\" in line 410 of the component's code. Example: Line 410 changed to: \"for k in range(1,1000,10):\", means step \"1\" increased to \"10\"."
    return None  # in m2, corresponds to 0.01 kW (10 Watts) systemSize, moduleEfficiency 15%, moduleActiveArea 90%,


def main(ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, nameplateDCpowerRating, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, moduleEfficiency, gamma, lifetime, gridEfficiency, locationName):
    
    # montly cellTemperature, totalRadiation, ACenergy, ACenergyDemand
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
        PacDemand = ACenergyDemandPerHourData[i]
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
        if len(monthsOfYearHoyTcellFiltered[i]) == 0:
            monthsOfYearHoyTcellFiltered[i] = [0]
        if len(monthsOfYearHoyEpoaFiltered[i]) == 0:
            monthsOfYearHoyEpoaFiltered[i] = [0]
        if len(monthsOfYearHoyPacFiltered[i]) == 0:
            monthsOfYearHoyPacFiltered[i] = [0]
    
    cellTemperaturePerMonthAverageFiltered = [sum(monthTcell)/len(monthTcell) for monthTcell in monthsOfYearHoyTcellFiltered]  # in C
    cellTemperaturePerYearAverageFiltered = sum(cellTemperaturePerMonthAverageFiltered)/len(cellTemperaturePerMonthAverageFiltered)  # in C
    
    totalRadiationPerMonth = [sum(monthEpoa) for monthEpoa in monthsOfYearHoyEpoa]  # in kWh/m2
    totalRadiationPerYear = sum(totalRadiationPerMonth)  # in kWh/m2
    totalRadiationPerMonthAverageFiltered = [sum(monthEpoa2) for monthEpoa2 in monthsOfYearHoyEpoaFiltered]  # in kWh/m2
    
    ACenergyPerMonth = [sum(monthPac) for monthPac in monthsOfYearHoyPac]  # in kWh
    ACenergyPerYear = sum(ACenergyPerMonth)  # in kWh
    ACenergyPerMonthAverageFiltered = [sum(monthPac2) for monthPac2 in monthsOfYearHoyPacFiltered]  # in kWh
    
    ACenergyDemandPerMonth = [sum(monthPacDemand) for monthPacDemand in monthsOfYearHoyPacDemand]  # in kWh
    ACenergyDemandPerYear = sum(ACenergyDemandPerMonth)  # in kWh
    
    temperatureCorrectedPRperMonth = []
    for i,Epoa in enumerate(totalRadiationPerMonthAverageFiltered):
        Ktemp = 1+gamma*(cellTemperaturePerMonthAverageFiltered[i]-cellTemperaturePerYearAverageFiltered)
        if Epoa == 0:  # correction for if Epoa per some month = 0 (if conditionalStatement_ from "Photovoltaics surface" component has been used, too high (positive or negative) latitude):
            TcellCorrectedPR = 0
        else:
            TcellCorrectedPR = (ACenergyPerMonthAverageFiltered[i]/(nameplateDCpowerRating*Ktemp)) / (Epoa/1)*100
        temperatureCorrectedPRperMonth.append(TcellCorrectedPR)  # in %
    temperatureCorrectedPRperYear = sum(temperatureCorrectedPRperMonth)/len(temperatureCorrectedPRperMonth)  # in %
    temperatureCorrectedPRperMonth = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "PV system's Temperature corrected Performance Ratio", "%", "Monthly-> total", (1, 1, 1), (12, 31, 24)] + temperatureCorrectedPRperMonth
    
    
    energyOffsetPerMonth = []
    for i,monthPacDemand in enumerate(ACenergyDemandPerMonth):
        if monthPacDemand == 0:  # correction if PacDemand per some month = 0
            energyOffsetPM = 0
        else:
            energyOffsetPM = (ACenergyPerMonth[i]/ACenergyDemandPerMonth[i])*100
        energyOffsetPerMonth.append(energyOffsetPM)
    energyOffsetPerMonth = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "PV system's Energy offset", "%", "Monthly-> total", (1, 1, 1), (12, 31, 24)] + energyOffsetPerMonth
    
    if ACenergyDemandPerYear == 0:  # correction if PacDemand for all months = 0
        energyOffsetPerYear = 0
    else:
        energyOffsetPerYear = ACenergyPerYear/ACenergyDemandPerYear*100
    #averageEnergyOffsetPerMonth = sum(energyOffsetPerMonth)/12
    
    Yield = ACenergyPerYear/nameplateDCpowerRating  # in hours
    
    CUFperYear = ACenergyPerYear/(nameplateDCpowerRating * 8760) * 100  # in %
    
    basicPRperYear = (ACenergyPerYear / (srfArea*(moduleEfficiency/100)*totalRadiationPerYear)) * 100  # in % (it is not calculated for mid-day hours the way temperatureCorrectedPR is, so its values may fluctuate more)
    
    energyValue = energyCostPerKWh * ACenergyPerYear  # in chosen currency
    
    embodiedEnergy = embodiedEnergyPerGJ_M2 * srfArea  # in GigaJoules
    embodiedCO2 = embodiedCO2PerT_M2 * srfArea   # in tCO2
    
    CO2emissionRate = (embodiedCO2*1000000)/(ACenergyPerYear*lifetime)  # in gCO2/kWh
    CO2emissionRate2 = (embodiedCO2*1000000)/(totalRadiationPerYear*(moduleEfficiency/100)*basicPRperYear*lifetime*srfArea)  # in gCO2/kWh
    
    embodiedEnergy_kWh_m2 = embodiedEnergyPerGJ_M2 * (1000/3.6) * (gridEfficiency/100)  # to kWh/m2
    
    EPBT = (embodiedEnergy_kWh_m2) / (totalRadiationPerYear*(moduleEfficiency/100)*(basicPRperYear/100))  # in years
    
    EROI = lifetime / EPBT  # formula by Hall, 2008; Heinberg, 2009; Lloyd and Forest, 2010
    
    
    if optimal_:
        # optimal_ set to True
        if (ACenergyDemandPerYear != 0):
            # ACenergyDemandPerYear_ inputted
            pv_inputData = sc.sticky["pv_inputData"]
            conditionalStatementForFinalPrint, DCtoACderateFactor, PVmoduleSettings, elevationM, srfTiltD, sunZenithDL, AOI_RL, totalRadiationPerHour, beamRadiationPerHour, diffuseRadiationPerHour, groundRadiationPerHour, dryBulbTemperature, windSpeed, directNormalRadiation, diffuseHorizontalRadiation = pv_inputData
            if (conditionalStatementForFinalPrint == "No condition"):
                # nothing inputted into "Photovoltaics surface component"'s "annualHourlyData_" and "conditionalStatement_" inputs.
                optimalSystemSize = optimizePVsurfaceArea(DCtoACderateFactor, PVmoduleSettings, elevationM, srfTiltD, sunZenithDL, AOI_RL, totalRadiationPerHour, beamRadiationPerHour, diffuseRadiationPerHour, groundRadiationPerHour, dryBulbTemperature, windSpeed, directNormalRadiation, diffuseHorizontalRadiation, ACenergyDemandPerYear)
            else:
                # something inputted into "Photovoltaics surface component"'s "annualHourlyData_" and "conditionalStatement_" inputs.
                optimalSystemSize = Yield = CUFperYear = basicPRperYear = temperatureCorrectedPRperMonth = temperatureCorrectedPRperYear = energyOffsetPerMonth = energyOffsetPerYear = energyValue = embodiedEnergy = embodiedCO2 = CO2emissionRate = EPBT = EROI = None
                ACenergyDemandAndConditionalInputs = False
                printMsg = "Optimal optimalSystemSize can not be calculated from conditioned weather data.\nPlease disconnect the \"annualHourlyData_\" and \"conditionalStatement_\" inputs of \"Photovoltaics surface\" component."
                return optimalSystemSize, Yield, CUFperYear, basicPRperYear, temperatureCorrectedPRperMonth, temperatureCorrectedPRperYear, energyOffsetPerMonth, energyOffsetPerYear, energyValue, embodiedEnergy, embodiedCO2, CO2emissionRate, EPBT, EROI, ACenergyDemandAndConditionalInputs, printMsg
        else:
            # ACenergyDemandPerYear_ not inputted
            optimalSystemSize = Yield = CUFperYear = basicPRperYear = temperatureCorrectedPRperMonth = temperatureCorrectedPRperYear = energyOffsetPerMonth = energyOffsetPerYear = energyValue = embodiedEnergy = embodiedCO2 = CO2emissionRate = EPBT = EROI = None
            ACenergyDemandAndConditionalInputs = False
            printMsg = "Data needs to be inputted into ACenergyDemandPerHour_ in order to calculate the optimalSystemSize.\n\n" + \
                       "If you did input data to ACenergyDemandPerHour_, then its sum is 0 kWh. optimalSystemSize can not be calculated unless ACenergyDemandPerHour_ sum > 0 kWh."
            return optimalSystemSize, Yield, CUFperYear, basicPRperYear, temperatureCorrectedPRperMonth, temperatureCorrectedPRperYear, energyOffsetPerMonth, energyOffsetPerYear, energyValue, embodiedEnergy, embodiedCO2, CO2emissionRate, EPBT, EROI, ACenergyDemandAndConditionalInputs, printMsg
    else:
        # optimal_ set to False
        optimalSystemSize = None
    
    ACenergyDemandAndConditionalInputs = True
    printMsg = "ok"
    return optimalSystemSize, Yield, CUFperYear, basicPRperYear, temperatureCorrectedPRperMonth, temperatureCorrectedPRperYear, energyOffsetPerMonth, energyOffsetPerYear, energyValue, embodiedEnergy, embodiedCO2, CO2emissionRate, EPBT, EROI, ACenergyDemandAndConditionalInputs, printMsg


def printOutput(locationName, PVsurfacePercent, moduleActiveAreaPercent, srfArea, activeArea, nameplateDCpowerRating, moduleEfficiency, lifetime, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency):
    resultsCompletedMsg = "Photovoltaics performance metrics successfully calculated!"
    
    embodiedEnergyPerMJ_M2 = embodiedEnergyPerGJ_M2*1000
    embodiedCO2PerKg_M2 = embodiedCO2PerT_M2*1000
    
    printOutputMsg = \
    """
Input data:

Location:  %s,

Surface percentage used for PV modules:  %0.2f,
Active area Percentage:  %0.2f,
Surface area (m2):  %0.2f,
Surface active area (m2):  %0.2f,
Nameplate DC power rating (kW):  %0.2f,
Module efficiency:  %s,

Energy cost per KWh:  %s,
Embodied energy/m2 (MJ/m2):  %0.2f,
Embodied CO2/m2 (kg CO2/m2):  %0.2f,
Lifetime:  %s,
gridEfficiency:  %s,
    """ % (locationName, PVsurfacePercent, moduleActiveAreaPercent, srfArea, activeArea, nameplateDCpowerRating, moduleEfficiency, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerKg_M2, lifetime, gridEfficiency)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        if _PVsurface:
            unitConversionFactor = lb_preparation.checkUnits()
            unitAreaConversionFactor = unitConversionFactor**2
            nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleEfficiency, temperatureCoefficientFraction, moduleActiveAreaPercent, ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, lifetime, gridEfficiency, locationName, validInputData, printMsg = PVinputData(_PVsurface, PVsurfacePercent_, unitConversionFactor, PVmoduleSettings_, _ACenergyPerHour, _totalRadiationPerHour, _cellTemperaturePerHour, ACenergyDemandPerHour_, energyCostPerKWh_, embodiedEnergyPerM2_, embodiedCO2PerM2_, lifetime_, gridEfficiency_)
            if validInputData:
                # all inputs ok
                if _runIt:
                    optimalSystemSize, Yield, CUFperYear, basicPRperYear, temperatureCorrectedPRperMonth, temperatureCorrectedPRperYear, energyOffsetPerMonth, energyOffsetPerYear, energyValue, embodiedEnergy, embodiedCO2, CO2emissionRate, EPBT, EROI, ACenergyDemandAndConditionalInputs, printMsg = main(ACenergyPerHourData, ACenergyPerHourDataFiltered, totalRadiationPerHourData, totalRadiationPerHourDataFiltered, cellTemperaturePerHourData, cellTemperaturePerHourDataFiltered, ACenergyDemandPerHourData, nameplateDCpowerRating, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, moduleEfficiency, temperatureCoefficientFraction, lifetime, gridEfficiency, locationName)
                    if ACenergyDemandAndConditionalInputs:
                        printOutput(locationName, PVsurfacePercent, moduleActiveAreaPercent, srfArea, activeArea, nameplateDCpowerRating, moduleEfficiency, lifetime, energyCostPerKWh, embodiedEnergyPerGJ_M2, embodiedCO2PerT_M2, gridEfficiency)
                    else:
                        print printMsg
                        ghenv.Component.AddRuntimeMessage(level, printMsg)
                else:
                    print "All inputs are ok. Please set the \"_runIt\" to True, in order to run the Photovoltaics performance metrics"
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please input a Surface (not polysurface) to \"_PVsurface\". The same Surface you inputted to \"Photovoltaics Surface\" component."
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
