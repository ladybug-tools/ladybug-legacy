# Sunrise Sunset
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Use this component to get information about the sun
-
This component is based on NOAA's research (National Oceanic and Atmospheric Administration) and it uses equations from Astronomical Algorithms, by Jean Meeus.
"The sunrise and sunset results are theoretically accurate to within a minute for locations between +/- 72 latitude, and within 10 minutes outside of those latitudes."
Special thanks goes to the authors of the spreadsheets Solar Calculation and the web page
http://www.esrl.noaa.gov/gmd/grad/solcalc/index.html
-
This component calculates sunrise and sunset per hourly data. The approximation error of OfficialSunriseSunset could be about one-two minutes.
-
Despite this component does not consider the leap day (FEB 29th), results are accurate enough.
-
Provided by Ladybug 0.0.62
    
    Args:
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        _HOYorAnalysisPeriod: Connect: 
        a) a list of HOYs from outputs of the Ladybug_DOY_HOY for specific date;
        b) OR a list of values from 1 to 8760 for the whole year;
        c) OR Ladybug Analysis Period for the whole year.
        _year: A number between -1000 to 3000. The approximations used in these script are very good for years between 1800 and 2100. Results should still be sufficiently accurate for the range from -1000 to 3000.
        
    Returns:
        readMe!: ...
        officialSunriseSunset: It is the time between day and night when there is light outside and the Sun is on the horizon (9050').
        solarNoon: Solar noon is when the sun is at its highest point in the sky each day.
        solarElevationCorrected: Number(s) indicating the sun altitude(s) in degrees for each sun position on the sun path. It consider the atmospheric refraction.
        solarAzimut: Number(s) indicating the sun azimuths in degrees for each sun position on the sun path.
        sunVector: Vector(s) indicating the direction of sunlight for each sun position.
        isSunUp: A list of number. 1 if the sun is up and 0 if the sun is down.
        -
        Use Ladybug Analysis Period or a list of values from 1 to 8760 to generate data for the whole year.
        -
        Try to connect this output to Ladybug 3D Chart to get a daylight chart of your location.
        date: Detailied information for each sun position including date and time.
        sunLightDuration: Duration of sunlight per day expressed in minutes.
        -
        This output is available just for _HOYorAnalysisPeriod type a) and b)
        -
        Try to connect this output to Ladybug_Average Data to create charts of your location using Ladybug_Monthly Bar Chart.
