# Open Weather data file
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to open a .stat file, which downloads with the .epw weather file and contains information such as the climate zone and maximum temperatures for designing heating/cooling systems.
This component opens the file from a location on your computer.
-
Provided by Ladybug 0.0.65
    
    Args:
        _open: Set Boolean to True to browse for a .stat file on your system.
    Returns:
        readMe!: ...
        statFile: The file path of the selected .stat file.
"""
ghenv.Component.Name = "Ladybug_Open STAT File"
ghenv.Component.NickName = 'Open stat file'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass



import rhinoscriptsyntax as rs

if _open == True:
    filter = "STAT file (*.stat)|*.stat|All Files (*.*)|*.*||"
    statFile = rs.OpenFileName("Open .stat File", filter)
    print 'Done!'
else:
    print 'Please set open to True'
