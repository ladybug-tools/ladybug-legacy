# thermal comfort indices
# By Djordje Spasic
# djordjedspasic@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate different thermal comfort indices

Provided by Ladybug 0.0.58
    
    input:
        _comfortIndex: Choose one of the comfort indices:
                       0 - HI (Heat Index)
                       1 - humidex (humidity index)
                       2 - DI (Discomfort Index)
                       3 - WCI (Wind Chill Index)
                       4 - WCT (Wind Chill Temperature)
                       5 - WBGT (Wet-Bulb Globe Temperature) indoors
                       6 - WBGT (Wet-Bulb Globe Temperature) outdoors
                       7 - TE (Effective Temperature)
                       8 - AT (Apparent Temperature)
                       9 - TS (Thermal Sensation)
                       10 - ASV (Actual Sensation Vote)
                       11 - MRT (Mean Radiant Temperature)
                       12 - Iclp (Predicted Insulation Index Of Clothing)
                       13 - HR (Heart Rate)
                       14 - DhRa (Dehydration Risk)
        _location: Input data from Ladybug's "Import epw" "location" output, or create your own location data with Ladybug's "Construct Location" component
        _dryBulbTemperature: Hourly Dry Bulb Temperature (air temperature), in Celsius
        dewPointTemperature_: Hourly Dew Point Temperature, in Celsius
                              If not supplied, it will be calculated from dryBulbTemperature and relativeHumidity
        _relativeHumidity: Hourly Relative Humidity, in percent (from 0% to 110%)
        windSpeed_: Hourly Wind Speed, in meters/second
                    If not supplied, default value of 0.3 m/s is used.
        globalHorizontalRadiation_:  Total amount of direct and diffuse solar radiation received on a horizontal surface, in Wh/m2.
                                     If not supplied, default value of 0 Wh/m2 is used.
        totalSkyCover_: Amount of sky dome in tenths covered by clouds or obscuring phenomena, in tenths of coverage (from 1 to 10). For example: 1 is 1/10 covered. 10 is total coverage (10/10).
                        If not supplied, dfault value of 8 (8/10) is used.
        metabolicRate_: Input metabolic rate in mets. If not supplied 2.32 will be used as default value
                        Here are some of the examples of metabolic rates mets based on activity:
                        Activity - met
                        -------------------
                        Reclining  - 0.8
                        Seating - 1.0
                        Car driving - 1.2
                        Sedentary activity (office, dwelling, school, laboratory) - 1.2
                        Standing - 1.2
                        Standing (light activity: shopping, laboratory, light industry) - 1.6
                        Standing (medium activity: shop assistant, domestic work) - 2.0
                        Walking (5 km/h) - 3.4
                        ...
                        Washing dishes standing - 2.5
                        Domestic work (raking leaves on the lawn) - 2.9
                        Domestic work (washing by hand and ironing) - 2.9
                        Iron and steel (ramming the mould with a pneumatic hammer) - 3.0
                        Building industry (brick laying) - 2.2
                        Building industry (forming the mould) - 3.1
                        Building industry (loading a wheelbarrow with stones and mortar) - 4.7
                        Forestry (cutting with chainsaw) - 3.5
                        Forestry (working with an axe) - 8.5
                        Agriculture (digging with a spade) - 6.5
                        ...
                        Volleyball - 4.0
                        Golf - 5.0
                        Softball - 5.0
                        Gymnastics - 5.5
                        Aerobic Dancing - 6.0
                        Swimming - 6.0
                        Ice skating - 6.2
                        Bicycling (15 km/h) - 4.0
                        Bicycling (20km/h) - 6.2
                        Skiing (9 km/h) - 7.0
                        Backpacking - 7.0
                        Basketball - 7.0
                        Handball - 8.0
                        Hockey - 8.0
                        Racquetball - 8.0
                        Soccer - 8.0
                        Running (8 km/h) - 8.5
                        Running (15km/h) - 9.5
        age_: An age of the person. This input is only important for HR (Heart Rate) index.
              If not supplied, default value of 30 will be used.
        gender_: Input 0 or "male"  or  1 or "female". This input is only important for HR (Heart Rate) index.
                 If not supplied, "male" will be used as a default value.
        acclimated_: Input True if person in subject is acclimatized, or False if it's not. This input is only important for DhRa (Dehydration risk).
                     If no value is supplied, False (unacclimated) will be used by default.
        
        HOY_: An hour of the year for which you would like to calculate thermal indices.  This must be a value between 1 and 8760.
	          This input will override the analysisPeriod_ input below.
        analysisPeriod_: An optional analysis period from the Analysis Period component. 
        _runIt: ...
        
    output:
        readMe!: ...
