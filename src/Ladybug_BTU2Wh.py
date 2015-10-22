#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to convert energy values in BTU to Wh, kBTU to kWh, BTU/ft2 to Wh/m2, or kBTU/ft2 to kWh/m2.
-
Provided by Ladybug 0.0.60
    
    Args:
        _BTU: An energy value or list of energy values in BTU, kBTU, BTU/ft2, or kBTU/ft2.  Note that, for the component to recognize flux (division by ft2), the input must have a Ladybug header.
    Returns:
        Wh: The input enervy values converted to Wh, kWh, Wh/m2, or kWh/m2 (depeding on input).
"""

ghenv.Component.Name = "Ladybug_BTU2Wh"
ghenv.Component.NickName = 'BTU2Wh'
ghenv.Component.Message = 'VER 0.0.60\nOCT_15_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

floorNorm = False
Wh = []
for num in _BTU:
    try:
        if 'BTU/FT2' in num.upper():
            Wh.append('Wh/m2')
            floorNorm = True
        elif 'KBTU/FT2' in num.upper():
            Wh.append('kWh/m2')
            floorNorm = True
        elif 'BTU' in num.upper():
            Wh.append('Wh')
        elif 'KBTU' in num.upper():
            Wh.append('kWh')
        else:
            if floorNorm == True:
                try: Wh.append(float(num)/0.316998331)
                except: Wh.append(num)
            else:
                try: Wh.append(float(num)/3.41214163)
                except: Wh.append(num)
    except:
        if floorNorm == True:
            try: Wh.append(float(num)/0.316998331)
            except: Wh.append(num)
        else:
            try: Wh.append(float(num)/3.41214163)
            except: Wh.append(num)
