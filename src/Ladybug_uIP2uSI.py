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


"""
Use this component to convert U-Values in IP (BTU/hft2F) to U-Values in SI (W/Km2) to plug into any of the Honeybee material components.
-
Provided by Ladybug 0.0.60
    
    Args:
        _R_IP: A U-Value in IP (BTU/hft2F).
    Returns:
        R_SI: The U-Value in SI (W/Km2).
"""

ghenv.Component.Name = "Ladybug_uIP2uSI"
ghenv.Component.NickName = 'uIP2uSI'
ghenv.Component.Message = 'VER 0.0.60\nSEP_14_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


U_SI = []
for num in _U_IP:
    try: U_SI.append(float(num)*5.678263337)
    except: U_SI.append(num)