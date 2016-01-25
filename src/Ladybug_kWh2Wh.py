#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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


#kWh to Wh
"""
Use this component to convert energy values in kW to W, kW/m2 to W/m2, kWh to Wh, kWh/m2 to Wh/m2, kBTU to BTU, or kBTU/ft2 to BTU/ft2.
-
Provided by Ladybug 0.0.62
    
    Args:
        _Wh: An energy value or list of energy values in kW, kW/m2, kWh, kWh/m2, kBTU, or kBTU/ft2.
    Returns:
        BTU: The input energy values converted to W, W/m2, Wh, Wh/m2, BTU, or BTU/ft2 (depending on the input unit).
"""

ghenv.Component.Name = "Ladybug_kWh2Wh"
ghenv.Component.NickName = 'kWh2Wh'
ghenv.Component.Message = 'VER 0.0.62\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


Wh = []
for num in _kWh:
    try:
        if 'KWH/M2' in num.upper():
            Wh.append('Wh/m2')
        elif 'KW/M2' in num.upper():
            Wh.append('W/m2')
        elif 'KWH' in num.upper():
            Wh.append('Wh')
        elif 'KW' in num.upper():
            Wh.append('W')
        elif 'KBTU/FT2' in num.upper():
            Wh.append('BTU/ft2')
        elif 'KBTU' in num.upper():
            Wh.append('BTU')
        else:
            try: Wh.append(float(num)*1000)
            except: Wh.append(num)
    except:
        try: Wh.append(float(num)*1000)
        except: Wh.append(num)