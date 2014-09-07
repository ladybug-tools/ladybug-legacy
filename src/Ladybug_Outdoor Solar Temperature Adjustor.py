# Outdoor Solar Adjusted Temperature Calculator
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to adjust an existing Mean Radiant Temperature for shortwave solar radiation.  This adjusted mean radiant temperature can then be used in comfort studies.
_
Note that this component assumes that you have already accounted for longwave radiation in the form of the meanRadTemperature_ input.  If you do not hook up a meanRadTemperature_, this component will assume that the surrounding radiant temperature is the same as the air temperature, which is a decent assumption for someone standing in an unobstructed field.  However, the more obstacles that surround the person (and the more "context" that you add), the more important it is to derive a starting mean radiant temperature from a Honeybee Energy simulation.  Also note that this component is not meant to account for shortwave radiation passing through glass.
_
This component uses Radiance functions in order to determine the amount of direct and diffuse solar radiation falling on a comfort mannequin.  The portion reflected off of the ground to the comfort mannequin is derived from these values of direct and diffuse radiation.

Lastly, the formulas to translate this radiation into an effective radiant field and into a solar-adjusted mean radiant temperature come from this paper:
Arens, Edward; Huang, Li; Hoyt, Tyler; Zhou, Xin; Shiavon, Stefano. (2014). Modeling the comfort effects of short-wave solar radiation indoors.  Indoor Environmental Quality (IEQ).
http://escholarship.org/uc/item/89m1h2dg#page-4
-
Provided by Ladybug 0.0.58
    
    Args:
        _cumulativeSkyMtx: The output from a GenCumulativeSkyMtx component.
        _dryBulbTemperature: The direct output of dryBulbTemperature from the Import EPW component or air temperatures from an hourly annual EnergyPlus simulation.
        meanRadiantTemperature_: A number or list of numbers representing the mean radiant temperature of the surrounding surfaces in degrees Celcius.  This number will be modified to account for solar radiation.  If no value is plugged in here, this component will assume that the mean radiant temperature is equal to air temperature value above, which is a decent assumption for someone standing in an unobstructed field.  However, the more obstacles that surround the person (and the more "context" that you add), the more important it is to derive a starting mean radiant temperature from a Honeybee Energy simulation.
        -------------------------: ...
        bodyPosture_: An interger to set the posture of the comfort mannequin, which can have a large effect on the radiation striking the mannequin.  0 = Standing, 1 = Sitting, and 2 = Lying Down.  The default is set to 1 for sitting.
        rotationAngle_: An optional rotation angle in degrees.  Use this number to adjust the angle of the comfort mannequin in space.  The angle of the mannequin in relation to the sun can have a large effect on the amount of radiation that falls on it and thus largely affect the resulting mean radiant temperature.
        bodyLocation_: An optional point that sets the position of the comfort mannequin in space.  Use this to move the comfort mannequin around in relation to contextShading_ connected below. The default is set to the Rhino origin.
        contextShading_: Optional breps or meshes that represent shading and solar obstructions around the mannequin.  Note that, if you end up having a lot of these, you should make sure that you input a starting meanRadTemperature_ derived from an energy simulation.
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        -------------------------: ...
        groundReflectivity_: An optional decimal value between 0 and 1 that represents the fraction of solar radiation reflected off of the ground.  By default, this is set to 0.25, which is characteristic of outdoor grass or dry bare soil.  You may want to increase this value for concrete or decrease it for water or dark soil.
        clothingAbsorptivity_: An optional decimal value between 0 and 1 that represents the fraction of solar radiation absorbed by the human body. The default is set to 0.67 for (white) skin and average clothing.  You may want to increase this value for darker skin or darker clothing.
        -------------------------: ...
        analysisPeriod_: An optional analysis period from the Analysis Period component.  If no Analysis period is given, the analysis will be run for the enitre year.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        parallel_: Set to "True" to run the component using multiple CPUs.  This can dramatically decrease calculation time but can interfere with other intense computational processes that might be running on your machine.
        _runIt: Set to "True" to run the component and calculate solar-adjusted Mean Radiant Temperature.
    Returns:
        readMe!: ...
        --------------------: ...
        effectiveRadiantField: The estimated effective radiant field of the comfort mannequin induced by the sun for each hour of the analysis period.  This is in W/m2.
        MRTDelta: The estimated change in mean radiant temperature for the comfort mannequin induced by the solar radiation.  This is in degreed Celcius.
        solarAdjustedMRT: The estimated solar adjusted mean radiant temperature for each hour of the analysis period.  This is essentially the change in mean radiant temperature above added to the hourly meanRadTemperature_ input.  This is in degreed Celcius and can be plugged into any comfort components for comfort studies.
        solarAdjOperativeTemp: The estimated change in operative temperature for each hour of the analysis period.  This is essentially an average of the solarAdjustedMRT above and the input dryBulbTemperature_.  This is in degrees celcius.
        --------------------: ...
        mannequinMesh: A colored mesh of a comfort mannequin showing the amount of radiation falling over the mannequin's body.
        legend: A legend that corresponds to the colors on the mannequinMesh and shows the relative W/m2.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the chart with the grasshopper "move" component.

