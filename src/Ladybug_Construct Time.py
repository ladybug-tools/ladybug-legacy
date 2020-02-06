# Construct Time
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
Use this component to construct a specific hour from corresponding time in hours, minutes and seconds.  The output can be plugged into the analysisPeriod or sunPath components.
-
Provided by Ladybug 0.0.68

    Args:
        _hour_: A number between 1 and 23 representing the hour of the day.
        _minutes_: A number between 1 and 60 representing the minute of the hour.
        _seconds_: A number between 1 and 60 representing the second of the minute.
    Returns:
        hour: An output hour that an be plugged into the analysisPeriod or sunPath components.

"""
ghenv.Component.Name = "Ladybug_Construct Time"
ghenv.Component.NickName = 'constructTime'
ghenv.Component.Message = 'VER 0.0.68\nFEB_06_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = 'LB-Legacy'
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

hour = _hour_ + _minutes_/60 + _seconds_/3600