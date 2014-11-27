# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to branch any data based on day, month and hour. Number of data items should match number of HOYs.
-
Provided by Ladybug 0.0.58
    
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
ghenv.Component.Message = 'VER 0.0.58\nOCT_27_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
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
