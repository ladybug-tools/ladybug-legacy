# GenCumulativeSkyMtx
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component uses Radiance's gendaymtx function to calculate the sky's radiation for each hour of the year. This is a necessary pre-step before doing radiation analysis with Rhino geometry or generating a radiation rose.

The first time you use this component, you will need to be connected to the internet so that the component can download the "gendaymtx.exe" function to your system.

Gendaymtx is written by Ian Ashdown and Greg Ward. For more information, check the Radiance manual at:
http://www.radiance-online.org/learning/documentation/manual-pages/pdfs/gendaymtx.pdf

-
Provided by Ladybug 0.0.57
    
    Args:
        _epwFile: The output of the Ladybug Open EPW component or the file path location of the epw weather file on your system.
        _skyDensity_: Set to 0 to generate a Tregenza sky, which will divide up the sky dome with a coarse density of 145 sky patches.  Set to 1 to generate a Reinhart sky, which will divide up the sky dome using a very fine density of 580 sky patches.  Note that, while the Reinhart sky is more accurate, it will result in considerably longer calculation times.  Accordingly, the default is set to 0 for a Tregenza sky.
        workingDir_: An optional working directory in your system where the sky will be generated. Default is set to C:\Ladybug and any valid file path location can be connected.
        useOldRes_: Set this to "True" if you have already run this component previously and you want to use the already-generated data for this weather file.
        _runIt: Set to "True" to run the component and generate a sky matrix.
    Returns:
        readMe!: ...
        cumulativeSkyMtx: The result of the gendaymtx function. Use the selectSkyMtx component to select a desired sky matrix from this output for use in a radiation study, radition rose, or sky dome visualization.
"""

ghenv.Component.Name = "Ladybug_GenCumulativeSkyMtx"
ghenv.Component.NickName = 'genCumulativeSkyMtx'
ghenv.Component.Message = 'VER 0.0.57\nMAR_26_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import os
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from itertools import izip

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
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        # make working directory
        if workingDir: workingDir = lb_preparation.removeBlankLight(workingDir)
        workingDir = lb_preparation.makeWorkingDir(workingDir)
        
        # make sure the directory has been created
        if workingDir == -1: return -2
        workingDrive = workingDir[0:1]
        
        # GenCumulativeSky
        lb_preparation.downloadGendaymtx(workingDir)
        if not os.path.isfile(workingDir + '\gendaymtx.exe'): return -3
        
        ## check for epw file to be connected
        if epwFile != None and epwFile[-3:] == 'epw':
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
                command = "@echo off \necho.\n echo HELLO " + os.getenv("USERNAME").upper()+ "! " + \
                          "DO NOT CLOSE THIS WINDOW. \necho.\necho IT WILL BE CLOSED AUTOMATICALLY WHEN THE CALCULATION IS OVER!\n" + \
                          "echo.\necho AND MAY TAKE FEW MINUTES...\n" + \
                          "echo.\n" + \
                          "echo CALCULATING DIFFUSE COMPONENT OF THE SKY...\n" + \
                          workingDir + "\\gendaymtx -m " + str(n) + " -s -O1 " + weaFile + "> " + outputFileDif + "\n" + \
                          "echo.\necho CALCULATING DIRECT COMPONENT OF THE SKY...\n" + \
                          workingDir + "\\gendaymtx -m " + str(n) + " -d -O1 " + weaFile + "> " + outputFileDir
                      
                file = open(batchFile, 'w')
                file.write(command)
                file.close()
        
                os.system(batchFile)
            
            return outputFileDif, outputFileDir, newLocName
            
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
        
def readMTXFile(daylightMtxDif, daylightMtxDir, n, newLocName):
    # All the patches on top high get the same values so maybe
    # I should re-create the geometry 577 instead of 580
    
    skyPatchesDict = {1 : 145 + 1,
                      2 : 580 - 3 + 1}
    
    numOfPatchesInEachRow = {1: [30, 30, 24, 24, 18, 12, 6, 1],
                             2: [60, 60, 60, 60, 48, 48, 48, 48, 36, 36, 24, 24, 12, 12, 1]}
                             
    strConv = {1 : [0.0435449227, 0.0416418006, 0.0473984151, 0.0406730411, 0.0428934136, 0.0445221864, 0.0445221864, 0.0344199465],
               2: [0.0113221971, 0.0111894547, 0.0109255262, 0.0105335058, 0.0125224872, 0.0117312774, 0.0108025291, 0.00974713106, 0.011436609, 0.00974295956, 0.0119026242, 0.00905126163, 0.0121875626, 0.00612971396]} #steradians conversion
    
    numOfSkyPatches = skyPatchesDict[n]
    
    # create an empty dictionary
    radValuesDict = {}
    for skyPatch in range(numOfSkyPatches):
        radValuesDict[skyPatch] = {}
        
    resFileDif = open(daylightMtxDif, "r") 
    resFileDir = open(daylightMtxDir, "r") 
    
    def getValue(line):
        R, G, B = line.split(' ')
        value = (.265074126 * float(R) + .670114631 * float(G) + .064811243 * float(B)) * strConv[n][rowNumber]
        return value
        
    lineCount = 0
    warnOff = False
    failedHours = {}
    for difLine, dirLine in izip(resFileDif, resFileDir):
        # that line is an empty line to separate patches
        hour = (lineCount+1)% 8761
        if hour != 0:
            patchNumber = int((lineCount + 1) /8761)
            
            #
            for rowCount, patchCountInRow in enumerate(numOfPatchesInEachRow[n]):
                if patchNumber <= sum(numOfPatchesInEachRow[n][:rowCount]):
                    rowNumber = rowCount
                    break
            try:
                difValue = getValue(difLine)
                dirValue = getValue(dirLine)
            
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
                    print month + "/" + day + " @" + time
                
            try: radValuesDict[patchNumber][hour] = [difValue, dirValue]
            except: print patchNumber, hour, value
            
        lineCount += 1
    
    resFileDif.close()
    resFileDir.close()
    
    class SkyResultsCollection(object):
        def __init__(self, valuesDict, locationName):
            self.d = valuesDict
            self.location = locationName
        
    return SkyResultsCollection(radValuesDict, newLocName)
    
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
        daylightMtxDiffueFile, daylightMtxDirectFile, newLocName = result
        cumulativeSkyMtx = readMTXFile(daylightMtxDiffueFile, daylightMtxDirectFile, n, newLocName)
else:
    warn = "Set runIt to True and connect a valid epw file address"
    print warn
    #ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)

