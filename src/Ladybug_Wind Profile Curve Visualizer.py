# Wind Profile Curve Visualizer
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to visualize a wind profile curve for a given terrain type.  Wind speed increases logarithmically as one leaves the ground and wind profiles are a means of visualizing this change in wind speed with height.

-
Provided by Ladybug 0.0.57
    
    Args:
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _windSpeed_tenMeters: The wind speed from the import EPW component or a number representing the wind speed at 10 meters off the ground in agricultural or airport terrian.  This input also accepts lists of numbers representing different speeds at 10 meters.
        _windDirection: The wind direction from the import EPW component or a number in degrees represeting the wind direction from north,  This input also accepts lists of numbers representing different directions.
        _terrainType: The logarithmic model for wind speed varies with the type of terrain. The user may enter values from a slider or a string of text indicating the type of landscape to be evaluated, note that strings of text are case sensistive and therefore capitalization must match exactly the following terms. 0 = "water", 0.5 = "concrete", 1 = "agricultural", 1.5 = "orchard", 2 = "rural", 2.5 = "sprawl", 3 = "suburban", 3.5 = "town", 4 = "urban".
        -------------------------: ...
        stepOfList_ : Use this input to select out specific indices of a list of values connected for wind speed and wind direction.  If you have connected hourly EPW data, this is the equivalent of a "HOY" input and you can use the "Ladybug_DOY_HOY" component to select out a specific hour and date.  Note that this overrides the analysisPeriod_ input below.
        analysisPeriod_: If you have connected data from an EPW component, plug in an analysis period from the Ladybug_Analysis Period component to calculate data for just a portion of the year. The default is Jan 1st 00:00 - Dec 31st 24:00, the entire year.
        averageData_: Set to "True" to average all of the wind data that you have connected into a single wind profile curve. Set to False to return a list of wind profile curves for all connected data or hours within the analysis period.  The default is set to "True" as many wind profile curves can easily become unmanagable. 
        -------------------------: ...
        groundBasePt_: An optional point that can be used to change the base point at shich the wind profile curves are generated.  By default, the wond profile curves generate at the Rhino model origin.
        windVectorScale_: An optional number that can be used to change the scale of the wind vectors in relation to the height of the wind profile curve.  The default is set to 2 so that it is easier to see how the wind speed is changing with height.
        windProfileHeight_: An optional number in Rhino model units that can be used to change the height of the wind profile curve.  By default, the height of the curve is set to 20 meters (or the equivalent distance in your Rhino model units).  You may want to move this number higher or lower depending on the wind effects that you are interested in.
        distBetweenVec_: An optional number in rhino model units that represents the distance between wind vectors in the profile curve.  The default is set to 2 meters (or the equivalent distance in your Rhino model units).
    Returns:
        readMe!: ...
        --------------------: ...
        windSpeedAtHeight: The wind speeds that correspond to the wind vectors in the wind profile visualization.
        windVectors: The wind vectors that correspond to those in the wind profile visualization.  Note that the magnitude of these vectors will be scaled based on the windVectorScale_ input.
        vectorAnchorPts: Anchor points for each of the vectors above, which correspond to the height above the ground for each of the vectors.  Connect this along with the output above to a Grasshopper "Vector Display" component to see the vectors as a grasshopper vector display (as opposed to the vector mesh below).
        --------------------: ...
        windVectorMesh: A mesh displaying the wind vectors that were used to make the profile curve.
        windProfileCurve: A curve outlining the wind speed as it changes with height.  This may also be a list of wind profile curves if multiple "stepOfList_" inputs are connected or "averageData_" is set to False."