"""

ghenv.Component.Name = "Ladybug_Thermal Comfort Indices"
ghenv.Component.NickName = 'ThermalComfortIndices'
ghenv.Component.Message = 'VER 0.0.58\nDEC_28_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math

if sc.sticky.has_key('ladybug_release'):
    lb_preparation = sc.sticky["ladybug_Preparation"]()

else:
    warningM = "First please let the Ladybug fly..."
    print warningM
    level = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(level, warningM)



def getLocationData(location):

    if location:
        try:
            # code from Ladybug "Explode Location" component of Mostapha Sadeghipour Roudsari
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
            
            latitude, longitude, timeZone, elevation = float(latitude), float(longitude), float(timeZone), float(elevation)
            validLocationData = True
            printMsg = "ok"
        
        except:
            # something is wrong with "_location" input (the input is not from Ladybug 'Import epw' component 'location' ouput)
            latitude = longitude = timeZone = locationName = None
            validLocationData = False
            printMsg = "Something is wrong with '_location' input."
    else:
        latitude = longitude = timeZone = locationName = None
        validLocationData = False
        printMsg = "Please input 'location' ouput of Ladybug 'Import epw' component, or make your own location data using Ladybug's 'Contruct Location' and plug it into '_location' input of this component."

    return latitude, longitude, timeZone, locationName, validLocationData, printMsg


def getWeatherData(Ta, Tdp, rh, ws, SR, N, M, age, gender):

    if (len(Ta) == 0) or (Ta[0] is ""):
        Ta = Tdp = rh = ws = SR = N = M = age = gender = None
        printMsg = "Please input _dryBulbTemperature"
        validWeatherData = False
        return Ta, Tdp, rh, ws, SR, N, M, age, gender, validWeatherData, printMsg
    if (len(rh) == 0) or (rh[0] is ""):
        Ta = Tdp = rh = ws = SR = N = M = age = gender = None
        printMsg = "Please input _relativeHumidity"
        validWeatherData = False
        return Ta, Tdp, rh, ws, SR, N, M, age, gender, validWeatherData, printMsg
    
    if M == None:
        M = 2.3196*58.2  # default value - 135 W/m2
    else:
        M = M*58.2  # convert mets to W/m2
    
    if age == None or age < 0:
        age = 30
    
    if gender == None:
        gender = "male"
    elif gender == 0 or gender.lower() == "male":
        gender = "male"
    elif gender == 1 or gender.lower() == "female":
        gender = "female"
    else:
        gender = "male"

    # combination of lists(inputed from "Ladybug import epw" component" and single values:
    try:
        TaLlength = len(Ta)
    except:
        TaLlength = 1
    try:
        TdpLlength = len(Tdp)
    except:
        TdpLlength = 1
    try:
        rhLlength = len(rh)
    except:
        rhLlength = 1
    try:
        wsLlength = len(ws)
    except:
        wsLlength = 1
    try:
        SRLlength = len(SR)
    except:
        SRLlength = 1
    try:
        NLlength = len(N)
    except:
        NLlength = 1

    maximalListLength = max(TaLlength, TdpLlength, rhLlength, wsLlength, SRLlength, NLlength)

    # at least one of inputed dryBulbTemperature_, relativeHumidity_ comes from "Ladybug import epw" component". The rest are single values
    if maximalListLength == 8767:
        
        for list in Ta, Tdp, rh, ws, SR, N:
            try:
                if len(list) == maximalListLength:
                    inputList = list
            except:
                pass
        
        if len(Ta) == 1:
            try:
                item = float(Ta[0])
                Ta = inputList[:7]
                for i in range(maximalListLength-7):
                    Ta.append(item)
            except:
                pass
        
        # this is for calculating Tdp , in case dewPointTemperature_ has not been inputted
        if len(rh) == 1:
            try:
                item = float(rh[0])
                rh = inputList[:7]
                for i in range(maximalListLength-7):
                    rh.append(item)
            except:
                pass
    
        if (len(Tdp) == 0) or (Tdp[0] is ""):
            nm = 0
            try:
                Tdp = inputList[:7]
                for i in range(maximalListLength-7):
                    dewPoint = dewPointTemperature(Ta[i+7], rh[i+7])
                    Tdp.append(dewPoint)
            except:
                pass
    
        if (len(ws) == 0) or (ws[0] is ""):
            try:
                ws = inputList[:7]
                for i in range(maximalListLength-7):
                    ws.append(0.3) # default value 0.3 m/s
            except:
                pass
    
        if (len(SR) == 0) or (SR[0] is ""):
            try:
                SR = inputList[:7]
                for i in range(maximalListLength-7):
                    SR.append(0) # default value 0 Wh/m2(%)
            except:
                pass
    
        if (len(N) == 0) or (N[0] is ""):
            try:
                N = inputList[:7]
                for i in range(maximalListLength-7):
                    N.append(8) # default value 8 tens (%)
            except:
                pass

        if len(Ta) == maximalListLength:
            Ta = Ta[7:]
        else:  # Ta is not a list, but a single value
            item = Ta[0]
            Ta = []
            for i in range(maximalListLength-7):
                Ta.append(float(item))
        if len(Tdp) == maximalListLength:
            Tdp = Tdp[7:]
        else:  # Tdp is not a list, but a single value
            item = Tdp[0]
            Tdp = []
            for i in range(maximalListLength-7):
                Tdp.append(float(item))
        if len(rh) == maximalListLength:
            rh = rh[7:]
        else:  # rh is not a list, but a single value
            item = rh[0]
            rh = []
            for i in range(maximalListLength-7):
                rh.append(float(item))
        if len(ws) == maximalListLength:
            ws = ws[7:]
        else:  # ws is not a list, but a single value
            item = ws[0]
            ws = []
            for i in range(maximalListLength-7):
                ws.append(float(item))
        if len(SR) == maximalListLength:
            SR = SR[7:]
        else:  # SR is not a list, but a single value
            item = SR[0]
            SR = []
            for i in range(maximalListLength-7):
                SR.append(float(item))
        if len(N) == maximalListLength:
            N = N[7:]
        else:  # N is not a list, but a single value
            item = N[0]
            N = []
            for i in range(maximalListLength-7):
                N.append(float(item))
        item = M
        M = []
        for i in range(maximalListLength-7):
            M.append(float(item))
                
        printMsg = "ok"
        validWeatherData = True
        return Ta, Tdp, rh, ws, SR, N, M, age, gender, validWeatherData, printMsg


    # all inputs come as a single value (maximalListLength != 8767)
    elif maximalListLength == 1:
        TaL = [float(Ta[0]) for i in range(8760)]
        rhL = [float(rh[0]) for i in range(8760)]

        if (len(Tdp) == 0) or (Tdp[0] is ""):
            dewPoint = dewPointTemperature(float(Ta[0]), float(rh[0]))
            TdpL = [dewPoint for i in range(8760)]
        else:
            TdpL = [float(Tdp[0]) for i in range(8760)]
        
        if (len(ws) == 0) or (ws[0] is ""):
            wsL = [0.3 for i in range(8760)] # default value 0.3 m/s
        else:
            wsL = [float(ws[0]) for i in range(8760)]
        
        if (len(SR) == 0) or (SR[0] is ""):
            SRL = [0 for i in range(8760)] # default value 0 W/m2
        else:
            SRL = [float(SR[0]) for i in range(8760)]
        
        if (len(N) == 0) or (N[0] is ""):
            NL = [8 for i in range(8760)] # default value 8 (tens)
        else:
            NL = [float(N[0]) for i in range(8760)]
        
        ML = [float(M) for i in range(8760)]
        
        printMsg = "ok"
        validWeatherData = True

        return TaL, TdpL, rhL, wsL, SRL, NL, ML, age, gender, validWeatherData, printMsg

    # some inputs come as a single value, but some as list of at least 2 values (list of 2 values not supported)
    else:
        Ta = Tdp = rh = ws = SR = N = M = None
        printMsg = "Something is wrong with your dryBulbTemperature_, relativeHumidity_, globalHorizontalRadiation_ input data."
        validWeatherData = False
        return Ta, Tdp, rh, ws, SR, N, M, age, gender, validWeatherData, printMsg


#angle units conversion
def degreesToRadians(deg):
    return deg*0.0174532925 

def radiansToDegrees(R):
    return R*57.2957795

# temperature units conversion
def celsiusToFahrenheit(Tc):
    Tf = (Tc * (9/5)) + 32
    return Tf

def fahrenheitToCelsius(Tf):
    Tc = (Tf-32)*(5/9)
    return Tc
    
def celsiusToKelvin(Tc):
    Tk = Tc + 273.15
    return Tk

# thermal comfort indices
def heatIndex(Ta, rh):
    # formula by (NWS) National Weather Service
    Tf = celsiusToFahrenheit(Ta)

    if Tf < 80:
        HI_f = 0.5 * (Tf + 61.0 + ((Tf-68.0)*1.2) + (rh*0.094))
    else:
        HI_f = -42.379 + 2.04901523*Tf + 10.14333127*rh - \
             0.22475541*Tf*rh -6.83783*(10**(-3))*(Tf**(2)) - \
             5.481717*(10**(-2))*(rh**(2)) + \
             1.22874*(10**(-3))*(Tf**(2))*(rh) + 8.5282*(10**(-4))*(Tf)*(rh**(2)) - \
             1.99*(10**(-6))*(Tf**(2))*(rh**(2))
        if (Tf >= 80) and (Tf <= 112) and (rh < 13):
            adjust = ((13-rh)/4) * math.sqrt((17-abs(Tf-95))/17)
            HI_f = HI_f-adjust
        elif (Tf >= 80) and (Tf <= 87) and (rh > 85):
            adjust = ((rh-85)/10) * ((87-Tf)/5)
            HI_f = HI_f+adjust
    if HI_f < 80:
        effectHI = 0
        comfortable = 1
    elif HI_f >= 80 and HI_f < 90:
        effectHI = 1
        comfortable = 0
    elif HI_f >= 90 and HI_f < 105:
        effectHI = 2
        comfortable = 0
    elif HI_f >= 105 and HI_f < 130:
        effectHI = 3
        comfortable = 0
    elif HI_f >= 130:
        effectHI = 4
        comfortable = 0

    HI_c = fahrenheitToCelsius(HI_f)

    return HI_c, effectHI, comfortable


def dewPointTemperature(Ta, rh):
    # MET4 and MET4A calculation of dew point temperature.
    # limits:
    # uncertainty in the calculated dew point temperature: +/- 0.4°C
    # for Tc in range:  0°C < Tc < 60°C  
    # for Tdp in range:  0°C < Tdp < 50°C   
    a = 17.27
    b = 237.7
    rh = rh/100  # 0.01 < rh < 1.00
    Tdp = (b * ( ((a*Ta)/(b+Ta))+math.log(rh) ))/(a-( ((a*Ta)/(b+Ta))+math.log(rh) ))  # in Celius degrees

    return Tdp

def Humidex(Ta, Tdp):
    # formula by Environment Canada
    dewpointK = celsiusToKelvin(Tdp)  # to Kelvin
    e = 6.11 * math.exp(5417.7530 * ((1/273.16) - (1/dewpointK)))
    h = (0.5555)*(e - 10.0)
    humidex = Ta + h

    if humidex < 30:
        effectHumidex = 0
        comfortable = 1
    elif humidex >=30 and humidex < 35:
        effectHumidex = 1
        comfortable = 0
    elif humidex >=35 and humidex < 40:
        effectHumidex = 2
        comfortable = 0
    elif humidex >=40 and humidex < 45:
        effectHumidex = 3
        comfortable = 0
    elif humidex >=45 and humidex < 54:
        effectHumidex = 4
        comfortable = 0
    elif humidex >= 54:
        effectHumidex = 5
        comfortable = 0

    return humidex, effectHumidex, comfortable


def discomfortIndex(Ta, rh):
    # also called "Thom's Index"
    # formula from: Thom, E.C. (1959): The discomfort index. Weather wise, 12: 57–60.
    DI = Ta - (0.55 - 0.0055*rh)*(Ta - 14.5)
    
    if DI < 21:
        effectDI = 0
        comfortable = 1
    elif DI >= 21 and DI < 24:
        effectDI = 1
        comfortable = 0
    elif DI >= 24 and DI <= 27:
        effectDI = 2
        comfortable = 0
    elif DI > 27 and DI <= 29:
        effectDI = 3
        comfortable = 0
    elif DI > 29 and DI <= 32:
        effectDI = 4
        comfortable = 0
    elif DI > 32:
        effectDI = 5
        comfortable = 0
    
    return DI, effectDI, comfortable


def windChillIndex(Ta, ws):
    # formula by Gregorczuk 1976
    WCI = (10*math.sqrt(ws) + 10.45 - ws)*(33 - Ta)*1.163
    
    # Thermal sensations of man wearing clothing with insulation of 4 clo (heavy polar equipment):
    if WCI >= 2326:
        effectWCI = -4
        comfortable = 0
    elif WCI < 2326 and WCI >= 1628.2:
        effectWCI = -3
        comfortable = 0
    elif WCI < 1628.2 and WCI >= 930.4:
        effectWCI = -2
        comfortable = 0
    elif WCI < 930.4 and WCI >= 581.5:
        effectWCI = -1
        comfortable = 0
    elif WCI < 581.5 and WCI >= 232.6:
        effectWCI = 0
        comfortable = 1
    elif WCI < 232.6 and WCI >= 116.3:
        effectWCI = 1
        comfortable = 0
    elif WCI < 116.3 and WCI >= 58.3:
        effectWCI = 2
        comfortable = 0
    elif WCI < 58.3:
        effectWCI = 3
        comfortable = 0
    return WCI, effectWCI, comfortable


def windChillTemperature(Ta, ws):
    # formula by Environment Canada (corresponds to National Weather Service (NSW) Wind chill formula used in U.S.)
    ws_km_h = ws * 3.6   # convert m/s to km/h wind speed

    Twc = 13.12 + 0.6215*Ta - 11.37*(ws_km_h**0.16) + 0.3965*Ta*(ws_km_h**0.16)   # in Celius degrees

    if Twc >= 0:
        effectTwc = 0
        comfortable = 1
    elif Twc < 0 and Twc >= -9:
        effectTwc = -1
        comfortable = 0
    elif Twc < -9 and Twc >= -27:
        effectTwc = -2
        comfortable = 0
    elif Twc < -27 and Twc >= -39:
        effectTwc = -3
        comfortable = 0
    elif Twc < -39 and Twc >= -47:
        effectTwc = -4
        comfortable = 0
    elif Twc < -47 and Twc >= -54:
        effectTwc = -5
        comfortable = 0
    elif Twc < -54:
        effectTwc = -6
        comfortable = 0
    return Twc, effectTwc, comfortable


def effectiveTemperature(Ta, ws, rh, SR):
    if ws <= 0.2:
        # formula by Missenard
        TE = Ta - 0.4*(Ta - 10)*(1-rh/100)
    elif ws > 0.2:
        # modified formula by Gregorczuk (WMO, 1972; Hentschel, 1987)
        TE = 37 - ( (37-Ta)/(0.68-(0.0014*rh)+(1/(1.76+1.4*(ws**0.75)))) ) - (0.29 * Ta * (1-0.01*rh))
    
    # Radiative-effective temperature
    ac = 31  # default value
    TRE = TE + ((1 - 0.01*ac)*SR) * ((0.0155 - 0.00025*TE) - (0.0043 - 0.00011*TE))
    
    if TRE < 1:
        effectTE = -4
        comfortable = 0
    elif TRE >= 1 and TE < 9:
        effectTE = -3
        comfortable = 0
    elif TRE >= 9 and TE < 17:
        effectTE = -2
        comfortable = 0
    elif TRE >= 17 and TE < 21:
        effectTE = -1
        comfortable = 0
    elif TRE >= 21 and TE < 23:
        effectTE = 0
        comfortable = 1
    elif TRE >= 23 and TE < 27:
        effectTE = 1
        comfortable = 0
    elif TRE >= 27:
        effectTE = 2
        comfortable = 0

    return TRE, effectTE, comfortable


def apparentTemperature(Ta, ws, rh):

    e = (rh/100) * 6.105 * math.exp((17.27*Ta)/(237.7+Ta))
    AT = Ta + (0.33*e) - (0.70*ws) - 4.00
    
    # Apparel effects by: Norms of apparent temperature in Australia, Aust. Met. Mag., 1994, Vol 43, 1-16:
    if AT > 40:
        effectAT = 4
        comfortable = 0
    elif AT > 35 and AT <= 40:
        effectAT = 3
        comfortable = 0
    elif AT > 30 and AT <= 35:
        effectAT = 2
        comfortable = 0
    elif AT > 25 and AT <= 30:
        effectAT = 1
        comfortable = 0
    elif AT > 20 and AT <= 25:
        effectAT = 0
        comfortable = 1
    elif AT > 15 and AT <= 20:
        effectAT = -1
        comfortable = 0
    elif AT > 10 and AT <= 15:
        effectAT = -2
        comfortable = 0
    elif AT > 5 and AT <= 10:
        effectAT = -3
        comfortable = 0
    elif AT > 0 and AT <= 5:
        effectAT = -4
        comfortable = 0
    elif AT > -5 and AT <= 0:
        effectAT = -5
        comfortable = 0
    elif AT <= -5:
        effectAT = -6
        comfortable = 0

    return AT, effectAT, comfortable


def thermalSensation(Ta, ws, rh, SR, Tground):
    # formula from: Givoni, Noguchi, Issues and problems in outdoor comfort research, in: Proceedings of the PLEA’2000 Conference, Cambridge, UK, July 2000
    TS=1.7+0.1118*Ta+0.0019*SR-0.322*ws-0.0073*rh+0.0054*Tground

    if TS < 2:
        effectTS = -3
        comfortable = 0
    elif TS >= 2 and TS < 3:
        effectTS = -2
        comfortable = 0
    elif TS >= 3 and TS < 4:
        effectTS = -1
        comfortable = 0
    elif TS >= 4 and TS < 5:
        effectTS = 0
        comfortable = 1
    elif TS >= 5 and TS < 6:
        effectTS = 1
        comfortable = 0
    elif TS >= 6 and TS < 7:
        effectTS = 2
        comfortable = 0
    elif TS >= 7:
        effectTS = 3
        comfortable = 0

    return TS, effectTS, comfortable


def actualSensationModel(Ta, ws, rh, S):
    # Actual Sensation Model for whole Europe 
    # formula by RUROS project.
    ASV = 0.049*Ta + 0.001*S - 0.051*ws + 0.014*rh - 2.079
    
    #Classification of human thermal sensation according to TS levels and ASV scale
    #Givoni and Noguchi, 2000; Nikolopoulou et al., 2004
    if ASV < -2:
        effectASV = -2
        comfortable = 0
    elif ASV >= -2 and ASV < -1:
        effectASV = -1
        comfortable = 0
    elif ASV >= -1 and ASV <= 1:
        effectASV = 0
        comfortable = 1
    elif ASV > 1 and ASV <= 2:
        effectASV = 1
        comfortable = 0
    elif ASV > 2:
        effectASV = 2
        comfortable = 0

    return ASV, effectASV, comfortable


def noaaSolarCalculator(latitude, longitude, timeZone, month, day, hour):
    # by NOAA Earth System Research Laboratory
    # NOAA defines longitude and time zone as positive to the west:
    timeZone = -timeZone
    longitude = -longitude
    DOY = int(lb_preparation.getJD(month, day))
    minute = 0  # default
    sc = 0  # default
    gamma = (2*math.pi)/365*(DOY-1+((hour-12)/24))
    eqtime = 229.18*(0.000075 + 0.001868*math.cos(gamma) - 0.032077*math.sin(gamma) - 0.014615*math.cos(2*gamma) - 0.040849*math.sin(2*gamma))
    declAngle = 0.006918 - 0.399912*math.cos(gamma) + 0.070257*math.sin(gamma) - 0.006758*math.cos(2*gamma) + 0.000907*math.sin(2*gamma) - 0.002697*math.cos(3*gamma) + 0.00148*math.sin(3*gamma)
    time_offset = eqtime-4*longitude+60*timeZone
    tst = hour *60 + minute + sc / 60 + time_offset
    solarHangle = (tst / 4) - 180
    
    # solar zenith angle
    solarZenithR = math.acos(math.sin(math.radians(latitude)) * math.sin(declAngle) + math.cos(math.radians(latitude)) * math.cos(declAngle) * math.cos(math.radians(solarHangle)))
    solarZenithD = math.degrees(solarZenithR)
    if solarZenithD > 90:
        solarZenithD = 90
    elif solarZenithD < 0:
        solarZenithD = 0
    
    # solar altitude angle
    solarAltitudeD = 90 - solarZenithD

    # solar azimuth angle
    solarAzimuthR = - (math.sin(math.radians(latitude)) * math.cos(solarZenithR) - math.sin(declAngle)) / (math.cos(math.radians(latitude)) * math.sin(solarZenithR))
    solarAzimuthR = math.acos(solarAzimuthR)
    solarAzimuthD = math.degrees(solarAzimuthR)
    
    return solarZenithD, solarAzimuthD, solarAltitudeD


def solarRadiationNudeMan(Kglob, hSl):
    # formula from: Bioclimatic principles of recreation and tourism in Poland, 2nd edition, Blazejczyk, Kunert, 2011 (MENEX_2005 model)
    Kt = Kglob / (-0.0015*(hSl**3) + 0.1796*(hSl**2) + 9.6375*hSl - 11.9)
    
    ac = 31  # default value
    ac_ = 1 - 0.01*ac
    
    if hSl <= 12:
        Rprim = ac_*(0.0014*(Kglob**2) + 0.476*Kglob - 3.8)
    elif hSl > 12 and Kt <= 0.8:
        Rprim = 0.2467*ac_*(Kglob**0.9763)
    elif hSl > 12 and Kt >0.8 and Kt <=1.05:
        Rprim = 3.6922*ac_*(Kglob**0.5842)
    elif hSl > 12 and Kt > 1.05 and Kt <=1.2:
        Rprim = 43.426*ac_*(Kglob**0.2326)
    elif hSl > 12 and Kt >1.2:
        Rprim = 8.9281*ac_*(Kglob**0.4861)
        
    if Rprim < 0:
        Rprim = 0
    
    return Rprim


def groundTemperature(Ta, N):
    # formula from: Assessment of bioclimatic differentiation of Poland. Based on the human heat balance, Geographia Polonica, Matzarakis, Blazejczyk, 2007
    N100 = N *10 #converting weather data totalSkyCover from 0 to 10% to 0 to 100%

    if (N100 == None) or (N100 >= 80):
        Tground = Ta
    elif (N100 < 80) and (Ta >= 0):
        Tground = 1.25*Ta
    elif (N100 < 80) and (Ta < 0):
        Tground = 0.9*Ta

    return Tground


def VapourPressure(Ta, rh):
    # formula by ITS-90 formulations for vapor pressure, frostpoint temperature, dewpoint temperature, and enhancement factors in the range –100 to +100 c, Thunder Scientific Corporation, Albuquerque, NM, Bob Hardy
    TaK = Ta + 273.15   # convert to Kelvins
    
    TS90coefficients = [-2.8365744*(10**(3)), -6.028076559*(10**(3)), 1.954263612*(10**(1)), -2.737830188*(10**(-2)), 1.6261698*(10**(-5)), 7.0229056*(10**(-10)), -1.8680009*(10**(-13)), 2.7150305]
    e_s = TS90coefficients[7]*math.log(TaK)

    for i in range(7):
        e_s += TS90coefficients[i]*(TaK**(i-2))

    es = math.exp(e_s)  # in Pa

    es = (es*0.01*rh)/100  # convert to hPa
    
    return es


def meanRadiantTemperature(Ta, Tground, Rprim, e):
    # formula by Man-ENvironment heat EXchange model (MENEX_2005)
    Lg = 5.5 *(10**(-8)) * ((273 + Tground)**(4))
    La = 5.5*(10**(-8)) *((273 + Ta)**(4)) *(0.82 - 0.25*(10**(-0.094*0.75*e)))

    MRT = (((Rprim + 0.5*Lg + 0.5*La) / (0.95*5.667*(10**(-8))))**(0.25)) - 273

    return MRT


def wbgt_indoors(Ta, ws, rh, e, MRT, Tdp):
    # WBGT indoor formula by Bernard
    # formula from: "Calculating Workplace WBGT from Meteorological Data: A Tool for Climate Change Assessment", Lemke, Kjellstrom, 2012
    ed = 0.6106 * math.exp(17.27 * Tdp / (237.7 + Tdp))
    step = 0.02  # lowering the step value increases precision
    Tpwb = Tdp + step
    McPherson_1 = 1
    McPherson_2 = 1
    while Tpwb <= Ta and ((McPherson_1 > 0 and McPherson_2 > 0) or (McPherson_1 < 0 and McPherson_2 <0)):
        ew = 0.6106 * math.exp(17.27 * Tpwb / (237.7 + Tpwb))
        McPherson_1 = McPherson_2
        McPherson_2 = 1556*ed - 1.484*ed*Tpwb - 1556*ew + 1.484*ew*Tpwb + 101*(Ta - Tpwb)
        Tpwb = Tpwb + step

    if (ws > 3):
        WBGTid = 0.7*Tpwb + 0.3*Ta
    elif (ws >= 0.3) and (ws <= 3):
        WBGTid = 0.67 * Tpwb + 0.33 * Ta - 0.048*math.log10(ws) * (Ta - Tpwb)
    elif (ws < 0.3):
        ws = 0.3
        WBGTid = 0.67 * Tpwb + 0.33 * Ta - 0.048*math.log10(ws) * (Ta - Tpwb)
    WBGT_f = celsiusToFahrenheit(WBGTid)

    # Suggested actions and Impact Prevention by Environmental Health Section, Dwight D. Eisenhower Medical Center:
    if WBGT_f < 80:
        effectWBGT = 0
        comfortable = 1
    elif WBGT_f >= 80 and WBGT_f < 82:
        effectWBGT = 1
        comfortable = 0
    elif WBGT_f >= 82 and WBGT_f < 85:
        effectWBGT = 2
        comfortable = 0
    elif WBGT_f >=85 and WBGT_f < 88:
        effectWBGT = 3
        comfortable = 0
    elif WBGT_f >=88 and WBGT_f < 90:
        effectWBGT = 4
        comfortable = 0
    elif WBGT_f >= 90:
        effectWBGT = 5
        comfortable = 0

    return WBGTid, effectWBGT, comfortable


def wbgt_outdoors(Ta, ws, rh, e, MRT):
    # WBGT outdoor formula from Heat stress and occupational health and safety – spatial and temporal differentiation, K. Blazejczyk, J.Baranowski, A. Blazejczyk, Miscellanea geographica – regional studies on development, Vol. 18, No. 1, 2014, 
    Tw = 1.885 + 0.3704*Ta + 0.4492*e
    Tg = 2.098 - 2.561*ws + 0.5957*Ta + 0.4017*MRT
    WBGTout = 0.7*Tw + 0.2*Tg + 0.1*Ta
    WBGT_f = celsiusToFahrenheit(WBGTout)

    # Suggested actions and Impact Prevention by Environmental Health Section, Dwight D. Eisenhower Medical Center:
    if WBGT_f < 80:
        effectWBGT = 0
        comfortable = 1
    elif WBGT_f >= 80 and WBGT_f < 82:
        effectWBGT = 1
        comfortable = 0
    elif WBGT_f >= 82 and WBGT_f < 85:
        effectWBGT = 2
        comfortable = 0
    elif WBGT_f >=85 and WBGT_f < 88:
        effectWBGT = 3
        comfortable = 0
    elif WBGT_f >=88 and WBGT_f < 90:
        effectWBGT = 4
        comfortable = 0
    elif WBGT_f >= 90:
        effectWBGT = 5
        comfortable = 0

    return WBGTout, effectWBGT, comfortable


def predictedInsulationIndexOfClothing(Ta, ws, M):
    #  total insulation of clothing and the surrounding air layer by Burton and Edholm (1955)
    It = (0.082*(91.4 - (1.8*Ta + 32)) / (0.01724*M))
    # insulation of the surrounded air layer by Fourt and Hollies (1970)
    Ia = 1/(0.61+1.9*(ws**0.5))
    
    Iclp = It - Ia
    
    if Iclp > 4.0:
        effectIclp = -4
        comfortable = 1
    elif Iclp > 3.0 and Iclp <= 4.0:
        effectIclp = -3
        comfortable = 0
    elif Iclp > 2.0 and Iclp <= 3.0:
        effectIclp = -2
        comfortable = 0
    elif Iclp > 1.20 and Iclp <= 2.0:
        effectIclp = -1
        comfortable = 0
    elif Iclp > 0.80 and Iclp <= 1.20:
        effectIclp = 0
        comfortable = 1
    elif Iclp > 0.30 and Iclp <= 0.80:
        effectIclp = 1
        comfortable = 0
    elif Iclp <= 0.30:
        effectIclp = 2
        comfortable = 0
    
    return Iclp, effectIclp, comfortable

def heartRates(age, gender):
    #Resting Heart Rates for Man taken from: http://www.topendsports.com/testing/heart-rate-resting-chart.htm
    if gender == "male":
        if age <= 25:
            HRrates = [73,82,90]
        elif age > 25 and age <= 35:
            HRrates = [74,82,90]
        elif age > 35 and age <= 45:
            HRrates = [75,83,90]
        elif age > 45 and age <= 55:
            HRrates = [76,84,90]
        elif age > 55 and age <= 65:
            HRrates = [75,82,90]
        elif age > 65:
            HRrates = [73,80,90]
    elif gender == "female":
        if age <= 25:
            HRrates = [78,85,90]
        elif age > 25 and age <= 35:
            HRrates = [76,83,90]
        elif age > 35 and age <= 45:
            HRrates = [78,85,90]
        elif age > 45 and age <= 55:
            HRrates = [77,84,90]
        elif age > 55 and age <= 65:
            HRrates = [77,84,90]
        elif age > 65:
            HRrates = [76,84,90]
    
    return HRrates


def heartRate(Ta, e, M, HRrates):
    #formula by Fuller, Brouha 1966
    HR = 22.4 + 0.18*M + 0.25*(5*Ta + 2.66*e)
    HR = round(HR)
    
    if HR < HRrates[0]:
        effectHR = 0
        comfortable = 1
    elif HR >= HRrates[0] and HR < HRrates[1]:
        effectHR = 1
        comfortable = 0
    elif HR >= HRrates[1] and HR < HRrates[2]:
        effectHR = 2
        comfortable = 0
    elif HR >= HRrates[2]:
        effectHR = 3
        comfortable = 0
    
    return HR, effectHR, comfortable


def clothingInsulation(Ta):
    
    if Ta < -30:
        Icl = 3.0
    elif Ta > 25:
        Icl = 0.6
    else:
        Icl = 1.691 - 0.0436*Ta
    
    return Icl


def meanSkinTemperature(Ta, ws, rh, MRT, Icl, M):
    
    Ts = (26.4 + 0.02138*MRT + 0.2095*Ta - 0.0185*rh - 0.009*ws) + 0.6*(Icl - 1) + 0.00128*M
    return Ts  # in °C


def turbulentExchangeOfLatentHeat(Ta, ws, Ts, Icl, e_, M):
    # Turbulent exchange of latent heat (evaporation - mE) in W/m2
    
    p = 1000  # barometricpressure in hPa, default value
    he = Ta*(6*(10**(-5))*Ta - 2*(10**(-5))*p + 0.011) + 0.02*p - 0.773
    
    hc = 0.013*p - 0.04*Ta - 0.503
    
    vprim = 1.1 #m/s default value (for man movement 4km/h)
    d = math.sqrt(ws+vprim)
    
    if Ts < 22:
        w = 0.002
    elif Ts >= 22 and Ts <= 36.5:
        w = 1.031/(37.5-Ts)- 0.065
    elif Ts > 36.5:
        w = 1.0
    
    if ws >= 0.2:
        vcor = ws
    elif ws < 0.2:
        vcor = 0.2
    d_ = 0.53/ (Icl *(1-0.27*math.exp(0.4*math.log(vcor+vprim))))
    Ie = hc*d_ / (hc*(d + d_))
    
    esk = math.exp(0.058*Ts + 2.003)
    
    mE = he*d*w*Ie*(e_-esk) - 0.42*(M - 58.0) + 5.04
    
    return mE


def DehydrationRiskRates(acclimated):
    if acclimated:
        # for acclimated subject:
        dehydrationRiskRates = [780,1040]
    elif not acclimated:
        # for non-acclimated subject:
        dehydrationRiskRates = [520,650]
    
    return dehydrationRiskRates


def dehydrationRisk(Epot, acclimated, dehydrationRiskRates):
    # formula from MENEX_2005 model
    # water loss
    SW = -2.6*Epot  # in g/hour
    
    if SW < dehydrationRiskRates[0]:
        effectSW = 0
        comfortable = 1
    elif SW >= dehydrationRiskRates[0] and SW <= dehydrationRiskRates[1]:
        effectSW = 1
        comfortable = 0
    elif SW > dehydrationRiskRates[1]:
        effectSW = 2
        comfortable = 0
    
    return SW, effectSW, comfortable


def extractDataFromHOY(HOY):
    #function from Ladybug "Day_Month_Hour_Calculator" component by Mostapha Sadeghipour Roudsari
    day = []
    month = []
    hour = []
    date = []
    for hoy in HOY:
        d, m, t = lb_preparation.hour2Date(hoy, True)
        day.append(d)
        month.append(m + 1)
        hour.append(t)
        date.append(lb_preparation.hour2Date(hoy))
    
    return day, month, hour, date


def HOYsDaysMonthsHoursFromHOY_analysisPeriod(HOY, analysisPeriod):
    if (HOY):
        day, month, hour, date = extractDataFromHOY(HOY)
        HOYs = HOY
        newAnalysisPeriod = [(month[0], day[0], hour[0]),(month[-1], day[-1], hour[-1])]
    
    elif not (HOY) and (len(analysisPeriod)!=0) and (analysisPeriod[0]!=None):
        HOYs, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod_, 1)
        newAnalysisPeriod = analysisPeriod
    
    else:  # no "HOY_" nor "analysisPeriod_" inputted. Use annual data.
        HOYs = range(1,8761)
        newAnalysisPeriod = [(1, 1, 1),(12, 31, 24)]
        HOYs, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod_, 1)  # print first string in "readMe!"
    
    days = []
    months = []
    hours = []
    for hoy in HOYs:
        day, month, hour, date = extractDataFromHOY([hoy])
        days.append(day[0])
        months.append(month[0])
        hours.append(hour[0])
    
    return HOYs, days, months, hours, newAnalysisPeriod


def createHeaders(comfortIndex, Ta, Tdp, rh, ws, SR, N, HRrates, dehydrationRiskRates, locationName):

    for data in Ta, Tdp, rh, ws, SR, N:
        if "key:location/dataType/units/frequency/startsAt/endsAt" in data:
            header = data[:7]
            break
        else:
            # default header
            header = ["key:location/dataType/units/frequency/startsAt/endsAt", "none", "none", "none", "Hourly", (1, 1, 1), (1, 1, 2)]
    
    # change (or just replace it with the same current) locationName
    header[1] = locationName
    
    comfortIndexValue = []
    comfortIndexCategory = []
    comfortableOrNot = []
    IndicesEmptyLists = [comfortIndexValue, comfortIndexCategory, comfortableOrNot]
    
    
    IndiceTitles = [
    ["Heat Index - values", "Heat Index - categories", "Heat Index - comfortable(1) or not(0)"],
    ["Humidex - values", "Humidex - categories", "Humidex - comfortable(1) or not(0)"],
    ["Discomfort Index - values", "Discomfort Index - categories", "Discomfort Index - comfortable(1) or not(0)"],
    ["Wind Chill Index - values", "Wind Chill Index - categories", "Wind Chill Index - comfortable(1) or not(0)"],
    ["Wind Chill Temperature - values", "Wind Chill Temperature - categories", "Wind Chill Temperature - comfortable(1) or not(0)"],
    ["Wet-Bulb Globe Temperature (indoors) - values", "Wet-Bulb Globe Temperature (indoors) - categories", "Wet-Bulb Globe Temperature (indoors) - comfortable(1) or not(0)"],
    ["Wet-Bulb Globe Temperature (outdoors) - values", "Wet-Bulb Globe Temperature (outdoors) - categories", "Wet-Bulb Globe Temperature (outdoors) - comfortable(1) or not(0)"],
    ["Effective Temperature - values", "Effective Temperature - categories", "Effective Temperature - comfortable(1) or not(0)"],
    ["Apparent Temperature - values", "Apparent Temperature - categories", "Apparent Temperature - comfortable(1) or not(0)"],
    ["Thermal Sensation - values", "Thermal Sensation - categories ", "Thermal Sensation - comfortable(1) or not(0)"],
    ["Actual Sensation Vote - values", "Actual Sensation Vote - categories", "Actual Sensation Vote - comfortable(1) or not(0)"],
    ["Mean Radiant Temperature - values"],
    ["Predicted Insulation Index Of Clothing - values", "Predicted Insulation Index Of Clothing - categories", "Predicted Insulation Index Of Clothing - comfortable(1) or not(0)"],
    ["Heart Rate - values", "Heart Rate - categories", "Heart Rate - comfortable(1) or not(0)"],
    ["Dehydration Risk - values", "Dehydration Risk - categories", "Dehydration Risk - comfortable(1) or not(0)"],
    ]
    
    IndiceUnitsCat = [
    ["°C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot", "Boolean value"],
    ["°C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"],
    ["°C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"],
    ["W/m2", "-4 = Extreme frost,  -3 = Frosty,  -2 = Cold,  -1 = Cool,  0 = Comfortable,  1 = Warm, 2 = Hot, 3 = Extremely hot", "Boolean value"],
    ["°C", "-6 = Extreme risk of frostbite,  -5 = Very high risk of frostbite,  -4 = High risk of frostbite,  -3 = Moderate risk of frostbite,  -2 = Low risk of frostbite,  -1 = Very low risk of frostbite, 0 = No risk of frostbite", "Boolean value"],
    ["°C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"],
    ["°C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"],
    ["°C", "-4 = Very cold,  -3 = Cold,  -2 = Cool,  -1 = Fresh,  0 = Comfortable,  1 = Warm, 2 = Hot", "Boolean value"],
    ["°C", "Appareal increments:\n-5 = Overcoat, cap,  -4 = Overcoat,  -3 = Coat and sweater,  -2 = Sweater,  -1 = Thin sweater,  0 = Normal office wear,  1 = Cotton pants,  2 = Light undershirt,  3 = Shirt, shorts,  4 = Minimal cloths. Sun protection as needed", "Boolean value"],
    ["unit-less", "-3 = Very cold, -2 = Quite cold,  -1 = Cold,  0 = Comfortable,  1 = Hot,  2 = Quite hot,  3 = Very hot", "Boolean value"],
    ["unit-less", "-2 = Very cold,  -1 = Cold,  0 = Comfortable,  1 = Hot,  2 = Very hot", "Boolean value"],
    ["°C"],
    ["clo", "-4 = Arctic, -3 = Very cold,, -2 = Cold,  -1 = Cool,  0 = Comfortable,  1 = Warm,  2 = Very warm", "Boolean value"],
    ["beats per minute", "0 = Average,  1 = Below Average,  2 = Poor,  3 = Warning", "Boolean value"],
    ["g/hour", "0 = No risk,  1 = Dehydration warning,  2 = Dehydration hazard", "Boolean value"]
    ]
    
    for i in range(len(IndiceTitles[comfortIndex])):
        for item in header:
            IndicesEmptyLists[i].append(item)
        IndicesEmptyLists[i][2] = IndiceTitles[comfortIndex][i]  # change header's title
        IndicesEmptyLists[i][3] = IndiceUnitsCat[comfortIndex][i]  # change header's units or categories
        IndicesEmptyLists[i][5] = newAnalysisPeriod[0]  # change header's from to date
        IndicesEmptyLists[i][6] = newAnalysisPeriod[1]  # change header's from to date

    outputNickNames = [
    ["HI", "HIlevel", "HIcomfortableOrNot", "HIpercentComfortable", "HIpercentHotExtreme", "HIpercentColdExtreme"],
    ["humidex", "humidexLevel", "humidexComfortableOrNot", "humidexPercentComfortable", "humidexPercentHotExtreme", "_"],
    ["DI", "DIlevel", "DIcomfortableOrNot", "DIpercentComfortable", "DIpercentHotExtreme", "_"],
    ["WCI", "WCIlevel", "WCIcomfortableOrNot", "WCIpercentComfortable", "WCIpercentHotExtreme", "WCTpercentColdExtreme"],
    ["WCT", "WCTlevel", "WCTcomfortableOrNot", "WCTpercentComfortable", "_", "WCTpercentColdExtreme"],
    ["WBGTindoor", "WBGTlevel", "WBGTcomfortableOrNot", "WBGTpercentComfortable", "WBGTpercentHotExtreme", "_"],
    ["WBGToutdoor", "WBGTlevel", "WBGTcomfortableOrNot", "WBGTpercentComfortable", "WBGTpercentHotExtreme", "_"],
    ["TE", "TElevel", "TEcomfortableOrNot", "TEpercentComfortable", "TEpercentHotExtreme", "TEpercentColdExtreme"],
    ["AT", "ATlevel", "ATcomfortableOrNot", "ATpercentComfortable", "ATpercentHotExtreme", "ATpercentColdExtreme"],
    ["TS", "TSlevel", "TScomfortableOrNot", "TSpercentComfortable", "TSpercentHotExtreme", "TSpercentColdExtreme"],
    ["ASV", "ASVlevel", "ASVcomfortableOrNot", "ASVpercentComfortable", "ASVpercentHotExtreme", "ASVpercentColdExtreme"],
    ["MRT", "_", "_", "_", "_", "_"],
    ["Iclp", "IclpLevel", "IclpComfortableOrNot", "IclpPercentComfortable", "IclpPercentHotExtreme", "IclpPercentColdExtreme"],
    ["HR", "HRlevel", "HRcomfortableOrNot", "HRpercentComfortable", "HRpercentHotExtreme", "HRpercentColdExtreme"],
    ["DhRa", "DhRaLevel", "DhRaComfortableOrNot", "DhRaPercentComfortable", "DhRaPercentHotExtreme", "DhRaPercentColdExtreme"]
    ] # outputNames = outputNickNames

    outputDescriptions = [
    ["Heat Index (°C) - the human-perceived increase in air temperature due to humidity increase. It is used by National Weather Service (NSW).\nHeat Index is calculated for shade values. Exposure to full sunshine can increase heat index values by up to 8°C (14°F)",  #comfortIndexValues
    
    "Each number (from 0 to 4) represents a certain HI thermal sensation category. With categories being the following:\
    \n- category 0 (<26.6°C): Satisfactory temperature. Can continue with activity.\
    \n- category 1 (26.6-32.2°C): Caution: fatigue is possible with prolonged exposure and activity. Continuing activity could result in heat cramps.\
    \n- category 2 (32.2-40.5°C): Extreme caution: heat cramps and heat exhaustion are possible. Continuing activity could result in heat stroke.\
    \n- category 3 (40.5-54.4°C): Danger: heat cramps and heat exhaustion are likely; heat stroke is probable with continued activity.\
    \n- category 4 (>54.4°C): Extreme danger: heat stroke is imminent.",  # comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning HI temperature is < 26.6°C)",  #comfortableOrNot
    
    "Percentage of time, during which HI is < 26.6°C",  #percentComfortable
    
    "Percentage of time, during which HI is > 54.4°C",  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Humidex (°C) - the human-perceived increase in air temperature due to Dew point temperature increase. Used by Canadian Meteorologist service.",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain humidex thermal sensation category. With categories being the following:\
    \n- category 0 (<30°C): Little or no discomfort\
    \n- category 1 (30-35°C): Noticeable discomfort\
    \n- category 2 (35-40°C): Evident discomfort\
    \n- category 3 (40-45°C): Intense discomfort; avoid exertion\
    \n- category 4 (45-54°C): Dangerous discomfort\
    \n- category 5 (>54°C): Heat stroke probable",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning humidex is < 30°C)",  # comfortableOrNot
    
    "Percentage of time chosen for analysis period, during which humidex is < 26.6°C",  # percentComfortable
    
    "Percentage of time chosen for analysis period, during which humidex is > 54.4°C", # percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Discomfort Index (or Thom's Index)(°C) - the human-perceived increase in air temperature due to himidity increase.",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain DI thermal sensation category. With categories being the following:\
    \n- category 0 (<21°C): No discomfort\
    \n- category 1 (21-24°C): Under 50% of population feels discomfort\
    \n- category 2 (24-27°C): Over 50% of population feels discomfort\
    \n- category 3 (27-29°C): Most of population suffers discomfort\
    \n- category 4 (29-32°C): Everyone feels stress\
    \n- category 5 (>32°C): State of medical emergency",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning DI temperature is < 21°C)",  #comfortableOrNot
    
    "Percentage of time chosen for analysis period, during which DI is < 21°C",  #percentComfortable
    
    "Percentage of time chosen for analysis period, during which DI is > 32°C",  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Wind Chill Index (W/m2) - qualifies thermal sensations of man in wintertime. It is especially useful at low and very low air temperature and at high wind speed. WCI values are not equal to the actual heat loss from the human organism.",  #comfortIndexValues
    
    "Each number (from -4 to 3) represents a certain WCI thermal sensation category. With categories being the following:\
    \n- category -4 (≥2326 W/m2) Extreme frost\
    \n- category -3 (1628.2-2326 W/m2) Frosty\
    \n- category -2 (930.4-1628.2 W/m2) Cold\
    \n- category -1 (581.5-930.4 W/m2) Cool\
    \n- category 0 (232.6-581.5 W/m2) Comfortable\
    \n- category 1 (116.3-232.6 W/m2) Warm\
    \n- category 2 (58.3-116.3 W/m2) Hot\
    \n- category 3 (<58.3 W/m2) Extremely hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning WCI is in range: 232.6 to 581.5 W/m2)",  #comfortableOrNot
    
    "Percentage of time, during which WCI is < 232.6-581.5 W/m2",  #percentComfortable
    
    "Percentage of time, during which WCI is < 58.3 W/m2",  #percentHotExtreme
    
    "Percentage of time, during which WCI is ≥ 2326 W/m2"]  #percentColdExtreme
    
    ,
    
    ["Wind Chill Temperature (°C) - the perceived decrease in air temperature felt by the body on exposed skin due to the flow of air.\nIt's used by both National Weather Service (NSW) in US and Canadian Meteorologist service. This is new (2001 by JAG/TI) WCT.\nWind chill index does not take into account the effect of sunshine.\nBright sunshine may reduce the effect of wind chill (make it feel warmer) by 6 to 10 units(°C or °F)!\nWindchill temperature is defined only for temperatures at or below 10°C (50°F) and for wind speeds at and above 1.3 m/s (or 4.8 km/h or 3.0 mph)",  #comfortIndexValues
    
    "Each number (from -4 to 0) represents a certain WCT thermal sensation category. With categories being the following:\
    \n- category 0 (>0°C) No discomfort. No risk of frostbite for most people\
    \n- category -1 (0-(-9)°C) Slight increase in discomfort. Low risk of frostbite for most people\
    \n- category -2 (-9-(-27)°C) Risk of hypothermia if outside for long periods without adequate protection. Low risk of frostbite for most people\
    \n- category -3 (-27-(-39)°C) Risk of hypothermia if outside for long periods without adequate clothing or shelter from wind and cold. Increasing risk of frostbite for most people in 10 to 30 minutes of exposure\
    \n- category -4 (-39-(-47)°C) Risk of hypothermia if outside for long periods without adequate clothing or shelter from wind and cold. High risk of frostbite for most people in 5 to 10 minutes of exposure\
    \n- category -5 (-47-(-54)°C) Serious risk of hypothermia if outside for long periods without adequate clothing or shelter from wind and cold. High risk of frostbite for most people in 2 to 5 minutes of exposure\
    \n- category -6 (<-54°C) Danger! Outdoor conditions are hazardous. High risk of frostbite for most people in 2 minutes of exposure or less",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that there is danger of frostbite, 1 there is not danger of frostbite at that hour (meaning WCT temperature is in range: >-27°C)",  #comfortableOrNot
    
    "Percentage of time, during which there is low risk of frostbite (DI is > -27°C)",  #percentComfortable
    " ",  #percentHotExtreme
    
    "Percentage of time, during which there is high risk of frostbite (DI is < -54°C)"]  #percentColdExtreme
    
    ,
    
    ["Wet-Bulb Globe Temperature(°C) - perceived indoor temperature.\nIt is used by the U.S. military, American Academy of Pediatrics and OSHA (Occupational Safety and Health Administration) to obtain measure of heat stress involved in manual labor jobs of soldiers, construction workers, steel mill workers, firefighters, law enforcement officers, athletes...",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain WBGT thermal sensation category. With categories being the following:\
    \n- category 0 (<26°C): No change in activity is required.\
    \n- category 1 (26-27.7°C): No change in activity is required. Use discretion when planning heavy activities for unacclimated person.\
    \n- category 2 (27.7-29.4°C): Outdoor physical activities and strenuous exercise should be limited to 50 minutes per hour. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 3 (29.4-31.1°C): Outdoor physical activities and strenuous exercise should be limited to 40 minutes per hour. You should unblouse trouser legs. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 4 (31.1-32.2°C): Outdoor physical activities and strenuous exercise should be limited to 30 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 5 (>32.2°C): Outdoor physical activities and strenuous exercise should be limited to 20 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning WBGT temperature is in range: 29.4 to 31.1°C)",  #comfortableOrNot
    
    "Percentage of time, during which WBGT is < 26°C",  #percentComfortable
    
    "Percentage of time, during which WBGT is > 32.2°C",  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Wet-Bulb Globe Temperature(°C) - perceived outdoor temperature.\nIt is used by the U.S. military, American Academy of Pediatrics and OSHA (Occupational Safety and Health Administration) to obtain measure of heat stress involved in manual labor jobs of soldiers, construction workers, steel mill workers, firefighters, law enforcement officers, athletes...",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain WBGT thermal sensation category. With categories being the following:\
    \n- category 0 (<26°C): No change in activity is required.\
    \n- category 1 (26-27.7°C): No change in activity is required. Use discretion when planning heavy activities for unacclimated person.\
    \n- category 2 (27.7-29.4°C): Outdoor physical activities and strenuous exercise should be limited to 50 minutes per hour. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 3 (29.4-31.1°C): Outdoor physical activities and strenuous exercise should be limited to 40 minutes per hour. You should unblouse trouser legs. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 4 (31.1-32.2°C): Outdoor physical activities and strenuous exercise should be limited to 30 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 5 (>32.2°C): Outdoor physical activities and strenuous exercise should be limited to 20 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning WBGT temperature is in range: 29.4 to 31.1°C)",  #comfortableOrNot
    
    "Percentage of time, during which WBGT is < 26°C",  #percentComfortable
    
    "Percentage of time, during which WBGT is > 32.2°C",  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Effective Temperature (°C) - influence of air temperature, wind speed, relative humidity of air, and solar radiation on man indoors and outdoors (both in shade and under the sun)",  #comfortIndexValues
    
    "Each number (from -4 to 2) represents a certain TE thermal sensation category. With categories being the following:\
    \n- category -4 (<1°C): Very cold\
    \n- category -3 (1-9°C): Cold\
    \n- category -2 (9-17°C): Cool\
    \n- category -1 (17-21°C): Fresh\
    \n- category 0 (21-23°C): Comfortable\
    \n- category 1 (23-27°C): Warm\
    \n- category 2 (>27°C): Hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning TE temperature is in range: 21 to 23°C)",  #comfortableOrNot
    
    "Percentage of time, during which TE is < 21-23°C",  #percentComfortable
    
    "Percentage of time, during which TE is > 27°C",  #percentHotExtreme
    
    "Percentage of time, during which TE is < 1°C"]  #percentColdExtreme
    
    ,
    
    ["Apparent Temperature (°C) - combines wind chill and heat index to give one single perceived outdoor temperature for Australian climate.\nNon-radiation formula from ABM(Australian Bureau of Meteorology).",  #comfortIndexValues
    
    "Each number (from -5 to 4) represents a certain AT thermal sensation category. With categories being the following:\
    \nAppareal increments:\
    \n- category 4 (>40°C): Minimal; sun protection required\
    \n- category 3 (35-40°C): Minimal; sun protection as needed\
    \n- category 2 (30-35°C): Short sleeve, shirt and shorts\
    \n- category 1 (25-30°C): Light undershirt\
    \n- category 0 (20-25°C): Cotton-type slacks (pants)\
    \n- category -1 (15-20°C): Normal office wear\
    \n- category -2 (10-15°C): Thin or sleeveless sweater\
    \n- category -3 (5-10°C): Sweater. Thicker underwear\
    \n- category -4 (0-5°C): Coat and sweater\
    \n- category -5 (-5-0°C): Overcoat. Wind protection as needed\
    \n- category -6 (<-5°C): Overcoat. Head insulation. Heavier footwear",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning AT temperature is in range: 20 to 25°C)",  #comfortableOrNot
    
    "Percentage of time, during which AT is < 20-25°C",  #percentComfortable
    
    "Percentage of time, during which AT is > 40°C",  #percentHotExtreme
    
    "Percentage of time, during which AT is < -5°C"]  #percentColdExtreme
    
    ,
    
    ["Thermal Sensation (index) (unit-less) - and index which predicts sensation of satisfaction/dissatisfaction under the prevailing outdoor climatic conditions.\nIt is applicable to Japan only (with exception of Hokaido and central parts of Honshu island).",  #comfortIndexValues
    
    "Each number (from -3 to 3) represents a certain TS thermal sensation category. With categories being the following:\
    \n- category -3 (<2): Very cold\
    \n- category -2 (2-3): Quite cold\
    \n- category -1 (3-4): Cold\
    \n- category 0 (4-5): Comfort\
    \n- category 1 (5-6): Hot\
    \n- category 2 (6-7): Quite Hot\
    \n- category 3 (>7): Very hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning TS index is in range: 4 to 5)",  #comfortableOrNot
    
    "Percentage of time, during which TS is 4 to 5",  #percentComfortable
    
    "Percentage of time, during which TS is > 7",  #percentHotExtreme
    
    "Percentage of time, during which TS is < 2"]  #percentColdExtreme
    
    ,
    
    ["Actual Sensation Vote (unit-less) - is an index which estimates human thermal sensation based on the empirical data gathered from field and human surveys, interviews and questionnaires in 7 European cities (RUROS project: Cambridge, Sheffield, Milan, Fribourg, Kassel, Athens, Thessaloniki). ASV index is valid for Europe only.",  #comfortIndexValues
    
    "Each number (from -2 to 2) represents a certain ASV thermal sensation category. With categories being the following:\
    \n- category -2 (<-2): Very cold\
    \n- category -1 (-2-(-1)): Cold\
    \n- category 0 (-1-1): Comfort\
    \n- category 1 (1-2): Hot\
    \n- category 2 (>2): Very Hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning ASV index is in range: -1 to 1)",  #comfortableOrNot
    
    "Percentage of time, during which ASV is -1 to 1",  #percentComfortable
    
    "Percentage of time, during which ASV is > 2",  #percentHotExtreme
    
    "Percentage of time, during which ASV is < -2"]  #percentColdExtreme
    
    ,
    
    ["Mean Radiant Temperature (°C) - uniform temperature of an imaginary enclosure in which the radiant heat transfer from the human body is equal to the radiant heat transfer in the actual non-uniform enclosure.\nFor indoor conditions MRT equals the dry bulb (air) temperature.", " ", " ", " ", " ", " "]  #comfortIndexValues
    
    ,
    
    ["Predicted Insulation Index Of Clothing (clo) - is approximated, predicted value of thermal insulation of clothing which is necessary to keep thermal comfort in man.",  #comfortIndexValues
    
    "Each number (from -4 to 2) represents a certain Iclp thermal sensation category. With categories being the following:\
    \n- category -4 (>4): Arctic\
    \n- category -3 (3.0-4.0): Very cold\
    \n- category -2 (2.0-3.0): Cold\
    \n- category -1 (1.20-2.0): Cool\
    \n- category 0 (0.80-1.20): Comfortable\
    \n- category 1 (0.30-0.80): Warm\
    \n- category 2 (≤0.30): Very warm",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning Iclp index is in range: 0.80 to 1.20)",  #comfortableOrNot
    
    "Percentage of time, during which Iclp is 0.80 to 1.20",  #percentComfortable
    
    "Percentage of time, during which Iclp is ≤ 0.30",  #percentHotExtreme
    
    "Percentage of time, during which Iclp is > 4"]  #percentColdExtreme
    
    ,
    
    ["Heart Rate (beats per minute) - is the number of heart beats per 1 minute.",  #comfortIndexValues
    
    "Each number (from 0 to 3) represents a certain HR beats per minute category. With categories being the following:\
    \n- category 0 (<%s  beats per minute): Average.\
    \n- category 1 (%s-%s beats per minute): Below Average.\
    \n- category 2 (%s-%s  beats per minute): Poor.\
    \n- category 3 (>%s beats per minute): Warning." % (HRrates[0], HRrates[0], HRrates[1], HRrates[1], HRrates[2], HRrates[2]), # comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning HR is < %s beaps per minute) " % HRrates[0], #comfortableOrNot
    
    "Percentage of time, during which HR is <%s beats per minute" % HRrates[0],  #percentComfortable
    
    "Percentage of time, during which HR is > %s beats per minute" % HRrates[2],  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Dehydration Risk (g/hour) - is the excessive loss of body water, with an accompanying disruption of metabolic processes.",  #comfortIndexValues
    
    "Each number (from 0 to 2) represents a certain Dehydration risk category. With categories being the following:\
    \n- category 0 (<%s g/hour): No risk.\
    \n- category 1 (%s-%s g/hour): Dehydration warning.\
    \n- category 2 (>%s g/hour): Dehydration hazard." % (dehydrationRiskRates[0],dehydrationRiskRates[0],dehydrationRiskRates[1],dehydrationRiskRates[1]),  # comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning HI temperature is < %s g/hour)" % dehydrationRiskRates[0],  #comfortableOrNot
    
    "Percentage of time, during which HI is < %s g/hour" % dehydrationRiskRates[0],  #percentComfortable
    
    "Percentage of time, during which HI is > %s g/hour" % dehydrationRiskRates[1],  #percentHotExtreme
    " "]  #percentColdExtreme
    ]

    return comfortIndexValue, comfortIndexCategory, comfortableOrNot, outputNickNames[comfortIndex], outputDescriptions[comfortIndex]

def printThermalComfortIndexName(comfortIndex):
    thermalComfortIndexName = ["HI (Heat Index)", "humidex (humidity index)", "DI (Discomfort Index)", "WCI (Wind Chill Index)", "WCT (Wind Chill Temperature)", "WBGT (Wet-Bulb Globe Temperature) indoors", "WBGT (Wet-Bulb Globe Temperature) outdoors", "TE (Effective Temperature)", "AT (Apparent Temperature)", "TS (Thermal Sensation)", "ASV (Actual Sensation Vote)", "MRT (Mean Radiant Temperature)", "Iclp (Predicted Insulation Index Of Clothing)", "HR (Heart Rate)", "DhRa (Dehydration Risk)"]
    print "%s successfully calculated for upper period." % thermalComfortIndexName[comfortIndex]



level = gh.GH_RuntimeMessageLevel.Warning

if (_comfortIndex != None) and _comfortIndex in range(15):
    latitude, longitude, timeZone, locationName, validLocationData, printMsgLocation = getLocationData(_location)
    if validLocationData:
        TaL, TdpL, rhL, wsL, SRL, NL, ML, age, gender, validWeatherData, printMsgWeather = getWeatherData(_dryBulbTemperature, dewPointTemperature_, _relativeHumidity, windSpeed_, globalHorizontalRadiation_, totalSkyCover_, metabolicRate_, age_, gender_)
        if validWeatherData:
            if _runIt:
                HOYs, days, months, hours, newAnalysisPeriod = HOYsDaysMonthsHoursFromHOY_analysisPeriod(HOY_, analysisPeriod_)
                HRrates = heartRates(age, gender)
                dehydrationRiskRates = DehydrationRiskRates(acclimated_)
                comfortIndexValue, comfortIndexCategory, comfortableOrNot, outputNickNames, outputDescriptions = createHeaders(_comfortIndex, _dryBulbTemperature, dewPointTemperature_, _relativeHumidity, windSpeed_, globalHorizontalRadiation_, totalSkyCover_, HRrates, dehydrationRiskRates, locationName)
                for i,hoy in enumerate(HOYs):
                    if _comfortIndex == 0:
                        hi,cat,cnc = heatIndex(TaL[int(hoy)-1], rhL[int(hoy)-1]);  comfortIndexValue.append(hi);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 4
                    elif _comfortIndex == 1:
                        humi,cat,cnc = Humidex(TaL[int(hoy)-1], TdpL[int(hoy)-1]);  comfortIndexValue.append(humi);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 5
                    elif _comfortIndex == 2:
                        di,cat,cnc = discomfortIndex(TaL[int(hoy)-1], rhL[int(hoy)-1]);  comfortIndexValue.append(di);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 5
                    elif _comfortIndex == 3:
                        wci,cat,cnc = windChillIndex(TaL[int(hoy)-1], wsL[int(hoy)-1]);  comfortIndexValue.append(wci);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 3
                        ColdExtremeCategory = -4
                    elif _comfortIndex == 4:
                        wct,cat,cnc = windChillTemperature(TaL[int(hoy)-1], wsL[int(hoy)-1]);  comfortIndexValue.append(wct);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        ColdExtremeCategory = -4
                    elif _comfortIndex == 5:
                        Tground = groundTemperature(TaL[int(hoy)-1], NL[int(hoy)-1])
                        solarZenithD, solarAzimuthD, solarAltitudeD = noaaSolarCalculator(latitude, longitude, timeZone, months[i], days[i], hours[i])
                        Rprim = solarRadiationNudeMan(SRL[int(hoy)-1], solarAltitudeD)
                        vapourPressure = VapourPressure(TaL[int(hoy)-1], rhL[int(hoy)-1])
                        mrt = meanRadiantTemperature(TaL[int(hoy)-1], Tground, Rprim, vapourPressure)
                        wbgt,cat,cnc = wbgt_indoors(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1], vapourPressure, mrt, TdpL[int(hoy)-1]);  comfortIndexValue.append(wbgt);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 5
                    elif _comfortIndex == 6:
                        Tground = groundTemperature(TaL[int(hoy)-1], NL[int(hoy)-1])
                        solarZenithD, solarAzimuthD, solarAltitudeD = noaaSolarCalculator(latitude, longitude, timeZone, months[i], days[i], hours[i])
                        Rprim = solarRadiationNudeMan(SRL[int(hoy)-1], solarAltitudeD)
                        vapourPressure = VapourPressure(TaL[int(hoy)-1], rhL[int(hoy)-1])
                        mrt = meanRadiantTemperature(TaL[int(hoy)-1], Tground, Rprim, vapourPressure)
                        wbgt,cat,cnc = wbgt_outdoors(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1], vapourPressure, mrt);  comfortIndexValue.append(wbgt);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 5
                    elif _comfortIndex == 7:
                        et,cat,cnc = effectiveTemperature(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1], SRL[int(hoy)-1]);  comfortIndexValue.append(et);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 2
                        ColdExtremeCategory = -4
                    elif _comfortIndex == 8:
                        at,cat,cnc = apparentTemperature(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1]);  comfortIndexValue.append(at);  comfortIndexCategory.append(cat); comfortableOrNot.append(cnc)
                        HotExtremeCategory = 4
                        ColdExtremeCategory = -6
                    elif _comfortIndex == 9:
                        Tground = groundTemperature(TaL[int(hoy)-1], NL[int(hoy)-1])
                        ts,cat,cnc = thermalSensation(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1], SRL[int(hoy)-1], Tground);  comfortIndexValue.append(ts);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 3
                        ColdExtremeCategory = -3
                    elif _comfortIndex == 10:
                        asv,cat,cnc = actualSensationModel(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1], SRL[int(hoy)-1]);  comfortIndexValue.append(asv);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 2
                        ColdExtremeCategory = -2
                    elif _comfortIndex == 11:
                        Tground = groundTemperature(TaL[int(hoy)-1], NL[int(hoy)-1])
                        solarZenithD, solarAzimuthD, solarAltitudeD = noaaSolarCalculator(latitude, longitude, timeZone, months[i], days[i], hours[i])
                        Rprim = solarRadiationNudeMan(SRL[int(hoy)-1], solarAltitudeD)
                        vapourPressure = VapourPressure(TaL[int(hoy)-1], rhL[int(hoy)-1])
                        mrt = meanRadiantTemperature(TaL[int(hoy)-1], Tground, Rprim, vapourPressure);  comfortIndexValue.append(mrt)
                    elif _comfortIndex == 12:
                        iclp,cat,cnc = predictedInsulationIndexOfClothing(TaL[int(hoy)-1], wsL[int(hoy)-1], ML[int(hoy)-1]);  comfortIndexValue.append(iclp);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 2
                        ColdExtremeCategory = -4
                    elif _comfortIndex == 13:
                        vapourPressure = VapourPressure(TaL[int(hoy)-1], rhL[int(hoy)-1])
                        hr,cat,cnc = heartRate(TaL[int(hoy)-1], vapourPressure, ML[int(hoy)-1], HRrates);  comfortIndexValue.append(hr);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 3
                    elif _comfortIndex == 14:
                        Tground = groundTemperature(TaL[int(hoy)-1], NL[int(hoy)-1])
                        solarZenithD, solarAzimuthD, solarAltitudeD = noaaSolarCalculator(latitude, longitude, timeZone, months[i], days[i], hours[i])
                        Rprim = solarRadiationNudeMan(SRL[int(hoy)-1], solarAltitudeD)
                        vapourPressure = VapourPressure(TaL[int(hoy)-1], rhL[int(hoy)-1])
                        mrt = meanRadiantTemperature(TaL[int(hoy)-1], Tground, Rprim, vapourPressure)
                        Icl = clothingInsulation(TaL[int(hoy)-1])
                        Ts = meanSkinTemperature(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1], mrt, Icl, ML[int(hoy)-1])
                        e_ = VapourPressure(TaL[int(hoy)-1], 5)
                        Epot = turbulentExchangeOfLatentHeat(TaL[int(hoy)-1], wsL[int(hoy)-1], Ts, Icl, e_, ML[int(hoy)-1])
                        sw,cat,cnc = dehydrationRisk(Epot, acclimated_, dehydrationRiskRates);  comfortIndexValue.append(sw);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 2
                
                if _comfortIndex != 11:  # not for MRT
                    percentComfortable = (comfortableOrNot[7:].count(1))/(len(comfortIndexValue[7:]))*100
                    if _comfortIndex != 4:
                        percentHotExtreme = (comfortIndexCategory[7:].count(HotExtremeCategory))/(len(comfortIndexCategory[7:]))*100
                    else: # remove percentHotExtreme for WCT
                        percentHotExtreme = []
                    if _comfortIndex not in [0,1,2,5,6,13,14]: # no Cold categories
                        percentColdExtreme = (comfortIndexCategory[7:].count(ColdExtremeCategory))/(len(comfortIndexCategory[7:]))*100
                    else:  # remove percentColdExtreme
                        percentColdExtreme = []
                else:
                    percentComfortable = []
                    percentHotExtreme = []
                    percentColdExtreme = []
                
                generalOutputLists = ["dummy", "comfortIndexValue", "comfortIndexCategory", "comfortableOrNot", "percentComfortable", "percentHotExtreme", "percentColdExtreme"]
                for i in range(6):
                    ghenv.Component.Params.Output[i+1].Name = outputNickNames[i]
                    ghenv.Component.Params.Output[i+1].NickName = outputNickNames[i]
                    ghenv.Component.Params.Output[i+1].Description = outputDescriptions[i]
                    exec("%s = %s" % (outputNickNames[i], generalOutputLists[i+1]))
                printThermalComfortIndexName(_comfortIndex)
            else:
                print "Please set \"_runIt\" to True, to calculate the chosen Thermal Comfort index"
        else:
            print printMsgWeather
            ghenv.Component.AddRuntimeMessage(level, printMsgWeather)
    else:
        print printMsgLocation
        ghenv.Component.AddRuntimeMessage(level, printMsgLocation)
else:
    printMsgComfortIndex = "Please input _comfortIndex from 0 to 10"
    print printMsgComfortIndex
    ghenv.Component.AddRuntimeMessage(level, printMsgComfortIndex)
    
