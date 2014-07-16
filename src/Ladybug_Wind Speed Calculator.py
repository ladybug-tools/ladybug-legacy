# Wind Speed Calculator
# By Chris Mackey and Alex Jacobson
# Chris@MackeyArchitecture.com and Jacobson@gsd.harvard.edu
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate wind speed at a specific height over analysis period.  Terain types ....

-
Provided by Ladybug 0.0.57
    
    Args:
        _hourlyWindSpeed: The wind speed from the import EPW component.
        _hourlyWindDirection: The wind direction from the import EPW component.
        _terrainType: The logarithmic model for wind speed varies with the type of terrain. The user may enter values from a slider or a string of text indicating the type of landscape to be evaluated, note that strings of text are case sensistive and therefore capitalization must match exactly the following terms. 0 = "water", 0.5 = "concrete", 1 = "agricultural", 1.5 = "orchard", 2 = "rural", 2.5 = "sprawl", 3 = "suburban", 3.5 = "town", 4 = "urban".
        heightAboveGround_ : Optional. This is the height above ground for which you would like to measure wind speed. Providing more than one value will generate a list of speeds at each given height. Default height is 1 m above ground.
        analysisPeriod_: Optional. Plug in an analysis period from the Ladybug_Analysis Period component. Default is Jan 1st 00:00 - Dec 31st 24:00, the entire year.
        averageData_: Optional boolean toggle. The default is False, which means the component will return a list of all hours within the analysis period.  If se tot Ture, the wind data will be averaged for the entire analysis period into a single value. 
    Returns:
        readMe!: ...
        windSpeedAtHeight: If averageData_ = True, this returns a single value representing the average speed for the analysis period at each height. If averageData_ = False, this returns a list of wind speeds for every hour within the analysis period at each height. Note than when averageData_ =  False, the list will include a header specific to each list. This header is located in in positions 0-6 of the list and can be removed by culling those values.
        windVectorAtHeight: Returns a list of vectors representing wind speed and direction at every hour within the analysis period, at each height provided.
