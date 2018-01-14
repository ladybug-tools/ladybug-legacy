# Explode Location
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari - based on a wish from Brian Timothy Ringley <mostapha@ladybug.tools> 
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
Use this component to separate and exctract the information in the 'location' output of the importEPW or constructLocation component.
-
Provided by Ladybug 0.0.65

    Args:
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
    Returns:
        readMe! : ...
        locationName: Name of the location.
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        timeZone: Time zone of the location.
        elevation: Elevation of the location.
"""
ghenv.Component.Name = "Ladybug_Decompose Location"
ghenv.Component.NickName = 'explodeLocation'
ghenv.Component.Message = 'VER 0.0.65\nJAN_14_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass



if _location:
    locationStr = _location.split('\n')
    newLocStr = ""
    #clean the idf file
    for line in locationStr:
        if '!' in line:
            line = line.split('!')[0]
            newLocStr  = newLocStr + line.replace(" ", "")
        else:
            newLocStr  = newLocStr + line
    
    newLocStr = newLocStr.replace(';', "")
    
    site, locationName, latitude, longitude, timeZone, elevation = newLocStr.split(',')
    
    latitude, longitude, timeZone, elevation = float(latitude), float(longitude), float(timeZone), float(elevation)
