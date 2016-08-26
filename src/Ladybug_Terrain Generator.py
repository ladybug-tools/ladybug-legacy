# Terrain Generator
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
This component uses Google Maps API to achieve elevation data and satellite images of the terrain generated.
-
This component requires an internet connection and it runs for free up to 2,500 requests per day. Once you go over this limit the component doesn't work.
Note that each surface is a request, for example if you use a surface made by sub-surfaces 6x6, this will be 36 requests.
For informations about the rules of use of Google Maps API, take a look at this link:
https://developers.google.com/maps/pricing-and-plans/#details

Special thanks goes to Google Maps and the authors of gHowl.
-
Provided by Ladybug 0.0.63
    
    Args:
        _basePoint: Input a point here to georeference the terrain model.
        _basePointGeo: Write latitude, longitude and elevation that represent WSG84 coordinates of the base point. You can achieve these type of coordinates from Google Maps or similar.
        -
        e.g. 40.821796, 14.426439, 990
        _surface: Connect multiple surfaces. Remember that each surface is a request and you have 2500 requests per day.
        -
        I suggest you start from a rectangular surface and divide it by using "Isotrim" component, in this way it is possible to control the dimension of the sub-surfaces.
        -
        The output will have the same unit of your Rhino file. Thus the scale factor is 1:1; e.g. if your model is made in meters the outputs will be in meters.
        _numDivision_: Set the number of points for each surface. If no input is connected this will be 15 (grid: 16x16).
        _imgResolution_: Connect an integer number which manage the quality of single satellite image.
        -
        The following list shows the approximate level of detail you can expect to see at each _imgResolution_ level:
        1 = World
        5 = Landmass/continent
        10 = City
        15 = Streets
        20 = Buildings
        -
        The default value is 18.
        _runIt: Set to "True" to run the component and generate the 3D terrain model. 
    Returns:
        readMe!: ...
        pointsGeo : WSG84 coordinates of the grid points (longitude, latitude).
        pointsXY : Cartesian coordinates of the grid points (X, Y).
        pointsZ : Z values of the grid points. Connect this output to a Z vector to move the pointsXY in the right positions.
        imagePath: Satellite images from Google Static Maps API. Connect it to 'DB' input of 'Human Custom Preview Material' to apply textures to the 3d model or to the list of input surfaces.
