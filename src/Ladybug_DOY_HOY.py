# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Calculate day of the year and hour of the year based on day, month and hour
-
Provided by Ladybug 0.0.54
    
    Args:
        _day_: Days of the month [1-31]
        _month_: Months of the year [1-12]
        _hour_: Hours of the day [1-24]
    
    Returns:
        DOY: Days of the year
        HOY: Hours of the year
        date: Date 
"""

ghenv.Component.Name = "Ladybug_DOY_HOY"
ghenv.Component.NickName = 'DOY/HOY'
ghenv.Component.Message = 'VER 0.0.54\nFEB_16_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "4"

import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

def main(days, months, hours):
    DOY = []
    HOY = []
    date = []
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        for d in days:
            for m in months:
                for h in hours:
                    h = lb_preparation.checkHour(float(h))
                    m  = lb_preparation.checkMonth(int(m))
                    d = lb_preparation.checkDay(int(d), m)
                    HOY.append(lb_preparation.date2Hour(m, d, h))
                    DOY.append(int(lb_preparation.getJD(m, d)))
                    date.append(lb_preparation.hour2Date(lb_preparation.date2Hour(m, d, h)))
        return HOY, DOY, date
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1

result = main(_days_, _months_, _hours_)
if result!= -1: HOY, DOY, date = result
