#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate values for Honeybee_Create CSV Schedule
-
Use this component to write schedules for EnergyPlus using LB_schedules as inputs.
-
Provided by Ladybug 0.0.62
    
    Args:
        _sun: Sunday. Connect a LB_schedule.
        _mon: Monday. Connect a LB_schedule.
        _tue: Tuesday. Connect a LB_schedule.
        _wed: Wednesday. Connect a LB_schedule.
        _thu: Thursday. Connect an LB_schedule.
        _fri: Friday. Connect a LB_schedule.
        _sat: Saturday. Connect a LB_schedule.
        holiday_: Optional input. Connect a LB_schedule for the holidays.
        ------------: ...
        _runIt: Set to "True" to run the component
        epwFile_: If you want to generate a list of holiday DOYs automatically connect an .epw file path on your system as a string.
        weekStartWith_: Set the schedule start day of the week. The default is set to "monday".
        -
        Write one of the following string:
        1) sun
        2) mon
        3) tue
        4) wed
        5) thu
        6) fri
        7) sat
        overwriteHolidays_: Connect a list of DOYs (from 1 to 365) or a list of strings (example: DEC 25).
        -
        Attention this input overwrites epwFile DOYs.
        analysisPeriod_: If your input units do not represent a full year, use this input to specify the period of the year that the schedule applies to.
    Returns:
        readMe!: ...
        scheduleValues: The values to be written into the .csv schedule. Connect it to "_values/Honeybee_Create CSV Schedule".
        nationalHolidays: Date of the national holydays.
