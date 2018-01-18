# ASHRAE Design Day Sky Model
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
Use this component to generate a clear sky for a cooling design day, which can then be used to size a HVAC system.  This component outputs both the hourly solar radiation values as well as a cumulative sky that can be used in solar radiation studies (if requested).
_
Specifically, this component uses the ASHRAE Revised Clear Sky Model (Tau Model), which was originally published in the ASHRAE 2009 Handbook of Fundementals (American Society of Heating, Refrigerating and Air-Conditioning Engineers. (2009). 2009 ASHRAE handbook: Fundamentals. Atlanta, GA: American Society of Heating, Refrigeration and Air-Conditioning Engineers).
The "Tau Model" is currently the recommended sky model for cooling design day calculations and is the default assumption of Honeybee EnergyPlus HVAC sizing calculations.
_
More information on the calculation for the can be found in the EnergyPlus Input/Output reference:
http://bigladdersoftware.com/epx/docs/8-4/engineering-reference/climate-calculations.html#ashrae-revised-clear-sky-model-tau-model
-
Provided by Ladybug 0.0.65
    
    Args:
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        _tauBeam: Values representing the optical sky depth for beam (direct) solar radiation.  Optical depth is the natural logarithm of the ratio of incident to transmitted radiant power through the atmosphere.  It can vary from month to month as water vapor concentrations in the atmosphere change.  This input can be either a single value for the whole year, a list of 12 monthly values, or the output from the "Ladybug_Import stat" component.  Typical values range from 0.3 in cool dry months to 0.65 in warm humid months.
        _tauDiffuse: Values representing the optical sky depth for diffuse solar radiation.  Optical depth is the natural logarithm of the ratio of incident to transmitted radiant power through the atmosphere.  It can vary from month to month as water vapor concentrations in the atmosphere change. This input can be either a single value for the whole year, a list of 12 monthly values, or the output from the "Ladybug_Import stat" component. Typical values range from 1.75 in warm humid months to 2.5 in cool dry months.
        _skyDensity_: Set to 0 to generate a Tregenza sky, which will divide up the sky dome with a coarse density of 145 sky patches.  Set to 1 to generate a Reinhart sky, which will divide up the sky dome using a very fine density of 580 sky patches.  Note that, while the Reinhart sky is more accurate, it will result in considerably longer calculation times.  Accordingly, the default is set to 0 for a Tregenza sky.
        workingDir_: An optional working directory in your system where the sky will be generated. Default is set to C:\Ladybug or C:\Users\yourUserName\AppData\Roaming\Ladybug.  The latter is used if you cannot write to the C:\ drive of your computer.  Any valid file path location can be connected.
        useOldRes_: Set this to "True" if you have already run this component previously and you want to use the already-generated data for this weather file.
        genCumSky_: Set to 'True' to have this component generate a cumulative sky matrix for the design day sky.  This can then be used in Ladybug solar radiation studies and visualized with the "Ladybug_Sky Dome" or "Ladybug_Radiation Rose."
    Returns:
        readMe!: ...
        directNormRad: The hourly Direct Normal Radiation in Wh/m2 for an ASHRAE Revised Clear Sky (Tau Model). Direct normal radiation is the amount of solar radiation in Wh/m2 received directly from the solar disk on a surface perpendicular to the sun's rays.
        diffuseHorizRad: The hourly Diffuse Horizontal Radiation in Wh/m2 for an ASHRAE Revised Clear Sky (Tau Model). Diffuse horizontal radiation is the amount of solar radiation in Wh/m2 received from the sky (excluding the solar disk) on a horizontal surface.
        globalHorizRad; The hourly Global Horizontal Radiation in Wh/m2 for an ASHRAE Revised Clear Sky (Tau Model). Diffuse horizontal radiation is the total amount of direct and diffuse solar radiation in Wh/m2 received on a horizontal surface.
        cumulativeSkyMtx: The result of the gendaymtx function. Use the selectSkyMtx component to select a desired sky matrix from this output for use in a radiation study, radition rose, or sky dome visualization.
