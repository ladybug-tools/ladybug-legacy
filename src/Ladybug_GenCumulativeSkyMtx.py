# GenCumulativeSkyMtx
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
This component uses Radiance's gendaymtx function to calculate the sky's radiation for each hour of the year. This is a necessary pre-step before doing radiation analysis with Rhino geometry or generating a radiation rose.

The first time you use this component, you will need to be connected to the internet so that the component can download the "gendaymtx.exe" function to your system.

Gendaymtx is written by Ian Ashdown and Greg Ward. For more information, check the Radiance manual at:
http://www.radiance-online.org/learning/documentation/manual-pages/pdfs/gendaymtx.pdf

-
Provided by Ladybug 0.0.65
    
    Args:
        _epwFile: The output of the Ladybug Open EPW component or the file path location of the epw weather file on your system.
        _skyDensity_: Set to 0 to generate a Tregenza sky, which will divide up the sky dome with a coarse density of 145 sky patches.  Set to 1 to generate a Reinhart sky, which will divide up the sky dome using a very fine density of 580 sky patches.  Note that, while the Reinhart sky is more accurate, it will result in considerably longer calculation times.  Accordingly, the default is set to 0 for a Tregenza sky.
        workingDir_: An optional working directory in your system where the sky will be generated. Default is set to C:\Ladybug or C:\Users\yourUserName\AppData\Roaming\Ladybug.  The latter is used if you cannot write to the C:\ drive of your computer.  Any valid file path location can be connected.
        useOldRes_: Set this to "True" if you have already run this component previously and you want to use the already-generated data for this weather file.
        _runIt: Set to "True" to run the component and generate a sky matrix.
    Returns:
        readMe!: ...
        cumulativeSkyMtx: The result of the gendaymtx function. Use the selectSkyMtx component to select a desired sky matrix from this output for use in a radiation study, radition rose, or sky dome visualization.
"""

ghenv.Component.Name = "Ladybug_GenCumulativeSkyMtx"
ghenv.Component.NickName = 'genCumulativeSkyMtx'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import os
import scriptcontext as sc
import Grasshopper.Kernel as gh
from itertools import izip
import shutil

def date2Hour(month, day, hour):
    # fix the end day
    numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    # dd = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    JD = numOfDays[int(month)-1] + int(day)
    return (JD - 1) * 24 + hour

def hour2Date(hour):
    
    monthList = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
    numOfHours = [24 * numOfDay for numOfDay in numOfDays]

    for h in range(len(numOfHours)-1):
        if hour <= numOfHours[h+1]: month = h + 1; break

    if hour == 0: day = 1
    elif (hour)%24 == 0: day = int((hour - numOfHours[h]) / 24)
    else: day = int((hour - numOfHours[h]) / 24) + 1
    
    time = hour%24 + 0.5
    
    return str(day), str(month), str(time)

def getRadiationValues(epw_file, analysisPeriod, weaFile):
    # start hour and end hour
    stHour = 0
    endHour = 8760
    epwfile = open(epw_file,"r")
    for lineCount, line in enumerate(epwfile):
        hour = lineCount - 8
        if  int(stHour) <= hour <= int(endHour):
            dirRad = (line.split(',')[14])
            difRad = (line.split(',')[15])
            day, month, time = hour2Date(hour)
            weaFile.write(month + " " + day + " " + time + " " + dirRad + " " + difRad + "\n")
    epwfile.close()
    return weaFile

def weaHeader(epwFileAddress, lb_preparation):
    
    locName, lat, long, timeZone, elev, dataStr = lb_preparation.epwLocation(epwFileAddress)
    
    #print locName, lat, long, timeZone, elev
    
    return  "place " + locName + "\n" + \
            "latitude " + lat + "\n" + \
            "longitude " + `-float(long)` + "\n" + \
            "time_zone " + `-float(timeZone) * 15` + "\n" + \
            "site_elevation " + elev + "\n" + \
            "weather_data_file_units 1\n"

def epw2wea(weatherFile, analysisPeriod, lb_preparation):
    outputFile = weatherFile.replace(".epw", ".wea")
    header = weaHeader(weatherFile, lb_preparation)
    weaFile = open(outputFile, 'w')
    weaFile.write(header)
    weaFile = getRadiationValues(weatherFile, analysisPeriod, weaFile)
    weaFile.close()
    return outputFile

def main(epwFile, skyType, workingDir, useOldRes):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        # make working directory
        if workingDir: workingDir = lb_preparation.removeBlankLight(workingDir)
        workingDir = lb_preparation.makeWorkingDir(workingDir)
        
        # make sure the directory has been created
        if workingDir == -1: return -2
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
        if not os.path.isfile(gendaymtxFile) or  os.path.getsize(gendaymtxFile)< 15000 : return -3
        
        if not os.access(gendaymtxFile, os.X_OK):
            raise Exception("%s is blocked by system! Right click on the file,"%gendaymtxFile + \
                " select properties and unblock it.")
                
        ## check for epw file to be connected
        if epwFile != None and epwFile[-3:] == 'epw':
            if not os.path.isfile(epwFile):
                print "Can't find epw file at " + epwFile
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Can't find epw file at " + epwFile)
                return -1
                
            # import data from epw file
            locName, lat, lngt, timeZone, elev, locationStr = lb_preparation.epwLocation(epwFile)
            newLocName = lb_preparation.removeBlank(locName)
            
            # make new folder for each city
            subWorkingDir = lb_preparation.makeWorkingDir(workingDir + "\\" + newLocName)
            print 'Current working directory is set to: ', subWorkingDir
            # copy .epw file to sub-directory
            weatherFileAddress = lb_preparation.copyFile(epwFile, subWorkingDir + "\\" + newLocName + '.epw')
            
            # create weaFile
            weaFile = epw2wea(weatherFileAddress, [], lb_preparation)
        
            outputFile = weaFile.replace(".wea", ".mtx")
            outputFileDif = weaFile.replace(".wea", "_dif_" + `skyType` + ".mtx")
            outputFileDir = weaFile.replace(".wea", "_dir_" + `skyType` + ".mtx")
            
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
            
            return outputFileDif, outputFileDir, newLocName, lat, lngt, timeZone
            
        else:
            print "epwWeatherFile address is not a valid .epw file"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "epwWeatherFile address is not a valid .epw file")
            return -1
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1
        
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
    
if _runIt and _epwFile!=None:
    
    if _skyDensity_ == None: n = 1 #Tregenza Sky
    else: n = _skyDensity_%2 + 1 #
    
    result = main(_epwFile, n, workingDir_, useOldRes_)
    w = gh.GH_RuntimeMessageLevel.Warning
    if result== -3:
        warning = 'Download failed!!! You need GenDayMtx.exe to use this component.' + \
                '\nPlease check your internet connection, and try again!'
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    elif result == -2:
        warning = 'Working directory cannot be created! Please set workingDir to a new path'
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    elif result == -1:
        pass
    else:
        daylightMtxDiffueFile, daylightMtxDirectFile, newLocName, lat, lngt, timeZone = result
        cumulativeSkyMtx = readMTXFile(daylightMtxDiffueFile, daylightMtxDirectFile, n, newLocName, lat, lngt, timeZone)
else:
    warn = "Set runIt to True and connect a valid epw file address"
    print warn
    #ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)

