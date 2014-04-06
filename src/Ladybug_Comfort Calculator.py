# Comfort Calculator
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate comfort metrics of Prediceted Mean Vote (PMV), the Percent of People Dissatisfied (PPD) and the Standard Effective Temperature (SET) for a set of individual climate conditions or for imported EPW weather data.
Perhaps the most familiar application of SET is the temperature given by TV weathermen and women when they say that, even though the dry bulb temperature outside is a certain value, the temperature actually "feels like" something that is much higher or lower.
This is because SET takes into account other climate variables such as relative humidity and wind speed and uses them in a human energy balance model to give a temperature value that is indicative of the heat stress or loss felt by the human body.

Specifically, SET is definied as the equivalent temperature of an imaginary environment at 50% relative humidity, <0.1 m/s air speed, and mean radiant temperature equal to air temperature, in which the total heat loss from the skin of an imaginary occupant is the same as that from a person existing under the input conditions.
It is also important to note that the imaginary occupant is modeled with an activity level of 1.0 met, a clothing level of 0.6 clo, and an external work value of 0 (meaning that all of the energy the body produces is heat).  The actual occupant in the real environment can have different values from these.

The specific human energy balance model that SET uses to perform this calculation is the Predicted Mean Vote (PMV) model developed by P.O. Fanger.  PMV technically refers to a scale from -3 to +3 where -3 is extremely uncomfortably cold, +3 is extremely uncomfortably hot, and values between -1 and +1 are comfortable.
Accordingly, this component will also output the PMV of the occupant for the input conditions as well as an estimated percentage of people dissatisfied (PPD) in the given conditions.

The comfort models that make this component possible were translated to python from a series of validated javascript comfort models developed at the Berkely Center for the Built Environment (CBE).
Specific documentation on the comfort models can be found here: https://code.google.com/p/cbe-comfort-tool/wiki/ComfortModels

Special thanks goes to the authors of the online CBE Thermal Comfort Tool who first made the javascript models in order to power the tool:
Hoyt Tyler, Schiavon Stefano, Piccioli Alberto, Moon Dustin, and Steinfeld Kyle, 2013, CBE Thermal Comfort Tool. 
Center for the Built Environment, University of California Berkeley, http://cbe.berkeley.edu/comforttool/
-
Provided by Ladybug 0.0.57
    
    Args:
        _dryBulbTemperature: A number representing the dry bulb temperature of the air in degrees Celcius.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        meanRadiantTemperature_: A number representing the mean radiant temperature of the surrounding surfaces in degrees Celcius.  If no value is plugged in here, this component will assume that the mean radiant temperature is equal to air temperature value above.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        windSpeed_: A number representing the wind speed of the air in meters per second.  If no value is plugged in here, this component will assume a very low wind speed of 0.05 m/s, characteristic of most indoor conditions.  This input can also accept a list of wind speeds representing conditions at different times or the direct output of windSpeed from of the Import EPW component.
        _relativeHumidity: A number between 0 and 100 representing the relative humidity of the air in percentage.  This input can also accept a list of relative humidity values representing conditions at different times or the direct output of relativeHumidity from of the Import EPW component.
        ------------------------------: ...
        metabolicRate_: A number representing the metabolic rate of the human subject in met.  If no value is input here, the component will assume a metabolic rate of 1 met, which is the metabolic rate of a seated human being and roughly equal to 100 Watts for the average adult.  Sleeping human beings rarely drop below 0.8 met and exercising human beings can have metabolic rates as high as 6 to 8 met.  This input can also accept lists of metabolic rates.
        clothingLevel_: A number representing the clothing level of the human subject in clo.  If no value is input here, the component will assume a clothing level of 1 clo, which is roughly the insulation provided by a 3-piece suit. A person dressed in shorts and a T-shirt has a clothing level of roughly 0.5 clo and a person in a thick winter jacket can have a clothing level as high as 2 to 4 clo.  This input can also accept lists of clothing levels.
        ------------------------------: ...
        _runIt: Set to "True" to run the component ant calculate Standard Effective Temperature.  The default is set to "True" because the calculation is fast for individual conditions and only gets long if you try to use it for a whole year.
    Returns:
        readMe!: ...
        predictedMeanVote: The estimated predicted mean vote (PMV) of the test subject on a scale from -3 to +3.  A value of -3 inidcates extremely uncomfortably cold conditions while a value of +3 indicates extremely uncomfortably hot conditions.  A value of 0 indicates neither hot nor cold and the range of comfort is generally accepted as that between -1 and +1.
        percentPeopleDissatisfied: The estimated percentage of people dissatisfied (PPD) under the given input conditions as defined by the percent of people who would have a PMV less than -1 or greater than +1 under the conditions.  Note that, with this model, it is not possible to get a PPD of 0% and most engineers just aim to have a PPD below 20%.
        standardEffectiveTemperature: The standard effective temperature (SET) for the given input conditions in degrees Celcius. 
            Perhaps the most familiar application of SET is the temperature given by TV weathermen and women when they say that, even though the dry bulb temperature outside is a certain value, the temperature actually "feels like" something that is much higher or lower.
            Specifically, SET is definied as the equivalent temperature of an imaginary environment at 50% relative humidity, <0.1 m/s air speed, and mean radiant temperature equal to air temperature, in which the total heat loss from the skin of an imaginary occupant is the same as that from a person existing under the input conditions.
            It is also important to note that the imaginary occupant is modeled with an activity level of 1.0 met, a clothing level of 0.6 clo, and an external work value of 0 (meaning that all of the energy the body produces is heat).  The actual occupant in the real environment can have different values from these.