"""
ghenv.Component.Name = "Ladybug_Outdoor Solar Temperature Adjustor"
ghenv.Component.NickName = 'SolarAdjustTemperature'
ghenv.Component.Message = 'VER 0.0.58\nSEP_07_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Rhino as rc
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import System
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import math
import System.Threading.Tasks as tasks


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
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        lb_sunpath = sc.sticky["ladybug_SunPath"]()
        
        #Set a default value for epwStr.
        epwStr = []
        
        #Check to see if the user has connected valid air temperature data.
        checkData1 = False
        airTemp = []
        if len(_dryBulbTemperature) != 0:
            try:
                if "Temperature" in _dryBulbTemperature[2]:
                    airTemp = _dryBulbTemperature[7:]
                    checkData1 = True
                    epwStr = _dryBulbTemperature[0:7]
            except: pass
            if checkData1 == False:
                warning = '_dryBulbTemperature input does not contain valid temperature values from the ImportEPW component or a Honeybee energy simulation.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            print 'Connect a list of temperature data for _dryBulbTemperature'
        
        #Check to see if the user has connected valid MRT data.
        checkData2 = False
        radTemp = []
        radMultVal = False
        if len(meanRadTemperature_) != 0:
            try:
                if "Temperature" in meanRadTemperature_[2]:
                    radTemp = meanRadTemperature_[7:]
                    checkData2 = True
                    epwData = True
                    epwStr = meanRadTemperature_[0:7]
            except: pass
            if checkData2 == False:
                for item in meanRadTemperature_:
                    try:
                        radTemp.append(float(item))
                        checkData2 = True
                    except: checkData2 = False
            if len(radTemp) > 1: radMultVal = True
            if checkData2 == False:
                warning = 'meanRadTemperature_ input does not contain valid temperature values in degrees Celcius.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData2 = True
            radTemp = airTemp
            if len (radTemp) > 1: radMultVal = True
            print 'No value connected for meanRadiantTemperature_.  It will be assumed that the radiant temperature is the same as the air temperature.'
        #If there is only one value for MRT, duplicate it 8760 times.
        if len(radTemp) < 8760 and len(radTemp) !=0:
            if len(radTemp) == 1:
                dupData = []
                for count in range(8760):
                    dupData.append(data[0])
                radTemp = dupData
            else:
                checkData2 = False
                warning = 'Input for meanRadTemperature_ must be either the output of an energy simulation, a list of 8760 values, or a single MRT to be applied for every hour of the year..'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        #Check the bodyPosture_ input to be sure that it is a valid interger.
        if bodyPosture_ != 0 and bodyPosture_ != 1 and bodyPosture_ != 2 and bodyPosture_ != None:
            checkData3 = False
            warning = 'Input for bodyPosture_ is not an accepted input interger.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else: checkData3 = True
        if bodyPosture_ == None: bodyPosture = 1
        else: bodyPosture = bodyPosture_
        
        #Convert the rotation angle to radians or set a default of 0 if there is none.
        if rotationAngle_ != None:
            rotateAngle = rotationAngle_*0.0174532925
        else:
            rotateAngle = 0.0
        
        #Create the comfort mannequin.
        if checkData3 == True:
            if bodyPosture == 1:
                mannequinData = lb_comfortModels.getSeatedMannequinData()
            else:
                mannequinData = lb_comfortModels.getStandingMannequinData()
            #Construct the mannequin from the point data.
            mannequinMeshBreps = []
            for faceList in mannequinData:
                surfacePts = []
                for pointCoord in faceList:
                    point = rc.Geometry.Point3d(pointCoord[0], pointCoord[1], pointCoord[2])
                    surfacePts.append(point)
                if len(surfacePts) == 4: 
                    surface = rc.Geometry.Brep.CreateFromCornerPoints(surfacePts[0], surfacePts[1], surfacePts[2], surfacePts[3], sc.doc.ModelAbsoluteTolerance)
                else:
                    surface = rc.Geometry.Brep.CreateFromCornerPoints(surfacePts[0], surfacePts[1], surfacePts[2], sc.doc.ModelAbsoluteTolerance)
                mannequinMeshBreps.append(surface)
            mannequinMesh = rc.Geometry.Brep.JoinBreps(mannequinMeshBreps, sc.doc.ModelAbsoluteTolerance)[0]
            #Scale the Mannequin based on the model units.
            conversionFac = lb_preparation.checkUnits()
            scale = rc.Geometry.Transform.Scale(rc.Geometry.Plane.WorldXY, 1/conversionFac, 1/conversionFac, 1/conversionFac)
            mannequinMesh.Transform(scale)
            #If the user has selected a mannequin laying down, rotate the standing mannequin.
            if bodyPosture == 2:
                lieDownTransform = rc.Geometry.Transform.Rotation(rc.Geometry.Vector3d.ZAxis, rc.Geometry.Vector3d.YAxis, rc.Geometry.Point3d.Origin)
                moveUpTransform = rc.Geometry.Transform.Translation(0,-.85,.15)
                mannequinMesh.Transform(lieDownTransform)
                mannequinMesh.Transform(moveUpTransform)
            else: pass
            #Rotate the mannequin as the user wants.
            if rotateAngle != 0.0:
                rotateTransform = rc.Geometry.Transform.Rotation(rotateAngle, rc.Geometry.Vector3d.ZAxis, rc.Geometry.Point3d.Origin)
                mannequinMesh.Transform(rotateTransform)
            else: pass
            #Change the location of the mannequin as the user wants.
            if bodyLocation_ != None:
                moveTransform = rc.Geometry.Transform.Translation(bodyLocation_.X, bodyLocation_.Y, bodyLocation_.Z)
                mannequinMesh.Transform(moveTransform)
            else: pass
            #Turn the mannequin mesh into a brep.
            mannequinMesh = rc.Geometry.Mesh.CreateFromBrep(mannequinMesh, rc.Geometry.MeshingParameters.Coarse)
        else: mannequinMesh = None
        
        #Create a ground mesh.
        groundMesh = rc.Geometry.Mesh()
        point1 = rc.Geometry.Point3d(-.5, -1, 0)
        point2 = rc.Geometry.Point3d(-.5, -2, 0)
        point3 = rc.Geometry.Point3d(.5, -2, 0)
        point4 = rc.Geometry.Point3d(.5, -1, 0)
        groundMesh.Vertices.Add(point1)
        groundMesh.Vertices.Add(point2)
        groundMesh.Vertices.Add(point3)
        groundMesh.Vertices.Add(point4)
        groundMesh.Faces.AddFace(0, 1, 2, 3)
        if bodyLocation_ != None:
            groundMesh.Transform(moveTransform)
        else: pass
        
        # Mesh the context.
        if len(contextShading_)!=0:
            ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
            contextMesh, contextBrep = lb_preparation.cleanAndCoerceList(context)
            
            ## mesh Brep
            contextMeshedBrep = lb_mesh.parallel_makeContextMesh(contextBrep)
            
            ## Flatten the list of surfaces
            contextMeshedBrep = lb_preparation.flattenList(contextMeshedBrep)
            contextSrfs = contextMesh + contextMeshedBrep
        else: contextSrfs = []
        
        #Check the ground reflectivity.
        checkData4 = True
        if groundReflectivity_ != None:
            if groundReflectivity_ < 1 and groundReflectivity_ > 0:
                groundR = groundReflectivity_
            else:
                groundR = None
                checkData4 = False
                warning = 'groundReflectivity_ must be a value between 0 and 1.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            groundR = 0.25
            print 'No value found for groundReflectivity_.  The ground reflectivity will be set to 0.25 for grass or light bare soil.'
        
        #Check the clothing absorptivity.
        checkData5 = True
        if clothingAbsorptivity_ != None:
            if clothingAbsorptivity_ < 1 and clothingAbsorptivity_ > 0:
                cloA = clothingAbsorptivity_
            else:
                cloA = None
                checkData5 = False
                warning = 'clothingAbsorptivity_ must be a value between 0 and 1.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            cloA = 0.67
            print 'No value found for clothingAbsorptivity_.  The clothing absorptivity will be set to 0.67 for (white) skin and average clothing.'
        
        #Set the default parallel to true.
        if parallel_ == None:
            parallel = True
        else: parallel = parallel_
        
        #Make the default analyisis period for the whole year if the user has not input one.
        if analysisPeriod_ == []:
            analysisPeriod = [(1, 1, 1), (12, 31, 24)]
        else:
            analysisPeriod = analysisPeriod_
        
        #Set a north vector if there is not oe already.
        if north_ != None:
            northAngle, northVector = lb_preparation.angle2north(north_)
        else:
            northVector = rc.Geometry.Vector3d.YAxis
            northAngle = 0.0
        
        #Check if everything is good.
        if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True:
            checkData = True
        else:
            checkData = False
        
        return checkData, airTemp, radTemp, mannequinMesh, groundMesh, contextSrfs, groundR, cloA, parallel, analysisPeriod, northAngle, northVector, epwStr, conversionFac, lb_preparation, lb_visualization, lb_mesh, lb_runStudy_GH, lb_comfortModels, lb_sunpath
    else:
        return -1


def runAnalyses(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs, parallel, cumSky_radiationStudy, conversionFac, northVector, lb_preparation, lb_mesh, lb_runStudy_GH):
    RADIANCE_radiationStudy = []
    if len(RADIANCE_radiationStudy)!=0:
        pass
    elif cumSky_radiationStudy != None and (len(cumSky_radiationStudy) == 456 or len(cumSky_radiationStudy) == 1752) and analysisSrfs:
        indexList, listInfo = lb_preparation.separateList(cumSky_radiationStudy, lb_preparation.strToBeFound)
        selList = []
        for i in range(1):
            [selList.append(float(x)) for x in cumSky_radiationStudy[indexList[i]+7:indexList[i+1]]]
            
        cumSky_radiationStudy = selList
        if parallel:
            try:
                for geo in analysisSrfs + contextSrfs: geo.EnsurePrivateCopy()
            except:
                pass
        
        # join the meshes
        joinedAnalysisMesh = lb_mesh.joinMesh(analysisSrfs)
        if contextSrfs: joinedContext = lb_mesh.joinMesh(contextSrfs)
        else: joinedContext = None
        if len(cumSky_radiationStudy) == 145:
            radResults, totalRadResults, intersectionMtx = lb_runStudy_GH.parallel_radCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, joinedContext,
                                    parallel, cumSky_radiationStudy, lb_preparation.TregenzaPatchesNormalVectors, conversionFac, 2200000000000000, northVector)
        elif len(cumSky_radiationStudy) == 577:
            radResults, totalRadResults, intersectionMtx = lb_runStudy_GH.parallel_radCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, joinedContext,
                                    parallel, cumSky_radiationStudy, lb_preparation.getReinhartPatchesNormalVectors(), conversionFac, 2200000000000000, northVector)
                                    
    
    return radResults, totalRadResults, listInfo, intersectionMtx

def getHourlySky(daylightMtxDict, HOY):
    # for presentation
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    stDate = lb_preparation.hour2Date(HOY, 1)
    analysisP = ((stDate[1]+1, stDate[0], stDate[2]-1),(stDate[1]+1, stDate[0], stDate[2]))
    
    hourlyMtx = []
    for patchNumber in daylightMtxDict.keys():
        # first patch is the ground
        if patchNumber!=0:
            hourlyMtx.append(daylightMtxDict[patchNumber][HOY])
    return hourlyMtx, analysisP

def getCumulativeSky(daylightMtxDict, runningPeriod):
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    def selectHourlyData(dataList, analysisPeriod):
        # read analysis period
        stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, False)
        
        selHourlyData =[];
        
        # select data
        stAnnualHour = lb_preparation.date2Hour(stMonth, stDay, stHour)
        endAnnualHour = lb_preparation.date2Hour(endMonth, endDay, endHour)
        
        # check it goes from the end of the year to the start of the year
        if stAnnualHour < endAnnualHour:
            for i, item in enumerate(dataList[stAnnualHour-1:endAnnualHour+1]):
                if stHour-1 <= (i + stHour - 1)%24 <= endHour-1: selHourlyData.append(item)
            type = True
        else:
            for i, item in enumerate(dataList[stAnnualHour-1:]):
                if stHour-1 <= (i + stHour - 1)%24 <= endHour-1: selHourlyData.append(item)
            for i, item in enumerate(dataList[:endAnnualHour + 1]):
                if stHour-1 <= i %24 <= endHour-1: selHourlyData.append(item)
            type = False
        
        return selHourlyData
    
    HOYS = selectHourlyData(range(8760), runningPeriod)
    
    hourlyMtx = []
    for patchNumber in daylightMtxDict.keys():
        if patchNumber!=0:
            cumulativeDifValue = 0
            cumulativeDirValue = 0
            # adding upp the values
            try:
                for HOY in HOYS:
                    difValue, dirValue = daylightMtxDict[patchNumber][HOY + 1]
                    cumulativeDifValue += difValue
                    cumulativeDirValue += dirValue 
            except Exception, e:
                print `e`
                
            hourlyMtx.append([cumulativeDifValue/1000, cumulativeDirValue/1000])
    
    return hourlyMtx

def prepareLBList(skyMtxLists, analysisPeriod, locName, unit, removeDiffuse, removeDirect):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    # prepare the final output
    stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, False)
    totalRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Total Radiation", unit, 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
    diffuseRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Diffuse Radiation", unit, 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
    directRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Direct Radiation", unit, 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
    
    for radValues in skyMtxLists:
        if not removeDiffuse and not removeDirect:
            totalRad.append(sum(radValues))
            diffuseRad.append(radValues[0])
            directRad.append(radValues[1])
        elif removeDiffuse and removeDirect:
            totalRad.append(0)
            diffuseRad.append(0)
            directRad.append(0)
        elif removeDirect:
            totalRad.append(radValues[0])
            diffuseRad.append(radValues[0])
            directRad.append(0)
        elif removeDiffuse:
            totalRad.append(radValues[1])
            diffuseRad.append(0)
            directRad.append(radValues[1])
    
    return totalRad + diffuseRad + directRad

def resultVisualization(analysisSrfs, results, totalResults, legendPar, legendTitle, studyLayerName, checkTheName, l, listInfo, lb_preparation, lb_visualization):
    
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize = lb_preparation.readLegendParameters(legendPar, False)
    
    colors = lb_visualization.gradientColor(results, lowB, highB, customColors)
    
    # color mesh surfaces
    analysisSrfs = lb_visualization.colorMesh(colors, analysisSrfs)
    
    ## generate legend
    # calculate the boundingbox to find the legendPosition
    personGeo = analysisSrfs.DuplicateMesh()
    personGeo.Faces.DeleteFaces([len(results)-1])
    lb_visualization.calculateBB([personGeo])
    
    # legend geometry
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(results, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize)
    
    # legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)

    customHeading = '\n\nRadiation Analysis'
    titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[0]], lb_visualization.BoundingBoxPar, legendScale, customHeading, False, legendFont, legendFontSize)
    
    if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
    
    
    return analysisSrfs, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], l, legendBasePoint


def main(airTemp, radTemp, mannequinMesh, groundMesh, contextSrfs, groundR, cloA, parallel, analysisPeriod, northAngle, northVector, epwStr, conversionFac, lb_preparation, lb_visualization, lb_mesh, lb_runStudy_GH, lb_comfortModels, lb_sunpath):
    #Define lists to be filled and put headers on them.
    ERF = []
    MRTDelta = []
    solarAdjustedMRT = []
    solarAdjOperativeTemp = []
    hourOrder = []
    
    #Define the fraction of the body visible to radiation.
    if bodyPosture_ == 0:
        fracEff = 0.725
    elif bodyPosture_ == 1:
        fracEff = 0.696
    else:
        fracEff = 0.5
    
    #Define a good guess of a radiative heat transfer coefficient.
    radTransCoeff = 6.012
    
    #Get a list of HOYs for the analysis period
    HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
    
    #Compute the existing ERF for the analysis period.
    if analysisPeriod != [(1, 1, 1), (12, 31, 24)]:
        newAirTemp = []
        newRadTemp = []
        for hour in HOYS:
            newAirTemp.append(airTemp[hour-1])
            newRadTemp.append(radTemp[hour-1])
        airTemp = newAirTemp
        radTemp = newRadTemp
    
    currentERF = []
    for count, temp in enumerate(radTemp):
        erf = fracEff * radTransCoeff *(temp - airTemp[count])
        currentERF.append(erf)
    
    #Calculate the sun-up hours of the year to help make things faster down the road.
    lb_sunpath.initTheClass(float(_cumulativeSkyMtx.lat), northAngle, rc.Geometry.Point3d.Origin, 100, float(_cumulativeSkyMtx.lngt), float(_cumulativeSkyMtx.timeZone))
    altitudes = []
    for hour in HOYS:
        d, m, t = lb_preparation.hour2Date(hour, True)
        lb_sunpath.solInitOutput(d, m, t)
        altitude = lb_sunpath.solAlt
        altitudes.append(altitude)
    
    #Process the cumulative sky into an initial selected sky.
    skyMtxLists = []
    skyMtxLists = getCumulativeSky(_cumulativeSkyMtx.d, analysisPeriod)
    unit = 'kWh/m2'
    
    if len(skyMtxLists)!=0:
        selectedSkyMtx = prepareLBList(skyMtxLists, analysisPeriod, _cumulativeSkyMtx.location, unit, False, False)
        cumSky_radiationStudy = selectedSkyMtx
        
        #Set defaults.
        disFromBase = 0.01
        analysisSrfs = []
        for mesh in mannequinMesh:
             analysisSrfs.append(mesh)
        analysisSrfs.append(groundMesh)
        
        ## extract test points
        testPoints, ptsNormals, meshSrfAreas = lb_mesh.parallel_testPointCalculator(analysisSrfs, float(disFromBase), parallel)
        originalTestPoints = testPoints
        testPoints = lb_preparation.flattenList(testPoints)
        
        ptsNormals = lb_preparation.flattenList(ptsNormals)
        meshSrfAreas = lb_preparation.flattenList(meshSrfAreas)
        
        #Get an intersection matrix of the geometry and the sky and some results for the whole analysis period.
        radResults, totalRadResults, listInfo, intersectionMtx = runAnalyses(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs, parallel, cumSky_radiationStudy, conversionFac, northVector, lb_preparation, lb_mesh, lb_runStudy_GH)
        
        #Make a colored mesh of the mannequin for the whole analysis period.
        resultColored = []
        legendColored = []
        studyLayerNames = "RADIATION_STUDIES"
        if radResults!= None:
            resultColored, legendColored, l, legendBasePoint = resultVisualization(analysisSrfs, radResults, totalRadResults, legendPar_, unit, studyLayerNames, True, 0, listInfo, lb_preparation, lb_visualization)
        
        #Remove the ground mesh, which is the last one.
        resultColored.Faces.DeleteFaces([len(radResults)-1])
        
        #Unpack the legend.
        legend = []
        legend.append(legendColored[0])
        for item in legendColored[1]:
            legend.append(item)
        
        intDict = intersectionMtx
        personMeshAreas = []
        for area in meshSrfAreas[:-1]:
            personMeshAreas.append(area*conversionFac*conversionFac)
        totalPersonArea = sum(personMeshAreas)
        
        #Define functions for computing the radiation for each hour, which is in parallal and not in parallel.
        def nonParallelRadCalc():
            for count, hour in enumerate(HOYS):
                if count != len(HOYS)-1: lastVal = 1
                else: lastVal = 0
                if altitudes[count] > 0 or altitudes[count-1] > 0 or altitudes[count+lastVal] > 0:
                    skyMtxLists, _analysisPeriod_ = getHourlySky(_cumulativeSkyMtx.d, hour)
                    selSkyMatrix = prepareLBList(skyMtxLists, analysisPeriod, _cumulativeSkyMtx.location, unit, False, False)
                    
                    indexList, listInfo = lb_preparation.separateList(selSkyMatrix, lb_preparation.strToBeFound)
                    #separate total, diffuse and direct radiations
                    separatedLists = []
                    for i in range(len(indexList)-1):
                        selList = []
                        [selList.append(float(x)) for x in selSkyMatrix[indexList[i] + 7:indexList[i+1]]]
                        separatedLists.append(selList)
                    
                    skyMatrix = separatedLists[0]
                    
                    radiationResult = []
                    for ptCount in  intDict.keys():
                        radValue = 0
                        for patchCount in intDict[ptCount].keys():
                            if intDict[ptCount][patchCount]['isIntersect']:
                                radValue = radValue + (skyMatrix[patchCount] * math.cos(intDict[ptCount][patchCount]['vecAngle']))
                        radiationResult.append(radValue)
                    
                    personRad = radiationResult[:-1]
                    groundRad = radiationResult[-1]
                    totalPersonBeamDiffRad = sum([a*b for a,b in zip(personRad,personMeshAreas)])
                    
                    #Calculate the additional radiation reflected to the person by the ground.
                    groundRefRad = 0.5 * groundRad * fracEff * groundR
                    
                    #Calculate the total person radiation and the ERF.
                    totalPersonRad = totalPersonBeamDiffRad + groundRefRad
                    radiantFlux = totalPersonRad/totalPersonArea
                    hourSolERF = (radiantFlux * cloA)/0.95
                    hourERF = hourSolERF + currentERF[count]
                    ERF.append(hourERF/1000)
                    
                    #Calculate the MRT delta, the solar adjusted MRT, and the solar adjusted operative temperature.
                    hourMRT = (hourERF/(fracEff*radTransCoeff)) + (radTemp[count])
                    hourOp = (hourMRT+airTemp[count])/2
                    solarAdjustedMRT.append(hourMRT)
                    solarAdjOperativeTemp.append(hourOp)
                    mrtDelt = hourMRT - radTemp[count]
                    MRTDelta.append(mrtDelt)
                else:
                    ERF.append(currentERF[count])
                    solarAdjustedMRT.append(radTemp[count])
                    solarAdjOperativeTemp.append((radTemp[count] + airTemp[count])/2)
                    MRTDelta.append(0)
            return True
        
        def parallelRadCalc():
            def radCalc(count):
                if count != len(HOYS)-1: lastVal = 1
                else: lastVal = 0
                if altitudes[count] > 0 or altitudes[count-1] > 0 or altitudes[count+lastVal] > 0:
                    skyMtxLists, _analysisPeriod_ = getHourlySky(_cumulativeSkyMtx.d, HOYS[count])
                    selSkyMatrix = prepareLBList(skyMtxLists, analysisPeriod, _cumulativeSkyMtx.location, unit, False, False)
                    
                    indexList, listInfo = lb_preparation.separateList(selSkyMatrix, lb_preparation.strToBeFound)
                    #separate total, diffuse and direct radiations
                    separatedLists = []
                    for i in range(len(indexList)-1):
                        selList = []
                        [selList.append(float(x)) for x in selSkyMatrix[indexList[i] + 7:indexList[i+1]]]
                        separatedLists.append(selList)
                    
                    skyMatrix = separatedLists[0]
                    
                    radiationResult = []
                    for ptCount in  intDict.keys():
                        radValue = 0
                        for patchCount in intDict[ptCount].keys():
                            if intDict[ptCount][patchCount]['isIntersect']:
                                radValue = radValue + (skyMatrix[patchCount] * math.cos(intDict[ptCount][patchCount]['vecAngle']))
                        radiationResult.append(radValue)
                    
                    personRad = radiationResult[:-1]
                    groundRad = radiationResult[-1]
                    totalPersonBeamDiffRad = sum([a*b for a,b in zip(personRad,personMeshAreas)])
                    
                    #Calculate the additional radiation reflected to the person by the ground.
                    groundRefRad = 0.5 * groundRad * fracEff * groundR
                    
                    #Calculate the total person radiation and the ERF.
                    totalPersonRad = totalPersonBeamDiffRad + groundRefRad
                    radiantFlux = totalPersonRad/totalPersonArea
                    hourSolERF = (radiantFlux * cloA)/0.95
                    hourERF = hourSolERF + currentERF[count]
                    ERF.append(hourERF/1000)
                    
                    #Calculate the MRT delta, the solar adjusted MRT, and the solar adjusted operative temperature.
                    hourMRT = (hourERF/(fracEff*radTransCoeff)) + (radTemp[count])
                    hourOp = (hourMRT+airTemp[count])/2
                    solarAdjustedMRT.append(hourMRT)
                    solarAdjOperativeTemp.append(hourOp)
                    mrtDelt = hourMRT - radTemp[count]
                    MRTDelta.append(mrtDelt)
                else:
                    ERF.append(currentERF[count])
                    solarAdjustedMRT.append(radTemp[count])
                    solarAdjOperativeTemp.append((radTemp[count] + airTemp[count])/2)
                    MRTDelta.append(0)
                hourOrder.append(count)
            
            tasks.Parallel.ForEach(range(len(HOYS)), radCalc)
            
            return True
        
        # Compute the radiation for each hour of the year.
        if parallel == False:
            runSuccess = nonParallelRadCalc()
        else:
            runSuccess = parallelRadCalc()
        
        #If the process above was run in parallel, re-order the numbers correctly (instead of by when they finished calculating).
        if parallel == True:
            ERF = [x for (y,x) in sorted(zip(hourOrder, ERF))]
            MRTDelta = [x for (y,x) in sorted(zip(hourOrder, MRTDelta))]
            solarAdjustedMRT = [x for (y,x) in sorted(zip(hourOrder, solarAdjustedMRT))]
            solarAdjOperativeTemp = [x for (y,x) in sorted(zip(hourOrder, solarAdjOperativeTemp))]
        
        
        #Add the headers to the computed lists.
        ERF.insert(0,analysisPeriod[1])
        ERF.insert(0,analysisPeriod[0])
        ERF.insert(0,epwStr[4])
        ERF.insert(0,'kWh/m2')
        ERF.insert(0,'Effective Radiant Field')
        ERF.insert(0,epwStr[1])
        ERF.insert(0,epwStr[0])
        
        MRTDelta.insert(0,analysisPeriod[1])
        MRTDelta.insert(0,analysisPeriod[0])
        MRTDelta.insert(0,epwStr[4])
        MRTDelta.insert(0,'C')
        MRTDelta.insert(0,'Solar Mean Radiant Temp Delta')
        MRTDelta.insert(0,epwStr[1])
        MRTDelta.insert(0,epwStr[0])
        
        solarAdjustedMRT.insert(0,analysisPeriod[1])
        solarAdjustedMRT.insert(0,analysisPeriod[0])
        solarAdjustedMRT.insert(0,epwStr[4])
        solarAdjustedMRT.insert(0,'C')
        solarAdjustedMRT.insert(0,'Solar-Adjusted Mean Radiant Temperature')
        solarAdjustedMRT.insert(0,epwStr[1])
        solarAdjustedMRT.insert(0,epwStr[0])
        
        solarAdjOperativeTemp.insert(0,analysisPeriod[1])
        solarAdjOperativeTemp.insert(0,analysisPeriod[0])
        solarAdjOperativeTemp.insert(0,epwStr[4])
        solarAdjOperativeTemp.insert(0,'C')
        solarAdjOperativeTemp.insert(0,'Solar-Adjusted Operative Temp')
        solarAdjOperativeTemp.insert(0,epwStr[1])
        solarAdjOperativeTemp.insert(0,epwStr[0])
        
        
        return ERF, MRTDelta, solarAdjustedMRT, solarAdjOperativeTemp, resultColored, legend, legendBasePoint
    else:
        return None, None, None, None, None, None, None
        warning = "cumulativeSkyMtx failed to collect data."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)




#Check the inputs
checkData = False
results = checkTheInputs()

if results!= -1:
    checkData, airTemp, radTemp, mannequinMesh, groundMesh, context, groundR, \
    cloA, parallel, analysisPeriod, northAngle, northVector, epwStr, conversionFac, \
    lb_preparation, lb_visualization, lb_mesh, lb_runStudy_GH, lb_comfortModels,\
    lb_sunpath = results

#Run the analysis.
if _runIt == True and checkData == True:
    effectiveRadiantField, MRTDelta, solarAdjustedMRT, solarAdjOperativeTemp, \
    mannequinMesh, legend, legendBasePt = main(airTemp, radTemp, mannequinMesh, \
    groundMesh, context, groundR, cloA, parallel, analysisPeriod, northAngle, \
    northVector, epwStr, conversionFac, lb_preparation, lb_visualization, lb_mesh, \
    lb_runStudy_GH, lb_comfortModels, lb_sunpath)

#Hide the legend base point.
ghenv.Component.Params.Output[9].Hidden = True