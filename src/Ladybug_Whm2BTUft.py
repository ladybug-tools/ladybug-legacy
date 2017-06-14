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


#Wh to BTU
"""
Use this component to convert energy values in Wh/m2 to BTU/ft2 (or kWh/m2 to kBTU/ft2).
-
Provided by Ladybug 0.0.64
    
    Args:
        _Wh_m2: An energy value or list of energy values in Wh/m2, kWh/m2.
    Returns:
        BTU_ft2: The input energy flux values converted to BTU/ft2, or kBTU/ft2 (depeding on input).
"""

ghenv.Component.Name = "Ladybug_Whm2BTUft"
ghenv.Component.NickName = 'Wh2BTU'
ghenv.Component.Message = 'VER 0.0.64\nJUN_14_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


BTU_ft2 = []
for num in _Wh_m2:
    try:
        if 'KWH/M2' in num.upper():
            BTU_ft2.append('kBTU/ft2')
        elif 'WH/M2' in num.upper():
            BTU_ft2.append('BTU/ft2')
        else:
            try: BTU_ft2.append(float(num)*0.316998331)
            except: BTU_ft2.append(num)
    except:
        try: BTU_ft2.append(float(num)*0.316998331)
        except: BTU_ft2.append(num)