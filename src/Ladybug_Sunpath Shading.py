# Sunpath shading
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Djordje Spasic <djordjedspasic@gmail.com> 
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
This component calculates the shading of:
- Photovoltaic modules
- Solar Water Heating collectors
- any other purpose (shading of points)
-
Use "annualShading", "Sep21toMar21Shading" and "Mar21toSep21Shading" outputs for Photovoltaic modules shading. 
Use "beamIndexPerHour" and "skyViewFactor" outputs for Solar Water Heating collectors shading, or any other purpose.
Use "shadedSolarRadiationPerHour" data for "solarRadiationPerHour_" input of "Thermal Comfort Indices" component to account for shading.
-
"annualShading" output is based on "Using sun path charts to estimate the effects of shading on PV arrays", University of Oregon, Frank Vignola:
http://solardat.uoregon.edu/download/Papers/UsingSunPathChartstoEstimatetheEffectofShadingonPVArrays.pdf
-
Provided by Ladybug 0.0.62
    
    input:
        _epwFile: Input .epw file path by using the "File Path" parameter, or Ladybug's "Open EPW And STAT Weather Files" component.
        _analysisGeometry: Input surface(a) or point(b) (a single one or more of them).
                           -
                           a) Input planar Surface (not polysurface) on which the PV modules/Solar water heating collectors will be applied.
                           If you have a polysurface, explode it (using "Deconstruct Brep" component) and then feed its Faces(F) output to _analysisGeometry. Surface normal should be faced towards the sun.
                           -
                           b) You can also supply point(s) and its shading will be calculated.
                           -
                           Geometry inputted to "_analysisGeometry", will be accounted for self-shading, so there is no need to input it to the "context_" also.
        context_: Buildings, structures, mountains and other permanent obstructions.
                  -
                  If you supplied surface(s) to the "_analysisGeometry", input them into the "context_" too, to account for self-shading.
                  If you inputted point(s) into the "_analysisGeometry", there's no need to input them into the "context_".
                  -
                  Input polysurfaces, surfaces, or meshes.
        coniferousTrees_: This input allows for partial shading from coniferous(evergreen) context trees.
                          -
                          Input polysurfaces, surfaces, or meshes.
        deciduousTrees_: This input allows for partial shading during in-leaf and leaf-less periods from deciduous context trees.
                         In-leaf being a period from 21st March to 21st September in the northern hemisphere, and from 21st September to 21st March in the southern hemisphere.
                         Leaf-less being a period from 21st September to 21st March in the northern hemisphere, and from 21st March to 21st September in the in the southern hemisphere.
                         -
                         Input polysurfaces, surfaces, or meshes.
        coniferousAllyearIndex_: All year round transmission index for coniferous(evergreen) context trees. It ranges from 0 to 1.0. 0 represents deciduous trees which do not allow solar radiation to pass through them (100% shading). 1 represents all solar radiation passing through deciduous trees, like the trees do not exist (0% shading).
                                 -
                                 If not supplied default value of 0.30 (equals 70% shading) will be used.
                                 -
                                 Unitless.
        deciduousInleafIndex_: Deciduous context trees transmission index for in-leaf period. In-leaf being a period from 21st March to 21st September in the northern hemisphere, and from 21st September to 21st March in the southern hemisphere.
                               It ranges from 0 to 1.0. 0 represents deciduous trees which do not allow solar radiation to pass through them (100% shading). 1 represents all solar radiation passing through deciduous trees, like the trees do not exist (0% shading).
                               -
                               If not supplied default value of 0.23 (equals 77% shading) will be used.
                               -
                               Unitless.
        deciduousLeaflessIndex_: Deciduous context trees transmission index for leaf-less period. Leaf-less being a period from 21st September to 21st March in the northern hemisphere, and from 21st March to 21st September in the in the southern hemisphere.
                                It ranges from 0 to 1.0. 0 represents deciduous trees which do not allow solar radiation to pass through them (100% shading). 1 represents all solar radiation passing through deciduous trees, like the trees do not exist (0% shading).
                                -
                                If not supplied default value of 0.64 (equals 36% shading) will be used.
                                -
                                Unitless.
        leaflessPeriod_: Define the leafless period for deciduous trees using Ladybug's "Analysis Period" component.
                         IMPORTANT! This input affects only the skyViewFactor, beamIndexPerHour, shadedSolarRadiationPerHour output. Due to limitations of the used sunpath diagram, it does not affect the Sep21toMar21Shading, Mar21toSep21Shading, annualShading outputs, where default leafless periods (see the line bellow) will always be used.
                         -
                         If not supplied the following default periods will be used: from 21st September to 21st March in the northern hemisphere, and from 21st March to 21st September in the in the southern hemisphere.
        ACenergyPerHour_: This input is necessaty only if you are calculating the shading of the PV modules. If that is so, input the "ACenergyPerHour" output data from "Photovoltaics surface" component.
                          -
                          If you are calculating shading analysis for "Solar water heating surface" component (instead of "Photovoltaics surface" component), leave this input empty.
                          -
                          If you are calculating shading analysis for any other purpose (of point(s) for example) leave this input empty too.
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        albedo_: A list of 8767 (with header) or 8760 (without the header) albedo values for each hour during a year.
                 Albedo (or Reflection coefficient) is an average ratio of the global incident solar radiation reflected from the area surrounding the _analysisGeometry.
                 It ranges from 0 to 1.
                 -
                 It depends on the time of the year/day, surface type, temperature, vegetation, presence of water, ice and snow etc.
                 -
                 If no list supplied, default value of 0.20 will be used, corrected(increased) for the presence of snow (if any).
                 -
                 Unitless.
        outputGeometryIndex_: An index of the surface inputted into "_analysisGeometry" if "_analysisGeometry" would be flattened..
                              It determines the surface for which output geometry will be generated.
                              -
                              If not supplied, geometry for the first surface (index: 0) will be generated as a default.
        scale_: Scale of the overall geometry (sunPath curves, sunWindow mesh).
                Use the scale number which enables encompassing all of your context_, coniferousTrees_, deciduousTrees_ objects.
                -
                If not supplied, default value of 1 will be used.
        hoursPositionScale_: Scale factor for positioning of solar time hour points (that's "hoursPositions" output).
                             -
                             If not supplied, default value of 1 will be used.
        precision_: Overall shading precision. Ranges from 1-100. It represents the square root number of shading analysis points per sun window quadrant.
                    Example - precision of 20 would be 400 shading analysis points per single sun window quadrant.
                    CAUTION!!! Higher precision numbers (50 >) require stronger performance PCs. If your "_context" contains only straight shape buildings/objects, and you have just a couple of trees supplied to the "coniferousTrees_" and "deciduousTrees_" inputs, the precision of < 50 will be just fine.
                    -
                    If not supplied, default value of 2 will be used.
        legendPar_: Optional legend parameters from the Ladybug "Legend Parameters" component.
        bakeIt_: Set to "True" to bake the Sunpath shading results into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
        
    output:
        readMe!: ...
        skyViewFactor: Continuous Sky View Factor - portion of the visible sky (dome). It defines the shading of the parts of diffuse irradiance. It ranges from 0 to 1.
                       0 means that the sky dome is competely obstructed by obstacles and all incoming diffuse sky irradiance is blocked (100% shading). 1 means that sky dome is competely free of obstacles (0% shading).
                       -
                       This output is similar to "skyView" output of Ladybug's "Shading Mask" component. Unlike "skyView" it takes into account transparency of trees. But it does not visually present the shading, which is what "Shading Mask" component does.
                       -
                       Use it as an input for Ladybug "Solar Water Heating System" or "Solar Water Heating System Detailed" component's "skyViewFactor_" input to account for diffuse irradiance shading of SWHsurface.
                       -
                       Unitless.
        beamIndexPerHour: Transmission index of beam (direct) irradiance for each hour during a year. It ranges from 0-1.
                          Transmission index of 0 means 100% shading. Transmission index of 1 means 0% shading.
                          It is calculated for each analysisGeometry vertex and then averaged.
                          -
                          Use it as an input for Ladybug "Solar Water Heating System" or "Solar Water Heating System Detailed" component's "beamIndexPerHour_" input to account for diffuse direct beam shading of SWH surface.
                          -
                          Unitless.
        shadedSolarRadiationPerHour: Total shaded incidence for each hour during a year.
                                     Data from this output can be used for "solarRadiationPerHour_" input of "Thermal Comfort Indices" component to account for shading.
                                     -
                                     In Wh/m2.
        sunWindowShadedAreaPer: Percent of the overall sun window shaded area. It is calculated for analysisGeometry area centroid. It ranges from 0-100(%).
                                -
                                In percent(%).
        unweightedAnnualShading: Annual unweighted shading of the active sun window quadrants. Active sun window quadrants are only those which produce AC energy.
                                 Unweighted means that each active sun window quadrant produces the same percentage of AC power. It is calculated for each analysisGeometry vertex and then averaged. It ranges from 0-100(%).
                                 -
                                 In percent(%).
        Sep21toMar21Shading: Weighted shading of the active sun window quadrants, for period between 21st September to 21st March. Active sun window quadrants are only those which produce AC energy.
                             It is calculated for each analysisGeometry vertex and then averaged. It ranges from 0-100(%).
                             -
                             In percent(%).
        Mar21toSep21Shading: Weighted shading of the active sun window quadrants, for period between 21st March to 21st September. Active sun window quadrants are only those which produce AC energy.
                             It is calculated for each analysisGeometry vertex and then averaged. It ranges from 0-100(%).
                             -
                             In percent(%).
        annualShading: Annual weighted shading of the active sun window quadrants. To calculate it, input the hourly data to "ACenergyPerHour_" input.
                       Active sun window quadrants are only those which produce AC energy.
                       It is calculated for each analysisGeometry vertex and then averaged. It ranges from 0-100(%).
                       -
                       Use it as an input for Ladybug "DC to AC derate factor" component's "annualShading_" input to account for shading of PVsurface.
                       -
                       In percent(%).
        annalysisPts: Each vertex of the inputted _analysisGeometry for which a separate shading analysis was conducted.
                      -
                      Connect this output to a Grasshopper's "Point" parameter in order to preview the "annalysisPts" geometry in the Rhino scene.
        sunWindowCenPt: The center point of the "sunWindowCrvs" and "sunWindowMesh" geometry. It is calculated for analysisGeometry area centroid.
                        Use this point to move "sunWindowCrvs" and "sunWindowMesh" geometry around in the Rhino scene with the grasshopper's "Move" component.
                        -
                        Connect this output to a Grasshopper's "Point" parameter in order to preview the "sunWindowCenPt" point in the Rhino scene.
        sunWindowCrvs: Geometry of the sun window based on 3D polar sun path diagram. Perpendical curves represent solar time hours. Horizontal arc curves represent sun paths for: 21st December, 21st November/January, 21st October/February, 21st September/March, 21st August/April, 21st July/May, 21st June.
                       The whole sunWindowCrvs geometry output is calculated for analysisGeometry area centroid.
        sunWindowMesh: Sun window mesh based on 3D polar sun path diagram. It is calculated for analysisGeometry area centroid.
                       Black areas represent 100% shaded portions of the sun window (of both active and inactive quadrants). Darker green and green areas represent partially shaded portions from the coniferous and deciduous trees, respectively.
                       -
                       It is calculated ONLY if data is supplied to the "ACenergyPerHour_" input".
        legend: A legend of the sunWindowMesh. Connect this output to a Grasshopper's "Geo" parameter in order to preview the legend separately in the Rhino scene.  
        legendBasePt: Legend base point, which can be used to move the "legend" geometry with grasshopper's "Move" component.
                      -
                      Connect this output to a Grasshopper's "Point" parameter in order to preview the "annalysisPts" geometry in the Rhino scene.
        quadrantCentroids: Centroid for each sun window active quadrant above the horizon.
                           -
                           Use grasshopper's "Text tag" component to visualize them.
        quadrantShadingPercents: Shadinging percent per each sun window active quadrant above the horizon. Active quadrants with less than 0.01% are neglected.
                                 -
                                 Use grasshopper's "Text tag" component to visualize them.
        quadrantACenergyPercents: AC energy percent per each sun window active quadrant above the horizon.
                                  -
                                  Use grasshopper's "Text tag" component to visualize them.
        hoursPositions: Solar time hour point positions.
                        -
                        Use grasshopper's "Text tag" component to visualize them.
        hours: Solar time hour strings.
               -
               Use grasshopper's "Text tag" component to visualize them.
"""

ghenv.Component.Name = "Ladybug_Sunpath Shading"
ghenv.Component.NickName = "SunpathShading"
ghenv.Component.Message = 'VER 0.0.62\nMAY_09_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.61\nDEC_05_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import Grasshopper.DataTree as ghdt
import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System
import Rhino
import math
import time


def getEpwData(epwFile):
    
    if epwFile:
        try:
            # location data
            locationName, latitude, longitude, timeZone, elevation, locationString = lb_preparation.epwLocation(epwFile)
            # weather data
            weatherData = lb_preparation.epwDataReader(epwFile, locationName)
            dryBulbTemperature, dewPointTemperature, relativeHumidity, windSpeed, windDirection, directNormalRadiation, diffuseHorizontalRadiation, globalHorizontalRadiation, directNormalIlluminance, diffuseHorizontalIlluminance, globalHorizontalIlluminance, totalSkyCover, liquidPrecipitationDepth, barometricPressure, modelYear = weatherData
            
            dryBulbTemperatureData = dryBulbTemperature[7:]
            directNormalRadiationData = directNormalRadiation[7:]
            diffuseHorizontalRadiationData = diffuseHorizontalRadiation[7:]
            yearsHOY = modelYear[7:]
            
            validEpwData = True
            printMsg = "ok"
            
            return locationName, float(latitude), float(longitude), float(timeZone), dryBulbTemperatureData, directNormalRadiationData, diffuseHorizontalRadiationData, yearsHOY, validEpwData, printMsg
        
        except Exception, e:
            # something is wrong with "_epwFile" input
            locationName = latitude = longitude = timeZone = dryBulbTemperatureData = directNormalRadiationData = diffuseHorizontalRadiationData = yearsHOY = None
            validEpwData = False
            printMsg = "Something is wrong with \"_epwFile\" input."
    else:
        locationName = latitude = longitude = timeZone = dryBulbTemperatureData = directNormalRadiationData = diffuseHorizontalRadiationData = yearsHOY = None
        validEpwData = False
        printMsg = "Please supply .epw file path to \"_epwFile\" input"
    
    return locationName, latitude, longitude, timeZone, dryBulbTemperatureData, directNormalRadiationData, diffuseHorizontalRadiationData, yearsHOY, validEpwData, printMsg


def meshingGeometry(geometryList):
    # mesh the "context_", "coniferousTrees_", "deciduousTrees_" objects
    validContext = 1
    geometryListFiltered = [id for id in geometryList if id != None]
    if len(geometryListFiltered) > 0:
        meshParam = Rhino.Geometry.MeshingParameters()
        meshParam.MinimumEdgeLength = 0.0001
        meshParam.SimplePlanes = True
        joinedMesh = Rhino.Geometry.Mesh()
        for id in geometryListFiltered:
            obj = rs.coercegeometry(id)
            if (isinstance(obj, Rhino.Geometry.Mesh) == False):
                if (isinstance(obj, Rhino.Geometry.Point) == False):  # exlude the points if inputted into "context_"
                    meshL = Rhino.Geometry.Mesh.CreateFromBrep(obj, meshParam)
                    for mesh in meshL:
                        joinedMesh.Append(mesh)
            else:
                joinedMesh.Append(obj)
    else:
        joinedMesh = Rhino.Geometry.Mesh()
        validContext = 0
    
    return joinedMesh, validContext


def checkInputData(analysisGeometry, ACenergyPerHour, context, coniferousTrees, deciduousTrees, coniferousAllyearIndex, deciduousInleafIndex, deciduousLeaflessIndex, leaflessPeriod, dryBulbTemperatureData, albedo, latitude, north, outputGeometryIndex, scale, hoursPositionScale, precision, legendPar):
    
    pathsAnalysisGeometry = analysisGeometry.Paths
    analysisGeometryBranchesLists = analysisGeometry.Branches
    pathsACenergyPerHour = ACenergyPerHour.Paths
    ACenergyPerHourBranchesLists = ACenergyPerHour.Branches
    
    if len(pathsACenergyPerHour) > 0:  # data inputted into ACenergyPerHour_
        if len(pathsAnalysisGeometry) != len(pathsACenergyPerHour):
            srfCornerPtsLL = srfCentroidL = srfAreaL = srfTiltDL = correctedSrfAzimuthDL = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourDataLL = northRad = northVec = albedoL = outputGeometryIndex = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = None
            validInputData = False
            printMsg = "Tree structure of data tree inputted in  \"_analysisGeometry\" and  \"ACenergyPerHour_\" are not equal."
            return pathsAnalysisGeometry, srfCornerPtsLL, srfCentroidL, srfAreaL, srfTiltDL, correctedSrfAzimuthDL, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourDataLL, northRad, northVec, albedoL, outputGeometryIndex, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
    
    if (north == None):
        northRad = 0  # default, in radians
        northVec = Rhino.Geometry.Vector3d(0,1,0)
    else:
        try:  # check if it's a number
            north = float(north)
            if north < 0 or north > 360:
                srfCornerPtsLL = srfCentroidL = srfAreaL = srfTiltDL = correctedSrfAzimuthDL = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourDataLL = northRad = northVec = albedoL = outputGeometryIndex = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = None
                validInputData = False
                printMsg = "Please input north angle value from 0 to 360."
                return pathsAnalysisGeometry, srfCornerPtsLL, srfCentroidL, srfAreaL, srfTiltDL, correctedSrfAzimuthDL, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourDataLL, northRad, northVec, albedoL, outputGeometryIndex, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
        except Exception, e:  # check if it's a vector
            north.Unitize()
        
        northRad, northVec = lb_photovoltaics.angle2northClockwise(north)
    
    srfCornerPtsLL = []
    srfCentroidL = []
    srfAreaL = []
    srfTiltDL = []
    correctedSrfAzimuthDL = []
    ACenergyPerHourDataLL = []
    selfShadingAnalysisGeometry = []
    unitConversionFactor = lb_preparation.checkUnits()
    
    for branchIndex,branchList in enumerate(analysisGeometryBranchesLists):  # all branches have a single item in its list
        if len(branchList) > 0:  # branch list is not empty
            id = list(branchList)[0]
            obj = rs.coercegeometry(id)
            # input is a point
            if isinstance(obj, Rhino.Geometry.Point):
                analysisGeometryInputType = "point"
                srfCornerPts = [obj.Location]
                srfCentroid = obj.Location
                srfArea = 0  # dummy srfArea
                srfTiltD = 0
                correctedSrfAzimuthD = 180
            # input is brep
            elif isinstance(obj, Rhino.Geometry.Brep):
                selfShadingAnalysisGeometry.append(obj)
                analysisGeometryInputType = "brep"  # Sunpath shading allows only "brep" _analysisGeometry inputs
                facesCount = obj.Faces.Count
                if facesCount > 1:
                    # inputted polysurface
                    srfCornerPts = []
                    srfCentroid = []
                    srfArea = 0  # dummy srfArea
                    srfTiltD = 0  # dummy srfArea
                    correctedSrfAzimuthD = 180
                    printMsg = "One or more of the breps you supplied to \"_analysisGeometry\" is a polysurface. Please supply a surface instead."
                    level = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
                    print printMsg
                else:
                    # inputted brep with a single surface
                    srfCornerPts = obj.DuplicateVertices()
                    srfCentroid = Rhino.Geometry.AreaMassProperties.Compute(obj).Centroid
                    srfArea = Rhino.Geometry.AreaMassProperties.Compute(obj).Area * unitConversionFactor**2  # in m2, for printOutput() only
                    analysisGeometryTiltAngle = None
                    analysisGeometryAzimuthAngle = None
                    srfAzimuthD, surfaceTiltDCalculated = lb_photovoltaics.srfAzimuthAngle(analysisGeometryAzimuthAngle, analysisGeometryInputType, obj, latitude)
                    correctedSrfAzimuthD, northDeg, validNorth, printMsg = lb_photovoltaics.correctSrfAzimuthDforNorth(north, srfAzimuthD)
                    srfTiltD = lb_photovoltaics.srfTiltAngle(analysisGeometryTiltAngle, surfaceTiltDCalculated, analysisGeometryInputType, obj, latitude)
            else:
                # any other geometry than surface and point
                srfCornerPts = []
                srfCentroid = []
                srfArea = 0  # dummy srfArea
                srfTiltD = 0  # dummy srfArea
                correctedSrfAzimuthD = 180
                printMsg = "One or more of the geometry you supplied to \"_analysisGeometry\" is not a surface nor a point, which is what \"_analysisGeometry\" requires as an input."
                level = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(level, printMsg)
                print printMsg
        
        elif len(branchList) == 0:  # empty branches
            srfCornerPts = []
        
        try:
            ACenergyPerHour = list(ACenergyPerHourBranchesLists[branchIndex])
            if (len(ACenergyPerHour) != 0) and (ACenergyPerHour[0] is not ""):
                if len(ACenergyPerHour) == 8767:
                    ACenergyPerHourData = ACenergyPerHour[7:]
                elif len(ACenergyPerHour) == 8760:
                    ACenergyPerHourData = ACenergyPerHour
                if (ACenergyPerHour[0] is None) or (sum(ACenergyPerHourData) == 0):
                    ACenergyPerHourData = []  # dummy value
                    srfCornerPts = []  # instead of breaking the function with validInputData = False
                    if (branchIndex == outputGeometryIndex):
                        printMsg = "One or more of the inputted \"ACenergyPerHour_\" lists does not generate any AC energy (annual output = 0 kWh).\nIts shading and geometry can not be calculated."
                    else:
                        printMsg = "One or more of the inputted \"ACenergyPerHour_\" lists does not generate any AC energy (annual output = 0 kWh).\nIts shading can not be calculated."
                    level = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
                    print printMsg
            else:
                ACenergyPerHourData = []
        except:
            ACenergyPerHourData = []
        
        srfCornerPtsLL.append(srfCornerPts)
        srfCentroidL.append(srfCentroid)
        srfAreaL.append(srfArea)
        srfTiltDL.append(srfTiltD)
        correctedSrfAzimuthDL.append(correctedSrfAzimuthD)
        ACenergyPerHourDataLL.append(ACenergyPerHourData)
    
    contextMeshes = []
    # context
    joinedMesh1, validContext1 = meshingGeometry(context + selfShadingAnalysisGeometry)
    contextMeshes.append(joinedMesh1)
    # coniferousTrees
    joinedMesh2, validContext2 = meshingGeometry(coniferousTrees)
    contextMeshes.append(joinedMesh2)
    if validContext2 == 1: validContext2 = 2
    # deciduousTrees
    joinedMesh3, validContext3 = meshingGeometry(deciduousTrees)
    contextMeshes.append(joinedMesh3)
    if validContext3 == 1: validContext3 = 3
    validContextCategories = [index for index in [validContext1, validContext2, validContext3] if index > 0]
    
    # default transmission indices based on: Planning and Installing Photovoltaic Systems: A Guide for Installers, Architects and Engineers,
    # Deutsche Gesellschaft Für Sonnenenergie (Dgs), Dec 2007.
    if (coniferousAllyearIndex == None) or (coniferousAllyearIndex < 0) or (coniferousAllyearIndex > 1):
        coniferousAllyearIndex = 0.30
    if (deciduousInleafIndex == None) or (deciduousInleafIndex < 0) or (deciduousInleafIndex > 1):
        deciduousInleafIndex = 0.23
    if (deciduousLeaflessIndex == None) or (deciduousLeaflessIndex < 0) or (deciduousLeaflessIndex > 1):
        deciduousLeaflessIndex = 0.64
    treesTransmissionIndices = [coniferousAllyearIndex, [deciduousLeaflessIndex, deciduousInleafIndex]]
    
    if (len(leaflessPeriod)!=0) and (leaflessPeriod[0]!=None):
        leaflessHOYs, months, days = lb_preparation.getHOYsBasedOnPeriod(leaflessPeriod, 1)
        leaflessStartHOY = leaflessHOYs[0]
        leaflessEndHOY = leaflessHOYs[-1]
        if leaflessStartHOY == leaflessEndHOY:
            srfCornerPtsLL = srfCentroidL = srfAreaL = srfTiltDL = correctedSrfAzimuthDL = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourDataLL = northRad = northVec = albedoL = outputGeometryIndex = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = None
            validWeatherData = False
            printMsg = "Start and End time of your \"leaflessPeriod_\" input are the same. Please input a valid \"leaflessPeriod_\" input."
            return pathsAnalysisGeometry, srfCornerPtsLL, srfCentroidL, srfAreaL, srfTiltDL, correctedSrfAzimuthDL, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourDataLL, northRad, northVec, albedoL, outputGeometryIndex, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
    else:
        # nothing inputted in "leaflessPeriod_"
        if latitude > 0:  # northern hemisphere
            leaflessStartHOY = 6336
            leaflessEndHOY = 1920
            leaflessPeriod = [(9, 22, 1), (3, 21, 24)]
            
        elif latitude < 0:  # southern hemisphere
            leaflessStartHOY = 1921
            leaflessEndHOY = 6337
            leaflessPeriod = [(3, 22, 1), (9, 21, 24)]
    
    if (len(albedo) == 0) or (albedo[0] is ""):
        albedoL = lb_photovoltaics.calculateAlbedo(dryBulbTemperatureData)  # default
    elif (len(albedo) == 8767):
        albedoL = albedo[7:]
    elif (len(albedo) == 8760):
        albedoL = albedo
    else:
        srfCornerPtsLL = srfCentroidL = srfAreaL = srfTiltDL = correctedSrfAzimuthDL = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourDataLL = northRad = northVec = albedoL = outputGeometryIndex = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = None
        validInputData = False
        printMsg = "Something is wrong with your \"albedo_\" list input.\n\"albedo_\" input accepts a list of 8767 (with header) or 8760 (without the header) abledo values."
        
        return pathsAnalysisGeometry, srfCornerPtsLL, srfCentroidL, srfAreaL, srfTiltDL, correctedSrfAzimuthDL, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourDataLL, northRad, northVec, albedoL, outputGeometryIndex, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
    
    if (outputGeometryIndex == None) or (outputGeometryIndex < 0):
        outputGeometryIndex = 0  # default
    else:
        if (outputGeometryIndex + 1) > len(pathsAnalysisGeometry):
            srfCornerPtsLL = srfCentroidL = srfAreaL = srfTiltDL = correctedSrfAzimuthDL = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourDataLL = northRad = northVec = albedoL = outputGeometryIndex = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = None
            validInputData = False
            printMsg = "The index number inputted into \"outputGeometryIndex_\" is higher than number of inputted objects into \"outputGeometryIndex_\" (%s). Please choose a lower  \"outputGeometryIndex_\" index than %s." % (len(pathsACenergyPerHour), len(pathsACenergyPerHour))
            return pathsAnalysisGeometry, srfCornerPtsLL, srfCentroidL, srfAreaL, srfTiltDL, correctedSrfAzimuthDL, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourDataLL, northRad, northVec, albedoL, outputGeometryIndex, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
    
    if (scale == None) or (scale < 0):
        scale = 1 * 200  # default
    else:
        scale = scale * 200
    
    if (hoursPositionScale == None) or (hoursPositionScale < 0):
        hoursPositionScale = 1 * 12  #default
    else:
        hoursPositionScale = hoursPositionScale * 12
    
    if (precision == None) or (precision < 2) or (precision > 100):
        precision = 2  # default
    
    if (len(legendPar) == 0):
        lowB = None; highB = None; numSeg = None; customColors = [System.Drawing.Color.White, System.Drawing.Color.FromArgb(255,220,0), System.Drawing.Color.Red]; legendBasePoint = None; legendScale = None; legendFont = None; legendFontSize = None; legendBold = None; decimalPlaces = 2; removeLessThan = False
        legendPar = [lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan]
    
    monthsHOY = [1 for i in range(744)] + [2 for i in range(672)] + [3 for i in range(744)] + [4 for i in range(720)] + [5 for i in range(744)] + [6 for i in range(720)] + [7 for i in range(744)] + [8 for i in range(744)] + [9 for i in range(720)] + [10 for i in range(744)] + [11 for i in range(720)] + [12 for i in range(744)]
    
    numberOfDaysMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
    daysHOY = []
    day = 1
    for i,item in enumerate(numberOfDaysMonth):
        for k in range(item):
            for g in range(24):
                daysHOY.append(day)
            day += 1
        day = 1
    
    hoursHOY = []
    hour = 1
    for i in range(365):
        for k in range(24):
            hoursHOY.append(hour)
            hour += 1
        hour = 1
    
    validInputData = True
    printMsg = "ok"
    
    return pathsAnalysisGeometry, srfCornerPtsLL, srfCentroidL, srfAreaL, srfTiltDL, correctedSrfAzimuthDL, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourDataLL, northRad, northVec, albedoL, outputGeometryIndex, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg


def sunWindowCurves(latitude, northRad, northVec, testPt, scale, hoursPositionScale):
    
    # sunPath curves
    lb_sunpath.initTheClass(float(latitude), northRad, testPt, scale, longitude, timeZone)
    
    months = range(1,13); d = 21; hours = range(0,25)
    sunPsolarTimeL = []
    for h in range(len(hours)):
        subListPts = []
        for m in range(len(months)):
            lb_sunpath.solInitOutput(m, d, h)
            sunPt = lb_sunpath.sunPosPt()[2]
            subListPts.append(sunPt)
        hourlyPtsSolarTime = [subListPts[0], (subListPts[1]+subListPts[11])/2, (subListPts[2]+subListPts[10])/2, (subListPts[3]+subListPts[9])/2, (subListPts[4]+subListPts[8])/2, (subListPts[5]+subListPts[7])/2, subListPts[6]]
        sunPsolarTimeL.append(hourlyPtsSolarTime)
    
    sunPsolarTimeLFlattenFlipMatrix = [subList[i] for i in range(len(sunPsolarTimeL[0])) for subList in sunPsolarTimeL]
    
    # compass curves
    textSize = scale/25; legendBold = True
    compassCrvs, compassTextPts, compassText = lb_visualization.compassCircle(testPt, northVec, scale, range(0, 360, 30), textSize)
    numberCrvs = lb_visualization.text2srf(compassText, compassTextPts, "Times New Romans", textSize, legendBold)
    compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
    outerBaseCrv = Rhino.Geometry.Circle(testPt, 1.08*scale).ToNurbsCurve()
    compassCrvs = compassCrvs + [outerBaseCrv]
    
    knotStyle = Rhino.Geometry.CurveKnotStyle.UniformPeriodic
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    cuttingPlane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(testPt),Rhino.Geometry.Vector3d(0,0,1))
    
    # solar time hour curves
    solarTimeHourCrvs = []
    for subList in sunPsolarTimeL:
        solarTimeHourCrv = Rhino.Geometry.Curve.CreateInterpolatedCurve(subList, 3, knotStyle)
        intersectionEvents = Rhino.Geometry.Intersect.Intersection.CurvePlane(solarTimeHourCrv, cuttingPlane, tol)
        if intersectionEvents:  # intersection between solar hourly curves and cuttingPlane
            for intersectionEvent in intersectionEvents:
                splittedCrvs = solarTimeHourCrv.Split(intersectionEvent.ParameterA)
                if latitude > 0:
                    solarTimeHourCrvs.append(splittedCrvs[1])
                elif latitude < 0:
                    solarTimeHourCrvs.append(splittedCrvs[0])
        else:  # no intersection between solar hourly curves and cuttingPlane
            if testPt.Z <= solarTimeHourCrv.PointAtStart.Z:
                solarTimeHourCrvs.append(solarTimeHourCrv)
    
    # two month crvs
    twoMonthCrvPts = []
    for i in range(len(sunPsolarTimeL[0])):
        twoMonthCrvPts.append([])
    for subList in sunPsolarTimeL:
        for i in range(len(subList)):
            twoMonthCrvPts[i].append(subList[i])
    
    sunAboveHorizon = False
    twoMonthCrvsCutted = []
    for subList2 in twoMonthCrvPts:
        twoMonthCrv = Rhino.Geometry.Curve.CreateInterpolatedCurve(subList2, 3, knotStyle)
        intersectionEvents2 = Rhino.Geometry.Intersect.Intersection.CurvePlane(twoMonthCrv, cuttingPlane, tol)
        if intersectionEvents2 != None: # one or two intersections with cuttingPlane found
            if len(intersectionEvents2) == 2:
                domain = Rhino.Geometry.Interval(intersectionEvents2[0].ParameterA, intersectionEvents2[1].ParameterA)
                splittedCrvs2 = twoMonthCrv.Trim(domain)
                twoMonthCrvsCutted.append(splittedCrvs2)
            elif len(intersectionEvents2) == 1:
                splittedCrvs2 = twoMonthCrv.Split(intersectionEvents2[0].ParameterA)
                twoMonthCrvsCutted.append(splittedCrvs2[0])
        else: # no intersection with cuttingPlane. Check if twoMonthCrv is above the cuttingPlane
            if testPt.Z <= twoMonthCrv.PointAtStart.Z:
                twoMonthCrvsCutted.append(twoMonthCrv)
                sunAboveHorizon = True
    
    # final sunWindowCrvs:
    sunWindowCrvs = solarTimeHourCrvs + twoMonthCrvsCutted + compassCrvs
    
    # hours and hours positions
    hoursPositionsPts = []
    hoursStrings = range(1,25)
    # use Jun 21 sun positions:
    if latitude >= 0:
        hoursPositionsPts = sunPsolarTimeLFlattenFlipMatrix[151:]
    # use Dec 21 sun positions:
    elif latitude < 0:
        hoursPositionsPts = sunPsolarTimeLFlattenFlipMatrix[1:25]
    
    averageHourPt = []
    startPt = Rhino.Geometry.Point3d(0,0,0)
    for pt in hoursPositionsPts:
        startPt = startPt + pt
    averageHourPt.append(startPt)
    centerHourPt = averageHourPt[0]/24
    
    # filtering all hours bellow testPt.Z
    hoursPositionsPtsMovedFiltered = []
    hoursStringsFiltered = []
    for i,pt in enumerate(hoursPositionsPts):
        if pt.Z >= testPt.Z:
            centerHourToCircleHourVec = Rhino.Geometry.Vector3d(pt-centerHourPt)
            centerHourToCircleHourVec.Unitize()
            centerHourToCircleHourVec = centerHourToCircleHourVec * hoursPositionScale
            hoursPositionsPtsMovedFiltered.append(Rhino.Geometry.Point3d(centerHourToCircleHourVec) + hoursPositionsPts[i])
            hoursStringsFiltered.append(hoursStrings[i])
    
    return sunWindowCrvs, outerBaseCrv, solarTimeHourCrvs, twoMonthCrvsCutted, sunAboveHorizon, sunPsolarTimeLFlattenFlipMatrix, hoursPositionsPtsMovedFiltered, hoursStringsFiltered


def ACenergyQuadrantPercents(ACenergyPerHourData):
    # percentage of annual AC output per solar window quadrant
    sunPsolarTimeL = [[] for i in range(25)]
    startSolarTimeHour = 1
    endSolarTimeHour = 24
    
    numberOfDaysInMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
    PacPerHourPerTwoMonthStrip = [] # six two month strips
    for i in range(6):
        subList = []
        for k in range(24):
            subList.append([])
        PacPerHourPerTwoMonthStrip.append(subList)
    
    hoy = 1
    for numOfDays in numberOfDaysInMonth:
        for i in range(numOfDays):
            for k in range(1,25):
                if ((hoy >= 1) and (hoy <= 504)) or ((hoy >= 7801) and (hoy <= 8760)):
                    twoMonthIndex = 0
                elif ((hoy >= 505) and (hoy <= 1248)) or ((hoy >= 7057) and (hoy <= 7800)):
                    twoMonthIndex = 1
                elif ((hoy >= 1249) and (hoy <= 1920)) or ((hoy >= 6337) and (hoy <= 7056)):
                    twoMonthIndex = 2
                elif ((hoy >= 1921) and (hoy <= 2664)) or ((hoy >= 5593) and (hoy <= 6336)):
                    twoMonthIndex = 3
                elif ((hoy >= 2665) and (hoy <= 3384)) or ((hoy >= 4849) and (hoy <= 5592)):
                    twoMonthIndex = 4
                elif ((hoy >= 3385) and (hoy <= 4128)) or ((hoy >= 4129) and (hoy <= 4848)):
                    twoMonthIndex = 5
                
                if k >= startSolarTimeHour and k <= endSolarTimeHour:
                    hourIndex = k-startSolarTimeHour
                    Epoa = ACenergyPerHourData[hoy-1]
                    PacPerHourPerTwoMonthStrip[twoMonthIndex][hourIndex].append(Epoa)
                hoy += 1
    
    eachQuadrantPac = []  # each quadrant sum Pac, flattened
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    for twoMonthStrip in PacPerHourPerTwoMonthStrip:
        quadrantSum = []
        for PacPerHour in twoMonthStrip:
            quadrantSum.append(sum(PacPerHour))
        # filtering tolerance values
        if (abs(0 - sum(quadrantSum)) < tol):
            quadrantSum = [0]
        eachQuadrantPac.extend(quadrantSum)
    
    sunWindowACenergySum = sum(eachQuadrantPac)  # instead of: ACenergyPerYear = sum(ACenergyPerHourData), use: sunWindowACenergySum
    
    eachQuadrantACpercent = [(Pac/sunWindowACenergySum)*100 if sunWindowACenergySum > 0 else 0 for Pac in eachQuadrantPac]
    
    return eachQuadrantACpercent


def legendGeometry(legendPar, scale, testPt, eachQuadrantACpercent, validContextCategories):
    outerBaseCrv = Rhino.Geometry.Circle(testPt, 1.08*scale).ToNurbsCurve()
    
    # legend 1
    lowB, highB, numSeg, customColors, legend1BasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    lb_visualization.calculateBB([outerBaseCrv])
    if legend1BasePoint == None:
        legend1BasePoint = lb_visualization.BoundingBoxPar[0]
    # generate the legend
    legendSrfs, legendText, legendTextSrfs, textPt, textSize = lb_visualization.createLegend(eachQuadrantACpercent, lowB, highB, numSeg, "Annual AC energy percentage", lb_visualization.BoundingBoxPar, legend1BasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    # generate legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    legend1 = [legendSrfs] + lb_preparation.flattenList(legendTextSrfs)
    
    
    # legend 2
    BBYlength = 432*(scale/200)
    legendWidth = BBYlength/10*legendScale
    legendFontSize = (legendWidth/3) * legendScale
    titleBasePt = lb_visualization.BoundingBoxPar[5]
    legend2BasePoint = Rhino.Geometry.Point3d(titleBasePt.X, titleBasePt.Y, titleBasePt.Z)
    legend2MeshStartPt = Rhino.Geometry.Point3d(legend2BasePoint.X-legendWidth, legend2BasePoint.Y, legend2BasePoint.Z)
    
    # inputted context and/or context coniferousTrees and/or deciduousTrees
    if len(validContextCategories) > 0:
        legend2MeshPts = []
        step = legendWidth
        for i in range(len(validContextCategories)+1):
            for k in range(2):
                pt = Rhino.Geometry.Point3d(legend2MeshStartPt.X -k*step, legend2MeshStartPt.Y +i*step, legend2MeshStartPt.Z)
                legend2MeshPts.append(pt)
        
        legend2Mesh = lb_meshpreparation.meshFromPoints(len(validContextCategories)+1, 2, legend2MeshPts)
        allColors = ["dummy", System.Drawing.Color.Black, System.Drawing.Color.FromArgb(0,60,0), System.Drawing.Color.FromArgb(0,120,0)]
        newColors = [allColors[index] for index in validContextCategories]
        legend2MeshColored = lb_visualization.colorMesh(newColors, [legend2Mesh])
        
        legend2 = [legend2MeshColored]
        labelText = ["dummy", "context", "coniferous trees", "deciduous trees"]
        for i,index in enumerate(validContextCategories):
            labelOrigin = Rhino.Geometry.Point3d(legend2MeshStartPt.X - (legendWidth + legendFontSize*0.5), legend2MeshStartPt.Y + i*legendWidth, legend2MeshStartPt.Z)
            text = lb_visualization.text2srf([labelText[index]], [labelOrigin], legendFont, legendFontSize, legendBold, None, 2)[0]
            legend2.extend(text)
        labelTitleOrigin = Rhino.Geometry.Point3d(legend2MeshStartPt.X - (legendWidth + legendFontSize*0.5), legend2MeshStartPt.Y + (i+1)*legendWidth, legend2MeshStartPt.Z)
        textTitle = lb_visualization.text2srf(["Shading from:"], [labelTitleOrigin], legendFont, legendFontSize, legendBold, None, 2)[0]
        legend2.extend(textTitle)
    else:
        # nothing inputted in context and/or context coniferousTrees and/or deciduousTrees
        legend2 = []
    
    legend = legend1 + legend2
    
    if len(validContextCategories) > 0:
        legendBasePoint = (legend1BasePoint + legend2BasePoint)/2
    else:
        legendBasePoint = legend1BasePoint
    
    return legend, lowB, highB, customColors, legendBasePoint


def noLeavesPeriod(criteria, latitude, index, leaflessStartHOY=None, leaflessEndHOY=None):
    if criteria == "perQuadrant":
        if latitude > 0:  # northern hemisphere
            if index < 72:
                seasonIndex = 0  # winter/autumn
            elif index >= 72:
                seasonIndex = 1  # spring/summer
        elif latitude < 0:  # southern hemisphere
            if index < 72:
                seasonIndex = 1  # spring/summer
            elif index >= 72:
                seasonIndex = 0  # winter/autumn
    elif criteria == "perHoy":
        if leaflessStartHOY < leaflessEndHOY:
            if (index >= leaflessStartHOY) and (index <= leaflessEndHOY):
                seasonIndex = 0  # leafless period
            else:
                seasonIndex = 1  # inleaf period
        elif leaflessStartHOY > leaflessEndHOY:
            if (index >= leaflessStartHOY) or (index <= leaflessEndHOY):
                seasonIndex = 0  # leafless period
            else:
                seasonIndex = 1  # inleaf period
    
    return seasonIndex


def shadingAndQuadrantPercentages(testPt, createSunWindowMesh, contextMeshes, treesTransmissionIndices, outerBaseCrv, sunPsolarTimeLFlattenFlipMatrix, solarTimeHourCrvs, twoMonthCrvsCutted, sunAboveHorizon, eachQuadrantACpercent, colors, precision):
    
    # lifting up the testPt due to MeshRay intersection
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    testPtLifted = Rhino.Geometry.Point3d(testPt.X, testPt.Y, testPt.Z+tol)
    
    # add testPt plane horizontal mesh to contextMeshes
    meshParam = Rhino.Geometry.MeshingParameters()
    outerBaseMesh = Rhino.Geometry.Mesh.CreateFromPlanarBoundary(outerBaseCrv, meshParam)
    contextAndOuterBaseMesh = Rhino.Geometry.Mesh()
    contextAndOuterBaseMesh.Append(contextMeshes[0])
    contextAndOuterBaseMesh.Append(outerBaseMesh)
    contextAndOuterBaseMeshList = [contextAndOuterBaseMesh, contextMeshes[1], contextMeshes[2]]
    
    ptCloudPts = []
    ptCloudColors = []
    quadrantCentroids = []
    newQuadrantsACpercents = []
    treesTransmissionIndicesAllQuadrants = []
    Sep21toMar21_Mar21toSep21newACpercent = [[],[]]
    
    u = 7
    v = 25
    index = 0
    reparematizedDomain = Rhino.Geometry.Interval(0,1)
    for i in range(1,u):
        for k in range(1,v):
            brep = Rhino.Geometry.Brep.CreateFromCornerPoints(sunPsolarTimeLFlattenFlipMatrix[k-1+(i-1)*v], sunPsolarTimeLFlattenFlipMatrix[k-1+i*v], sunPsolarTimeLFlattenFlipMatrix[k-1+i*v+1], sunPsolarTimeLFlattenFlipMatrix[k-1+(i-1)*v+1], tol)
            srf = brep.Faces[0]
            srf.SetDomain(0, reparematizedDomain)
            srf.SetDomain(1, reparematizedDomain)
            srfCentroid = srf.PointAt(0.5, 0.5)
            step = 1/(precision-1)
            quadrantCornerPts = [(sunPsolarTimeLFlattenFlipMatrix[k-1+(i-1)*v].Z, 0), (sunPsolarTimeLFlattenFlipMatrix[k-1+i*v].Z, 1), (sunPsolarTimeLFlattenFlipMatrix[k-1+i*v+1].Z, 2), (sunPsolarTimeLFlattenFlipMatrix[k-1+(i-1)*v+1].Z, 3)]
            quadrantCornerPts.sort()
            highestQuadrantPtZ = quadrantCornerPts[-1][0]
            
            treesTransmissionIndicesPerQuadrant = []
            if highestQuadrantPtZ > (testPtLifted.Z):  # filter1: cull quadrants surfaces (and points on it) bellow the following height
                for uPt in range(0,precision):
                    for vPt in range(0,precision):
                        skyDomePt = srf.PointAt(step*uPt,step*vPt)
                        rayVector = skyDomePt-testPtLifted
                        ray = Rhino.Geometry.Ray3d(testPtLifted, rayVector)
                        if rayVector.Z >= 0:  # filter2 cull all rays bellow analysis analysisPt height
                            ptCloudPts.append(skyDomePt)
                            for meshIndex,mesh in enumerate(contextAndOuterBaseMeshList):
                                intersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(mesh,ray)
                                # ray hitted something
                                if intersectParam >= 0:
                                    seasonIndex = noLeavesPeriod("perQuadrant", latitude, index)
                                    if meshIndex == 0:  # context mesh hitted
                                        treesTransmissionIndex = 0
                                        color = System.Drawing.Color.Black
                                    elif meshIndex == 1:  # coniferousTrees mesh hitted
                                        treesTransmissionIndex = treesTransmissionIndices[0]
                                        
                                        intersectParamConifDecid = Rhino.Geometry.Intersect.Intersection.MeshRay(contextAndOuterBaseMeshList[2],ray)  # ray penetrates both coniferous and deciduous tree, check which one is closer
                                        if intersectParamConifDecid >= 0:
                                            if intersectParam > intersectParamConifDecid:  # coniferous tree further away than deciduous tree
                                                color = System.Drawing.Color.FromArgb(0,60,0)
                                            else:  # deciduous tree further away (or equally distant) than coniferous tree
                                                color = System.Drawing.Color.FromArgb(0,120,0)
                                        else: # it only hits the coniferousTrees mesh
                                            color = System.Drawing.Color.FromArgb(0,60,0)
                                    elif meshIndex == 2:  # deciduousTrees mesh hitted
                                        treesTransmissionIndex = treesTransmissionIndices[1][seasonIndex]
                                        color = System.Drawing.Color.FromArgb(0,120,0)
                                    
                                    treesTransmissionIndicesPerQuadrant.append(treesTransmissionIndex)
                                    ptCloudColors.append(color)
                                    break
                            # no hitting, the ray only hits the sky dome
                            else:
                                color = colors[index]
                                ptCloudColors.append(color)
                                if eachQuadrantACpercent[index] > 0.0:
                                    treesTransmissionIndicesPerQuadrant.append(1)
                
                newQuadrantACpercent = (len(treesTransmissionIndicesPerQuadrant)*eachQuadrantACpercent[index]/(precision*precision))
                newQuadrantsACpercents.append(newQuadrantACpercent)
                treesTransmissionIndicesAllQuadrants.append(treesTransmissionIndicesPerQuadrant)
                quadrantCentroids.append(srfCentroid)
                if index < 72:
                    Sep21toMar21_Mar21toSep21newACpercent[0].append(newQuadrantACpercent)
                    Mar22StartIndex = len(newQuadrantsACpercents)+1
                elif index >= 72:
                    Sep21toMar21_Mar21toSep21newACpercent[1].append(newQuadrantACpercent)
            index += 1
    
    newUnweightedACpercent = sum(newQuadrantsACpercents)/len(newQuadrantsACpercents)
    newUnweightedQuadrantsACpercents = [newUnweightedACpercent for i in range(len(newQuadrantsACpercents))]
    
    quadrantsSumACPercentsUnshaded = []
    quadrantsSumUnweightedACPercentsUnshaded = []
    Sep21toMar21_Mar21toSep21ACPercentsUnshaded = [[],[]]
    quadrantsSumShadingPercents = []
    for i,treesTransIndicesPerQuadrant in enumerate(treesTransmissionIndicesAllQuadrants):
        quadrantSumACPercentUnshaded = 0
        quadrantSumUnweightedACPercentUnshaded = 0
        # ACenergyPercents
        for k,treesTransIndex in enumerate(treesTransIndicesPerQuadrant):
            quadrantACPercentUnshaded = 1/(len(treesTransIndicesPerQuadrant))*newQuadrantsACpercents[i]*treesTransIndex
            quadrantSumACPercentUnshaded += quadrantACPercentUnshaded
            quadrantUnweightedACPercentUnshaded = 1/(len(treesTransIndicesPerQuadrant))*newUnweightedQuadrantsACpercents[i]*treesTransIndex
            quadrantSumUnweightedACPercentUnshaded += quadrantUnweightedACPercentUnshaded
        quadrantsSumACPercentsUnshaded.append(quadrantSumACPercentUnshaded)
        quadrantsSumUnweightedACPercentsUnshaded.append(quadrantSumUnweightedACPercentUnshaded)
        if i < Mar22StartIndex:
            Sep21toMar21_Mar21toSep21ACPercentsUnshaded[0].append(quadrantSumACPercentUnshaded)
        elif i >= Mar22StartIndex:
            Sep21toMar21_Mar21toSep21ACPercentsUnshaded[1].append(quadrantSumACPercentUnshaded)
        
        # ShadingPercents
        if newQuadrantsACpercents[i] == 0:
            # to avoid dividing with zero, shading is always 0 if AC quadrant percent is zero
            quadrantsSumShadingPercents.append(0)
        else:
            quadrantsSumShadingPercents.append(100-(quadrantSumACPercentUnshaded/newQuadrantsACpercents[i]*100))
    
    annualShading = 100-(100*sum(quadrantsSumACPercentsUnshaded)/sum(newQuadrantsACpercents))
    Sep21toMar21Shading = 100-(100*sum(Sep21toMar21_Mar21toSep21ACPercentsUnshaded[0])/sum(Sep21toMar21_Mar21toSep21newACpercent[0]))
    Mar21toSep21Shading = 100-(100*sum(Sep21toMar21_Mar21toSep21ACPercentsUnshaded[1])/sum(Sep21toMar21_Mar21toSep21newACpercent[1]))
    unweightedAnnualShading = 100-(100*sum(quadrantsSumUnweightedACPercentsUnshaded)/sum(newUnweightedQuadrantsACpercents))
    
    if (createSunWindowMesh == False):
        return annualShading, unweightedAnnualShading, Sep21toMar21Shading, Mar21toSep21Shading
    else:
        if (outputGeometryIndex != branchIndex):
            #return annualShading, unweightedAnnualShading, Sep21toMar21Shading, Mar21toSep21Shading
            sunWindowShadedAreaPer = quadrantCentroidsFiltered = quadrantShadingPercentRoundedFiltered = quadrantACPercentUnshadedRoundedFiltered = sunWindowMesh = None
            return sunWindowShadedAreaPer, quadrantCentroidsFiltered, quadrantShadingPercentRoundedFiltered, quadrantACPercentUnshadedRoundedFiltered, sunWindowMesh
        else:
            # filtering (and rounding) centroids, acpercents and shading percents (per quadrant) to only those above analysisPt plane
            quadrantCentroidsFiltered = []
            quadrantShadingPercentRoundedFiltered = []
            quadrantACPercentUnshadedRoundedFiltered = []
            for i,ACpercent in enumerate(newQuadrantsACpercents):
                if quadrantCentroids[i].Z >= testPtLifted.Z:  # filter quadrant centroids bellow the analysisPt plane
                    if newQuadrantsACpercents[i] >= 0.01:  # filter < 0.01 unshaded AC quadrant percents
                        roundedACpercent = round(quadrantsSumACPercentsUnshaded[i],1)
                        if roundedACpercent == 0:
                            if quadrantsSumACPercentsUnshaded[i] >= 0.01:
                                # (shaded AC quadrant >= 0.01) and (shaded AC quadrant <= 0.1)
                                roundedACpercent = 0.01
                            else:
                                # (shaded AC quadrant <= 0.01)
                                roundedACpercent = int(roundedACpercent)
                        roundedShadingPercent = int(round(quadrantsSumShadingPercents[i],0))
                        # if (shaded AC quadrant <= 0.01): roundedShadingPercent = 100
                        if roundedACpercent == 0:
                            roundedShadingPercent = 100
                        
                        quadrantCentroidsFiltered.append(quadrantCentroids[i])
                        quadrantACPercentUnshadedRoundedFiltered.append(roundedACpercent)
                        quadrantShadingPercentRoundedFiltered.append(roundedShadingPercent)
            
            # point cloud
            ptcloud = Rhino.Geometry.PointCloud()
            for i in range(len(ptCloudPts)):
                ptcloud.Add(ptCloudPts[i],ptCloudColors[i])
            
            # sun window mesh
            startPt = endPt = Rhino.Geometry.Point3d.Unset
            # closed brep
            if sunAboveHorizon == True:
                sunWindowBrep = Rhino.Geometry.Brep.CreateFromLoftRefit(solarTimeHourCrvs[:-1], startPt, endPt, Rhino.Geometry.LoftType.Normal, True, tol)[0]
            # open brep
            else:
                sunWindowBrep = Rhino.Geometry.Brep.CreateFromLoftRefit(twoMonthCrvsCutted, startPt, endPt, Rhino.Geometry.LoftType.Normal, False, tol)[0]
            sunWindowSrf = sunWindowBrep.Faces[0]
            sunWindowSrf.SetDomain(0, reparematizedDomain)
            sunWindowSrf.SetDomain(1, reparematizedDomain)
            sunWindowMeshPts = []
            sunWindowMeshColors = []
            
            # closed brep
            if sunAboveHorizon == True:
                multiplierU = 16
                multiplierV = 3
            # open brep:
            else:
                multiplierU = 3
                multiplierV = 6
            blackColors = 0
            stepU = 1/((multiplierU*precision)-1)
            stepV = 1/((multiplierV*precision)-1)
            for uPt in range(0,multiplierU*precision):
                for vPt in range(0,multiplierV*precision):
                    sunWindowPt = sunWindowSrf.PointAt(stepU*uPt,stepV*vPt)
                    sunWindowMeshPts.append(sunWindowPt)
                    ptCloundPtIndex = ptcloud.ClosestPoint(sunWindowPt)
                    sunWindowMeshColors.append(ptCloudColors[ptCloundPtIndex])
                    if (ptCloudColors[ptCloundPtIndex] == System.Drawing.Color.Black):
                        blackColors += 1
                    elif (ptCloudColors[ptCloundPtIndex] == System.Drawing.Color.FromArgb(0,60,0)):
                        # coniferous trees
                        blackColors += 1*treesTransmissionIndices[0]
                    elif (ptCloudColors[ptCloundPtIndex] == System.Drawing.Color.FromArgb(0,120,0)):
                        # deciduous trees
                        blackColors += 1*((treesTransmissionIndices[1][0]+treesTransmissionIndices[1][1])/2)
            
            sunWindowMesh = lb_meshpreparation.meshFromPoints(multiplierU*precision, multiplierV*precision, sunWindowMeshPts, sunWindowMeshColors)
            sunWindowShadedAreaPer = round((blackColors/len(sunWindowMeshColors))*100, 2)
            
            return sunWindowShadedAreaPer, quadrantCentroidsFiltered, quadrantShadingPercentRoundedFiltered, quadrantACPercentUnshadedRoundedFiltered, sunWindowMesh


def diffuseShading(testPt, contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, scale, precision):
    
    # lifting up the testPt due to MeshRay intersection
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    testPtLifted = Rhino.Geometry.Point3d(testPt.X, testPt.Y, testPt.Z+tol)
    
    precisionU = precision*5
    precisionV = int(precisionU/3.5)
    
    skyDomeHalfSphere = Rhino.Geometry.Sphere(Rhino.Geometry.Plane(Rhino.Geometry.Point3d(testPtLifted),Rhino.Geometry.Vector3d(0,0,1)),scale)
    splittedSkyDomeDomainUmin, splittedSkyDomeDomainUmax = [0, 2*math.pi]  # sphere diameter
    splittedSkyDomeDomainVmin, splittedSkyDomeDomainVmax = [0, 0.5*math.pi]  # sphere vertical arc
    splittedSkyDomeDomainVmax = 0.9*splittedSkyDomeDomainVmax
    
    stepU = (splittedSkyDomeDomainUmax - splittedSkyDomeDomainUmin)/precisionU
    stepV = (splittedSkyDomeDomainVmax - splittedSkyDomeDomainVmin)/precisionV
    
    hittedRaysIntensities = 0
    for i in range(0,precisionU):
        for k in range(0,precisionV):
            u = splittedSkyDomeDomainUmin + stepU*i
            v = splittedSkyDomeDomainVmin + stepV*k
            skyDomePt = skyDomeHalfSphere.PointAt(u,v)
            vector = Rhino.Geometry.Vector3d(skyDomePt)-Rhino.Geometry.Vector3d(testPtLifted)
            ray = Rhino.Geometry.Ray3d(testPtLifted, vector)
            for meshIndex,mesh in enumerate(contextMeshes):
                intersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(mesh,ray)
                # ray hitted something
                if intersectParam >= 0:
                    seasonIndex = noLeavesPeriod("perHoy", latitude, i, leaflessStartHOY, leaflessEndHOY)
                    if meshIndex == 0:  # context mesh hitted
                        treesTransmissionIndex = 0
                    elif meshIndex == 1:  # coniferousTrees mesh hitted
                        treesTransmissionIndex = treesTransmissionIndices[0]
                    elif meshIndex == 2:  # deciduousTrees mesh hitted
                        treesTransmissionIndex = treesTransmissionIndices[1][seasonIndex]
                    hittedRaysIntensities += treesTransmissionIndex
                    break
            # no hitting, the ray only hits the sky dome
            else:
                hittedRaysIntensities += 1
    
    # top sky dome part
    verticalRay = Rhino.Geometry.Ray3d(testPtLifted, Rhino.Geometry.Vector3d(0,0,1))
    for meshIndex,mesh in enumerate(contextMeshes):
        intersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(mesh,ray)
        # ray hitted something
        if intersectParam >= 0:
            seasonIndex = noLeavesPeriod("perHoy", latitude, i, leaflessStartHOY, leaflessEndHOY)
            if meshIndex == 0:  # context mesh hitted
                treesTransmissionIndex = 0
            elif meshIndex == 1:  # coniferousTrees mesh hitted
                treesTransmissionIndex = treesTransmissionIndices[0]
            elif meshIndex == 2:  # deciduousTrees mesh hitted
                treesTransmissionIndex = treesTransmissionIndices[1][seasonIndex]
    # no hitting, the ray only hits the sky dome
    else:
        hittedRaysIntensities += 1
    skyViewFactor = hittedRaysIntensities/(precisionU*precisionV+1)
    
    return skyViewFactor


def noaaSolarCalculator(latitude, longitude, timeZone, month, day, hour):
    # by NOAA Earth System Research Laboratory
    # NOAA defines longitude and time zone as positive to the west:
    timeZone = -timeZone
    longitude = -longitude
    DOY = int(lb_preparation.getJD(month, day))
    minute = 0  # default
    second = 0  # default
    gamma = (2*math.pi)/365*(DOY-1+((hour-12)/24))
    eqtime = 229.18*(0.000075 + 0.001868*math.cos(gamma) - 0.032077*math.sin(gamma) - 0.014615*math.cos(2*gamma) - 0.040849*math.sin(2*gamma))
    declAngle = 0.006918 - 0.399912*math.cos(gamma) + 0.070257*math.sin(gamma) - 0.006758*math.cos(2*gamma) + 0.000907*math.sin(2*gamma) - 0.002697*math.cos(3*gamma) + 0.00148*math.sin(3*gamma)
    time_offset = eqtime-4*longitude+60*timeZone
    tst = hour *60 + minute + second / 60 + time_offset
    solarHangle = (tst / 4) - 180
    
    # solar zenith angle
    solarZenithR = math.acos(math.sin(math.radians(latitude)) * math.sin(declAngle) + math.cos(math.radians(latitude)) * math.cos(declAngle) * math.cos(math.radians(solarHangle)))
    solarZenithD = math.degrees(solarZenithR)
    if solarZenithD > 90:
        solarZenithD = 90
    elif solarZenithD < 0:
        solarZenithD = 0
    
    # solar altitude angle
    solarAltitudeD = 90 - solarZenithD
    
    # solar azimuth angle
    solarAzimuthR = - (math.sin(math.radians(latitude)) * math.cos(solarZenithR) - math.sin(declAngle)) / (math.cos(math.radians(latitude)) * math.sin(solarZenithR))
    solarAzimuthR = math.acos(solarAzimuthR)
    solarAzimuthD = math.degrees(solarAzimuthR)
    
    return solarZenithD, solarAzimuthD, solarAltitudeD


def beamShadingPerEachHour(testPt, srfTiltD, correctedSrfAzimuthD, SVF, contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, albedoL, scale, latitude, longitude, timeZone, directNormalRadiationData, diffuseHorizontalRadiationData, yearsHOY, monthsHOY, daysHOY, hoursHOY):
    
    # lifting up the testPt due to MeshRay intersection
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    testPtLifted = Rhino.Geometry.Point3d(testPt.X, testPt.Y, testPt.Z+tol)
    
    beamIndexPerHourL = []
    for i in range(8760):
        sunZenithD, sunAzimuthD, sunAltitudeD = noaaSolarCalculator(latitude, longitude, timeZone, monthsHOY[i], daysHOY[i], hoursHOY[i])
        if sunZenithD <= 90:  # above the horizon
            sunAzimuthR = math.radians(sunAzimuthD)
            rotationAxis = Rhino.Geometry.Vector3d(0, 0, 1)
            YAxis = Rhino.Geometry.Vector3d(testPtLifted.X, testPtLifted.Y+scale, 0)
            azimuthVector = Rhino.Geometry.Vector3d(YAxis)
            azimuthVector.Rotate(-sunAzimuthR, rotationAxis)  # for clockwise
            sunAltitudeR = math.radians(sunAltitudeD)
            sunHeight = math.tan(sunAltitudeR)*scale
            sunPt = Rhino.Geometry.Point3d(azimuthVector.X, azimuthVector.Y, azimuthVector.Z+sunHeight)
            sunVector = Rhino.Geometry.Vector3d(sunPt)-Rhino.Geometry.Vector3d(testPtLifted)
            ray = Rhino.Geometry.Ray3d(testPtLifted, sunVector)
            for meshIndex,mesh in enumerate(contextMeshes):
                intersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(mesh,ray)
                # ray hitted something
                if intersectParam >= 0:
                    seasonIndex = noLeavesPeriod("perHoy", latitude, i, leaflessStartHOY, leaflessEndHOY)
                    if meshIndex == 0:  # context mesh hitted
                        treesTransmissionIndex = 0
                    elif meshIndex == 1:  # coniferousTrees mesh hitted
                        treesTransmissionIndex = treesTransmissionIndices[0]
                    elif meshIndex == 2:  # deciduousTrees mesh hitted
                        treesTransmissionIndex = treesTransmissionIndices[1][seasonIndex]
                    beamIndexPerHourL.append(treesTransmissionIndex)
                    break
            # no hitting, the ray only hits the sky dome
            else:
                beamIndexPerHourL.append(1)
        
        elif sunZenithD > 90:  # bellow the horizon
            beamIndexPerHourL.append(0)  # always shaded
    
    
    # totalRadiationPerHour
    totalRadiationPerHourL = []
    for i in range(8760):
        sunZenithD, sunAzimuthD, sunAltitudeD = noaaSolarCalculator(latitude, longitude, timeZone, monthsHOY[i], daysHOY[i], hoursHOY[i])
        Epoa_shaded, Eb_shaded, Ed_sky, Eground, AOI_R = lb_photovoltaics.POAirradiance(sunZenithD, sunAzimuthD, srfTiltD, correctedSrfAzimuthD, directNormalRadiationData[i], diffuseHorizontalRadiationData[i], albedoL[i], beamIndexPerHourL[i], SVF)
        totalRadiationPerHourL.append(Epoa_shaded)
    
    return beamIndexPerHourL, totalRadiationPerHourL


def main(srfCornerPts, srfCentroid, contextMeshes, treesTransmissionIndices, eachQuadrantACpercent, latitude, northRad, northVec, scale, hoursPositionScale, precision, years, months, days, hoursHOY):
    northDeg = math.degrees(northRad)
    #createSunWindowMesh = False
    colors = [System.Drawing.Color.Black for i in range(len(eachQuadrantACpercent))]  # dummy colors
    annualShadingL = []
    unweightedAnnualShadingL = []
    Sep21toMar21ShadingL = []
    Mar21toSep21ShadingL = []
    for cornerPt in srfCornerPts:
    # calculate shading (annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading)
        sunWindowCrvs, outerBaseCrv, solarTimeHourCrvs, twoMonthCrvsCutted, sunAboveHorizon, sunPsolarTimeLFlattenFlipMatrix, hoursPositions, hours = sunWindowCurves(latitude, northRad, northVec, cornerPt, scale, hoursPositionScale)
        createSunWindowMesh = False
        annualShading, unweightedAnnualShading, Sep21toMar21Shading, Mar21toSep21Shading = shadingAndQuadrantPercentages(cornerPt, createSunWindowMesh, contextMeshes, treesTransmissionIndices, outerBaseCrv, sunPsolarTimeLFlattenFlipMatrix, solarTimeHourCrvs, twoMonthCrvsCutted, sunAboveHorizon, eachQuadrantACpercent, colors, precision)
        annualShadingL.append(annualShading)
        unweightedAnnualShadingL.append(unweightedAnnualShading)
        Sep21toMar21ShadingL.append(Sep21toMar21Shading)
        Mar21toSep21ShadingL.append(Mar21toSep21Shading)
    
    annualShading = round(sum(annualShadingL)/len(annualShadingL), 2)
    unweightedAnnualShading = round(sum(unweightedAnnualShadingL)/len(unweightedAnnualShadingL), 2)
    Sep21toMar21Shading = round(sum(Sep21toMar21ShadingL)/len(Sep21toMar21ShadingL), 2)
    Mar21toSep21Shading = round(sum(Mar21toSep21ShadingL)/len(Mar21toSep21ShadingL), 2)
    
    # sunWindow mesh, sunWindowCrvs, sunWindowCenPt, sunWindowShadedAreaPer, legend, legendBasePt, quadrantCentroids, quadrantACenergyPercents
    createSunWindowMesh = True
    sunWindowCrvs, outerBaseCrv, solarTimeHourCrvs, twoMonthCrvsCutted, sunAboveHorizon, sunPsolarTimeLFlattenFlipMatrix, hoursPositions, hours = sunWindowCurves(latitude, northRad, northVec, srfCentroid, scale, hoursPositionScale)
    legend, lowB, highB, customColors, legendBasePoint = legendGeometry(legendPar, scale, srfCentroid, eachQuadrantACpercent, validContextCategories)
    colors2 = lb_visualization.gradientColor(eachQuadrantACpercent, lowB, highB, customColors)
    sunWindowShadedAreaPer, quadrantCentroidsFiltered, quadrantShadingPercentRoundedFiltered, quadrantACPercentUnshadedRoundedFiltered, sunWindowMesh = shadingAndQuadrantPercentages(srfCentroid, createSunWindowMesh, contextMeshes, treesTransmissionIndices, outerBaseCrv, sunPsolarTimeLFlattenFlipMatrix, solarTimeHourCrvs, twoMonthCrvsCutted, sunAboveHorizon, eachQuadrantACpercent, colors2, precision)
    
    return annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading, sunWindowShadedAreaPer, sunWindowCrvs, sunWindowMesh, legend, legendBasePoint, quadrantCentroidsFiltered, quadrantShadingPercentRoundedFiltered, quadrantACPercentUnshadedRoundedFiltered, hoursPositions, hours


def swhshading(srfCornerPts, srfTiltD, correctedSrfAzimuthD, contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, albedoL, scale, latitude, longitude, timeZone, directNormalRadiationData, diffuseHorizontalRadiationData, yearsHOY, monthsHOY, daysHOY, hoursHOY):
    
    skyViewFactorL = []
    beamIndexPerHourLL = []
    totalRadiationPerHourLL = []
    for cornerPt in srfCornerPts:
        skyViewFactor = diffuseShading(cornerPt, contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, scale, precision)
        beamIndexPerHourL, totalRadiationPerHourL = beamShadingPerEachHour(cornerPt, srfTiltD, correctedSrfAzimuthD, skyViewFactor, contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, albedoL, scale, latitude, longitude, timeZone, directNormalRadiationData, diffuseHorizontalRadiationData, yearsHOY, monthsHOY, daysHOY, hoursHOY)
        skyViewFactorL.append(skyViewFactor)
        beamIndexPerHourLL.append(beamIndexPerHourL)
        totalRadiationPerHourLL.append(totalRadiationPerHourL)
    
    # averaging the skyViewFactor
    skyViewFactor = round(sum(skyViewFactorL)/len(skyViewFactorL), 2)
    
    # averaging the beamIndexPerHour, totalRadiationPerHour
    beamIndexPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Beam irradiance transmission index", "unitless", "Hourly", (1, 1, 1), (12, 31, 24)]
    totalRadiationPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Total solar irradiance", "kW/m2", "Hourly", (1, 1, 1), (12, 31, 24)]
    for i in range(8760):
        shadingRatioAdd = 0
        totalRadiationAdd = 0
        for k in range(len(beamIndexPerHourLL)):
            shadingRatioAdd += beamIndexPerHourLL[k][i]
            totalRadiationAdd += totalRadiationPerHourLL[k][i]
        shadingRatio = shadingRatioAdd/(len(beamIndexPerHourLL))
        averageGlobalRadiation = totalRadiationAdd/(len(totalRadiationPerHourLL))
        beamIndexPerHour.append(shadingRatio)
        totalRadiationPerHour.append(averageGlobalRadiation)
    
    #if not ACenergyPerHour_:
    # nothing inputted into "ACenergyPerHour_", or data inputted, but data comming from "Photovoltaics surface" component's "ACenergyPerHour" output is "None" ("Photovoltaics surface" component not ran)
    if (len(branchLists) == 0) or (sum(branchLists) == (len(list(ACenergyPerHour_.Paths)))):
        annualShading = Sep21toMar21Shading = Mar21toSep21Shading = unweightedAnnualShading = sunWindowShadedAreaPer = sunWindowCrvs = sunWindowMesh = legend = legendBasePt = quadrantCentroids = quadrantShadingPercents = quadrantACenergyPercents = hoursPositions = hours = "Please input \"ACenergyPerHour_\" to calculate this output."
        return skyViewFactor, beamIndexPerHour, totalRadiationPerHour, annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading, sunWindowShadedAreaPer, sunWindowCrvs, sunWindowMesh, legend, legendBasePt, quadrantCentroids, quadrantShadingPercents, quadrantACenergyPercents, hoursPositions, hours
    else:
        # dummy values except for skyViewFactor and beamIndexPerHour
        annualShading = Sep21toMar21Shading = Mar21toSep21Shading = unweightedAnnualShading = sunWindowShadedAreaPer = sunWindowCrvs = sunWindowMesh = legend = legendBasePt = quadrantCentroids = quadrantShadingPercents = quadrantACenergyPercents = hoursPositions = hours = None
        return skyViewFactor, beamIndexPerHour, totalRadiationPerHour, annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading, sunWindowShadedAreaPer, sunWindowCrvs, sunWindowMesh, legend, legendBasePt, quadrantCentroids, quadrantShadingPercents, quadrantACenergyPercents, hoursPositions, hours


def bakingGrouping(locationName, sunWindowCrvs, sunWindowMesh, legend, quadrantCentroidsFiltered, quadrantShadingPercentRoundedFiltered, srfCornerPts, sunWindowCenPt, annualShading, hoursPositions, hours):
    
    layerName = str(annualShading) + "%_" + locationName
    layerIndex, l = lb_visualization.setupLayers(layerName, "LADYBUG", "Shading_analysis", "PHOTOVOLTAICS")
    
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex = layerIndex
    attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    attr.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
    
    # bake sunWindowCrvs
    sunPathGeometryIds = []
    for obj in sunWindowCrvs:
        id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj,attr)
        sunPathGeometryIds.append(id)
    Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(sunWindowMesh, attr)
    
    # bake sunWindowMesh
    legendIds = []
    for obj in legend:
        id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj,attr)
        legendIds.append(id)
    
    # bake text dot quadrant percents
    textDotIds = []
    attr.ObjectColor = System.Drawing.Color.White
    for i,pt in enumerate(quadrantCentroidsFiltered):
        textDot = Rhino.Geometry.TextDot(str(quadrantShadingPercentRoundedFiltered[i]), pt)
        textDot.FontHeight = 10
        textDotIds.append(Rhino.RhinoDoc.ActiveDoc.Objects.AddTextDot(textDot, attr))
    
    # bake annualShadingValueTextDot and analysisPts
    textDot = Rhino.Geometry.TextDot(str(annualShading)+"%_"+str(l), sunWindowCenPt)
    textDot.FontHeight = 10
    annualShadingValueTextDotId = Rhino.RhinoDoc.ActiveDoc.Objects.AddTextDot(textDot, attr)
    attr.ObjectColor = System.Drawing.Color.Black
    annualPtsIds = []
    for cornerPt in srfCornerPts:
        annualPtsIds.append(Rhino.RhinoDoc.ActiveDoc.Objects.AddPoint(cornerPt, attr))
    
    # bake hours text dots
    hourTextDotIds = []
    for i,pt in enumerate(hoursPositions):
        hourTextDot = Rhino.Geometry.TextDot(str(hours[i]), pt)
        hourTextDot.FontHeight = 10
        hourTextDotIds.append(Rhino.RhinoDoc.ActiveDoc.Objects.AddTextDot(hourTextDot, attr))
    
    # grouping
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add("Shading_analysis_" + str(l) + "-sunPathCrvs_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, sunPathGeometryIds)
    
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add("Shading_analysis_" + str(l) + "-legend_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, legendIds)
    
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add("Shading_analysis_" + str(l) + "-quadrantPercentsUnshaded_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, textDotIds)
    
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add("Shading_analysis_" + str(l) + "-analysisPts_annualShadingValueTextDot_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, annualPtsIds + [annualShadingValueTextDotId])
    
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add("Shading_analysis_" + str(l) + "-hoursTextDots_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, hourTextDotIds)


def printOutput(locationName, latitude, longitude, northRad, srfAreaL, ACenergyPerHourDataLL, treesTransmissionIndices, leaflessPeriod, albedoL, scale, hoursPositionScale, precision, srfCornerPtsLL):
    printOutputMsg = \
    """

Input data:

Location: %s
Latitude (deg.): %s
Longitude (deg.): %s
North (deg.): %s

Surface area (m2): %s

Coniferous context trees transmission index for all year : %s
Deciduous context trees transmission index for in-leaf period: %s
Deciduous context trees transmission index for leaf-less period: %s 
Leafless period: %s, %s
ACenergyPerYear (kWh): %s
Average annual albedo(-): %0.2f

Scale: %s
Hours position scale: %s
Precision: %s
Number of shading analysis test points (analysisGeometry corner points): %s
    """ % (locationName, latitude, longitude, math.degrees(northRad), [float("%0.2f" % srfArea) if srfArea>0 else srfArea for srfArea in srfAreaL], treesTransmissionIndices[0], treesTransmissionIndices[1][0], treesTransmissionIndices[1][1], leaflessPeriod[0], leaflessPeriod[1], [sum(ACenergyPerHourData) for ACenergyPerHourData in ACenergyPerHourDataLL], sum(albedoL)/len(albedoL), scale, hoursPositionScale, precision, [len(srfCorners) for srfCorners in srfCornerPtsLL])
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_meshpreparation = sc.sticky["ladybug_Mesh"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        lb_sunpath = sc.sticky["ladybug_SunPath"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        if _epwFile:
            locationName, latitude, longitude, timeZone, dryBulbTemperatureData, directNormalRadiationData, diffuseHorizontalRadiationData, yearsHOY, validEpwData, printMsg = getEpwData(_epwFile)
            if validEpwData:
                branchLists = [len(list(branchL)) for branchL in ACenergyPerHour_.Branches]
                if (len(branchLists) != 0) or (sum(branchLists) != (len(list(_analysisGeometry.Paths)))):  #if _analysisGeometry:
                    # valid "_analysisGeometry" inputted
                    pathsAnalysisGeometry, srfCornerPtsLL, srfCentroidL, srfAreaL, srfTiltDL, correctedSrfAzimuthDL, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourDataLL, northRad, northVec, albedoL, outputGeometryIndex, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg = checkInputData(_analysisGeometry, ACenergyPerHour_, context_, coniferousTrees_, deciduousTrees_, coniferousAllyearIndex_, deciduousInleafIndex_, deciduousLeaflessIndex_, leaflessPeriod_, dryBulbTemperatureData, albedo_, latitude, north_, outputGeometryIndex_, scale_, hoursPositionScale_, precision_, legendPar_)
                    if validInputData:
                        # all inputs ok
                        if _runIt:
                            newTree = ghdt[object]()
                            newTree2 = ghdt[object]()
                            newTree3 = ghdt[object]()
                            newTree4 = ghdt[object]()
                            newTree5 = ghdt[object]()
                            newTree6 = ghdt[object]()
                            annualShadingL = []
                            sunWindowCrvsLL = []
                            sunWindowMeshL = []
                            legendLL = []
                            legendBasePtLL = []
                            quadrantCentroidsLL = []
                            quadrantShadingPercentsLL = []
                            quadrantACenergyPercentsLL = []
                            hoursPositionsLL = []
                            hoursLL = []
                            branchLists2 = [len(list(branchL2)) for branchL2 in ACenergyPerHour_.Branches]
                            for branchIndex,srfCornerPts in enumerate(srfCornerPtsLL):
                                if (len(branchLists2) != 0) or (sum(branchLists2) != (len(list(ACenergyPerHour_.Paths)))):
                                    # valid "ACenergyPerHour_" inputted
                                    if len(srfCornerPts) > 0:
                                        skyViewFactor, beamIndexPerHour, shadedSolarRadiationPerHour, annualShadingDummy, Sep21toMar21ShadingDummy, Mar21toSep21ShadingDummy, unweightedAnnualShadingDummy, sunWindowShadedAreaPerDummy, sunWindowCrvsDummy, sunWindowMeshDummy, legendDummy, legendBasePtDummy, quadrantCentroidsDummy, quadrantShadingPercentsDummy, quadrantACenergyPercentsDummy, hoursPositionsDummy, hoursDummy = swhshading(srfCornerPtsLL[branchIndex], srfTiltDL[branchIndex], correctedSrfAzimuthDL[branchIndex], contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, albedoL, scale, latitude, longitude, timeZone, directNormalRadiationData, diffuseHorizontalRadiationData, yearsHOY, monthsHOY, daysHOY, hoursHOY)
                                        eachQuadrantACpercent = ACenergyQuadrantPercents(ACenergyPerHourDataLL[branchIndex])
                                        annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading, sunWindowShadedAreaPer, sunWindowCrvs, sunWindowMesh, legend, legendBasePt, quadrantCentroids, quadrantShadingPercents, quadrantACenergyPercents, hoursPositions, hours = main(srfCornerPtsLL[branchIndex], srfCentroidL[branchIndex], contextMeshes, treesTransmissionIndices, eachQuadrantACpercent, latitude, northRad, northVec, scale, hoursPositionScale, precision, yearsHOY, monthsHOY, daysHOY, hoursHOY)
                                    else:
                                        skyViewFactor = Sep21toMar21Shading = Mar21toSep21Shading = annualShading = None
                                        beamIndexPerHour = shadedSolarRadiationPerHour = []
                                else:
                                    # nothing inputted into "ACenergyPerHour_", or data inputted, but data comming from "Photovoltaics surface" component's "ACenergyPerHour" output is "None" ("Photovoltaics surface" component not ran)
                                    if len(srfCornerPts) > 0:
                                        skyViewFactor, beamIndexPerHour, shadedSolarRadiationPerHour, annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading, sunWindowShadedAreaPer, sunWindowCrvs, sunWindowMesh, legend, legendBasePt, quadrantCentroids, quadrantShadingPercents, quadrantACenergyPercents, hoursPositions, hours = swhshading(srfCornerPtsLL[branchIndex], srfTiltDL[branchIndex], correctedSrfAzimuthDL[branchIndex], contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, albedoL, scale, latitude, longitude, timeZone, directNormalRadiationData, diffuseHorizontalRadiationData, yearsHOY, monthsHOY, daysHOY, hoursHOY)
                                    else:
                                        skyViewFactor = Sep21toMar21Shading = Mar21toSep21Shading = annualShading = None
                                        beamIndexPerHour = shadedSolarRadiationPerHour = []
                                
                                newTree.AddRange([skyViewFactor], pathsAnalysisGeometry[branchIndex])
                                newTree2.AddRange(beamIndexPerHour, pathsAnalysisGeometry[branchIndex])
                                newTree3.AddRange(shadedSolarRadiationPerHour, pathsAnalysisGeometry[branchIndex])
                                newTree4.AddRange([Sep21toMar21Shading], pathsAnalysisGeometry[branchIndex])
                                newTree5.AddRange([Mar21toSep21Shading], pathsAnalysisGeometry[branchIndex])
                                newTree6.AddRange([annualShading], pathsAnalysisGeometry[branchIndex])
                                annualShadingL.append(annualShading)
                                sunWindowCrvsLL.append(sunWindowCrvs)
                                sunWindowMeshL.append(sunWindowMesh)
                                legendLL.append(legend)
                                legendBasePtLL.append(legendBasePt)
                                quadrantCentroidsLL.append(quadrantCentroids)
                                quadrantShadingPercentsLL.append(quadrantShadingPercents)
                                quadrantACenergyPercentsLL.append(quadrantACenergyPercents)
                                hoursPositionsLL.append(hoursPositions)
                                hoursLL.append(hours)
                            
                            skyViewFactor = newTree
                            beamIndexPerHour = newTree2
                            shadedSolarRadiationPerHour = newTree3
                            Sep21toMar21Shading = newTree4
                            Mar21toSep21Shading = newTree5
                            annualShading = newTree6
                            annalysisPts = srfCornerPtsLL[outputGeometryIndex]
                            sunWindowCenPt = srfCentroidL[outputGeometryIndex]
                            sunWindowCrvs = sunWindowCrvsLL[outputGeometryIndex]
                            sunWindowMesh = sunWindowMeshL[outputGeometryIndex]
                            legend = legendLL[outputGeometryIndex]
                            legendBasePt = legendBasePtLL[outputGeometryIndex]
                            quadrantCentroids = quadrantCentroidsLL[outputGeometryIndex]
                            quadrantShadingPercents = quadrantShadingPercentsLL[outputGeometryIndex]
                            quadrantACenergyPercents = quadrantACenergyPercentsLL[outputGeometryIndex]
                            hoursPositions = hoursPositionsLL[outputGeometryIndex]
                            hours = hoursLL[outputGeometryIndex]
                            
                            if (len(branchLists2) == 0) or (sum(branchLists2) == (len(list(ACenergyPerHour_.Paths)))):
                                # nothing inputted into "ACenergyPerHour_", or data inputted, but data comming from "Photovoltaics surface" component's "ACenergyPerHour" output is "None" ("Photovoltaics surface" component not ran)
                                annalysisPts = sunWindowCenPt = sunWindowCrvs = sunWindowMesh = legend = legendBasePt = quadrantCentroids = quadrantShadingPercents = quadrantACenergyPercents = hoursPositions = hours = "Please input \"ACenergyPerHour_\" to calculate this output."
                            
                            ghenv.Component.Params.Output[9].Hidden= True
                            ghenv.Component.Params.Output[10].Hidden= True
                            ghenv.Component.Params.Output[14].Hidden= True
                            ghenv.Component.Params.Output[15].Hidden= True
                            ghenv.Component.Params.Output[18].Hidden= True
                            
                            printOutput(locationName, latitude, longitude, northRad, srfAreaL, ACenergyPerHourDataLL, treesTransmissionIndices, leaflessPeriod, albedoL, scale_, hoursPositionScale_, precision, srfCornerPtsLL)
                            if bakeIt_: 
                                if (len(branchLists) != 0) or (sum(branchLists) != (len(list(ACenergyPerHour_.Paths)))):
                                    bakingGrouping(locationName, sunWindowCrvs, sunWindowMesh, legend, quadrantCentroids, quadrantShadingPercents, annalysisPts, sunWindowCenPt, annualShadingL[outputGeometryIndex], hoursPositions, hours)
                                else:
                                    print "Baking is only provided if surface(s) is(are) inputted into _analysisGeometry and data is inputted in ACenergyPerHour_."
                        else:
                            print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Sunpath shading component"
                    else:
                        print printMsg
                        ghenv.Component.AddRuntimeMessage(level, printMsg)
                else:
                    printMsg = "Please input Surface(s) (not polysurface(s)) or point(s) to \"_analysisGeometry\"."
                    print printMsg
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please supply .epw file path to \"_epwFile\" input."
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        printMsg = "You need a newer version of Ladybug to use this component." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag the Ladybug_Ladybug component " + \
            "into the canvas and try again."
        print printMsg
else:
    printMsg = "First please let the Ladybug fly..."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
    
