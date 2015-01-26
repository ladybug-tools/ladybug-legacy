# Predicted Mean Vote Comfort Calculator
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate comfort metrics of Predicted Mean Vote (PMV), the Percent of People Dissatisfied (PPD), and the Standard Effective Temperature (SET) for a set of climate conditions and occupant behavior/clothing.
This component can also calculate Outdoor Standard Effective Temperature (OUT-SET) if EPW weather data is connected.  HOWEVER, if you are interested in knowing whether outdoor conditions are actually comfortable, it is highly recommended that you use the Ladybug UTCI Comfort Calculator.  OUT-SET has been shown to be a poor indicator of outdoor comfort and is better used as a tool to help understand what clothing and metabolic rate a comfortable person might have in the outdoors AFTER running a UTCI study.
_
Predicted Mean Vote (PMV) is a seven-point scale of occupant comfort from cold (-3) to hot (+3) that was used in the comfort surveys of P.O. Fanger, who initially developed the scale and the PMV comfort model off of it. Each interger value of the PMV scale indicates the following: -3:Cold, -2:Cool, -1:Slightly Cool, 0:Neutral, +1:Slightly Warm, +2:Warm, +3:Hot.  The range of comfort is generally accepted as a PMV between -1 and +1.  Exceeding +1 will result in an uncomfortably warm occupant while dropping below -1 will result in an uncomfortably cool occupant.  PMV is a MEAN vote because is meant to represent the average vote of all people under the input conditions.
This component will output the PMV of the occupant for the input conditions as well as an estimated Percentage of People Dissatisfied (PPD) under the given conditions.  PPD refers to the perceont of people that would give a PMV greater than/equal to 1 or less than/equal to -1.  Note that, with this model, it is not possible to get a PPD of 0% and most engineers just aim to have a PPD below 20% when designing a HVAC system.
This component will also output Standard Effective Temperature (SET), which is an ajusted temperature scale meant to reflect the heat stress or cold felt by the occupant.  Specifically, SET is definied as the equivalent temperature of an imaginary environment at 50% relative humidity, <0.1 m/s air speed, and mean radiant temperature equal to air temperature, in which the total heat loss from the skin of an imaginary occupant is the same as that from a person existing under the input conditions. It is also important to note that the imaginary occupant is modeled with an activity level of 1.0 met and a clothing level of 0.6 clo.  The actual occupant in the real environment can have different values from these.
_
The original PMV studies by Fanger involved placing subjects in an air conditioned climate chamber for an hour in which the subjects had no means to adjust their conditions to make them comfortable.  Subjects where then asked to pick an interger on the PMV scale.  Since PMV subjects could not change their layers of clothing or open windows to make themselves comfortable, the PMV model is most useful when applied to these conditions of an air conditioned building in which users cannot open windows, turn on fans or change dress code.  For comfort in conditions where people can adjust these factors, the adaptive comfort calculator or UTCI comfort calculator would be most useful.
_
The comfort models that make this component possible were translated to python from a series of validated javascript comfort models coded at the Berkely Center for the Built Environment (CBE).  The PMV model used by both the CBE Tool and this component was originally published in ASHARAE 55.
Special thanks goes to the authors of the online CBE Thermal Comfort Tool who first coded the javascript comfort models: Hoyt Tyler, Schiavon Stefano, Piccioli Alberto, Moon Dustin, and Steinfeld Kyle. http://cbe.berkeley.edu/comforttool/
-
Provided by Ladybug 0.0.58
    
    Args:
        _dryBulbTemperature: A number representing the dry bulb temperature of the air in degrees Celcius.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        meanRadiantTemperature_: A number representing the mean radiant temperature of the surrounding surfaces in degrees Celcius.  If no value is plugged in here, this component will assume that the mean radiant temperature is equal to air temperature value above.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        windSpeed_: A number representing the wind speed of the air in meters per second.  If no value is plugged in here, this component will assume a very low wind speed of 0.05 m/s, characteristic of most indoor conditions.  This input can also accept a list of wind speeds representing conditions at different times or the direct output of windSpeed from of the Import EPW component.
        _relativeHumidity: A number between 0 and 100 representing the relative humidity of the air in percentage.  This input can also accept a list of relative humidity values representing conditions at different times or the direct output of relativeHumidity from of the Import EPW component.
        ------------------------------: ...
        metabolicRate_: A number representing the metabolic rate of the human subject in met.  This input can also accept text inputs for different activities.  Acceptable text inputs include Sleeping, Reclining, Sitting, Typing, Standing, Driving, Cooking, House Cleaning, Walking, Walking 2mph, Walking 3mph, Walking 4mph, Running 9mph, Lifting 10lbs, Lifting 100lbs, Shoveling, Dancing, and Basketball.  If no value is input here, the component will assume a metabolic rate of 1 met, which is the metabolic rate of a seated human being.  This input can also accept lists of metabolic rates.
        clothingLevel_: A number representing the clothing level of the human subject in clo.  If no value is input here, the component will assume a clothing level of 1 clo, which is roughly the insulation provided by a 3-piece suit. A person dressed in shorts and a T-shirt has a clothing level of roughly 0.5 clo and a person in a thick winter jacket can have a clothing level as high as 2 to 4 clo.  This input can also accept lists of clothing levels.
        ------------------------------: ...
        comfortPar_: Optional comfort parameters from the "Ladybug_PMV Comfort Parameters" component.  Use this to adjust maximum and minimum acceptable humidity ratios.  These comfortPar can also change whether comfort is defined by eighty or ninety percent of people comfortable.  By default, comfort is defined as 90% of the occupants comfortable and there are no limits on humidity when there is no thermal stress.
        analysisPeriod_: An optional analysis period from the Analysis Period component.  If no Analysis period is given and epw data from the ImportEPW component has been connected, the analysis will be run for the enitre year.
        calcBalanceTemperature_: Set to "True" to have the component calculate the balance temperature for the input windSpeed_, _relativeHumidity, metabolicRate_, and clothingLevel_.  The balance temperature is essentially the temperature for these conditions at which the PMV is equal to 0 (or the energy flowing into the human body is equal to the energy flowing out).  Note that calculating the balance temperature for a whole year with epw windspeed can take as long as 10 minutes and so, by default, this option is set to "False".
        _runIt: Set to "True" to run the component and calculate the PMV comfort metrics.
    Returns:
        readMe!: ...
        ------------------------------: ...
        predictedMeanVote: The estimated predicted mean vote (PMV) of test subjects under the input conditions.  PMV is a seven-point scale from cold (-3) to hot (+3) that was used in comfort surveys of P.O. Fanger.  Each interger value of the scale indicates the following: -3:Cold, -2:Cool, -1:Slightly Cool, 0:Neutral, +1:Slightly Warm, +2:Warm, +3:Hot.  The range of comfort is generally accepted as a PMV between -1 and +1.  Exceeding +1 will result in an uncomfortably warm occupant while dropping below -1 will result in an uncomfortably cool occupant.  For detailed information on the PMV scale, see P.O. Fanger's original paper: Fanger, P Ole (1970). Thermal Comfort: Analysis and applications in environmental engineering.
        percentPeopleDissatisfied: The estimated percentage of people dissatisfied (PPD) under the given input conditions.  Specifically, this is defined by the percent of people who would have a PMV less than -1 or greater than +1 under the conditions.  Note that, with this model, it is not possible to get a PPD of 0% and most engineers just aim to have a PPD below 20%.
        standardEffectiveTemperature: The standard effective temperature (SET) for the given input conditions in degrees Celcius. 
            SET is an ajusted temperature scale meant to reflect the heat stress or cold felt by the occupant.
            Specifically, SET is definied as the equivalent temperature of an imaginary environment at 50% relative humidity, <0.1 m/s air speed, and mean radiant temperature equal to air temperature, in which the total heat loss from the skin of an imaginary occupant is the same as that from a person existing under the input conditions.
            It is also important to note that the imaginary occupant is modeled with an activity level of 1.0 met and a clothing level of 0.6 clo.  The actual occupant in the real environment can have different values from these.
        ------------------------------: ...
        comfortableOrNot: A stream of 0's and 1's (or "False" and "True" values) indicating whether the occupant is comfortable for each hour of the input conditions.  0 indicates that the occupant is not comfortable while 1 indicates that the occupant is comfortable.
        percentOfTimeComfortable: The percent of input conditions for which the occupant is comfortable.  Note that this output is only menaingful when multiple values are connected for the input conditions.
        ------------------------------: ...
        balanceTemperature: The balance temperature is the temperature for the input windSpeed_, _relativeHumidity, metabolicRate_, and clothingLevel_ at which the PMV is equal to 0 (or the energy flowing into the human body is equal to the energy flowing out).  Setting the dry bulb and radiant temperatures to this value will produce a PMV of 0 and will yield the lowest possible PPD.