"""

ghenv.Component.Name = "Ladybug_Design Day Sky Model"
ghenv.Component.NickName = 'DesignDaySky'
ghenv.Component.Message = 'VER 0.0.65\nSEP_03_2017'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
import Rhino as rc
import math
import os
from itertools import izip

w = gh.GH_RuntimeMessageLevel.Warning



def weaHeader(locName, lat, long, timeZone, elev):
    return  "place " + locName + "\n" + \
            "latitude " + str(lat) + "\n" + \
            "longitude " + `-float(long)` + "\n" + \
            "time_zone " + `-float(timeZone) * 15` + "\n" + \
            "site_elevation " + str(elev) + "\n" + \
            "weather_data_file_units 1\n"

def generateWea(workingDir, header, diffuseRad, directRad, lb_preparation):
    outputFile = workingDir + "\Design_Day_ASHRAE_Clear_Sky" + ".wea"
    weaFile = open(outputFile, 'w')
    weaFile.write(header)
    for hour in range(1,8761):
        day, month, time = lb_preparation.hour2Date(hour, True)
        weaFile.write(str(month+1) + " " + str(day) + " " + str(time) + " " + str(directRad[hour-1]) + " " + str(diffuseRad[hour-1]) + "\n")
    weaFile.close()
    return outputFile

def readMTXFile(daylightMtxDif, daylightMtxDir, n, newLocName, lat, lngt, timeZone):
    # All the patches on top high get the same values so maybe
    # I should re-create the geometry 577 instead of 580
    # and keep in mind that first patch is ground!
    # I create the dictionary only for sky patches and don't collect the data
    # for the first patch
    # this line could have saved me 5 hours
    skyPatchesDict = {1 : 145,
                      2 : 580 - 3}

    numOfPatchesInEachRow = {1: [30, 30, 24, 24, 18, 12, 6, 1],
                             2: [60, 60, 60, 60, 48, 48, 48, 48, 36, 36, 24, 24, 12, 12, 1]}
                             
    # first row is horizon and last row is the one 
    strConv = {1 : [0.0435449227, 0.0416418006, 0.0473984151, 0.0406730411, 0.0428934136, 0.0445221864, 0.0455168385, 0.0344199465],
               2: [0.0113221971, 0.0111894547, 0.0109255262, 0.0105335058, 0.0125224872, 0.0117312774, 0.0108025291, 0.00974713106, 0.011436609, 0.00974295956, 0.0119026242, 0.00905126163, 0.0121875626, 0.00612971396, 0.00921483254]}
    
    numOfSkyPatches = skyPatchesDict[n]
    
    # create an empty dictionary
    radValuesDict = {}
    for skyPatch in range(numOfSkyPatches):
        radValuesDict[skyPatch] = {}
        
    resFileDif = open(daylightMtxDif, "r") 
    resFileDir = open(daylightMtxDir, "r") 
    
    def getValue(line, rowNumber):
        R, G, B = line.split(' ')
        value = (.265074126 * float(R) + .670114631 * float(G) + .064811243 * float(B)) * strConv[n][rowNumber]
        return value
        
    lineCount = 0
    extraHeadingLines = 0 # no heading
    warnOff = False
    failedHours = {}
    for difLine, dirLine in izip(resFileDif, resFileDir):
        # each line is the data for each hour for a single patch
        
        # new version of gendaymtx genrates a header
        # this is a check to make sure the component will work for both versions
        if lineCount == 0 and difLine.startswith("#?RADIANCE"):
            # the file has a header
            extraHeadingLines = -8
            
        if lineCount + extraHeadingLines < 0:
            # pass heading line
            lineCount += 1
            continue
        
        # these lines is an empty line to separate patches do let's pass them
        hour = (lineCount + 1 + extraHeadingLines)% 8761
        
        #print lineCount, hour
        
        if hour != 0:
            patchNumber = int((lineCount + 1 + extraHeadingLines) /8761)
            
            # first patch is ground!
            if patchNumber != 0: #and patchNumber < numOfSkyPatches:
                for rowCount, patchCountInRow in enumerate(numOfPatchesInEachRow[n]):
                    if patchNumber - 1 < sum(numOfPatchesInEachRow[n][:rowCount+1]):
                        rowNumber = rowCount
                        # print rowNumber
                        break
                try:
                    difValue = getValue(difLine, rowNumber)
                    dirValue = getValue(dirLine, rowNumber)
                except Exception, e:
                    value = 0
                    if not warnOff:
                        print "genDayMtx returns null Values for few hours. The study will run anyways." + \
                              "\nMake sure that you are using an standard epw file." + \
                              "\nThe failed hours are listed below in [Month/Day @Hour] format."
                    warnOff = True
                    day, month, time = hour2Date(hour - 1)
                    if hour-1 not in failedHours.keys():
                        failedHours[hour-1] = [day, month, time]
                        print "Failed to read the results > " + month + "/" + day + " @" + time
                    
                try: radValuesDict[patchNumber-1][hour] = [difValue, dirValue]
                except:print patchNumber-1, hour, value
            
        lineCount += 1
    
    resFileDif.close()
    resFileDir.close()
    
    class SkyResultsCollection(object):
        def __init__(self, valuesDict, locationName, lat, lngt, timeZone):
            self.d = valuesDict
            self.location = locationName
            self.lat = lat
            self.lngt = lngt
            self.timeZone = timeZone
        
        def ToString(self):
            return 'AnnualDaylightMatrix::%s' % self.location
    
    return SkyResultsCollection(radValuesDict, newLocName, lat, lngt, timeZone)

def main(location, monthlyTauBeam, monthlyTauDiffuse, skyDensity, workingDir, useOldRes, genCumSky):
    # Call the necessary libraries.
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_sunpath = sc.sticky["ladybug_SunPath"]()
    
    # Clean the tauBeam and tauDiffuse inputs.
    header = []
    if len(monthlyTauBeam) == 1:
        monthlyTauBeam = [float(monthlyTauBeam[0]) for i in range(12)]
    elif len(monthlyTauBeam) == 12:
        monthlyTauBeam = [float(i) for i in monthlyTauBeam]
    elif len(monthlyTauBeam) == 19 and monthlyTauBeam[2] == 'Clear Sky Optical Depth for Beam Irradiance':
        header = monthlyTauBeam[:7]
        monthlyTauBeam = monthlyTauBeam[7:]
        monthlyTauBeam = [float(i) for i in monthlyTauBeam]
    else:
        warning = 'The connected _tauBeam must be either a single value, 12 values for different months, or the direct output from the "Ladybug_Import stat" component.'
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    if len(monthlyTauDiffuse) == 1:
        monthlyTauDiffuse = [float(monthlyTauDiffuse[0]) for i in range(12)]
    elif len(monthlyTauDiffuse) == 12:
        monthlyTauDiffuse = [float(i) for i in monthlyTauDiffuse]
    elif len(monthlyTauDiffuse) == 19 and monthlyTauDiffuse[2] == 'Clear Sky Optical Depth for Diffuse Irradiance':
        header = monthlyTauDiffuse[:7]
        monthlyTauDiffuse = monthlyTauDiffuse[7:]
        monthlyTauDiffuse = [float(i) for i in monthlyTauDiffuse]
    else:
        warning = 'The connected _tauDiffuse must be either a single value, 12 values for different months, or the direct output from the "Ladybug_Import stat" component.'
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
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
    lb_sunpath.initTheClass(float(lat), None, rc.Geometry.Point3d.Origin, 100, float(lngt), float(timeZone))
    altitudes = []
    months = []
    HOYS = range(1,8761)
    for hour in HOYS:
        d, m, t = lb_preparation.hour2Date(hour, True)
        months.append(m)
        lb_sunpath.solInitOutput(m+1, d, t)
        altitude = math.degrees(lb_sunpath.solAlt)
        altitudes.append(altitude)
    
    # Calculate the hourly air mass between the sun at the top of the atmosphere and the surface of the earth.
    airMasses = []
    for alt in altitudes:
        airMass = 0
        if alt > 0:
            airMass = 1/(math.sin(math.radians(alt)) + (0.50572 * math.pow((6.07995 + alt), -1.6364)))
        airMasses.append(airMass)
    
    # Calculate monthly air mass exponents.
    beamEpxs = []
    diffuseExps = []
    for count, tb in enumerate(monthlyTauBeam):
        td = monthlyTauDiffuse[count]
        ab = 1.219 - (0.043*tb) - (0.151*td) - (0.204*tb*td)
        ad = 0.202 + (0.852*tb) - (0.007*td) - (0.357*tb*td)
        beamEpxs.append(ab)
        diffuseExps.append(ad)
    
    # Calculate hourly diffuse and direct solar radiation
    directNormRad, diffuseHorizRad, globalHorizRad = header[:], header[:], header[:]
    directNormRad[2:5] = ['Direct Normal Radiation', 'Wh/m2', 'Hourly']
    diffuseHorizRad[2:5] = ['Diffuse Horizontal Radiation', 'Wh/m2', 'Hourly']
    globalHorizRad[2:5] = ['Global Horizontal Radiation', 'Wh/m2', 'Hourly']
    for i, airMass in enumerate(airMasses):
        alt = altitudes[i]
        if alt > 0:
            m = months[i]
            eBeam = 1415 * math.exp(-monthlyTauBeam[m] * math.pow(airMass, beamEpxs[m]))
            eDiff = 1415 * math.exp(-monthlyTauDiffuse[m] * math.pow(airMass, diffuseExps[m]))
            eGlob = eDiff + eBeam*math.cos(math.radians(90-alt))
            directNormRad.append(eBeam)
            diffuseHorizRad.append(eDiff)
            globalHorizRad.append(eGlob)
        else:
            directNormRad.append(0)
            diffuseHorizRad.append(0)
            globalHorizRad.append(0)
    
    if genCumSky == True:
        # Check the sky density.
        if skyDensity == None: n = 1 #Tregenza Sky
        else: n = skyDensity%2 + 1 # Custom Sky
        
        # make working directory.
        if workingDir:
            workingDir = lb_preparation.removeBlankLight(workingDir)
        workingDir = lb_preparation.makeWorkingDir(None)
        # make sure the directory has been created.
        if workingDir == -1:
            warning = 'Failed to create working directory for genCumSky.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        workingDrive = workingDir[0:1]
        # GenCumulativeSky
        gendaymtxFile = os.path.join(workingDir, 'gendaymtx.exe')
        if not os.path.isfile(gendaymtxFile):
            # let's see if we can grab it from radiance folder
            if os.path.isfile("c:/radiance/bin/gendaymtx.exe"):
                # just copy this file
                shutil.copyfile("c:/radiance/bin/gendaymtx.exe", gendaymtxFile)
                # in newer versions of radiance you also need msvcr120.dll
                if os.path.isfile("c:/radiance/bin/msvcr120.dll"):
                    shutil.copyfile("c:/radiance/bin/msvcr120.dll",
                                    os.path.join(workingDir, 'msvcr120.dll'))
            else:
                # download the file
                lb_preparation.downloadGendaymtx(workingDir)
            #check if the file is there
        if not os.path.isfile(gendaymtxFile) or os.path.getsize(gendaymtxFile)< 15000:
            warning = 'Download failed!!! You need GenDayMtx.exe to use this component.' + \
                '\nPlease check your internet connection, and try again!'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        if not os.access(gendaymtxFile, os.X_OK):
            raise Exception("%s is blocked by system! Right click on the file,"%gendaymtxFile + \
                " select properties and unblock it.")
        
        newLocName = lb_preparation.removeBlank(locName)
        # make new folder for each city
        subWorkingDir = lb_preparation.makeWorkingDir(workingDir + "\\" + newLocName)
        print 'Current working directory is set to: ', subWorkingDir
        
        # Generate a .wea file with the appropriate information.
        header = weaHeader(locName, lat, lngt, timeZone, elev)
        weaFile = generateWea(subWorkingDir, header, diffuseHorizRad[7:], directNormRad[7:], lb_preparation)
        
        outputFile = weaFile.replace(".wea", ".mtx")
        outputFileDif = weaFile.replace(".wea", "_dif_" + `n` + ".mtx")
        outputFileDir = weaFile.replace(".wea", "_dir_" + `n` + ".mtx")
        
        # check if the study is already ran for this weather file
        if useOldRes and os.path.isfile(outputFileDif) and os.path.isfile(outputFileDir):
            # ask the user if he wants to re-run the study
            print "Sky matrix files for this epw file are already existed on your system.\n" + \
                  "The component won't recalculate the sky and imports the available result.\n" + \
                  "In case you don't want to use these files, set useOldRes input to False and re-run the study.\n" + \
                  "If you found the lines above confusing just ignore it! It's all fine. =)\n"
        else:
            batchFile = weaFile.replace(".wea", ".bat")
            try:
                username = ' %s' % os.getenv("USERNAME")
            except:
                username = ''
            
            command = '@echo off \necho.\n echo HELLO{0}!\n' \
                      'echo DO NOT CLOSE THIS WINDOW. \necho.\necho IT WILL BE CLOSED AUTOMATICALLY WHEN THE CALCULATION IS OVER!\n' \
                      'echo.\necho AND MAY TAKE FEW MINUTES...\n' \
                      'echo.\n' \
                      'echo CALCULATING DIFFUSE COMPONENT OF THE SKY...\n' \
                      '"{1}\\gendaymtx" -m {2} -s -O1 "{3}"> "{4}"\n' \
                      'echo.\necho CALCULATING DIRECT COMPONENT OF THE SKY...\n' \
                      '"{1}\\gendaymtx" -m {2} -d -O1 "{3}"> "{5}"\n'
                     
            command = command.format(username, workingDir, n, weaFile,
                                     outputFileDif, outputFileDir)
            file = open(batchFile, 'w')
            file.write(command.encode('utf-8'))
            file.close()
            
            os.system('"%s"' % batchFile)
        
        # Read in the result matrix.
        cumulativeSkyMtx = readMTXFile(outputFileDif, outputFileDir, n, newLocName, lat, lngt, timeZone)
    else:
        cumulativeSkyMtx = None
    
    return directNormRad, diffuseHorizRad, globalHorizRad, cumulativeSkyMtx


#If Honeybee or Ladybug is not flying or is an older version, give a warning.
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
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck == True:
    result = main(_location, _tauBeam, _tauDiffuse, _skyDensity_, workingDir_, useOldRes_, genCumSky_)
    if result != -1:
        directNormRad, diffuseHorizRad, globalHorizRad, cumulativeSkyMtx = result

