# This component calculates heating and cooling degree hours
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Calculates heating and cooling degree-hours.
Degree-hours are defined as the difference between the base temperature and the average ambient outside air temperature multiplied by the number of hours that this difference condition exists.
-
Provided by Ladybug 0.0.66
    
    Args:
        _hourlyDryBulbTemperature: Annual dry bulb temperature from the Import epw component (in degrees Celsius).
        _coolingBaseTemperature_: Base temperature for cooling (in degrees Celsius). Default is set to 23.3C but this can be much lower if the analysis is for a building with high heat gain or insulation.
        _heatingBaseTemperature_: Base temperature for heating (in degrees Celsius). Default is set to 18.3C but this can be much lower if the analysis is for a building with high heat gain or insulation.
    Returns:
        readMe!: A ummary of the input.
        hourly_coolingDegHours: Cooling degree-hours for each hour of the year. For visualizations over the whole year, connect this to the grasshopper chart/graph component. 
        hourly_heatingDegHours: Heating degree-days for each hour of the year. For visualizations over the whole year, connect this to the grasshopper chart/graph component. 
        daily_coolingDegHours: Cooling degree-days summed for each day of the year. For visualizations of over the whole year, connect this to the grasshopper chart/graph component. 
        daily_heatingDegHours: Heating degree-days summed for each day of the year. For visualizations of over the whole year, connect this to the grasshopper chart/graph component. 
        monthly_coolingDegHours: Cooling degree-days summed for each month of the year.
        monthly_heatingDegHours: Heating degree-days summed for each month of the year.
        annual_coolingDegHours: The total cooling degree-days for the entire year.
        annual_heatingDegHours: The total heating degree-days for the entire year.
