#C to F
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2020, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Convert from m/s to mile/h 
-
Provided by Ladybug 0.0.68
    
    Args:
        ms: Input wind speed in meters per second
    Returns:
        mph: Output wind speed in miles per hour
"""

ghenv.Component.Name = "Ladybug_ms2mph"
ghenv.Component.NickName = 'ms2mph'
ghenv.Component.Message = 'VER 0.0.68\nFEB_06_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = 'LB-Legacy'
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

def convertTomph(ms):
    return ms*2.23694
    
mph = []
for num in ms:
   if num == 'm/s': mph.append('mph')
   else:
       try: mph.append(convertTomph(num))
       except: mph.append(num)