# pedestrian wind comfort
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Djordje Spasic <djordjedspasic@gmail.com>
# with assistance of Dr. Liam Harrington
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
Use this component to analyse pedestrian wind comfort and safety for the present and potential (newly built) urban environments.
Construction of a new building changes the wind microclimate in its vicinity. These changes can result in either decreased or increased wind speeds around the building, which may be uncomfortable or even dangerous.
-
Based on Lawsons Pedestrian Comfort Criteria (1990)
https://www.dropbox.com/s/t9pxhr45vwg2xd2/Wind_Microclimate.pdf?dl=0
-
Provided by Ladybug 0.0.64
    
    input:
        _epwFile: Input an .epw file path by using the "File Path" parameter, or Ladybug's "Open EPW And STAT Weather Files" component.
        _windFactor: Division of cfd simulation's wind speed values, and annual average wind speed value from the weather data (.epw file) at 10 meters height.
                     They are used to normalize against the weather data (.epw file), given that a CFD simulation with the exact .epw file wind speed and direction has not been performed.
                     -
                     _windFactor data should be supplied into different branches corresponding to different directions for which the cfd simulation has been performed.
                     For example: the first branch holds windFactors for all analysis points for wind direction 0. Second branch would hold windFactors for all analysis points for wind direction 20. Third branch would hold windFactors for all analysis points for wind direction 40 ... and so on.
        _analysisGeometry: Input a mesh for whose face centroids the cfd simulation has been performed.
                           -
                           The number of mesh face centroids needs to be equal to the number of values in each of the _windFactor branches.
        pedestrianType_: Choose the pedestrian type used at the analysis location:
                         0 = typical pedestrian (20 m/s)
                         1 = sensitive pedestrian (15 m/s): elderly people, cyclists, children.
                         -
                         This input is used to analyse pedestrian safety.
                         -
                         If not supplied, the 0 (typical pedestrian) will be used by default.
        northCfd_: Input a vector to be used as a Cfd simulation's true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                   -
                   If not supplied, default North Cfd direction will be set to the Y-axis (0 degrees).
        north_: Input a vector to be used as Rhino's true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        legendPar_: Optional legend parameters from the Ladybug "Legend Parameters" component.
                    -
                    Notice: the "numSegments_" and "customColors_" inputs of the "Legend Parameters" component will only affect the "legend" output, not the "legend2" output. This is due to "legend2" requirement of always having only two values: 0 and 1, representing Safe and Not safe pedestrian safety criteria.
        resultGradient_: Choose whether or not the resulting geometry-values will be created as a gradient-float or not.
                         -
                         It allows the following two inputs:
                         True - the resulting pedestrianComfortMesh, pedestrianSafetyMesh will be created as a gradient, and the pedestrianComfortCategory, pedestrianSafetyCategory will be outputed as float values.
                         False - the resulting pedestrianComfortMesh, pedestrianSafetyMesh will NOT be created as a gradient, and the pedestrianComfortCategory, pedestrianSafetyCategory will be outputed as integer values.
                         -
                         If not supplied, no gradient (integer values) will be set by default.
        analysisPeriod_: An optional analysis period from the "Analysis Period" component.
                         -
                         This input can be useful in cases where certain areas show higher pedestrianComfortCategory than required. For example: when analysis is run for the whole year period, the component shows that a certain location does not fulfill the comfort criteria for sitting.
                         However if we perform the analysis for the period from late spring to early autumn (when the sitting is suppose to happen), the comfort criteria for sitting can be fulfilled.
                         -
                         If not supplied, the whole year period will be used as an analysis period.
        annualHourlyData_: An optional list of hourly data from Ladybug's "Import epw" component (e.g. windSpeed), which will be used for "conditionalStatement_".
        conditionalStatement_: This input allows users to calculate the Pedestrian wind comfort component results only for those annualHourlyData_ values which fit specific conditions or criteria. To use this input correctly, hourly data, such as windSpeed or windDirection, must be plugged into the "annualHourlyData_" input. The conditional statement input here should be a valid condition statement in Python, such as "a>4" or "b<90" (without the quotation marks).
                               conditionalStatement_ accepts "and" and "or" operators. To visualize the hourly data, English letters should be used as variables, and each letter alphabetically corresponds to each of the lists (in their respective order): "a" always represents the 1st list, "b" always represents the 2nd list, etc.
                               -
                               For example, if you have an hourly windSpeed connected as the first list, and windDirection connected as the second list (both to the annualHourlyData_ input), and you want to plot the data for the time period when windSpeed is larger than 4m/s and windDirection is southerly, the conditionalStatement_ should be written as "a>4 and b==180" (without the quotation marks).
        bakeIt_: Set to "True" to bake the pedestrianComfortMesh, pedestrianSafetyMesh, legend, legend2 into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        pedestrianComfortCategory: Pedestrian wind comfort categories for each face centroid of the _analysisGeometry mesh.
                                   The categories depend on the threshold wind speed for particular point: the wind speed that for 95% of the chosen analysis period is below a certain value. With values being the following:
                                   -
                                   0) < 4 m/s  sitting (outdoor cafes, patios, terraces, benches, gardens, parks, fountains, monuments...)
                                   1) 4-6 m/s  standing (building entrances or exits, bus stops, childrens play areas...)
                                   2) 6-8 m/s  leisurely walking (general areas of walking, strolling and sightseeing, window shopping, public/private sidewalks, pathways, public spaces...)
                                   3) 8-10 m/s  business walking (walking from one place to another quickly, or where individuals pass rapidly through local areas around buildings, public/private vehicular drop-off zones, roads and car parks, cyclists pathways...)
                                   4) > 10 m/s  uncomfortable (uncomfortable for all pedestrian activities)
                                   -
                                   If resultGradient_ input is set to True, then upper mentioned category values will be calculated as floats, instead of integers.
        pedestrianSafetyCategory: Pedestrian wind safety categories for each face centroid of the _analysisGeometry mesh.
                                  -
                                  Infrequent strong wind can cause some pedestrians to have difficulties with walking, to stumble or fall.
                                  The location is safe if these infrequent strong winds appear for only 0.01% of the whole year period, and do not exceed the:
                                  -
                                  20 m/s for typical pedestrians (pedestrianType_ = 0)
                                  15 m/s for sensitive pedestrians (pedestrianType_ = 1): elderly people, cyclists, children
                                  -
                                  So the pedestrian safety categories are the following:
                                  -
                                  0) not safe (upper mentioned wind speeds and its occurrences are exceeded)
                                  1) safe (upper mentioned winds speeds and its occurrences are NOT exceeded)
                                  -
                                  If resultGradient_ input is set to True, then the mentioned category values will be calculated as floats, instead of integers.
        thresholdWindSpeed: Wind speed that for 95% of the chosen analysis period is below the outputted value, for each _analysisGeometry face centroid.
                            It is used to determine the pedestrianComfortCategory output.
                            -
                            In meters/second.
        strongestLocationWindSpeed: The strongest wind speed for the chosen analysis period, for each _analysisGeometry face centroid.
                                    It is used along with pedestrianType_ input to determine the pedestrianSafetyCategory output.
                                    -
                                    In meters/second.
        locationWindSpeed: Wind speed values for each hour during the chosen analysis period, for each _analysisGeometry face centroid.
                           -
                           In meters/second.
        pedestrianComfortMesh: Colored _analysisGeometry mesh in accordance with disposition of the pedestrian wind comfort categories.
                               For explanation of each of the categories, check the upper "pedestrianComfortCategory" output.
        pedestrianSafetyMesh: Colored _analysisGeometry mesh. Coloring performed on the basis of whether the pedestrian safety criteria for the chosen location is fulfilled or not.
                              For explanation of each of the categories, check the upper "pedestrianSafetyCategory" output.
                              -
                              Green colored areas are locations where the pedestrian safety criteria has been fulfilled.
                              Red colored areas are locations where the pedestrian safety criteria has NOT been fulfilled.
        legend: Legend for the pedestrianComfortMesh and its title.
        legend2: Legend for the pedestrianSafetyMesh and its title.
                 -
                 Red colored areas are locations where the pedestrian safety criteria has NOT been fulfilled.
                 Green colored areas are locations where the pedestrian safety criteria has been fulfilled.
        legendBasePt: Legend base point, which can be used to move the "legend" geometry with grasshopper's "Move" component.
                      -
                      Connect this output to a Grasshopper's "Point" parameter in order to preview the point in the Rhino scene.
        legendBasePt2: Legend2 base point, which can be used to move the "legend2" geometry with grasshopper's "Move" component.
                      -
                      Connect this output to a Grasshopper's "Point" parameter in order to preview the point in the Rhino scene.
