# Photovoltaics performance metrics
# By Djordje Spasic
# djordjedspasic@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate various Photovoltaics performance metrics

-
Provided by Ladybug 0.0.59
    
    input:
        _PVsurface: - Input planar Surface (not polysurface) on which the PV modules will be applied. If you have a polysurface, explode it (using "Deconstruct Brep" component) and then feed its Faces(F) output to _PVsurface. Surface normal should be faced towards the sun.
                    - Or input surface Area, in square meters (example: "100").
                    - Or input PV system size (nameplate DC power rating), in kiloWatts at standard test conditions (example: "4 kw").
        PVsurfacePercent_: The percentage of surface which will be used for PV modules (range 0-100).
                           -
                           If not supplied, default value of 100 (all surface area will be covered in PV modules) is used.
        moduleActiveAreaPercent_: Percentage of the module's area excluding module framing and gaps between cells. 
                                  -
                                  If not supplied, default value of 90(%) will be used.
        moduleEfficiency_: The ratio of energy output from the PV module to input energy from the sun. It ranges from 0 to 100 (%).
                           -
                           If not defined, default value of 15(%) will be used.
        lifetime_: Life expectancy of a PV module. In years.
                   -
                   If not supplied default value of 30 (years) will be used.
        _ACenergyPerHour: Import "ACenergyPerYear" output data from "Photovoltaics surface" component.
                          In kWh.
        _totalRadiationPerHour: Import "totalRadiationPerHour" output data from "Photovoltaics surface" component.
                                In kWh/m2.
        _cellTemperaturePerHour: Import "cellTemperaturePerHour" output data from "Photovoltaics surface" component.
                                 In °C.
        energyCostPerKWh_: The cost of one kilowatt hour in any currency unit (dollar, euro, yuan...)
                           -
                           If not supplied, 0.15 $/kWh will be used as default value.
        embodiedEnergyPerM2_: Energy necessary for an entire product life-cycle of PV module per square meter.
                             In MJ/m2 (megajoules per square meter).
                             -
                             If not supplied default value of 4410 (MJ/m2) will be used.
        embodiedCO2PerM2_: Carbon emissions produced during PV module's life-cycle per square meter..
                          In kg CO2/m2 (kilogram of CO2 per square meter).
                          -
                          If not supplied default value of 225 (kg CO2/m2) will be used.
        gridEfficiency_: An average primary energy to electricity conversion efficiency.
                        -
                        If not supplied default value of 29 (%) will be used.
        _runIt: ...
        
    output:
        readMe!: ...
        Yield: Ratio of annual AC power output and nameplate DC power rating.
               In hours (h).
        CUFperMonth: Capacity Utilization Factor - ratio of the annual AC power output and maximum possible output under ideal conditions if the sun shone throughout the day for the each month.
             In percent (%).
        CUFperYear: Capacity Utilization Factor (sometimes called Plant Load Factor (PLF)) - ratio of the annual AC power output and maximum possible output under ideal conditions if the sun shone throughout the day and throughout the year.
             In percent (%).
        basicPRperMonth: Basic Performance Ratio - ratio of the actual and theoretically possible energy output per month.
                 In percent(%).
        basicPRperYear: Basic Performance Ratio - ratio of the actual and theoretically possible annual energy output.
                 In percent(%).
        temperatureCorrectedPRperMonth: Temperature corrected Performance Ratio - ratio of the actual and theoretically possible energy output per month, corrected for PV module's Cell temperature. Mid-day hours (solarRadiation > 0.6 kWh/m2) only taken into account.
                 In percent(%).
        temperatureCorrectedPRperYear: Temperature corrected Performance Ratio - ratio of the actual and theoretically possible annual energy output, corrected for PV module's Cell temperature. Mid-day hours (solarRadiation > 0.6 kWh/m2) only taken into account.
                 In percent(%).
        energyValuePerMonth: Total Energy value for each month in currency unit (dollars, euros, yuans...)
        energyValuePerYear: Total Energy value for whole year in currency unit (dollars, euros, yuans...)
        embodiedEnergy: Total energy necessary for an entire product life-cycle of PV modules.
                        In GJ (gigajoules).
        embodiedCO2: Total carbon emissions produced during PV module's life-cycle.
                     In tCO2 (tons of CO2).
        CO2emissionRate: An index which shows how effective a PV system is in terms of global warming.
                         It is used in comparison with other fuels and technologies (Hydroelectricity(15), Wind(21), Nuclear(60), Geothermal power(91), Natural gas(577), Oil(893), Coal(955) ...)
                         In gCO2/kWh.
        EPBT: Energy PayBack Time - time it takes for PV modules to produce all the energy used through-out its product life-cycle.
              In years.
        EROI: Energy Return On Investment - a comparison of the generated electricity to the amount of primary energy used throughout the PV module's product life-cycle.
              Unitless.
