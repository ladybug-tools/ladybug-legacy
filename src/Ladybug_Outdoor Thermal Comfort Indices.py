# thermal comfort indices
# By Djordje Spasic
# djordjedspasic@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate different thermal comfort indices frequently used by weather reporters.

Provided by Ladybug 0.0.58
    
    input:
        _comfortIndex: Choose one of the comfort indices:
                       0 - HI (Heat Index)
                       1 - humidex
                       2 - DI (Discomfort Index)
                       3 - WCT (Wind Chill Temperature)
                       4 - WBGT (Wet-Bulb Globe Temperature) indoors
                       5 - WBGT (Wet-Bulb Globe Temperature) outdoors
                       6 - TE (Effective Temperature)
                       7 - AT (Apparent Temperature)
                       8 - TS (Thermal Sensation)
                       9 - ASV (Actual Sensation Vote)
                       10 - MRT (Mean Radiant Temperature)
        _location: Input data from Ladybug's "Import epw" "location" output.
        _dryBulbTemperature: Hourly Dry Bulb Temperature (air temperature), in Celsius
        dewPointTemperature_: Hourly Dew Point Temperature, in Celsius
        _relativeHumidity: Hourly Relative Humidity, in percent (from 0% to 110%)
        windSpeed_: Hourly Wind Speed, in meters/second
        globalHorizontalRadiation_:  Total amount of direct and diffuse solar radiation received on a horizontal surface, in Wh/m2.
                                     Default value is 100 Wh/m2
        totalSkyCover_: Amount of sky dome in tenths covered by clouds or obscuring phenomena, in tenths of coverage (from 1 to 10). For example: 1 is 1/10 covered. 10 is total coverage (10/10).
			Default value is 8 (8/10)
        HOY_: An hour of the year for which you would like to calculate thermal indices.  This must be a value between 1 and 8760.
	      This input will override the analysisPeriod_ input below.
        analysisPeriod_: An optional analysis period from the Analysis Period component. 
        _runIt: ...
        
    output:
        readMe!: ...