"""

ghenv.Component.Name = "Ladybug_Pedestrian Wind Comfort"
ghenv.Component.NickName = "PedestrianWindComfort"
ghenv.Component.Message = 'VER 0.0.64\nFEB_05_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import ghpythonlib.components as ghc
import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import System
import Rhino
import time
import math
import re


def getEpwData(epwFile):
    
    if epwFile:
        try:
            # location data
            locationName, latitude, longitude, timeZone, elevation, locationString = lb_preparation.epwLocation(epwFile)
            # weather data
            weatherData = lb_preparation.epwDataReader(epwFile, locationName)
            dryBulbTemperature, dewPointTemperature, relativeHumidity, windSpeed, windDirection, directNormalRadiation, diffuseHorizontalRadiation, globalHorizontalRadiation, directNormalIlluminance, diffuseHorizontalIlluminance, globalHorizontalIlluminance, totalSkyCover, liquidPrecipitationDepth, barometricPressure, modelYear = weatherData
            
            windSpeedData = windSpeed[7:]
            windDirectionData = windDirection[7:]
            
            validEpwData = True
            printMsg = "ok"
            
            return locationName, windSpeedData, windDirectionData, validEpwData, printMsg
        
        except Exception, e:
            # something is wrong with "_epwFile" input
            locationName = windSpeedData = windDirectionData = None
            validEpwData = False
            printMsg = "Something is wrong with \"_epwFile\" input."
    else:
        locationName = windSpeedData = windDirectionData = None
        validEpwData = False
        printMsg = "Please supply an .epw file path to the \"_epwFile\" input."
    
    return locationName, windSpeedData, windDirectionData, validEpwData, printMsg


def HOYs_from_analysisPeriod(analysisPeriod):
    
    if (len(analysisPeriod) != 0) and (analysisPeriod[0] != None):
        startingDate = analysisPeriod[0]
        endingDate = analysisPeriod[1]
        startingHOY = lb_preparation.date2Hour(startingDate[0], startingDate[1], startingDate[2])
        endingHOY = lb_preparation.date2Hour(endingDate[0], endingDate[1], endingDate[2])
        
        if (startingHOY < endingHOY):
            HOYs = range(startingHOY, endingHOY+1)
        elif (startingHOY > endingHOY):
            startingHOYs = range(startingHOY, 8760+1)
            endingHOYs = range(1,endingHOY+1)
            HOYs = startingHOYs + endingHOYs
    
    else:  # no "analysisPeriod_" inputted. Use the whole year period
        HOYs = range(1,8761)
        analysisPeriod = [(1, 1, 1),(12, 31, 24)]
    
    days = []
    months = []
    hours = []
    for hoy in HOYs:
        d, m, h = lb_preparation.hour2Date(hoy, True)
        days.append(d)
        months.append(m + 1)
        hours.append(h)
    
    startingDate = lb_preparation.hour2Date(lb_preparation.date2Hour(months[0], days[0], hours[0]))
    endingDate = lb_preparation.hour2Date(lb_preparation.date2Hour(months[-1], days[-1], hours[-1]))
    date = startingDate + " to " + endingDate
    
    return HOYs, analysisPeriod, date


def checkInputData(windFactor, analysisGeometryMesh, pedestrianType, north, northCfd, resultGradient, analysisPeriod):
    
    if (windFactor.DataCount == 0):  # if an empty data tree inputted into "_windFactor". Not if "None" inputted into "_windFactor"
        windFactorsPerPointLL = analysisGeometryMesh = cfdSimulationDirections = pedestrianSafetyThreshold = northCfdD = northD = resultGradient = HOYs = analysisPeriod = date = None
        validInputData = False
        printMsg = "Please supply the data to the \"_windFactor\" input.\n" + \
                   "\"_windFactor\" data should be supplied into different branches corresponding to different directions for which the cfd simulation has been performed.\n" + \
                   "For example: the first branch holds windFactors for all analysis points for wind direction 0. Second branch would hold windFactors for all analysis points for wind direction 20. Third branch would hold windFactors for all analysis points for wind direction 40 ... and so on."
        return windFactorsPerPointLL, analysisGeometryMesh, cfdSimulationDirections, pedestrianSafetyThreshold, northCfdD, northD, resultGradient, HOYs, analysisPeriod, date, validInputData, printMsg
    
    
    windFactorPaths = windFactor.Paths
    windFactorBranchesLists = windFactor.Branches  # each subList contains windFactors for all points for particular cfd direction
    windFactorBranchesFirstListLength = len(windFactorBranchesLists[0])
    
    windFactorAllBranchesEqualLength = 0
    for windFactorList in windFactorBranchesLists:
        if len(windFactorList) == windFactorBranchesFirstListLength:
            windFactorAllBranchesEqualLength += 1
    if windFactorAllBranchesEqualLength != len(windFactor.Branches):
        windFactorsPerPointLL = analysisGeometryMesh = cfdSimulationDirections = pedestrianSafetyThreshold = northCfdD = northD = resultGradient = HOYs = analysisPeriod = date = None
        validInputData = False
        printMsg = "The \"_windFactor\" data you supplied has unequal number of values in its branches.\n" + \
                   "Please input the \"_windFactor\" data with equal number of values in all its branches."
        return windFactorsPerPointLL, analysisGeometryMesh, cfdSimulationDirections, pedestrianSafetyThreshold, northCfdD, northD, resultGradient, HOYs, analysisPeriod, date, validInputData, printMsg
    
    
    if (analysisGeometryMesh == None):
        windFactorsPerPointLL = analysisGeometryMesh = cfdSimulationDirections = pedestrianSafetyThreshold = northCfdD = northD = resultGradient = HOYs = analysisPeriod = date = None
        validInputData = False
        printMsg = "Please supply a mesh to the \"_analysisGeometry\" input.\n" + \
                   "-\n" + \
                   "The number of mesh face centroids needs to be equal to the number of values in each of the \"_windFactor\" branches."
        return windFactorsPerPointLL, analysisGeometryMesh, cfdSimulationDirections, pedestrianSafetyThreshold, northCfdD, northD, resultGradient, HOYs, analysisPeriod, date, validInputData, printMsg
    else:
        faceCentroids = [analysisGeometryMesh.Faces.GetFaceCenter(i) for i in xrange(analysisGeometryMesh.Faces.Count)]
        if len(faceCentroids) != windFactorBranchesFirstListLength:
            windFactorsPerPointLL = analysisGeometryMesh = cfdSimulationDirections = pedestrianSafetyThreshold = northCfdD = northD = resultGradient = HOYs = analysisPeriod = date = None
            validInputData = False
            printMsg = "The mesh you supplied to the \"_analysisGeometry\" input does not have the same number of face centroids as the number of values in each \"_windFactor\" branches.\n" + \
                       "Please input a mesh which does."
            return windFactorsPerPointLL, analysisGeometryMesh, cfdSimulationDirections, pedestrianSafetyThreshold, northCfdD, northD, resultGradient, HOYs, analysisPeriod, date, validInputData, printMsg
    
    
    if (pedestrianType == None):
        pedestrianSafetyThreshold = 20  # default, typical pedestrian
    elif (pedestrianType == 0):
        pedestrianSafetyThreshold = 20  # typical pedestrian
    elif (pedestrianType == 1):
        pedestrianSafetyThreshold = 15  # sensitive pedestrians (elderly people, cyclists, children)
    elif (pedestrianType < 0) or (pedestrianType > 1):
        pedestrianSafetyThreshold = 20  # default, typical pedestrian
        printMsg = "The \"pedestrianType_\" input can only take \"0\" or \"1\" as inputs.\n" + \
                   "\"pedestrianType_\" input set to \"0\" (typical pedestrian)."
    
    
    if (north == None):
        northRad = 0  # default, in radians
        northVec = Rhino.Geometry.Vector3d(0,1,0)
    else:
        try:  # check if it's a number
            north = float(north)
            if north < 0 or north > 360:
                windFactorsPerPointLL = analysisGeometryMesh = cfdSimulationDirections = pedestrianSafetyThreshold = northCfdD = northD = resultGradient = HOYs = analysisPeriod = date = None
                validInputData = False
                printMsg = "Please input north angle value from 0 to 360."
                return windFactorsPerPointLL, analysisGeometryMesh, cfdSimulationDirections, pedestrianSafetyThreshold, northCfdD, northD, resultGradient, HOYs, analysisPeriod, date, validInputData, printMsg
        except Exception, e:  # check if it's a vector
            north.Unitize()
        
        northRad, northVec = lb_photovoltaics.angle2northClockwise(north)
    northVec.Unitize()
    northD = 360-math.degrees(northRad)
    if northD == 360: northD = 0
    
    
    if (northCfd == None):
        northCfdRad = 0  # default, in radians
        northCfdVec = Rhino.Geometry.Vector3d(0,1,0)
    else:
        try:  # check if it's a number
            northCfd = float(northCfd)
            if northCfd < 0 or northCfd > 360:
                windFactorsPerPointLL = analysisGeometryMesh = cfdSimulationDirections = pedestrianSafetyThreshold = northCfdD = northD = resultGradient = HOYs = analysisPeriod = date = None
                validInputData = False
                printMsg = "Please input northCfd angle value from 0 to 360."
                return windFactorsPerPointLL, analysisGeometryMesh, cfdSimulationDirections, pedestrianSafetyThreshold, northCfdD, northD, resultGradient, HOYs, analysisPeriod, date, validInputData, printMsg
        except Exception, e:  # check if it's a vector
            northCfd.Unitize()
        
        northCfdRad, northCfdVec = lb_photovoltaics.angle2northClockwise(northCfd)
    northCfdVec.Unitize()
    northCfdD = 360-math.degrees(northCfdRad)
    if northCfdD == 360: northCfdD = 0
    
    
    if (resultGradient == None):
        resultGradient = True  # default
    
    
    HOYs, analysisPeriod, date = HOYs_from_analysisPeriod(analysisPeriod)
    
    
    cfdSimulationDirections = []  # directions for which cfd simulation has been conducted and from it the _windFactors branches created
    startingCfdSimulationDirection = 0
    cfdSimulationDirectionStep = 360/len(windFactor.Branches)
    for i in range(len(windFactor.Branches)):
        cfdSimulationDirections.append(startingCfdSimulationDirection)
        startingCfdSimulationDirection += cfdSimulationDirectionStep
    
    
    # create windFactors for each point in a single list
    windFactorsPerPointLL = [[] for i in range(len(windFactorBranchesLists[0]))]
    for i in range(len(windFactorBranchesLists[0])):
        for k in range(len(windFactorBranchesLists)):
            windFactorsPerPointLL[i].append(windFactorBranchesLists[k][i])
    
    
    validInputData = True
    printMsg = "ok"
    
    return windFactorsPerPointLL, analysisGeometryMesh, cfdSimulationDirections, pedestrianSafetyThreshold, northCfdD, northD, resultGradient, HOYs, analysisPeriod, date, validInputData, printMsg


def checkAnnualHourlyInputData(annualHourlyData):
    
    if annualHourlyData == []:
        annualHourlyDataLists = []
        annualHourlyDataListsEpwNames = []
        validAnnualHourlyData = True
        printMsg = "ok"
        return validAnnualHourlyData, annualHourlyDataLists, annualHourlyDataListsEpwNames, printMsg
    elif len(annualHourlyData) % 8767 != 0:
        annualHourlyDataLists = annualHourlyDataListsEpwNames = None
        validAnnualHourlyData = False
        printMsg = "Your annualHourlyData_ input is not correct. Please input complete 8767 items long list(s) from \"Ladybug_Import epw\" component"
        return annualHourlyDataLists, validAnnualHourlyData, annualHourlyDataListsEpwNames, printMsg
    else:
        annualHourlyDataLists = []
        annualHourlyDataListsEpwNames = []
        startIndex = 0
        endIndex = 8767
        for i in range(int(len(annualHourlyData)/8767)):
            untrimmedList = annualHourlyData[startIndex:endIndex]
            trimmedList = untrimmedList[7:]
            annualHourlyDataListsName = untrimmedList[2]
            annualHourlyDataLists.append(trimmedList)
            annualHourlyDataListsEpwNames.append(annualHourlyDataListsName)
            startIndex += 8767
            endIndex += 8767
        
        validAnnualHourlyData = True
        printMsg = "ok"
        return validAnnualHourlyData, annualHourlyDataLists, annualHourlyDataListsEpwNames, printMsg


def checkConditionalStatement(conditionalStatement, annualHourlyDataLists, annualHourlyDataListsEpwNames, weatherPerHourDataSubLists, addZero):
    
    if conditionalStatement == None and len(annualHourlyDataLists) > 0: # conditionalStatement_ not inputted, annualHourlyData_ inputted
        validConditionalStatement = False
        weatherPerHourDataConditionalStatementSubLists = conditionalStatementForFinalPrint = None
        printMsg = "Please supply \"conditionalStatement_\" for inputted \"annualHourlyData_\" data."
        return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg
    elif conditionalStatement == None and len(annualHourlyDataLists) == 0:  # conditionalStatement_ not inputted, annualHourlyData_ not inputted
        conditionalStatement = "True"
    else:  # conditionalStatement_ inputted, annualHourlyData_ not
        if annualHourlyDataLists == []:
            validConditionalStatement = False
            weatherPerHourDataConditionalStatementSubLists = conditionalStatementForFinalPrint = None
            printMsg = "Please supply \"annualHourlyData_\" data for inputted \"conditionalStatement_\"."
            return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg
        else:  # both conditionalStatement_ and annualHourlyData_ inputted
            conditionalStatement = conditionalStatement.lower()
            conditionalStatement = re.sub(r"\b([a-z])\b", r"\1[i]", conditionalStatement)
    
    annualHourlyDataListsNames = map(chr, range(97, 123))
    
    # finalPrint conditonal statements for "printOutput" function
    if conditionalStatement != "True":  # conditionalStatement_ not inputted
        # replace conditionalStatement annualHourlyDataListsNames[i] names with annualHourlyDataListsEpwNames:
        conditionalStatementForFinalPrint = conditionalStatement[:]
        for i in range(len(annualHourlyDataLists)):
            conditionalStatementForFinalPrint = conditionalStatementForFinalPrint.replace(annualHourlyDataListsNames[i]+"[i]", annualHourlyDataListsEpwNames[i])
    else:
        conditionalStatementForFinalPrint = "No condition"
    
    annualHourlyDataListsNames = map(chr, range(97, 123))
    numberOfLetters = 0
    
    for letter in annualHourlyDataListsNames:
        changedLetter = letter+"[i]"
        if changedLetter in conditionalStatement:
            numberOfLetters += 1
    if numberOfLetters > len(annualHourlyDataLists):
        validConditionalStatement = False
        weatherPerHourDataConditionalStatementSubLists = conditionalStatementForFinalPrint = None
        printMsg = "The number of a,b,c... variables you supplied in \"conditionalStatement_\" is larger than the number of \"annualHourlyData_\" lists you inputted. Please make the numbers of these two equal or less."
        return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg
    else:
        for i in range(len(annualHourlyDataLists)):
            exec("%s = %s" % (annualHourlyDataListsNames[i],annualHourlyDataLists[i]))
        
        try:
            weatherPerHourDataConditionalStatementSubLists = []
            for i in range(len(weatherPerHourDataSubLists)):
                weatherPerHourDataConditionalStatementSubLists.append([])
            for i in range(len(weatherPerHourDataSubLists[0])):
                exec("conditionalSt = %s" % conditionalStatement)
                if addZero == True:  # add 0 if conditionalStatement == False
                    if conditionalSt:
                        for k in range(len(weatherPerHourDataConditionalStatementSubLists)):
                            weatherPerHourDataConditionalStatementSubLists[k].append(weatherPerHourDataSubLists[k][i])
                    else:
                        for k in range(len(weatherPerHourDataConditionalStatementSubLists)):
                            weatherPerHourDataConditionalStatementSubLists[k].append(0)
                else:  # skip the value
                    if conditionalSt:
                        for k in range(len(weatherPerHourDataConditionalStatementSubLists)):
                            weatherPerHourDataConditionalStatementSubLists[k].append(weatherPerHourDataSubLists[k][i])
        except Exception, e:
            validConditionalStatement = False
            weatherPerHourDataConditionalStatementSubLists = conditionalStatementForFinalPrint = None
            printMsg = "Your \"conditionalStatement_\" is incorrect. Please provide a valid conditional statement in Python, such as \"a>25 and b<80\" (without the quotation marks)"
            return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg
        
        if len(weatherPerHourDataConditionalStatementSubLists[0]) == 0:
            validConditionalStatement = False
            weatherPerHourDataConditionalStatementSubLists = conditionalStatementForFinalPrint = None
            printMsg = "No \"annualHourlyData_\" coresponds to \"conditionalStatement_\". Please edit your \"conditionalStatement_\""
            return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg
        else:
            validConditionalStatement = True
            printMsg = "ok"
            return validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg


def correctEpwWindDirection(cfdSimulationDirections, epwWindDirection):
    # correct the "windDirectionsData" according to the "cfdSimulationDirections"
    # the first closer value will always be used (e.g. epwWindDirection = 30, cfdSimulationDirections = [0,60...], closestEpwWindDirection = 0
    
    difference = []
    for index,cfdSimulationDir in enumerate(cfdSimulationDirections):
        if (epwWindDirection < 90) and (cfdSimulationDir > 270): cfdSimulationDir = abs(360-cfdSimulationDir)  # if 0 to 90 epwWindDirection is closer to 270 to 360 degrees than 0 to 90 degrees
        difference.append([abs(epwWindDirection-cfdSimulationDir),index])
    difference.sort()
    
    closestEpwWindDirection = cfdSimulationDirections[difference[0][1]]
    if (closestEpwWindDirection == 360) and (0 in cfdSimulationDirections):
        closestEpwWindDirection = 0
    
    return closestEpwWindDirection


def percentile(listOfValues, percent, key=lambda x:x):
    # by Wai Yip Tung
    # http://code.activestate.com/recipes/511478
    
    k = (len(listOfValues)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(listOfValues[int(k)])
    d0 = key(listOfValues[int(f)]) * (c-k)
    d1 = key(listOfValues[int(c)]) * (k-f)
    
    return d0+d1


def choosePedestrianComfortCategory(windSpeed95percentPerYear):
    
    if (windSpeed95percentPerYear < 4):
        pedestrianComfortCategoryInt_perPoint = 0
        pedestrianComfortCategoryFloat_perPoint = windSpeed95percentPerYear - 3
        if pedestrianComfortCategoryFloat_perPoint < 0: pedestrianComfortCategoryFloat_perPoint = 0
    elif (windSpeed95percentPerYear >= 4) and (windSpeed95percentPerYear < 6):
        pedestrianComfortCategoryInt_perPoint = 1
        if windSpeed95percentPerYear <= 5:
            pedestrianComfortCategoryFloat_perPoint = windSpeed95percentPerYear - 3
        elif windSpeed95percentPerYear < 6:
            pedestrianComfortCategoryFloat_perPoint = windSpeed95percentPerYear - 4
    elif (windSpeed95percentPerYear >= 6) and (windSpeed95percentPerYear < 8):
        pedestrianComfortCategoryInt_perPoint = 2
        if windSpeed95percentPerYear <= 7:
            pedestrianComfortCategoryFloat_perPoint = windSpeed95percentPerYear - 4
        elif windSpeed95percentPerYear < 8:
            pedestrianComfortCategoryFloat_perPoint = windSpeed95percentPerYear - 5
    elif (windSpeed95percentPerYear >= 8) and (windSpeed95percentPerYear < 10):
        pedestrianComfortCategoryInt_perPoint = 3
        if windSpeed95percentPerYear <= 9:
            pedestrianComfortCategoryFloat_perPoint = windSpeed95percentPerYear - 5
        elif windSpeed95percentPerYear < 10:
            pedestrianComfortCategoryFloat_perPoint = windSpeed95percentPerYear - 6
    elif (windSpeed95percentPerYear >= 10):
        pedestrianComfortCategoryInt_perPoint = 4
        pedestrianComfortCategoryFloat_perPoint = 4.0
    
    return pedestrianComfortCategoryInt_perPoint, pedestrianComfortCategoryFloat_perPoint


def main(windSpeedData, windDirectionData, windFactorsPerPointLL, outputLocationWindSpeed, analysisGeometryMesh, cfdSimulationDirections, pedestrianSafetyThreshold, northCfdD, northD, resultGradient, HOYs, analysisPeriod):
    
    # correct the cfdSimulationDirections for the inputted "northCfd_"
    cfdSimulationDirections_corrected = []
    for cfdWindDirection in cfdSimulationDirections:
        correctedCfdWindDirection, northDegDummy, validNorthDummy, printMsgDummy = lb_photovoltaics.correctSrfAzimuthDforNorth(northCfdD, cfdWindDirection)
        cfdSimulationDirections_corrected.append(correctedCfdWindDirection)
    
    # correct the cfdSimulationDirections for the inputted "northCfd_"
    cfdSimulationDirections_corrected_forWindDirectionData_corrected2 = []
    for cfdWindDirection2 in cfdSimulationDirections:
        correctedCfdWindDirection, northDegDummy, validNorthDummy, printMsgDummy = lb_photovoltaics.correctSrfAzimuthDforNorth(northCfdD, cfdWindDirection2)
        cfdSimulationDirections_corrected_forWindDirectionData_corrected2.append(correctedCfdWindDirection)
    if 360 not in cfdSimulationDirections_corrected_forWindDirectionData_corrected2:
        cfdSimulationDirections_corrected_forWindDirectionData_corrected2.append(360+northCfdD)  # add 360, so that "windDirectionData" values closer to 360 will be corrected to 360, and then set to 0, if there are both 0 and 360 in "cfdSimulationDirections"
    
    
    # correct the .epw windDirectionData for the inputted "north_"
    windDirectionData_corrected = []
    for epwWindDirection in windDirectionData:
        correctedEpwWindDirection, northDegDummy, validNorthDummy, printMsgDummy = lb_photovoltaics.correctSrfAzimuthDforNorth(northD, epwWindDirection)
        windDirectionData_corrected.append(correctedEpwWindDirection)
    
    
    # correct (simplify) the .epw windDirectionData for the cfdSimulationDirections
    windDirectionData_corrected2 = []  
    for epwWindDirection2 in windDirectionData_corrected:
        correctedEpwWindDirection2 = correctEpwWindDirection(cfdSimulationDirections_corrected_forWindDirectionData_corrected2, epwWindDirection2)
        windDirectionData_corrected2.append(correctedEpwWindDirection2)
    
    
    # correct epw windSpeed with windFactor for each point
    windSpeedDataPerPointDataTree_corrected = Grasshopper.DataTree[object]()  # "locationWindSpeed" output
    header = ["key:location/dataType/units/frequency/startsAt/endsAt", "%s" % locationName, "Location's wind speed", "m/s", "Hourly", analysisPeriod[0], analysisPeriod[1]]
    
    windSpeedDataPerPointLL_corrected = []
    for pointIndex, windFactorsPerPointL in enumerate(windFactorsPerPointLL):  # iterrate through each point
        windSpeedDataPerPoint_corrected = []
        for hoy in HOYs:
            hoyIndex = hoy - 1
            for cfdDirIndex,correctedCfdWindDirection in enumerate(cfdSimulationDirections_corrected):
                correctedEpwWindDirection2 = windDirectionData_corrected2[hoyIndex]
                if (correctedEpwWindDirection2 == correctedCfdWindDirection):
                    correctedEpwWindSpeed = windSpeedData[hoyIndex] * windFactorsPerPointL[cfdDirIndex]  # "locationWindSpeed" output hourly value
                    windSpeedDataPerPoint_corrected.append(correctedEpwWindSpeed)
                    break
        windSpeedDataPerPointLL_corrected.append(windSpeedDataPerPoint_corrected)
        if outputLocationWindSpeed:
            path = Grasshopper.Kernel.Data.GH_Path(pointIndex)
            windSpeedDataPerPointDataTree_corrected.AddRange(header + windSpeedDataPerPoint_corrected, path)
    
    
    # Lawson's comfort and safety assessment criteria (1990)
    pedestrianComfortCategoryInt_forAllPoints = []
    pedestrianComfortCategoryFloat_forAllPoints = []
    pedestrianSafetyInt_forAllPoints = []
    pedestrianSafetyFloat_forAllPoints = []
    windSpeed95percentPerYear_forAllPoints = []
    strongestLocationWindSpeed_forAllPoints = []
    for windSpeedDataPerPoint_corrected in windSpeedDataPerPointLL_corrected:
        # pedestrian comfort
        windSpeedDataPerPoint_corrected.sort()
        windSpeed95percentPerYear = percentile(windSpeedDataPerPoint_corrected, 0.95)  # "windSpeed95percentPerYear" is threshold wind speed for particular point, in m/s
        pedestrianComfortCategoryInt_perPoint, pedestrianComfortCategoryFloat_perPoint = choosePedestrianComfortCategory(windSpeed95percentPerYear)
        windSpeed95percentPerYear_forAllPoints.append(windSpeed95percentPerYear)
        pedestrianComfortCategoryInt_forAllPoints.append(pedestrianComfortCategoryInt_perPoint)
        pedestrianComfortCategoryFloat_forAllPoints.append(pedestrianComfortCategoryFloat_perPoint)
        
        # pedestrian safety
        if (windSpeedDataPerPoint_corrected[-1] > pedestrianSafetyThreshold):  # check if pedestrianSafetyThreshold wind speed appeared at least 0.011% during the chosen analysis period
            pedestrianSafetyInt_perPoint = 0  # False
            pedestrianSafetyFloat_perPoint = 0.0  # False
        else:
            pedestrianSafetyInt_perPoint = 1  # True
            pedestrianSafetyFloat_perPoint = 1-(windSpeedDataPerPoint_corrected[-1]/pedestrianSafetyThreshold)  # True
        pedestrianSafetyInt_forAllPoints.append(pedestrianSafetyInt_perPoint)
        pedestrianSafetyFloat_forAllPoints.append(pedestrianSafetyFloat_perPoint)
        strongestLocationWindSpeed_forAllPoints.append(windSpeedDataPerPoint_corrected[-1])
    
    if resultGradient == True:
        pedestrianComfortCategory_forAllPoints = pedestrianComfortCategoryFloat_forAllPoints
        pedestrianSafety_forAllPoints = pedestrianSafetyFloat_forAllPoints
    elif resultGradient == False:
        pedestrianComfortCategory_forAllPoints = pedestrianComfortCategoryInt_forAllPoints
        pedestrianSafety_forAllPoints = pedestrianSafetyInt_forAllPoints
    
    
    return windSpeedDataPerPointDataTree_corrected, windSpeed95percentPerYear_forAllPoints, strongestLocationWindSpeed_forAllPoints, pedestrianComfortCategory_forAllPoints, pedestrianSafety_forAllPoints


def createGeometry(legendPar, locationName, analysisGeometryMesh, pedestrianComfortCategory_forAllPoints, pedestrianSafety_forAllPoints, resultGradient, date):
    
    # extract data from "legendPar_" input
    if len(legendPar) == 0:
        lowB = "min"; highB = "max"; legendBasePt = None; legendScale = 1; legendFont = None; legendFontSize = None; legendBold = None; decimalPlaces = 2; removeLessThan = False
        
        # define the colors according to present pedestrian category values in pedestrianComfortCategory_forAllPoints
        unique_pedestrianComfortCategory_forAllPoints = list(set(pedestrianComfortCategory_forAllPoints))
        customColors = []
        for categoryNumber in unique_pedestrianComfortCategory_forAllPoints:
            if int(categoryNumber) == 4:
                customColors.append(System.Drawing.Color.FromArgb(75,107,169))  # sitting
                customColors.append(System.Drawing.Color.FromArgb(176,203,237))  # standing
                customColors.append(System.Drawing.Color.FromArgb(249,235,89))  # leisurely walking
                customColors.append(System.Drawing.Color.FromArgb(235,131,5))  # business walking
                customColors.append(System.Drawing.Color.FromArgb(234,38,0))  # uncomfortable
                break
        else:
            for categoryNumber in unique_pedestrianComfortCategory_forAllPoints:
                if int(categoryNumber) == 3:
                    customColors.append(System.Drawing.Color.FromArgb(75,107,169))  # sitting
                    customColors.append(System.Drawing.Color.FromArgb(176,203,237))  # standing
                    customColors.append(System.Drawing.Color.FromArgb(249,235,89))  # leisurely walking
                    customColors.append(System.Drawing.Color.FromArgb(235,131,5))  # business walking
                    break
            else:
                for categoryNumber in unique_pedestrianComfortCategory_forAllPoints:
                    if int(categoryNumber) == 2:
                        customColors.append(System.Drawing.Color.FromArgb(75,107,169))  # sitting
                        customColors.append(System.Drawing.Color.FromArgb(176,203,237))  # standing
                        customColors.append(System.Drawing.Color.FromArgb(249,235,89))  # leisurely walking
                        break
                else:
                    for categoryNumber in unique_pedestrianComfortCategory_forAllPoints:
                        if int(categoryNumber) == 1:
                            customColors.append(System.Drawing.Color.FromArgb(75,107,169))  # sitting
                            customColors.append(System.Drawing.Color.FromArgb(176,203,237))  # standing
                            break
                    else:
                        for categoryNumber in unique_pedestrianComfortCategory_forAllPoints:
                            if int(categoryNumber) == 0:
                                customColors.append(System.Drawing.Color.FromArgb(75,107,169))  # sitting
                                customColors.append(System.Drawing.Color.FromArgb(176,203,237))  # standing
                                break
        
        numSeg = len(customColors)
        legendPar = [lowB, highB, numSeg, customColors, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan]
    else:
        lowB, highB, numSeg, customColors, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    # always used for legend2:
    numSeg2 = 2; lowB2 = "min"; highB2 = "max";
    customColors2 = [System.Drawing.Color.FromArgb(255,0,0), System.Drawing.Color.FromArgb(42,182,64)]
    # fix in case all values in the "pedestrianSafety_forAllPoints" are 1 (in case resultGradient == False), or > 0 (in case resultGradient == True):
    numberOfSafePoints = [math.ceil(item) for item in pedestrianSafety_forAllPoints if math.ceil(item) == 1]
    if len(numberOfSafePoints) == len(pedestrianSafety_forAllPoints):  # all points are safe (have value: 1)
        customColors2 = [System.Drawing.Color.FromArgb(42,182,64), System.Drawing.Color.FromArgb(255,0,0)]
    
    # color the analysisGeometryMesh to pedestrianComfortMesh
    pedestrianComfortCategory_colors = lb_visualization.gradientColor(pedestrianComfortCategory_forAllPoints, lowB, highB, customColors)
    pedestrianComfortMesh = lb_visualization.colorMesh(pedestrianComfortCategory_colors, analysisGeometryMesh)
    
    # color the analysisGeometryMesh to pedestrianSafetyMesh
    pedestrianSafety_colors = lb_visualization.gradientColor(pedestrianSafety_forAllPoints, lowB, highB, customColors2)
    pedestrianSafetyMesh = lb_visualization.colorMesh(pedestrianSafety_colors, analysisGeometryMesh)
    
    # move the pedestrianSafetyMesh below from the pedestrianComfortMesh
    lb_visualization.calculateBB([analysisGeometryMesh])
    pedestrianComfortMesh_bottomLeftPt = lb_visualization.BoundingBoxPar[5]
    pedestrianSafetyMesh_bottomLeftPt = Rhino.Geometry.Point3d(pedestrianComfortMesh_bottomLeftPt.X, pedestrianComfortMesh_bottomLeftPt.Y-(2*lb_visualization.BoundingBoxPar[2]), pedestrianComfortMesh_bottomLeftPt.Z)
    transformMatrix = Rhino.Geometry.Transform.PlaneToPlane(Rhino.Geometry.Plane(pedestrianComfortMesh_bottomLeftPt, Rhino.Geometry.Vector3d(0,0,1)), Rhino.Geometry.Plane(pedestrianSafetyMesh_bottomLeftPt, Rhino.Geometry.Vector3d(0,0,1)))
    pedestrianSafetyMesh.Transform(transformMatrix)
    
    
    # titlePedestrianComfort
    if legendFont == None: legendFont = "Verdana"
    if legendFontSize == None: legendFontSize = ((lb_visualization.BoundingBoxPar[2]/10)/3) * legendScale
    legendFontSize = legendFontSize * 1.2  # enlarge the title font size 1.2 times of the legend font size
    
    titleLabelOrigin = lb_visualization.BoundingBoxPar[5]
    titleLabelOrigin.Y = titleLabelOrigin.Y - (lb_visualization.BoundingBoxPar[2]/10)*legendScale  # (height2d_ofBB/10)*legendScale
    titleLabelText = "Pedestrian wind comfort\n%s\n%s" % (locationName, date)
    titleLabelMeshes = lb_visualization.text2srf([titleLabelText], [titleLabelOrigin], legendFont, legendFontSize*1.2, legendBold, None, 6)[0]
    titleDescriptionLabelMeshes = titleLabelMeshes
    
    # titlePedestrianSafety
    titleLabelOrigin2 = Rhino.Geometry.Point3d(pedestrianSafetyMesh_bottomLeftPt.X, pedestrianSafetyMesh_bottomLeftPt.Y, pedestrianSafetyMesh_bottomLeftPt.Z)
    titleLabelOrigin2.Y = titleLabelOrigin2.Y - (lb_visualization.BoundingBoxPar[2]/10)*legendScale  # (height2d_ofBB/10)*legendScale
    titleLabelText2 = "Pedestrian wind safety\n%s\n%s" % (locationName, date)
    titleLabelMeshes2 = lb_visualization.text2srf([titleLabelText2], [titleLabelOrigin2], legendFont, legendFontSize*1.2, legendBold, None, 6)[0]
    titleDescriptionLabelMeshes2 = titleLabelMeshes2
    
    
    # legendPedestrianComfort (legend1)
    if legendBasePt == None:
        legendBasePt = lb_visualization.BoundingBoxPar[0]
    # generate the legend
    try:
        legendSrfs, legendText, legendTextSrfs, textPt, textSize = lb_visualization.createLegend([int(item) for item in pedestrianComfortCategory_forAllPoints], lowB, highB, numSeg, "comfort category", lb_visualization.BoundingBoxPar, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    except:
        validModelTolerance = False
        pedestrianComfortMesh = pedestrianSafetyMesh = titleDescriptionLabelMeshes = titleDescriptionLabelMeshes2 = legend = legend2 = legendBasePt = legendBasePt2 = None
        printMsg = "The mesh you supplied to the _analysisGeometry input is too small for the current Rhino model tolerance.\n" + \
                   "\n" + \
                   "Increase your tolerance by choosing in Rhino: Tools -> Options, then click on Units -> Model.\n" + \
                   "Decrease the \"Absolute tolerance\" value. For example if it was: 0.01, set it to 0.001. Click on \"OK\" to close the Rhino Options window.\n" + \
                   "Rerun the \"Pedestrian wind comfort\" component (set the _runIt to False, and then to True)."
        return pedestrianComfortMesh, pedestrianSafetyMesh, titleDescriptionLabelMeshes, titleDescriptionLabelMeshes2, legend, legend2, legendBasePt, legendBasePt2, validModelTolerance, printMsg
    # generate legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    legend = [legendSrfs] + lb_preparation.flattenList(legendTextSrfs)
    
    # legendPedestrianSafety (legend2)
    lb_visualization.calculateBB([pedestrianSafetyMesh])
    legendBasePt2 = Rhino.Geometry.Point3d(legendBasePt.X, legendBasePt.Y -(2*lb_visualization.BoundingBoxPar[2]), legendBasePt.Z)
    # generate the legend2
    legendSrfs2, legendText2, legendTextSrfs2, textPt2, textSize2 = lb_visualization.createLegend([math.ceil(item) for item in pedestrianSafety_forAllPoints], lowB, highB, numSeg2, "safe or not", lb_visualization.BoundingBoxPar, legendBasePt2, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    # generate legend colors2
    legendColors2 = lb_visualization.gradientColor(legendText2[:-1], lowB2, highB2, customColors2)
    # color legend surfaces2
    legendSrfs2 = lb_visualization.colorMesh(legendColors2, legendSrfs2)
    legend2 = [legendSrfs2] + lb_preparation.flattenList(legendTextSrfs2)
    
    
    # hide legendBasePt, legendBasePt2 output
    ghenv.Component.Params.Output[11].Hidden = True
    ghenv.Component.Params.Output[12].Hidden = True
    
    validModelTolerance = True
    printMsg = "ok"
    
    return pedestrianComfortMesh, pedestrianSafetyMesh, titleDescriptionLabelMeshes, titleDescriptionLabelMeshes2, legend, legend2, legendBasePt, legendBasePt2, validModelTolerance, printMsg


def bakingGrouping(locationName, pedestrianComfortMesh, pedestrianSafetyMesh, titleDescriptionLabelMeshes, titleDescriptionLabelMeshes2, legend, legend2):
    
    layerName = locationName
    
    layerIndex, l = lb_visualization.setupLayers(layerName, "LADYBUG", "PEDESTRIAN WIND COMFORT-SAFETY", "WIND ANALYSIS")
    
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex = layerIndex
    attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    attr.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
    
    # bake pedestrianComfortMesh
    geometryIds = []
    geometry = [pedestrianComfortMesh]
    for obj in geometry:
        id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj,attr)
        geometryIds.append(id)
    
    # bake title1
    geometryIds2 = []
    geometry2 = titleDescriptionLabelMeshes
    for obj2 in geometry2:
        id2 = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj2,attr)
        geometryIds2.append(id2)
    
    # bake legend1
    geometryIds3 = []
    geometry3 = legend
    for obj3 in geometry3:
        id3 = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj3,attr)
        geometryIds3.append(id3)
    
    
    # bake pedestrianSafetyMesh
    geometryIds_ = []
    geometry_ = [pedestrianSafetyMesh]
    for obj_ in geometry_:
        id_ = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj_,attr)
        geometryIds_.append(id_)
    
    # bake title2
    geometryIds2_ = []
    geometry2_ = titleDescriptionLabelMeshes2
    for obj2_ in geometry2_:
        id2_ = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj2_,attr)
        geometryIds2_.append(id2_)
    
    # bake legend1
    geometryIds3_ = []
    geometry3_ = legend2
    for obj3_ in geometry3_:
        id3_ = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj3_,attr)
        geometryIds3_.append(id3_)
    
    
    # grouping of pedestrianComfortMesh
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_pedestrianWindComfort_mesh_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, geometryIds)
    # grouping of title1
    groupIndex2 = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_pedestrianWindComfort_title1_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex2, geometryIds2)
    # grouping of legend1
    groupIndex3 = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_pedestrianWindComfort_legend1_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex3, geometryIds3)
    
    # grouping of pedestrianSafetyMesh
    groupIndex_ = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_pedestrianWindSafety_mesh_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex_, geometryIds_)
    # grouping of title2
    groupIndex2_ = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_pedestrianWindComfort_title2_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex2_, geometryIds2_)
    # grouping of legend2
    groupIndex3_ = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_pedestrianWindComfort_legend2_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex3_, geometryIds3_)


def printOutput(locationName, cfdSimulationDirections, pedestrianType, northCfd, north, resultGradient, analysisPeriod, conditionalStatementForFinalPrint):
    
    if pedestrianType == 0:
        pedestrianTypeLabel = "typical pedestrian"
    elif pedestrianType == 1:
        pedestrianTypeLabel = "sensitive pedestrian"
    resultsCompletedMsg = "Pedestrian wind comfort component results successfully completed!"
    printOutputMsg = \
    """