"""

ghenv.Component.Name = "Ladybug_Photovoltaics Performance Metrics"
ghenv.Component.NickName = "PhotovoltaicsPerformanceMetrics"
ghenv.Component.Message = "VER 0.0.59\nMAY_26_2015"
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.59\nMAY_26_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino


def PVinputData(PVsurface, PVsurfacePercent, unitConversionFactor, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHour, totalRadiationPerHour, cellTemperaturePerHour, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency):
    
    if (PVsurface == None):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHourData = totalRadiationPerHourData = cellTemperaturePerHourData = energyCostPerKWh = embodiedEnergyPerM2 = embodiedCO2PerM2 = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input Surface (not polysurface) to \"_PVsurface\".\nOr input surface Area in square meters (example: \"100\").\nOr input Nameplate DC power rating in kiloWatts (example: \"4 kw\")."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency, locationName, validInputData, printMsg
    
    if (len(ACenergyPerHour) == 0) or (ACenergyPerHour[0] is "") or (ACenergyPerHour[0] is None):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHourData = totalRadiationPerHourData = cellTemperaturePerHourData = energyCostPerKWh = embodiedEnergyPerM2 = embodiedCO2PerM2 = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input \"_ACenergyPerHour\" from Ladybug \"Photovoltaics surface\" component."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency, locationName, validInputData, printMsg
    else:
        ACenergyPerHourData = ACenergyPerHour[7:]
        locationName = ACenergyPerHour[1]
    
    if (len(totalRadiationPerHour) == 0) or (totalRadiationPerHour[0] is "") or (totalRadiationPerHour[0] is None):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHourData = totalRadiationPerHourData = cellTemperaturePerHourData = energyCostPerKWh = embodiedEnergyPerM2 = embodiedCO2PerM2 = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input \"_totalRadiationPerHour\" from Ladybug \"Photovoltaics surface\" component."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency, locationName, validInputData, printMsg
    else:
        totalRadiationPerHourData = totalRadiationPerHour[7:]
    
    if (len(cellTemperaturePerHour) == 0) or (cellTemperaturePerHour[0] is "") or (cellTemperaturePerHour[0] is None):
        nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHourData = totalRadiationPerHourData = cellTemperaturePerHourData = energyCostPerKWh = embodiedEnergyPerM2 = embodiedCO2PerM2 = gridEfficiency = locationName = None
        validInputData = False
        printMsg = "Please input \"_totalRadiationPerHour\" from Ladybug \"Photovoltaics surface\" component."
        
        return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency, locationName, validInputData, printMsg
    else:
        cellTemperaturePerHourData = cellTemperaturePerHour[7:]
    
    if (PVsurfacePercent == None) or (PVsurfacePercent < 0) or (PVsurfacePercent > 100):
        PVsurfacePercent = 100  # default value 100%
    
    if (moduleActiveAreaPercent == None) or (moduleActiveAreaPercent < 0) or (moduleActiveAreaPercent > 100):
        moduleActiveAreaPercent = 90  # default value in %
    
    if (moduleEfficiency == None) or (moduleEfficiency < 0) or (moduleEfficiency > 100):
        moduleEfficiency = 15  # default for crystalline silicon, in %
    
    if (lifetime == None) or (lifetime < 0):
        lifetime = 30  # default, in years
    
    if (energyCostPerKWh == None) or (energyCostPerKWh < 0):
        energyCostPerKWh = 0.15  # dollars per kWh
    
    if (embodiedEnergyPerM2 == None) or (embodiedEnergyPerM2 < 0):
        embodiedEnergyPerM2 = 4410/1000  # default, in GJ/m2
    else:
        embodiedEnergyPerM2 = embodiedEnergyPerM2/1000  # in in GJ/m2
    
    if (embodiedCO2PerM2 == None) or (embodiedCO2PerM2 < 0):
        embodiedCO2PerM2 = 225/1000  # default, in t CO2/m2
    else:
        embodiedCO2PerM2 = embodiedCO2PerM2/1000  # in t CO2/m2
    
    if (gridEfficiency == None) or (gridEfficiency < 0) or (gridEfficiency > 100):
        gridEfficiency = 29  # default, in %
    
    # check PVsurface input
    obj = rs.coercegeometry(PVsurface)
    
    # input is surface
    if isinstance(obj,Rhino.Geometry.Brep):
        PVsurfaceInputType = "brep"
        facesCount = obj.Faces.Count
        if facesCount > 1:
            # inputted polysurface
            nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHour = totalRadiationPerHour = cellTemperaturePerHour = embodiedEnergyPerM2 = embodiedCO2PerM2 = None
            validInputData = False
            printMsg = "The brep you supplied to \"_PVsurface\" is a polysurface. Please supply a surface"
            
            return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency, locationName, validInputData, printMsg
        else:
            # inputted brep with a single surface
            srfArea = Rhino.Geometry.AreaMassProperties.Compute(obj).Area * (PVsurfacePercent/100)  # in m2
            srfArea = srfArea * unitConversionFactor  # in m2
            activeArea = srfArea * (moduleActiveAreaPercent/100)  # in m2
            nameplateDCpowerRating = activeArea * (1 * (moduleEfficiency/100))  # in kW
            validInputData = True
            printMsg = "ok"
            
            return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency, locationName, validInputData, printMsg
    else:
        PVsurfaceInputType = "number"
        try:
            # input is number (pv surface area in m2)
            srfArea = float(PVsurface) * (PVsurfacePercent/100)  # in m2
            srfArea = srfArea * unitConversionFactor  # in m2
            activeArea = srfArea * (moduleActiveAreaPercent/100)  # in m2
            nameplateDCpowerRating = activeArea * (1 * (moduleEfficiency/100))  # in kW
            validInputData = True
            printMsg = "ok"
            
            return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency, locationName, validInputData, printMsg
        except Exception, e:
            pass
        
        # input is string (nameplateDCpowerRating in kW)
        lowerString = PVsurface.lower()
        
        if "kw" in lowerString:
            nameplateDCpowerRating = float(lowerString.replace("kw","")) * (PVsurfacePercent/100)  # in kW
            activeArea = nameplateDCpowerRating / (1 * (moduleEfficiency/100))  # in m2
            srfArea = activeArea * (100/moduleActiveAreaPercent)  # in m2
            validInputData = True
            printMsg = "ok"
            
            return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency, locationName, validInputData, printMsg
        else:
            nameplateDCpowerRating = srfArea = activeArea = PVsurfacePercent = moduleActiveAreaPercent = moduleEfficiency = lifetime = ACenergyPerHour = totalRadiationPerHour = cellTemperaturePerHour = embodiedEnergyPerM2 = embodiedCO2PerM2 = None
            validInputData = False
            printMsg = "Something is wrong with your \"PVsurface\" input data"
            
            return nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency, locationName, validInputData, printMsg


def monthlyYearlyPacEpoaTmTcell(ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh):
    HOYs = range(1,8761)
    hoyForMonths = [0, 744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296, 8016, 8760, 9000]
    numberOfDaysInThatMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
    monthsOfYearHoyPac = [[],[],[],[],[],[],[],[],[],[],[],[]]
    monthsOfYearHoyPacFiltered = [[],[],[],[],[],[],[],[],[],[],[],[]]
    monthsOfYearHoyEpoa = [[],[],[],[],[],[],[],[],[],[],[],[]]
    monthsOfYearHoyEpoaFiltered = [[],[],[],[],[],[],[],[],[],[],[],[]]
    monthsOfYearHoyTcellFiltered = [[],[],[],[],[],[],[],[],[],[],[],[]]
    for i,hoy in enumerate(HOYs):
        Pac = ACenergyPerHourData[i]
        Epoa = totalRadiationPerHourData[i]
        Tcell = cellTemperaturePerHourData[i]
        for k,item in enumerate(hoyForMonths):
            if hoy >= hoyForMonths[k]+1 and hoy <= hoyForMonths[k+1]:
                #if ACenergyPerHourData[i] > 0:
                if totalRadiationPerHourData[i] > 0.6:  # basicPR and CPR mid-day hours (Epoa > 0.6 kWh/m2) filter
                    monthsOfYearHoyTcellFiltered[k].append(Tcell)
                    monthsOfYearHoyEpoaFiltered[k].append(Epoa)
                    monthsOfYearHoyPacFiltered[k].append(Pac)
                monthsOfYearHoyEpoa[k].append(Epoa)
                monthsOfYearHoyPac[k].append(Pac)
    # correction for if Epoa per some month = 0 (if conditionalStatement_ from "Photovoltaics surface" component has been used, too high (positive or negative) latitude):
    for i,monthSumTcellFiltered in enumerate(monthsOfYearHoyTcellFiltered):
        if len(monthSumTcellFiltered) == 0:
            monthsOfYearHoyTcellFiltered[i] = [0]
    for i,monthSumEpoaFiltered in enumerate(monthsOfYearHoyEpoaFiltered):
        if len(monthSumEpoaFiltered) == 0:
            monthsOfYearHoyEpoaFiltered[i] = [0]
    for i,monthSumPacFiltered in enumerate(monthsOfYearHoyPacFiltered):
        if len(monthSumPacFiltered) == 0:
            monthsOfYearHoyPacFiltered[i] = [0]
    
    cellTemperaturePerMonthAverageFiltered = [sum(monthTcell)/len(monthTcell) for monthTcell in monthsOfYearHoyTcellFiltered]  # in C
    cellTemperaturePerYearAverageFiltered = sum(cellTemperaturePerMonthAverageFiltered)/len(cellTemperaturePerMonthAverageFiltered)  # in C
    
    solarRadiationPerMonth = [sum(monthEpoa) for monthEpoa in monthsOfYearHoyEpoa]  # in kWh/m2
    solarRadiationPerYear = sum(solarRadiationPerMonth)  # in kWh/m2
    
    solarRadiationPerMonthAverageFiltered = [sum(monthEpoa2) for monthEpoa2 in monthsOfYearHoyEpoaFiltered]  # in kWh/m2
    
    ACenergyPerMonth = [sum(monthPac) for monthPac in monthsOfYearHoyPac]  # in kWh
    ACenergyPerYear = sum(ACenergyPerMonth)  # in kWh
    
    ACenergyPerMonthAverageFiltered = [sum(monthPac2) for monthPac2 in monthsOfYearHoyPacFiltered]  # in kWh/m2
    
    energyValuePerMonth = [month*energyCostPerKWh for month in ACenergyPerMonth]
    energyValuePerYear = sum(energyValuePerMonth)
    
    return ACenergyPerMonth, ACenergyPerYear, ACenergyPerMonthAverageFiltered, energyValuePerMonth, energyValuePerYear, solarRadiationPerMonth, solarRadiationPerYear, solarRadiationPerMonthAverageFiltered, cellTemperaturePerMonthAverageFiltered, cellTemperaturePerYearAverageFiltered


def main(ACenergyPerMonth, ACenergyPerYear, ACenergyPerMonthAverageFiltered, solarRadiationPerMonth, solarRadiationPerYear, solarRadiationPerMonthAverageFiltered, cellTemperaturePerMonthAverageFiltered, cellTemperaturePerYearAverageFiltered, embodiedEnergyPerM2, embodiedCO2PerM2, lifetime, gridEfficiency):
    
    Yield = ACenergyPerYear/nameplateDCpowerRating  # in hours
    
    CUFperYear = ACenergyPerYear/(nameplateDCpowerRating * 8760) * 100  # in %
    
    CUFperMonth = []
    numberOfDaysInThatMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
    for i in range(len(numberOfDaysInThatMonth)):
        CUFperMonth.append(ACenergyPerYear/(nameplateDCpowerRating * (numberOfDaysInThatMonth[i]*24)) * 100)  # in %
    
    basicPRperMonth = []
    for i,monthPac in enumerate(ACenergyPerMonth):
        if monthPac == 0:  # correction for if Epoa per some month = 0 (if conditionalStatement_ from "Photovoltaics surface" component has been used, too high (positive or negative) latitude):
            basicPRpM = 0
        else:
            basicPRpM = (ACenergyPerMonth[i] / (activeArea*(moduleEfficiency/100)*solarRadiationPerMonth[i])) * 100
        basicPRperMonth.append(basicPRpM)
    
    basicPRperYear = (ACenergyPerYear / (activeArea*(moduleEfficiency/100)*solarRadiationPerYear)) * 100  # in %
    
    gamma = -0.005   # default value for crystalline silicon PV modules
    temperatureCorrectedPRperMonth = []
    for i,Epoa in enumerate(solarRadiationPerMonthAverageFiltered):
        Ktemp = 1+gamma*(cellTemperaturePerMonthAverageFiltered[i]-cellTemperaturePerYearAverageFiltered)
        if Epoa == 0:  # correction for if Epoa per some month = 0 (if conditionalStatement_ from "Photovoltaics surface" component has been used, too high (positive or negative) latitude):
            TaCorrectedPR = 0
        else:
            TaCorrectedPR = (ACenergyPerMonthAverageFiltered[i]/nameplateDCpowerRating*Ktemp) / ((Epoa)/1)*100
        temperatureCorrectedPRperMonth.append(TaCorrectedPR)  # in %
    temperatureCorrectedPRperYear = sum(temperatureCorrectedPRperMonth)/len(temperatureCorrectedPRperMonth)  # in %
    
    embodiedEnergy = embodiedEnergyPerM2 * srfArea  # in GigaJoules
    embodiedCO2 = embodiedCO2PerM2 * srfArea   # in tCO2
    
    CO2emissionRate = (embodiedCO2*1000000)/(ACenergyPerYear*lifetime)  # in gCO2/kWh
    embodiedEnergy_kWh_m2 = embodiedEnergyPerM2 * (1000/3.6) * (gridEfficiency/100)  # to kWh/m2
    
    EPBT = (embodiedEnergy_kWh_m2) / (solarRadiationPerYear*(moduleEfficiency/100)*(basicPRperYear/100))  # in years
    EROI = lifetime / EPBT  # formula by Hall, 2008; Heinberg, 2009; Lloyd and Forest, 2010
    
    return Yield, CUFperMonth, CUFperYear, basicPRperMonth, basicPRperYear, temperatureCorrectedPRperMonth, temperatureCorrectedPRperYear, embodiedEnergy, embodiedCO2, CO2emissionRate, EPBT, EROI


def printOutput(locationName, PVsurfacePercent, moduleActiveAreaPercent, srfArea, activeArea, nameplateDCpowerRating, moduleEfficiency, lifetime, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency):
    resultsCompletedMsg = "Photovoltaics performance metrics successfully calculated!"
    printOutputMsg = \
    """
