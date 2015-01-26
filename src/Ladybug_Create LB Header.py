# This component generates a Ladybug Header that can be combined with any raw data in order to format it for use with the Ladybug/Honeybee components
# By Chris Mackey
# chris@mackeyarchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed

"""
Use this component to generates a Ladybug Header that can be combined with any raw data in order to format it for use with the Ladybug/Honeybee components.
_
This component is particularly useful if you are bringing in data from other plugins or from instrumental measurements and you want to visualize it or analyze it with the Ladybug and Honeybee components.  It is also useful if you want to replace the header on Ladybug data.
-
Provided by Ladybug 0.0.58
    
    Args:
        location_: A text string that represents the name of the location where the data was collected.  If no value is connected here, the default will be "Somewhere."
        dataType_: A text string that represents the type of data that the header corresponds to.  This can be "Temperature", "Wind", etc.  If no value is connected here, the default will be "Some Data."
        units_: A text string that represents the units of the data. This can be "C", "m/s", etc.  If no value is connected here, the default will be "Some Units."
        timeStep_:  A text string that represents the time step of the data.  Acceptable values include "Hourly", "Daily", "Monthly", or "Annually."  If no value is connected here, the default will be "Hourly."
        analysisPeriod_: An optional analysis period from the Analysis Period component.  If no analysis period is given, the default will be for the enitre year: (1,1,1)(12,31,24).
    Returns:
        LBHEader: A Ladybug header that can be combined with any raw data in order to format it for the Ladybug and Honeybee components.
"""

ghenv.Component.Name = "Ladybug_Create LB Header"
ghenv.Component.NickName = 'CreateHeader'
ghenv.Component.Message = 'VER 0.0.58\nOCT_25_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning


def setDefaults():
    checkData = True
    #Set a default location.
    if location_ == None: location = "Somewhere"
    else: location = location_
    
    #Set a default dataType.
    if dataType_ == None: dataType = "Some Data"
    else: dataType = dataType_
    
    #Set a default units.
    if units_ == None: units = "Some Units"
    else: units = units_
    
    #Set a default analysis period.
    if analysisPeriod_ == []: analysisPeriod = [(1,1,1), (12,31,24)]
    else:
        if len(analysisPeriod_) == 2: analysisPeriod = analysisPeriod_
        else:
            analysisPeriod = None
            checkData = False
            warning = "analysisPeriod_ is not valid."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the timpeStep_.
    if timeStep_ == None: timeStep = "Hourly"
    else:
        if timeStep_ == "Hourly" or timeStep_ == "Daily" or timeStep_ == "Monthly" or timeStep_ == "Anually": timeStep = timeStep_
        else:
            timeStep = None
            checkData = False
            warning = "timeStep_ is not valid."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    
    return checkData, location, dataType, units, timeStep, analysisPeriod


def main(location, dataType, units, timeStep, analysisPeriod):
    header = ['key:location/dataType/units/frequency/startsAt/endsAt', location, dataType, units, timeStep]
    header.extend(analysisPeriod)
    
    return header

checkData, location, dataType, units, timeStep, analysisPeriod = setDefaults()
if checkData == True:
    LBHeader = main(location, dataType, units, timeStep, analysisPeriod)