# This component calculates heating and cooling degree days
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Heating and cooling degree days
In traditional way degree day is the difference between the base temperature and the average ambient air temperature for the day.
This component uses a more accurate calculation method based on min and max temperature of the day.
You may check the formulas in this page: "http://www.vesma.com/ddd/ddcalcs.htm"
If you rather to use the traditional method set useDailyAvrMethod to True.
-
Provided by Ladybug 0.0.52
    
    Args:
        _hourlyDryBulbTemperature: Annual dry bulb temperature (in degrees Celsius)
        _coolingBaseTemperature_: Base temperature for cooling (in degrees Celsius)
        _heatingBaseTemperature_: Base temperature for heating (in degrees Celsius)
        useDailyAvrMethod_: set it to True to use the traditional method of degree days calculation
    Returns:
        readMe!: summary of the input for double check
        daily_coolingDegDays: Daily cooling degree days data. For visualization connect to the chart/graph component(s) 
        daily_heatingDegDays: Heating degree days. For visualization connect to the chart/graph component(s) 
        monthly_coolingDegDays: Monthly cooling degree days data
        monthly_heatingDegDays: Monthly heating degree days data
        annual_coolingDegDays: Annual cooling degree days
        annual_heatingDegDays: Annual heating degree days
"""

ghenv.Component.Name = "Ladybug_CDD_HDD"
ghenv.Component.Message = 'VER 0.0.52\nNOV_01_2013'

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


result = main(coolingSetPoint, heatingSetPoint, _hourlyDryBulbTemperature, useDailyAvrMethod_)
if result!= -1:
    daily_coolingDegDays, daily_heatingDegDays, monthly_coolingDegDays, monthly_heatingDegDays, annual_coolingDegDays, annual_heatingDegDays = result