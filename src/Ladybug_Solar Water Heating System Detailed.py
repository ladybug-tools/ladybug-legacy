# Solar water heating system detailed
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Djordje Spasic <djordjedspasic@gmail.com> 
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
Use this component to define a detailed Solar water heating system settings.
-
If nothing inputed, the following swh system will be used by default:
- glazed flat plate collectors
- active
- closed loop
- pipe length: 20 meters
- unshaded
-
Provided by Ladybug 0.0.62
    
    input:
        collectorOpticalEfficiency_: Fr(tau alpha) Collector's optical efficiency coefficient. Also called Collector heat removal factor. Varies based on collector's type. Some default values by type:
                                     -
                                     0.87 - unglazed flat plate
                                     0.70 - glazed flat plate
                                     0.50 - evacuated tube
                                     -
                                     If not supplied, default value 0.70 (glazed flat plate) will be used.
                                     -
                                     Unitless.
        collectorThermalLoss_: (FrUL) Collector's thermal loss coefficient. Varies based on collector's type. Some default values by type:
                                -
                                21 - unglazed flat plate
                                4 - glazed flat plate
                                1.5 - evacuated tube
                                -
                                If not supplied, default value 4 (glazed flat plate) will be used.
                                -
                                In W/m2/C.
        collectorActiveAreaPercent_: Percentage of the collector's area excluding collector framing, lateral insulation, or gaps between evacuated tubes... Also called aperture area.
                                     It ranges from 70 to 95% depending on the type of collector.
                                     -
                                     If not supplied, default value of 90(%) will be used.
                                     -
                                     In percent.
        workingFluidHeatCapacity_: Specific heat of the working fluid.
                                   -
                                   If swh system is intended to be used in a non-freezing or light freezing climate (tropical and subtropical regions), then water should be used as a working fluid. The specific heat of water is: 4180 J/kg/C.
                                   -
                                   If swh system is used in freezing climates (temperate, polar...), an antifreeze needs to be added to the water. In most cases this is Propylen glycol, Ethylen glycol or Bio glycol added in certain percentages to the water. Depending on the freezing temperatures of the climates, there are the following specific heats of water-glycol mixtures:
                                   up to -10C:  water-propylenglycol 25%:  4080 J/kg/C.
                                   up to -10C:  water-ethylenglycol 20%:  4020 J/kg/C.
                                   up to -20C:  water-propylenglycol 38%:  4000 J/kg/C.
                                   up to -20C:  water-ethylenglycol 34%:  3840 J/kg/C.
                                   up to -30C:  water-propylenglycol 47%:  3890 J/kg/C.
                                   up to -40C:  water-ethylenglycol 52%:  3560 J/kg/C.
                                   -
                                   If not supplied 3840 (water-ethylenglycol 34%) J/kg/C will be used.
                                   -
                                   In J/kg/C.
        flowRatePerM2_: Test flow rate of working fluid through the collector per square meter of collector's area.
                        The higher the flow rate, the higher the collector efficiency is. On the other hand higher flow rates require more pump power, larger pipe diameters and can cause erosion corrosion.
                        -
                        If not supplied, a value of 0.012 kg/s/m2 will be used.
                        -
                        In kg/s/m2.
        IAMcoefficient_: Incidence angle modifier coefficient (bo) - Use this input to account for collector efficiency losses due to different angles of incidence.
                         Depends on the type of collector, tilt angle...
                         Some default values depending on the type of collector:
                         -
                         0.1 - glazed flat plate
                         0.1 - unglazed flat plate
                         -0.05 - evacuated tube
                         -
                         If not supplied, 0.1 (glazed flat plate) will be used.
                         -
                         Unitless.
        skyViewFactor_: Continuous Sky View Factor - portion of the visible sky (dome). It defines the shading of the parts of diffuse irradiance. It ranges from 0 to 1.
                        Import it from "Sunpath shading" component's "skyViewFactor" output.
                        -
                        If not supplied, 1 will be used as a default value (SWHsurface is unshaded).
                        -
                        Unitless.
        beamIndexPerHour_: Transmission index of beam (direct) irradiance for each hour during a year. It ranges from 0-1.
                           Import it from "Sunpath shading" component's "beamIndexPerHour" output.
                           -
                           If not supplied, a value of 1 for each hour during a year, will be used (SWHsurface is unshaded).
                           -
                           Unitless.
        maxWorkingTemperature_: Maximal working temperature of the tank storage.
                                It is used to prevent the overheating problems and damage of the swh system due to exceedance of allowable temperature (and pressure) and appearance of fluid boiling.
                                Depends on the quality of pipes, valves, tank, working fluid type... Generally ranges from 93-99C.
                                -
                                If not supplied 95C (203F) will be used.
                                -
                                In C.
        dischargeTemperature_: Storage tank temperature at which the discharge of the excess heat and cold water makeup stops.
                               It is generally 2-3C degrees less than maximal working temperature.
                               -
                               If not supplied maxWorkingTemperature-3C will be used.
                               -
                               In C.
        deliveryWaterTemperature_: Water heater lower thermostat setting. Depends on the type of usage of solar hot water system. In Celsius
                                   For domestic hot water, it is recommended not be lower than 60C (140F).
                                   For space heating, it varies from 33 to 82C (90 to 180F) depending on the type (in-floor tubes, radiators/baseboards, heat exchanger inside a forced-air heater).
                                   For space cooling it varies from 60 to 80C (140 to 176F) depending on the cooling system used.
                                   -
                                   If not supplied, default value: 60C (140F) will be used.
                                   -
                                   In C.
        avrJanuaryColdWaterTemperature_: Average January cold water inlet temperature. This is the temperature of the water from the local pipe grid.
                                      Input it from first item of "Cold Water Temperature" component's "avrColdWaterTemperaturePerMonth" output.
                                      -
                                      If not supplied it will be calculated for the following input data: method "1" (Christensen and Burch), pipes depth from 0.3 to 1 meters.
                                      -
                                      In C.
        mechanicalRoomTemperature_: Temperature of the room where the storage tank will be located.
                                    This input accepts list of values (8760 values or 8767 with heading included) or a single value. If you input a single value, this means that for each 8760 hours during a year, the mechanicalRoomTemperature will correspond to that inputted value.
                                    -
                                    In case your storage tank is located outside, not inside the building (thermosyphon, ics-batch swh systems or active swh systems), supply the "dryBulbTemperature" data from Ladybug's "Import epw" component to "mechanicalRoomTemperature_" input.
                                    -
                                    If not supplied, a value of 20C degrees will be used for each hour during a year (meaning: storage tank is located inside the building).
                                    -
                                    In C.
        pipeLength_: Total pipes length run in the solar loop.
                     -
                     If collectors are located on the roof: a rule of a thumb is to add 10 meters for each story (basement is calculated as a story too) and additionally 10 meters for the roof.
                     For example: for a 3 story building with a basement (basement, ground floor, first floor, second floor, roof), if storage tank is located in the basement and collectors are on the roof, the piping length would be: 4 stories * 10m + 10m (on the roof) = 50m.
                     -
                     If collectors are located on the ground, one would have to estimate the distance from the house to collectors and multiply it by 2 (supply pipes go to collectors and return ones from them).
                     -
                     If nothing inputted, a default value of 20 meters will be used (Ground story house without a basement. Collectors are located on a roof, the storage tank is at the ground story).
                     -
                     In meters.
        pipeDiameter_: Average pipes inner diameter, in milimeters.
                       Depends on overall collector area, working fluid type, piping length...
                       -
                       If not supplied, for active swh systems, it will be calculated as:
                       (4 * flowRatePerM2 * collectorActiveArea / flowSpeed / pi), with flowSpeed assumed to be 0.7 liters/sec.
                       -
                       For passive swh systems as:
                       1.5 times the value of upper formula.
                       -
                       In millimetres.
        pipeInsulationThickness_: Thickness of the pipes insulation, in milimeters.
                                  For pipes with insulation thermal conductivity lower than 0.04 W/(m*K), based on pipeDiameter, the following insulation thicknesses can be used:
                                  -
                                  20 mm - pipeDiameter < 22mm
                                  25mm - pipeDiameter 22 to 28mm
                                  30mm - pipeDiameter 28 to 42mm
                                  equal to pipeDiameter - pipeDiameter 42 to 100mm
                                  100mm - pipeDiameter > 100mm
                                  -
                                  If not supplied, it will be calculate based on pipeDiameter and upper criteria.
                                  -
                                  In millimetres.
        pipeInsulationConductivity_: Pipe's insulation thermal conductivity (k value).
                                     Depends on the type of insulation material used.
                                     Some common solar piping insulation materials are:
                                     -
                                     0.33 - Polyethylene (PEL)
                                     0.04 - Glass wool
                                     0.027 - Polyurethane (PUR) = 0.027
                                     0.0245 - Ethylene Propylene Diene Rubber (EPDM, EPT)
                                     0.023 - Plyisocyanurate (PIR) = 0.023
                                     -
                                     If not supplied, 0.027 (Polyurethane) will be used as a default value.
                                     -
                                     In W/(m*C).
        pumpPower_: Overall circulation pumps power.
                    In SWH systems, there are typically two pumps: solar and storage tank ones.
                    -
                    Circulation pumps power depends on SWH active area, flow rate, working fluid, pipe length and its disposition...
                    Generally they range from 30 W for small swh system, up to a couple of hundreds for large ones (SWH active area > 30m2)
                    -
                    In case of passive circulation (thermosyphon, ICS or batch systems), set the pumpPower to 0.
                    -
                    If not supplied, it will be calculated based on SWHsurface active area (that's "Surface active area" from SWHsurface component's "readMe!" output) and pipeLength.
                    -
                    In Watts.
        pumpEfficiency_: Circulation pumps efficiency (ni) - ratio between hydraulic and supplied, electrical power.
                         Ranges from 0.5 to 0.95 depending on the type, and size of the circulation pump.
                         -
                         If not supplied, 0.85 will be used.
                         -
                         Unitless.
        tankSize_: Storage tank volume in liters.
                   It varies depending on heating load and SWHsurface area.
                   -
                   If not supplied, a default value equal to 1.5 * daily average hot water consumption per year (with 100 liters minimum), will be used.
                   -
                   In Liters.
        tankLoss_: Storage tank's heat loss coefficient (U). Varies from 0.30 to 0.50 depending on the tank volume, insulation type, thickness ...
                   -
                   If not supplied, default value 0.30 will be used.
                   -
                   In W/m2/C.
        heightDiameterTankRatio_: Storage tank height and diameter ratio. It mostly ranges from 1 to 3.
                                  This input is important for calculation of tank's area.
                                  -
                                  If not supplied 2.6 will be used.
                                  -
                                  Unitless.
        heatExchangerEffectiveness_: Depends on the type of heat exchanger: its transfer coefficient, surface, flow rates, working fluid...
                                     It mostly ranges from 0.6 to 0.9 for closed (indirect) loop swh systems. Accepted default value can be 0.8.
                                     -
                                     Set it to 1.0 in case of open (direct) loop swh system (no heat exchanger is used).
                                     -
                                     If not supplied it will be set to 0.8.
                                     -
                                     Unitless.
        _runIt: ...
        
    output:
        readMe!: ...
        SWHsystemSettings: A list of all Solar water heating system settings. Plug it to SWHsurface component's "SWHsystemSettings_" input.
