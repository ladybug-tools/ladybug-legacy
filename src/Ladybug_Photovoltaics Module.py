# Photovoltaics module
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
Use this component to define the Photovoltaics module settings.
-
If nothing inputed, the following PV module settings will be used by default:
- moduleType: Close (flush) roof mount 
- moduleEfficiency: 15%
- temperatureCoefficient: -0.5 %/C
- moduleActiveAreaPercent: 90%
-
Provided by Ladybug 0.0.62
    
    input:
        moduleType_: Module type and mounting configuration:
                     -
                     0 = Glass/cell/polymer sheet, Insulated back (pv curtain wall, pv skylights)
                     1 = Glass/cell/glass, Close (flush) roof mount (pv array mounted parallel and relatively close to the plane of the roof (between 5 and 15 centimenters))
                     2 = Glass/cell/polymer sheet, Open rack (ground mount array, flat/sloped roof array that is tilted, pole-mount solar panels, solar carports, solar canopies)
                     3 = Glass/cell/glass, Open rack (the same as upper "2" type, just with a glass on the back part of the module).
                     -
                     If not supplied, default type: "Glass/cell/glass, Close (flush) roof mount" (1) is used.
        moduleEfficiency_: The ratio of electrical energy output from the PV module to input solar energy from the sun.
                           Current typical module efficiencies for crystalline silicon modules range from 14-20%
                           -
                           If not defined, default value of 15(%) will be used.
                           -
                           In percent (%).
        temperatureCoefficient_: A coefficient which accounts for the percentage the solar module's DC output power decrease/increase for every degree Celsius the solar cells temperature rises above/below 25C. 
                                 -
                                 In general it ranges from -0.44 to -0.5 for crystaline silicon modules.
                                 -
                                 If not supplied, -0.5 will be used as a default.
                                 -
                                 In %/C.
        moduleActiveAreaPercent_: Percentage of the module's area excluding module framing and gaps between cells. 
                                  -
                                  If not supplied, default value of 90(%) will be used.
                                  -
                                  In percent (%).
    
    output:
        readMe!: ...
        PVmoduleSettings: A list of PV module settings. Plug it to "Photovoltaics surface" component's "PVmoduleSettings_" input.
"""

ghenv.Component.Name = "Ladybug_Photovoltaics Module"
ghenv.Component.NickName = "PhotovoltaicsModule"
ghenv.Component.Message = 'VER 0.0.62\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
#ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleLBVersion = VER 0.0.61\nDEC_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc


def main(moduleType, moduleEfficiency, temperatureCoefficientPercent, moduleActiveAreaPercent):
    
    # checking for inputs and input ranges
    if (moduleType == None) or (moduleType < 0) or (moduleType > 3):
        moduleType = 1  # default for Glass/cell/glass, Close (flush) roof mount
    
    if (moduleEfficiency == None) or (moduleEfficiency <= 0) or (moduleEfficiency > 100):
        moduleEfficiency = 15  # default in %, for crystalline silicon PV modules
    
    if (temperatureCoefficientPercent == None) or (temperatureCoefficientPercent >= 0):
        temperatureCoefficientPercent = -0.5  # default in %, for crystalline silicon PV modules
    
    if (moduleActiveAreaPercent == None) or (moduleActiveAreaPercent <= 0) or (moduleActiveAreaPercent > 100):
        moduleActiveAreaPercent = 90  # default in %
    
    PVmoduleSettings = [moduleType, moduleEfficiency, temperatureCoefficientPercent, moduleActiveAreaPercent]
    
    resultsCompletedMsg = "Module settings component results successfully completed!"
    moduleTypesL = ["Glass/cell/polymer sheet Insulated back", "Glass/cell/glass Close (flush) roof mount", "Glass/cell/polymer sheet Open rack", "Glass/cell/glass Open rack"]
    model = moduleTypesL[moduleType]
    
    printOutputMsg = \
    """
Input data:

Module type: %s (%s)
Module efficiency: %s
Temperature coefficient: %s
Module active area percent: %s
    """ % (moduleType, model, moduleEfficiency, temperatureCoefficientPercent, moduleActiveAreaPercent)
    print resultsCompletedMsg
    print printOutputMsg
    
    return PVmoduleSettings


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        
        PVmoduleSettings = main(moduleType_, moduleEfficiency_, temperatureCoefficient_, moduleActiveAreaPercent_)
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