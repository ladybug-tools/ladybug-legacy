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
Use this component to convert energy values in W to kW, W/m2 to kW/m2, Wh to kWh, Wh/m2 to kWh/m2, BTU to kBTU, or BTU/ft2 to kBTU/ft2.
-
Provided by Ladybug 0.0.62
    
    Args:
        _Wh: An energy value or list of energy values in W, W/m2, Wh, Wh/m2, BTU, or BTU/ft2.
    Returns:
        BTU: The input energy values converted to kW, kW/m2, kWh, kWh/m2, kBTU, or kBTU/ft2 (depending on the input unit).
"""

ghenv.Component.Name = "Ladybug_Wh2kWh"
ghenv.Component.NickName = 'Wh2kWh'
ghenv.Component.Message = 'VER 0.0.62\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


kWh = []
for num in _Wh:
    try:
        if 'WH/M2' in num.upper():
            kWh.append('kWh/m2')
        elif 'W/M2' in num.upper():
            kWh.append('kW/m2')
        elif num.upper() == 'WH':
            kWh.append('kWh')
        elif num.upper() == 'W':
            kWh.append('kW')
        elif 'BTU' in num.upper():
            kWh.append('kBTU')
        elif 'BTU/FT2' in num.upper():
            kWh.append('kBTU/ft2')
        else:
            try: kWh.append(float(num)/1000)
            except: kWh.append(num)
    except:
        try: kWh.append(float(num)/1000)
        except: kWh.append(num)