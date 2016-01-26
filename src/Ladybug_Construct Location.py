# Explode Location
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari - based Brian Timothy Ringley suggestion <Sadeghipour@gmail.com> 
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
Use this component if you do not have an .epw weather file but have a latitude or other information on the site.
The location output of this component can be used to make a sun plot in the absence of an .epw weather file.
-
Provided by Ladybug 0.0.62

    Args:
        _locationName: A name for the location you are constructing. (ie. Steventon Island, Antarctica)
        _latitude: The latitude of the location you are constructing. Values must be between -90 and 90. Default is set to the equator.
        _longitude_: An optional numerical value representing the longitude of the location you are constructing. This can improve the accuracy of the resulting sun plot.
        _timeZone_: An optional integer representing the time zone of the location you are constructing. This can improve the accuracy of the resulting sun plot.  The time zone should follow the epw convention and should be between -12 and +12, where 0 is at Greenwich, UK, positive values are to the East of Greenwich and negative values are to the West.
        _elevation_: An optional numerical value representing the elevation of the location you are constructing.
    Returns:
        readMe!: ...
        location: A list of text summarizing the location data in the weather file (use this to construct the sun path).
        

"""
ghenv.Component.Name = "Ladybug_Construct Location"
ghenv.Component.NickName = 'constructLocation'
ghenv.Component.Message = 'VER 0.0.62\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

if _locationName and _latitude!=None:
    location = "Site:Location,\n" + \
            _locationName + ',\n' + \
            str(_latitude)+',      !Latitude\n' + \
            str(_longitude_)+',     !Longitude\n' + \
            str(_timeZone_)+',     !Time Zone\n' + \
            str(_elevation_) + ';       !Elevation'
else:
    pass
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "locationName or latitude is missing")
