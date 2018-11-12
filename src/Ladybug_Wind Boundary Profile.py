# Wind Profile Curve Visualizer
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Djordje Spasic and Chris Mackey <djordjedspasic@gmail.com and chris@mackeyarchitecture.com> 
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
Use this component to visualize a wind profile curve for a given terrain type.  Wind speed increases as one leaves the ground and wind profiles are a means of visualizing this change in wind speed with height. 
-
The wind profile will point you in the direction of prevailing wind if EPW data is connected to _windSpeed_tenMeters and windDirections_. In case you are trying to orient your building to take advantage of natural ventilation, as a good rule of thumb, it always a good strategy to align the shorter axis of your building parellel to the prevailing wind directions.
-
More information on the power law of the wind profile can be found here: http://en.wikipedia.org/wiki/Wind_profile_power_law
-
Provided by Ladybug 0.0.66
    
    Args:
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _windSpeed_tenMeters: The wind speed from the import EPW component or a number representing the wind speed at 10 meters off the ground.  If this value is input without a corresponding wind direction below, the profile will be drawn with the average of the speed input here.  If corresponding values are connected to the windDirection, the speed on the profile will be the average speed of the prevailing wind direction.
        windDirection_: An optional number representing the degrees from north of the wind direction.  This can also be the windDirection output from the import EPW component.  This direction will be used to orient the wind profile in 3 dimensions to the direction of the prevailing wind.
        terrainType_: An interger or text string that sets the terrain class associated with the output windSpeedAtHeight. Interger values represent the following terrain classes:
            0 = City: large city centres, 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = Suburban: suburbs, wooded areas.
            2 = Country: open, with scattered objects generally less than 10m high.
            3 = Water: Flat, unobstructed areas exposed to wind flowing over a large water body (no more than 500m inland).
        epwTerrain_: An interger or text string that sets the terrain class associated with the output windSpeedAtHeight. The default is set to 2 for flat clear land, which is typical for most EPW files that are recorded at airports.  Interger values represent the following terrain classes:
            0 = City: large city centres, 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = Suburban: suburbs, wooded areas.
            2 = Country: open, with scattered objects generally less than 10m high.
            3 = Water: Flat, unobstructed areas exposed to wind flowing over a large water body (no more than 500m inland).
        powerOrLog_: Set to "True" to use a power law to translate the wind speed to that at a given height and set to "False" to use a log law to translate the wind speed.  The default is set to "True" for a power law as this is the function that is used by EnergyPlus.
        -------------------------: ...
        HOY_ : Use this input to select out specific indices of a list of values connected for wind speed and wind direction.  If you have connected hourly EPW data, this is the equivalent of a "HOY" input and you can use the "Ladybug_DOY_HOY" component to select out a specific hour and date.  Note that this overrides the analysisPeriod_ input below.
        analysisPeriod_: If you have connected data from an EPW component, plug in an analysis period from the Ladybug_Analysis Period component to calculate data for just a portion of the year. The default is Jan 1st 00:00 - Dec 31st 24:00, the entire year.
        annualHourlyData_: An optional list of hourly data from the Import epw component, which will be overlaid on wind rose (e.g. dryBulbTemperature)
        conditionalStatement_: This input allows users to remove data that does not fit specific conditions or criteria from the wind rose. To use this input correctly, hourly data, such as temperature or humidity, must be plugged into the annualHourlyData_ input. The conditional statement input here should be a valid condition statement in Python, such as "a>25" or "b<80" (without quotation marks).
                              The current version of this component accepts "and" and "or" operators. To visualize the hourly data, only lowercase English letters should be used as variables, and each letter alphabetically corresponds to each of the lists (in their respective order): "a" always represents the 1st list, "b" always represents the 2nd list, etc.
                              For the WindBoundaryProfile component, the variable "a" always represents windSpeed. For example, if you have hourly dry bulb temperature connected as the second list, and relative humidity connected as the third list (both to the annualHourlyData_ input), and you want to plot the data for the time period when temperature is between 18C and 23C, and humidity is less than 80%, the conditional statement should be written as 18<b<23 and c<80 (without quotation marks).
        originPt_: An optional point that can be used to change the base point at shich the wind profile curves are generated.  By default, the wond profile curves generate at the Rhino model origin.
        windVectorScale_: An optional number that can be used to change the scale of the wind vectors in relation to the height of the wind profile curve.  The default is set to 5 so that it is easier to see how the wind speed is changing with height.
        windProfileHeight_: An optional number in rc model units that can be used to change the height of the wind profile curve.  By default, the height of the curve is set to 30 meters (or the equivalent distance in your Rhino model units).  You may want to move this number higher or lower depending on the wind effects that you are interested in.
        distBetweenVec_: An optional number in rhino model units that represents the distance between wind vectors in the profile curve.  The default is set to 2 meters (or the equivalent distance in your rc model units).
        windArrowStyle_: An optional integer to set the style of the wind vectors.  The default is set to 1 for colored arrows.  Choose from the following options:
            0 = No Wind Arrows - use this option if you do not want to gerenate arrows.
            1 = 3D Colored Wind Arrows - use this option to generate arrows as a colored 3D mesh (arrows will be colored based on the magnitude of their wind speed).
            2 = High-Res 3D Colored Wind Arrows - use this option to create color arrows just like Option 1 but with a circular cross section and smooth edges.
            3 = Colored Line Wind Arrows - use this option to generate arrows as lines with colored tips.
            4 = Black Line Wind Arrows - use this option to generate arrows as lines with black tips.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
    Returns:
        readMe!: ...
        --------------------: ...
        windSpeeds: The wind speeds that correspond to the wind vectors in the wind profile visualization.
        windDirections: The wind directions that correspond to the wind vectors in the wind profile visualization.
        windVectors: The wind vectors that correspond to those in the wind profile visualization.  Note that the magnitude of these vectors will be scaled based on the windVectorScale_ input.
        vectorAnchorPts: Anchor points for each of the vectors above, which correspond to the height above the ground for each of the vectors.  Connect this along with the output above to a Grasshopper "Vector Display" component to see the vectors as a grasshopper vector display (as opposed to the vector mesh below).
        --------------------: ...
        windVectorMesh: A mesh displaying the wind vectors that were used to make the profile curve.
        windProfileCurve: A curve outlining the wind speed as it changes with height.  This may also be a list of wind profile curves if multiple "HOY_" inputs are connected or "averageData_" is set to False."
        axesText: The meshes of the axes text (labelling wind speeds and heights).
        legend: A legend of the wind profile curves. Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the rc scene.
        legendBasePt: The legend base point(s), which can be used to move the legend in relation to the wind profile with the grasshopper "move" component.
