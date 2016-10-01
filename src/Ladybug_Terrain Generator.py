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
-
Special thanks goes to Google Maps and the authors of gHowl.
-
Provided by Ladybug 0.0.63
    
    Args:
        _basePoint: Input a point here to georeference the terrain model.
        _basePointGeo: It accepts two type of inputs. 
        a) latitude, longitude and elevation that represent WSG84 coordinates of the base point. You can achieve these type of coordinates from Google Maps or similar.
        e.g. 40.821796, 14.426439, 990
        -
        b) location, you can obtain this type of input from "Ladybug_Construct Location", "Ladybug_Location Finder", "Ladybug_Import epw", "Ladybug_Import Location".
        _radius_: A radius to make the terrain 3D model in Rhino model units. The default is set to 100.
        -
        If you provide a big radius, this could require lots of time (also a couple of minutes).
        type_: Select the type of output:
        0 = rectangular mesh
        1 = rectangular surface
        -
        The default value is 0.
        _numOfTiles_: Set the number of tiles (e.g. 4, that means 4x4). If no input is connected this will be 3 (tiles: 3x3).
        _numDivision_: Set the number of points for each tile. If no input is connected this will be 15 (grid: 16x16).
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
        mapType_: Connect an integer number, from 0 to 3, which manages the formats of map.
        -
        0 = Satellite (default)
        1 = Roadmap, specifies a standard roadmap image
        2 = Terrain, it shows terrain and vegetation 
        3 = Hybrid, it specifies a hybrid of the satellite and roadmap image
        _runIt: Set to "True" to run the component and generate the 3D terrain model. 
    Returns:
        readMe!: ...
        pointsGeo : WSG84 coordinates of the grid points (longitude, latitude).
        pointsXY : Cartesian coordinates of the grid points (X, Y).
        pointsZ : Z values of the grid points. Connect this output to a Z vector to move the pointsXY in the right positions.
        tiles: The area which will be calculated. If you want to visualize Satellite images connect this output to 'G' input of 'Human Custom Preview Material'.
        imagePath: Satellite images from Google Static Maps API. Connect it to 'DB' input of 'Human Custom Preview Material' to apply textures to the 3d model or to the list of input surfaces.
        -----------: ...
        terrain: 3D terrain model.