"""
ghenv.Component.Name = "Ladybug_PMV Comfort Calculator"
ghenv.Component.NickName = 'PMVComfortCalculator'
ghenv.Component.Message = 'VER 0.0.58\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import Grasshopper.Kernel as gh
import math
import scriptcontext as sc



# Manage component outputs
outputsDict = {
     
0: ["readMe!", "..."],
1: ["------------------------------", "------------------------------"],
2: ["predictedMeanVote", "The estimated predicted mean vote (PMV) of test subjects under the input conditions.  PMV is a seven-point scale from cold (-3) to hot (+3) that was used in comfort surveys of P.O. Fanger.  Each interger value of the scale indicates the following: -3:Cold, -2:Cool, -1:Slightly Cool, 0:Neutral, +1:Slightly Warm, +2:Warm, +3:Hot.  The range of comfort is generally accepted as a PMV between -1 and +1.  Exceeding +1 will result in an uncomfortably warm occupant while dropping below -1 will result in an uncomfortably cool occupant.  For detailed information on the PMV scale, see P.O. Fanger's original paper: Fanger, P Ole (1970). Thermal Comfort: Analysis and applications in environmental engineering."],
3: ["percentPeopleDissatisfied", "The estimated percentage of people dissatisfied (PPD) under the given input conditions.  Specifically, this is defined by the percent of people who would have a PMV less than -1 or greater than +1 under the conditions.  Note that, with this model, it is not possible to get a PPD of 0% and most engineers just aim to have a PPD below 20%."],
4: ["standardEffectiveTemperature", "The standard effective temperature (SET) for the given input conditions in degrees Celcius. SET is an ajusted temperature scale meant to reflect the heat stress or cold felt by the occupant. Specifically, SET is definied as the equivalent temperature of an imaginary environment at 50% relative humidity, <0.1 m/s air speed, and mean radiant temperature equal to air temperature, in which the total heat loss from the skin of an imaginary occupant is the same as that from a person existing under the input conditions. It is also important to note that the imaginary occupant is modeled with an activity level of 1.0 met and a clothing level of 0.6 clo.  The actual occupant in the real environment can have different values from these."],
5: ["------------------------------", "------------------------------"],
6: ["comfortableOrNot", "A stream of 0's and 1's (or 'False' and 'True' values) indicating whether the occupant is comfortable for each hour of the input conditions.  0 indicates that the occupant is not comfortable while 1 indicates that the occupant is comfortable."],
7: ["percentOfTimeComfortable", "The percent of input conditions for which the occupant is comfortable.  Note that this output is only menaingful when multiple values are connected for the input conditions."],
8: ["------------------------------", "------------------------------"],
9: ["balanceTemperature", "The balance temperature is the temperature for the input windSpeed_, _relativeHumidity, metabolicRate_, and clothingLevel_ at which the PMV is equal to 0 (or the energy flowing into the human body is equal to the energy flowing out).  Setting the dry bulb and radiant temperatures to this value will produce a PMV of 0 and will yield the lowest possible PPD."],
}

numOutputs = ghenv.Component.Params.Output.Count
outSet = False
try:
    if _dryBulbTemperature[2] == "Dry Bulb Temperature":
        outSet = True
except: pass
try:
    if meanRadiantTemperature_[2] == "Dry Bulb Temperature" or meanRadiantTemperature_[2] == "Solar-Adjusted Mean Radiant Temperature":
        outSet = True
except: pass
try:
    if windSpeed_[2] == "Wind Speed":
        outSet = True
except: pass

if outSet == True:
    message1 = "Because the PMV comfort model is derived from indoor comfort studies and you have hooked up outdoor data, the values out of this component only indicate how much the outdoor condtions should be changed in order to make indoor conditions comfortable."
    message2 = "They do not idicate whether someone will actually be comfortable outdoors."
    message3 = "If you are interested in whether the outdoors are actually comfortable, you should use the Ladybug Outdoor Comfort Calculator."
    print message1, message2, message3
    m = gh.GH_RuntimeMessageLevel.Remark
    ghenv.Component.AddRuntimeMessage(m, message1)
    ghenv.Component.AddRuntimeMessage(m, message2)
    ghenv.Component.AddRuntimeMessage(m, message3)

if outSet == True:
    for output in range(numOutputs):
        if output == 2:
            ghenv.Component.Params.Output[output].NickName = "--------------------"
            ghenv.Component.Params.Output[output].Name = "--------------------"
            ghenv.Component.Params.Output[output].Description = "Because the PMV comfort model is derived from indoor comfort studies and you have hooked up outdoor data, the PMV values out of this component are not meaningful."
        elif output == 3:
            ghenv.Component.Params.Output[output].NickName = "--------------------"
            ghenv.Component.Params.Output[output].Name = "--------------------"
            ghenv.Component.Params.Output[output].Description = "Because the PMV comfort model is derived from indoor comfort studies and you have hooked up outdoor data, the PPD values out of this component are not meaninful."
        elif output == 4:
            ghenv.Component.Params.Output[output].NickName = "OUT_SET"
            ghenv.Component.Params.Output[output].Name = "OUT_SET"
            ghenv.Component.Params.Output[output].Description = "The Outdoor Standard Effective Temperature (OUT_SET) in degrees Celcius.  OUT_SET is an ajusted temperature scale meant to reflect the heat stress or cold felt by an individual and has passed peer review as an indicator of outdoor comfort.  HOWEVER, if you are interested in knowing whether outdoor conditions are actually comfortable, it is highly recommended that you use the Ladybug UTCI Comfort Calculator.  OUT-SET has been shown to be a poor indicator of outdoor comfort and is better used as a tool to help understand what clothing and metabolic rate a comfortable person might have in the outdoors AFTER running a UTCI study."
        elif output == 6:
            ghenv.Component.Params.Output[output].NickName = "restrictedComfOrNot"
            ghenv.Component.Params.Output[output].Name = "restrictedComfOrNot"
            ghenv.Component.Params.Output[output].Description = "Because the PMV comfort model is derived from indoor comfort studies and you have hooked up outdoor data, the comfortableOrNot values out of this component should be taken with a grain of salt.  The comfort here represents a very narrow range because you are restricting the theoretical person's clothing and metabolic rate, which is normally unrestricted in the outdoors."
        elif output == 7:
            ghenv.Component.Params.Output[output].NickName = "restrictedPercentComf"
            ghenv.Component.Params.Output[output].Name = "restrictedPercentComf"
            ghenv.Component.Params.Output[output].Description = "Because the PMV comfort model is derived from indoor comfort studies and you have hooked up outdoor data, the percentOfTimeComfortable values out of this component should be taken with a grain of salt.  The comfort here represents a very narrow range because you are restricting the theoretical person's clothing and metabolic rate, which is normally unrestricted in the outdoors."
        else: pass
else:
    for output in range(numOutputs):
        if output == 2 or output == 3 or output == 4 or output == 6 or output == 7:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
        else: pass
    
ghenv.Component.Attributes.Owner.OnPingDocument()



def checkTheInputs():
    #Define a value that will indicate whether someone has hooked up epw data.
    epwData = False
    epwStr = []
    
    #Check lenth of the _dryBulbTemperature list and evaluate the contents.
    checkData1 = False
    airTemp = []
    airMultVal = False
    if len(_dryBulbTemperature) != 0:
        try:
            if "Temperature" in _dryBulbTemperature[2]:
                airTemp = _dryBulbTemperature[7:]
                checkData1 = True
                epwData = True
                epwStr = _dryBulbTemperature[0:7]
        except: pass
        if checkData1 == False:
            for item in _dryBulbTemperature:
                try:
                    airTemp.append(float(item))
                    checkData1 = True
                except: checkData1 = False
        if len(airTemp) > 1: airMultVal = True
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
        try:
            if "Temperature" in meanRadiantTemperature_[2]:
                radTemp = meanRadiantTemperature_[7:]
                checkData2 = True
                epwData = True
                epwStr = meanRadiantTemperature_[0:7]
        except: pass
        if checkData2 == False:
            for item in meanRadiantTemperature_:
                try:
                    radTemp.append(float(item))
                    checkData2 = True
                except: checkData2 = False
        if len(radTemp) > 1: radMultVal = True
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
        try:
            if windSpeed_[2] == 'Wind Speed':
                windSpeed = windSpeed_[7:]
                checkData3 = True
                epwData = True
                epwStr = windSpeed_[0:7]
        except: pass
        if checkData3 == False:
            for item in windSpeed_:
                try:
                    if float(item) >= 0:
                        windSpeed.append(float(item))
                        checkData3 = True
                    else: nonPositive = False
                except: checkData3 = False
        if nonPositive == False: checkData3 = False
        if len(windSpeed) > 1: windMultVal = True
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
        try:
            if "Humidity" in _relativeHumidity[2]:
                relHumid = _relativeHumidity[7:]
                checkData4 = True
                epwData = True
                epwStr = _relativeHumidity[0:7]
        except: pass
        if checkData4 == False:
            for item in _relativeHumidity:
                try:
                    if 0 <= float(item) <= 100:
                        relHumid.append(float(item))
                        checkData4 = True
                    else: nonValue = False
                except:checkData4 = False
        if nonValue == False: checkData4 = False
        if len(relHumid) > 1: humidMultVal = True
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
        if checkData5 == False:
            try:
                if str(metabolicRate_[0]) == "Sleeping": metRate.append(0.7)
                elif str(metabolicRate_[0]) == "Reclining": metRate.append(0.8)
                elif str(metabolicRate_[0]) == "Sitting": metRate.append(1.0)
                elif str(metabolicRate_[0]) == "Typing": metRate.append(1.1)
                elif str(metabolicRate_[0]) == "Standing": metRate.append(1.2)
                elif str(metabolicRate_[0]) == "Driving": metRate.append(1.5)
                elif str(metabolicRate_[0]) == "Cooking": metRate.append(1.8)
                elif str(metabolicRate_[0]) == "House Cleaning": metRate.append(2.7)
                elif str(metabolicRate_[0]) == "Walking": metRate.append(1.7)
                elif str(metabolicRate_[0]) == "Walking 2mph": metRate.append(2.0)
                elif str(metabolicRate_[0]) == "Walking 3mph": metRate.append(2.6)
                elif str(metabolicRate_[0]) == "Walking 4mph": metRate.append(3.8)
                elif str(metabolicRate_[0]) == "Running 9mph": metRate.append(9.5)
                elif str(metabolicRate_[0]) == "Lifting 10lbs": metRate.append(2.1)
                elif str(metabolicRate_[0]) == "Lifting 100lbs": metRate.append(4.0)
                elif str(metabolicRate_[0]) == "Shoveling": metRate.append(4.4)
                elif str(metabolicRate_[0]) == "Dancing": metRate.append(3.4)
                elif str(metabolicRate_[0]) == "Basketball": metRate.append(6.3)
                else: pass
            except: pass
        if len(metRate) > 0: checkData5 = True
        if nonVal == False: checkData5 = False
        if len(metRate) > 1: metMultVal = True
        if checkData5 == False:
            warning = 'metabolicRate_ input does not contain valid value. Note that metabolicRate_ must be a value between 0.5 and 10. Any thing outside of that is frankly not human.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData5 = True
        metRate = [1]
        print 'No value connected for metabolicRate_.  It will be assumed that the metabolic rate is that of a seated person at 1 met.'
    
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
        if len(cloLevel) > 1: cloMultVal = True
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
                warning = 'If you have put in lists with multiple values, the lengths of these lists must match across the parameters or you have a single value for a given parameter to be applied to all values in the list.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData7 = True
            calcLength = 1
            exWork = [0]
    else:
        calcLength = 0
        exWork = []
    
    #If there are comfort parameters hooked up, read them out.
    checkData8 = True
    print comfortPar_
    if comfortPar_ != []:
        try:
            eightyPercentComfortable = bool(comfortPar_[0])
            humidRatioUp = float(comfortPar_[1])
            humidRatioLow = float(comfortPar_[2])
        except:
            eightyPercentComfortable = False
            humidRatioUp = 0.03
            humidRatioLow = 0.0
            checkData8 = False
            warning = 'The comfortPar are not valid comfort parameters from the Ladybug_Comfort Parameters component.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        eightyPercentComfortable = False
        humidRatioUp = 0.03
        humidRatioLow = 0.0
    
    #If all of the checkDatas have been good to go, let's give a final go ahead.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True:
        checkData = True
    else:
        checkData = False
    
    #Let's return everything we need.
    return checkData, epwData, epwStr, calcLength, airTemp, radTemp, windSpeed, relHumid, metRate, cloLevel, exWork, eightyPercentComfortable, humidRatioUp, humidRatioLow



def main():
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
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        
        #Check the inputs and organize the incoming data into streams that can be run throught the comfort model.
        checkData = False
        checkData, epwData, epwStr, calcLength, airTemp, radTemp, windSpeed, relHumid, metRate, cloLevel, exWork, eightyPercentComfortable, humidRatioUp, humidRatioLow = checkTheInputs()
        
        #Check if there is an analysisPeriod_ connected and, if not, run it for the whole year.
        if calcLength == 8760 and len(analysisPeriod_)!=0 and epwData == True:
            HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod_, 1)
            runPeriod = analysisPeriod_
            calcLength = len(HOYS)
        elif len(analysisPeriod_)==0 and epwData == True:
            HOYS = range(calcLength)
            runPeriod = [epwStr[5], epwStr[6]]
        else:
            HOYS = range(calcLength)
            runPeriod = [(1,1,1), (12,31,24)]
        
        #If things are good, run it through the comfort model.
        predictedMeanVote = []
        percentPeopleDissatisfied = []
        standardEffectiveTemperature = []
        comfortableOrNot = []
        percentOfTimeComfortable = None
        if checkData == True and epwData == True and 'for' not in epwStr[2]:
            predictedMeanVote.extend([epwStr[0], epwStr[1], 'Predicted Mean Vote', '+3 hot, +2 warm, +1 slightly warm, 0 neutral, -1 slightly cool, -2 cool, -3 cold', epwStr[4], runPeriod[0], runPeriod[1]])
            percentPeopleDissatisfied.extend([epwStr[0], epwStr[1], 'Percentage of People Dissatisfied', '%', epwStr[4], runPeriod[0], runPeriod[1]])
            standardEffectiveTemperature.extend([epwStr[0], epwStr[1], 'Standard Effective Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
            comfortableOrNot.extend([epwStr[0], epwStr[1], 'Comfortable Or Not', 'Boolean', epwStr[4], runPeriod[0], runPeriod[1]])
        elif checkData == True and epwData == True and 'for' in epwStr[2]:
            predictedMeanVote.extend([epwStr[0], epwStr[1], 'Predicted Mean Vote' + ' for ' + epwStr[2].split('for ')[-1], '+3 hot, +2 warm, +1 slightly warm, 0 neutral, -1 slightly cool, -2 cool, -3 cold', epwStr[4], runPeriod[0], runPeriod[1]])
            percentPeopleDissatisfied.extend([epwStr[0], epwStr[1], 'Percentage of People Dissatisfied' + ' for ' + epwStr[2].split('for ')[-1], '%', epwStr[4], runPeriod[0], runPeriod[1]])
            standardEffectiveTemperature.extend([epwStr[0], epwStr[1], 'Standard Effective Temperature' + ' for ' + epwStr[2].split('for ')[-1], 'C', epwStr[4], runPeriod[0], runPeriod[1]])
            comfortableOrNot.extend([epwStr[0], epwStr[1], 'Comfortable Or Not' + ' for ' + epwStr[2].split('for ')[-1], 'Boolean', epwStr[4], runPeriod[0], runPeriod[1]])
        if checkData == True:
            try:
                for count in HOYS:
                    # let the user cancel the process
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    
                    pmv, ppd, set, taAdj, coolingEffect = lb_comfortModels.comfPMVElevatedAirspeed(airTemp[count], radTemp[count], windSpeed[count], relHumid[count], metRate[count], cloLevel[count], exWork[count])
                    predictedMeanVote.append(pmv)
                    percentPeopleDissatisfied.append(ppd)
                    standardEffectiveTemperature.append(set)
                    if humidRatioUp != 0.03 or humidRatioLow != 0.0:
                        HR, EN, vapPress, satPress = lb_comfortModels.calcHumidRatio(airTemp[count], relHumid[count], 101325)
                        if eightyPercentComfortable == True:
                            if ppd < 20 and HR < humidRatioUp and HR > humidRatioLow: comfortableOrNot.append(1)
                            else: comfortableOrNot.append(0)
                        else:
                            if ppd < 10 and HR < humidRatioUp and HR > humidRatioLow: comfortableOrNot.append(1)
                            else: comfortableOrNot.append(0)
                    else:
                        if eightyPercentComfortable == True:
                            if ppd < 20: comfortableOrNot.append(1)
                            else: comfortableOrNot.append(0)
                        else:
                            if ppd < 10: comfortableOrNot.append(1)
                            else: comfortableOrNot.append(0)
                if epwData == True:
                    percentOfTimeComfortable = ((sum(comfortableOrNot[7:]))/calcLength)*100
                else: percentOfTimeComfortable = ((sum(comfortableOrNot))/calcLength)*100
            except:
                predictedMeanVote = []
                percentPeopleDissatisfied = []
                standardEffectiveTemperature = []
                comfortableOrNot = []
                percentOfTimeComfortable = None
                print "The calculation has been terminated by the user!"
                e = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
        
        #If things are good and the user has set the calcBalanceTemperature to "True", calculate the balance temperature.
        balanceTemperature = []
        if checkData == True and calcBalanceTemperature_ == True and epwData == True:
            balanceTemperature.extend([epwStr[0], epwStr[1], 'Balance Temperature', 'C', epwStr[4], runPeriod[0], runPeriod[1]])
        if checkData == True and calcBalanceTemperature_ == True:
            try:
                for count in HOYS:
                    # let the user cancel the process
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    
                    if count == HOYS[0]:
                        balTemp = 24
                    else: pass
                    
                    balTemp = lb_comfortModels.calcBalTemp(balTemp, windSpeed[count], relHumid[count], metRate[count], cloLevel[count], exWork[count])
                    balanceTemperature.append(balTemp)
            except:
                balanceTemperature = []
                print "The balance temperature calculation has been terminated by the user!  The initial calculation of PMV, PPD and SET finished and has been output."
                e = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(e, "The balance temperature calculation has been terminated by the user!  The initial calculation of PMV, PPD and SET finished and has been output.")
        
        #Return all of the info.
        return predictedMeanVote, percentPeopleDissatisfied, standardEffectiveTemperature, comfortableOrNot, percentOfTimeComfortable, balanceTemperature
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return [None, None, None, None, None, None]




if _runIt == True:
    results = main()
    if results!=-1:
        predictedMeanVote, percentPeopleDissatisfied, standardEffectiveTemperature, \
        comfortableOrNot, percentOfTimeComfortable, balanceTemperature = results
        
        if outSet == True:
            indoorEquivalentPMV = predictedMeanVote
            indoorEquivalentPPD = percentPeopleDissatisfied
            OUT_SET = standardEffectiveTemperature
            restrictedComfOrNot = comfortableOrNot
            restrictedPercentComf = percentOfTimeComfortable


