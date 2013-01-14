# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Calculate day, month and hour for any day or hour of the year
-
Provided by Ladybug 0.0.35
    
    Args:
        HOY: Hour of the year
        DOY: Day of the year
            
    Returns:
        report: Report!!!

        day: Day of the month
        month: Month of the year
        hour: Hour of the day
        date: Date!
        
"""

ghenv.Component.Name = "Ladybug_Day_Month_Hour"
ghenv.Component.NickName = 'Day_Month_Hour_Calculator'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'

import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

def main():
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        day = []
        month = []
        hour = []
        date = []
        for hoy in HOY:
            d, m, t = lb_preparation.hour2Date(hoy, True)
            day.append(d)
            month.append(m + 1)
            hour.append(t)
            date.append(lb_preparation.hour2Date(hoy))
        
        return day, month, hour, date
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1

result = main()
if result!=-1: day, month, hour, date = result