"""

ghenv.Component.Name = "Ladybug_Solar Water Heating System Detailed"
ghenv.Component.NickName = "SolarWaterHeatingSystemDetailed"
ghenv.Component.Message = 'VER 0.0.62\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleLBVersion = VER 0.0.61\nDEC_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc


def SWHsystemInputData(collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, workingFluidHeatCapacity, flowRatePerM2, IAMcoefficient, skyViewFactor, beamIndexPerHour, maxWorkingTemperature, dischargeTemperature, deliveryWaterTemperature, avrJanuaryColdWaterTemperature, mechanicalRoomTemperature, pipeLength, pipeDiameterMM, pipeInsulationThicknessMM, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeLiters, tankLoss, heightDiameterTankRatio, heatExchangerEffectiveness):
    
    # collector inputs
    if (collectorOpticalEfficiency == None) or (collectorOpticalEfficiency <= 0) or (collectorOpticalEfficiency > 1):
        collectorOpticalEfficiency = 0.7  # default value for flat plate glazed collectors
    
    if (collectorThermalLoss == None) or (collectorThermalLoss <= 0):
        collectorThermalLoss = 4  # default value for flat plate glazed collectors
    
    if (collectorActiveAreaPercent == None) or (collectorActiveAreaPercent <= 0) or (collectorActiveAreaPercent > 100):
        collectorActiveAreaPercent = 90  # default value for flat plate glazed collectors
    
    if (workingFluidHeatCapacity == None) or (workingFluidHeatCapacity <= 0):
        workingFluidHeatCapacity = 3840  # default value for water-ethylenglycol 34%
    
    if (flowRatePerM2 == None) or (flowRatePerM2 < 0.01):
        flowRatePerM2 = 0.012  # default value for flat plate collectors
    
    if (IAMcoefficient == None):
        IAMcoefficient = 0.1  # default value for flat plate collectors
    
    if (skyViewFactor == None) or (skyViewFactor < 0) or (skyViewFactor > 1):
        skyViewFactor = 1  # default - no shading
    
    if (len(beamIndexPerHour) == 0) or (beamIndexPerHour[0] is ""):
        beamIndexPerHourData = [1 for i in range(0,8760)]  # default - no shading
    elif (len(beamIndexPerHour) == 8767):
        beamIndexPerHourData = beamIndexPerHour[7:]
    elif (len(beamIndexPerHour) == 8760):
        beamIndexPerHourData = beamIndexPerHour
    else:
        SWHsystemSettings = None
        validSWHsystemData = False
        printMsg = "Something is wrong with your \"beamIndexPerHour_\" input. Please use \"beamIndexPerHour\" output from \"Sunpath shading\" component to generate them."
        
        return SWHsystemSettings, validSWHsystemData, printMsg
    
    # temperature inputs
    if (maxWorkingTemperature == None) or (maxWorkingTemperature <= 0):
        maxWorkingTemperature = 95  # default
    
    if (dischargeTemperature == None) or (dischargeTemperature <= 0) or (dischargeTemperature > maxWorkingTemperature):
        dischargeTemperature = maxWorkingTemperature-3  # default
    
    if (deliveryWaterTemperature == None) or (deliveryWaterTemperature <= 0) or (deliveryWaterTemperature > dischargeTemperature):
        deliveryWaterTemperature = 60  # default
    
    if (avrJanuaryColdWaterTemperature == None) or (avrJanuaryColdWaterTemperature > deliveryWaterTemperature):
        avrJanuaryColdWaterTemperature = None  # will be calculated from lb_photovoltaics.inletWaterTemperature()
    
    if (len(mechanicalRoomTemperature) == 0) or (mechanicalRoomTemperature[0] is ""):
        mechanicalRoomTemperatureData = [20 for i in range(8760)]  # default value 20C for each hour
    elif (len(mechanicalRoomTemperature) == 1):
        mechanicalRoomTemperatureData = [float(mechanicalRoomTemperature[0]) for i in range(8760)]
    elif (len(mechanicalRoomTemperature) == 8760):
        mechanicalRoomTemperatureData = [float(mechanicalRoomTemperature[i]) for i in range(8760)]
    elif (len(mechanicalRoomTemperature) == 8767):
        mechanicalRoomTemperatureNumbers = mechanicalRoomTemperature[7:]
        mechanicalRoomTemperatureData = [float(mechanicalRoomTemperatureNumbers[i]) for i in range(8760)]
    else:
        SWHsystemSettings = None
        validSWHsystemData = False
        printMsg = "Something is wrong with your \"mechanicalRoomTemperature_\" input." + \
                   "If your storage tank is planned to be located outside of the house (on the roof: ICS-batch or Thermosyphone systems) or simply on the ground outside of the house, then input the \"dryBulbTemperature\" data from \"Import epw\" component." + \
                   "You can also input a list of 8760 values if you plan to locate the storage tank inside the house and you know the temperature of the mechanical room for each hour during a year." + \
                   "If you do not know the temperature of the mechanical room for each hour, then an approximation of 20C degrees (68F) can be used for each hour during a year. This is the default behavior in case you do not supply anything to the \"mechanicalRoomTemperature_\" input"
        
        return SWHsystemSettings, validSWHsystemData, printMsg
    
    # piping and pump inputs
    if (pipeLength == None) or (pipeLength <= 0):
        pipeLength = 20  # default value for active swh system
    
    if (pipeDiameterMM == None) or (pipeDiameterMM <= 0):
        pipeDiameterMM = None  # will be calculated based on sqrt(4 * flowRatePerM2 * collectorActiveArea / flowSpeed / pi)
    
    if (pipeInsulationThicknessMM == None) or (pipeInsulationThicknessMM < 0):
        pipeInsulationThicknessMM = None  # will be calculated based on pipeDiameter
    
    if (pipeInsulationConductivity == None) or (pipeInsulationConductivity <= 0):
        pipeInsulationConductivity = 0.027  # default for Polyurethane (PUR)
    
    if (pumpPower == None) or (pumpPower < 0):
        pumpPower = None  # will be calculated based on SWH active area
    
    if (pumpEfficiency == None) or (pumpEfficiency <= 0):
        pumpEfficiency = 0.85  # default value for flat plate glazed collectors
    
    # storage tank inputs
    if (tankSizeLiters == None) or (tankSizeLiters <= 0):
        tankSizeLiters = None  # will be calculated based on 1.5 * HWCdailyAveragePerYear
    
    if (tankLoss == None) or (tankLoss <= 0) or (tankLoss > 1):
        tankLoss = 0.3  # default
    
    if (heightDiameterTankRatio == None) or (heightDiameterTankRatio <= 0):
        heightDiameterTankRatio = 2.6  # default
    
    if (heatExchangerEffectiveness == None) or (heatExchangerEffectiveness <= 0):
        heatExchangerEffectiveness = 0.8  # default
    
    SWHsystemSettings = [collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, workingFluidHeatCapacity, flowRatePerM2, IAMcoefficient, skyViewFactor, beamIndexPerHourData, maxWorkingTemperature, dischargeTemperature, deliveryWaterTemperature, avrJanuaryColdWaterTemperature, mechanicalRoomTemperatureData, pipeLength, pipeDiameterMM, pipeInsulationThicknessMM, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeLiters, tankLoss, heightDiameterTankRatio, heatExchangerEffectiveness]
    # printing
    printOutputMsg = \
    """
