# GenCumulativeSky
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component uses GenCumulativeSky.exe to calculate the cumulative radiation for the Tregenza sky patches.
GenCumulativeSky is developed by Darren Robinson and Andrew Stone, and modified by Christoph Reinhart.
For more information, reference: "http://plea-arch.net/PLEA/ConferenceResources/PLEA2004/Proceedings/p1153final.pdf"

The first time you use this component, you need to be connected to the internet so the component can download GenCumulativeSky.exe
to the working directory.
-
Provided by Ladybug 0.0.35
    
    Args:
        epwWeatherFile: epw weather file address on your system
        analysisPeriod: Indicates the analysis period. An annual study will be run if this input is not provided by the user
        workingDir: Working directory on your system. Default is set to C:\Ladybug
        runIt: Set boolean to True to run the component
    Returns:
        report: Report!!!
        genCumSkyResult: Result of the study; to be used for radiation rose, Tregenza sky dome and radiation analysis.
"""

ghenv.Component.Name = "Ladybug_GenCumulativeSky"
ghenv.Component.NickName = 'genCumulativeSky'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'


import scriptcontext as sc
import os
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh


def main(workingDir):
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
        lb_preparation.downloadGenCumulativeSky(workingDir)
        if not os.path.isfile(workingDir + '\GenCumulativeSky.exe'): return -3
        
        # if workingDir\
        ## check for epw file to be connected
        if epwWeatherFile != None and epwWeatherFile[-3:] == 'epw':
            # import data from epw file
            locName, lat, lngt, timeZone, locationStr = lb_preparation.epwLocation(epwWeatherFile)
            newLocName = lb_preparation.removeBlank(locName)
            
            # make new folder for each city
            subWorkingDir = lb_preparation.makeWorkingDir(workingDir + "\\" + newLocName)
            print 'Current working directory is set to: ', subWorkingDir
            # copy .epw file to sub-directory
            lb_preparation.copyFile(epwWeatherFile, subWorkingDir + "\\" + newLocName + '.epw')
            
            # generate the batch file
            batchStr = lb_preparation.genCumSkyStr(analysisPeriod, subWorkingDir, workingDir, newLocName, lat, lngt, timeZone)
            
            # write and eyn the batch file
            batchFileName = subWorkingDir + '\\' + newLocName + '_cumulativeSky.bat'
            batchFile = open(batchFileName, "w")
            batchFile.write(batchStr)
            batchFile.close()
            os.system(batchFileName)
            
            # read the result
            totalRadiationCal = subWorkingDir + "\\" + newLocName + '_1.cal'
            diffuseRadiationCal = subWorkingDir + "\\" + newLocName + '_2.cal'
            totalRadiation = lb_preparation.readCalFile(totalRadiationCal)
            diffuseRadiation = lb_preparation.readCalFile(diffuseRadiationCal)
            
            # make sure the result files are imported
            if totalRadiation == -1 or diffuseRadiation == -1: return -1
            
            reportFileName = subWorkingDir + "\\" + newLocName + '_1_report.txt'
            lb_preparation.printReportFile(reportFileName)
            
            # prepare the final output
            stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, False)
            totalRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Total Radiation", 'kWh/m2', 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
            diffuseRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Diffuse Radiation", 'kWh/m2', 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
            directRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Direct Radiation", 'kWh/m2', 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
            
            for patchNum in range(len(totalRadiation)):
                totalRad.append(totalRadiation[patchNum])
                diffuseRad.append(diffuseRadiation[patchNum])
                directRad.append(totalRadiation[patchNum] - diffuseRadiation[patchNum])
            
            return totalRad + diffuseRad + directRad
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


if runIt:
    result = main(workingDir)
    w = gh.GH_RuntimeMessageLevel.Warning
    if result== -3:
        warning = 'Download failed!!! You need GenCumulativeSky.exe to use this component.' + \
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
        genCumSkyResult = result