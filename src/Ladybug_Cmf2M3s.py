# Liter to Gallon
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Djordje Spasic <djordjedspasic@gmail.com> 
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
Use this component to convert volume flow rate from U.S. cubic feet per minute (cfm) to S.I. cubic meters per second (m3/s).
-
Provided by Ladybug 0.0.63
    
    Args:
        _cfm: A value or list of values in cubic feet per minute (cfm).
    Returns:
        m3_s: Input volume flow rate converted to cubic meters per second (m3/s).
"""

ghenv.Component.Name = "Ladybug_Cmf2M3s"
ghenv.Component.NickName = "cfm2m3s"
ghenv.Component.Message = 'VER 0.0.63\nAUG_18_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nMAR_26_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

# component, and component icon is based on "C2F" Ladybug component by Mostapha Sadeghipour Roudsari.
m3_s = []
for num in _cfm:
   if num == "cfm": m3_s.append("m3/s")
   else:
       try: m3_s.append(float(num)*0.000471947)
       except: m3_s.append(num)