"""

ghenv.Component.Name = "Ladybug_Terrain Generator"
ghenv.Component.NickName = 'TerrainGenerator'
ghenv.Component.Message = 'VER 0.0.63\nSEP_30_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Rhino
import scriptcontext as sc
import socket
import System
import os
import clr
from math import pi, log, tan, atan, exp, sqrt

clr.AddReference("Grasshopper")
import Grasshopper.Kernel as gh
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


def checkInputs(basePoint, basePointGeo):
    if basePoint == None or basePointGeo == None:
        return False
    elif basePoint and basePointGeo:
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
    
    url_part1 = 'http://maps.googleapis.com/maps/api/elevation/json?locations='
    goog_url = url_part1 + url_part2 + '&sensor=false'
    
    # Temporary file
    # I should change this part here, the alternative way is to use urllib.request,
    # but it doesn't exist in GH. However this method works and it is fast enough.
    appdata = os.getenv("APPDATA")
    name = os.path.join(appdata, "Ladybug\\", "elevation.txt")
    if len(pts) <= 257:
        if run:
            try:
                client = System.Net.WebClient()
                written_file = client.DownloadFile(goog_url, name)
            except:
                pass
    
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
    
    return points, elevations


def centerPtsGeo(srf):
    centre = Rhino.Geometry.AreaMassProperties.Compute(srf).Centroid
    return centre


def findCorner(relation, list_latitude, list_longitude):
    relation_latitude = relation(list_latitude)
    indices_latitude_relation = {i for i, elem in enumerate(list_latitude) if elem == relation_latitude}
    
    relation_longitude = relation(list_longitude)
    indices_longitude_relation = {i for i, elem in enumerate(list_longitude) if elem == relation_longitude}
    
    intersection = indices_latitude_relation.intersection(indices_longitude_relation)
    value = list(intersection)[0]
    
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


def textureGen(run, center, points, origin_shift, initial_resolution, imgResolution, mapType):
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
    
    urlPart1 = 'http://maps.googleapis.com/maps/api/staticmap?'
    urlPart2 = "center={0},%20{1}&zoom={2}&size={3}x{4}&maptype={5}&sensor=false".format(str(center.Y), str(center.X), str(zoom), str(int(dx)), str(int(dy)), str(mapType))
    
    goog_url = urlPart1 + urlPart2
    
    return goog_url


def createTiles(base_point, radius, numOfTiles):
    interval_radius = Rhino.Geometry.Interval(-radius, radius)
    rectangle_tiles = Rhino.Geometry.Rectangle3d(Rhino.Geometry.Plane(base_point, Rhino.Geometry.Vector3d.ZAxis), interval_radius, interval_radius).ToNurbsCurve()
    brep_tiles = Rhino.Geometry.Brep.CreatePlanarBreps(rectangle_tiles)[0]
    surface_tiles = brep_tiles.Surfaces[0]
    surface_tiles.SetDomain(0, Rhino.Geometry.Interval(0, 1))
    surface_tiles.SetDomain(1, Rhino.Geometry.Interval(0, 1))
    
    edge = brep_tiles.DuplicateEdgeCurves(True)[0]
    t = edge.DivideByCount(numOfTiles, True)
    
    intervals = []
    for i in range(0, numOfTiles):
        part = Rhino.Geometry.Interval(t[i], t[i+1])
        intervals.append(part)
    
    tiles = []
    for part in intervals:
        for part2 in intervals:
            tiles.append(surface_tiles.Trim(part, part2))
    
    return tiles


def cullAndSortPoints(pts, elevations):
    terrain_pts = [Rhino.Geometry.Point3d(pt.X, pt.Y, elevations[i]) for i, pt in enumerate(pts)]
    cull_pts = list(set(terrain_pts))
    
    cull_pts.sort(key = lambda pt: pt.X)
    cull_pts.sort(key = lambda pt: pt.Y, reverse=True)
    
    return cull_pts


def main():
    earth_radius = 6378137
    equator_circumference = 2 * pi * earth_radius
    initial_resolution = equator_circumference / 256.0
    origin_shift = equator_circumference / 2.0
    
    mapsType = {'0':'satellite', '1':'roadmap', '2':'terrain', '3':'hybrid'}
    
    if _imgResolution_ == None:
        imgResolution = 18
    else: imgResolution = int(_imgResolution_) # make sure that it is an integer number
    if _numDivision_ == None:
        numDivision = 15
    else: numDivision = int(_numDivision_)
    if _radius_ == None:
        radius = 100
    else: radius = _radius_
    if _numOfTiles_ == None:
        numOfTiles = 3
    else: numOfTiles = int(_numOfTiles_)
    if mapType_ == None:
        mapType = mapsType['0']
    else: mapType = mapsType[mapType_]
    if type_ == None: type = 0
    else: type = type_
    
    # location or point3d
    try:
        lat, lon, elev = eval(_basePointGeo)
        basePointGeo = Rhino.Geometry.Point3d(lat, lon, elev)
    except:
        locationName, latitude, longitude, timeZone, elevation = lb_preparation.decomposeLocation(_basePointGeo)
        basePointGeo = Rhino.Geometry.Point3d(latitude, longitude, elevation)
        
    xf = earthPoint(basePointGeo, _basePoint) 
    
    tilesTree = DataTree[System.Object]()
    tiles = createTiles(_basePoint, radius, numOfTiles)
    for i, tile in enumerate(tiles):
        path = GH_Path(0, i)
        tilesTree.Add(tile, path)
    
    points_for_srf = []
    elevations_for_srf = []
    URLs = []
    imagePath = DataTree[System.Object]()
    if _runIt:
        pointsGeo, pointsZ, pointsXY, imagePath  = DataTree[System.Object](), DataTree[System.Object](), DataTree[System.Object](), DataTree[System.Object]()
        
        for i in range(len(tiles)):
            points_srf = divideSrf(tiles[i], numDivision)
            try:
                points, elevations = terrainGen(points_srf, xf, _runIt)
                ptCenter = centerPtsGeo(tiles[i])
                pointGeo = xf * ptCenter
                points_for_srf.extend(points_srf)
                elevations_for_srf.extend(elevations)
                
                URL = textureGen(_runIt, pointGeo, points, origin_shift, initial_resolution, imgResolution, mapType)
                URLs.append(URL)
                
                path = GH_Path(0, i)
                pointsGeo.AddRange(points, path)
                pointsZ.AddRange(elevations, path)
                pointsXY.AddRange(points_srf, path)
                
            except TypeError: return None, None, None, None, None, None
        
        # make 3D points
        # thanks to djordje for this advice
        cull_pts = cullAndSortPoints(points_for_srf, elevations_for_srf)
        num = (numDivision + 1) * numOfTiles - (numOfTiles - 1)
        if type == 0:
            lb_meshpreparation = sc.sticky["ladybug_Mesh"]()
            terrain = lb_meshpreparation.meshFromPoints(num, num, cull_pts)
        elif type == 1:
             uDegree = min(3, num - 1)
             vDegree = min(3, num - 1)
             terrain = Rhino.Geometry.NurbsSurface.CreateThroughPoints(cull_pts, num, num, uDegree, vDegree, False, False)
             
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
    
    else:
        # check the grid size
        dimension = round(((radius * 2) / numOfTiles) / numDivision, 3)
        print("Size of the grid = {0} x {0}".format(dimension))
        return None, None, None, None, None, tilesTree
    
    return pointsGeo, pointsZ, pointsXY, imagePath, terrain, tilesTree


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


check = checkInputs(_basePoint, _basePointGeo)
if check and initCheck:
    if checkInternetConnection():
        result = main()
        if result != -1:
            pointsGeo, pointsZ, pointsXY, imagePath, terrain, tiles = result
    else:
        warning = "Please enable your internet connection."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else:
    pass
    print("Please provide all inputs.")