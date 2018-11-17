#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to convert energy values in BTU/ft2 to Wh/m2 (or kBTU/ft2 to kWh/m2).
-
Provided by Ladybug 0.0.67
    
    Args:
        _BTU_ft2: An energy value or list of energy values in BTU/ft2, kBTU/ft2.
    Returns:
        Wh_m2: The input energy flux values converted to Wh/m2 or kWh/m2 (depeding on input).
"""

ghenv.Component.Name = "Ladybug_BTUft2Whm"
ghenv.Component.NickName = 'BTU2Wh'
ghenv.Component.Message = 'VER 0.0.67\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


Wh_m2 = []
for num in _BTU_ft2:
    try:
        if 'kBTU/ft2' in num.upper():
            Wh_m2.append('KWH/M2')
        elif 'BTU/ft2' in num.upper():
            Wh_m2.append('WH/M2')
        else:
            try: Wh_m2.append(float(num)*3.15459)
            except: Wh_m2.append(num)
    except:
        try: Wh_m2.append(float(num)*3.15459)
        except: Wh_m2.append(num)