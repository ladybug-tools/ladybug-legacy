#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to generate shading depths, numbers of shades, horizontal or vertical boolean values, and shade angles for different cardinal directions to be plugged into the "Ladybug_Shading Designer" component or the "Honeybee_EnergyPlus Window Shade Generator".
-
Provided by Ladybug 0.0.66

    Args:
        _northShdParam_: Shading parameter for north-facing glazing.
        _westShdParam_: Shading parameter for west-facing glazing.
        _southShdParam_: Shading parameter for south-facing glazing.
        _eastShdParam_: Shading parameter for east-facing glazing.
        --------------------: ...
    Returns:
        readMe!: ...
        shdParamList: A list of shading parameters for different cardinal directions to be plugged into either the input of the "ShadingDesigner" component or the "Honeybee_EnergyPlus Window Shade Generator".  Depending on the type of values that you input, these can go into either of these inputs: _depth, _numOfShds, _distBetween, _horOrVertical_, _shdAngle_.
"""
ghenv.Component.Name = "Ladybug_Shading Parameters List"
ghenv.Component.NickName = 'shdParamList'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import scriptcontext as sc

def checkParam(parameter):
    if parameter != None:
        if isinstance(parameter, (bool)): newParam = parameter
        else: newParam = float(parameter)
    else: newParam = None
    return newParam

northShdParam = checkParam(_northShdParam_)
westShdParam = checkParam(_westShdParam_)
southShdParam = checkParam(_southShdParam_)
eastShdParam = checkParam(_eastShdParam_)

shdParamList = northShdParam, westShdParam, southShdParam, eastShdParam
