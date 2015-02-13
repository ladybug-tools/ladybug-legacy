# Select and average hourly data
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to select the data out of an annual hourly data stream (from the importEPW component) using the "Analysis Period" component.
This componenent also averages this selected data for each day during the analysis period, each month during the analysis period, and for the average hour of each month for the analysis period.
-
Provided by Ladybug 0.0.59
    
    Args:
        _annualHourlyData: An hourly data stream from the "Import epw" component.
        _analysisPeriod_: The "analysisPeriod" Output from "Analysis Period" component. If no input is provided, the default analysis period is set to the whole year.
    Returns:
        readMe!: A text confirmation of the analysis period.
        selHourlyData: The hourly data stream for the analysis period.
        averagedDaily: The averaged data for each day during the analysis period
        averagedMonthly: The averaged data for each month during the analysis period
        avrMonthlyPerHour: The data for the average hour of each month during the analysis period
        avrAnalysisPeriod: The averaged data for the analysis period
"""

ghenv.Component.Name = "Ladybug_Average Data"
ghenv.Component.NickName = 'selectAndAverageData'
ghenv.Component.Message = 'VER 0.0.59\nFEB_08_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass



import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

def main(annualHourlyData, analysisPeriod):
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
        
        # check the input data
        try:
            hourlyData = annualHourlyData
            if hourlyData[4] == 'Hourly': checkData = True
            else: checkData = False
        except: 
            checkData = False
        
        if checkData:
            # separate data
            indexList, listInfo = lb_preparation.separateList(hourlyData, lb_preparation.strToBeFound)
        
            #separate lists of lists
            separatedLists = []
            for i in range(len(indexList)-1):
                selList = []
                [selList.append(float(x)) for x in hourlyData[indexList[i]+7:indexList[i+1]]]
                separatedLists.append(selList)
        
            # read analysis period
            stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod)
            
            def average(list):
                return sum(list)/len(list)
        
            selHourlyData =[];
            selDailyData = []; avDailyData = []
            selWeeklyData = []; avWeeklyData = []
            selMonthlyData = []; avMonthlyData = []
            avrAnalysisPeriod =[]
            
            
            for l in range(len(separatedLists)):
                [selHourlyData.append(item) for item in listInfo[l][:4]]
                selHourlyData.append('Hourly')
                selHourlyData.append((stMonth, stDay, stHour))
                selHourlyData.append((endMonth, endDay, endHour))
                # select data
                stAnnualHour = lb_preparation.date2Hour(stMonth, stDay, stHour)
                endAnnualHour = lb_preparation.date2Hour(endMonth, endDay, endHour)
                
                # check it goes from the end of the year to the start of the year
                selectedData = []
                if stAnnualHour < endAnnualHour:
                    for i, item in enumerate(separatedLists[l][stAnnualHour-1:endAnnualHour]):
                        if stHour-1 <= (i + stHour - 1)%24 <= endHour-1:
                            selHourlyData.append(item)
                            selectedData.append(item)
                    type = True
                else:
                    for i, item in enumerate(separatedLists[l][stAnnualHour-1:]):
                        if stHour-1 <= (i + stHour - 1)%24 <= endHour-1:
                            selHourlyData.append(item)
                            selectedData.append(item)
                    for i, item in enumerate(separatedLists[l][:endAnnualHour]):
                        if stHour-1 <= i %24 <= endHour-1:
                            selHourlyData.append(item)
                            selectedData.append(item)
                    type = False
                
                
                [avrAnalysisPeriod.append(item) for item in listInfo[l][:4]]
                avrAnalysisPeriod.append('Analysis Period -> averaged')
                avrAnalysisPeriod.append((stMonth, stDay, stHour))
                avrAnalysisPeriod.append((endMonth, endDay, endHour))
                avrAnalysisPeriod.append(average(selectedData))
                
                
                # add list informations
                [selDailyData.append(item) for item in listInfo[l][:4]]
                selDailyData.append('Daily-> averaged for each hour')
                selDailyData.append((stMonth, stDay, stHour))
                selDailyData.append((endMonth, endDay, endHour))
                
                [avDailyData.append(item) for item in listInfo[l][:4]]
                avDailyData.append('Daily-> averaged')
                avDailyData.append((stMonth, stDay, stHour))
                avDailyData.append((endMonth, endDay, endHour))
                
                if type:
                    for JD in range(lb_preparation.getJD(stMonth,stDay), lb_preparation.getJD(endMonth,endDay) + 1):
                        dailyData = separatedLists[l][lb_preparation.getHour(JD, stHour)-1 : lb_preparation.getHour(JD, endHour)]
                        avDailyData.append(average(dailyData))
                        for hour in range(endHour - stHour + 1): selDailyData.append(dailyData[hour])
                else:
                    for JD in range(lb_preparation.getJD(stMonth,stDay), 365 + 1):
                        dailyData = separatedLists[l][lb_preparation.getHour(JD, stHour)-1 : lb_preparation.getHour(JD, endHour)]
                        avDailyData.append(average(dailyData))
                        for hour in range(endHour - stHour + 1): selDailyData.append(dailyData[hour])
                    
                    for JD in range(1, lb_preparation.getJD(endMonth,endDay) +1):
                        dailyData = separatedLists[l][lb_preparation.getHour(JD, stHour)-1 : lb_preparation.getHour(JD, endHour)]
                        avDailyData.append(average(dailyData))
                        for hour in range(endHour - stHour + 1): selDailyData.append(dailyData[hour])
                

                # average monthly
                [selMonthlyData.append(item) for item in listInfo[l][:4]]
                selMonthlyData.append('Monthly-> averaged for each hour')
                selMonthlyData.append((stMonth, stDay, stHour))
                selMonthlyData.append((endMonth, endDay, endHour))
                
                [avMonthlyData.append(item) for item in listInfo[l][:4]]
                avMonthlyData.append('Monthly-> averaged')
                avMonthlyData.append((stMonth, stDay, stHour))
                avMonthlyData.append((endMonth, endDay, endHour))

                monthDays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] 
                if type:
                    for month in range(stMonth, endMonth + 1):
                        stJD = lb_preparation.getJD(month, 1)
                        endJD = lb_preparation.getJD(month, monthDays[month])
                        monthlyData = separatedLists[l][lb_preparation.getHour(stJD, stHour)-1 : lb_preparation.getHour(endJD , endHour)]
                        selMonthly = []
                        for i, item in enumerate(monthlyData):
                            if stHour-1 <= (i + stHour -1)%24 <= endHour-1: selMonthly.append(item)
                        
                        avMonthlyData.append(average(selMonthly))
                        
                        for hour in range(endHour - stHour + 1):
                            eachHourData = []
                            for day in range(monthDays[month]):
                                eachHourData.append(monthlyData[hour + (day * (endHour - stHour + 1))])
                            selMonthlyData.append(average(eachHourData))
                else:
                    for month in range(stMonth, 12 + 1):
                        stJD = lb_preparation.getJD(month, 1)
                        endJD = lb_preparation.getJD(month, monthDays[month])
                        
                        #for item in 
                        monthlyData = separatedLists[l][lb_preparation.getHour(stJD, stHour)-1 : lb_preparation.getHour(endJD , endHour)]
                        selMonthly = []
                        for i, item in enumerate(monthlyData):
                            if stHour-1 <= (i + stHour -1)%24 <= endHour-1: selMonthly.append(item)
                        
                        avMonthlyData.append(average(selMonthly))
                    
                        for hour in range(endHour - stHour + 1):
                            eachHourData = []
                            for day in range(monthDays[month]):
                                eachHourData.append(monthlyData[hour + (day * (endHour - stHour + 1))])
                            selMonthlyData.append(average(eachHourData))
                    
                    for month in range(1, endMonth + 1):
                        stJD = lb_preparation.getJD(month, 1)
                        endJD = lb_preparation.getJD(month, monthDays[month])
                        monthlyData = separatedLists[l][lb_preparation.getHour(stJD, stHour)-1 : lb_preparation.getHour(endJD , endHour)]
                        avMonthlyData.append(average(monthlyData))
                    
                        for hour in range(endHour - stHour + 1):
                            eachHourData = []
                            for day in range(monthDays[month]):
                                eachHourData.append(monthlyData[hour + (day * (endHour - stHour + 1))])
                            selMonthlyData.append(average(eachHourData))
                
            return selHourlyData, avDailyData, selDailyData, selWeeklyData, selMonthlyData, avMonthlyData, avrAnalysisPeriod
        elif _annualHourlyData[0] == "Connect Data Here!":
            print "Connect annualHourlyData from the importEPW component!"
            return -1
        else:
            print "Input annualHourlyData is not a valid Ladybug hourly data!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "hourlyData is not a valid Ladybug hourly data!")
            return -1
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1


result = main(_annualHourlyData, _analysisPeriod_)
if result!= -1:
            selHourlyData, averagedDaily, avrDailyPerHour, avrWeeklyPerHour, \
            avrMonthlyPerHour, averagedMonthly, avrAnalysisPeriod = result