"""
ghenv.Component.Name = "Ladybug_Wind Profile Curve Visualizer"
ghenv.Component.NickName = 'WindProfileCurve'
ghenv.Component.Message = 'VER 0.0.57\nJUL_22_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
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
        
        #If the user has input a stepOfList_ that is longer than the calculation length, throw a warning.
        checkData7 = True
        if stepOfList_ == []: pass
        else:
            for item in stepOfList_:
                if item > calcLength or item < 1:
                    checkData7 = False
                    warning = 'You cannot input a stepOfList_ that is less than 1 or greater than the length of values in the _windSpeed or _windDirection lists.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                else: pass
        
        # Evaluate the terrain type to get the right roughness length.
        if _terrainType != None:
            checkData3, roughLength = lb_wind.readTerrainType(_terrainType)
            if checkData3 == True: pass
            else:
                print "You have not connected a correct Terrain type."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "You have not connected a correct Terrain type.")
        else:
            roughLength = None
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
        
        if distBetweenVec > windProfileHeight or distBetweenVec < 0 or distBetweenVec < roughLength:
            distBetweenVec = 0
            checkData4 = False
            print "The input distBetweenVec_ cannot be less than 0, cannot be less than the windProfileHeight_, and cannot be less than the roughness length of your terrain type."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "The input distBetweenVec_ cannot be less than 0, cannot be less than the windProfileHeight_, and cannot be less than the roughness length of your terrain type.")
        
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
        
        #Set the default to averageData_.
        if averageData_ == None:
            averageData = True
        else:
            averageData = averageData_
        
        if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True:
            checkData = True
        else:
            checkData = False
        
        return checkData, heightsAboveGround, analysisPeriod, roughLength, averageData, windSpeed, windDir, epwData, epwStr, lb_preparation, lb_visualization, lb_wind, windVectorScale, conversionFactor
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return False, None, None, None, None, None, None, None, None, None, None,  None


def main(heightsAboveGround, analysisPeriod, roughLength, averageData, windSpeed, windDir, epwData, epwStr, lb_preparation, lb_visualization, lb_wind, windVectorScale, scaleFactor):
    #If epw data is connected, get the data for the analysis period and strip the header off.
    if epwData == True and analysisPeriod != [(1, 1, 1), (12, 31, 24)] and stepOfList_ == []:
        HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
        hrWindDir = []
        hrWindSpd = []
        for count in HOYS:
            hrWindSpd.append(windSpeed[count-1])
            hrWindDir.append(windDir[count-1])
    else:
        hrWindSpd = windSpeed
        hrWindDir = windDir
    
    #If the user has specified a stepOfList_, use this to select out values.
    if stepOfList_ != []:
        hrWindDir = []
        hrWindSpd = []
        for num in stepOfList_:
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
            windSpdHeight[0].append(lb_wind.calcWindSpeedBasedOnHeight(avgHrWindSpd, height, roughLength))
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
            if roughLength < 1:
                profileLine = rc.Geometry.Curve.CreateInterpolatedCurve(ptList, 3, rc.Geometry.CurveKnotStyle.Uniform, startVec, tanCrv)
            else:
                profileLine = rc.Geometry.LineCurve(ptList[0], ptList[1])
            profileCrv = [rc.Geometry.Curve.JoinCurves([interpCrv, profileLine], sc.doc.ModelAbsoluteTolerance)[0]]
        else:
            profileCrv = rc.Geometry.Curve.CreateInterpolatedCurve(profilePts, 3)
        
        #Get colors for the und profile mesh.
        customColors = [System.Drawing.Color.FromArgb(250,250,255), System.Drawing.Color.FromArgb(225,225,255), System.Drawing.Color.FromArgb(200,200,255), System.Drawing.Color.FromArgb(175,175,255), System.Drawing.Color.FromArgb(150,150,255), System.Drawing.Color.FromArgb(125,125,255), System.Drawing.Color.FromArgb(100,100,255), System.Drawing.Color.FromArgb(75,75,255), System.Drawing.Color.FromArgb(50,50,255)]
        values = windSpdHeight[0][:]
        values.sort()
        lowB = values[0]
        highB = values[-1]
        colors = lb_visualization.gradientColor(windSpdHeight[0], lowB, highB, customColors)
        
        #Create the wind profile mesh.
        windVecMesh = rc.Geometry.Mesh()
        for count, point in enumerate(anchorPts[0][1:]):
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
            arrowMesh.VertexColors.CreateMonotoneMesh(colors[count+1])
            windVecMesh.Append(arrowMesh)
    else:
        #Evaluate each height.
        windSpdHeight = []
        anchorPts = []
        for count, speed in enumerate(hrWindSpd):
            windHeight = []
            anchorPt = []
            for count, height in enumerate(heightsAboveGround):
                windHeight.append(lb_wind.calcWindSpeedBasedOnHeight(speed, height, roughLength))
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
                if roughLength < 1:
                    profileLine = rc.Geometry.Curve.CreateInterpolatedCurve(ptList, 3, rc.Geometry.CurveKnotStyle.Uniform, startVec, tanCrv)
                else:
                    profileLine = rc.Geometry.LineCurve(ptList[0], ptList[1])
                profileCrv.append(rc.Geometry.Curve.JoinCurves([interpCrv, profileLine], sc.doc.ModelAbsoluteTolerance)[0])
            else:
                profileCrv.append(rc.Geometry.Curve.CreateInterpolatedCurve(profilePts[listCount], 3))
        
        #Get colors for the und profile mesh.
        customColors = [System.Drawing.Color.FromArgb(250,250,255), System.Drawing.Color.FromArgb(225,225,255), System.Drawing.Color.FromArgb(200,200,255), System.Drawing.Color.FromArgb(175,175,255), System.Drawing.Color.FromArgb(150,150,255), System.Drawing.Color.FromArgb(125,125,255), System.Drawing.Color.FromArgb(100,100,255), System.Drawing.Color.FromArgb(75,75,255), System.Drawing.Color.FromArgb(50,50,255)]
        values = []
        for list in windSpdHeight:
            for value in list:
                values.append(value)
        values.sort()
        lowB = values[0]
        highB = values[-1]
        colors = []
        for list in windSpdHeight:
            colors.append(lb_visualization.gradientColor(list, lowB, highB, customColors))
        
        
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
                    arrowMesh.VertexColors.CreateMonotoneMesh(colors[listCount][count+1])
                    vectorMesh.Append(arrowMesh)
            windVecMesh.append(vectorMesh)
    
    
    
    return profileCrv, windVecMesh, windSpdHeight, windVec, anchorPts




#Check the inputs.
checkData, heightsAboveGround, analysisPeriod, roughLength, averageData, windSpeed, windDir, epwData, epwStr, lb_preparation, lb_visualization, lb_wind, windVectorScale, scaleFactor = checkTheInputs()

#Get the wind profile curve if everything looks good.
if checkData == True:
    windProfileCurve, windVectorMesh, speeds, vectors, anchorPts = main(heightsAboveGround, analysisPeriod, roughLength, averageData, windSpeed, windDir, epwData, epwStr, lb_preparation, lb_visualization, lb_wind, windVectorScale, scaleFactor)
    
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