"""

ghenv.Component.Name = "Ladybug_Terrain Generator"
ghenv.Component.NickName = 'TerrainGenerator'
ghenv.Component.Message = 'VER 0.0.63\nAUG_19_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Rhino
import scriptcontext as sc
import socket
import System
import os
import clr
from math import pi, log, tan, atan, exp

clr.AddReference("Grasshopper")
import Grasshopper.Kernel as gh
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


def checkInputs(basePoint, basePointGeo, surface):
    if basePoint == None or basePointGeo == None or surface == None:
        return False
    elif basePoint and basePointGeo and surface:
        return True


def checkInternetConnection():
    server = "www.google.com"
    try:
        host = socket.gethostbyname(server)
        port = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
        return False


def earthPoint(basePointGeo, basePoint):
    base_point = Rhino.DocObjects.EarthAnchorPoint()
    base_point.EarthBasepointLatitude = basePointGeo.X
    base_point.EarthBasepointLongitude = basePointGeo.Y
    base_point.EarthBasepointElevation = basePointGeo.Z
    base_point.ModelEast = Rhino.Geometry.Vector3d.XAxis
    base_point.ModelNorth = Rhino.Geometry.Vector3d.YAxis
    base_point.ModelBasePoint = basePoint
    
    modelUnit = Rhino.UnitSystem()
    xf = base_point.GetModelToEarthTransform(modelUnit)
    
    return xf


def divideSrf(srf, numDivision):
    pts = []
    srf.SetDomain(0, Rhino.Geometry.Interval(0,1))
    srf.SetDomain(1, Rhino.Geometry.Interval(0,1))
    for i in range(0, numDivision+1):
        for j in range(0, numDivision+1):
            pts.append(srf.PointAt(i/numDivision, j/numDivision))
            
    return pts


def terrainGen(pts, xf, run):
    
    if len(pts) > 257:
        warning = 'Your request is too big. The upper limit of _numDivision_ is 15.'
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    points = [xf * point for point in pts]
    
    list_coordinate = [str(pt.Y) + ',' + str(pt.X) + "|" for pt in points]
    flat_list_coordinate = ''.join(list_coordinate)
    flat_list_coordinate = flat_list_coordinate[:len(flat_list_coordinate)-1]
    url_part2 = flat_list_coordinate
    
    url_part1 = 'https://maps.googleapis.com/maps/api/elevation/json?locations='
    goog_url = url_part1 + url_part2
    
    # Temporary file
    # I should change this part here, the alternative way is to use urllib.request,
    # but it doesn't exist in GH. However this method works and it is fast enough.
    appdata = os.getenv("APPDATA")
    name = os.path.join(appdata, "Ladybug\\", "elevation.txt")
    if len(pts) <= 257:
        if run:
            client = System.Net.WebClient()
            written_file = client.DownloadFile(goog_url, name)
    
    open_file = open(name, 'r')
    txt = open_file.read()
    lines = txt.split('\n')
    
    indices = [i for i, elem in enumerate(lines) if 'elevation' in elem]
    open_file.close()
    
    elevations = []
    for index in indices:
        basic_line = lines[index]
        removed = basic_line.replace(",", "")
        split_elevation = removed.split(' ')
        num = split_elevation[-1]
        num = float(num)
        elevations.append(num)
    
    return points, elevations, pts


def centerPtsGeo(srf):
    centre = Rhino.Geometry.AreaMassProperties.Compute(srf).Centroid
    return centre


def findCorner(relation, list_latitude, list_longitude):
    relation_latitude = relation(list_latitude)
    indices_latitude_relation = {i for i, elem in enumerate(list_latitude) if elem == relation_latitude}
    
    relation_longitude = relation(list_longitude)
    indices_longitude_relation = {i for i, elem in enumerate(list_longitude) if elem == relation_longitude}
    
    a = indices_latitude_relation.intersection(indices_longitude_relation)
    value = list(a)[0]
    
    return value

# This Mercator projection function is made by heltonbiker (http://stackoverflow.com/)
def latlontopixels(lat, lon, zoom, origin_shift, initial_resolution):
    mx = (lon * origin_shift) / 180.0
    my = log(tan((90 + lat) * pi/360.0))/(pi/180.0)
    my = (my * origin_shift) /180.0
    res = initial_resolution / (2**zoom)
    px = (mx + origin_shift) / res
    py = (my + origin_shift) / res
    return px, py


def textureGen(run, center, points, origin_shift, initial_resolution, imgResolution):
    list_latitude = [pt.Y for pt in points]
    list_longitude = [pt.X for pt in points]
    
    upperleft = points[findCorner(max, list_latitude, list_longitude)]
    lowerright = points[findCorner(min, list_latitude, list_longitude)]
    
    zoom = imgResolution
    
    ullon, ullat = (upperleft[0], upperleft[1])
    lrlon, lrlat = (lowerright[0], lowerright[1])
    ulx, uly = latlontopixels(ullat, ullon, zoom, origin_shift, initial_resolution)
    lrx, lry = latlontopixels(lrlat, lrlon, zoom, origin_shift, initial_resolution)
    
    # calculate total pixel dimensions
    dx, dy = ulx - lrx, uly - lry
    
    if dx > 640 or dy > 640:
        warning = 'Your request is too big. Change image resolution or make smaller tiles.'
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    urlPart1 = 'https://maps.googleapis.com/maps/api/staticmap?'
    urlPart2 = "center={0},%20{1}&zoom={2}&size={3}x{4}&maptype=satellite".format(str(center.Y), str(center.X), str(zoom), str(int(dx)), str(int(dy)))
    
    goog_url = urlPart1 + urlPart2
    
    return goog_url


def main():
    
    earth_radius = 6378137
    equator_circumference = 2 * pi * earth_radius
    initial_resolution = equator_circumference / 256.0
    origin_shift = equator_circumference / 2.0
    if _imgResolution_ == None:
        imgResolution = 18
    else: imgResolution = int(_imgResolution_) # make sure that it is an integer number
    if _numDivision_ == None:
        numDivision = 15
    else: numDivision = int(_numDivision_)
    
    
    
    xf = earthPoint(_basePointGeo, _basePoint)
    
    URLs = []
    imagePath = DataTree[System.Object]()
    if _runIt:
        pointsGeo, pointsZ, pointsXY, imagePath  = DataTree[System.Object](), DataTree[System.Object](), DataTree[System.Object](), DataTree[System.Object]()
        
        for i in range(len(_surface)):
            points_srf = divideSrf(_surface[i], numDivision)
            try:
                points, elevations, pts = terrainGen(points_srf, xf, _runIt)
                ptCenter = centerPtsGeo(_surface[i])
                pointGeo = xf * ptCenter
                
                URL = textureGen(_runIt, pointGeo, points, origin_shift, initial_resolution, imgResolution)
                URLs.append(URL)
                
                path = GH_Path(0, i)
                pointsGeo.AddRange(points, path)
                pointsZ.AddRange(elevations, path)
                pointsXY.AddRange(pts, path)
                
            except TypeError: return None, None, None, None
        
        # make a folder for the images
        appdata = os.getenv("APPDATA")
        directory = os.path.join(appdata, "Ladybug\IMG_Google\\")
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            for i, u in enumerate(URLs):
                path = GH_Path(0, i)
                name = directory + str(i) + "elevation.png"
                client = System.Net.WebClient()
                written_file = client.DownloadFile(u, name)
                imagePath.Add(name, path)
        except:
            pass
            print("Something went wrong during the request of images. Please, try again.")
        
        
    else: return None, None, None, None
    
    return pointsGeo, pointsZ, pointsXY, imagePath


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
    lb_preparation = sc.sticky["ladybug_Preparation"]()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")


check = checkInputs(_basePoint, _basePointGeo, _surface)
if check and initCheck:
    if checkInternetConnection():
        result = main()
        if result != -1:
            pointsGeo, pointsZ, pointsXY, imagePath = result
    else:
        warning = "Please enable your internet connection."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else:
    pass
    print("Please provide all inputs.")