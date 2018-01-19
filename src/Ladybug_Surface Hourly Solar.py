# Comfort Parameters
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to quickly compute the hourly solar radiation or illuminance falling on an unobstructed surface that faces any direction from EPW inputs.
_
The calculation method of this component is faster than running a full Ladybug Solar Radiation Analysis but this comes at the cost of not being able to account for obstructions that block the sun.
-
Provided by Ladybug 0.0.66
    Args:
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        _directNormal: A list of 8760 hourly values (with an optional Ladybug header on it) that denotes direct normal solar.  This can be either directNormalRadiation or directNormalIlluminance (depending on what output is needed).  These values can be obtained from the "Ladybug_Import EPW" component or the "Ladybug_Design Day Sky Model" component.
        _diffuseHorizontal: A list of 8760 hourly values (with an optional Ladybug header on it) that denotes diffuse horizontal solar.  This can be either globalHorizontalRadiation or globalHorizontallIlluminance (depending on what output is needed).  These values can be obtained from the "Ladybug_Import EPW" component or the "Ladybug_Design Day Sky Model" component.
        _srfAzimuth_: A number between 0 and 360 that represents the azimuth that a surface is facing in degrees.  A value of 0 means North, 90 means East, 180 means South, and 270 means West.  If no value is connected here, a default azimuth of 180 will be assumed for a south facing window.
        _srfAltitude_: A number between 0 and 90 that represents the altitude that a surface is facing in degrees.  A value of 0 means the surface is facing the horizon and a value of 90 means a surface is facing straight up.  If no value is connected here, a default altitude of 90 will be assumed for a surface facing straignt up.
    Returns:
        readMe!: ...
        srfDirect: Hourly direct solar falling on the surface.
        srfDiffuse: Hourly diffuse solar falling on the surface.
        srfTotal: Hourly total solar falling on the surface.
        srfDirection: A vector showing the direction that the surface is facing in the Rhino scene.