"""

ghenv.Component.Name = "Ladybug_CDH_HDH"
ghenv.Component.NickName = "CDH_HDH"
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

# provide inputs
try: coolingSetPoint = float(_coolingBaseTemperature_)
except: coolingSetPoint = 23.3
print 'Cooling base temperature: ' + `coolingSetPoint` + ' C.'
coolingSetBack = coolingSetPoint

try: heatingSetPoint = float(_heatingBaseTemperature_)
except: heatingSetPoint = 18.3
print 'Heating base temperature is: ' + `heatingSetPoint` + ' C.'

heatingSetBack = heatingSetPoint

try: startOfWorkingHours = float(occupationStartHour - 1)
except: startOfWorkingHours = 0

try: endOfWorkingHours = float(occupationEndHour - 1)
except: endOfWorkingHours = 23


def main(coolingSetPoint, heatingSetPoint, coolingSetBack, heatingSetBack, startOfWorkingHours, endOfWorkingHours):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        # copy the custom code here
        # check the input data
        try:
            hourlyDBTemp = _hourlyDryBulbTemperature
            if hourlyDBTemp[2] == 'Dry Bulb Temperature' and hourlyDBTemp[4] == 'Hourly': checkData = True
            else: checkData = False
        except: checkData = False
        
        if checkData:
            # separate data
            indexList, listInfo = lb_preparation.separateList(hourlyDBTemp, lb_preparation.strToBeFound)
        
            #separate total, diffuse and direct radiations
            separatedLists = []
            for i in range(len(indexList)-1):
                selList = []
                [selList.append(float(x)) for x in hourlyDBTemp[indexList[i]+7:indexList[i+1]]]
                separatedLists.append(selList)
            
            hourly_coolingDegHours = [];
            hourly_heatingDegHours = [];
            daily_coolingDegHours = [];
            daily_heatingDegHours = [];
            monthly_coolingDegHours = [];
            monthly_heatingDegHours = [];
            annual_coolingDegHours = [];
            annual_heatingDegHours = [];
            
            for l in range(len(separatedLists)):
                [hourly_coolingDegHours.append(item) for item in listInfo[l][:2]]
                hourly_coolingDegHours.append('Cooling Degree Hours')
                hourly_coolingDegHours.append('Degree Hours')
                hourly_coolingDegHours.append('Hourly')
                [hourly_coolingDegHours.append(item) for item in listInfo[l][5:7]]
                
                [hourly_heatingDegHours.append(item) for item in listInfo[l][:2]]
                hourly_heatingDegHours.append('Heating Degree Hours')
                hourly_heatingDegHours.append('Degree Hours')
                hourly_heatingDegHours.append('Hourly')
                [hourly_heatingDegHours.append(item) for item in listInfo[l][5:7]]
                
                [daily_coolingDegHours.append(item) for item in listInfo[l][:2]]
                daily_coolingDegHours.append('Cooling Degree Hours')
                daily_coolingDegHours.append('Degree Hours')
                daily_coolingDegHours.append('Daily')
                [daily_coolingDegHours.append(item) for item in listInfo[l][5:7]]
                
                [daily_heatingDegHours.append(item) for item in listInfo[l][:2]]
                daily_heatingDegHours.append('Heating Degree Hours')
                daily_heatingDegHours.append('Degree Hours')
                daily_heatingDegHours.append('Daily')
                [daily_heatingDegHours.append(item) for item in listInfo[l][5:7]]

                [monthly_coolingDegHours.append(item) for item in listInfo[l][:2]]
                monthly_coolingDegHours.append('Cooling Degree Hours')
                monthly_coolingDegHours.append('Degree Hours')
                monthly_coolingDegHours.append('Monthly')
                [monthly_coolingDegHours.append(item) for item in listInfo[l][5:7]]
                
                [monthly_heatingDegHours.append(item) for item in listInfo[l][:2]]
                monthly_heatingDegHours.append('Heating Degree Hours')
                monthly_heatingDegHours.append('Degree Hours')
                monthly_heatingDegHours.append('Monthly')
                [monthly_heatingDegHours.append(item) for item in listInfo[l][5:7]]
                
                [annual_coolingDegHours.append(item) for item in listInfo[l][:2]]
                annual_coolingDegHours.append('Cooling Degree Hours')
                annual_coolingDegHours.append('Degree Hours')
                annual_coolingDegHours.append('Annual')
                [annual_coolingDegHours.append(item) for item in listInfo[l][5:7]]
                
                [annual_heatingDegHours.append(item) for item in listInfo[l][:2]]
                annual_heatingDegHours.append('Heating Degree Hours')
                annual_heatingDegHours.append('Degree Hours')
                annual_heatingDegHours.append('Annual')
                [annual_heatingDegHours.append(item) for item in listInfo[l][5:7]]
                
                hourlyTemperature = separatedLists[l]
                
                # for each hour based on hourly temperature data
                for hour, temp in enumerate(hourlyTemperature):
                    if float(temp) < heatingSetPoint:
                        hourly_heatingDegHours.append(heatingSetPoint - float(temp))
                    else: hourly_heatingDegHours.append(0)
                    if coolingSetPoint < float(temp):
                        hourly_coolingDegHours.append(float(temp) - coolingSetPoint)
                    else: hourly_coolingDegHours.append(0)
                
                # for each day based on hourly degree hours
                for day in range (int(len(hourlyTemperature)/24)):
                    # 7 is for thr first 7 members of the list which are information
                    daily_heatingDegHours.append(sum(hourly_heatingDegHours[(day * 24) + 7:((day+1)*24) + 7]))
                    daily_coolingDegHours.append(sum(hourly_coolingDegHours[(day * 24) + 7:((day+1)*24) + 7]))
                
                numOfDays = lb_preparation.numOfDays
                for month in range(len(numOfDays)- 1):
                    monthly_heatingDegHours.append(sum(daily_heatingDegHours[numOfDays[month] + 7: numOfDays[month + 1]+ 7]))
                    monthly_coolingDegHours.append(sum(daily_coolingDegHours[numOfDays[month] + 7: numOfDays[month + 1]+ 7]))
                
                annual_heatingDegHours.append(sum(monthly_heatingDegHours[7:]))
                annual_coolingDegHours.append(sum(monthly_coolingDegHours[7:]))
                
            return hourly_coolingDegHours, hourly_heatingDegHours, daily_coolingDegHours, daily_heatingDegHours, monthly_coolingDegHours, monthly_heatingDegHours, annual_coolingDegHours, annual_heatingDegHours
        elif hourlyDBTemp[0] == 'Connect temperature here':
            print 'Connect annual hourly dry bulb temperature'
            return -1
        else:
            warning = 'Please provide annual hourly dry bulb temperature!'
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1


if 1 > 0: #(geometry and geometry[0]!=None):
    #if runIt:
    result = main(coolingSetPoint, heatingSetPoint, coolingSetBack, heatingSetBack, startOfWorkingHours, endOfWorkingHours)
    if result!= -1:
        hourly_coolingDegHours, hourly_heatingDegHours, daily_coolingDegHours, daily_heatingDegHours, monthly_coolingDegHours, monthly_heatingDegHours, annual_coolingDegHours, annual_heatingDegHours = result
            
