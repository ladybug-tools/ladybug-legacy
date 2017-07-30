# RealTime Radiation Analysis
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
Use this component to scroll through the results of a Ladybug Radiation Analysis on an hour-by-hour, day-by-day, or month-by-month basis in real time!
The component uses a sky matrix (SkyMxt) from the selectSkyMxt component and the intersection matrix (intersectionMxt) from the Radiation Analysis component to calculate real time radiation results.
Once the correct inputs have been hooked up to this component, you should use the inputs of the connected selectSkyMxt component to scroll through results.
-
Provided by Ladybug 0.0.65
    
    Args:
        _selectedSkyMatrix: The output from a Ladybug selectedSkyMtx component.  This matrix basically carries all of the radiation values that define a sky and includes a radiation value for each sky patch on the sky dome.  You should use the selectSkyMxt component connected here to scroll through radiation results.
        _intersectionMatrix: The intersectionMxt output from a Ladybug Radiation Analysis component that has been run for test geometry.  This matrix is basically a python list that includes the relation between each test point in the Radiation Analysis and all the sky patchs on the sky dome.
    Returns:
        radiationResult: New radiation values for each test point in the original Radiation Analysis.  Values indicate radiation for the the connected sky matrix.  To visualize these new radiation values in the Rhino scene, connect these values to the Ladybug Re-Color Mesh component to re-color the mesh from the original Radiation Analysis with these new values.
"""

ghenv.Component.Name = "Ladybug_Real Time Radiation Analysis"
ghenv.Component.NickName = 'RTRadiationAnalysis'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import math

def main(intDict, selSkyMatrix):
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
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
