# This component provides a tuple that represents the running period
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
Use this component to set an analysis period, which can be used as input for a variety of other Ladybug and Honeybee components.  Default analysis period without any inputs is set to the entire year.
-
Provided by Ladybug 0.0.65
    
    Args:
        _fromMonth_: A number between 1 and 12 that represents the month of the year for the start of the analysis.  Default starting month is set to 1 (January).
        _fromDay_: A number between 1 and 31 that represents the day of the month for the start of the analysis. Default starting day is set to 1 (the first of the month).
        _fromHour_: A number between 1 and 24 that represents the hour of the day for the start of the analysis. Default starting hour is set to 1 (the first hour of the day after midnight).
        _toMonth_: A number between 1 and 12 that represents the month of the year for the end of the analysis. Default end month is set to 12 (December).
        _toDay_: A number between 1 and 31 that represents the day of the month for the end of the analysis.  Default end day is set to 31 (the 31st of the month).
        _toHour_: A number between 1 and 24 that represents the hour of the day for the end of the analysis. Default end hour is set to 24 (the last hour of the day before midnight)
    Returns:
        readMe!: A text confirmation of the analysis period.
        analysisPeriod: Two tuples that represent the running period
                        (fromMonth, fromDay, fromHour) to (toMonth, toDay, toHour)
"""

ghenv.Component.Name = "Ladybug_Analysis Period"
ghenv.Component.NickName = 'analysisPeriod'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
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
