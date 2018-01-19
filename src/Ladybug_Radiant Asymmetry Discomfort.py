# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
#
# This file is part of Ladybug.
#
# Copyright (c) 2013-2015, ....(YOUR NAME).... <....(YOUR EMAIL)....>
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
Use this component to calculate discomfort from radiant assymetry.
_
The comfort functions in this function come from Figure 5.2.4.1 of ASHRAE 55 2010.
-
Provided by Ladybug 0.0.66

    Args:
        _radTempDifference: The temperature difference between one side of a pla
        _radAsymmType: An integer that represents the type of radiant assymetry being evaluated.  Occupants are more sensitive to warm cielings and cool walls than cool ceilings and warm walls.  Choose from the following options:
            0 = Warm Ceiling
            1 = Cool Wall
            2 = Cool Cieling
            3 = Warm Wall
        PPDThreshold_: The percentage of people dissatisfied (PPD) above which conditions are not longer considered acceptable.  The default is set to 5%, which is the specification for the ASHRAE 55 comfort standard.  The EN-7730 varies from 6% to 10% depending on the building class.
    Returns:
        readMe!: ...
        PPD: The percentage of people dissatisfied (PPD) from radiant asymmetry.
        comfOrNot: A lidt of 0's and 1's (or "False" and "True" values) indicating whether occupants are comfortable under the input conditions.
"""

ghenv.Component.Name = "Ladybug_Radiant Asymmetry Discomfort"
ghenv.Component.NickName = 'radAsymmetry'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import math
import Grasshopper.Kernel as gh

w = gh.GH_RuntimeMessageLevel.Warning

def giveWarning():
    warning = "You have enetered a radiant temperature difference that is beyond the \n" + \
    "range of the original equations derived from logistic regression analysis. \n" + \
    "The maximum radiant asymmetry value will be returned."
    print warning
    ghenv.Component.AddRuntimeMessage(w, warning)

def giveTypeWarning():
    warning = "_radAsymmType not recognized."
    print warning
    ghenv.Component.AddRuntimeMessage(w, warning)

def clacRadAsymmDiscomf(radTempDif, asymmType, PPDThresh = 5):
    PPDList = []
    comfOrNot = []
    
    for temp in radTempDif:
        if asymmType == 0:
            if temp > 23:
                ppd = 100 / (1 + math.exp(2.84 - 0.174 * 23)) - 5.5
                giveWarning()
            else:
                ppd = 100 / (1 + math.exp(2.84 - 0.174 * temp)) - 5.5
        elif asymmType == 1:
            if temp > 15:
                ppd = 100 / (1 + math.exp(6.61 - 0.345 * 15))
                giveWarning()
            else:
                ppd = 100 / (1 + math.exp(6.61 - 0.345 * temp))
        elif asymmType == 2:
            if temp > 15:
                ppd = 100 / (1 + math.exp(9.93 - 0.50 * 15))
                giveWarning()
            else:
                ppd = 100 / (1 + math.exp(9.93 - 0.50 * temp))
        elif asymmType == 3:
            if temp > 35:
                ppd = 100 / (1 + math.exp(3.72 - 0.052 * 35)) - 3.5
                giveWarning()
            else:
                ppd = 100 / (1 + math.exp(3.72 - 0.052 * temp)) - 3.5
        else:
            ppd = None
        
        PPDList.append(ppd)
        if ppd == None: comfOrNot.append(None)
        elif ppd > PPDThresh: comfOrNot.append(0)
        else: comfOrNot.append(1)
    
    return PPDList, comfOrNot





if len(_radTempDifference) and _radAsymmType != None:
    if PPDThreshold_ == None: PPDThreshold = 5
    else: PPDThreshold = PPDThreshold_
    PPD, comfOrNot = clacRadAsymmDiscomf(_radTempDifference, _radAsymmType, PPDThreshold)
