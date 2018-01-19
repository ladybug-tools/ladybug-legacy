# Solar water heating system
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
Use this component to define Solar water heating system settings.
-
If nothing inputed, the following swh system will be used by default:
- glazed flat plate collectors
- active
- closed loop
- 1 story
- unshaded
-
Provided by Ladybug 0.0.66
    
    input:
        collectorType_: Type of the collector. The following ones can be used:
                        -
                        0 - unglazed flat plate
                        Least expensive.
                        Mostly used for single home domestic how water heating and for heating swimming pools.
                        More cost efficient in tropical and subtropical environments. They can also be used in moderate climates for seasonal usage.
                        Can output water temperatures up to 30C (86F).
                        -
                        1 - glazed flat plate
                        Less expensive.
                        More cost efficient in warm and mild-warm climates. But also used in temperate climates.
                        Mostly used for single home domestic how water heating, space heating and space cooling. And for heating swimming pools.
                        Can output water temperatures up to 60C (140F).
                        - 
                        2 - evacuated tube
                        The most expensive.
                        More cost efficient in cold temperate and cold climates (with low ambient temperature, for example: during winter) and during overcast skies.
                        Evacuated tube collectors (or concentrating collectors) are typically used for industrial applications, or multi residential or commercial buildings for space heating and space cooling. 
                        Can output water temperatures higher than 90C (194F) degrees, up to 177C (350F).
                        -
                        -
                        If not supplied, glazed flat plate collectors (1) will be used.
        activeSWHsystem_: Define whether the swh system is active (pumped) or passive (not pumped).
                          -
                          0 - passive (not pumped) swh system
                          Less expensive.
                          More efficient in warm and mild-warm climates.
                          Does not require electricity to operate.
                          Is used for domestic hot water heating and space heating of a single home.
                          If positioned on a roof require putting a storage tank above the collector, and therefor impose the roof construction to be able to carry the weight of the storage tank.
                          SWHsurface component supports passive swh systems with auxiliary heater.
                          -
                          1 - active (pumped) swh system
                          More expensive.
                          More efficient in temperate and cold climates.
                          Require electricity to operate and battery back-up in case of power outage.
                          Can be used for domestic hot water heating, space heating and space cooling of a single home, building or several buildings (central heating).
                          More efficient in warm and mild-warm climates, where it rarely freezes
                          -
                          -
                          If not supplied, active (pumped) loop will be used.
        openLoop_: Define whether the swh system has an open (indirect) or closed (indirect) solar loop.
                   -
                   0 - closed (indirect) loop
                   Usage of heatexchanger. Antifreeze is a working fluid.
                   More expensive.
                   More efficient in temperate and cold climates where freezing may occur.
                   Also suitable for locations with hard water hardness (mineral content).
                   -
                   1 - open (direct) loop
                   No usage of heatexchangers. Water is the working fluid.
                   Less expensive.
                   More efficient in warm and mild-warm climates, where it rarely freezes (air temperature never drops below 5C(41F) degrees).
                   Only suitable for locations with low water hardness (mineral content) otherwise limescale will form in solar collectors.
                   -
                   -
                   If not supplied, closed (indirect) loop will be used.
        numberOfStories_: Total number of stories plus basement (if there is a basement).
                          This input is used to calculate the total piping length in the solar loop, based on an assumption that the storage tank will be located at the lowest story (basement or ground floor), and solar collectors are located at the roof.
                          -
                          Example 1:
                          a house with a ground floor, first floor and a basement - has 3 stories total.
                          Example 2:
                          a house with a ground floor, first floor, second floor and without a basement - has 3 stories total.
                          -
                          If sollar collectors are used on a ground instead of roof, use the "Solar Water Heating System Detailed" component instead of this one to enter the exact pipe length of the solar loop.
                          -
                          -
                          If not supplied, "1" story will be used as a default value (a house with only a ground floor, without a basement).
        skyExposureFactor_: Continuous Sky Exposure Factor - portion of the visible sky (dome). It defines the shading of the diffuse irradiance components. It ranges from 0 to 1.
                            Import it from "Sunpath shading" component's "skyExposureFactor" output.
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
        
    output:
        readMe!: ...
        SWHsystemSettings: A list of all Solar water heating system settings. Plug it to SWHsurface component's "SWHsystemSettings_" input.
