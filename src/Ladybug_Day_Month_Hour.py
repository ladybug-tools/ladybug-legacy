# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate date information from an hour of the year.  Date information includes the day of the month, the month of the year and the hour of the day.
-
Provided by Ladybug 0.0.57
    
    Args:
        HOY: A number between 1 and 8760 that represents an hour of the year.
            
    Returns:
        day: The day of the month on which the input HOY falls.
        month: The month of the year on which the input HOY falls.
        hour: The hour of the day on which the input HOY falls.
        date: The input information written out as a full date and time text string.
        
"""

ghenv.Component.Name = "Ladybug_Day_Month_Hour"
ghenv.Component.NickName = 'Day_Month_Hour_Calculator'
ghenv.Component.Message = 'VER 0.0.57\nMAR_26_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

def main(HOY):
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

result = main(_HOY)
if result!=-1: day, month, hour, date = result