Input data:

Location: %s

Surface percentage used for PV modules: %0.2f
Active area Percentage: %0.2f
Surface area (m2): %0.2f
Surface active area (m2): %0.2f
Nameplate DC power rating (kW): %0.2f
Module efficiency: %s
Lifetime: %s
Embodied energy/m2 (MJ/m2): %0.2f
Embodied CO2/m2 (kg CO2/m2): %0.2f
gridEfficiency: %s
    """ % (locationName, PVsurfacePercent, moduleActiveAreaPercent, srfArea, activeArea, nameplateDCpowerRating, moduleEfficiency, lifetime, embodiedEnergyPerM2*1000, embodiedCO2PerM2*1000, gridEfficiency)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        if _PVsurface:
            unitConversionFactor = lb_preparation.checkUnits()
            unitAreaConversionFactor = unitConversionFactor**2
            nameplateDCpowerRating, srfArea, activeArea, PVsurfacePercent, moduleActiveAreaPercent, moduleEfficiency, lifetime, ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency, locationName, validInputData, printMsg = PVinputData(_PVsurface, PVsurfacePercent_, unitConversionFactor, moduleActiveAreaPercent_, moduleEfficiency_, lifetime_, _ACenergyPerHour, _totalRadiationPerHour, _cellTemperaturePerHour, energyCostPerKWh_, embodiedEnergyPerM2_, embodiedCO2PerM2_, gridEfficiency_)
            if validInputData:
                # all inputs ok
                if _runIt:
                    ACenergyPerMonth, ACenergyPerYear, ACenergyPerMonthAverageFiltered, energyValuePerMonth, energyValuePerYear, solarRadiationPerMonth, solarRadiationPerYear, solarRadiationPerMonthAverageFiltered, cellTemperaturePerMonthAverageFiltered, cellTemperaturePerYearAverageFiltered = monthlyYearlyPacEpoaTmTcell(ACenergyPerHourData, totalRadiationPerHourData, cellTemperaturePerHourData, energyCostPerKWh)
                    Yield, CUFperMonth, CUFperYear, basicPRperMonth, basicPRperYear, temperatureCorrectedPRperMonth, temperatureCorrectedPRperYear, embodiedEnergy, embodiedCO2, CO2emissionRate, EPBT, EROI = main(ACenergyPerMonth, ACenergyPerYear, ACenergyPerMonthAverageFiltered, solarRadiationPerMonth, solarRadiationPerYear, solarRadiationPerMonthAverageFiltered, cellTemperaturePerMonthAverageFiltered, cellTemperaturePerYearAverageFiltered, embodiedEnergyPerM2, embodiedCO2PerM2, lifetime, gridEfficiency)
                    printOutput(locationName, PVsurfacePercent, moduleActiveAreaPercent, srfArea, activeArea, nameplateDCpowerRating, moduleEfficiency, lifetime, embodiedEnergyPerM2, embodiedCO2PerM2, gridEfficiency)
                else:
                    print "All inputs are ok. Please set the \"_runIt\" to True, in order to run the Photovoltaics performance metrics"
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please input Surface (not polysurface) to \"_PVsurface\".\nOr input surface Area in square meters (example: \"100\").\nOr input Nameplate DC power rating in kiloWatts (example: \"4 kw\")."
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        printMsg = "You need a newer version of Ladybug to use this component." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag the Ladybug_Ladybug component " + \
            "into the canvas and try again."
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please let the Ladybug fly..."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
    