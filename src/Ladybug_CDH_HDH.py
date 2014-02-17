# This component calculates heating and cooling degree hours
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Heating and cooling degree hours.
Degree hour for each hour is the difference between the base temperature and the average ambient outside air temperature.
-
Provided by Ladybug 0.0.54
    
    Args:
        _hourlyDryBulbTemperature: Annual dry bulb temperature (in degrees Celsius)
        _coolingBaseTemperature_: Base temperature for cooling (in degrees Celsius)
        _heatingBaseTemperature_: Base temperature for heating (in degrees Celsius)
    Returns:
        readMe!: Summary of the input for double check
        hourly_coolingDegHours: Hourly cooling degree hours data. For visualization connect to the chart/graph component(s) 
        hourly_heatingDegHours: Hourly heating degree hours data. For visualization connect to the chart/graph component(s)
        daily_coolingDegHours: Daily cooling degree hours data. For visualization connect to the chart/graph component(s)
        daily_heatingDegHours: Daily heating degree hours data. For visualization connect to the chart/graph component(s)
        monthly_coolingDegHours: Monthly cooling degree hours data
        monthly_heatingDegHours: Monthly heating degree hours data
        annual_coolingDegHours: Annual cooling degree hours data
        annual_heatingDegHours: Annual heating degree hours
"""

ghenv.Component.Name = "Ladybug_CDH_HDH"
ghenv.Component.NickName = "CDH_HDH"
ghenv.Component.Message = 'VER 0.0.54\nFEB_16_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

# provide inputs
try: coolingSetPoint = float(_coolingBaseTemperature_)
except: coolingSetPoint = 23.3
print 'Cooling base temperature: ' + `coolingSetPoint` + ' C.'
coolingSetBack = coolingSetPoint

#try: coolingSetBack = float(coolingSetBack)
#except: coolingSetBack = 26.7
#print 'Cooling setback is: ' + `coolingSetBack` + ' C.'

try: heatingSetPoint = float(_heatingBaseTemperature_)
except: heatingSetPoint = 18.3
print 'Heating base temperature is: ' + `heatingSetPoint` + ' C.'

#try: heatingSetBack = float(heatingSetBack)
#except: heatingSetBack = 16.0
#print 'Heating setback is: ' + `heatingSetBack` + ' C.'
heatingSetBack = heatingSetPoint

try: startOfWorkingHours = float(occupationStartHour - 1)
except: startOfWorkingHours = 0
#print 'Occupation hours starts at ' + `startOfWorkingHours + 1` + ':00.'


try: endOfWorkingHours = float(occupationEndHour - 1)
except: endOfWorkingHours = 23
#print 'Occupation hours ends at ' + `endOfWorkingHours + 1` + ':00.'


def main(coolingSetPoint, heatingSetPoint, coolingSetBack, heatingSetBack, startOfWorkingHours, endOfWorkingHours):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
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
            
