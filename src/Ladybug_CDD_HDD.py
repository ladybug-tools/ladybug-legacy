# This component calculates heating and cooling degree days
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
Calculates heating and cooling degree-days.
Traditionally, degree-days are defined as the difference between a base temperature and the average ambient air temperature multiplied by the number of days that this difference exists.
By default, this component uses a more accurate calculation than the traditional method based on the minimum and maximum temperature of each day.
You may check the formulas in this page: "http://www.vesma.com/ddd/ddcalcs.htm"
If you rather to use the traditional method, set useDailyAvrMethod to True.
-
Provided by Ladybug 0.0.61
    
    Args:
        _hourlyDryBulbTemperature: Annual dry bulb temperature from the Import epw component (in degrees Celsius).
        _coolingBaseTemperature_: Base temperature for cooling (in degrees Celsius).  Default is set to 23.3C but this can be much lower if the analysis is for a building with high heat gain or insulation.
        _heatingBaseTemperature_: Base temperature for heating (in degrees Celsius).  Default is set to 18.3C but this can be much lower if the analysis is for a building with high heat gain or insulation.
        useDailyAvrMethod_: set to "True" to use the traditional method of degree days calculation, which will calculate the average temperature of each day and sum up all of these temperatures over the year.  This is opoosed to this component's default analysis, which will will examine each hour of the year and then convert results to degree-days.
    Returns:
        readMe!: A summary of the input.
        daily_coolingDegDays: Cooling degree-days summed for each day of the year. For visualizations of over the whole year, connect this to the grasshopper chart/graph component. 
        daily_heatingDegDays: Heating degree-days summed for each day of the year. For visualizations of over the whole year, connect this to the grasshopper chart/graph component. 
        monthly_coolingDegDays: Cooling degree-days summed for each month of the year.
        monthly_heatingDegDays: Heating degree-days summed for each month of the year.
        annual_coolingDegDays: The total cooling degree-days for the entire year.
        annual_heatingDegDays: The total heating degree-days for the entire year.
