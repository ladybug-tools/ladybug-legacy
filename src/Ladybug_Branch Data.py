#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Use this component to branch any data based on day, month and hour. Number of data items should match number of HOYs.
-
Provided by Ladybug 0.0.60
    
    Args:
        _data: A list of data to be branched for each month
        _HOY: A list of numbers between 1 and 8760 that represents an hour of the year.
            
    Returns:
        dataEachDay: Branched data for each day of the month. Branches are from 0 to 30.
        dataEachMonth: Branched data for each month of the year. Branches are from 0 to 11.
        dataEachHour: Branched data for each hour of the day. Branches are from 0 to 23.
"""

ghenv.Component.Name = "Ladybug_Branch Data"
ghenv.Component.NickName = 'branchDataDailyMonthlyHourly'
ghenv.Component.Message = 'VER 0.0.60\nJUL_06_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

def main(data, HOY):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
            
        if len(data) != len(HOY):
            warning = "Number of data should match number of hours."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
            
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        # prepare empty lists
        dataEachDay = DataTree[Object]()
        dataEachMonth = DataTree[Object]()
        dataEachHour = DataTree[Object]()
        for day in range(31): dataEachDay.AddRange([], GH_Path(day))
        for month in range(12): dataEachMonth.AddRange([], GH_Path(month))
        for hour in range(24): dataEachHour.AddRange([], GH_Path(hour))
        
        for dd, hoy in zip(data, HOY):
            d, m, t = lb_preparation.hour2Date(hoy, True)
            dataEachDay.Add(dd, GH_Path(d-1))
            dataEachMonth.Add(dd, GH_Path(m))
            dataEachHour.Add(dd, GH_Path(t-1))
                
        return dataEachDay, dataEachMonth, dataEachHour
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1

result = main(_data, _HOY)
if result!=-1: dataEachDay, dataEachMonth, dataEachHour = result
