# Open EPW and STAT weather files together
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to automatically create a URL that can be used with the "Open EPW and STAT Weather Files" component. 
Only TMY3 weather files will be searched for and can be downloaded using this component. 
-
Provided by Ladybug 0.0.66

    Args:
        _Location: The output from the Location Finder or constructLocation component. This is essentially a list of text summarizing a location on the earth.
    Returns:
        weatherFileURL: The URL of the weatherfile. Connect this output to OPEN EPW AND STAT WEATHER FILES Component to download the weather file from onebuilding or DOE website"""

ghenv.Component.Name = "Ladybug_Create WeatherFile Download URL"
ghenv.Component.NickName = 'WeatherFileURL'
ghenv.Component.Message = 'VER 0.0.66\nOCT_16_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import rhinoscriptsyntax as rs
import Grasshopper.Kernel as gh

def Location(_location):
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
        
        latitude, longitude= float(latitude), float(longitude)
    return latitude, longitude
    
def Parse():
    file = open("C:/ladybug/epw.csv")
    Lines = file.readlines()
    Lines = Lines[1:]
    Lat = []
    Long = []
    Host = []
    Link = []
    
    for line in Lines:
        line = line.split(',')

        Lat.append(float(line[4]))
        Long.append(float(line[5]))
        Host.append(line[7])
        Link.append(line[6])
    return Lat, Long, Host, Link

def pointCloud(Lat, Long):
    pt = []
    for i in range(0, len(Lat)):
        pt.append(rs.AddPoint((Long[i], Lat[i],0)))
    return pt

def URL(index,Host, Link):
    host = Host[index]
    link = Link[index]
    if host == "onebuilding":
        url = "http://climate.onebuilding.org" + str(link)
    elif host == "doe":
        url = "http://www.energyplus.net/weather-download" + str(link)
    return url


if _Location:
    Lat, Long, Host, Link = Parse()
    
    PointCloud = pointCloud(Lat,Long)
    _Latitude, _Longitude = Location(_Location)
    Point2 = rs.AddPoint(_Longitude,_Latitude,0)
    try:
        index =  rs.PointArrayClosestPoint(PointCloud,Point2)
    except:
        warning = "No weather file found near the selected location. Please search for another location or download the file manually"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w,warning)
    weatherFileURL = URL(index, Host, Link)

else:
    warning2 = "Please connect a valid Location"
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, warning2)