# Wind Profile Curve Visualizer
# By Chris Mackey and Djordje Spasic
# Chris@MackeyArchitecture.com and issworld2000@yahoo.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to visualize a wind profile curve for a given terrain type.  Wind speed increases as one leaves the ground and wind profiles are a means of visualizing this change in wind speed with height.
-
More information on the power law of the wind profile can be found here: http://en.wikipedia.org/wiki/Wind_profile_power_law
-
Provided by Ladybug 0.0.58
    
    Args:
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _windSpeed_tenMeters: The wind speed from the import EPW component or a number representing the wind speed at 10 meters off the ground in agricultural or airport terrian.  This input also accepts lists of numbers representing different speeds at 10 meters.
        _windDirection: The wind direction from the import EPW component or a number in degrees represeting the wind direction from north,  This input also accepts lists of numbers representing different directions.
        _terrainType: An interger from 0 to 3 that sets the terrain class associated with the output windSpeedAtHeight. Interger values represent the following terrain classes:
            0 = Urban: large city centres, 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = Suburban: suburbs, wooded areas.
            2 = Country: open, with scattered objects generally less than 10m high.
            3 = Water: Flat, unobstructed areas exposed to wind flowing over a large water body (no more than 500m inland).
        epwTerrain_: An optional interger from 0 to 3 that sets the terrain class associated with the output windSpeedAtHeight. The default is set to 2 for flat clear land, which is typical for most EPW files that are recorded at airports.  Interger values represent the following terrain classes:
            0 = Urban: large city centres, 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = Suburban: suburbs, wooded areas.
            2 = Country: open, with scattered objects generally less than 10m high.
            3 = Water: Flat, unobstructed areas exposed to wind flowing over a large water body (no more than 500m inland).
        -------------------------: ...
        HOY_ : Use this input to select out specific indices of a list of values connected for wind speed and wind direction.  If you have connected hourly EPW data, this is the equivalent of a "HOY" input and you can use the "Ladybug_DOY_HOY" component to select out a specific hour and date.  Note that this overrides the analysisPeriod_ input below.
        analysisPeriod_: If you have connected data from an EPW component, plug in an analysis period from the Ladybug_Analysis Period component to calculate data for just a portion of the year. The default is Jan 1st 00:00 - Dec 31st 24:00, the entire year.
        annualHourlyData_: An optional list of hourly data from the Import epw component, which will be overlaid on wind rose (e.g. dryBulbTemperature)
        conditionalStatement_: This input allows users to remove data that does not fit specific conditions or criteria from the wind rose. To use this input correctly, hourly data, such as temperature or humidity, must be plugged into the annualHourlyData_ input. The conditional statement input here should be a valid condition statement in Python, such as "a>25" or "b<80" (without quotation marks).
                              The current version of this component accepts "and" and "or" operators. To visualize the hourly data, only lowercase English letters should be used as variables, and each letter alphabetically corresponds to each of the lists (in their respective order): "a" always represents the 1st list, "b" always represents the 2nd list, etc.
                              For example, if you have hourly dry bulb temperature connected as the first list, and relative humidity connected as the second list (both to the annualHourlyData_ input), and you want to plot the data for the time period when temperature is between 18C and 23C, and humidity is less than 80%, the conditional statement should be written as 18<a<23 and b<80 (without quotation marks).
                              For the windRose component, the variable "a" always represents windSpeed.
        averageData_: Set to "True" to average all of the wind data that you have connected into a single wind profile curve. Set to False to return a list of wind profile curves for all connected data or hours within the analysis period.  The default is set to "True" as many wind profile curves can easily become unmanagable.
        -------------------------: ...
        groundBasePt_: An optional point that can be used to change the base point at shich the wind profile curves are generated.  By default, the wond profile curves generate at the Rhino model origin.
        windVectorScale_: An optional number that can be used to change the scale of the wind vectors in relation to the height of the wind profile curve.  The default is set to 2 so that it is easier to see how the wind speed is changing with height.
        windProfileHeight_: An optional number in Rhino model units that can be used to change the height of the wind profile curve.  By default, the height of the curve is set to 20 meters (or the equivalent distance in your Rhino model units).  You may want to move this number higher or lower depending on the wind effects that you are interested in.
        distBetweenVec_: An optional number in rhino model units that represents the distance between wind vectors in the profile curve.  The default is set to 2 meters (or the equivalent distance in your Rhino model units).
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
    Returns:
        readMe!: ...
        --------------------: ...
        windSpeedAtHeight: The wind speeds that correspond to the wind vectors in the wind profile visualization.
        windVectors: The wind vectors that correspond to those in the wind profile visualization.  Note that the magnitude of these vectors will be scaled based on the windVectorScale_ input.
        vectorAnchorPts: Anchor points for each of the vectors above, which correspond to the height above the ground for each of the vectors.  Connect this along with the output above to a Grasshopper "Vector Display" component to see the vectors as a grasshopper vector display (as opposed to the vector mesh below).
        --------------------: ...
        windVectorMesh: A mesh displaying the wind vectors that were used to make the profile curve.
        windProfileCurve: A curve outlining the wind speed as it changes with height.  This may also be a list of wind profile curves if multiple "HOY_" inputs are connected or "averageData_" is set to False."
        legend: A legend of the wind profile curves. Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the Rhino scene.  
        legendBasePt: The legend base point(s), which can be used to move the legend in relation to the wind profile with the grasshopper "move" component.