"""

ghenv.Component.Name = "Ladybug_Solar Water Heating System"
ghenv.Component.NickName = "SolarWaterHeatingSystem"
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Renewables"
#compatibleLBVersion = VER 0.0.61\nDEC_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc


def SWHsystemInputData(collectorType, activeSWHsystem, openLoop, numberOfStories, skyExposureFactor, beamIndexPerHour):
    
    if (collectorType == 0):
        # unglazed flat plate
        collectorOpticalEfficiency = 0.87
        collectorThermalLoss = 21
        collectorActiveAreaPercent = 90
        IAMcoefficient = 0.1
        deliveryWaterTemperature = 30
    elif (collectorType == 2):
        # evacuated tube
        collectorOpticalEfficiency = 0.5
        collectorThermalLoss = 1.5
        collectorActiveAreaPercent = 90
        IAMcoefficient = -0.05
        deliveryWaterTemperature = 60
    elif (collectorType == 1) or (collectorType < 0) or (collectorType > 2):
        print "Collector type smaller than \"0\" and larger than \"2\" are not supported.\nGlazed flat plate type will be used as default."
        # glazed flat plate
        collectorType = 1
        collectorOpticalEfficiency = 0.7
        collectorThermalLoss = 4
        collectorActiveAreaPercent = 90
        IAMcoefficient = 0.1
        deliveryWaterTemperature = 60
    
    if activeSWHsystem:
        # active swh system (with pumps(s))
        mechanicalRoomTemperatureData = [20 for i in range(8760)]  # default value 20C for each hour = tank storage located inside the building
        pumpPower = None  # will be calculated based on SWH active area
        pumpEfficiency = 0.85  # default value for flat plate glazed collectors
    else:
        # passive swh system (without pump(s))
        mechanicalRoomTemperatureData = ["air temperature"]  # will be equal to air temperature
        pumpPower = 0
        pumpEfficiency = 0
    
    if openLoop:
        # open (direct) loop swh system
        workingFluidHeatCapacity = 4180  # default value for water
        heatExchangerEffectiveness = 1
    else:
        # closed (indirect) loop swh system
        workingFluidHeatCapacity = 3840  # default value for water-ethylenglycol 34%
        heatExchangerEffectiveness = 0.8  # default
    
    if (numberOfStories == None) or (numberOfStories <= 0):
        numberOfStories = 1
    numberOfStories = numberOfStories + 1  # (plus roof)
    pipeLength = 10 * numberOfStories  # in meters
    
    flowRatePerM2 = 0.012  # default value for flat plate collectors
    
    if (skyExposureFactor == None) or (skyExposureFactor < 0) or (skyExposureFactor > 1):
        skyExposureFactor = 1  # default - no shading
    
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
    
    maxWorkingTemperature = 95  # default
    dischargeTemperature = maxWorkingTemperature-3  # default
    avrJanuaryColdWaterTemperature = None  # will be calculated from lb_photovoltaics.inletWaterTemperature()
    pipeDiameter = None  # will be calculated based on sqrt(4 * flowRatePerM2 * collectorActiveArea / flowSpeed / pi)
    pipeInsulationThickness = None  # will be calculated based on pipeDiameter
    pipeInsulationConductivity = 0.027  # default for Polyurethane (PUR)
    tankSizeLiters = None  # will be calculated based on 1.5 * HWCdailyAveragePerYear
    tankLoss = 0.3  # default
    heightDiameterTankRatio = 2.6  # default
    
    # printing
    if mechanicalRoomTemperatureData[0] != "air temperature":
        averageAnnualMechanicalRoomTemp = sum(mechanicalRoomTemperatureData)/len(mechanicalRoomTemperatureData)
    else:
        averageAnnualMechanicalRoomTemp = "will be calculated based on air temperature"
    
    SWHsystemSettings = [collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, workingFluidHeatCapacity, flowRatePerM2, IAMcoefficient, skyExposureFactor, beamIndexPerHourData, maxWorkingTemperature, dischargeTemperature, deliveryWaterTemperature, avrJanuaryColdWaterTemperature, mechanicalRoomTemperatureData, pipeLength, pipeDiameter, pipeInsulationThickness, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeLiters, tankLoss, heightDiameterTankRatio, heatExchangerEffectiveness]
    
    printOutputMsg = \
    """
Input data:

Collector type: %s
Active SWH system: %s
Open loop: %s
Average annual Transmission index of beam irradiance (-): %s


Results in the following SWH system settings:

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
Average mechanical room temperature (C): %s
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
    """ % (collectorType, activeSWHsystem, openLoop, sum(beamIndexPerHourData)/8760, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, workingFluidHeatCapacity, flowRatePerM2, IAMcoefficient, skyExposureFactor, sum(beamIndexPerHourData)/len(beamIndexPerHourData), maxWorkingTemperature, dischargeTemperature, deliveryWaterTemperature, avrJanuaryColdWaterTemperature, averageAnnualMechanicalRoomTemp, pipeLength, pipeDiameter, pipeInsulationThickness, pipeInsulationConductivity, pumpPower, pumpEfficiency, tankSizeLiters, tankLoss, heightDiameterTankRatio, heatExchangerEffectiveness)
    print printOutputMsg
    
    validSWHsystemData = True
    printMsg = "ok"
    
    return SWHsystemSettings, validSWHsystemData, printMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        SWHsystemSettings, validSWHsystemData, printMsg = SWHsystemInputData(collectorType_, activeSWHsystem_, openLoop_, numberOfStories_, skyExposureFactor_, beamIndexPerHour_)
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