"""

ghenv.Component.Name = "Ladybug_Outdoor Thermal Comfort Indices"
ghenv.Component.NickName = 'ThermalComfortIndices'
ghenv.Component.Message = 'VER 0.0.58\nSEP_26_2014'
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
        printMsg = "Please input 'location' ouput of Ladybug 'Import epw' component, or\nmake your own location data using Ladybug's 'Contruct Location' and plug it into '_location' input of this component."

    return latitude, longitude, timeZone, locationName, validLocationData, printMsg


def getWeatherData(comfortIndex, Ta, Tdp, rh, ws, SR, N):
    if not comfortIndex:
        comfortIndex = 0

    if (not Ta):
        Ta = Tdp = rh = ws = SR = N = None
        printMsg = "Please input _dryBulbTemperature"
        validWeatherData = False
        return comfortIndex, Ta, Tdp, rh, ws, SR, N, validWeatherData, printMsg
    elif (not rh):
        Ta = Tdp = rh = ws = SR = N = None
        printMsg = "Please input _relativeHumidity"
        validWeatherData = False
        return comfortIndex, Ta, Tdp, rh, ws, SR, N, validWeatherData, printMsg

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

    maximalListLength = max(TaLlength, TdpLlength, rhLlength, wsLlength, SRLlength)

    # at least one of inputed dryBulbTemperature_, relativeHumidity_ comes from "Ladybug import epw" component". The rest are single values
    if maximalListLength == 8767:
        # this is for calculating Tdp , in case dewPointTemperature_ has not been inputted
        if len(rh) == 1:
            try:
                item = float(rh[0])
                rh = []
                for i in range(maximalListLength-7):
                    rh.append(item) # default value 0.3 m/s
            except:
                pass
    
        if not Tdp:
            try:
                Td = []
                #Tdp = Ta[:7]
                for i in range(maximalListLength-7):
                    dewPoint = dewPointTemperature(Ta[i+7], rh[i+7])
                    Tdp.append(dewPoint)
    
            except:
                pass
    
        if not ws:
            try:
                ws = Ta[:7]
                for i in range(maximalListLength-7):
                    ws.append(0.3) # default value 0.3 m/s
            except:
                pass
    
        if not SR:
            try:
                SR = Ta[:7]
                for i in range(maximalListLength-7):
                    SR.append(100) # default value 100 Wh/m2(%)
            except:
                pass
    
        if not N:
            try:
                N = Ta[:7]
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
                
        printMsg = "ok"
        validWeatherData = True
        return comfortIndex, Ta, Tdp, rh, ws, SR, N, validWeatherData, printMsg


    # all inputs come as a single value (maximalListLength != 8767)
    elif maximalListLength == 1:
        TaL = [float(Ta[0]) for i in range(8760)]
        rhL = [float(rh[0]) for i in range(8760)]

        if not Tdp:
            dewPoint = dewPointTemperature(float(Ta[0]), float(rh[0]))
            TdpL = []
            for i in range(8760):
                TdpL.append(dewPoint)
        else:
            TdpL = [float(Tdp[0]) for i in range(8760)]
        if not ws:
            wsL = []
            for i in range(8760):
                wsL.append(0.3) # default value 0.3 m/s
        else:
            wsL = [float(ws[0]) for i in range(8760)]
        if not SR:
            SRL = []
            for i in range(8760):
                SRL.append(8) # default value 8 (tens)
        else:
            SRL = [float(SR[0]) for i in range(8760)]

        if not N:
            NL = []
            for i in range(8760):
                NL.append(8) # default value 8 (tens)
        else:
            NL = [float(N[0]) for i in range(8760)]

        printMsg = "ok"
        validWeatherData = True

        return comfortIndex, TaL, TdpL, rhL, wsL, SRL, NL, validWeatherData, printMsg

    # some inputs come as a single value, but some as list of at least 2 values (list of 2 values not supported)
    else:
        Ta = Tdp = rh = ws = SR = N = None
        printMsg = "Something is wrong with your dryBulbTemperature_, relativeHumidity_, globalHorizontalRadiation_ input data."
        validWeatherData = False
        return comfortIndex, Ta, Tdp, rh, ws, SR, N, validWeatherData, printMsg


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
    # uncertainty in the calculated dew point temperature: +/- 0.4C
    # for Tc in range:  0C < Tc < 60C  
    # for Tdp in range:  0C < Tdp < 50C   
    a = 17.27
    b = 237.7
    rh = rh/100  # 0.01 < rh < 1.00
    Tdp = (b * ( ((a*Ta)/(b+Ta))+math.log(rh) ))/(a-( ((a*Ta)/(b+Ta))+math.log(rh) ))  # in Celius degrees
    
    return Tdp

def Humidex(Ta, rh, Tdp=None):

    if not Tdp:
        Tdp = dewPointTemperature(Ta, rh)  # in Celius degrees

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
    # formula from: Thom, E.C. (1959): The discomfort index. Weather wise, 12: 5760.
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


def windChillTemperature(Ta, ws):
    # formula by Environment Canada (corresponds to National Weather Service (NSW) Wind chill formula used in U.S.)
    ws_km_h = ws * 3.6   # convert m/s to km/h wind speed

    Twc = 13.12 + 0.6215*Ta - 11.37*(ws_km_h**0.16) + 0.3965*Ta*(ws_km_h**0.16)   # in Celius degrees

    if Twc >= -27:
        effectTwc = 0
        comfortable = 1
    elif Twc < -27 and Twc >= -39:
        effectTwc = -1
        comfortable = 0
    elif Twc < -39 and Twc >= -47:
        effectTwc = -2
        comfortable = 0
    elif Twc < -47 and Twc >= -54:
        effectTwc = -3
        comfortable = 0
    elif Twc < -54:
        effectTwc = -4
        comfortable = 0
    return Twc, effectTwc, comfortable


def effectiveTemperature(Ta, ws, rh):
    if ws <= 0.2:
        # formula by Missenard
        TE = Ta - 0.4*(Ta - 10)*(1-rh/100)
    elif ws > 0.2:
        # modified formula by Gregorczuk (WMO, 1972; Hentschel, 1987)
        TE = 37 - ( (37-Ta)/(0.68-(0.0014*rh)+(1/(1.76+1.4*(ws**0.75)))) ) - (0.29 * Ta * (1-0.01*rh)) # nije Missenard, drugi je neki

    if TE < 1:
        effectTE = -4
        comfortable = 0
    elif TE >= 1 and TE < 9:
        effectTE = -3
        comfortable = 0
    elif TE >= 9 and TE < 17:
        effectTE = -2
        comfortable = 0
    elif TE >= 17 and TE < 21:
        effectTE = -1
        comfortable = 0
    elif TE >= 21 and TE < 23:
        effectTE = 0
        comfortable = 1
    elif TE >= 23 and TE < 27:
        effectTE = 1
        comfortable = 0
    elif TE >= 27:
        effectTE = 2
        comfortable = 0

    return TE, effectTE, comfortable


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
    # formula from: Givoni, Noguchi, Issues and problems in outdoor comfort research, in: Proceedings of the PLEA2000 Conference, Cambridge, UK, July 2000
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
    #(Givoni and Noguchi, 2000; Nikolopoulou et al., 2004
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


def solarZenithAngle(latitude, longitude, timeZone, month, day, hour):
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
    # solar zenith angle (in Radians)
    tetaR = math.acos(math.sin(degreesToRadians(latitude)) * math.sin(declAngle) + math.cos(degreesToRadians(latitude)) * math.cos(declAngle) * math.cos(degreesToRadians(solarHangle)))
    tetaC = radiansToDegrees(tetaR)
    cosTeta = math.cos(tetaR)
    # solar altitude:
    solarAltitudeC = 90 - tetaC

    return tetaR, solarAltitudeC


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
    
    return Rprim


def groundTemperature(Ta, N):
    # formula from: Assessment of bioclimatic differentiation of Poland. Based on the human heat balance, Geographia Polonica, Matzarakis, Blazejczyk, 2007
    N100 = N *10 #converting weather data totalSkyCover from 0 to 10% to 0 to 100%

    if (not N100) or (N100 >= 80):
        Tground = Ta
    elif (N100 < 80) and (Ta >= 0):
        Tground = 1.25*Ta
    elif (N100 < 80) and (Ta < 0):
        Tground = 0.9*Ta

    return Tground


def VapourPressure(Ta, rh):
    # formula by ITS-90 formulations for vapor pressure, frostpoint temperature, dewpoint temperature, and enhancement factors in the range 100 to +100 c, Thunder Scientific Corporation, Albuquerque, NM, Bob Hardy
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


def wbgt_indoors(Ta, ws, rh, e, MRT, Tdp=None):
    
    if not Tdp:
        Tdp = dewPointTemperature(Ta, rh)  # in Celius degrees
    
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
    # WBGT outdoor formula from Heat stress and occupational health and safety  spatial and temporal differentiation, K. Blazejczyk, J.Baranowski, A. Blazejczyk, Miscellanea geographica  regional studies on development, Vol. 18, No. 1, 2014, 
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
    
    days = []
    months = []
    hours = []
    for hoy in HOYs:
        day, month, hour, date = extractDataFromHOY([hoy])
        days.append(day[0])
        months.append(month[0])
        hours.append(hour[0])
    
    return HOYs, days, months, hours, newAnalysisPeriod


def createHeaders(comfortIndex, Ta, Tdp, rh, ws, SR, N, locationName):

    for data in Ta, Tdp, rh, ws, SR, N:
        if "key:location/dataType/units/frequency/startsAt/endsAt" in data:
            header = data[:7]
            break
        else:
            # default header
            header = ["key:location/dataType/units/frequency/startsAt/endsAt", "SACRAMENTO_CA_USA", "Universal Thermal Climate Index", "C", "Hourly", (1, 1, 1), (1, 1, 2)]
    
    # change (or just replace it with the same current) locationName
    header[1] = locationName
    
    comfortIndexValue = []
    comfortIndexCategory = []
    comfortableOrNot = []
    IndicesEmptyLists = [comfortIndexValue, comfortIndexCategory, comfortableOrNot]
    
    
    IndiceTitles = [
    ["Heat Index - values", "Heat Index - categories", "Heat Index - comfortable(1) or not(0)"], \
    ["Humidex - values", "Humidex - categories", "Humidex - comfortable(1) or not(0)"], \
    ["Discomfort Index - values", "Discomfort Index - categories", "Discomfort Index - comfortable(1) or not(0)"], \
    ["Wind Chill Temperature - values", "Wind Chill Temperature - categories", "Wind Chill Temperature - comfortable(1) or not(0)"], \
    ["Wet-Bulb Globe Temperature (indoors) - values", "Wet-Bulb Globe Temperature (indoors) - categories", "Wet-Bulb Globe Temperature (indoors) - comfortable(1) or not(0)"], \
    ["Wet-Bulb Globe Temperature (outdoors) - values", "Wet-Bulb Globe Temperature (outdoors) - categories", "Wet-Bulb Globe Temperature (outdoors) - comfortable(1) or not(0)"], \
    ["Effective Temperature - values", "Effective Temperature - categories", "Effective Temperature - comfortable(1) or not(0)"], \
    ["Apparent Temperature - values", "Apparent Temperature - categories", "Apparent Temperature - comfortable(1) or not(0)"], \
    ["Thermal Sensation - values", "Thermal Sensation - categories ", "Thermal Sensation - comfortable(1) or not(0)"], \
    ["Actual Sensation Vote - values", "Actual Sensation Vote - categories", "Actual Sensation Vote - comfortable(1) or not(0)"], \
    ["Mean Radiant Temperature - values"]]
    
    IndiceUnitsCat = [
    ["C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot", "Boolean value"], \
    ["C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"], \
    ["C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"], \
    ["C", "-4 = Extreme risk of frostbite,  -3 = Very high risk of frostbite,  -2 = High risk of frostbite,  -1 = Moderate risk of frostbite,  0 = Low risk of frostbite", "Boolean value"], \
    ["C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"], \
    ["C", "0 = Comfortable,  1 = Moderate Hot,  2 = Hot,  3 = Quite hot,  4 = Very hot,  5 = Extremely hot", "Boolean value"], \
    ["C", "-4 = Very cold,  -3 = Cold,  -2 = Cool,  -1 = Fresh,  0 = Comfortable,  1 = Warm, 2 = Hot", "Boolean value"], \
    ["C", "Appareal increments:\n-5 = Overcoat, cap,  -4 = Overcoat,  -3 = Coat and sweater,  -2 = Sweater,  -1 = Thin sweater,  0 = Normal office wear,  1 = Cotton pants,  2 = Light undershirt,  3 = Shirt, shorts,  4 = Minimal cloths. Sun protection as needed", "Boolean value"], \
    ["unit-less", "-3 = Very cold, -2 = Quite cold,  -1 = Cold,  0 = Comfortable,  1 = Hot,  2 = Quite hot,  3 = Very hot", "Boolean value"], \
    ["unit-less", "-2 = Very cold,  -1 = Cold,  0 = Comfortable,  1 = Hot,  2 = Very hot", "Boolean value"], \
    ["C"]]
    
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
    ["WCT", "WCTlevel", "WCTcomfortableOrNot", "WCTpercentComfortable", "_", "WCTpercentColdExtreme"],
    ["WBGTindoor", "WBGTlevel", "WBGTcomfortableOrNot", "WBGTpercentComfortable", "WBGTpercentHotExtreme", "_"],
    ["WBGToutdoor", "WBGTlevel", "WBGTcomfortableOrNot", "WBGTpercentComfortable", "WBGTpercentHotExtreme", "_"],
    ["TE", "TElevel", "TEcomfortableOrNot", "TEpercentComfortable", "TEpercentHotExtreme", "TEpercentColdExtreme"],
    ["AT", "ATlevel", "ATcomfortableOrNot", "ATpercentComfortable", "ATpercentHotExtreme", "ATpercentColdExtreme"],
    ["TS", "TSlevel", "TScomfortableOrNot", "TSpercentComfortable", "TSpercentHotExtreme", "TSpercentColdExtreme"],
    ["ASV", "ASVlevel", "ASVcomfortableOrNot", "ASVpercentComfortable", "ASVpercentHotExtreme", "ASVpercentColdExtreme"],
    ["MRT", "_", "_", "_", "_", "_"],
    ] # outputNames = outputNickNames

    outputDescriptions = [
    ["Heat Index (C) - the human-perceived increase in air temperature due to humidity increase. It is used by National Weather Service (NSW).\nHeat Index is calculated for shade values. Exposure to full sunshine can increase heat index values by up to 8C (14F)",  #comfortIndexValues
    
    "Each number (from 0 to 4) represents a certain HI thermal sensation category. With categories being the following:\
    \n- category 0 (<26.6C): Satisfactory temperature. Can continue with activity.\
    \n- category 1 (26.6-32.2C): Caution: fatigue is possible with prolonged exposure and activity. Continuing activity could result in heat cramps.\
    \n- category 2( 32.2-40.5C): Extreme caution: heat cramps and heat exhaustion are possible. Continuing activity could result in heat stroke.\
    \n- category 3 (40.5-54.4C): Danger: heat cramps and heat exhaustion are likely; heat stroke is probable with continued activity.\
    \n- category 4 (>54.4C): Extreme danger: heat stroke is imminent.",  # comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning HI temperature is < 26.6C)",  #comfortableOrNot
    
    "Percentage of time, during which HI is < 26.6C",  #percentComfortable
    
    "Percentage of time, during which HI is > 54.4C",  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Humidex (C) - the human-perceived increase in air temperature due to Dew point temperature increase. Used by Canadian Meteorologist service.",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain humidex thermal sensation category. With categories being the following:\
    \n- category 0 (<30C): Little or no discomfort\
    \n- category 1 (30-35C): Noticeable discomfort\
    \n- category 2 (35-40C): Evident discomfort\
    \n- category 3 (40-45C): Intense discomfort; avoid exertion\
    \n- category 4 (45-54C): Dangerous discomfort\
    \n- category 5 (>54C): Heat stroke probable",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning humidex is < 30C)",  # comfortableOrNot
    
    "Percentage of time chosen for analysis period, during which humidex is < 26.6C",  # percentComfortable
    
    "Percentage of time chosen for analysis period, during which humidex is > 54.4C", # percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["Discomfort Index (or Thom's Index)(C) - the human-perceived increase in air temperature due to himidity increase.",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain DI thermal sensation category. With categories being the following:\
    \n- category 0 (<21C): No discomfort\
    \n- category 1 (21-24C): Under 50% of population feels discomfort\
    \n- category 2 (24-27C): Over 50% of population feels discomfort\
    \n- category 3 (27-29C): Most of population suffers discomfort\
    \n- category 4 (29-32C): Everyone feels stress\
    \n- category 5 (>32C): State of medical emergency",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning DI temperature is < 21C)",  #comfortableOrNot
    
    "Percentage of time chosen for analysis period, during which DI is < 21C",  #percentComfortable
    
    "Percentage of time chosen for analysis period, during which DI is > 32C",  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    ["(WCT) Wind Chill Temperature (index/factor) (C) - the perceived decrease in air temperature felt by the body on exposed skin due to the flow of air.\nIt's used by both National Weather Service (NSW) in US and Canadian Meteorologist service. This is new (2001 by JAG/TI) WCT.\nWind chill index does not take into account the effect of sunshine.\nBright sunshine may reduce the effect of wind chill (make it feel warmer) by 6 to 10 units(C or F)!\nWindchill temperature is defined only for temperatures at or below 10C (50F) and for wind speeds at and above 1.3 m/s (or 4.8 km/h or 3.0 mph)",  #comfortIndexValues
    
    "Each number (from -4 to 0) represents a certain WCT thermal sensation category. With categories being the following:\
    \n- category 0 (>-27C) Low risk of frostbite for most people\
    \n- category -1 (-27-(-39)C) Increasing risk of frostbite for most people in 10 to 30 minutes of exposure\
    \n- category -2 (-39-(-47)C) High risk of frostbite for most people in 5 to 10 minutes of exposure\
    \n- category -3 (-47-(-54)C) High risk of frostbite for most people in 2 to 5 minutes of exposure\
    \n- category -4 (<-54C) High risk of frostbite for most people in 2 minutes of exposure or less",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that there is danger of frostbite, 1 there is not danger of frostbite at that hour (meaning WCT temperature is in range: >-27C)",  #comfortableOrNot
    
    "Percentage of time, during which there is low risk of frostbite (DI is > -27C)",  #percentComfortable
    " ",  #percentHotExtreme
    
    "Percentage of time, during which there is high risk of frostbite (DI is < -54C)"]  #percentColdExtreme
    
    ,
    
    ["Wet-Bulb Globe Temperature(C) - perceived indoor temperature.\nIt is used by the U.S. military, American Academy of Pediatrics and OSHA (Occupational Safety and Health Administration) to obtain measure of heat stress involved in manual labor jobs of soldiers, construction workers, steel mill workers, firefighters, law enforcement officers, athletes...",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain WBGT thermal sensation category. With categories being the following:\
    \n- category 0 (<26C): No change in activity is required.\
    \n- category 1 (26-27.7C): No change in activity is required. Use discretion when planning heavy activities for unacclimated person.\
    \n- category 2 (27.7-29.4C): Outdoor physical activities and strenuous exercise should be limited to 50 minutes per hour. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 3 (29.4-31.1C): Outdoor physical activities and strenuous exercise should be limited to 40 minutes per hour. You should unblouse trouser legs. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 4 (31.1-32.2C): Outdoor physical activities and strenuous exercise should be limited to 30 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 5 (>32.2C): Outdoor physical activities and strenuous exercise should be limited to 20 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning WBGT temperature is in range: 29.4 to 31.1C)",  #comfortableOrNot
    
    "Percentage of time, during which WBGT is < 26C",  #percentComfortable
    
    "Percentage of time, during which WBGT is > 32.2C",  #percentHotExtreme
    " "]  #percentColdExtreme
    ,
    
    ["Wet-Bulb Globe Temperature(C) - perceived outdoor temperature.\nIt is used by the U.S. military, American Academy of Pediatrics and OSHA (Occupational Safety and Health Administration) to obtain measure of heat stress involved in manual labor jobs of soldiers, construction workers, steel mill workers, firefighters, law enforcement officers, athletes...",  #comfortIndexValues
    
    "Each number (from 0 to 5) represents a certain WBGT thermal sensation category. With categories being the following:\
    \n- category 0 (<26C): No change in activity is required.\
    \n- category 1 (26-27.7C): No change in activity is required. Use discretion when planning heavy activities for unacclimated person.\
    \n- category 2 (27.7-29.4C): Outdoor physical activities and strenuous exercise should be limited to 50 minutes per hour. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 3 (29.4-31.1C): Outdoor physical activities and strenuous exercise should be limited to 40 minutes per hour. You should unblouse trouser legs. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 4 (31.1-32.2C): Outdoor physical activities and strenuous exercise should be limited to 30 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.\
    \n- category 5 (>32.2C): Outdoor physical activities and strenuous exercise should be limited to 20 minutes per hour. You should unblouse trouser legs and top down to t-shirt. This recommendation applies to the average acclimated person and conducting moderate work outdoors. Use discretion when planning heavy exercises for unacclimated person.",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning WBGT temperature is in range: 29.4 to 31.1C)",  #comfortableOrNot
    
    "Percentage of time, during which WBGT is < 26C",  #percentComfortable
    
    "Percentage of time, during which WBGT is > 32.2C",  #percentHotExtreme
    " "]  #percentColdExtreme
    
    ,
    
    
    ["Effective Temperature (C) - influence of air temperature, wind speed and relative humidity of air on man staying in the shadow.",  #comfortIndexValues
    
    "Each number (from -4 to 2) represents a certain TE thermal sensation category. With categories being the following:\
    \n- category -4 (<1C): Very cold\
    \n- category -3 (1-9C): Cold\
    \n- category -2 (9-17C): Cool\
    \n- category -1 (17-21C): Fresh\
    \n- category 0 (21-23C): Comfortable\
    \n- category 1 (23-27C): Warm\
    \n- category 2 (>27C): Hot",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning TE temperature is in range: 21 to 23C)",  #comfortableOrNot
    
    "Percentage of time, during which TE is < 21-23C",  #percentComfortable
    
    "Percentage of time, during which TE is > 27C",  #percentHotExtreme
    
    "Percentage of time, during which TE is < 1C"]  #percentColdExtreme
    
    ,
    
    ["Apparent Temperature (C) - combines wind chill and heat index to give one single perceived outdoor temperature for Australian climate.\nNon-radiation formula from ABM(Australian Bureau of Meteorology).",  #comfortIndexValues
    
    "Each number (from -5 to 4) represents a certain AT thermal sensation category. With categories being the following:\
    \nAppareal increments:\
    \n- category 4 (>40C): Minimal; sun protection required\
    \n- category 3 (35-40C): Minimal; sun protection as needed\
    \n- category 2 (30-35C): Short sleeve, shirt and shorts\
    \n- category 1 (25-30C): Light undershirt\
    \n- category 0 (20-25C): Cotton-type slacks (pants)\
    \n- category -1 (15-20C): Normal office wear\
    \n- category -2 (10-15C): Thin or sleeveless sweater\
    \n- category -3 (5-10C): Sweater. Thicker underwear\
    \n- category -4 (0-5C): Coat and sweater\
    \n- category -5 (-5-0C): Overcoat. Wind protection as needed\
    \n- category -6 (<-5C): Overcoat. Head insulation. Heavier footwear",  #comfortIndexCategory
    
    "Outputs 0 or 1. 0 indicates that a person is not comfortable, 1 that he/she is comfortable at that hour (meaning AT temperature is in range: 20 to 25C)",  #comfortableOrNot
    
    "Percentage of time, during which AT is < 20-25C",  #percentComfortable
    
    "Percentage of time, during which AT is > 40C",  #percentHotExtreme
    
    "Percentage of time, during which AT is < -5C"]  #percentColdExtreme
    
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
    
    ["Mean Radiant Temperature (C) - uniform temperature of an imaginary enclosure in which the radiant heat transfer from the human body is equal to the radiant heat transfer in the actual non-uniform enclosure.\nFor indoor conditions MRT equals the dry bulb (air) temperature.", " ", " ", " ", " ", " "]  #comfortIndexValues
    ]

    return comfortIndexValue, comfortIndexCategory, comfortableOrNot, outputNickNames[comfortIndex], outputDescriptions[comfortIndex]




level = gh.GH_RuntimeMessageLevel.Warning

if (_comfortIndex != None) and _comfortIndex in range(11):
    latitude, longitude, timeZone, locationName, validLocationData, printMsgLocation = getLocationData(_location)
    if validLocationData:
        comfortIndex, TaL, TdpL, rhL, wsL, SRL, NL, validWeatherData, printMsgWeather = getWeatherData(_comfortIndex, _dryBulbTemperature, dewPointTemperature_, _relativeHumidity, windSpeed_, globalHorizontalRadiation_, totalSkyCover_)
        if validWeatherData:
            if _runIt:
                HOYs, days, months, hours, newAnalysisPeriod = HOYsDaysMonthsHoursFromHOY_analysisPeriod(HOY_, analysisPeriod_)
                comfortIndexValue, comfortIndexCategory, comfortableOrNot, outputNickNames, outputDescriptions = createHeaders(_comfortIndex, _dryBulbTemperature, dewPointTemperature_, _relativeHumidity, windSpeed_, globalHorizontalRadiation_, totalSkyCover_, locationName)
                for i,hoy in enumerate(HOYs):
                    if comfortIndex == 0:
                        hi,cat,cnc = heatIndex(TaL[int(hoy)-1], rhL[int(hoy)-1]);  comfortIndexValue.append(hi);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 4
                    elif comfortIndex == 1:
                        humi,cat,cnc = Humidex(TaL[int(hoy)-1], rhL[int(hoy)-1], TdpL[int(hoy)-1]);  comfortIndexValue.append(humi);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 5
                    elif comfortIndex == 2:
                        di,cat,cnc = discomfortIndex(TaL[int(hoy)-1], rhL[int(hoy)-1]);  comfortIndexValue.append(di);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 5
                    elif comfortIndex == 3:
                        wct,cat,cnc = windChillTemperature(TaL[int(hoy)-1], wsL[int(hoy)-1]);  comfortIndexValue.append(wct);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        ColdExtremeCategory = -4
                    elif comfortIndex == 4:
                        Tground = groundTemperature(TaL[int(hoy)-1], NL[int(hoy)-1])
                        solarZenithAngleR, solarAltitudeC = solarZenithAngle(latitude, longitude, timeZone, months[i], days[i], hours[i])
                        Rprim = solarRadiationNudeMan(SRL[int(hoy)-1], solarAltitudeC)
                        vapourPressure = VapourPressure(TaL[int(hoy)-1], rhL[int(hoy)-1])
                        mrt = meanRadiantTemperature(TaL[int(hoy)-1], Tground, Rprim, vapourPressure)
                        wbgt,cat,cnc = wbgt_indoors(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1], vapourPressure, mrt);  comfortIndexValue.append(wbgt);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 5
                    elif comfortIndex == 5:
                        Tground = groundTemperature(TaL[int(hoy)-1], NL[int(hoy)-1])
                        solarZenithAngleR, solarAltitudeC = solarZenithAngle(latitude, longitude, timeZone, months[i], days[i], hours[i])
                        Rprim = solarRadiationNudeMan(SRL[int(hoy)-1], solarAltitudeC)
                        vapourPressure = VapourPressure(TaL[int(hoy)-1], rhL[int(hoy)-1])
                        mrt = meanRadiantTemperature(TaL[int(hoy)-1], Tground, Rprim, vapourPressure)
                        wbgt,cat,cnc = wbgt_outdoors(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1], vapourPressure, mrt);  comfortIndexValue.append(wbgt);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 5
                    elif comfortIndex == 6:
                        et,cat,cnc = effectiveTemperature(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1]);  comfortIndexValue.append(et);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 2
                        ColdExtremeCategory = -4
                    elif comfortIndex == 7:
                        at,cat,cnc = apparentTemperature(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1]);  comfortIndexValue.append(at);  comfortIndexCategory.append(cat); comfortableOrNot.append(cnc)
                        HotExtremeCategory = 4
                        ColdExtremeCategory = -6
                    elif comfortIndex == 8:
                        Tground = groundTemperature(TaL[int(hoy)-1], NL[int(hoy)-1])
                        ts,cat,cnc = thermalSensation(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1], SRL[int(hoy)-1], Tground);  comfortIndexValue.append(ts);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 3
                        ColdExtremeCategory = -3
                    elif comfortIndex == 9:
                        asv,cat,cnc = actualSensationModel(TaL[int(hoy)-1], wsL[int(hoy)-1], rhL[int(hoy)-1], SRL[int(hoy)-1]);  comfortIndexValue.append(asv);  comfortIndexCategory.append(cat);  comfortableOrNot.append(cnc)
                        HotExtremeCategory = 2
                        ColdExtremeCategory = -2
                    elif comfortIndex == 10:
                        Tground = groundTemperature(TaL[int(hoy)-1], NL[int(hoy)-1])
                        solarZenithAngleR, solarAltitudeC = solarZenithAngle(latitude, longitude, timeZone, months[i], days[i], hours[i])
                        Rprim = solarRadiationNudeMan(SRL[int(hoy)-1], solarAltitudeC)
                        vapourPressure = VapourPressure(TaL[int(hoy)-1], rhL[int(hoy)-1])
                        mrt = meanRadiantTemperature(TaL[int(hoy)-1], Tground, Rprim, vapourPressure);  comfortIndexValue.append(mrt)
                
                if comfortIndex != 10:  # not for MRT
                    percentComfortable = (comfortableOrNot[7:].count(1))/(len(comfortIndexValue[7:]))*100
                    if comfortIndex != 3:
                        percentHotExtreme = (comfortIndexCategory[7:].count(HotExtremeCategory))/(len(comfortIndexCategory[7:]))*100
                    else: # remove percentHotExtreme for WCT
                        percentHotExtreme = []
                    if comfortIndex not in [0,1,2,4,5]:
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
                print "Thermal Comfort index successfully calculated."
            else:
                print "Please set \"_runIt\" to True, to calculate Thermal Comfort indices"
        else:
            print printMsgWeather
            ghenv.Component.AddRuntimeMessage(level, printMsgWeather)
    else:
        print printMsgLocation
        ghenv.Component.AddRuntimeMessage(level, printMsgLocation)
else:
    printMsgComfortIndex = "Please input _comfortIndex from 0 to 10"
    print printMsgComfortIndex