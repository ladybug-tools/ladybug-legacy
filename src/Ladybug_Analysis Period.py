# This component provides a tuple that represents the running period
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Analysis period 
-
Provided by Ladybug 0.0.35
    
    Args:
        fromMonth: Default starting month is set to 1, if not provided [1-12]
        fromDay: Default starting day is set to 1, if not provided [1-31]
        fromHour: Default starting hour is set to 1, if not provided [1-24]
        toMonth: Default end month is set to 12, if not provided [1-12]
        toDay: Default end day is set to 31, if not provided [1-31]
        toHour: Default end hour is set to 24, if not provided [1-24]
    Returns:
        report: Simulation period
        analysisPeriod: Two tuples that represent the running period
                        (fromMonth, fromDay, fromHour) to (toMonth, toDay, toHour)
"""

ghenv.Component.Name = "Ladybug_Analysis Period"
ghenv.Component.NickName = 'analysisPeriod'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'

import scriptcontext as sc
import clr
clr.AddReference('Grasshopper')
import Grasshopper.Kernel as gh
we = gh.GH_RuntimeMessageLevel.Error
ww = gh.GH_RuntimeMessageLevel.Warning

if fromMonth==None: fromMonth = 1;
if fromDay==None: fromDay = 1;
if fromHour==None: fromHour = 1;
if toMonth==None: toMonth = 12;
if toDay==None: toDay = 31;
if toHour==None: toHour = 24;
if fromHour==0: fromHour = 1;
if toHour==0: toHour = 1


def main(fromMonth, fromDay, fromHour, toMonth, toDay, toHour):
    if not sc.sticky.has_key('ladybug_release'):
        warning0 = "You should first let the Ladybug fly..."
        print warning0
        ghenv.Component.AddRuntimeMessage(ww, warning0)
        return -1
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
    fromHour = lb_preparation.checkHour(fromHour)
    toHour = lb_preparation.checkHour(toHour)
    fromMonth = lb_preparation.checkMonth(fromMonth)
    toMonth = lb_preparation.checkMonth(toMonth)
    fromDay = lb_preparation.checkDay(fromDay, fromMonth)
    toDay = lb_preparation.checkDay(toDay, toMonth)
    
    
    if toHour == fromHour and toMonth == fromMonth and toDay == fromDay:
        error = 'start time and end time are identical!\n' + \
                'I have no idea what do you mean by this!'
        print error
        ghenv.Component.AddRuntimeMessage(we, error)
        return -1
    
    elif toHour == fromHour and toHour!=24:
        warning1 = 'Start and finish hour inputs are the same...' + \
                   'Ladybug added 1 hour to toHour not to crash!'
        print warning1
        ghenv.Component.AddRuntimeMessage(ww, warning1)
        toHour += 1
        toHour = lb_preparation.checkHour(toHour)
        #return -1
    
    elif toHour == fromHour and toHour==24:
        warning1 = 'I guess by setting both toHour and fromHour to 24 ' + \
                   'you mean fromHour = 1 toHour = 24...right?'
        print warning1
        ghenv.Component.AddRuntimeMessage(ww, warning1)
        fromHour = 1
    
    elif toHour < fromHour:
        warning2 = 'Well! I think I know what do you mean by ' + \
                   'having start hour bigger than end hour...' + \
                   'Ladybug is not ready for that yet so it swapped the values order!' +\
                   '...Sorry!'
        print warning2
        ghenv.Component.AddRuntimeMessage(ww, warning2)
        toHour, fromHour = fromHour, toHour
    
    #print int(fromMonth), int(fromDay), int(fromHour), int(toMonth),int(toDay), int(toHour)
        
    def makeTuple(fromMonth, fromDay, fromHour, toMonth, toDay, toHour):
        return ((fromMonth, fromDay, fromHour), ((toMonth, toDay, toHour)))
    
    analysisPeriod = makeTuple(int(fromMonth), int(fromDay), int(fromHour),
                            int(toMonth),int(toDay), int(toHour))
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_preparation.readRunPeriod(analysisPeriod)
    
    return analysisPeriod

result = main(fromMonth, fromDay, fromHour, toMonth, toDay, toHour)
if result!= -1: analysisPeriod = result
else: pass