Input data:

Location (deg.): %s
Wind factor directions: %s
Pedestrian type: %s (%s)
North Cfd (deg.): %s
North Rhino (deg.): %s
Result gradient: %s

Analysis period: %s

Caclulation based on the following condition:
%s
    """ % (locationName, cfdSimulationDirections, pedestrianType, pedestrianTypeLabel, northCfd, north, resultGradient, analysisPeriod, conditionalStatementForFinalPrint)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_meshpreparation = sc.sticky["ladybug_Mesh"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        if _epwFile:
            locationName, windSpeedData, windDirectionData, validEpwData, printMsg = getEpwData(_epwFile)
            if validEpwData:
                windFactorsPerPointLL, analysisGeometryMesh, cfdSimulationDirections, pedestrianSafetyThreshold, northCfdD, northD, resultGradient, HOYs, analysisPeriod, date, validInputData, printMsg = checkInputData(_windFactor, _analysisGeometry, pedestrianType_, north_, northCfd_, resultGradient_, analysisPeriod_)
                if validInputData:
                    validAnnualHourlyData, annualHourlyDataLists, annualHourlyDataListsEpwNames, printMsg = checkAnnualHourlyInputData(annualHourlyData_)
                    if validAnnualHourlyData:
                        validConditionalStatement, weatherPerHourDataConditionalStatementSubLists, conditionalStatementForFinalPrint, printMsg = checkConditionalStatement(conditionalStatement_, annualHourlyDataLists, annualHourlyDataListsEpwNames, [windSpeedData, windDirectionData], True)
                        if validConditionalStatement:
                            windSpeedCondStat, windDirectionCondStat = weatherPerHourDataConditionalStatementSubLists
                            if _runIt:
                                outputLocationWindSpeed = False
                                windSpeedDataPerPointDataTree_corrected, windSpeed95percentPerYear_forAllPoints, strongestLocationWindSpeed_forAllPoints, pedestrianComfortCategory_forAllPoints, pedestrianSafety_forAllPoints = main(windSpeedCondStat, windDirectionCondStat, windFactorsPerPointLL, outputLocationWindSpeed, analysisGeometryMesh, cfdSimulationDirections, pedestrianSafetyThreshold, northCfdD, northD, resultGradient, HOYs, analysisPeriod)
                                pedestrianComfortMesh, pedestrianSafetyMesh, titleDescriptionLabelMeshes, titleDescriptionLabelMeshes2, legend, legend2, legendBasePt, legendBasePt2, validModelTolerance, printMsg = createGeometry(legendPar_, locationName, analysisGeometryMesh, pedestrianComfortCategory_forAllPoints, pedestrianSafety_forAllPoints, resultGradient, date)
                                if validModelTolerance:
                                    if bakeIt_: bakingGrouping(locationName, pedestrianComfortMesh, pedestrianSafetyMesh, titleDescriptionLabelMeshes, titleDescriptionLabelMeshes2, legend, legend2)
                                    printOutput(locationName, cfdSimulationDirections, pedestrianType_, northCfd_, north_, resultGradient, analysisPeriod, conditionalStatementForFinalPrint)
                                    pedestrianComfortCategory = pedestrianComfortCategory_forAllPoints; pedestrianSafetyCategory = pedestrianSafety_forAllPoints;
                                    thresholdWindSpeed = windSpeed95percentPerYear_forAllPoints; strongestLocationWindSpeed = strongestLocationWindSpeed_forAllPoints; locationWindSpeed = windSpeedDataPerPointDataTree_corrected;
                                    legend = titleDescriptionLabelMeshes + legend; legend2 = titleDescriptionLabelMeshes2 + legend2
                                else:
                                    print printMsg
                                    ghenv.Component.AddRuntimeMessage(level, printMsg)
                            else:
                                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Pedestrian wind comfort component"
                        else:
                            print printMsg
                            ghenv.Component.AddRuntimeMessage(level, printMsg)
                    else:
                        print printMsg
                        ghenv.Component.AddRuntimeMessage(level, printMsg)
                else:
                    print printMsg
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please supply an .epw file path to the \"_epwFile\" input."
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        printMsg = "You need a newer version of Ladybug to use this component.\n" + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag the Ladybug_Ladybug component " + \
            "into the canvas and try again."
        print printMsg
else:
    printMsg = "First please let the Ladybug fly..."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
