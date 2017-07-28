# Liter to Gallon
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
Use this component to convert the liquid volume from Liters to U.S. Gallons (not Imperial Gallons).
-
Provided by Ladybug 0.0.65
    
    Args:
        _L: A value or list of values in Liters.
    Returns:
        G: Input volume converted to U.S. Gallons.
"""

ghenv.Component.Name = "Ladybug_L2G"
ghenv.Component.NickName = "L2G"
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nMAR_26_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

# component, and component icon is based on "C2F" Ladybug component by Mostapha Sadeghipour Roudsari.
G = []
for num in _L:
   if num == "L": G.append("G")
   elif num == "L/h": G.append("G/h")
   else:
       try: G.append(float(num)*1/3.785412)
       except: G.append(num)
