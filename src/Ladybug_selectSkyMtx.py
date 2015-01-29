# Select GenCumulativeSkyMtx
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to select a specific sky matrix (skyMxt) for an hour of the year or for an analysis period.

-
Provided by Ladybug 0.0.58
    
    Args:
        _cumulativeSkyMtx: The output from a GenCumulativeSkyMtx component.
        HOY_: An hour of the year for which you would like to select a sky.  This must be a value between 1 and 8760.
        _analysisPeriod_: An analysis period from Analysis Period component.  This will override an input HOY (hour of the year).
        removeDiffuse_: Set to "True" if you want to remove the diffuse component of the selected sky.
        removeDirect_: Set to "True" if you want to remove the direct component of the selected sky.
    Returns:
        readMe!: ...
        selectedSkyMtx: The selected sky matrix (SkyMtx) for the input hour of the year or an analysis period.
"""

ghenv.Component.Name = "Ladybug_selectSkyMtx"
ghenv.Component.NickName = 'selectSkyMtx'
ghenv.Component.Message = 'VER 0.0.58\nJAN_28_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.58\nJAN_21_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import System
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def getHourlySky(daylightMtxDict, HOY):
    # for presentation
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    stDate = lb_preparation.hour2Date(HOY, 1)
    analysisP = ((stDate[1]+1, stDate[0], stDate[2]-1),(stDate[1]+1, stDate[0], stDate[2]))
    
    hourlyMtx = []
    for patchNumber in daylightMtxDict.keys():
        convertedMtx = []
        for val in daylightMtxDict[patchNumber][HOY]: convertedMtx.append(val/1000)
        hourlyMtx.append(convertedMtx)
    return hourlyMtx, analysisP
    
def getCumulativeSky(daylightMtxDict, runningPeriod):
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    def selectHourlyData(dataList, analysisPeriod):
        # read analysis period
        stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, False)
        
        selHourlyData =[];
        
        # select data
        stAnnualHour = lb_preparation.date2Hour(stMonth, stDay, stHour)
        endAnnualHour = lb_preparation.date2Hour(endMonth, endDay, endHour)
        
        # check it goes from the end of the year to the start of the year
        if stAnnualHour < endAnnualHour:
            for i, item in enumerate(dataList[stAnnualHour-1:endAnnualHour+1]):
                if stHour-1 <= (i + stHour - 1)%24 <= endHour-1: selHourlyData.append(item)
            type = True
        else:
            for i, item in enumerate(dataList[stAnnualHour-1:]):
                if stHour-1 <= (i + stHour - 1)%24 <= endHour-1: selHourlyData.append(item)
            for i, item in enumerate(dataList[:endAnnualHour + 1]):
                if stHour-1 <= i %24 <= endHour-1: selHourlyData.append(item)
            type = False
        
        return selHourlyData
    
    HOYS = selectHourlyData(range(8760), runningPeriod)
    
    hourlyMtx = []
    for patchNumber in daylightMtxDict.keys():
        cumulativeDifValue = 0
        cumulativeDirValue = 0
        # adding upp the values
        try:
            for HOY in HOYS:
                difValue, dirValue = daylightMtxDict[patchNumber][HOY + 1]
                cumulativeDifValue += difValue
                cumulativeDirValue += dirValue 
        except Exception, e:
            print `e`
            
        hourlyMtx.append([cumulativeDifValue/1000, cumulativeDirValue/1000])
    
    return hourlyMtx

def prepareLBList(skyMtxLists, analysisPeriod, locName, unit, removeDiffuse, removeDirect):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    # prepare the final output
    stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, False)
    totalRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Total Radiation", unit, 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
    diffuseRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Diffuse Radiation", unit, 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
    directRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Direct Radiation", unit, 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
    
    for radValues in skyMtxLists:
        if not removeDiffuse and not removeDirect:
            totalRad.append(sum(radValues))
            diffuseRad.append(radValues[0])
            directRad.append(radValues[1])
        elif removeDiffuse and removeDirect:
            totalRad.append(0)
            diffuseRad.append(0)
            directRad.append(0)
        elif removeDirect:
            totalRad.append(radValues[0])
            diffuseRad.append(radValues[0])
            directRad.append(0)
        elif removeDiffuse:
            totalRad.append(radValues[1])
            diffuseRad.append(0)
            directRad.append(radValues[1])
    
    return totalRad + diffuseRad + directRad

def isLadybugFlying():
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return False
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return False
        return True
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return False
        

skyMtxLists = []
if _cumulativeSkyMtx and HOY_ and isLadybugFlying:
    skyMtxLists, _analysisPeriod_ = getHourlySky(_cumulativeSkyMtx.d, HOY_)
    unit = 'kWh/m2'
elif _cumulativeSkyMtx and isLadybugFlying:
    skyMtxLists = getCumulativeSky(_cumulativeSkyMtx.d, _analysisPeriod_)
    unit = 'kWh/m2'

selectedSkyMtx = []
if len(skyMtxLists)!=0:
    selectedSkyMtx = prepareLBList(skyMtxLists, _analysisPeriod_, _cumulativeSkyMtx.location, unit, removeDiffuse_, removeDirect_)
else:
    print "cumulativeSkyMtx failed to collect data."
