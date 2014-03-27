# This component provides a tuple that represents the running period
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to set an analysis period, which can be used as input for a variety of other Ladybug and Honeybee components.  Default analysis period without any inputs is set to the entire year.
-
Provided by Ladybug 0.0.57
    
    Args:
        _fromMonth_: The number of the month for the start of the analysis.  Default starting month is set to 1 (January).
        _fromDay_: The day of the month for the start of the analysis. Default starting day is set to 1 (the first of the month).
        _fromHour_: The hour of the day for the start of the analysis. Default starting hour is set to 1 (the first hour of the day after midnight).
        _toMonth_: The number of the month for the end of the analysis. Default end month is set to 12 (December).
        _toDay_: The day of the month for the end of the analysis.  Default end day is set to 31 (the 31st of the month).
        _toHour_: The hour of the day for the end of the analysis. Default end hour is set to 24 (the last hour of the day before midnight)
    Returns:
        readMe!: A text confirmation of the analysis period.
        analysisPeriod: Two tuples that represent the running period
                        (fromMonth, fromDay, fromHour) to (toMonth, toDay, toHour)
"""

ghenv.Component.Name = "Ladybug_Analysis Period"
ghenv.Component.NickName = 'analysisPeriod'
ghenv.Component.Message = 'VER 0.0.57\nMAR_26_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import clr
clr.AddReference('Grasshopper')
import Grasshopper.Kernel as gh
we = gh.GH_RuntimeMessageLevel.Error
ww = gh.GH_RuntimeMessageLevel.Warning

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

if _fromMonth_==None: _fromMonth_ = 1;
if _fromDay_==None: _fromDay_ = 1;
if _fromHour_==None: _fromHour_ = 1;
if _toMonth_==None: _toMonth_ = 12;
if _toDay_==None: _toDay_ = 31;
if _fromHour_==None: _fromHour_ = 1;
if _toHour_==None: _toHour_ = 24;

result = main(_fromMonth_, _fromDay_, _fromHour_, _toMonth_, _toDay_, _toHour_)
if result!= -1: analysisPeriod = result
else: pass