"""
ghenv.Component.Name = "Ladybug_Wind Profile Curve Visualizer"
ghenv.Component.NickName = 'WindProfileCurve'
ghenv.Component.Message = 'VER 0.0.58\nDEC_05_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.58\nDEC_02_2014
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


windSpeeds = DataTree[Object]()
windVectors = DataTree[Object]()
vectorAnchorPts = DataTree[Object]()


def checkTheInputs():
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
        
        #Check lenth of the _windDirection list and evaluate the contents.
        checkData2 = False
        windDir = []
        dirMultVal = False
        nonPositive = True
        if len(_windDirection) != 0:
            try:
                if _windDirection[2] == 'Wind Direction':
                    windDir = _windDirection[7:]
                    checkData2 = True
                    epwData = True
                    epwStr = _windDirection[0:7]
            except: pass
            if checkData2 == False:
                for item in _windDirection:
                    try:
                        if float(item) >= 0:
                            windDir.append(float(item))
                            checkData2 = True
                        else: nonPositive = False
                    except: checkData2 = False
            if nonPositive == False: checkData2 = False
            if len(windDir) > 1: dirMultVal = True
            if checkData2 == False:
                warning = '_windDirection input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData2 = False
            print "Connect wind direction."
        
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
                    if dirMultVal == False: windDir = duplicateData(windDir, calcLength)
                    
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
        if HOY_ == []: pass
        else:
            for item in HOY_:
                if item > calcLength or item < 1:
                    checkData7 = False
                    warning = 'You cannot input a HOY_ that is less than 1 or greater than the length of values in the _windSpeed or _windDirection lists.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                else: pass
        
        # Evaluate the terrain type to get the right roughness length.
        if _terrainType != None:
            checkData3, d, a = lb_wind.readTerrainType(_terrainType)
            if checkData3 == True: pass
            else:
                print "Please choose one of three terrain types: 0=city, 1=urban, 2=country 3=water"
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Please choose one of three terrain types: 0=city, 1=urban, 2=country 3=water")
        else:
            d = None
            a = None
            print "Connect a value for terrain type."
            checkData3 = False
        
        #Calaculate the heights above the ground to make the vectors from input profile ehight and distance between vectors.
        checkData4 = True
        heightsAboveGround = []
        scaleFactor = lb_preparation.checkUnits()
        conversionFactor = 1/(scaleFactor)
        
        if windProfileHeight_ == None:
            windProfileHeight = 20*conversionFactor
            print "Wind profile height set to " + str(windProfileHeight) + " " + str(sc.doc.ModelUnitSystem)
        else:
            if windProfileHeight_ < 0:
                windProfileHeight = 0
                checkData4 = False
                print "The input windProfileHeight_ cannot be less than 0."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "The input windProfileHeight_ cannot be less than 0.")
            else:
                windProfileHeight = windProfileHeight_
                print "Wind profile height set to " + str(windProfileHeight) + " " + str(sc.doc.ModelUnitSystem)
        
        if distBetweenVec_ == None:
            distBetweenVec = 2*conversionFactor
            print "Wind vector distance set to " + str(distBetweenVec) + " " + str(sc.doc.ModelUnitSystem)
        else:
            distBetweenVec = distBetweenVec_
            print "Wind vector distance set to " + str(windProfileHeight) + " " + str(sc.doc.ModelUnitSystem)
        
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
            windVectorScale = 2
        else:
            if windVectorScale_ < 0:
                windVectorScale = 0
                checkData6 = False
                print "The input windVectorScale_ cannot be less than 0."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "The input windVectorScale_ cannot be less than 0.")
            else:
                windVectorScale = windVectorScale_
        
        # Set a defult epwTerrain if none is connected.
        checkData8 = True
        if epwTerrain_ != None:
            if epwTerrain_ <=3 and epwTerrain_ >= 0: epwTerrain = epwTerrain_
            else:
                epwTerrain = None
                checkData8 = False
                print "You have not connected a correct epwTerrain_ type."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "You have not connected a correct epwTerrain_ type.")
        else:
            epwTerrain = 2
            print "epwTerrain_ has been set to 2 for flat clear land, which is typical for most EPW files that are recorded at airports."
        
        #Set the default to averageData_.
        if averageData_ == None:
            averageData = True
        else:
            averageData = averageData_
        
        if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True:
            checkData = True
        else:
            checkData = False
        
        return checkData, heightsAboveGround, analysisPeriod, d, a, epwTerrain, averageData, windSpeed, windDir, epwData, epwStr, lb_preparation, lb_visualization, lb_wind, windVectorScale, conversionFactor
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return False, None, None, None, None, None, None, None, None, None, None,  None, None



def checkConditionalStatement(annualHourlyData, conditionalStatement):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        indexList, listInfo = lb_preparation.separateList(annualHourlyData, lb_preparation.strToBeFound)
        
        letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
        # remove 'and' and 'or' from conditional statements
        csCleaned = conditionalStatement.replace('and', '',20000)
        csCleaned = csCleaned.replace('or', '',20000)
        
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
                warning = 'At least one of the input data lists is not a valis ladybug hourly data! Please fix this issue and try again!\n List number = '+ `i+1`
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
        
        # check for the pattern
        patternList = []
        try:
            for HOY in range(8760):
                exec(finalStatement)
                patternList.append(pattern)
        except Exception,e:
            warning = 'There is an error in the conditional statement:\n' + `e`
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1, -1
        
        return titleStatement, patternList


def main(heightsAboveGround, analysisPeriod, d, a, epwTerrain, averageData, windSpeed, windDir, epwData, epwStr, lb_preparation, lb_visualization, lb_wind, windVectorScale, scaleFactor):
    #Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar_, False)
    
    #Read the coefficients of the epwTerrain.
    checkData, metD, metA = lb_wind.readTerrainType(epwTerrain)
    
    #If epw data is connected, get the data for the analysis period and strip the header off.
    if epwData == True and analysisPeriod != [(1, 1, 1), (12, 31, 24)] and HOY_ == []:
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
        hrWindDir = []
        hrWindSpd = []
        for count in HOYS:
            hrWindSpd.append(windSpeed[count])
            hrWindDir.append(windDir[count])
    else:
        hrWindSpd = windSpeed
        hrWindDir = windDir
    
    #Check the conditional statement and apply it.
    if epwData == True:
        titleStatement = -1
        annualHourlyData = _windSpeed_tenMeters + annualHourlyData_
        if conditionalStatement_ and len(annualHourlyData)!=0 and annualHourlyData[0]!=None:
            print 'Checking conditional statements...'
            # send all data and statement to a function and return back
            # True, False Pattern and condition statement
            titleStatement, patternList = checkConditionalStatement(annualHourlyData, conditionalStatement_)
        
        if titleStatement != -1 and True not in patternList:
            warning = 'No hour meets the conditional statement.' 
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        if titleStatement == -1:
            patternList = [True] * 8760
            titleStatement = False
        patternListFinal = []
        if epwData == True and analysisPeriod != [(1, 1, 1), (12, 31, 24)] and HOY_ == []:
            for count in HOYS:
                patternListFinal.append(patternList[count])
        else: patternListFinal = patternList
        
        newHrWindDir = []
        newHrWindSpd = []
        for count, bool in enumerate(patternListFinal):
            if bool == True:
                newHrWindSpd.append(hrWindSpd[count])
                newHrWindDir.append(hrWindDir[count])
            else: pass
        hrWindSpd = newHrWindSpd
        hrWindDir = newHrWindDir
    
    #If the user has specified a HOY_, use this to select out values.
    if HOY_ != []:
        hrWindDir = []
        hrWindSpd = []
        for num in HOY_:
            hrWindDir.append(windDir[num-1])
            hrWindSpd.append(windSpeed[num-1])
    else: pass
    
    
    if averageData == True:
        #Avergage the data.
        avgHrWindSpd = sum(hrWindSpd)/len(hrWindSpd)
        
        avgHrWindDirDeg = sum(hrWindDir)/len(hrWindDir)
        avgHrWindDir = 0.0174532925*avgHrWindDirDeg
        
        #Evaluate each height.
        windSpdHeight = [[]]
        anchorPts = [[]]
        for count, height in enumerate(heightsAboveGround):
            windSpdHeight[0].append(lb_wind.calcWindSpeedBasedOnHeight(avgHrWindSpd, height, d, a, metD, metA))
            anchorPts[0].append(rc.Geometry.Point3d(0, 0, height))
       
       #Create vectors for each height.
        windVec = [[]]
        for speed in windSpdHeight[0]:
            vec = rc.Geometry.Vector3d(0, speed*windVectorScale, 0)
            vec.Rotate(avgHrWindDir, rc.Geometry.Vector3d.ZAxis)
            windVec[0].append(vec)
        
        #If there is a north angle hooked up, rotate the vectors.
        if north_ != None:
            northAngle, northVector = lb_preparation.angle2north(north_)
            for vec in windVec[0]:
                vec.Rotate(northAngle, rc.Geometry.Vector3d.ZAxis)
        else: pass
        
        #Create the wind profile curve.
        profilePts = []
        for count, point in enumerate(anchorPts[0]):
            profilePts.append(rc.Geometry.Point3d(windVec[0][count].X, windVec[0][count].Y, point.Z))
        if len(anchorPts[0]) != 2:
            interpCrv = rc.Geometry.Curve.CreateInterpolatedCurve(profilePts[1:], 3)
            ptList = [rc.Geometry.Point3d.Origin, profilePts[1]]
            tanCrv = interpCrv.TangentAtStart
            tanCrv = rc.Geometry.Vector3d.Multiply(.33, tanCrv)
            startVec = rc.Geometry.Vector3d(windVec[0][1].X, windVec[0][1].Y, 0)
            startVec.Unitize()
            profileLine = rc.Geometry.Curve.CreateInterpolatedCurve(ptList, 3, rc.Geometry.CurveKnotStyle.Uniform, startVec, tanCrv)
            profileCrv = [rc.Geometry.Curve.JoinCurves([interpCrv, profileLine], sc.doc.ModelAbsoluteTolerance)[0]]
        else:
            profileCrv = rc.Geometry.Curve.CreateInterpolatedCurve(profilePts, 3)
        
        #Get colors for the und profile mesh.
        if legendPar_ == []:
            customColors = [System.Drawing.Color.FromArgb(200,200,255), System.Drawing.Color.FromArgb(175,175,255), System.Drawing.Color.FromArgb(150,150,255), System.Drawing.Color.FromArgb(125,125,255), System.Drawing.Color.FromArgb(100,100,255), System.Drawing.Color.FromArgb(75,75,255), System.Drawing.Color.FromArgb(50,50,255)]
        values = windSpdHeight[0][1:]
        #values.sort()
        #lowB = values[0]
        #highB = values[-1]
        colors = lb_visualization.gradientColor(windSpdHeight[0][1:], lowB, highB, customColors)
        
        #Create the wind profile mesh.
        totalMesh = rc.Geometry.Mesh()
        for count, point in enumerate(anchorPts[0][1:]):
            try:
                circle = rc.Geometry.Circle(rc.Geometry.Plane(point, windVec[0][count+1]), scaleFactor*0.05).ToNurbsCurve()
                extruVec = rc.Geometry.Vector3d(windVec[0][count+1].X, windVec[0][count+1].Y, 0)
                extruVec.Unitize()
                extruVec = rc.Geometry.Vector3d.Multiply(scaleFactor*-.5, extruVec)
                extruVec = rc.Geometry.Vector3d.Add(windVec[0][count+1], extruVec)
                extrusion = rc.Geometry.Brep.CreateFromSurface(rc.Geometry.Surface.CreateExtrusion(circle, extruVec))
                conePlane = rc.Geometry.Plane(rc.Geometry.Point3d(windVec[0][count+1].X, windVec[0][count+1].Y, point.Z), windVec[0][count+1])
                cone = rc.Geometry.Brep.CreateFromCone(rc.Geometry.Cone(conePlane, scaleFactor*-.5, scaleFactor*.15), True)
                arrowMesh = rc.Geometry.Mesh()
                arrowMesh.Append(rc.Geometry.Mesh.CreateFromBrep(extrusion)[0])
                arrowMesh.Append(rc.Geometry.Mesh.CreateFromBrep(cone)[0])
                arrowMesh.VertexColors.CreateMonotoneMesh(colors[count])
                totalMesh.Append(arrowMesh)
            except: pass
        windVecMesh = [totalMesh]
    else:
        #Evaluate each height.
        windSpdHeight = []
        anchorPts = []
        for count, speed in enumerate(hrWindSpd):
            windHeight = []
            anchorPt = []
            for count, height in enumerate(heightsAboveGround):
                windHeight.append(lb_wind.calcWindSpeedBasedOnHeight(speed, height, d, a, metD, metA))
                anchorPt.append(rc.Geometry.Point3d(0, 0, height))
            windSpdHeight.append(windHeight)
            anchorPts.append(anchorPt)
        
        #Create vectors for each height.
        windVec = []
        for listCount, list in enumerate(windSpdHeight):
            vecForHeights = []
            for speedCount, speed in enumerate(list):
                vec = rc.Geometry.Vector3d(0, speed*windVectorScale, 0)
                vec.Rotate(hrWindDir[listCount], rc.Geometry.Vector3d.ZAxis)
                vecForHeights.append(vec)
            windVec.append(vecForHeights)
        
        #If there is a north angle hooked up, rotate the vectors.
        if north_ != None:
            northAngle, northVector = lb_preparation.angle2north(north_)
            for list in windVec:
                for vec in list:
                    vec.Rotate(northAngle, rc.Geometry.Vector3d.ZAxis)
        else: pass
        
        #Create the wind profile curve.
        profilePts = []
        profileCrv = []
        for listCount, list in enumerate(anchorPts):
            intiPts = []
            for count, point in enumerate(list):
                intiPts.append(rc.Geometry.Point3d(windVec[listCount][count].X, windVec[listCount][count].Y, point.Z))
            profilePts.append(intiPts)
        for listCount, list in enumerate(anchorPts):
            if len(list) != 2:
                interpCrv = rc.Geometry.Curve.CreateInterpolatedCurve(profilePts[listCount][1:], 3)
                ptList = [rc.Geometry.Point3d.Origin, profilePts[listCount][1]]
                tanCrv = interpCrv.TangentAtStart
                tanCrv = rc.Geometry.Vector3d.Multiply(.33, tanCrv)
                startVec = rc.Geometry.Vector3d(windVec[listCount][1].X, windVec[listCount][1].Y, 0)
                startVec.Unitize()
                profileLine = rc.Geometry.Curve.CreateInterpolatedCurve(ptList, 3, rc.Geometry.CurveKnotStyle.Uniform, startVec, tanCrv)
                profileCrv.append(rc.Geometry.Curve.JoinCurves([interpCrv, profileLine], sc.doc.ModelAbsoluteTolerance)[0])
            else:
                profileCrv.append(rc.Geometry.Curve.CreateInterpolatedCurve(profilePts[listCount], 3))
        
        #Get colors for the und profile mesh.
        if legendPar_ == []:
            customColors = [System.Drawing.Color.FromArgb(200,200,255), System.Drawing.Color.FromArgb(175,175,255), System.Drawing.Color.FromArgb(150,150,255), System.Drawing.Color.FromArgb(125,125,255), System.Drawing.Color.FromArgb(100,100,255), System.Drawing.Color.FromArgb(75,75,255), System.Drawing.Color.FromArgb(50,50,255)]
        values = []
        for list in windSpdHeight:
            for value in list[1:]:
                values.append(value)
        values.sort()
        if str(lowB) == "min":
            lowB = values[0]
        if str(highB) == "max":
            highB = values[-1]
        colors = []
        for list in windSpdHeight:
            colors.append(lb_visualization.gradientColor(list[1:], lowB, highB, customColors))
        
        #Create the wind profile mesh.
        windVecMesh = []
        for listCount, list in enumerate(windSpdHeight):
            vectorMesh = rc.Geometry.Mesh()
            
            for count, point in enumerate(anchorPts[listCount][1:]):
                circle = rc.Geometry.Circle(rc.Geometry.Plane(point, windVec[listCount][count+1]), scaleFactor*0.05).ToNurbsCurve()
                extruVec = rc.Geometry.Vector3d(windVec[listCount][count+1].X, windVec[listCount][count+1].Y, 0)
                extruVec.Unitize()
                extruVec = rc.Geometry.Vector3d.Multiply(scaleFactor*-.5, extruVec)
                extruVec = rc.Geometry.Vector3d.Add(windVec[listCount][count+1], extruVec)
                if windVec[listCount][count+1].Length != 0:
                    extrusion = rc.Geometry.Brep.CreateFromSurface(rc.Geometry.Surface.CreateExtrusion(circle, extruVec))
                    conePlane = rc.Geometry.Plane(rc.Geometry.Point3d(windVec[listCount][count+1].X, windVec[listCount][count+1].Y, point.Z), windVec[listCount][count+1])
                    cone = rc.Geometry.Brep.CreateFromCone(rc.Geometry.Cone(conePlane, scaleFactor*-.5, scaleFactor*.15), True)
                    arrowMesh = rc.Geometry.Mesh()
                    arrowMesh.Append(rc.Geometry.Mesh.CreateFromBrep(extrusion)[0])
                    arrowMesh.Append(rc.Geometry.Mesh.CreateFromBrep(cone)[0])
                    arrowMesh.VertexColors.CreateMonotoneMesh(colors[listCount][count])
                    vectorMesh.Append(arrowMesh)
            windVecMesh.append(vectorMesh)
    
    #Calculate a bounding box around everything that will help place the legend ad title.
    allGeo = []
    for item in profileCrv:
        allGeo.append(item)
    if groundBasePt_ == None: basept = rc.Geometry.Point3d.Origin
    else: basept = groundBasePt_
    secondPt = rc.Geometry.Point3d.Add(basept, rc.Geometry.Vector3d(0,((1/scaleFactor)*3),0))
    extraLine = rc.Geometry.LineCurve(basept, secondPt)
    allGeo.append(extraLine)
    lb_visualization.calculateBB(allGeo, True)
    
    #Create a legend.
    legendSrfs, legendText, legendTextSrf, textPt, textSize = lb_visualization.createLegend(values
                    , lowB, highB, numSeg, "m/s", lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
    # generate legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    #Flaten the text list
    legend = lb_preparation.flattenList(legendTextSrf)
    legend.append(legendSrfs)
    #Get the legend base point.
    if legendBasePoint == None:
        legendBasePoint = lb_visualization.BoundingBoxPar[0]
    
    #If the user has specified a base point, use this to move everything.
    if groundBasePt_ != None:
        transformMtx = rc.Geometry.Transform.Translation(groundBasePt_.X, groundBasePt_.Y, groundBasePt_.Z)
        for geo in profileCrv: geo.Transform(transformMtx)
        for geo in windVecMesh: geo.Transform(transformMtx)
        legendBasePoint.Transform(transformMtx)
        for geo in legend:
            if geo != -1: geo.Transform(transformMtx)
        for list in anchorPts:
            for geo in list:
                geo.Transform(transformMtx)
    
    
    return profileCrv, windVecMesh, windSpdHeight, windVec, anchorPts, legend, legendBasePoint




#Check the inputs.
checkData = False
check = checkTheInputs()

if check != -1:
    checkData, heightsAboveGround, analysisPeriod, d, a, epwTerrain, averageData, \
    windSpeed, windDir, epwData, epwStr, lb_preparation, lb_visualization, \
    lb_wind, windVectorScale, scaleFactor = check

#Get the wind profile curve if everything looks good.
if checkData == True:
    windProfileCurve, windVectorMesh, speeds, vectors, anchorPts, legend, legendBasePt = main(heightsAboveGround, analysisPeriod, d, a, epwTerrain, averageData, windSpeed, windDir, epwData, epwStr, lb_preparation, lb_visualization, lb_wind, windVectorScale, scaleFactor)
    
    #Unpack the lists of lists in Python.
    for count, list in enumerate(speeds):
        for item in list:
            windSpeeds.Add(item, GH_Path(count))
    
    for count, list in enumerate(vectors):
        for item in list:
            windVectors.Add(item, GH_Path(count))
    
    for count, list in enumerate(anchorPts):
        for item in list:
            vectorAnchorPts.Add(item, GH_Path(count))

#Hide the anchor points.
ghenv.Component.Params.Output[4].Hidden = True
ghenv.Component.Params.Output[9].Hidden = True