"""
ghenv.Component.Name = "Ladybug_Comfort Calculator"
ghenv.Component.NickName = 'ComfortCalculator'
ghenv.Component.Message = 'VER 0.0.57\nAPR_06_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Grasshopper.Kernel as gh
import math


def checkTheInputs():
    #Check lenth of the _dryBulbTemperature list and evaluate the contents.
    checkData1 = False
    airTemp = []
    airMultVal = False
    if len(_dryBulbTemperature) != 0:
        for item in _dryBulbTemperature:
            try:
                airTemp.append(float(item))
                checkData1 = True
            except: checkData1 = False
        if checkData1 == False:
            try:
                if _dryBulbTemperature[2] == 'Dry Bulb Temperature':
                    for item in _dryBulbTemperature[7:]:
                        airTemp.append(float(item))
                    checkData1 = True
            except: checkData1 = False
        if len(_dryBulbTemperature) > 1: airMultVal = True
        if checkData1 == False:
            warning = '_dryBulbTemperature input does not contain valid temperature values in degrees Celcius.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'Connect a temperature in degrees celcius for _dryBulbTemperature'
    
    #Check lenth of the meanRadiantTemperature_ list and evaluate the contents.
    checkData2 = False
    radTemp = []
    radMultVal = False
    if len(meanRadiantTemperature_) != 0:
        for item in meanRadiantTemperature_:
            try:
                radTemp.append(float(item))
                checkData2 = True
            except: checkData2 = False
        if checkData2 == False:
            try:
                if meanRadiantTemperature_[2] == 'Dry Bulb Temperature':
                    for item in meanRadiantTemperature_[7:]:
                        radTemp.append(float(item))
                    checkData2 = True
            except: checkData2 = False
        if len(meanRadiantTemperature_) > 1: radMultVal = True
        if checkData2 == False:
            warning = 'meanRadiantTemperature_ input does not contain valid temperature values in degrees Celcius.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData2 = True
        radTemp = airTemp
        if len (radTemp) > 1: radMultVal = True
        print 'No value connected for meanRadiantTemperature_.  It will be assumed that the radiant temperature is the same as the air temperature.'
    
    #Check lenth of the windSpeed_ list and evaluate the contents.
    checkData3 = False
    windSpeed = []
    windMultVal = False
    nonPositive = True
    if len(windSpeed_) != 0:
        for item in windSpeed_:
                try:
                    if float(item) >= 0:
                        windSpeed.append(float(item))
                        checkData3 = True
                    else: nonPositive = False
                except: checkData3 = False
        if nonPositive == False: checkData3 = False
        if checkData3 == False:
            try:
                if meanRadiantTemperature_[2] == 'Dry Bulb Temperature':
                    for item in meanRadiantTemperature_[7:]:
                        windSpeed.append(float(item))
                    checkData3 = True
            except: checkData3 = False
        if len(windSpeed_) > 1: windMultVal = True
        if checkData3 == False:
            warning = 'windSpeed_ input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData3 = True
        windSpeed = [0.05]
        print 'No value connected for windSpeed_.  It will be assumed that the wind speed is a low 0.05 m/s.'
    
    #Check lenth of the _relativeHumidity list and evaluate the contents.
    checkData4 = False
    relHumid = []
    humidMultVal = False
    nonValue = True
    if len(_relativeHumidity) != 0:
        for item in _relativeHumidity:
            try:
                if 0 <= float(item) <= 100:
                    relHumid.append(float(item))
                    checkData4 = True
                else: nonValue = False
            except:checkData4 = False
        if nonValue == False: checkData4 = False
        if checkData4 == False:
            try:
                if _relativeHumidity[2] == 'Relative Humidity':
                    for item in _relativeHumidity[7:]:
                        relHumid.append(float(item))
                    checkData4 = True
            except: checkData4 = False
        if len(_relativeHumidity) > 1: humidMultVal = True
        if checkData4 == False:
            warning = '_relativeHumidity input does not contain valid value.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'Connect a value for _relativeHumidity.'
    
    #Check lenth of the metabolicRate_ list and evaluate the contents.
    checkData5 = False
    metRate = []
    metMultVal = False
    nonVal = True
    if len(metabolicRate_) != 0:
        for item in metabolicRate_:
            try:
                if 0.5 <= float(item) <= 10:
                    metRate.append(float(item))
                    checkData5 = True
                else: nonVal = False
            except: checkData5 = False
        if nonVal == False: checkData5 = False
        if len(metabolicRate_) > 1: metMultVal = True
        if checkData5 == False:
            warning = 'metabolicRate_ input does not contain valid value. Note that metabolicRate_ must be a value between 0.5 and 10. Any thing outside of that is frankly not human.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData5 = True
        metRate = [1]
        print 'No value connected for metabolicRate_.  It will be assumed that the metabolic rate is that of a seated person at 1.2 met.'
    
    #Check lenth of the clothingLevel_ list and evaluate the contents.
    checkData6 = False
    cloLevel = []
    cloMultVal = False
    noVal = True
    if len(clothingLevel_) != 0:
        for item in clothingLevel_:
            try:
                if 0 <= float(item) <= 5:
                    cloLevel.append(float(item))
                    checkData6 = True
                else: noVal = False
            except: checkData6 = False
        if noVal == False: checkData6 = False
        if len(clothingLevel_) > 1: cloMultVal = True
        if checkData6 == False:
            warning = 'clothingLevel_ input does not contain valid value. Note that clothingLevel_ must be a value between 0 and 5. Any thing outside of that is frankly not human.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData6 = True
        cloLevel = [1]
        print 'No value connected for clothingLevel_.  It will be assumed that the clothing level is that of a person wearing a 3-piece suit at 1 clo.'
    
    #Finally, for those lists of length greater than 1, check to make sure that they are all the same length.
    checkData7 = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True:
        if airMultVal == True or radMultVal == True or windMultVal == True or humidMultVal == True or metMultVal == True or cloMultVal == True:
            listLenCheck = []
            if airMultVal == True: listLenCheck.append(len(airTemp))
            if radMultVal == True: listLenCheck.append(len(radTemp))
            if windMultVal == True: listLenCheck.append(len(windSpeed))
            if humidMultVal == True: listLenCheck.append(len(relHumid))
            if metMultVal == True: listLenCheck.append(len(metRate))
            if cloMultVal == True: listLenCheck.append(len(cloLevel))
            
            if all(x == listLenCheck[0] for x in listLenCheck) == True:
                checkData7 = True
                calcLength = listLenCheck[0]
                
                def duplicateData(data, calcLength):
                    dupData = []
                    for count in range(calcLength):
                        dupData.append(data[0])
                    return dupData
                
                if airMultVal == False: airTemp = duplicateData(airTemp, calcLength)
                if radMultVal == False: radTemp = duplicateData(radTemp, calcLength)
                if windMultVal == False: windSpeed = duplicateData(windSpeed, calcLength)
                if humidMultVal == False: relHumid = duplicateData(relHumid, calcLength)
                if metMultVal == False: metRate = duplicateData(metRate, calcLength)
                if cloMultVal == False: cloLevel = duplicateData(cloLevel, calcLength)
                exWork = duplicateData([0], calcLength)
                
            else:
                calcLength = None
                warning = 'If you have put in lists with multiple values, the lengths of these lists must match across the parameters.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData7 = True
            calcLength = 1
            exWork = [0]
    else:
        calcLength = 0
        exWork = []
    
    #If all of the checkDatas have been good to go, let's give a final go ahead.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True:
        checkData = True
    else:
        checkData = False
    
    #Let's return everything we need.
    return checkData, calcLength, airTemp, radTemp, windSpeed, relHumid, metRate, cloLevel, exWork



def comfPMVElevatedAirspeed(ta, tr, vel, rh, met, clo, wme):
    #This function accepts any input conditions (including low air speeds) but will return accurate values if the airspeed is above (>0.15m/s).
    #The function will return the following:
    #pmv : Predicted mean vote
    #ppd : Percent predicted dissatisfied [%]
    #ta_adj: Air temperature adjusted for air speed [C]
    #cooling_effect : The difference between the air temperature and adjusted air temperature [C]
    #set: The Standard Effective Temperature [C] (see below)
    
    r = []
    set = comfPierceSET(ta, tr, vel, rh, met , clo, wme)
    
    #This function is taken from the util.js script of the CBE comfort tool page and has been modified to include the fn inside the utilSecant function definition.
    def utilSecant(a, b, epsilon):
        # root-finding only
        res = []
        def fn(t):
            return (set - comfPierceSET(t, tr, 0.15, rh, met, clo, wme));
        f1 = fn(a)
        f2 = fn(b)
        if abs(f1) <= epsilon:
            res.append(a)
        elif abs(f2) <= epsilon:
            res.append(b)
        else:
            count = range(100)
            for i in count:
                if (b - a) != 0 and (f2 - f1) != 0:
                    slope = (f2 - f1) / (b - a)
                    c = b - f2/slope
                    f3 = fn(c)
                    if abs(f3) < epsilon:
                        res.append(c)
                    a = b
                    b = c
                    f1 = f2
                    f2 = f3
                else: pass
        res.append('NaN')
        return res[0]
    
    #This function is taken from the util.js script of the CBE comfort tool page and has been modified to include the fn inside the utilSecant function definition.
    def utilBisect(a, b, fn, epsilon, target):
        def fn(t):
            return (set - comfPierceSET(t, tr, 0.15, rh, met, clo, wme))
        while abs(b - a) > (2 * epsilon):
            midpoint = (b + a) / 2
            a_T = fn(a)
            b_T = fn(b)
            midpoint_T = fn(midpoint)
            if (a_T - target) * (midpoint_T - target) < 0:
                b = midpoint
            elif (b_T - target) * (midpoint_T - target) < 0:
                a = midpoint
            else: return -999
        return midpoint
    
    
    if vel <= 0.15:
        pmv, ppd = comfPMV(ta, tr, vel, rh, met, clo, wme)
        ta_adj = ta
        ce = 0
    else:
        ta_adj_l = -200
        ta_adj_r = 200
        eps = 0.001  # precision of ta_adj
        
        ta_adj = utilSecant(ta_adj_l, ta_adj_r, eps)
        if ta_adj == 'NaN':
            ta_adj = utilBisect(ta_adj_l, ta_adj_r, eps, 0)
        
        pmv, ppd = comfPMV(ta_adj, tr, 0.15, rh, met, clo, wme)
        ce = abs(ta - ta_adj)
    
    r.append(pmv)
    r.append(ppd)
    r.append(set)
    r.append(ta_adj)
    r.append(ce)
    
    return r


def comfPMV(ta, tr, vel, rh, met, clo, wme):
    #returns [pmv, ppd]
    #ta, air temperature (C)
    #tr, mean radiant temperature (C)
    #vel, relative air velocity (m/s)
    #rh, relative humidity (%) Used only this way to input humidity level
    #met, metabolic rate (met)
    #clo, clothing (clo)
    #wme, external work, normally around 0 (met)
    
    pa = rh * 10 * math.exp(16.6536 - 4030.183 / (ta + 235))
    
    icl = 0.155 * clo #thermal insulation of the clothing in M2K/W
    m = met * 58.15 #metabolic rate in W/M2
    w = wme * 58.15 #external work in W/M2
    mw = m - w #internal heat production in the human body
    if (icl <= 0.078):
        fcl = 1 + (1.29 * icl)
    else:
        fcl = 1.05 + (0.645 * icl)
    
    #heat transf. coeff. by forced convection
    hcf = 12.1 * math.sqrt(vel)
    taa = ta + 273
    tra = tr + 273
    tcla = taa + (35.5 - ta) / (3.5 * icl + 0.1)

    p1 = icl * fcl
    p2 = p1 * 3.96
    p3 = p1 * 100
    p4 = p1 * taa
    p5 = (308.7 - 0.028 * mw) + (p2 * math.pow(tra / 100, 4))
    xn = tcla / 100
    xf = tcla / 50
    eps = 0.00015
    
    n = 0
    while abs(xn - xf) > eps:
        xf = (xf + xn) / 2
        hcn = 2.38 * math.pow(abs(100.0 * xf - taa), 0.25)
        if (hcf > hcn):
            hc = hcf
        else:
            hc = hcn
        xn = (p5 + p4 * hc - p2 * math.pow(xf, 4)) / (100 + p3 * hc)
        n += 1
        if (n > 150):
            print 'Max iterations exceeded'
            return 1
        
    
    tcl = 100 * xn - 273
    
    #heat loss diff. through skin 
    hl1 = 3.05 * 0.001 * (5733 - (6.99 * mw) - pa)
    #heat loss by sweating
    if mw > 58.15:
        hl2 = 0.42 * (mw - 58.15)
    else:
        hl2 = 0
    #latent respiration heat loss 
    hl3 = 1.7 * 0.00001 * m * (5867 - pa)
    #dry respiration heat loss
    hl4 = 0.0014 * m * (34 - ta)
    #heat loss by radiation  
    hl5 = 3.96 * fcl * (math.pow(xn, 4) - math.pow(tra / 100, 4))
    #heat loss by convection
    hl6 = fcl * hc * (tcl - ta)
    
    ts = 0.303 * math.exp(-0.036 * m) + 0.028
    pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)
    ppd = 100.0 - 95.0 * math.exp(-0.03353 * pow(pmv, 4.0) - 0.2179 * pow(pmv, 2.0))
    
    r = []
    r.append(pmv)
    r.append(ppd)
    
    return r


def comfPierceSET(ta, tr, vel, rh, met, clo, wme):
    #Function to find the saturation vapor pressure, used frequently throughtout the comfPierceSET function.
    def findSaturatedVaporPressureTorr(T):
        #calculates Saturated Vapor Pressure (Torr) at Temperature T  (C)
        return math.exp(18.6686 - 4030.183 / (T + 235.0))
    
    #Key initial variables.
    VaporPressure = (rh * findSaturatedVaporPressureTorr(ta)) / 100
    AirVelocity = max(vel, 0.1)
    KCLO = 0.25
    BODYWEIGHT = 69.9
    BODYSURFACEAREA = 1.8258
    METFACTOR = 58.2
    SBC = 0.000000056697 # Stefan-Boltzmann constant (W/m2K4)
    CSW = 170
    CDIL = 120
    CSTR = 0.5
    
    TempSkinNeutral = 33.7 #setpoint (neutral) value for Tsk
    TempCoreNeutral = 36.49 #setpoint value for Tcr
    TempBodyNeutral = 36.49 #setpoint for Tb (.1*TempSkinNeutral + .9*TempCoreNeutral)
    SkinBloodFlowNeutral = 6.3 #neutral value for SkinBloodFlow

    #INITIAL VALUES - start of 1st experiment
    TempSkin = TempSkinNeutral
    TempCore = TempCoreNeutral
    SkinBloodFlow = SkinBloodFlowNeutral
    MSHIV = 0.0
    ALFA = 0.1
    ESK = 0.1 * met
    
    #Start new experiment here (for graded experiments)
    #UNIT CONVERSIONS (from input variables)
    
    p = 101325.0 / 1000 # This variable is the pressure of the atmosphere in kPa and was taken from the psychrometrics.js file of the CBE comfort tool.
    
    PressureInAtmospheres = p * 0.009869
    LTIME = 60
    TIMEH = LTIME / 60.0
    RCL = 0.155 * clo
    #AdjustICL(RCL, Conditions);  TH: I don't think this is used in the software
    
    FACL = 1.0 + 0.15 * clo #% INCREASE IN BODY SURFACE AREA DUE TO CLOTHING
    LR = 2.2 / PressureInAtmospheres #Lewis Relation is 2.2 at sea level
    RM = met * METFACTOR
    M = met * METFACTOR
    
    if clo <= 0:
        WCRIT = 0.38 * pow(AirVelocity, -0.29)
        ICL = 1.0
    else:
        WCRIT = 0.59 * pow(AirVelocity, -0.08)
        ICL = 0.45
    
    CHC = 3.0 * pow(PressureInAtmospheres, 0.53)
    CHCV = 8.600001 * pow((AirVelocity * PressureInAtmospheres), 0.53)
    CHC = max(CHC, CHCV)
    
    #initial estimate of Tcl
    CHR = 4.7
    CTC = CHR + CHC
    RA = 1.0 / (FACL * CTC) #resistance of air layer to dry heat transfer
    TOP = (CHR * tr + CHC * ta) / CTC
    TCL = TOP + (TempSkin - TOP) / (CTC * (RA + RCL))

    # ========================  BEGIN ITERATION
    #
    # Tcl and CHR are solved iteratively using: H(Tsk - To) = CTC(Tcl - To),
    # where H = 1/(Ra + Rcl) and Ra = 1/Facl*CTC
    
    TCL_OLD = TCL
    TIME = range(LTIME)
    flag = True
    for TIM in TIME:
        if flag == True:
            while abs(TCL - TCL_OLD) > 0.01:
                TCL_OLD = TCL
                CHR = 4.0 * SBC * pow(((TCL + tr) / 2.0 + 273.15), 3.0) * 0.72
                CTC = CHR + CHC
                RA = 1.0 / (FACL * CTC) #resistance of air layer to dry heat transfer
                TOP = (CHR * tr + CHC * ta) / CTC
                TCL = (RA * TempSkin + RCL * TOP) / (RA + RCL)
        flag = False
        DRY = (TempSkin - TOP) / (RA + RCL)
        HFCS = (TempCore - TempSkin) * (5.28 + 1.163 * SkinBloodFlow)
        ERES = 0.0023 * M * (44.0 - VaporPressure)
        CRES = 0.0014 * M * (34.0 - ta)
        SCR = M - HFCS - ERES - CRES - wme
        SSK = HFCS - DRY - ESK
        TCSK = 0.97 * ALFA * BODYWEIGHT
        TCCR = 0.97 * (1 - ALFA) * BODYWEIGHT
        DTSK = (SSK * BODYSURFACEAREA) / (TCSK * 60.0)# //deg C per minute
        DTCR = SCR * BODYSURFACEAREA / (TCCR * 60.0)# //deg C per minute
        TempSkin = TempSkin + DTSK
        TempCore = TempCore + DTCR
        TB = ALFA * TempSkin + (1 - ALFA) * TempCore
        SKSIG = TempSkin - TempSkinNeutral
        WARMS = (SKSIG > 0) * SKSIG
        COLDS = ((-1.0 * SKSIG) > 0) * (-1.0 * SKSIG)
        CRSIG = (TempCore - TempCoreNeutral)
        WARMC = (CRSIG > 0) * CRSIG
        COLDC = ((-1.0 * CRSIG) > 0) * (-1.0 * CRSIG)
        BDSIG = TB - TempBodyNeutral
        WARMB = (BDSIG > 0) * BDSIG
        COLDB = ((-1.0 * BDSIG) > 0) * (-1.0 * BDSIG)
        SkinBloodFlow = (SkinBloodFlowNeutral + CDIL * WARMC) / (1 + CSTR * COLDS)
        if SkinBloodFlow > 90.0: SkinBloodFlow = 90.0
        if SkinBloodFlow < 0.5: SkinBloodFlow = 0.5
        REGSW = CSW * WARMB * math.exp(WARMS / 10.7)
        if REGSW > 500.0: REGSW = 500.0
        ERSW = 0.68 * REGSW
        REA = 1.0 / (LR * FACL * CHC) #evaporative resistance of air layer
        RECL = RCL / (LR * ICL) #evaporative resistance of clothing (icl=.45)
        EMAX = (findSaturatedVaporPressureTorr(TempSkin) - VaporPressure) / (REA + RECL)
        PRSW = ERSW / EMAX
        PWET = 0.06 + 0.94 * PRSW
        EDIF = PWET * EMAX - ERSW
        ESK = ERSW + EDIF
        if PWET > WCRIT:
            PWET = WCRIT
            PRSW = WCRIT / 0.94
            ERSW = PRSW * EMAX
            EDIF = 0.06 * (1.0 - PRSW) * EMAX
            ESK = ERSW + EDIF
        if EMAX < 0:
            EDIF = 0
            ERSW = 0
            PWET = WCRIT
            PRSW = WCRIT
            ESK = EMAX
        ESK = ERSW + EDIF
        MSHIV = 19.4 * COLDS * COLDC
        M = RM + MSHIV
        ALFA = 0.0417737 + 0.7451833 / (SkinBloodFlow + .585417)
    
    
    #Define new heat flow terms, coeffs, and abbreviations
    STORE = M - wme - CRES - ERES - DRY - ESK #rate of body heat storage
    HSK = DRY + ESK #total heat loss from skin
    RN = M - wme #net metabolic heat production
    ECOMF = 0.42 * (RN - (1 * METFACTOR))
    if ECOMF < 0.0: ECOMF = 0.0 #from Fanger
    EREQ = RN - ERES - CRES - DRY
    EMAX = EMAX * WCRIT
    HD = 1.0 / (RA + RCL)
    HE = 1.0 / (REA + RECL)
    W = PWET
    PSSK = findSaturatedVaporPressureTorr(TempSkin)
    #Definition of ASHRAE standard environment... denoted "S"
    CHRS = CHR
    if met < 0.85:
        CHCS = 3.0
    else:
        CHCS = 5.66 * pow((met - 0.85), 0.39)
        if CHCS < 3.0: CHCS = 3.0
    
    CTCS = CHCS + CHRS
    RCLOS = 1.52 / ((met - wme / METFACTOR) + 0.6944) - 0.1835
    RCLS = 0.155 * RCLOS
    FACLS = 1.0 + KCLO * RCLOS
    FCLS = 1.0 / (1.0 + 0.155 * FACLS * CTCS * RCLOS)
    IMS = 0.45
    ICLS = IMS * CHCS / CTCS * (1 - FCLS) / (CHCS / CTCS - FCLS * IMS)
    RAS = 1.0 / (FACLS * CTCS)
    REAS = 1.0 / (LR * FACLS * CHCS)
    RECLS = RCLS / (LR * ICLS)
    HD_S = 1.0 / (RAS + RCLS)
    HE_S = 1.0 / (REAS + RECLS)
    
    #SET* (standardized humidity, clo, Pb, and CHC)
    #determined using Newton's iterative solution
    #FNERRS is defined in the GENERAL SETUP section above
    
    DELTA = .0001
    dx = 100.0
    X_OLD = TempSkin - HSK / HD_S #lower bound for SET
    while abs(dx) > .01:
        ERR1 = (HSK - HD_S * (TempSkin - X_OLD) - W * HE_S * (PSSK - 0.5 * findSaturatedVaporPressureTorr(X_OLD)))
        ERR2 = (HSK - HD_S * (TempSkin - (X_OLD + DELTA)) - W * HE_S * (PSSK - 0.5 * findSaturatedVaporPressureTorr((X_OLD + DELTA))))
        X = X_OLD - DELTA * ERR1 / (ERR2 - ERR1)
        dx = X - X_OLD
        X_OLD = X
    
    return X






# Cehck the inputs and organize the incoming data into streams that can be run t
checkData = False
if _runIt == True:
    checkData, calcLength, airTemp, radTemp, windSpeed, relHumid, metRate, cloLevel, exWork = checkTheInputs()

#If things are good, run it through the PMV model.
if checkData == True:
    predictedMeanVote = []
    percentPeopleDissatisfied = []
    standardEffectiveTemperature = []
    for count in range(calcLength):
        pmv, ppd, set, taAdj, coolingEffect = comfPMVElevatedAirspeed(airTemp[count], radTemp[count], windSpeed[count], relHumid[count], metRate[count], cloLevel[count], exWork[count])
        predictedMeanVote.append(pmv)
        percentPeopleDissatisfied.append(ppd)
        standardEffectiveTemperature.append(set)