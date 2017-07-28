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


#BTU to Wh
"""
Use this component to convert energy values in BTU to Wh or kBTU to kWh.
-
Provided by Ladybug 0.0.65
    
    Args:
        _BTU: An energy value or list of energy values in BTU or kBTU.
    Returns:
        Wh: The input enervy values converted to Wh or kWh (depeding on input).
"""

ghenv.Component.Name = "Ladybug_BTU2Wh"
ghenv.Component.NickName = 'BTU2Wh'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

Wh = []
for num in _BTU:
    try:
        if 'BTU' in num.upper():
            Wh.append('Wh')
        elif 'KBTU' in num.upper():
            Wh.append('kWh')
        else:
            try: Wh.append(float(num)/3.41214163)
            except: Wh.append(num)
    except:
        try: Wh.append(float(num)/3.41214163)
        except: Wh.append(num)
