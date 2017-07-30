# Photovoltaics module
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
Use this component to define the Photovoltaics crystalline silicon (c-Si) module settings.
-
If nothing inputed, the following PV module settings will be used by default:
- module material: crystalline silicon (c-Si)
- mountType: Close (flush) roof mount 
- moduleEfficiency: 15%
- temperatureCoefficient: -0.5 %/C
- moduleActiveAreaPercent: 90%
-
If you would like to use a thin-film module, then use the thin-film module from "Import Sandia Photovoltaics Module" component.
-
Sources:
http://prod.sandia.gov/techlib/access-control.cgi/2004/043535.pdf
-
Provided by Ladybug 0.0.65
    
    input:
        mountType_: Mounting type (configuration) of a module. There are three of them:
                    -
                    0 = Insulated back (pv curtain wall, pv skylights)
                    1 = Close (flush) roof mount (pv array mounted parallel and relatively close to the plane of the roof (between 5 and 15 centimenters))
                    2 = Open rack (ground mount array, flat/sloped roof array that is tilted, pole-mount solar panels, solar carports, solar canopies)
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
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Renewables"
#compatibleLBVersion = VER 0.0.64\nMAR_27_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc


def main(mountType, moduleEfficiency, temperatureCoefficientPercent, moduleActiveAreaPercent):
    
    # checking for inputs and input ranges
    if (mountType == None) or (mountType < 0) or (mountType > 2):
        printMsg = "\"mountType_\" input accepts only the following values: 0,1,2.\n" + \
                   "\"mountType_\" input set to default value: \"1\" (Close (flush) roof mount)."
        print printMsg
        mountType = 1  # default for Glass/cell/glass, Close (flush) roof mount
    
    if (moduleEfficiency == None) or (moduleEfficiency <= 0) or (moduleEfficiency > 100):
        moduleEfficiency = 15  # default in %, for crystalline silicon PV modules
    
    if (temperatureCoefficientPercent == None) or (temperatureCoefficientPercent >= 0):
        temperatureCoefficientPercent = -0.5  # default in %, for crystalline silicon PV modules
    
    if (moduleActiveAreaPercent == None) or (moduleActiveAreaPercent <= 0) or (moduleActiveAreaPercent > 100):
        moduleActiveAreaPercent = 90  # default in %
    
    
    # Sandia Cell Temperature Model
    if mountType == 0:   # glass/cell/polymer sheet   insulated back
        mountTypeName = "insulated back"
        a = -2.81
        b = -0.0455
        deltaT = 0
    elif mountType == 1:   # glass/cell/glass   close roof mount
        mountTypeName = "close roof mount"
        a = -2.98
        b = -0.0471
        deltaT = 1
    elif mountType == 2:   # glass/cell/polymer sheet   open rack
        mountTypeName = "open rack"
        a = -3.56
        b = -0.0750
        deltaT = 3
    
    moduleMaterial = "c-Si"
    
    PVmoduleSettings = [mountTypeName, moduleMaterial, mountType, moduleActiveAreaPercent, moduleEfficiency, temperatureCoefficientPercent, a, b, deltaT]
    
    resultsCompletedMsg = "Photovoltaics Module component results successfully completed!"
    mountTypesL = ["Insulated back", "Close (flush) roof mount", "Open rack"]
    model = mountTypesL[mountType]
    
    printOutputMsg = \
    """
Input data:

Module type:  %s (%s),
Module efficiency:  %s (perc.),
Temperature coefficient:  %s (perc./celsius deg.),
Module active area percent:  %s (perc.),
    """ % (mountType, model, moduleEfficiency, temperatureCoefficientPercent, moduleActiveAreaPercent)
    print resultsCompletedMsg
    print printOutputMsg
    
    return PVmoduleSettings


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        
        PVmoduleSettings = main(mountType_, moduleEfficiency_, temperatureCoefficient_, moduleActiveAreaPercent_)
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