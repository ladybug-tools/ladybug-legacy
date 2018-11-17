# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component calculate Mean Radiant Temperature (MRT) given a set of temperatures and corresponding view factors.  This component will check to be sure view factors add to 1 and will use the following formula:
MRT = (V1*T1^4 + V2*T2^4 + ...) ^ (1/4)
Where V corresponds to a view factor and T corresponds to a temperature.
-
Provided by Ladybug 0.0.67
    Args:
        _temperatures: A list of radiant temperatures in Celcius that correspond to view factors below.
        _viewFactors: A list of viewFactors that correspond to the temperatures above.  These should sum to 1.
    Returns:
        MRT: The Mean Radiant Temperature that results from the input temperatures and view factors.
"""

ghenv.Component.Name = "Ladybug_MRT Calculator"
ghenv.Component.NickName = 'MRT'
ghenv.Component.Message = 'VER 0.0.67\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import math
import Grasshopper.Kernel as gh
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

def getMRT(temperatures, viewFactors):
    equRight = 0
    for i, temp in enumerate(temperatures):
        tempK = temp + 273.15
        equRight = equRight + math.pow(tempK, 4)*viewFactors[i]
    MRT = math.pow(equRight, 0.25)
    MRTC = MRT - 273.15
    return MRTC

def main(temperatures, viewFactors):
    if sum(viewFactors) < 0.99:
        warning = "The sum of the view factors is less than 1."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    elif sum(viewFactors) > 1.01:
        warning = "The sum of the view factors is greater than 1."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    #Create a Python list from the temperature data tree.
    dataPyList = []
    for i in range(temperatures.BranchCount):
        branchList = temperatures.Branch(i)
        dataVal = []
        for item in branchList:
            try: dataVal.append(float(item))
            except: dataVal.append(item)
        dataPyList.append(dataVal)
    
    MRTs = DataTree[Object]()
    for count, templist in enumerate(dataPyList):
        mrt = getMRT(templist, viewFactors)
        p = GH_Path(count)
        MRTs.Add(mrt, p)
    
    return MRTs

if _temperatures.BranchCount >0 and _viewFactors != [] and _viewFactors != [None]:
    result = main(_temperatures, _viewFactors)
    if result != -1:
        MRT = result