# RealTime Radiation Analysis
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component uses skyMatrix and intersection matrix to produce real time radiation result.
-
Provided by Ladybug 0.0.52
    
    Args:
        _selectedSkyMatrix: SelectedSkyMtx component result
        _intersectionMatrix: Intersection matrix [Output of the radiation study]
    Returns:
        radiationResult: The results of the study
"""

ghenv.Component.Name = "Ladybug_Real Time Radiation Analysis"
ghenv.Component.NickName = 'RTRadiationAnalysis'
ghenv.Component.Message = 'VER 0.0.52\nNOV_01_2013'

import scriptcontext as sc
import math

def main(intDict, selSkyMatrix):
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
    else:
        return
        
    indexList, listInfo = lb_preparation.separateList(selSkyMatrix, lb_preparation.strToBeFound)
    #separate total, diffuse and direct radiations
    separatedLists = []
    for i in range(len(indexList)-1):
        selList = []
        [selList.append(float(x)) for x in selSkyMatrix[indexList[i] + 7:indexList[i+1]]]
        separatedLists.append(selList)
    
    skyMatrix = separatedLists[0]
    
    radiationResult = []
    for ptCount in  intDict.keys():
        radValue = 0
        for patchCount in intDict[ptCount].keys():
            if intDict[ptCount][patchCount]['isIntersect']:
                radValue = radValue + (skyMatrix[patchCount] * math.cos(intDict[ptCount][patchCount]['vecAngle']))
        radiationResult.append(radValue)
    return radiationResult
if _selectedSkyMatrix and _intersectionMatrix:
    radiationResult = main(_intersectionMatrix.d, _selectedSkyMatrix)