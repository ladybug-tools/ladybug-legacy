# Location Finder
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
This component uses Google Maps API to generate locations.
-
This component requires an internet connection and a secure connection (HTTPS), it runs for free up to 2,500 requests per day. Once you go over this limit the component doesn't work.
For informations about the rules of use of Google Maps API, take a look at this link:
https://developers.google.com/maps/pricing-and-plans/#details
-
Special thanks goes to Google Maps.
-
Provided by Ladybug 0.0.68
    
    Args:
        _address: Write a location address. For example,
        -
        'Colosseum, Rome'    OR
        .
        'Colosseum, Piazza del Colosseo, 1, 00184 Roma, Italy'
        
        APIKey: Your Google PLACES API KEY. Generate one from: https://developers.google.com/maps/documentation/geocoding/get-api-key
    Returns:
        readMe!: ...
        location: A list of text summarizing the location data in the weather file (use this to construct the sun path).
"""

ghenv.Component.Name = "Ladybug_Location Finder"
ghenv.Component.NickName = 'LocationFinder'
ghenv.Component.Message = 'VER 0.0.68\nJAN_01_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Grasshopper.Kernel as gh
import scriptcontext as sc
import urllib
import socket
import System
import os
import re

try:
    System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12
except AttributeError:
    # TLS 1.2 not provided by MacOS .NET Core; revert to using TLS 1.0
    System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls


class GoogleToolsLocation:
    
    def __init__(self, address, _APIKey):
        self.address = address
        self.key = _APIKey
    
    
    def findLatLonName(self):
        try:
            urlPart1 = "https://maps.googleapis.com/maps/api/geocode/json?address="
            urlPart2 = self.address
            open_file = urllib.urlopen(urlPart1 + urlPart2 + '&key=' + self.key)
            print self.address
            read_file = open_file.read()
            
            
            withoutSymbol_line = re.sub('[{}\]\[]', '', read_file)
            lines = withoutSymbol_line.split('\n')
            start_index = [i for i, elem in enumerate(lines) if 'location' in elem][0]
        except IndexError:
            return None, None, None
            
        lat = lines[start_index + 1].replace(',','').partition(":")
        lon = lines[start_index + 2].replace(',','').partition(":")
        latitude = lat[2][1:]
        longitude = lon[2][1:]
        
        index_detail = [i for i, elem in enumerate(lines) if 'formatted_address' in elem]
        address = lines[index_detail[0]].partition(":")[2].replace('"', '')
        locationName = address[1:-1]
        
        open_file.close()
        
        return latitude, longitude, locationName.decode('utf8')
    
    
    def timeZoneLocation(self, latitude, longitude):
        urlPart1 = "https://maps.googleapis.com/maps/api/timezone/json?location="
        uslPart3 = "&timestamp=1331161200"
        url = urlPart1 + str(latitude) + ',' + str(longitude) + uslPart3 + '&key='+ self.key
        
        # The Google Maps Time Zone API must be over SSL
        appdata = os.getenv("APPDATA")
        timeZone_file = os.path.join(appdata, "Ladybug\\", "timeZone.txt")
        client = System.Net.WebClient()
        written_file = client.DownloadFile(url, timeZone_file)
        open_file = open(timeZone_file, 'r')
        txt = open_file.read()
        
        withoutSymbol_line = re.sub('[{}\]\[ \n]', '', txt)
        lines = withoutSymbol_line.split(',')
        timeZone = float(lines[1].partition(":")[2]) / 3600
        
        open_file.close()
        os.remove(timeZone_file)
        
        return timeZone
    
    
    def elevationLocation(self, latitude, longitude):
        
        urlPart1 = "https://maps.googleapis.com/maps/api/elevation/json?locations="
        url = urlPart1 + str(latitude) + ',' + str(longitude) + '&key='+ self.key
        open_file = urllib.urlopen(url)
        read_file = open_file.read()
        
        withoutSymbol_line = re.sub('[{}\]\[ ]', '', read_file)
        lines = withoutSymbol_line.split('\n')
        elevation = float(lines[3].replace(',','').partition(":")[2])
        
        open_file.close()
        
        return elevation


def createLocation(locationName, latitude, longitude, timeZone, elevation):
    location = "Site:Location,\n" + \
            locationName + ',\n' + \
            str(latitude)+',      !Latitude\n' + \
            str(longitude)+',     !Longitude\n' + \
            str(timeZone)+',     !Time Zone\n' + \
            str(elevation) + ';       !Elevation'
    
    return location


def checkInternetConnection():
    server = "www.google.com"
    try:
        host = socket.gethostbyname(server)
        port = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
        return False


def main():
    if _address and _APIKey:
        address = urllib.quote(_address.encode('utf8'), '%')
        
        location = GoogleToolsLocation(address, _APIKey)
        
        latitude, longitude, completeAddress = location.findLatLonName()
        
        if latitude != None and longitude != None and completeAddress != None:
            print("complete address: {}".format(completeAddress))
            locationName = completeAddress.split(',')[0]
            timeZone = location.timeZoneLocation(latitude, longitude)
            elevation = location.elevationLocation(latitude, longitude)
            
            location = createLocation(locationName, latitude, longitude, timeZone, elevation)
        else:
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Location not found, please try to change the address or connect the correct API Key.")
            return -1
        return location


initCheck = False
if sc.sticky.has_key('ladybug_release'):
    initCheck = True
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = True
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")

if initCheck:
    if checkInternetConnection():
        
        result = main()
        if result != -1:
            
            location = result
            
    else:
        warning = "Please enable your internet connection."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)