"""
ghenv.Component.Name = "Ladybug_Wind Boundary Profile"
ghenv.Component.NickName = 'WindBoundaryProfile'
ghenv.Component.Message = 'VER 0.0.66\nNOV_13_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.59\nAPR_12_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import Rhino as rc
import scriptcontext as sc
import math
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from System import Object
import System



def checkTheInputs():
    # import the classes
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    lb_wind = sc.sticky["ladybug_WindSpeed"]()
    
    #Define a value that will indicate whether someone has hooked up epw data.
    epwData = False
    epwStr = []
    
    #Check lenth of the _windSpeed_tenMeterslist and evaluate the contents.
    checkData1 = False
    windSpeed = []
    windMultVal = False
    nonPositive = True
    if len(_windSpeed_tenMeters) != 0:
        try:
            if _windSpeed_tenMeters[2] == 'Wind Speed':
                windSpeed = _windSpeed_tenMeters[7:]
                checkData1 = True
                epwData = True
                epwStr = _windSpeed_tenMeters[0:7]
        except: pass
        if checkData1 == False:
            for item in _windSpeed_tenMeters:
                try:
                    if float(item) >= 0:
                        windSpeed.append(float(item))
                        checkData1 = True
                    else: nonPositive = False
                except: checkData1 = False
        if nonPositive == False: checkData1 = False
        if len(windSpeed) > 1: windMultVal = True
        if checkData1 == False:
            warning = '_windSpeed_tenMeters input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData1 = False
        print "Connect wind speed."
    
    #Check lenth of the windDirection_ list and evaluate the contents.
    checkData2 = False
    windDir = []
    dirMultVal = False
    nonPositive = True
    if len(windDirection_) != 0:
        try:
            if windDirection_[2] == 'Wind Direction':
                windDir = windDirection_[7:]
                checkData2 = True
                epwData = True
                epwStr = windDirection_[0:7]
        except: pass
        if checkData2 == False:
            for item in windDirection_:
                try:
                    if float(item) >= 0:
                        windDir.append(float(item))
                        checkData2 = True
                    else: nonPositive = False
                except: checkData2 = False
        if nonPositive == False: checkData2 = False
        if len(windDir) > 1: dirMultVal = True
        if checkData2 == False:
            warning = 'windDirection_ input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData2 = True
        print "No value is connected for wind direction.  The profile will be drawn in 2D and the speed depicted on the profile will be the average of all connected wind speeds."
    
    #Define a function to duplicate data
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    #For those lists of length greater than 1, check to make sure that they are all the same length.
    checkData5 = False
    if checkData1 == True and checkData2 == True :
        if windMultVal == True or dirMultVal == True:
            listLenCheck = []
            if windMultVal == True: listLenCheck.append(len(windSpeed))
            if dirMultVal == True: listLenCheck.append(len(windDir))
            
            if all(x == listLenCheck[0] for x in listLenCheck) == True:
                checkData5 = True
                calcLength = listLenCheck[0]
                
                if windMultVal == False: windSpeed = duplicateData(windSpeed, calcLength)
                if dirMultVal == False and windDir != []: windDir = duplicateData(windDir, calcLength)
                
            else:
                calcLength = None
                warning = 'If you have put in lists with multiple values for wind speed or direction, the lengths of these lists must match across the parameters or you have a single value for a given parameter to be applied to all values in the list.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData5 = True
            calcLength = 1
    else:
        calcLength = 0
    
    #If the user has input a HOY_ that is longer than the calculation length, throw a warning.
    checkData7 = True
    if HOY_ == None: pass
    else:
        if HOY_ > calcLength or HOY_ < 1:
            checkData7 = False
            warning = 'You cannot input a HOY_ that is less than 1 or greater than the length of values in the _windSpeed or windDirection_ lists.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else: pass
    
    # Evaluate the terrain type to get the right roughness length.
    checkData3, terrainType, d, a, rl = lb_wind.readTerrainType(terrainType_, 2)
    if checkData3 == False:
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, 'terrainType_ not correct.')
    else: print "Terrain set to " + terrainType + "."
    
    #Take the model units into account.
    checkData4 = True
    heightsAboveGround = []
    scaleFactor = lb_preparation.checkUnits()
    conversionFactor = 1/(scaleFactor)
    
    #If a height has been entered that is above the boundary layer, set the height to the boundary layer.
    if windProfileHeight_ != None:
        if windProfileHeight_*scaleFactor > d:
            windProfileHeight = float(d)
            print "The input windProfileHeight_ is greater than the boundary layer height. The wind profile height has been set to the boundary layer height."
            r = gh.GH_RuntimeMessageLevel.Remark
            ghenv.Component.AddRuntimeMessage(r, "The input windProfileHeight_ is greater than the boundary layer height. The wind profile height has been set to the boundary layer height.")
        else:
            windProfileHeight = windProfileHeight_
    else: windProfileHeight = None
    
    #Calaculate the heights above the ground to make the vectors from input profile ehight and distance between vectors.
    if windProfileHeight == None:
        windProfileHeight = 30*conversionFactor
        print "Wind profile height set to " + str(windProfileHeight) + " " + str(sc.doc.ModelUnitSystem)
    else:
        if windProfileHeight < distBetweenVec_:
            windProfileHeight = 0
            checkData4 = False
            print "The input windProfileHeight_ cannot be less than 0."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "The input windProfileHeight_ cannot be less than 0.")
        else:
            windProfileHeight = windProfileHeight
            print "Wind profile height set to " + str(windProfileHeight) + " " + str(sc.doc.ModelUnitSystem)
    
    if distBetweenVec_ == None:
        distBetweenVec = 2*conversionFactor
        print "Distance between wind vectors is set to " + str(distBetweenVec) + " " + str(sc.doc.ModelUnitSystem)
    else:
        distBetweenVec = distBetweenVec_
        print "Distance between wind vectors is set to " + str(windProfileHeight) + " " + str(sc.doc.ModelUnitSystem)
    
    if distBetweenVec > windProfileHeight or distBetweenVec < 0:
        distBetweenVec = 0
        checkData4 = False
        print "The input distBetweenVec_ cannot be less than 0 and cannot be less than the windProfileHeight_."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The input distBetweenVec_ cannot be less than 0 and cannot be less than the windProfileHeight_.")
    
    if windProfileHeight != 0 and distBetweenVec != 0:
        height = 0
        for num in range(int((windProfileHeight+distBetweenVec)/distBetweenVec)):
            heightsAboveGround.append(height)
            height += distBetweenVec
    else:
        checkData4 = False
    
    #Make the default analyisis period for the whole year if the user has not input one.
    if analysisPeriod_ == []:
        analysisPeriod = [(1, 1, 1), (12, 31, 24)]
    else:
        analysisPeriod = analysisPeriod_
    
    # Check to make sure that the wind vector scale has not been set to less than zero and set the deault to 5.
    checkData6 = True
    if windVectorScale_ == None:
        windVectorScale = 5
    else:
        if windVectorScale_ < 0:
            windVectorScale = 0
            checkData6 = False
            print "The input windVectorScale_ cannot be less than 0."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "The input windVectorScale_ cannot be less than 0.")
        else:
            windVectorScale = windVectorScale_
    
    checkData8 = True
    if epwTerrain_ != None:
        # Set a defult epwTerrain if none is connected.
        checkData8, epwTerr, metD, metA, metrl = lb_wind.readTerrainType(epwTerrain_, 2)
        if checkData8 == False:
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, 'epwTerrain_ not correct.')
        else: print "epwTerrain_ set to " + epwTerr + "."
    else:
        checkData8, epwTerr, metD, metA, metrl = lb_wind.readTerrainType(2, 2)
        print "epwTerrain_ has been set to (2 = country) for flat clear land, which is typical for most EPW files that are recorded at airports."
    
    #Set a default arrow style if none has been set.
    checkData9 = True
    if windArrowStyle_ != None:
        if windArrowStyle_ <=4 and windArrowStyle_ >= 0: windArrowStyle = windArrowStyle_
        else:
            windArrowStyle = None
            checkData9 = False
            print "You have not connected a correct windArrowStyle_ type."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "You have not connected a correct windArrowStyle_ type.")
    else:
        windArrowStyle = 1
        print "windArrowStyle_ has been set to 1 for colored arrows."
    
    #Check if everything is good.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True  and checkData9 == True:
        checkData = True
    else:
        checkData = False
    
    return checkData, heightsAboveGround, analysisPeriod, d, a, rl, terrainType, epwTerr, metD, metA, metrl, windSpeed, windDir, epwData, epwStr, windArrowStyle, lb_preparation, lb_visualization, lb_wind, windVectorScale, conversionFactor


def checkConditionalStatement(annualHourlyData, conditionalStatement, analysisPeriod, HOYS):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        indexList, listInfo = lb_preparation.separateList(annualHourlyData, lb_preparation.strToBeFound)
        
        
        letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
        # remove 'and' and 'or' from conditional statements
        csCleaned = conditionalStatement.replace('and', '',20000)
        csCleaned = csCleaned.replace('or', '',20000).replace('not', '',20000)
        
        # find the number of the lists that have assigned conditional statements
        listNum = []
        for count, let in enumerate(letters):
            if csCleaned.find(let)!= -1: listNum.append(count)
        
        # check if all the conditions are actually applicable
        for num in listNum:
            if num>len(listInfo) - 1:
                warning = 'A conditional statement is assigned for list number ' + `num + 1` + '  which is not existed!\n' + \
                          'Please remove the letter "' + letters[num] + '" from the statements to solve this problem!\n' + \
                          'Number of lists are ' + `len(listInfo)` + '. Please fix this issue and try again.'
                          
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1, -1
        
        selList = [[]] * len(listInfo)
        for i in range(len(listInfo)):
            selList[i] = annualHourlyData[indexList[i]+7:indexList[i+1]]
            if listInfo[i][4]!='Hourly' or listInfo[i][5]!=(1,1,1) or  listInfo[i][6]!=(12,31,24) or len(selList[i])!=8760:
                warning = 'At least one of the input data lists is not valid ladybug hourly data! Please fix this issue and try again!\n List number = '+ `i+1`
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1, -1
        
        # replace the right list in the conditional statement
        statement = conditionalStatement.split(' ')
        finalStatement = 'pattern = '
        titleStatement = '...                         ...                         ...\n' +\
                         'Conditional Selection Applied:\n'
        
        for statemntPart in statement:
            statementCopy = str.Copy(statemntPart)
            if statemntPart!='and' and statemntPart!='or':
                for num in listNum:
                    toBeReplacedWith = 'selList[this][HOY]'.replace('this', `num`)
                    titleToBeReplacedWith = listInfo[num][2]
                    statemntPart = statemntPart.replace(letters[num], toBeReplacedWith, 20000)
                    statementCopy = statementCopy.replace(letters[num], titleToBeReplacedWith, 20000)
                    if statementCopy.find(letters[num])!=-1: break
                    
                titleStatement = titleStatement + ' ' + statementCopy
            else:
                titleStatement = titleStatement + '\n' + statementCopy 
            finalStatement = finalStatement + ' ' + statemntPart
        print titleStatement
        
        #If there is an analysis period connected, change the sel list to only be for that period.
        if analysisPeriod != [(1, 1, 1), (12, 31, 24)]:
            newSelList = []
            for dataCount, dataList in enumerate(selList):
                newSelList.append([])
                for count in HOYS:
                    newSelList[dataCount].append(dataList[count-1])
            selList = newSelList
        
        # check for the pattern
        patternList = []
        try:
            for HOY in range(len(HOYS)):
                exec(finalStatement)
                patternList.append(pattern)
        except Exception,e:
            warning = 'There is an error in the conditional statement:\n' + `e`
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1, -1
        
        return titleStatement, patternList

def createColoredArrowMesh(count, point, colors, windVec, heightsAboveGround, use1meterArrowHeadSize, scaleFactor):
    meshArrowTip = rc.Geometry.Point3d.Add(point, windVec[count+1])
    meshArrowBottom = point
    meshArrowAxis = rc.Geometry.Line(meshArrowTip, meshArrowBottom)
    meshArrowAxis = meshArrowAxis.ToNurbsCurve()
    
    if (meshArrowAxis.GetLength() > (windVectorScale/1.75)*scaleFactor) and use1meterArrowHeadSize:
        t = meshArrowAxis.LengthParameter((windVectorScale/1.75)*scaleFactor)
    else:
        length = meshArrowAxis.GetLength()* 0.3
        t = meshArrowAxis.LengthParameter(length)
        use1meterArrowHeadSize = False
    meshArrowBottomCentroid = meshArrowAxis.PointAt(t[1])
    meshArrowBottomCircle = rc.Geometry.Circle(rc.Geometry.Plane(meshArrowBottomCentroid, meshArrowTip-meshArrowBottomCentroid), 0.3*(windVectorScale/1.75)*scaleFactor)  # arrow bottom circle radius is a function of the distance between vectors
    meshArrowBottomCircle = meshArrowBottomCircle.ToNurbsCurve()
    t1 = meshArrowBottomCircle.NormalizedLengthParameter(0.125)
    meshArrowBottomPt1 = meshArrowBottomCircle.PointAt(t1[1])
    t2 = meshArrowBottomCircle.NormalizedLengthParameter(0.375)
    meshArrowBottomPt2 = meshArrowBottomCircle.PointAt(t2[1])
    t3 = meshArrowBottomCircle.NormalizedLengthParameter(0.625)
    meshArrowBottomPt3 = meshArrowBottomCircle.PointAt(t3[1])
    t4 = meshArrowBottomCircle.NormalizedLengthParameter(0.875)
    meshArrowBottomPt4 = meshArrowBottomCircle.PointAt(t4[1])
    
    #mesh body
    # top 4 points
    meshbodyTopCircle = rc.Geometry.Circle(rc.Geometry.Plane(meshArrowBottomCentroid, meshArrowTip-meshArrowBottomCentroid), 0.05*(windVectorScale/1.75)*scaleFactor)  # body top circle radius is a function of the distance between vectors
    meshbodyTopCircle = meshbodyTopCircle.ToNurbsCurve()
    t1 = meshbodyTopCircle.NormalizedLengthParameter(0.125)
    meshBodyTopPt1 = meshbodyTopCircle.PointAt(t1[1])
    t2 = meshbodyTopCircle.NormalizedLengthParameter(0.375)
    meshBodyTopPt2 = meshbodyTopCircle.PointAt(t2[1])
    t3 = meshbodyTopCircle.NormalizedLengthParameter(0.625)
    meshBodyTopPt3 = meshbodyTopCircle.PointAt(t3[1])
    t4 = meshbodyTopCircle.NormalizedLengthParameter(0.875)
    meshBodyTopPt4 = meshbodyTopCircle.PointAt(t4[1])
    # bottom 4 points
    meshBodyBottomCircle = rc.Geometry.Circle(rc.Geometry.Plane(meshArrowBottom, meshArrowTip-meshArrowBottomCentroid), 0.1*(windVectorScale/1.75)*scaleFactor)  # body bottom circle radius: 0.2
    meshBodyBottomCircle = meshBodyBottomCircle.ToNurbsCurve()
    t1 = meshBodyBottomCircle.NormalizedLengthParameter(0.125)
    meshBodyBottomPt1 = meshBodyBottomCircle.PointAt(t1[1])
    t2 = meshBodyBottomCircle.NormalizedLengthParameter(0.375)
    meshBodyBottomPt2 = meshBodyBottomCircle.PointAt(t2[1])
    t3 = meshBodyBottomCircle.NormalizedLengthParameter(0.625)
    meshBodyBottomPt3 = meshBodyBottomCircle.PointAt(t3[1])
    t4 = meshBodyBottomCircle.NormalizedLengthParameter(0.875)
    meshBodyBottomPt4 = meshBodyBottomCircle.PointAt(t4[1])
    # create mesh
    mesh = rc.Geometry.Mesh()
    # mesh arrow vertices
    mesh.Vertices.Add(meshArrowBottomPt1)
    mesh.Vertices.Add(meshArrowBottomPt2)
    mesh.Vertices.Add(meshArrowBottomPt3)
    mesh.Vertices.Add(meshArrowBottomPt4)
    mesh.Vertices.Add(meshArrowTip)
    # mesh body vertices
    mesh.Vertices.Add(meshBodyTopPt1)
    mesh.Vertices.Add(meshBodyTopPt2)
    mesh.Vertices.Add(meshBodyTopPt3)
    mesh.Vertices.Add(meshBodyTopPt4)
    mesh.Vertices.Add(meshBodyBottomPt1)
    mesh.Vertices.Add(meshBodyBottomPt2)
    mesh.Vertices.Add(meshBodyBottomPt3)
    mesh.Vertices.Add(meshBodyBottomPt4)
    
    mesh.Faces.AddFace(0,1,2,3)
    mesh.Faces.AddFace(0,1,4)
    mesh.Faces.AddFace(1,2,4)
    mesh.Faces.AddFace(2,3,4)
    mesh.Faces.AddFace(3,0,4)
    
    mesh.Faces.AddFace(5,6,10,9)
    mesh.Faces.AddFace(6,7,11,10)
    mesh.Faces.AddFace(7,8,12,11)
    mesh.Faces.AddFace(8,5,9,12)
    mesh.Faces.AddFace(9,10,11,12)
    
    mesh.VertexColors.CreateMonotoneMesh(colors[count])
    
    return mesh

def createHighResColoredArrows(count, point, colors, windVec, heightsAboveGround, windDir):
    circle = rc.Geometry.Circle(rc.Geometry.Plane(point, windVec[count+1]), scaleFactor*0.05*(windVectorScale/1.75)).ToNurbsCurve()
    extruVec = rc.Geometry.Vector3d(windVec[count+1].X, windVec[count+1].Y, 0)
    extruVec.Unitize()
    extruVec = rc.Geometry.Vector3d.Multiply(scaleFactor*-.5*(windVectorScale/1.75), extruVec)
    extruVec = rc.Geometry.Vector3d.Add(windVec[count+1], extruVec)
    extrusion = rc.Geometry.Brep.CreateFromSurface(rc.Geometry.Surface.CreateExtrusion(circle, extruVec))
    if windDir != []:
        conePlane = rc.Geometry.Plane(rc.Geometry.Point3d(windVec[count+1].X, windVec[count+1].Y, point.Z), windVec[count+1])
    else:
        conePlane = rc.Geometry.Plane(rc.Geometry.Point3d(windVec[count+1].X, point.Y, point.Z), windVec[count+1])
    cone = rc.Geometry.Brep.CreateFromCone(rc.Geometry.Cone(conePlane, scaleFactor*-.5*(windVectorScale/1.75), scaleFactor*.15*(windVectorScale/1.75)), True)
    arrowMesh = rc.Geometry.Mesh()
    arrowMesh.Append(rc.Geometry.Mesh.CreateFromBrep(extrusion)[0])
    arrowMesh.Append(rc.Geometry.Mesh.CreateFromBrep(cone)[0])
    arrowMesh.VertexColors.CreateMonotoneMesh(colors[count])
    
    return arrowMesh

def createLineArrow(count, point, colors, windVec, heightsAboveGround, windDir, windVectorScale):
    meshTipPt = rc.Geometry.Point3d.Add(point, windVec[count+1])
    extruVec = rc.Geometry.Vector3d(windVec[count+1].X, windVec[count+1].Y, 0)
    extruVec.Unitize()
    extruVec = rc.Geometry.Vector3d.Multiply(scaleFactor*-1*(windVectorScale/1.75), extruVec)
    extruVec = rc.Geometry.Vector3d.Add(rc.Geometry.Vector3d(meshTipPt), extruVec)
    arrowStartPt = rc.Geometry.Point3d(extruVec)
    
    if windDir == []: mestPt1 = rc.Geometry.Point3d(meshTipPt.X-.75*(windVectorScale/1.75), meshTipPt.Y+.25*(windVectorScale/1.75), meshTipPt.Z)
    else: mestPt1 = rc.Geometry.Point3d(arrowStartPt.X, arrowStartPt.Y, arrowStartPt.Z+.25*(windVectorScale/1.75))
    if windDir == []: mestPt2 = rc.Geometry.Point3d(meshTipPt.X-.75*(windVectorScale/1.75), meshTipPt.Y-.25*(windVectorScale/1.75), meshTipPt.Z)
    else: mestPt2 = rc.Geometry.Point3d(arrowStartPt.X, arrowStartPt.Y, arrowStartPt.Z-.25*(windVectorScale/1.75))
    mesh = rc.Geometry.Mesh()
    mesh.Vertices.Add(meshTipPt)
    mesh.Vertices.Add(mestPt1)
    mesh.Vertices.Add(mestPt2)
    mesh.Faces.AddFace(0,1,2)
    mesh.VertexColors.CreateMonotoneMesh(colors[count])
    if windDir == []: arrowLine = rc.Geometry.Line(point, rc.Geometry.Point3d(meshTipPt.X-.75*(windVectorScale/1.75), meshTipPt.Y, meshTipPt.Z))
    else: arrowLine = rc.Geometry.Line(point, arrowStartPt)
    
    return arrowLine, mesh

def createChartAxes(heightsAboveGround, windVectorScale, scaleFactor, windVec, windDir, maxSpeed):
    #Create lists to be filled.
    axesLines = []
    axesArrows = []
    xAxisPts = []
    yAxisPts = []
    xAxisText = []
    yAxisText = []
    origin = rc.Geometry.Point3d.Origin
    
    #Define variables that get used in all functions.
    addDist = (heightsAboveGround[1]-heightsAboveGround[0])*2
    
    if windDir != []:
        #Create the X Axis
        if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0:
            endPtX = rc.Geometry.Point3d(windVectorScale*6, 0, 0)
            xAxis = rc.Geometry.LineCurve(origin, endPtX)
            axesLines.append(xAxis)
        else:
            maxX = rc.Geometry.Vector3d(windVec[-1].X, windVec[-1].Y, 0)
            maxX.Unitize()
            endPtX = rc.Geometry.Vector3d.Multiply(maxSpeed*windVectorScale, maxX)
            endPtX = rc.Geometry.Point3d(endPtX)
            xAxis = rc.Geometry.LineCurve(origin, endPtX)
            axesLines.append(xAxis)
        
        #Create the Y Axis
        endPtY = rc.Geometry.Point3d(0,0, heightsAboveGround[-1]*1.05)
        yAxis = rc.Geometry.LineCurve(origin, endPtY)
        axesLines.append(yAxis)
        
        #Divide up the X Axis.
        if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: divisionParams = xAxis.DivideByCount(6, False)
        else: divisionParams = xAxis.DivideByCount(maxSpeed, False)
        for param in divisionParams:
            xAxisPts.append(xAxis.PointAt(param))
        
        #Create the X Axis markers.
        for count, point in enumerate(xAxisPts):
            otherPt = rc.Geometry.Point3d(point.X, point.Y, -((windVectorScale/1.75))/2)
            lineMarker = rc.Geometry.LineCurve(point, otherPt)
            axesLines.append(lineMarker)
            xAxisText.append(str(count+1))
        
        #Divide up the Y Axis.
        divisionParams = yAxis.DivideByLength(addDist, True)
        heightAboveGrnd = 0
        for param in divisionParams:
            yAxisText.append(str(round(heightAboveGrnd, 1)))
            yAxisPts.append(yAxis.PointAt(param))
            heightAboveGrnd += addDist
        
        #Create Y Axis markers.
        if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: vecForMarker = rc.Geometry.Vector3d(1,0,0)
        else: vecForMarker = rc.Geometry.Vector3d(windVec[-1])
        vecForMarker.Unitize()
        vecForMarker.Reverse()
        for point in yAxisPts:
            otherPt = rc.Geometry.Point3d(vecForMarker.X, vecForMarker.Y, point.Z)
            lineMarker = rc.Geometry.LineCurve(point, otherPt)
            axesLines.append(lineMarker)
        
        #Create the X Axis arrows.
        vecForMarker.Reverse()
        vecForMarker = rc.Geometry.Vector3d.Multiply((windVectorScale/1.75), vecForMarker)
        meshTipPt = rc.Geometry.Point3d.Add(endPtX, vecForMarker)
        
        arrowStartPt = endPtX
        mestPt1 = rc.Geometry.Point3d(arrowStartPt.X, arrowStartPt.Y, arrowStartPt.Z+.3*(windVectorScale/1.75))
        mestPt2 = rc.Geometry.Point3d(arrowStartPt.X, arrowStartPt.Y, arrowStartPt.Z-.3*(windVectorScale/1.75))
        mesh = rc.Geometry.Mesh()
        mesh.Vertices.Add(meshTipPt)
        mesh.Vertices.Add(mestPt1)
        mesh.Vertices.Add(mestPt2)
        mesh.Faces.AddFace(0,1,2)
        mesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
        axesArrows.append(mesh)
        
        #Create the Y Axis arrows.
        vecForOffset = rc.Geometry.Vector3d.Multiply(0.2, vecForMarker)
        meshTipPt = rc.Geometry.Point3d(0,0,endPtY.Z+(windVectorScale/1.75))
        
        arrowStartPt = endPtY
        mestPt1 = rc.Geometry.Point3d(vecForOffset.X, vecForOffset.Y, arrowStartPt.Z)
        vecForOffset.Reverse()
        mestPt2 = rc.Geometry.Point3d(vecForOffset.X, vecForOffset.Y, arrowStartPt.Z)
        mesh = rc.Geometry.Mesh()
        mesh.Vertices.Add(meshTipPt)
        mesh.Vertices.Add(mestPt1)
        mesh.Vertices.Add(mestPt2)
        mesh.Faces.AddFace(0,1,2)
        mesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
        axesArrows.append(mesh)
    else:
        #Create the X Axis
        endPtX = rc.Geometry.Point3d(maxSpeed*windVectorScale,0,0)
        xAxis = rc.Geometry.LineCurve(origin, endPtX)
        axesLines.append(xAxis)
        
        #Create the Y Axis
        endPtY = rc.Geometry.Point3d(0,heightsAboveGround[-1]*1.05, 0)
        yAxis = rc.Geometry.LineCurve(origin, endPtY)
        axesLines.append(yAxis)
        
        #Divide up the X Axis.
        divisionParams = xAxis.DivideByCount(maxSpeed, False)
        for param in divisionParams:
            xAxisPts.append(xAxis.PointAt(param))
        
        #Create the X Axis markers.
        for count, point in enumerate(xAxisPts):
            otherPt = rc.Geometry.Point3d(point.X, -((windVectorScale/1.75))/2, 0)
            lineMarker = rc.Geometry.LineCurve(point, otherPt)
            axesLines.append(lineMarker)
            xAxisText.append(str(count+1))
        
        #Divide up the Y Axis.
        divisionParams = yAxis.DivideByLength(addDist, True)
        heightAboveGrnd = 0
        for param in divisionParams:
            yAxisText.append(str(round(heightAboveGrnd, 1)))
            yAxisPts.append(yAxis.PointAt(param))
            heightAboveGrnd += addDist
        
        #Create Y Axis markers.
        for point in yAxisPts:
            otherPt = rc.Geometry.Point3d(-(windVectorScale/1.75)/2, point.Y, 0)
            lineMarker = rc.Geometry.LineCurve(point, otherPt)
            axesLines.append(lineMarker)
        
        #Create the X Axis arrows.
        meshTipPt = rc.Geometry.Point3d(endPtX.X+(windVectorScale/1.75), 0, 0)
        arrowStartPt = endPtX
        mestPt1 = rc.Geometry.Point3d(arrowStartPt.X, .3*(windVectorScale/1.75), 0)
        mestPt2 = rc.Geometry.Point3d(arrowStartPt.X, -.3*(windVectorScale/1.75), 0)
        mesh = rc.Geometry.Mesh()
        mesh.Vertices.Add(meshTipPt)
        mesh.Vertices.Add(mestPt1)
        mesh.Vertices.Add(mestPt2)
        mesh.Faces.AddFace(0,1,2)
        mesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
        axesArrows.append(mesh)
        
        #Create the Y Axis arrows.
        meshTipPt = rc.Geometry.Point3d(0, endPtY.Y+(windVectorScale/1.75), 0)
        arrowStartPt = endPtY
        mestPt1 = rc.Geometry.Point3d(.3*(windVectorScale/1.75), arrowStartPt.Y, 0)
        mestPt2 = rc.Geometry.Point3d(-.3*(windVectorScale/1.75), arrowStartPt.Y, 0)
        mesh = rc.Geometry.Mesh()
        mesh.Vertices.Add(meshTipPt)
        mesh.Vertices.Add(mestPt1)
        mesh.Vertices.Add(mestPt2)
        mesh.Faces.AddFace(0,1,2)
        mesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
        axesArrows.append(mesh)
    
    return axesLines, axesArrows, xAxisPts, yAxisPts, xAxisText, yAxisText

def makeChartText(xAxisPts, yAxisPts, xAxisText, yAxisText, scaleFactor, windDir, windVec, legendFont, legendFontSize, legendBold, lb_visualization):
    #Create the lists to be filled.
    axesText = []
    allText = []
    allTextPt = []
    
    #Figure out the x-axis base pts.
    xValuesOrigins = []
    for point in xAxisPts:
        if windDir == []:
            xValuesOrigins.append(rc.Geometry.Point3d(point.X, point.Y-(((windVectorScale/1.75))/2)-legendFontSize, 0))
        else:
            xValuesOrigins.append(rc.Geometry.Point3d(point.X, point.Y, point.Z-(((windVectorScale/1.75))/2)-legendFontSize))
    
    #Create the X-Axis Text.
    if windDir == []: xValuesTextMeshes = lb_visualization.text2srf(xAxisText, xValuesOrigins, legendFont, legendFontSize*.75, legendBold, None, 4)
    else:
        if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: rotatedWindVec = rc.Geometry.Vector3d(1,0,0)
        else: rotatedWindVec = rc.Geometry.Vector3d(windVec[-1])
        xValuesTextMeshes = []
        for count, point in enumerate(xValuesOrigins):
            textPlane = rc.Geometry.Plane(point, rotatedWindVec, rc.Geometry.Vector3d.ZAxis)
            xValuesTextMeshes.extend(lb_visualization.text2srf(xAxisText[count], point, legendFont, legendFontSize*.75, legendBold, textPlane, 4))
    allText.extend(xAxisText)
    allTextPt.extend(xValuesOrigins)
    
    for meshTxt in xValuesTextMeshes:
        axesText.extend(meshTxt)
    
    #Figure out the y-axis base pts.
    yValuesOrigins = []
    for point in yAxisPts:
        if windDir == []:
            yValuesOrigins.append(rc.Geometry.Point3d(point.X-(1.5*legendFontSize), point.Y, 0))
        else:
            if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: textWindVec = rc.Geometry.Vector3d(-1,0,0)
            else:
                textWindVec = rc.Geometry.Vector3d(windVec[-1])
                textWindVec.Unitize()
                textWindVec.Reverse()
            textWindVec = rc.Geometry.Vector3d.Multiply(textWindVec, 3.5*legendFontSize)
            yValuesOrigins.append(rc.Geometry.Point3d(point.X+textWindVec.X, point.Y+textWindVec.Y, point.Z-((legendFontSize*.1))))
    
    #Create the Y-Axis Text.
    if windDir == []:
        yValuesTextMeshes = lb_visualization.text2srf(yAxisText, yValuesOrigins, legendFont, legendFontSize*.75, legendBold, None, 2)
    else:
        if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: rotatedWindVec = rc.Geometry.Vector3d(1,0,0)
        else: rotatedWindVec = rc.Geometry.Vector3d(windVec[-1])
        yValuesTextMeshes = []
        for count, point in enumerate(yValuesOrigins):
            
            charCount = 0
            for character in list(yAxisText[count]):
                if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: moveVec = rc.Geometry.Vector3d(1,0,0)
                else:
                    moveVec = rc.Geometry.Vector3d(windVec[-1])
                    moveVec.Unitize()
                if character != ".": moveVec = rc.Geometry.Vector3d.Multiply(charCount*legendFontSize*.6, moveVec)
                else: moveVec = rc.Geometry.Vector3d.Multiply((charCount-0.4)*legendFontSize*.6, moveVec)
                newPoint = rc.Geometry.Point3d.Add(point, moveVec)
                textPlane = rc.Geometry.Plane(newPoint, rotatedWindVec, rc.Geometry.Vector3d.ZAxis)
                yValuesTextMeshes.extend(lb_visualization.text2srf(character, newPoint, legendFont, legendFontSize*.75, legendBold, textPlane, 2))
                charCount += 1
    allText.extend(yAxisText)
    allTextPt.extend(yValuesOrigins)
    
    for meshTxt in yValuesTextMeshes:
        axesText.extend(meshTxt)
    
    
    return axesText, allText, allTextPt

def makeUnitsText(heightsAboveGround, maxSpeed, scaleFactor, windDir, windVec, windVectorScale, axesLines, epwStr, terrainType, analysisPeriod, titleStatement, legendFont, legendFontSize, legendBold, lb_visualization, lb_preparation):
    unitsTextLabels = []
    untisTxt = []
    unitsTxtPts = []
    
    #Find the point and text for the X-Axis Label.
    xAxisLabelText = "Wind Speed (m/s)"
    if windDir == []:
        axesBasePt = rc.Geometry.Point3d(((maxSpeed*windVectorScale)/2), -(windVectorScale/3)-(legendFontSize*2.5), 0)
    else:
        lineMidPt = axesLines[0].PointAt(axesLines[0].DivideByCount(2, True)[1])
        axesBasePt = rc.Geometry.Point3d(lineMidPt.X, lineMidPt.Y, -(windVectorScale/3)-(legendFontSize*2.5))
    
    #Create the X-Axis label.
    xAxisTextLabelMesh = lb_visualization.text2srf([xAxisLabelText], [axesBasePt], legendFont, legendFontSize, legendBold, None, 4)
    untisTxt.append(xAxisLabelText)
    unitsTxtPts.append(axesBasePt)
    
    #If the profile has been oriented to a cardinal direction, re-orient the text label.
    if windDir != []:
        if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: rotatedWindVec = rc.Geometry.Vector3d(1,0,0)
        else: rotatedWindVec = rc.Geometry.Vector3d(windVec[-1])
        originalPlane =  rc.Geometry.Plane(axesBasePt, rc.Geometry.Vector3d.ZAxis)
        newPlane = rc.Geometry.Plane(axesBasePt, rotatedWindVec, rc.Geometry.Vector3d.ZAxis)
        reOrient = rc.Geometry.Transform.PlaneToPlane(originalPlane, newPlane)
        for geoList in xAxisTextLabelMesh:
            for geo in geoList:
                geo.Transform(reOrient)
    
    #Find the point and text for the Y-Axis Label.
    yAxisLabelText = "Height (" + str(sc.doc.ModelUnitSystem) + ")"
    lineMidPt = axesLines[1].PointAt(axesLines[1].DivideByCount(2, True)[1])
    if windDir == []:
        axesBasePt = rc.Geometry.Point3d(lineMidPt.X-(windVectorScale/2)-(legendFontSize*5), lineMidPt.Y, lineMidPt.Z)
    else:
        if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: moveVec = rc.Geometry.Vector3d(-1,0,0)
        else:
            moveVec = rc.Geometry.Vector3d(windVec[-1])
            moveVec.Reverse()
            moveVec.Unitize()
        moveVec = rc.Geometry.Vector3d.Multiply(moveVec, (windVectorScale/2)+(legendFontSize*3.5))
        axesBasePt = rc.Geometry.Point3d(lineMidPt.X+moveVec.X, lineMidPt.Y+moveVec.Y, lineMidPt.Z)
    
    #Create the Y-Axis label.
    yAxisTextLabelMesh = lb_visualization.text2srf([yAxisLabelText], [axesBasePt], legendFont, legendFontSize, legendBold, None, 4)
    untisTxt.append(yAxisLabelText)
    unitsTxtPts.append(axesBasePt)
    
    #Rotate the Y-Axis label.
    rotation = rc.Geometry.Transform.Rotation(rc.Geometry.Vector3d.XAxis, rc.Geometry.Vector3d.YAxis, axesBasePt)
    for geoList in yAxisTextLabelMesh:
        for geo in geoList:
            geo.Transform(rotation)
    
    #If the profile has been oriented to a cardinal direction, re-orient the text label.
    if windDir != []:
        if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: rotatedWindVec = rc.Geometry.Vector3d(1,0,0)
        else: rotatedWindVec = rc.Geometry.Vector3d(windVec[-1])
        originalPlane =  rc.Geometry.Plane(axesBasePt, rc.Geometry.Vector3d.ZAxis)
        newPlane = rc.Geometry.Plane(axesBasePt, rotatedWindVec, rc.Geometry.Vector3d.ZAxis)
        reOrient = rc.Geometry.Transform.PlaneToPlane(originalPlane, newPlane)
        for geoList in yAxisTextLabelMesh:
            for geo in geoList:
                geo.Transform(reOrient)
    
    #Make the title text.
    if windDir == []: velocityType = "Average Velocity In Time Period \n"
    else: velocityType = "Prevailing Wind Average Velocity \n"
    
    if epwStr != []:
        if HOY_ != None:
            date = lb_preparation.hour2Date(HOY_)
            titleText = "Wind Profile - Average Velocity at Hour" + epwStr[1] + " - " + terrainType + "\n" + str(date)
        else:
            stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, False)
            if titleStatement:
                titleText = "Wind Profile  - " + velocityType + epwStr[1] + " - " + terrainType+ \
                '\n'+lb_preparation.hour2Date(lb_preparation.date2Hour(stMonth, stDay, stHour)) + ' - ' + \
                lb_preparation.hour2Date(lb_preparation.date2Hour(endMonth, endDay, endHour)) + \
                '\n' + titleStatement
            else:
                titleText = "Wind Profile  - " + velocityType + epwStr[1] + " - " + terrainType + \
                '\n'+lb_preparation.hour2Date(lb_preparation.date2Hour(stMonth, stDay, stHour)) + ' - ' + \
                lb_preparation.hour2Date(lb_preparation.date2Hour(endMonth, endDay, endHour))
    else:
        titleText = "Wind Profile \n" + terrainType
    
    #Get the base point for the title.
    if windDir != []: titleBasePt = rc.Geometry.Point3d(0, 0, -(windVectorScale/2)-(legendFontSize*7))
    else: titleBasePt = rc.Geometry.Point3d(0, -(windVectorScale/2)-(legendFontSize*7), 0)
    
    #Create the Title label.
    titleLabelMesh = lb_visualization.text2srf([titleText], [titleBasePt], legendFont, legendFontSize*1.2, legendBold, None, 0)
    untisTxt.append(titleText)
    unitsTxtPts.append(titleBasePt)
    
    #If the profile has been oriented to a cardinal direction, re-orient the text label.
    if windDir != []:
        if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: rotatedWindVec = rc.Geometry.Vector3d(1,0,0)
        else: rotatedWindVec = rc.Geometry.Vector3d(windVec[-1])
        originalPlane =  rc.Geometry.Plane(titleBasePt, rc.Geometry.Vector3d.ZAxis)
        newPlane = rc.Geometry.Plane(titleBasePt, rotatedWindVec, rc.Geometry.Vector3d.ZAxis)
        reOrient = rc.Geometry.Transform.PlaneToPlane(originalPlane, newPlane)
        for geoList in titleLabelMesh:
            for geo in geoList:
                geo.Transform(reOrient)
    
    #Add the text to the full list of text.
    for meshTxt in xAxisTextLabelMesh:
        unitsTextLabels.extend(meshTxt)
    for meshTxt in yAxisTextLabelMesh:
        unitsTextLabels.extend(meshTxt)
    for meshTxt in titleLabelMesh:
        unitsTextLabels.extend(meshTxt)
    
    return unitsTextLabels, untisTxt, unitsTxtPts


def main(heightsAboveGround, analysisPeriod, d, a, rl, terrainType, epwTerr, metD, metA, metrl, windSpeed, windDir, epwData, epwStr, windArrowStyle, lb_preparation, lb_visualization, lb_wind, windVectorScale, scaleFactor):
    #Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar_, False)
    
    #Set lists to be filled.
    windDirHieghts = []
    
    #Define a maximum wind speed if none is provided in the legendPar.
    if highB == "max": maxSpeed = 10
    else: maxSpeed = int(highB)
    
    #Factor the units system into the scale.
    windVectorScale = windVectorScale*scaleFactor
    
    #If epw data is connected, get the data for the analysis period and strip the header off.
    HOYS = range(1,8761)
    if epwData == True and analysisPeriod != [(1, 1, 1), (12, 31, 24)] and HOY_ == None:
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
        hrWindDir = []
        hrWindSpd = []
        for count in HOYS:
            hrWindSpd.append(windSpeed[count-1])
            if windDir != []: hrWindDir.append(windDir[count-1])
    else:
        hrWindSpd = windSpeed
        hrWindDir = windDir
    
    #Check the conditional statement and apply it.
    if epwData == True:
        titleStatement = -1
        annualHourlyData = _windSpeed_tenMeters + annualHourlyData_
        if conditionalStatement_ and len(annualHourlyData)!=0 and annualHourlyData[0]!=None and HOY_ == None:
            print 'Checking conditional statements...'
            # send all data and statement to a function and return back
            # True, False Pattern and condition statement
            titleStatement, patternList = checkConditionalStatement(annualHourlyData, conditionalStatement_, analysisPeriod, HOYS)
            
            if titleStatement != -1 and True not in patternList:
                warning = 'No hour meets the conditional statement.' 
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            
            #Create new lists of wind speed and wind direction data.
            newHrWindSpd = []
            newHrWindDir = []
            for count, bool in enumerate(patternList):
                if bool == True:
                    newHrWindSpd.append(hrWindSpd[count])
                    if windDir != []: newHrWindDir.append(hrWindDir[count])
                else: pass
            hrWindSpd = newHrWindSpd
            hrWindDir = newHrWindDir
        else:
            titleStatement = False
    else:
        titleStatement = False
    
    #If the user has specified a HOY_, use this to select out values.
    if HOY_ != None:
        if windDir != []: avgHrWindDir = math.radians(-(windDir[HOY_-1]-180))
        avgHrWindSpd = windSpeed[HOY_-1]
    else: pass
    
    
    noHrMeetsStatement = False
    #Find the prevailing wind direction and corresponding speed.
    if HOY_ == None and windDir != [] and hrWindSpd != [] and hrWindDir != []:
        #Create lists to be filled
        compassDirs = []
        windDirections = []
        windSpeeds = []
        for i in range(16):
            windDirections.append([])
            windSpeeds.append([])
            compassDirs.append(i*22.5)
        
        #Organize all of the data based on 16 main cardinal directions.
        for dirCount, winDir in enumerate(hrWindDir):
            if hrWindSpd[dirCount] == 0.0: pass
            elif winDir < 11 or winDir > 349:
                windDirections[0].append(winDir)
                windSpeeds[0].append(hrWindSpd[dirCount])
            elif winDir < 34:
                windDirections[1].append(winDir)
                windSpeeds[1].append(hrWindSpd[dirCount])
            elif winDir < 56:
                windDirections[2].append(winDir)
                windSpeeds[2].append(hrWindSpd[dirCount])
            elif winDir < 79:
                windDirections[3].append(winDir)
                windSpeeds[3].append(hrWindSpd[dirCount])
            elif winDir < 101:
                windDirections[4].append(winDir)
                windSpeeds[4].append(hrWindSpd[dirCount])
            elif winDir < 124:
                windDirections[5].append(winDir)
                windSpeeds[5].append(hrWindSpd[dirCount])
            elif winDir < 146:
                windDirections[6].append(winDir)
                windSpeeds[6].append(hrWindSpd[dirCount])
            elif winDir < 169:
                windDirections[7].append(winDir)
                windSpeeds[7].append(hrWindSpd[dirCount])
            elif winDir < 191:
                windDirections[8].append(winDir)
                windSpeeds[8].append(hrWindSpd[dirCount])
            elif winDir < 214:
                windDirections[9].append(winDir)
                windSpeeds[9].append(hrWindSpd[dirCount])
            elif winDir < 236:
                windDirections[10].append(winDir)
                windSpeeds[10].append(hrWindSpd[dirCount])
            elif winDir < 259:
                windDirections[11].append(winDir)
                windSpeeds[11].append(hrWindSpd[dirCount])
            elif winDir < 281:
                windDirections[12].append(winDir)
                windSpeeds[12].append(hrWindSpd[dirCount])
            elif winDir < 304:
                windDirections[13].append(winDir)
                windSpeeds[13].append(hrWindSpd[dirCount])
            elif winDir < 326:
                windDirections[14].append(winDir)
                windSpeeds[14].append(hrWindSpd[dirCount])
            else:
                windDirections[15].append(winDir)
                windSpeeds[15].append(hrWindSpd[dirCount])
        
        # Create a list with the number of hours of each of the wind directions.
        windDirectionsNumHrs = []
        for directLis in windDirections:
            windDirectionsNumHrs.append(len(directLis))
        
        #Zip and sort all of the lists together.
        zipped = zip(windDirectionsNumHrs, windSpeeds, compassDirs)
        zipped.sort()
        
        #Get the final wind direction and wind speed.
        avgHrWindDir = math.radians(-(zipped[-1][2]-180))
        avgHrWindSpd = sum(zipped[-1][1])/len(zipped[-1][1])
    elif HOY_ == None and windDir == []:
        try:
            avgHrWindSpd = sum(hrWindSpd)/len(hrWindSpd)
        except:
            noHrMeetsStatement = True
    elif hrWindSpd == [] and hrWindDir == []:
        noHrMeetsStatement = True
    
    #Check if to be sure that there are hours that meet the conditional statement.
    if noHrMeetsStatement == True:
        return -1
    else:
        #Evaluate each height.
        windSpdHeight = []
        anchorPts = []
        for count, height in enumerate(heightsAboveGround):
            if powerOrLog_ == True or powerOrLog_ == None:
                windSpdHeight.append(lb_wind.powerLawWind(avgHrWindSpd, height/scaleFactor, d, a, metD, metA))
            else:
                windSpdHeight.append(lb_wind.logLawWind(avgHrWindSpd, height/scaleFactor, rl, metrl))
            if windDir != []: anchorPts.append(rc.Geometry.Point3d(0, 0, height))
            else: anchorPts.append(rc.Geometry.Point3d(0, height, 0))
       
       #Create vectors for each height.
        windVec = []
        for speed in windSpdHeight:
            if windDir != []:
                vec = rc.Geometry.Vector3d(0, speed*windVectorScale, 0)
                vec.Rotate(avgHrWindDir, rc.Geometry.Vector3d.ZAxis)
                windDirHieghts.append(avgHrWindDir)
            else:
                vec = rc.Geometry.Vector3d(speed*windVectorScale, 0, 0)
            windVec.append(vec)
        
        #If there is a north angle hooked up, rotate the vectors.
        if north_ != None and windDir != []:
            northAngle, northVector = lb_preparation.angle2north(north_)
            for vec in windVec:
                vec.Rotate(northAngle, rc.Geometry.Vector3d.ZAxis)
        else: pass
        
        #Create the wind profile curve.
        profilePts = []
        for count, point in enumerate(anchorPts):
            if windDir != []: profilePts.append(rc.Geometry.Point3d(windVec[count].X, windVec[count].Y, point.Z))
            else: profilePts.append(rc.Geometry.Point3d(windVec[count].X, point.Y, 0))
        if len(anchorPts) != 2:
            interpCrv = rc.Geometry.Curve.CreateInterpolatedCurve(profilePts[1:], 3)
            
            tanCrv = interpCrv.TangentAtStart
            tanCrv = rc.Geometry.Vector3d.Multiply(.33, tanCrv)
            startVec = rc.Geometry.Vector3d(windVec[-1].X, windVec[-1].Y, (tanCrv.Z))
            startVec.Unitize()
            
            if terrainType_ < 2:
                ptList = [rc.Geometry.Point3d.Origin, profilePts[1]]
            else:
                midPtHeight = (heightsAboveGround[1]-heightsAboveGround[0])/20
                if powerOrLog_ == True or powerOrLog_ == None:
                    midPtX = lb_wind.powerLawWind(avgHrWindSpd, midPtHeight, d, a, metD, metA)
                else: midPtX = lb_wind.logLawWind(avgHrWindSpd, midPtHeight, rl, metrl)
                if windDir == []:
                    midPt = rc.Geometry.Point3d(midPtX*windVectorScale, midPtHeight, 0)
                    ptList = [rc.Geometry.Point3d.Origin, midPt, profilePts[1]]
                else:
                    windDirVec = rc.Geometry.Vector3d(windVec[-1])
                    windDirVec.Unitize()
                    windDirVec = rc.Geometry.Vector3d.Multiply(midPtX*windVectorScale, windDirVec)
                    midPt = rc.Geometry.Point3d(windDirVec.X, windDirVec.Y, midPtHeight)
                    ptList = [rc.Geometry.Point3d.Origin, midPt, profilePts[1]]
            
            profileLine = rc.Geometry.Curve.CreateInterpolatedCurve(ptList, 3, rc.Geometry.CurveKnotStyle.Uniform, startVec, tanCrv)
            profileCrv = [rc.Geometry.Curve.JoinCurves([interpCrv, profileLine], sc.doc.ModelAbsoluteTolerance)[0]]
        else:
            profileCrv = rc.Geometry.Curve.CreateInterpolatedCurve(profilePts, 3)
        
        
        #If the user has requested arrows, then generate them
        if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0:
            windVecMesh = None
            colors = []
            values = windSpdHeight[1:]
        else:
            if windArrowStyle == 1 or windArrowStyle == 2 or windArrowStyle ==3:
                #Get colors for the and profile mesh.
                values = windSpdHeight[1:]
                colors = lb_visualization.gradientColor(windSpdHeight[1:], lowB, highB, customColors)
                
                #Create the wind profile mesh.
                windVecMesh = []
                #Create standard color 3D meshes.
                if windArrowStyle == 1:
                    arrowMesh = rc.Geometry.Mesh()
                    use1meterArrowHeadSize = True
                    for count, point in enumerate(anchorPts[1:]):
                        try:
                            mesh = createColoredArrowMesh(count, point, colors, windVec, heightsAboveGround, use1meterArrowHeadSize, scaleFactor)
                            arrowMesh.Append(mesh)
                        except: pass
                    windVecMesh.append(arrowMesh)
                #Create high-res colored 3D meshes
                elif windArrowStyle == 2:
                    arrowMesh = rc.Geometry.Mesh()
                    for count, point in enumerate(anchorPts[1:]):
                        try:
                            mesh = createHighResColoredArrows(count, point, colors, windVec, heightsAboveGround, windDir)
                            arrowMesh.Append(mesh)
                        except:pass
                    windVecMesh.append(arrowMesh)
                #Create line arrows (colored)
                elif windArrowStyle == 3:
                    for count, point in enumerate(anchorPts[1:]):
                        arrowLine, arrowMeshHead = createLineArrow(count, point, colors, windVec, heightsAboveGround, windDir, windVectorScale)
                        windVecMesh.extend([arrowLine, arrowMeshHead])
            #Create line arrows (black)
            elif windArrowStyle == 4:
                values = windSpdHeight[1:]
                windVecMesh = []
                colors = []
                for count, point in enumerate(anchorPts[1:]):
                    colors.append(System.Drawing.Color.Black)
                    arrowLine, arrowMeshHead = createLineArrow(count, point, colors, windVec, heightsAboveGround, windDir, windVectorScale)
                    windVecMesh.extend([arrowLine, arrowMeshHead])
            else:
                windVecMesh = None
                colors = []
                values = windSpdHeight[1:]
        
        #Plot the chart axes.
        profileAxes = []
        axesLines, axesArrows, xAxisPts, yAxisPts, xAxisText, yAxisText = createChartAxes(heightsAboveGround, windVectorScale, scaleFactor, windVec, windDir, maxSpeed)
        profileAxes.extend(axesLines)
        profileAxes.extend(axesArrows)
        
        #Calculate a bounding box around everything that will help place the legend and title.
        allGeo = []
        allGeo.append(profileCrv)
        allGeo.extend(profileAxes)
        lb_visualization.calculateBB(allGeo, True)
        
        legendScaleDeterminant = windVectorScale*maxSpeed+(scaleFactor*4)
        lb_visualization.BoundingBoxPar = (lb_visualization.BoundingBoxPar[0], lb_visualization.BoundingBoxPar[2], legendScaleDeterminant, lb_visualization.BoundingBoxPar[3], lb_visualization.BoundingBoxPar[4], lb_visualization.BoundingBoxPar[5], lb_visualization.BoundingBoxPar[6])
        
        #Create a color legend if wind arrow meshes have been generated.
        if windArrowStyle == 1 or windArrowStyle == 2 or windArrowStyle ==3:
            #Get the legend base point.
            legendSrfs, legendText, legendTextSrf, textPt, textSize = lb_visualization.createLegend(values, lowB, highB, numSeg, "m/s", lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
            # generate legend colors
            legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
            # color legend surfaces
            legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
            #Flaten the text list
            legend = lb_preparation.flattenList(legendTextSrf)
            legend.append(legendSrfs)
        else:
            BBYlength = lb_visualization.BoundingBoxPar[2]
            legendHeight = (BBYlength/10) * legendScale
            if  legendFontSize == None: textSize = (legendHeight/3) * legendScale
            else: textSize = legendFontSize
            legend = []
            legendBasePoint = None
        
        # If a wind direction is connected and a legend was produced, re-orient the legend to align with the previaling direction of the wind.
        keepLegendStatic = False
        if windDir != []:
            if windArrowStyle == 1 or windArrowStyle == 2 or windArrowStyle ==3:
                if windVec[-1].X == 0 and windVec[-1].Y == 0 and windVec[-1].Z == 0: rotatedWindVec = rc.Geometry.Vector3d(1,0,0)
                else: rotatedWindVec = rc.Geometry.Vector3d(windVec[-1])
                if legendBasePoint == None:
                    legendBasePoint = lb_visualization.BoundingBoxPar[0]
                    legendBasePointNew = axesLines[0].PointAtEnd
                else:
                    legendBasePointNew = legendBasePoint
                    keepLegendStatic = True
                originalPlane = rc.Geometry.Plane(legendBasePoint, rc.Geometry.Vector3d.ZAxis)
                newPlane = rc.Geometry.Plane(legendBasePointNew, rotatedWindVec, rc.Geometry.Vector3d.ZAxis)
                reOrientTrans = rc.Geometry.Transform.PlaneToPlane(originalPlane, newPlane)
                for geo in legend:
                    geo.Transform(reOrientTrans)
                legendBasePoint = legendBasePointNew
        
        if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
        elif windDir == []: keepLegendStatic = True
        
        # Create the axes text lables
        axesText, axesTextStr, axesTextPt = makeChartText(xAxisPts, yAxisPts, xAxisText, yAxisText, scaleFactor, windDir, windVec, legendFont, textSize, legendBold, lb_visualization)
   
        #i love rosi.
        #Create the units labels of the axes.
        unitsTextLabels, untisTxt, unitsTxtPts = makeUnitsText(heightsAboveGround, maxSpeed, scaleFactor, windDir, windVec, windVectorScale, axesLines, epwStr, terrainType, analysisPeriod, titleStatement, legendFont, textSize, legendBold, lb_visualization, lb_preparation)
        axesText.extend(unitsTextLabels)
        
        #If the user has specified a base point, use this to move everything.
        if originPt_ != None:
            transformMtx = rc.Geometry.Transform.Translation(originPt_.X, originPt_.Y, originPt_.Z)
            for geo in profileCrv: geo.Transform(transformMtx)
            if windVecMesh != None and windVecMesh != []:
                for geo in windVecMesh:
                    geo.Transform(transformMtx)
            if keepLegendStatic == False:
                if legendBasePoint != None: legendBasePoint.Transform(transformMtx)
                if legend != []:
                    for geo in legend:
                        if geo != -1: geo.Transform(transformMtx)
            for geo in anchorPts:
                geo.Transform(transformMtx)
            for geo in profileAxes:
                geo.Transform(transformMtx)
            for geo in axesTextPt:
                geo.Transform(transformMtx)
            for geo in axesText:
                geo.Transform(transformMtx)
            for geo in unitsTxtPts:
                geo.Transform(transformMtx)
            for geo in unitsTextLabels:
                geo.Transform(transformMtx)
            for geo in textPt:
                geo.Transform(transformMtx)

        # If bakeIt is set to true, then bake all of the geometry.
        if bakeIt_ > 0:
            #Group all of the curves together.
            finalCrvs = []
            for crv in profileAxes:
                try:
                    testPt = crv.PointAtEnd
                    finalCrvs.append(crv)
                except: pass
            finalCrvs.extend(profileCrv)
            #Make a joined mesh.
            try:
                finalMesh = rc.Geometry.Mesh()
                for mesh in windVecMesh:
                    try: finalMesh.Append(mesh)
                    except: finalCrvs.append(rc.Geometry.LineCurve(mesh))
            except: finalMesh = None
            #Adding axes arrows to the final mesh
            for arrow in axesArrows:
                finalMesh.Append(arrow)
            #Group all of the Text together.
            allText = []
            allTextPt = []
            allText.extend(axesTextStr)
            allTextPt.extend(axesTextPt)
            allText.extend(untisTxt)
            allTextPt.extend(unitsTxtPts)
            try:
                allText.extend(legendText)
                allTextPt.extend(textPt)
            except: legendSrfs = None
            # check the study type
            try:
                if 'Wind Speed' in _windSpeed_tenMeters[2]: placeName = _windSpeed_tenMeters[1]
                elif 'Wind Direction' in windDirection_[2]: placeName = windDirection_[1]
                else: placeName = 'alternateLayerName'
            except: placeName = 'alternateLayerName'
            studyLayerName = 'WIND_BOUNDARY_PROFILE'
            dataType = 'Wind Boundary Profile'
            newLayerIndex, l = lb_visualization.setupLayers(dataType, 'LADYBUG', placeName, studyLayerName)
            if bakeIt_ == 1: lb_visualization.bakeObjects(newLayerIndex, finalMesh, legendSrfs, allText, allTextPt, textSize,  legendFont, finalCrvs, decimalPlaces, True)
            else: lb_visualization.bakeObjects(newLayerIndex, finalMesh, legendSrfs, allText, allTextPt, textSize,  legendFont, finalCrvs, decimalPlaces, False)
        
        
        return profileCrv, windVecMesh, windSpdHeight, windDirHieghts, windVec, anchorPts, profileAxes, axesText, legend, legendBasePoint


#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)

#Check the inputs.
checkData = False
if initCheck == True:
    check = checkTheInputs()
    checkData, heightsAboveGround, analysisPeriod, d, a, rl, terrainType, epwTerr, metD, metA, metrl, \
    windSpeed, windDir, epwData, epwStr, windArrowStyle, lb_preparation, lb_visualization, \
    lb_wind, windVectorScale, scaleFactor = check
    
    #Get the wind profile curve if everything looks good.
    if checkData == True:
        result = main(heightsAboveGround, analysisPeriod, d, a, rl, terrainType, epwTerr, metD, metA, metrl, windSpeed, windDir, epwData, epwStr, windArrowStyle, lb_preparation, lb_visualization, lb_wind, windVectorScale, scaleFactor)
        if result != -1:
            windProfileCurve, windVectorMesh, windSpeeds, windDirections, windVectors, vectorAnchorPts, profileAxes, axesText, legend, legendBasePt = result

#Hide the anchor points.
ghenv.Component.Params.Output[4].Hidden = True
ghenv.Component.Params.Output[11].Hidden = True