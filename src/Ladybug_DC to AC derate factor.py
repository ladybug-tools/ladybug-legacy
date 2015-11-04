# DC to AC derate factor
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
Use this component to calculate overall DC to AC derate factor for Photovoltaics Surface's "DCtoACderateFactor_" input.
Overall DC to AC derate factor corresponds to various locations and instances in a PV system where power is lost from DC system nameplate to AC power.
-
Component first calculates PVWatts v5 Total losses, then converts them to PVWatts v1 overall DC to AC derate factor.
Based on PVWatts v5 Manual: http://www.nrel.gov/docs/fy14osti/62641.pdf
-
If nothing supplied to the inputs, default value of 0.85 will be used.

-
Provided by Ladybug 0.0.61
    
    input:
        annualShading_: Losses due to buildings, structures, trees, mountains or other objects that prevent solar radiation from reaching the cells.
                  Input range: 0 to 100(%), 0 being unshaded, and 100 being totally shaded PV module.
                  -
                  If not supplied default value of 0(%) will be used.
        age_: Losses over time due to weathering of the PV modules. The loss in performance is typically 1% per year. Example: for the 20th year of operation, an age loss of 19% would be appropriate. 
              Input range: 0 (new module) to 100%(theoretically: 101 year old module)
              -
              If not supplied default value of 0(%) will be used.
        snow_: Losses due to snow covering the array. The default value is zero, assuming either that there is never snow on the array, or that the array is kept clear of snow.
               Input range: 0 (there is never snow on the array, or the array is kept clear of snow) to 100%(an array is theoretically always covered with snow)
               -
               If not supplied default value of 0(%) will be used.
        wiring_: Resistive losses in the DC and AC wires connecting modules, inverters, and other parts of the system.
                 Input range: 0 to 100(%)
                 -
                 If not supplied default value of 2(%) will be used.
        soiling_: Losses due to dust, dirt, leaves, other wildlife droppings, snow, and other foreign matter on the surface of the PV module that prevent solar radiation from reaching the cells. Soiling is location- and weather-dependent. There are greater soiling losses in high-traffic, high-pollution areas with infrequent rain.
                  Input range: 0 to 100(%)
                  -
                  If not supplied default value of 2(%) will be used.
        mismatch_: Electrical losses due to slight differences caused by manufacturing imperfections between modules in the array that cause the modules to have slightly different current-voltage characteristics.
                   Input range: 0 to 100(%)
                   -
                   If not supplied default value of 2(%) will be used.
        availability_: Losses due to scheduled and unscheduled system shutdown for maintenance, grid outages, and other operational factors.
                       Input range: 0 to 100%
                       -
                       If not supplied default value of 3(%) will be used.
        connections_: Resistive losses in electrical connectors in the system.
                      Input range 0 to 100(%)
                      -
                      If not supplied default value of 0.5(%) will be used.
        nameplateRating_: Losses due to accuracy of the manufacturer's nameplate rating. Field measurements of the electrical characteristics of photovoltaic modules in the array may show that they differ from their nameplate rating. Example: a nameplate rating loss of 5% indicates that testing yielded power measurements at STC that were 5% less than the manufacturer's nameplate rating.
                                  Input range 0 to 100(%)
                                  -
                                  If not supplied default value of 1(%) will be used.
        lightInducedDegradation_: Effect of the reduction in the array's power during the first few months of its operation caused by light-induced degradation of photovoltaic cells.
                                  Input range 0 to 100(%)
                                  -
                                  If not supplied default value of 1.5(%) will be used.
    
    output:
        readMe!: ...
        totalLosses: PVWatts v5 representation of DCtoACderateFactor factor.
                      In percent (%).
        DCtoACderateFactor: Factor which accounts for various locations and instances in a PV system where power is lost from DC system nameplate to AC power.
                            Unitless.
"""

ghenv.Component.Name = "Ladybug_DC to AC derate factor"
ghenv.Component.NickName = "DCtoACderateFactor"
ghenv.Component.Message = 'VER 0.0.61\nNOV_03_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nMAY_26_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc


def main(annualShading, age, snow, wiring, soiling, mismatch, availability, connections, nameplateRating, lightInducedDegradation):
    # checking for inputs and input ranges
    if annualShading == None:
        annualShading = 0
    else:
        try:
            annualShading = float(annualShading)
            if float(annualShading) < 0 or float(annualShading) > 100:
                annualShading = 0
        except Exception, e:
            totalLosses = DCtoACderateFactor = False
            validInputs = False
            if annualShading == "Please input \"ACenergyPerHour\" to calculate this output.":
                printMsg = "Please insert a valid \"annualShading_\" input value by supplying data to \"ACenergyPerHour_\" input of the \"Sunpath shading\" component."
            else:
                printMsg = "Something is wrong with your \"annualShading_\" input. Please supply a valid numeric value."
            return totalLosses, DCtoACderateFactor, validInputs, printMsg
    
    if age == None or age < 0 or age > 100:
        age = 0
    if snow == None or snow < 0 or snow > 100:
        snow = 0
    if wiring == None or wiring < 0 or wiring > 100:
        wiring = 2
    if soiling == None or soiling < 0 or soiling > 100:
        soiling = 2
    if mismatch == None or mismatch < 0 or mismatch > 100:
        mismatch = 2
    if availability == None or availability < 0 or availability > 100:
        availability = 3
    if connections == None or connections < 0 or connections > 100:
        connections = 0.5
    if nameplateRating == None or nameplateRating < 0 or nameplateRating > 100:
        nameplateRating = 1
    if lightInducedDegradation == None or lightInducedDegradation < 0 or lightInducedDegradation > 100:
        lightInducedDegradation = 1.5
    
    lossesL = [annualShading, age, snow, wiring, soiling, mismatch, availability, connections, nameplateRating, lightInducedDegradation]
    
    reduction = 1
    for loss in lossesL:
        reduction = reduction * (1 - (loss/100))
        totalLosses = 100*(1-reduction)
    
    nominalInverterEfficiency = 0.96  # default 
    DCtoACderateFactor = (1 - (totalLosses/100))*nominalInverterEfficiency
    
    resultsCompletedMsg = "DC to AC derate factor component results successfully completed!"
    printOutputMsg = \
    """
Input data:

Annual shading: %s
Age: %s
Snow: %s
Wiring: %s
Soiling: %s
Mismatch: %s
Availability: %s
Connections: %s
Nameplate rating: %s
Light-induced degradation: %s
    """ % (annualShading, age, snow, wiring, soiling, mismatch, availability, connections, nameplateRating, lightInducedDegradation)
    print resultsCompletedMsg
    print printOutputMsg
    
    validInputs = True
    printMsg = "ok"
    
    return round(totalLosses,3), round(DCtoACderateFactor,3), validInputs, printMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        totalLosses, DCtoACderateFactor, validInputs, printMsg = main(annualShading_, age_, snow_, wiring_, soiling_, mismatch_, availability_, connections_, nameplateRating_, lightInducedDegradation_)
        if not validInputs:
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
