# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate the day of the year and hour of the year from an input date with a day of the month, month of the year and hour of the day.
-
Provided by Ladybug 0.0.58
    
    Args:
        _days_: A number (or list of numbers) between 1 and 31 that represents the day(s) of the month.
        _months_: A number (or list of numbers) between 1 and 12 that represents the month(s) of the year.
        _hours_: A number (or list of numbers) between 1 and 24 that represents the hour(s) of the day.
    
    Returns:
        DOY: The day of the year on which the input date falls.
        HOY: The hour of the year on which the input date and time fall.
        date: The input information written out as a full date and time text string.
"""

ghenv.Component.Name = "Ladybug_DOY_HOY"
ghenv.Component.NickName = 'DOY/HOY'
ghenv.Component.Message = 'VER 0.0.58\nJAN_21_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.58\nJAN_21_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


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
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        for m in months:
            for d in days:
                for h in hours:
                    hour = lb_preparation.checkHour(float(h))
                    month  = lb_preparation.checkMonth(int(m))
                    day = lb_preparation.checkDay(int(d), m, ghenv.Component)
                    HOY.append(lb_preparation.date2Hour(month, day, hour))
                    DOY.append(int(lb_preparation.getJD(month, day)))
                    date.append(lb_preparation.hour2Date(lb_preparation.date2Hour(month, day, hour)))
        return HOY, DOY, date
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1

result = main(_days_, _months_, _hours_)
if result!= -1: HOY, DOY, date = result