"""

ghenv.Component.Name = "Ladybug_CDD_HDD"
ghenv.Component.NickName = "CDD_HDD"
ghenv.Component.Message = 'VER 0.0.61\nDEC_12_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

# provide inputs
try: coolingSetPoint = float(_coolingBaseTemperature_)
except: coolingSetPoint = 23.3
print 'Cooling setpoint is: ' + `coolingSetPoint` + ' C.'

try: heatingSetPoint = float(_heatingBaseTemperature_)
except: heatingSetPoint = 18.3
print 'Heating setpoint is: ' + `heatingSetPoint` + ' C.'


def main(coolingSetPoint, heatingSetPoint, hourlyDryBulbTemperature, useDailyAvrMethod):
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
        
        # copy the custom code here
        # check the input data
        try:
            hourlyDBTemp = hourlyDryBulbTemperature
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
            
            daily_coolingDegDays = [];
            daily_heatingDegDays = [];
            monthly_coolingDegDays = [];
            monthly_heatingDegDays = [];
            annual_coolingDegDays = [];
            annual_heatingDegDays = [];
            
            for l in range(len(separatedLists)):
                    [daily_coolingDegDays.append(item) for item in listInfo[l][:2]]
                    daily_coolingDegDays.append('Daily_coolingDegDays')
                    daily_coolingDegDays.append('Degree Hours')
                    daily_coolingDegDays.append('Daily')
                    [daily_coolingDegDays.append(item) for item in listInfo[l][5:7]]
                
                    [daily_heatingDegDays.append(item) for item in listInfo[l][:2]]
                    daily_heatingDegDays.append('Daily_heatingDegDays')
                    daily_heatingDegDays.append('Degree Hours')
                    daily_heatingDegDays.append('Daily')
                    [daily_heatingDegDays.append(item) for item in listInfo[l][5:7]]

                    [monthly_coolingDegDays.append(item) for item in listInfo[l][:2]]
                    monthly_coolingDegDays.append('monthly_coolingDegDays')
                    monthly_coolingDegDays.append('Degree Hours')
                    monthly_coolingDegDays.append('Monthly')
                    [monthly_coolingDegDays.append(item) for item in listInfo[l][5:7]]
                
                    [monthly_heatingDegDays.append(item) for item in listInfo[l][:2]]
                    monthly_heatingDegDays.append('monthly_heatingDegDays')
                    monthly_heatingDegDays.append('Degree Hours')
                    monthly_heatingDegDays.append('Monthly')
                    [monthly_heatingDegDays.append(item) for item in listInfo[l][5:7]]
                
                    [annual_coolingDegDays.append(item) for item in listInfo[l][:2]]
                    annual_coolingDegDays.append('annual_coolingDegDays')
                    annual_coolingDegDays.append('Degree Hours')
                    annual_coolingDegDays.append('Annual')
                    [annual_coolingDegDays.append(item) for item in listInfo[l][5:7]]
                
                    [annual_heatingDegDays.append(item) for item in listInfo[l][:2]]
                    annual_heatingDegDays.append('annual_heatingDegDays')
                    annual_heatingDegDays.append('Degree Hours')
                    annual_heatingDegDays.append('Annual')
                    [annual_heatingDegDays.append(item) for item in listInfo[l][5:7]]
                    
                    hourlyTemperature = separatedLists[l]
                    
                    for day in range (int(len(hourlyTemperature)/24)):
                        # 7 is for thr first 7 members of the list which are information
                        dayHourlyTemp = hourlyTemperature[(day * 24):((day+1)*24)]
                        if useDailyAvrMethod == True:
                            dayAvrTemp = sum(dayHourlyTemp)/len(dayHourlyTemp)
                            if dayAvrTemp < heatingSetPoint:
                                daily_heatingDegDays.append(heatingSetPoint - dayAvrTemp)
                            else: daily_heatingDegDays.append(0)
                            if coolingSetPoint < dayAvrTemp:
                                daily_coolingDegDays.append(dayAvrTemp - coolingSetPoint)
                            else: daily_coolingDegDays.append(0)
                        else:
                            minT = min(dayHourlyTemp)
                            maxT = max(dayHourlyTemp)
                            
                            # heating degree days
                            if minT > heatingSetPoint: daily_heatingDegDays.append(0)
                            elif (maxT + minT)/2 > heatingSetPoint: daily_heatingDegDays.append((heatingSetPoint-minT)/4)
                            elif maxT >= heatingSetPoint: daily_heatingDegDays.append((heatingSetPoint-minT)/2-(maxT-heatingSetPoint)/4)
                            elif maxT < heatingSetPoint: daily_heatingDegDays.append(heatingSetPoint-(maxT+minT)/2)
                            
                            # cooling degree days
                            if maxT < coolingSetPoint: daily_coolingDegDays.append(0)
                            elif (maxT + minT)/2 < coolingSetPoint: daily_coolingDegDays.append((maxT-coolingSetPoint)/4)
                            elif minT <= coolingSetPoint: daily_coolingDegDays.append((maxT-coolingSetPoint)/2 - (coolingSetPoint-minT)/4)
                            elif minT > coolingSetPoint: daily_coolingDegDays.append((maxT + minT)/2 - coolingSetPoint)
                    
                    numOfDays = lb_preparation.numOfDays
                    
                    for month in range(len(numOfDays)- 1):
                        monthly_heatingDegDays.append(sum(daily_heatingDegDays[numOfDays[month] + 7: numOfDays[month + 1]+ 7]))
                        monthly_coolingDegDays.append(sum(daily_coolingDegDays[numOfDays[month] + 7: numOfDays[month + 1]+ 7]))
                    
                    annual_heatingDegDays.append(sum(monthly_heatingDegDays[7:]))
                    annual_coolingDegDays.append(sum(monthly_coolingDegDays[7:]))
                        
                    
                    
            return daily_coolingDegDays, daily_heatingDegDays, monthly_coolingDegDays, monthly_heatingDegDays, annual_coolingDegDays, annual_heatingDegDays
        elif hourlyDBTemp[0] == 'Connect temperature here':
            print 'Connect annual hourly dry bulb temperature'
            return -1
        else:
            print str(hourlyDBTemp[0])
            warning = 'Please connect valid annual hourly dry bulb temperature from the Import epw component!'
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1


result = main(coolingSetPoint, heatingSetPoint, _hourlyDryBulbTemperature, useDailyAvrMethod_)
if result!= -1:
    daily_coolingDegDays, daily_heatingDegDays, monthly_coolingDegDays, monthly_heatingDegDays, annual_coolingDegDays, annual_heatingDegDays = result