"""
ghenv.Component.Name = "Ladybug_Wind Speed Calculator"
ghenv.Component.NickName = 'WindSpeedCalculator'
ghenv.Component.Message = 'VER 0.0.57\nJUL_15_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Rhino as rc
import scriptcontext as sc
import math
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from System import Object


#Make data Tree objects.
windSpeedAtHeight = DataTree[Object]()
windVectorAtHeight = DataTree[Object]()


def checkTheInputs():
    # Check if the _hourlyWindSpeed is connected.
    if _hourlyWindSpeed != []:
        if _hourlyWindSpeed[2] == "Wind Speed":
            checkData1 = True
        else:
            checkData1 == False
            print "_hourlyWindSpeed is not valid EPW wind data."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "_hourlyWindSpeed is not valid EPW wind data.  Valid EPW data has a Ladybug header on it.")
    else:
        checkData1 = False
    
    if _hourlyWindDirection != []:
        if _hourlyWindDirection[2] == "Wind Direction":
            checkData2 = True
        else:
            checkData2 = False
            print "_hourlyWindDirection is not valid EPW wind data."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "_hourlyWindDirection is not valid EPW wind data.  Valid EPW data has a Ladybug header on it.")
    else:
        checkData2 = False
    
    #Make the default height at 1 meters if the user has not input a height.
    checkData4 = True
    if heightAboveGround_ == []:
        heightAboveGround = [1.6]
    else:
        for item in heightAboveGround_:
            if item < 1.6:
                checkData4 = False
                print "The input heightAboveGround cannot be less than 1.6."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "The input heightAboveGround cannot be less than 1.6.")
            else: pass
        heightAboveGround = heightAboveGround_
    
    #Make the default analyisis period for the whole year if the user has not input one.
    if analysisPeriod_ == []:
        analysisPeriod = [ (1, 1, 1), (12, 31, 24)]
    else:
        analysisPeriod = analysisPeriod_
    
    # Evaluate the terrain type to get the right boundary layer thickness and flow exponent.
    checkData3 = True
    if round(_terrainType, 1) == 0.0 or _terrainType == "water":
        print "Terrain set to water."
        roughLength = 0.0002
    elif round(_terrainType, 1) == 0.5 or _terrainType == "concrete":
        print "Terrain set to concrete."
        roughLength = 0.0024
    elif round(_terrainType, 1) == 1.0 or _terrainType == "agriculture":
        print "Terrain set to agriculture."
        roughLength = 0.03
    elif round(_terrainType, 1) == 1.5 or _terrainType == "orchard":
        print "Terrain set to orchard."
        roughLength = 0.055
    elif round(_terrainType, 1) == 2.0 or _terrainType == "rural":
        print "Terrain set to rural."
        roughLength = 0.1
    elif round(_terrainType, 1) == 2.5 or _terrainType == "sprawl":
        print "Terrain set to sprawl."
        roughLength = 0.2
    elif round(_terrainType, 1) == 3.0 or _terrainType == "suburban":
        print "Terrain set to suburban."
        roughLength = 0.4
    elif round(_terrainType, 1) == 3.5 or _terrainType == "town":
        print "Terrain set to town."
        roughLength = 0.6
    elif round(_terrainType, 1) == 4.0 or _terrainType == "urban":
        print "Terrain set to urban."
        roughLength = 1.6
    else:
        checkData3 = False
        print "You have not connected a correct Terrain type."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You have not connected a correct Terrain type.")
    
    #Set the default averageData_ to true.
    if averageData_ == None:
        averageData = False
    else:
        averageData = averageData_
    
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True:
        checkData = True
    else:
        checkData = False
    
    return checkData, heightAboveGround, analysisPeriod, roughLength, averageData

def calcWindSpeedBasedOnHeight(vMet, height, roughLength):
    #Calculate the velocity
    vHeight = vMet * ((math.log(height/roughLength))/(math.log(10/0.0024)))
    
    return vHeight


def main(heightAboveGround, analysisPeriod, roughLength, averageData):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        #Get the data for the analysis period and strip the header off.
        hourlyWindSpeed = _hourlyWindSpeed[7:]
        hrWindSpd = []
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
        hourlyWindDirection = _hourlyWindDirection[7:]
        hrWindDir = []
        for count in HOYS:
            hrWindDir.append(hourlyWindDirection[count-1])
            hrWindSpd.append(hourlyWindSpeed[count-1])
        
        
        if averageData == True:
            #Avergage the data.
            avgHrWindSpd = sum(hrWindSpd)/len(hrWindSpd)
            
            avgHrWindDir = sum(hrWindDir)/len(hrWindDir)
            avgHrWindDir = 0.0174532925*avgHrWindDir
            
            #Evaluate each height.
            windSpdHeight = []
            for count, height in enumerate(heightAboveGround):
                windSpdHeight.append([calcWindSpeedBasedOnHeight(avgHrWindSpd, height, roughLength)])
            
            #Make wind Vectors.
            windVec = []
            for speed in windSpdHeight:
                vec = rc.Geometry.Vector3d(0, speed[0], 0)
                vec.Rotate(avgHrWindDir, rc.Geometry.Vector3d.ZAxis)
                windVec.append([vec])
            
        else:
            #Add the headers to the data trees.
            for count, height in enumerate(heightAboveGround):
                for text in hourlyWindSpeed[:7]:
                    windSpeedAtHeight.Add(text, GH_Path(count))
            
            #Evaluate each height.
            windSpdHeight = []
            for height in heightAboveGround:
                initWindSpd = []
                for speed in hrWindSpd:
                    initWindSpd.append(calcWindSpeedBasedOnHeight(speed, height, roughLength))
                windSpdHeight.append(initWindSpd)
             
            #Make the wind vectors.
            windVec = []
            for list in windSpdHeight:
                initWindVec = []
                for count, speed in enumerate(list):
                    vec = rc.Geometry.Vector3d(0, speed, 0)
                    vec.Rotate(hrWindDir[count], rc.Geometry.Vector3d.ZAxis)
                    initWindVec.append(vec)
                windVec.append(initWindVec)
        
        return windSpdHeight, windVec
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1, -1



#Check the inputs.
checkData, heightAboveGround, analysisPeriod, roughLength, averageData = checkTheInputs()

#Run the function.
if checkData == True:
    windSpdAtHght, windVecAtHght = main(heightAboveGround, analysisPeriod, roughLength, averageData)


#Unpack the lists of lists in Python.
for count, list in enumerate(windSpdAtHght):
    for item in list:
        windSpeedAtHeight.Add(item, GH_Path(count))

for count, list in enumerate(windVecAtHght):
    for item in list:
        windVectorAtHeight.Add(item, GH_Path(count))