Input data:

Collector optical efficiency (-): %0.2f
Collector thermal loss (W/m2/C): %0.2f
Collector active area percent (percent): %0.2f
Working fluid heat capacity (J/kg/C): %0.2f
Flow rate per M2 (kg/s/m2): %0.3f
IAM modifier coefficient (-): %0.2f
Sky View Factor (-): %0.2f
Average annual Transmission index of beam irradiance (-): %0.2f
-----
Max working temperature (C): %0.2f
Discharge temperature (C): %0.2f
Delivery water temperature (C): %0.2f
Average January cold water temperature (C): %s
Average mechanical room temperature (C): %0.2f
-----
Pipe length (m): %0.2f
Pipe diameter (mm): %s
Pipe insulation thickness (mm): %s
Pipe insulation conductivity (W/m/C): %0.2f
Pump power (W): %s
Pump efficiency (-): %0.2f
-----
Tank size (l): %s
Tank loss (W/m2/C): %0.2f
Height-diameter tank ratio (-): %0.2f
Heat exchanger effectiveness (-): %0.2f
    """ % (collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, workingFluidHeatCapacity, flowRatePerM2, IAMcoefficient, skyViewFactor, sum(beamIndexPerHourData)/len(beamIndexPerHourData), maxWorkingTemperature, dischargeTemperature, deliveryWaterTemperature, avrJanuaryColdWaterTemperature, sum(mechanicalRoomTemperatureData)/len(mechanicalRoomTemperatureData), pipeLength, pipeDiameterMM, pipeInsulationThicknessMM, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeLiters, tankLoss, heightDiameterTankRatio, heatExchangerEffectiveness)
    
    print printOutputMsg
    
    validSWHsystemData = True
    printMsg = "ok"
    
    return SWHsystemSettings, validSWHsystemData, printMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        SWHsystemSettings, validSWHsystemData, printMsg = SWHsystemInputData(collectorOpticalEfficiency_, collectorThermalLoss_, collectorActiveAreaPercent_, workingFluidHeatCapacity_, flowRatePerM2_, IAMcoefficient_, skyViewFactor_, beamIndexPerHour_, maxWorkingTemperature_, dischargeTemperature_, deliveryWaterTemperature_, avrJanuaryColdWaterTemperature_, mechanicalRoomTemperature_, pipeLength_, pipeDiameter_, pipeInsulationThickness_, pipeInsulationConductivity_, pumpPower_, pumpEfficiency_, tankSize_, tankLoss_, heightDiameterTankRatio_, heatExchangerEffectiveness_)
        if not validSWHsystemData:
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