"""

ghenv.Component.Name = "Ladybug_SunriseSunset"
ghenv.Component.NickName = 'Sunrise Sunset'
ghenv.Component.Message = 'VER 0.0.62\nFEB_22_2016'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import math

def checkTheData(location, HOY):
    if location == None \
    and HOY == None:
        checkData = False
    elif location and HOY:
        checkData = False
    else: checkData = True
    return checkData

def sunVectorCalc(azimut, zenit):
    # from polar to cartesian
    x = 100 * math.sin(math.radians(90 - zenit)) * math.cos(math.radians(90 - azimut))
    y = 100 * math.sin(math.radians(90 - zenit)) * math.sin(math.radians(90 - azimut))
    z = 100 * math.cos(math.radians(90 - zenit))
    
    refPoint = rs.AddPoint(x,y,z)
    vector = rs.VectorCreate([0,0,0] , refPoint)
    vector = rs.VectorUnitize(vector)
    return vector

def readLocation(location):
    locationStr = location.split('\n')
    newLocStr = ""
    #clean the idf file
    for line in locationStr:
        if '!' in line:
            line = line.split('!')[0]
            newLocStr  = newLocStr + line.replace(" ", "")
        else:
            newLocStr  = newLocStr + line
    
    newLocStr = newLocStr.replace(';', "")
    site, locationName, latitude, longitude, timeZone, elevation = newLocStr.split(',')
    
    latitude = float(latitude)
    longitude = float(longitude)
    timeZone = float(timeZone)
    
    return latitude, longitude, timeZone

def JDtoTime(hour):
    hourDec = hour * 24
    hours = int(hourDec)
    minute = int(round((hourDec - hours) * 60,0))
    if minute == 60:
        hours += 1
        minute = "00"
    if hours < 10:
        hours = "0" + str(hours)
    if minute == 0:
        minutes = "00"
    elif minute < 10:
        minutes = "0" + str(minute)
    else: minutes = minute
    time = str(hours) + ":" + str(minutes)
    return time

def dateToDOY(month, day):
    doy = math.floor((275 * month)/9) - math.floor((month + 9)/12) + day -30
    
    return doy

def sunCalcPreparation(hour, day, month, year, timeZone):
    # year input
    if year == None:
        year = 2016
    else: year = year_
    
    # Julian day from calendar day
    if (month <= 2):
        year -= 1
        month += 12
    A = math.floor(year/100)
    B = 2 - A + math.floor(A/4)
    
    JulianDay = (math.floor(365.25*(year + 4716)) + math.floor(30.6001*(month+1))\
    + day + B - 1524.5) - timeZone / 24 + hour
    
    # calcTimeJulianCent	
    julianCent = (JulianDay - 2451545.0)/36525.0
    
    # calculate the Geometric Mean Longitude of the Sun
    L0 = 280.46646 + julianCent * (36000.76983 + 0.0003032 * julianCent)
    while (L0 > 360.0):
        L0 -= 360.0
    while (L0 < 0.0):
        L0 += 360.0
    
    # calculate the Geometric Mean Anomaly of the Sun
    M = 357.52911 + julianCent * (35999.05029 - 0.0001537 * julianCent)
    
    # calculate the eccentricity of earth's orbit
    e = 0.016708634 - julianCent * (0.000042037 + 0.0000001267 * julianCent)
    
    # calculate the equation of center for the sun
    CentreSun = math.sin(math.radians(M)) * (1.914602 - julianCent\
    * (0.004817 + 0.000014 * julianCent)) + math.sin(math.radians(2 * M))\
    * (0.019993 - 0.000101 * julianCent) + math.sin(math.radians(3 * julianCent)) * 0.000289
    
    #Sun True Long (deg)
    sunTrueLog = L0 + CentreSun
    
    #Sun True Anom (deg)
    sunTrueAnom = M + CentreSun
    
    #Sun Rad Vector (AUs)
    sunRadVector = (1.000001018 * (1 - e * e))/(1 + e * math.cos(math.radians(sunTrueAnom)))
    
    #Sun App Long (deg)
    sunAppLog = sunTrueLog - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * julianCent))
    
    #Mean Obliq Ecliptic (deg)
    meanObliqEcliptic = 23 + (26 + ((21.448 - julianCent\
    * (46.815 + julianCent * (0.00059 - julianCent * 0.001813)))) / 60) / 60
    
    #Obliq Corr (deg)
    obliqCorr = meanObliqEcliptic + 0.00256 * math.cos(math.radians(125.04 - 1934.136 * julianCent))
    
    #Sun Rt Ascen (deg)
    data1 = math.cos(math.radians(sunAppLog))
    data2 = math.cos(math.radians(obliqCorr))* math.sin(math.radians(sunAppLog))
    
    sunRtAscend = 90 - math.degrees(math.atan2(data1 , data2))
    
    #Sun Declin (deg)
    sunDeclin = math.degrees(math.asin(math.sin(math.radians(obliqCorr)) * math.sin(math.radians(sunAppLog))))
    
    #var y
    varY = math.tan(math.radians(obliqCorr / 2)) * math.tan(math.radians(obliqCorr / 2))
    
    #equation of time
    eqOfTime = 4 * math.degrees(varY * math.sin(2 * math.radians(L0))\
    - 2 * e * math.sin(math.radians(M)) + 4 * e * varY * math.sin(math.radians(M))\
    * math.cos(2 * math.radians(L0)) - 0.5 * varY * varY * math.sin(4 * math.radians(L0))\
    - 1.25 * e * e * math.sin(2 * math.radians(M)))
    
    #returns
    return eqOfTime, sunDeclin

def sunCalcTimeData(day, month, latitude, longitude, timeZone, eqOfTime, sunDeclin):
    try:
        #Solar Noon
        solarNoon = (720 - 4 * longitude - eqOfTime + timeZone * 60) / 1440
        solarNoonTime = JDtoTime(solarNoon)
        
        #HA Sunrise (deg)
        haSunrise = math.degrees(math.acos(math.cos(math.radians(90.833))\
        / (math.cos(math.radians(latitude)) * math.cos(math.radians(sunDeclin)))\
        - math.tan(math.radians(latitude)) * math.tan(math.radians(sunDeclin))))
        
        #Solar Noon
        solarNoon = (720 - 4 * longitude - eqOfTime + timeZone * 60) / 1440
        solarNoonTime = JDtoTime(solarNoon)
        
        #Sunrise Time (LST)
        sunriseTime = solarNoon - haSunrise * 4 / 1440
        time1 = JDtoTime(sunriseTime)
        if (sunriseTime*24 <= 0):
            time1 = "up"
        else:
            time1 = time1
        
        #Sunset Time (LST)
        sunsetTime = solarNoon + haSunrise * 4 / 1440
        time2 = JDtoTime(sunsetTime)
        if sunsetTime*24 >= 24:
            time2 = "up"
        else:
            time2 = time2
            
        #Sunlight Duration (minutes)
        sunLightDuration = int(round(haSunrise * 8,1))
        
        #solve the issue of extreme location
    except:
        solarNoonTime = solarNoonTime
        if ((latitude > 66.4) and (dateToDOY(month, day) < 79 or dateToDOY(month, day) > 267)):
            time1 = "down"
            time2 = "down"
            sunLightDuration = "0"
            sunriseTime = 9999
            sunsetTime = 9999
        elif ((latitude > 66.4) and (dateToDOY(month, day) > 79 or dateToDOY(month, day) < 267)):
            time1 = "up"
            time2 = "up"
            sunLightDuration = "1440"
            sunriseTime = 99
            sunsetTime = 99
        elif ((latitude < -66.4) and (dateToDOY(month, day) < 83 or dateToDOY(month, day) > 263)):
            time1 = "up"
            time2 = "up"
            sunLightDuration = "1440"
            sunriseTime = 99
            sunsetTime = 99
        elif ((latitude < -66.4) and (dateToDOY(month, day) > 83 or dateToDOY(month, day) < 263)):
            time1 = "down"
            time2 = "down"
            sunLightDuration = "0"
            sunriseTime = 9999
            sunsetTime = 9999
    
    #returns
    return time1, time2, solarNoonTime, sunriseTime, sunsetTime, sunLightDuration

def sunCalcSunData(hour, latitude, longitude, timeZone, eqOfTime, sunDeclin):
    #True Solar Time (min)
    trueSolarTime = (hour * 1440 + eqOfTime + 4 * longitude - 60 * timeZone) % 1440
    
    #Hour Angle (deg)
    if trueSolarTime / 4 <0:
        hourAngle = trueSolarTime / 4 + 180
    else: hourAngle = trueSolarTime / 4 - 180
    
    #Solar Zenith Angle (deg)
    solarZenit = math.degrees(math.acos(math.sin(math.radians(latitude))\
    * math.sin(math.radians(sunDeclin)) + math.cos(math.radians(latitude))\
    * math.cos(math.radians(sunDeclin)) * math.cos(math.radians(hourAngle))))
    
    #Solar Elevation Angle (deg)
    solarElevationAngle = 90 - solarZenit
    
    #Approx Atmospheric Refraction (deg)
    if solarElevationAngle > 85:
        apprAtmospRef = 0
    elif solarElevationAngle > 5:
        apprAtmospRef = (58.1 / math.tan(math.radians(solarElevationAngle)) - 0.07\
        / (math.tan(math.radians(solarElevationAngle))**3) + 0.000086 / (math.tan(math.radians(solarElevationAngle))**5)) / 3600
    elif solarElevationAngle > -0.575:
        apprAtmospRef = (1735 + solarElevationAngle * (-518.2 + solarElevationAngle\
        * (103.4 + solarElevationAngle * (-12.79 + solarElevationAngle * 0.711)))) / 3600
    else: apprAtmospRef = (-20.772 / math.tan(math.radians(solarElevationAngle))) / 3600
    
    #Solar Elevation corrected for atm refraction (deg)
    solarElevationCorrected = solarElevationAngle + apprAtmospRef
    
    #Solar Azimut
    if hourAngle > 0:
        solarAzimut = (math.degrees(math.acos(((math.sin(math.radians(latitude))\
        * math.cos(math.radians(solarZenit))) - math.sin(math.radians(sunDeclin)))\
        / (math.cos(math.radians(latitude)) * math.sin(math.radians(solarZenit))))) + 180) % 360
    else: solarAzimut = (540 - math.degrees(math.acos(((math.sin(math.radians(latitude))\
    * math.cos(math.radians(solarZenit))) - math.sin(math.radians(sunDeclin)))\
    / (math.cos(math.radians(latitude)) * math.sin(math.radians(solarZenit)))))) % 360
    
    #vector Rhino geometry
    vector = sunVectorCalc(solarAzimut, solarElevationCorrected)
    
    #returns
    return solarElevationCorrected, solarAzimut, vector

def main():
    if readLocation(_location)[0] == 90 or readLocation(_location)[0] == -90:
        warning = "Latitude should be in range (-89.99 , 89.99)"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
        
    # output lists
    officialSunriseSunset = []
    solarElevationCorrected = []
    isSunUp = []
    sunVector = []
    solarNoon = []
    solarAzimut = []
    date = []
    sunLightDuration = []
    # function lists
    eqOfTime = []
    eqOfTimeSet = []
    eqOfTimeRise = []
    eqOfTimeDuration = []
    sunDeclin = []
    sunDeclinSet = []
    sunDeclinRise = []
    sunDeclinDuration = []
    sunRiseTime = []
    sunSetTime = []
    hourJd = []
    sunset = []
    sunrise = []
    
    try:
        # run sunCalc function
        day = []
        month = []
        hour = []
        
        for hoy in _HOYorAnalysisPeriod:
            d, m, t = lb_preparation.hour2Date(hoy, True)
            day.append(d)
            month.append(m + 1)
            hour.append(t)
            date.append(lb_preparation.hour2Date(hoy))
        # hourJd function
        for item in hour:
            hourJd.append(item / 24)
            
        for i in range(0, len(_HOYorAnalysisPeriod)):
            eqOfTime.append(sunCalcPreparation(hourJd[i], day[i], month[i], year_, readLocation(_location)[2])[0])
            sunDeclin.append(sunCalcPreparation(hourJd[i], day[i], month[i], year_, readLocation(_location)[2])[1])
            #function for sun data
            dataSun = sunCalcSunData(hourJd[i], readLocation(_location)[0], readLocation(_location)[1],\
            readLocation(_location)[2], eqOfTime[i], sunDeclin[i])
            # output Sun
            solarElevationCorrected.append(dataSun[0])
            solarAzimut.append(dataSun[1])
            sunVector.append(dataSun[2])
            
            ##Sunlight Duration per day (minutes)
            eqOfTimeDuration.append(sunCalcPreparation(1, day[i], month[i], year_, readLocation(_location)[2])[0])
            sunDeclinDuration.append(sunCalcPreparation(1, day[i], month[i], year_, readLocation(_location)[2])[1])
            #function for sun data
            dataSunDuration = sunCalcTimeData(day[i], month[i], readLocation(_location)[0], readLocation(_location)[1],\
            readLocation(_location)[2], eqOfTimeDuration[i], sunDeclinDuration[i])
            sunLightDuration.append(dataSunDuration[5])
            
            # logical conditions for hoursJd
            if ((readLocation(_location)[0] > 66.4) and (dateToDOY(month[i], day[i]) < 79 or dateToDOY(month[i], day[i]) > 267)):
                sunRisehourJd = 0.5
                sunSethourJd = 0.5
            elif ((readLocation(_location)[0] > 66.4) and (dateToDOY(month[i], day[i]) > 79 or dateToDOY(month[i], day[i]) < 267)):
                sunRisehourJd = 0
                sunSethourJd = 1
                
            elif ((readLocation(_location)[0] < -66.4) and (dateToDOY(month[i], day[i]) < 83 or dateToDOY(month[i], day[i]) > 263)):
                sunRisehourJd = 0
                sunSethourJd = 1
            elif ((readLocation(_location)[0] <- 66.4) and (dateToDOY(month[i], day[i]) > 83 or dateToDOY(month[i], day[i]) < 263)):
                sunRisehourJd = 0.5
                sunSethourJd = 0.5
                
            elif (readLocation(_location)[0] <= 66.4) or (readLocation(_location)[0] >= -66.4):
                sunRisehourJd = 0
                sunSethourJd = 1
                
            # Sunrise
            eqOfTimeRise.append(sunCalcPreparation(sunRisehourJd, day[i], month[i], year_, readLocation(_location)[2])[0])
            sunDeclinRise.append(sunCalcPreparation(sunRisehourJd, day[i], month[i], year_, readLocation(_location)[2])[1])
            
            dataSunRise = sunCalcTimeData(day[i], month[i], readLocation(_location)[0], readLocation(_location)[1],\
            readLocation(_location)[2], eqOfTimeRise[i], sunDeclinRise[i])
            sunRiseTime.append(dataSunRise[0])
            sunrise.append(dataSunRise[3])
            
            # Sunset
            eqOfTimeSet.append(sunCalcPreparation(sunSethourJd, day[i], month[i], year_, readLocation(_location)[2])[0])
            sunDeclinSet.append(sunCalcPreparation(sunSethourJd, day[i], month[i], year_, readLocation(_location)[2])[1])
            
            dataSunSet = sunCalcTimeData(day[i], month[i], readLocation(_location)[0], readLocation(_location)[1],\
            readLocation(_location)[2], eqOfTimeSet[i], sunDeclinSet[i])
            sunSetTime.append(dataSunSet[1])
            sunset.append(dataSunSet[4])
            
            if sunRiseTime[i] == "down":
                officialSunriseSunset.append(sunRiseTime[i] + " , " + "down")
            else:
                officialSunriseSunset.append(sunRiseTime[i] + " , " + sunSetTime[i])
            
            # solarNoon
            solarNoon.append(dataSunSet[2])
            
        #generate isSunUp list
        for i in range (0, len(hour)):
            
            if sunrise[i] == 9999 or sunset[i] == 9999:
                sunUp = 0
                isSunUp.append(sunUp)
            elif sunrise[i] == 99 or sunset[i] == 99:
                sunUp = 1
                isSunUp.append(sunUp)
            elif hour[i] <= (24*sunrise[i]) or hour[i] >= (24*sunset[i]):
                sunUp = 0
                isSunUp.append(sunUp)
            else:
                sunUp = 1
                isSunUp.append(sunUp)
                
    except:
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(_HOYorAnalysisPeriod, 1)
        day = []
        month = []
        hour = []
        for hoy in HOYS:
            d, m, t = lb_preparation.hour2Date(hoy, True)
            day.append(d)
            month.append(m+1)
            hour.append(t)
            date.append(lb_preparation.hour2Date(hoy))
            
        # hourJd function
        for item in hour:
            hourJd.append(item / 24)
        
        for i in range(0, len(HOYS)):
            eqOfTime.append(sunCalcPreparation(hourJd[i], day[i], month[i], year_, readLocation(_location)[2])[0])
            sunDeclin.append(sunCalcPreparation(hourJd[i], day[i], month[i], year_, readLocation(_location)[2])[1])
            #function for sun data
            dataSun = sunCalcSunData(hourJd[i], readLocation(_location)[0], readLocation(_location)[1],\
            readLocation(_location)[2], eqOfTime[i], sunDeclin[i])
            # output Sun
            solarElevationCorrected.append(dataSun[0])
            solarAzimut.append(dataSun[1])
            sunVector.append(dataSun[2])
            
            # logical conditions for hoursJd
            if ((readLocation(_location)[0] > 66.4) and (dateToDOY(month[i], day[i]) < 79 or dateToDOY(month[i], day[i]) > 267)):
                sunRisehourJd = 0.5
                sunSethourJd = 0.5
            elif ((readLocation(_location)[0] > 66.4) and (dateToDOY(month[i], day[i]) > 79 or dateToDOY(month[i], day[i]) < 267)):
                sunRisehourJd = 0
                sunSethourJd = 1
                
            elif ((readLocation(_location)[0] < -66.4) and (dateToDOY(month[i], day[i]) < 83 or dateToDOY(month[i], day[i]) > 263)):
                sunRisehourJd = 0
                sunSethourJd = 1
            elif ((readLocation(_location)[0] <- 66.4) and (dateToDOY(month[i], day[i]) > 83 or dateToDOY(month[i], day[i]) < 263)):
                sunRisehourJd = 0.5
                sunSethourJd = 0.5
                
            elif (readLocation(_location)[0] <= 66.4) or (readLocation(_location)[0] >= -66.4):
                sunRisehourJd = 0
                sunSethourJd = 1
                
            # Sunrise
            eqOfTimeRise.append(sunCalcPreparation(sunRisehourJd, day[i], month[i], year_, readLocation(_location)[2])[0])
            sunDeclinRise.append(sunCalcPreparation(sunRisehourJd, day[i], month[i], year_, readLocation(_location)[2])[1])
            
            dataSunRise = sunCalcTimeData(day[i], month[i], readLocation(_location)[0], readLocation(_location)[1],\
            readLocation(_location)[2], eqOfTimeRise[i], sunDeclinRise[i])
            sunRiseTime.append(dataSunRise[0])
            sunrise.append(dataSunRise[3])
            
            # Sunset
            eqOfTimeSet.append(sunCalcPreparation(sunSethourJd, day[i], month[i], year_, readLocation(_location)[2])[0])
            sunDeclinSet.append(sunCalcPreparation(sunSethourJd, day[i], month[i], year_, readLocation(_location)[2])[1])
            
            dataSunSet = sunCalcTimeData(day[i], month[i], readLocation(_location)[0], readLocation(_location)[1],\
            readLocation(_location)[2], eqOfTimeSet[i], sunDeclinSet[i])
            sunSetTime.append(dataSunSet[1])
            sunset.append(dataSunSet[4])
            
            if sunRiseTime[i] == "down":
                officialSunriseSunset.append(sunRiseTime[i] + " , " + "down")
            else:
                officialSunriseSunset.append(sunRiseTime[i] + " , " + sunSetTime[i])
            
            # solarNoon
            solarNoon.append(dataSunSet[2])
            
        #generate isSunUp list
        for i in range (0, len(hour)):
            
            if sunrise[i] == 9999 or sunset[i] == 9999:
                sunUp = 0
                isSunUp.append(sunUp)
            elif sunrise[i] == 99 or sunset[i] == 99:
                sunUp = 1
                isSunUp.append(sunUp)
            elif hour[i] <= (24*sunrise[i]) or hour[i] >= (24*sunset[i]):
                sunUp = 0
                isSunUp.append(sunUp)
            else:
                sunUp = 1
                isSunUp.append(sunUp)
                
    return officialSunriseSunset, solarElevationCorrected, solarAzimut, solarNoon, isSunUp, sunVector, date, sunLightDuration
#import the classes
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
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    lb_preparation = sc.sticky["ladybug_Preparation"]()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")

#Check the data to make sure it is the correct type
checkData = False
if initCheck == True:
    checkData = checkTheData(_location, _HOYorAnalysisPeriod)
    
    if checkData == False :
        result = main()
        if result != -1:
            officialSunriseSunset, solarElevationCorrected, solarAzimut, solarNoon ,isSunUp, sunVector, date, sunLightDuration = result
            print 'calculation completed!'
    else:
        print 'Please provide all _inputs'