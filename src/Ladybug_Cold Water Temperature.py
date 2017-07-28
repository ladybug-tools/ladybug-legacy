# Cold water temperature
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
Use this component to calculate the cold (inlet, mains) water temperature, if water pipes are burried undeground.

Sources:
http://www.energy.ca.gov/2013publications/CEC-400-2013-003/CEC-400-2013-003-CMF-REV.pdf
http://www.nrel.gov/docs/fy04osti/35917.pdf
http://www.solarthermalworld.org/sites/gstec/files/story/2015-05-31/textbook_swh.pdf
-
Provided by Ladybug 0.0.65
    
    input:
        method_: A method by which the cold water temperature will be calculated:
                 -
                 0 - Carslaw and Jaeger (used by DOE-2)
                 1 - Christensen and Burch (used by EnergyPlus)
                 2 - used by RETScreen
                 -
                 If not supplied, method "1" (Christensen and Burch) will be used by default.
        _dryBulbTemperature: Hourly Dry Bulb Temperature (air temperature).
                             Import it from Ladybug "Import EPW" component.
                             -
                             In C.
        minimalTemperature_: The minimum cold temperature value.
                             For example this input can be used to prevent the water in your pipes from freezing, by limiting it to 1C (33.8F).
                             -
                             If not supplied, default value 1 (C) will be used.
                             -
                             In C.
        soilThermalDiffusivity_: The ability of a soil to conduct thermal energy relative to its ability to store thermal energy.
                                 -
                                 This input is only important for method "0" !!!
                                 Soil type for method "1" is unknown, and can not be changed. The "1" formula is derived from various field and soil data accross USA.
                                 Soil type for method "2" is fixed to: wet clay soil, and can not be changed.
                                 -
                                 Soil thermal diffusivity for particular types of soil (m2/s * 10^(-7)):
                                 2.4 - dry sand
                                 7.4 - wet sand
                                 2.5 - dry clay
                                 5.1 - wet clay
                                 1.0 - dry peat
                                 1.2 - wet peat
                                 12.9 - dense rock
                                 -
                                 If not supplied, default value 2.5 (dry clay) will be used.
                                 -
                                 In m2/s * 10^(-7).
        pipesDepth_: The soil depth at which cold water pipes are burried at.
                     -
                     This input is only important for method "0" !!!
                     Pipes depth range for method "1" is fixed from 0.3 to 1 meters (1 to 3.5 feet), and can not be changed.
                     Pipes depth for method "2" is fixed to 2 meters, and can not be changed.
                     -
                     If not supplied, default value of 1(m) will be used.
                     -
                     In meters.
    output:
        readMe!: ...
        coldWaterTemperaturePerHour: Cold water temperature for picked pipesDepth_ and soilThermalDiffusivity_, for each hour during a year.
                                     -
                                     In C.
        avrJanuaryColdWaterTemperature: Average January cold water temperature for picked pipesDepth_ and soilThermalDiffusivity_.
                                        Use it for "SWHsystem" component's "avrJanuaryColdWaterTemperature_" input.
                                        -
                                        In C.
        avrColdWaterTemperaturePerYear: Average annual cold water temperature for picked pipesDepth_ and soilThermalDiffusivity_.
                                        -
                                        In C.
"""

ghenv.Component.Name = "Ladybug_Cold Water Temperature"
ghenv.Component.NickName = "ColdWaterTemperature"
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Renewables"
#compatibleLBVersion = VER 0.0.61\nDEC_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc


def main(dryBulbTemperature, method, pipesDepth, soilThermalDiffusivity, minimalTemperature):
    
    if (len(dryBulbTemperature) == 0) or (dryBulbTemperature[0] is ""):
        coldWaterTemperaturePerHour = coldWaterTemperaturePerMonth = coldWaterTemperaturePerYear = None
        printMsg = "Please input data to _dryBulbTemperature input, from Ladybug \"Import EPW\" component."
        validInputData = False
        return coldWaterTemperaturePerHour, coldWaterTemperaturePerMonth, coldWaterTemperaturePerYear, validInputData, printMsg
    elif len(dryBulbTemperature) == 8767:
        dryBulbTemperatureData = dryBulbTemperature[7:]
        locationName = dryBulbTemperature[1]
    elif len(dryBulbTemperature) == 8760:
        dryBulbTemperatureData = dryBulbTemperature
        locationName = "unknown location"
    elif ((len(dryBulbTemperature) != 8767) and (len(dryBulbTemperature) != 8760)):
        coldWaterTemperaturePerHour = coldWaterTemperaturePerMonth = coldWaterTemperaturePerYear = None
        printMsg = printMsg = "Inputted \"_dryBulbTemperature\" list does not have required length.\n\"_dryBulbTemperature\" needs to be a list of either 8767 (heading plus values) or 8760 (only values) items.\nUse Ladybug's \"Import EPW\" component and its ouput: \"dryBulbTemperature\"."
        validInputData = False
        return coldWaterTemperaturePerHour, coldWaterTemperaturePerMonth, coldWaterTemperaturePerYear, validInputData, printMsg
    
    annualAverageTa = sum(dryBulbTemperatureData)/(365*24)
    
    if (method == None) or (method < 0) or (method > 2):
        method = 1  # default, by Christensen and Burch
    
    if (pipesDepth == None) or (pipesDepth <= 0):
        pipesDepth = 1  # dummy default, in meters
    
    if (soilThermalDiffusivity == None) or (soilThermalDiffusivity <= 0):
        soilThermalDiffusivity = 2.5  # dummy default, in m2/s * 10^(-7) (dry clay)
    
    if (minimalTemperature == None):
        minimalTemperature = 1  # default, in C
    
    coldWaterTemperaturePerHour, avrColdWaterTemperaturePerYear, coldWaterTemperaturePerYearMin, coldWaterTemperaturePerYearMax = lb_photovoltaics.inletWaterTemperature(dryBulbTemperatureData, method, minimalTemperature, pipesDepth, soilThermalDiffusivity)
    
    # data for tank size based on HWCdailyAveragePerYear in "Solar Water Heating surface" component:
    coldWater_inputData = [method, minimalTemperature, pipesDepth, soilThermalDiffusivity]
    sc.sticky["swh_coldWater_inputData"] = coldWater_inputData
    
    avrJanuaryColdWaterTemperature = sum(coldWaterTemperaturePerHour[:(31*24)])/(31*24)  # in average C per hour/month
    
    # adding headings to hourly and monthly lists
    coldWaterTemperaturePerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Mains water temperature at %0.2f m" % pipesDepth, "C", "Hourly", (1, 1, 1), (12, 31, 24)] + coldWaterTemperaturePerHour
    
    # printing
    methodName = ["0 - Carslaw and Jaeger", "1 - Christensen and Burch", "2 - RETScreen"]
    print "Input data:\n\nAverage annual dryBulbTemperature (C): %0.2f\nMethod: %s\nMinimum temperature (C): %0.2f\nPipes depth (m): %0.2f\nSoil thermal diffusivity (m2/s * 10^(-7)): %0.2f" % (annualAverageTa, methodName[method], minimalTemperature, pipesDepth, soilThermalDiffusivity)
    
    validInputData = True
    printMsg = "ok"
    return coldWaterTemperaturePerHour, avrJanuaryColdWaterTemperature, avrColdWaterTemperaturePerYear, validInputData, printMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        coldWaterTemperaturePerHour, avrJanuaryColdWaterTemperature, avrColdWaterTemperaturePerYear, validInputData, printMsg = main(_dryBulbTemperature, method_, pipesDepth_, soilThermalDiffusivity_, minimalTemperature_)
        if not validInputData:
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