"""
ghenv.Component.Name = "Ladybug_Surface Hourly Solar"
ghenv.Component.NickName = 'SrfSolar'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.60\nJUL_06_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Rhino as rc
import math
import Grasshopper.Kernel as gh

def checkInputs():
    analysisPeriod = [(1,1,1),(12,31,24)]
    header = []
    
    if len(_directNormal) == 8760:
        directNormal = [float(x) for x in _directNormal]
    elif len(_directNormal) > 8 and 'Direct Normal' in _directNormal[2]:
        directNormal = _directNormal[7:]
        analysisPeriod = _directNormal[5:7]
        header =_directNormal[:7]
    else:
        warning = 'The connected _directNormal must be either a list of 8760 values or have a Ladybug header on it that states "Direct Normal Radiation" in it.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    if len(_diffuseHorizontal) == 1:
        diffuseHorizontal = [float(_diffuseHorizontal[0]) for x in range(8760)]
    elif len(_diffuseHorizontal) == 8760:
        diffuseHorizontal = [float(x) for x in _diffuseHorizontal]
    elif len(_diffuseHorizontal) > 8 and 'Diffuse Horizontal' in _diffuseHorizontal[2]:
        diffuseHorizontal = _diffuseHorizontal[7:]
        analysisPeriod = _diffuseHorizontal[5:7]
        header =_diffuseHorizontal[:7]
    else:
        warning = 'The connected _diffuseHorizontal must be either a single value for all hours, list of 8760 values or have a Ladybug header on it that states "Diffuse Horizontal Radiation" in it.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    return directNormal, diffuseHorizontal, analysisPeriod, header

def pol2cart(phi, theta):
    mult = math.cos(theta)
    x = math.sin(phi) * mult
    y = math.cos(phi) * mult
    z = math.sin(theta)
    return(x, y, z)

def createHeader(studyType, header):
    return header[:2] + [studyType] + header[3:]

def main(location, directNormal, diffuseHorizontal, analysisPeriod, header, srfAzimuth, srfAltitude, lb_preparation, lb_sunpath):
    #Pull the location data from the inputs.
    locName = _location.split('\n')[1].replace(',','')
    lat = None
    lngt = None
    timeZone = None
    elev = None
    try:
        locList = _location.split('\n')
        for line in locList:
            if "Latitude" in line: lat = float(line.split(',')[0])
            elif "Longitude" in line: lngt = float(line.split(',')[0])
            elif "Time Zone" in line: timeZone = float(line.split(',')[0])
            elif "Elevation" in line: elev = float(line.split(';')[0])
    except:
        warning = 'The connected _location is not a valid location from the "Ladybug_Import EWP" component or the "Ladybug_Construct Location" component.'
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    #Calculate the houlry altitude of the sun.
    lb_sunpath.initTheClass(float(lat), 0, rc.Geometry.Point3d.Origin, 100, float(lngt), float(timeZone))
    sunVectors = []
    stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod)
    stAnnualHour = lb_preparation.date2Hour(stMonth, stDay, stHour)
    endAnnualHour = lb_preparation.date2Hour(endMonth, endDay, endHour)
    HOYS = range(stAnnualHour,endAnnualHour+1)
    for hour in HOYS:
        d, m, t = lb_preparation.hour2Date(hour-1, True)
        lb_sunpath.solInitOutput(m+1, d, t+0.5)
        altitude = lb_sunpath.solAlt
        if altitude > 0:
            sunVec = lb_sunpath.sunReverseVectorCalc()
            sunVectors.append(sunVec)
        else: sunVectors.append(None)
    
    # Create a normal vector for a theoretical surface.
    if srfAzimuth == None:
        srfAzimuth = 180
    if srfAltitude == None:
        srfAltitude = 90
    coords = pol2cart(math.radians(srfAzimuth), math.radians(srfAltitude))
    normalVec = rc.Geometry.Vector3d(coords[0], coords[1], coords[2])
    
    # Create final lists and add headers.
    srfDirect, srfDiffuse, srfGlobal = [], [], []
    if header != []:
        dataType = 'Solar'
        if 'Illuminance' in header[2]:
            dataType = 'Illuminance'
        elif 'Radiation' in header[2]:
            dataType = 'Radiation'
        srfDirect = createHeader('Direct ' + dataType + ' for Surface - Az' + str(int(srfAzimuth)) + ', Alt' + str(int(srfAltitude)), header)
        srfDiffuse = createHeader('Diffuse ' + dataType + ' for Surface - Az' + str(int(srfAzimuth)) + ', Alt' + str(int(srfAltitude)), header)
        srfGlobal = createHeader('Total ' + dataType + ' for Surface - Az' + str(int(srfAzimuth)) + ', Alt' + str(int(srfAltitude)), header)
    
    # Calculate solar on the surface.
    for i, vec in enumerate(sunVectors):
        srfDir = 0
        if vec != None:
            angle = rc.Geometry.Vector3d.VectorAngle(vec, normalVec)
            if angle < math.pi/2:
                srfDir = directNormal[i]*math.cos(angle)
            srfDirect.append(srfDir)
        else:
            srfDirect.append(0)
        
        srfDif = diffuseHorizontal[i] * ((math.sin(math.radians(srfAltitude))/2) + 0.5)
        srfDiffuse.append(srfDif)
        srfGlobal.append(srfDir+srfDif)
    
    
    return srfDirect, srfDiffuse, srfGlobal, normalVec

#If Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_sunpath = sc.sticky["ladybug_SunPath"]()
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck == True:
    checkData = checkInputs()
    if checkData != -1:
       directNormal, diffuseHorizontal, analysisPeriod, header = checkData
       result = main(_location, directNormal, diffuseHorizontal, analysisPeriod, header, _srfAzimuth_, _srfAltitude_, lb_preparation, lb_sunpath)
       if result != -1:
           srfDirect, srfDiffuse, srfTotal, srfDirection = result