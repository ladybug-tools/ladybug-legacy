# RealTime Radiation Analysis
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to scroll through the results of a Ladybug Radiation Analysis on an hour-by-hour, day-by-day, or month-by-month basis in real time!
The component uses a sky matrix (SkyMxt) from the selectSkyMxt component and the intersection matrix (intersectionMxt) from the Radiation Analysis component to calculate real time radiation results.
Once the correct inputs have been hooked up to this component, you should use the inputs of the connected selectSkyMxt component to scroll through results.
-
Provided by Ladybug 0.0.58
    
    Args:
        _selectedSkyMatrix: The output from a Ladybug selectedSkyMtx component.  This matrix basically carries all of the radiation values that define a sky and includes a radiation value for each sky patch on the sky dome.  You should use the selectSkyMxt component connected here to scroll through radiation results.
        _intersectionMatrix: The intersectionMxt output from a Ladybug Radiation Analysis component that has been run for test geometry.  This matrix is basically a python list that includes the relation between each test point in the Radiation Analysis and all the sky patchs on the sky dome.
    Returns:
        radiationResult: New radiation values in Wh/m2 for each test point in the original Radiation Analysis.  Values indicate radiation for the the connected sky matrix.  To visualize these new radiation values in the Rhino scene, connect these values to the Ladybug Re-Color Mesh component to re-color the mesh from the original Radiation Analysis with these new values.
"""

ghenv.Component.Name = "Ladybug_Real Time Radiation Analysis"
ghenv.Component.NickName = 'RTRadiationAnalysis'
ghenv.Component.Message = 'VER 0.0.58\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import math

def main(intDict, selSkyMatrix):
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return
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