"""

ghenv.Component.Name = "Honeybee_Annual Schedule"
ghenv.Component.NickName = 'AnnualSchedule'
ghenv.Component.Message = 'VER 0.0.62\nMAY_05_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
from collections import deque
import itertools
from datetime import date

def checkTheData(sun, mon, tue, wed, thu, fri, sat):
    if sun == None \
    and mon == None and tue == None and wed == None \
    and thu == None and fri == None and sat == None:
        checkData = False
    elif sun and mon and tue and wed and thu and fri and sat:
        checkData = True
    else: checkData = False
    return checkData

def flatten(container):
    for i in container:
        if isinstance(i, list) or isinstance(i, tuple):
            for j in flatten(i):
                yield j
        else:
            yield i

def fromDayToDate(day, months):
    date_day = date.fromordinal(date(2015, 1, 1).toordinal() + day) # 2015 is not leap year
    
    month, day = str(date_day).split('-')[1:]
    months_date = months[month]
    date_fromDay = months_date + ' ' + day
    
    return date_fromDay

def fromDateToDay(holiday, months):
    
    start_date = date(2015, 1, 1)
    # split
    text_month = holiday.split(' ')[0].upper()
    # reverse dict
    dict_reverse = {value: key for key, value in months.items()}
    # extract value
    int_month = int(dict_reverse[text_month])
    end_date = date(2015, int_month, int(holiday.split(' ')[1]))
    
    period = end_date - start_date
    
    day = period.days + 1
    return day

def main(sun, mon, tue, wed, thu, fri, sat, holiday, runIt, epwFile, weekStartWith, overwriteHolidays, analysisPeriod):
    if runIt == True:
        
        # dict of months
        months_dict = {'01':'GEN', '02':'FEB', '03':'MAR', '04':'APR', '05':'MAY', '06':'JUN',
        '07':'LUG', '08':'AGO', '09':'SEP', '10':'OCT', '11':'NOV', '12':'DEC'}
        
        # build the week
        def rotate_week(weekStartWith):
            days_of_week = {'sat':0, 'sun':1, 'mon':2, 'tue':3, 'wed':4, 'thu':5, 'fri':6}
            list_of_values = [0, 1, 2, 3, 4, 5, 6]
            d = deque(list_of_values)
            lower_key = weekStartWith.lower()
            d.rotate(-days_of_week[lower_key])
            return d
            
        # default value
        if weekStartWith:
            weekStartWith = weekStartWith
        else:
            weekStartWith = 'mon'
        
        # run the funcion
        week = rotate_week(weekStartWith)
        # make a year by cutting the list
        dayWeekList = list(itertools.chain.from_iterable(itertools.repeat(week, 53)))[:365]
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        #first loop: if epwFile is on
        if epwFile:
            #get the base code from EPW
            locationData = lb_preparation.epwLocation(epwFile)
            codeNation = lb_preparation.epwDataReader(epwFile, locationData[0])[14][1]
            code = codeNation.split("_")
            if len(code) == 3:
                country = code[2]
            elif len(code) == 2:
                country = code[1]
            else:
                country = code[1]
            print country
            
            if not overwriteHolidays:
                #only National Hoildays arranged by region
                #not found list:
                #BLZ (CENTRAL AMERICA), BRN (SOUTH PACIFIC), GUM (SOUTH PACIFIC), MHL (SOUTH PACIFIC), PLW (SOUTH PACIFIC), UMI (SOUTH PACIFIC)
                #https://energyplus.net/weather
                ###################################################
                #http://www.officeholidays.com/countries/ ------ http://www.officeholidays.com/countries/
                countries = {'USA':[0,[i for i, x in enumerate(dayWeekList) if x == 2][2],[i for i, x in enumerate(dayWeekList) if x == 2][21],184,[i for i, x in enumerate(dayWeekList) if x == 2][35],314,[i for i, x in enumerate(dayWeekList) if x == 5][46],359],
                'CAN': [0,181,[i for i, x in enumerate(dayWeekList) if x == 2][35],358,359],
                'CUB': [0,1,[i for i, x in enumerate(dayWeekList) if x == 6][12],120,205,206,207,282,358,364],
                'GTM': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],120,180,257,292,304,358],
                'HND': [0,[i for i, x in enumerate(dayWeekList) if x == 4][11],[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],120,257,278,358],
                'MEX': [0,[i for i, x in enumerate(dayWeekList) if x == 2][4],[i for i, x in enumerate(dayWeekList) if x == 2][11],[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],120,258,[i for i, x in enumerate(dayWeekList) if x == 2][46],345,358,359],
                'MTQ': [0,[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,127,[i for i, x in enumerate(dayWeekList) if x == 2][19],194,226,304,314,358],
                'NIC': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],120,121,169,256,257,341,358],
                'PRI': [0,5,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 2][12],127,169,327,358],
                'SLV': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],120,129,168,215,216,217,305,358,359],
                'VIR': [0,5,17,45,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],89,149,153,248,304,314,358,359],
                'ARG': [0,[i for i, x in enumerate(dayWeekList) if x == 2][5],[i for i, x in enumerate(dayWeekList) if x == 3][5],82,[i for i, x in enumerate(dayWeekList) if x == 6][12],91,120,144,170,188,189,[i for i, x in enumerate(dayWeekList) if x == 2][32],282,[i for i, x in enumerate(dayWeekList) if x == 2][47],341,358],
                'BOL': [0,21,[i for i, x in enumerate(dayWeekList) if x == 2][5],[i for i, x in enumerate(dayWeekList) if x == 3][5],[i for i, x in enumerate(dayWeekList) if x == 5][11],120,[i for i, x in enumerate(dayWeekList) if x == 5][20],171,305,358],
                'BRA': [0,[i for i, x in enumerate(dayWeekList) if x == 2][5],[i for i, x in enumerate(dayWeekList) if x == 3][5],[i for i, x in enumerate(dayWeekList) if x == 4][5],[i for i, x in enumerate(dayWeekList) if x == 5][11],110,120,[i for i, x in enumerate(dayWeekList) if x == 5][20],249,284,305,318,323,358],
                'CHL': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],120,140,179,196,226,261,262,303,304,341,358],
                'COL': [0,10,79,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],120,128,149,156,[i for i, x in enumerate(dayWeekList) if x == 2][26],200,218,226,289,[i for i, x in enumerate(dayWeekList) if x == 2][44],317,341,358],
                'ECU': [0,38,39,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 1][12],120,143,221,281,306,358],
                'PER': [0,[i for i, x in enumerate(dayWeekList) if x == 4][11],[i for i, x in enumerate(dayWeekList) if x == 5][11],120,179,208,209,242,280,304,341,358,359],
                'PRY': [0,59,[i for i, x in enumerate(dayWeekList) if x == 4][11],[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 1][12],120,133,134,162,227,271,284,341,358,364],
                'URY': [0,38,39,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],108,120,169,198,284,236,305,358],
                'VEN': [0,38,39,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],108,120,174,179,185,204,226,284,304,358,359,364],
                'AUS': [0,25,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],114,358,359,360],
                'FJI': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],174,249,282,303,345,359,360],
                'MYS': [38,120,121,140,155,186,187,242,254,258,274,345,358,359],
                'NZL': [0,3,38,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],114,[i for i, x in enumerate(dayWeekList) if x == 2][22],[i for i, x in enumerate(dayWeekList) if x == 2][42],358,359,360],
                'PHL': [0,1,38,55,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 0][12],98,120,162,187,232,240,253,303,304,333,357,358,363,364],
                'SGP': [0,38,39,[i for i, x in enumerate(dayWeekList) if x == 6][12],120,121,140,218,220,254,302,358,359],
                'DZA': [0,120,187,253,274,283,304,345],
                'EGY': [6,24,114,120,121,187,188,189,204,253,254,255,274,278,345],
                'ETH': [6,19,60,119,120,124,147,253,255,269,345],
                'GHA': [0,64,65,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,121,144,181,186,253,263,[i for i, x in enumerate(dayWeekList) if x == 6][48],358,359],
                'KEN': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,187,253,292,345,358,359],
                'LBY': [47,120,187,188,252,253,254,255,258,274,295,345,357],
                'MAR': [0,10,120,188,210,225,231,232,253,274,309,321,345],
                'MDG': [0,[i for i, x in enumerate(dayWeekList) if x == 2][12],88,120,124,135,176,226,304,345,358],
                'SEN': [0,[i for i, x in enumerate(dayWeekList) if x == 2][12],93,120,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],187,226,255,304,345,358],
                'TUN': [0,13,78,98,120,187,188,189,205,224,253,254,255,274,287,345],
                'ZAF': [0,79,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],117,120,121,166,220,266,349,358,359],
                'ZWE': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],107,120,144,[i for i, x in enumerate(dayWeekList) if x == 2][31],[i for i, x in enumerate(dayWeekList) if x == 3][31],355,358,359],
                'ARE': [0,124,186,187,252,253,254,255,274,333,335,336,344],
                'BDG': [51,75,84,103,120,140,142,181,183,185,187,226,236,253,254,255,283,284,345,349,358],
                'CHN': [0,37,38,39,40,41,42,43,93,120,121,159,257,258,273,274,275,276,277,278,279],
                'IND': [25,226,274],
                'IRN': [41,71,77,78,79,80,81,89,90,110,124,141,153,154,170,177,187,211,255,263,264,283,284,324,325,350,354],
                'JPN': [0,[i for i, x in enumerate(dayWeekList) if x == 2][1],41,79,118,122,123,124,[i for i, x in enumerate(dayWeekList) if x == 2][28],222,[i for i, x in enumerate(dayWeekList) if x == 2][37],264,282,306,326,356],
                'KAZ': [0,6,59,66,79,80,81,91,98,187,241,253,334,349,352],
                'KOR': [0,37,38,39,40,59,124,133,156,226,256,257,258,275,281,358],
                'KWT': [2,55,56,124,156,157,158,252,253,254,255,274,345],
                'LKA': [14,22,34,52,65,80,[i for i, x in enumerate(dayWeekList) if x == 6][12],102,103,110,120,140,141,169,186,199,228,254,284,301,317,345,346,358],
                'MAC': [0,38,39,40,94,120,258,273,293,353],
                'MDV': [0,11,120,156,186,206,253,254,274,306,314,334,345,364],
                'MNG': [0,38,191,192,193,194,195,362],
                'NPL': [14,49],
                'PAK': [35,81,120,187,188,189,225,253,254,283,312,345,358],
                'PRK': [0,39,46,52,104,114,120,156,169,207,236,251,281,357,360],
                'SAU': [187,190,191,253,254,255,264,265],
                'THA': [0,52,95,102,103,104,121,124,126,127,139,168,169,223,296,338,345,364],
                'TWN': [0,37,38,39,40,41,42,93,120,128,257,282],
                'UZB': [0,13,66,79,98,187,243,255,273,341],
                'VNM': [0,36,37,38,39,40,105,106,119,120,121,122,244],
                'AUT': [0,5,[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],145,226,298,304,311,341,358,359],
                'BEL': [0,[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],201,226,304,314,358],
                'BRG': [0,61,62,[i for i, x in enumerate(dayWeekList) if x == 6][17],120,[i for i, x in enumerate(dayWeekList) if x == 2][17],125,141,247,248,264,265,357,358,359],
                'BIH': [0,1,120,121],
                'BLR': [0,6,7,65,66,120,128,129,183,310,358],
                'CHE': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],124,212,358],
                'CYP': [0,5,[i for i, x in enumerate(dayWeekList) if x == 2][10],83,90,[i for i, x in enumerate(dayWeekList) if x == 6][17],120,[i for i, x in enumerate(dayWeekList) if x == 2][17],[i for i, x in enumerate(dayWeekList) if x == 2][24],226,273,300,358,359],
                'CZE': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,127,185,186,270,300,320,357,358,359],
                'DEU': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],275,358,359],
                'DNK': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],[i for i, x in enumerate(dayWeekList) if x == 6][16],124,[i for i, x in enumerate(dayWeekList) if x == 2][19],155,357,358,359],
                'ESP': [0,5,[i for i, x in enumerate(dayWeekList) if x == 6][12],120,226,284,304,339,341,358],
                'FIN': [0,5,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,174,175,308,340,357,358,359],
                'FRA': [0,[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,127,[i for i, x in enumerate(dayWeekList) if x == 2][19],194,226,304,314,358],
                'GBR': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],121,149,359,360],
                'GRC': [0,5,[i for i, x in enumerate(dayWeekList) if x == 2][10],83,[i for i, x in enumerate(dayWeekList) if x == 6][17],120,[i for i, x in enumerate(dayWeekList) if x == 2][17],[i for i, x in enumerate(dayWeekList) if x == 2][24],226,300,358],
                'HUN': [0,73,[i for i, x in enumerate(dayWeekList) if x == 1][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,[i for i, x in enumerate(dayWeekList) if x == 1][19],[i for i, x in enumerate(dayWeekList) if x == 2][19],231,295,304,358,359],
                'IRL': [0,75,[i for i, x in enumerate(dayWeekList) if x == 2][12],[i for i, x in enumerate(dayWeekList) if x == 2][17],[i for i, x in enumerate(dayWeekList) if x == 2][22],[i for i, x in enumerate(dayWeekList) if x == 2][30],303,358,359,360],
                'ISL': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 1][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],110,120,124,[i for i, x in enumerate(dayWeekList) if x == 1][19],[i for i, x in enumerate(dayWeekList) if x == 2][19],167,212,357,358,359,364],
                'ISR': [82,113,119,131,163,225,275,276,284,289,297],
                'ITA': [0,5,[i for i, x in enumerate(dayWeekList) if x == 2][12],114,120,152,226,304,341,358,359],
                'LTU': [0,46,69,[i for i, x in enumerate(dayWeekList) if x == 2][12],120,[i for i, x in enumerate(dayWeekList) if x == 1][22],174,186,226,304,357,358,359],
                'NLD': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],116,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],358],
                'NOR': [0,[i for i, x in enumerate(dayWeekList) if x == 5][11],[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,[i for i, x in enumerate(dayWeekList) if x == 2][19],136,358,359],
                'POL': [0,5,[i for i, x in enumerate(dayWeekList) if x == 1][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,122,134,145,226,304,314,358,359],
                'PRT': [0,[i for i, x in enumerate(dayWeekList) if x == 6][12],114,120,160,226,341,357,358],
                'ROU': [0,1,23,120,[i for i, x in enumerate(dayWeekList) if x == 2][17],170,226,333,334,358,359],
                'RUS': [0,3,4,5,6,53,66,120,128,163,307],
                'SRB': [0,1,6,7,45,46,[i for i, x in enumerate(dayWeekList) if x == 6][17],[i for i, x in enumerate(dayWeekList) if x == 0][17],[i for i, x in enumerate(dayWeekList) if x == 1][17],[i for i, x in enumerate(dayWeekList) if x == 2][17],128,283],
                'SVK': [0,5,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,127,155,240,243,257,273,289,357,358,359],
                'SVN': [0,38,[i for i, x in enumerate(dayWeekList) if x == 2][12],116,120,121,175,226,303,304,358,359],
                'SWE': [0,5,[i for i, x in enumerate(dayWeekList) if x == 6][12],[i for i, x in enumerate(dayWeekList) if x == 2][12],120,124,156,174,175,277,357,358,359,364],
                'SYR': [0,66,106,120,125,187,255,275,278,345,358],
                'TUR': [0,112,120,138,157,158,159,241,253,254,255,256,301],
                'UKR': [0,6,66,120,[i for i, x in enumerate(dayWeekList) if x == 2][17],127,128,[i for i, x in enumerate(dayWeekList) if x == 2][24],235,286,324]}
                
                if countries[country]:
                    country_selected = countries[country]
                else: country_selected = [0,120,358,359] # not found countries
                
                #change id value and debug message holiday
                if len(holiday) == 24:
                    holidays = country_selected
                    for index in sorted(holidays, reverse=True):
                        dayWeekList[index] = 7
                    print "National holidays(DOYs): ",
                    for item in country_selected:
                        print item+1,
            else:
                # if overwriteHolidays is string
                try:
                    if overwriteHolidays is not type(int):
                        overwriteHolidays = map(int, overwriteHolidays)
                except ValueError:
                    overwriteHolidays_day = []
                    for item in overwriteHolidays:
                        day_date = fromDateToDay(item, months_dict)
                        overwriteHolidays_day.append(day_date)
                    overwriteHolidays = overwriteHolidays_day
                    
                country_selected = []
                for item in overwriteHolidays:
                    country_selected.append(item-1)
                if len(holiday) == 24:
                    holidays = country_selected
                    for index in sorted(holidays, reverse=True):
                        dayWeekList[index] = 7
                    print "National holidays(DOYs): ",
                    for item in country_selected:
                        print item+1,
        #second loop: if epwFile is off and overwriteHolidays is on
        if epwFile == None and overwriteHolidays:
            # if overwriteHolidays is string
            try:
                if overwriteHolidays is not type(int):
                    overwriteHolidays = map(int, overwriteHolidays)
            except ValueError:
                overwriteHolidays_day = []
                for item in overwriteHolidays:
                    day_date = fromDateToDay(item, months_dict)
                    overwriteHolidays_day.append(day_date)
                overwriteHolidays = overwriteHolidays_day
            country_selected = []
            for item in overwriteHolidays:
                country_selected.append(item-1)
            if len(holiday) == 24:
                holidays = country_selected
                for index in sorted(holidays, reverse=True):
                    dayWeekList[index] = 7
                print "National holidays(DOYs): ",
                for item in country_selected:
                    print item+1,
        #third condition: if holiday_ is on and epw and/or overwrite are off
        if holiday and (not overwriteHolidays and not epwFile):
            warning = "In this way you do not consider holidays. Please connect epwFile and/or overwriteHolidays"
            w = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(w, warning)
        else: pass
        
        try:
            # nested lists for the whole year
            for n,i in enumerate(dayWeekList):
                if i==0:
                    dayWeekList[n]= sat
                elif i ==1:
                    dayWeekList[n]= sun
                elif i ==2:
                    dayWeekList[n]= mon
                elif i ==3:
                    dayWeekList[n]= tue
                elif i ==4:
                    dayWeekList[n]= wed
                elif i ==5:
                    dayWeekList[n]= thu
                elif i ==6:
                    dayWeekList[n]= fri
                elif i ==7:
                    dayWeekList[n]= holiday
                    
        except: pass
        annualSchedule = list(flatten(dayWeekList))
        
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
        max = HOYS[len(HOYS)-1]
        min = HOYS[0]-1
        
        # print national holidays
        nationalHolidays = []
        if holiday and(epwFile or overwriteHolidays):
            for day in country_selected:
                nationalHolidays.append(fromDayToDate(day, months_dict))
        scheduleValues = annualSchedule[min:max]
        return scheduleValues, nationalHolidays

# import the classes
w = gh.GH_RuntimeMessageLevel.Warning
initCheck = False
if sc.sticky.has_key('ladybug_release'):
    initCheck = True
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = True
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")

#Check the data to make sure it is the correct type
checkData = False
if initCheck == True:
    checkData = checkTheData(_sun, _mon, _tue, _wed, _thu, _fri, _sat)
    if checkData == True:
        if _runIt:
            result = main(_sun, _mon, _tue, _wed, _thu, _fri, _sat, holiday_, _runIt, epwFile_, weekStartWith_, overwriteHolidays_, analysisPeriod_)
            if result != -1:
                scheduleValues, nationalHolidays = result
                print '\nscheduleValues completed!'
                if analysisPeriod_:
                    print "Schedule period: ", analysisPeriod_ 
        else:
            print 'Run..'
    else:
        print 'Please provide all _inputs'