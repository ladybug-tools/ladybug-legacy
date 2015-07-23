# Sunpath shading
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Djordje Spasic <djordjedspasic@gmail.com> 
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
This component calculates the amount of annual shading of sun window due to location's surroundings. Sun (or solar) window being an area of the the sky dome between winter and summer solstice sun paths.
Obstruction from buildings, structures, trees, mountains or other objects are considered.
It can be used to calculate annual shading for Photovoltaic arrays, Solar hot water collectors or any other purpose.
-
Use "annualShading" or "beamIndexPerHour" output for Photovoltaic arrays and "beamIndexPerHour" output for Solar hot water collectors shading analysis.
-
Based on "Using sun path charts to estimate the effects of shading on PV arrays", University of Oregon, Frank Vignola:
http://solardat.uoregon.edu/download/Papers/UsingSunPathChartstoEstimatetheEffectofShadingonPVArrays.pdf
-
Provided by Ladybug 0.0.60
    
    input:
        _PVsurface: Input planar Surface (not polysurface) on which the PV modules/Solar hot water collectors will be applied. If you have a polysurface, explode it (using "Deconstruct Brep" component) and then feed its Faces(F) output to _PVsurface. Surface normal should be faced towards the sun.
                    Number inputs (example: "100") and kiloWatt (example: "4 kw"). are not supported.
        _epwFile: Input .epw file path by using grasshopper's "File Path" component.
        ACenergyPerHour_: Input the "ACenergyPerHour" output data from "Photovoltaics surface" component.
                          If you are calculating shading analysis for "Solar hot water surface" component (instead of "Photovoltaics surface" component), leave this input empty. In kWh.
                          If you are calculating shading analysis for any other purpose, input annual solar radiation per hour data.
        context_: Buildings, structures, mountains and other permanent obstructions. Input polysurfaces, surfaces, or meshes.
        coniferousTrees_: This input allows for partial shading from coniferous(evergreen) context trees.
                          Input polysurfaces, surfaces, or meshes.
        deciduousTrees_: This input allows for partial shading during in-leaf and leaf-less periods from deciduous context trees.
                         In-leaf being a period from 21st March to 21st September in the northern hemisphere, and from 21st September to 21st March in the southern hemisphere.
                         Leaf-less being a period from 21st September to 21st March in the northern hemisphere, and from 21st March to 21st September in the in the southern hemisphere.
                         Input polysurfaces, surfaces, or meshes.
        coniferousAllyearIndex_: All year round transmission index for coniferous(evergreen) context trees. It ranges from 0 to 1.0. 0 represents deciduous trees which do not allow solar radiation to pass through them (100% shading). 1 represents all solar radiation passing through deciduous trees, like the trees do not exist (0% shading).
                                 -
                                 If not supplied default value of 0.30 (equals 70% shading) will be used.
        deciduousInleafIndex_: Deciduous context trees transmission index for in-leaf period. In-leaf being a period from 21st March to 21st September in the northern hemisphere, and from 21st September to 21st March in the southern hemisphere.
                               It ranges from 0 to 1.0. 0 represents deciduous trees which do not allow solar radiation to pass through them (100% shading). 1 represents all solar radiation passing through deciduous trees, like the trees do not exist (0% shading).
                               -
                               If not supplied default value of 0.23 (equals 77% shading) will be used.
        deciduousLeaflessIndex_: Deciduous context trees transmission index for leaf-less period. Leaf-less being a period from 21st September to 21st March in the northern hemisphere, and from 21st March to 21st September in the in the southern hemisphere.
                                It ranges from 0 to 1.0. 0 represents deciduous trees which do not allow solar radiation to pass through them (100% shading). 1 represents all solar radiation passing through deciduous trees, like the trees do not exist (0% shading).
                                -
                                If not supplied default value of 0.64 (equals 36% shading) will be used.
        leaflessPeriod_: Define the leafless period for deciduous trees using Ladybug's "Analysis Period" component.
                        IMPORTANT! This input affects only the "beamIndexPerHour" output. Due to limitations of the used sunpath diagram, it does not affect all the other shading outputs, where default leafless periods (see the line bellow) will always be used.
                        -
                        If not supplied the following default periods will be used: from 21st September to 21st March in the northern hemisphere, and from 21st March to 21st September in the in the southern hemisphere.
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
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
        beamIndexPerHour: Transmission index of beam (direct) irradiance for each hour during a year.
                          Transmission index of 0 means 100% shading. Transmission index of 1 means 0% shading.
                          It is calculated for each PVsurface vertex and then averaged. It ranges from 0-1.
                          Unitless.
        sunWindowShadedAreaPer: Percent of the overall sun window shaded area. It is calculated for PVsurface area centroid. It ranges from 0-100(%).
                                In percent(%).
        unweightedAnnualShading: Annual unweighted shading of the active sun window quadrants. Active sun window quadrants are only those which produce AC energy (or solar radiation in case you are using this component for other purposes than Photovoltaics)
                                 Unweighted means that each active sun window quadrant produces the same percentage of AC power. It is calculated for each PVsurface vertex and then averaged. It ranges from 0-100(%).
                                 In percent(%).
        Sep21toMar21Shading: Weighted shading of the active sun window quadrants, for period between 21st September to 21st March. Active sun window quadrants are only those which produce AC energy (or solar radiation in case you are using this component for other purposes than Photovoltaics)
                             It is calculated for each PVsurface vertex and then averaged. It ranges from 0-100(%).
                             In percent(%).
        Mar21toSep21Shading: Weighted shading of the active sun window quadrants, for period between 21st March to 21st September. Active sun window quadrants are only those which produce AC energy (or solar radiation in case you are using this component for other purposes than Photovoltaics)
                             It is calculated for each PVsurface vertex and then averaged. It ranges from 0-100(%).
                             In percent(%).
        annualShading: Annual weighted shading of the active sun window quadrants. To calculate it, input data to "ACenergyPerHour_" input.
                       Active sun window quadrants are only those which produce AC energy (or solar radiation in case you are using this component for other purposes than Photovoltaics)
                       It is calculated for each PVsurface vertex and then averaged. It ranges from 0-100(%).
                       In percent(%).
        annalysisPts: Each vertex of the inputted _PVsurface for which a separate shading analysis was conducted.
        sunWindowCenPt: The center point of the "sunWindowCrvs" and "sunWindowMesh" geometry. It is calculated for PVsurface area centroid.
                        Use this point to move "sunWindowCrvs" and "sunWindowMesh" geometry around in the Rhino scene with the grasshopper's "Move" component.
        sunWindowCrvs: Geometry of the sun window based on 3D polar sun path diagram. Perpendical curves represent solar time hours. Horizontal arc curves represent sun paths for: 21st December, 21st November/January, 21st October/February, 21st September/March, 21st August/April, 21st July/May, 21st June.
                       The whole sunWindowCrvs geometry output is calculated for PVsurface area centroid.
                       Connect this output to a Grasshopper's "Geo" parameter in order to preview the "sunWindowCrvs" geometry separately in the Rhino scene.
        sunWindowMesh: Sun window mesh based on 3D polar sun path diagram. It is calculated for PVsurface area centroid.
                       Black areas represent 100% shaded portions of the sun window (of both active and inactive quadrants). Darker green and green areas represent partially shaded portions from the coniferous and deciduous trees, respectively.
                       Connect this output to a Grasshopper's "Mesh" parameter in order to preview the "sunWindowMesh" geometry separately in the Rhino scene.
        legend: A legend of the sunWindowMesh. Connect this output to a Grasshopper's "Geo" parameter in order to preview the legend separately in the Rhino scene.  
        legendBasePt: Legend base point, which can be used to move the "legend" geometry with grasshopper's "Move" component.
        quadrantCentroids: Centroid for each sun window active quadrant above the horizon.
                           Use grasshopper's "Text tag" component to visualize them.
        quadrantShadingPercents: Shadinging percent per each sun window active quadrant above the horizon. Active quadrants with less than 0.01% are neglected.
                                 Use grasshopper's "Text tag" component to visualize them.
        quadrantACenergyPercents: AC energy percent per each sun window active quadrant above the horizon.
                                  Use grasshopper's "Text tag" component to visualize them.
        hoursPositions: Solar time hour point positions.
                        Use grasshopper's "Text tag" component to visualize them.
        hours: Solar time hour strings.
               Use grasshopper's "Text tag" component to visualize them.
"""

ghenv.Component.Name = "Ladybug_Sunpath Shading"
ghenv.Component.NickName = "SunpathShading"
ghenv.Component.Message = 'VER 0.0.60\nJUL_06_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.59\nMAY_26_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System
import Rhino
import math
import time
from decimal import Decimal as d


def getEpwData(epwFile):
    
    if epwFile:
        try:
            # location data
            locationName, latitude, longitude, timeZone, elevation, locationString = lb_preparation.epwLocation(epwFile)
            # weather data
            weatherData = lb_preparation.epwDataReader(epwFile, locationName)
            dryBulbTemperature, dewPointTemperature, relativeHumidity, windSpeed, windDirection, directNormalRadiation, diffuseHorizontalRadiation, globalHorizontalRadiation, directNormalIlluminance, diffuseHorizontalIlluminance, globalHorizontalIlluminance, totalSkyCover, liquidPrecipitationDepth, barometricPressure, modelYear = weatherData
            
            yearsHOY = modelYear[7:]
            
            validEpwData = True
            printMsg = "ok"
            
            return locationName, float(latitude), float(longitude), float(timeZone), float(elevation), yearsHOY, validEpwData, printMsg
        
        except Exception, e:
            # something is wrong with "_epwFile" input
            locationName = latitude = longitude = timeZone = elevation = yearsHOY = None
            validEpwData = False
            printMsg = "Something is wrong with \"_epwFile\" input."
    else:
        locationName = latitude = longitude = timeZone = elevation = yearsHOY = None
        validEpwData = False
        printMsg = "Please supply .epw file path to \"_epwFile\" input"
    
    return locationName, latitude, longitude, timeZone, elevation, yearsHOY, validEpwData, printMsg


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
            if isinstance(obj, Rhino.Geometry.Mesh) == False:
                meshL = Rhino.Geometry.Mesh.CreateFromBrep(obj, meshParam)
                for mesh in meshL:
                    joinedMesh.Append(mesh)
            else:
                joinedMesh.Append(obj)
    else:
        joinedMesh = Rhino.Geometry.Mesh()
        validContext = 0
    
    return joinedMesh, validContext


def angle2northClockwise(north):
    # temporary function, until "Sunpath" class from Labybug_ladbybug.py starts calculating sun positions counterclockwise
    try:
        northVec =Rhino.Geometry.Vector3d.YAxis
        northVec.Rotate(-math.radians(float(north)),Rhino.Geometry.Vector3d.ZAxis)
        northVec.Unitize()
        return 2*math.pi-math.radians(float(north)), northVec
    except Exception, e:
        try:
            northVec =Rhino.Geometry.Vector3d(north)
            northVec.Unitize()
            return Rhino.Geometry.Vector3d.VectorAngle(Rhino.Geometry.Vector3d.YAxis, northVec, Rhino.Geometry.Plane.WorldXY), northVec
        except Exception, e:
            return 0, Rhino.Geometry.Vector3d.YAxis


def checkInputData(PVsurface, ACenergyPerHour, context, coniferousTrees, deciduousTrees, coniferousAllyearIndex, deciduousInleafIndex, deciduousLeaflessIndex, leaflessPeriod, latitude, north, scale, hoursPositionScale, precision, legendPar):
    
    if (PVsurface == None):
        srfCornerPts = srfCentroid = srfArea = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourData = northRad = northVec = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = HOYs = validInputData = printMsg = None
        validInputData = False
        printMsg = "Please input a surface to \"_PVsurface\" input."
        return srfCornerPts, srfCentroid, srfArea, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourData, northRad, northVec, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
    else:
        brepObj = rs.coercegeometry(PVsurface)
        # input is brep
        if isinstance(brepObj, Rhino.Geometry.Brep):
            facesCount = brepObj.Faces.Count
            if facesCount > 1:
                # inputted polysurface
                srfCornerPts = srfCentroid = srfArea = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourData = northRad = northVec = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = HOYs = validInputData = printMsg = None
                validInputData = False
                printMsg = "The brep you supplied to \"_PVsurface\" is a polysurface. Please supply a surface."
                return srfCornerPts, srfCentroid, srfArea, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourData, northRad, northVec, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
            else:
                # inputted brep with a single surface
                srfCornerPts = brepObj.DuplicateVertices()
                srfCentroid = Rhino.Geometry.AreaMassProperties.Compute(brepObj).Centroid
                unitConversionFactor = lb_preparation.checkUnits()
                srfArea = Rhino.Geometry.AreaMassProperties.Compute(brepObj).Area * unitConversionFactor**2  # in m2
        else:
            try:
                # input is number (pv surface area in m2)
                PVsurfaceArea = float(PVsurface)
                srfCornerPts = srfCentroid = srfArea = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourData = northRad = northVec = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = HOYs = validInputData = printMsg = None
                validInputData = False
                printMsg = "\"Sunpath shading\" component does not accept numbers for \"_PVsurface\" input. Input your actual surface from Rhino/Grasshopper instead."
                return srfCornerPts, srfCentroid, srfArea, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourData, northRad, northVec, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
            except Exception, e:
                pass
            # input is string (nameplateDCpowerRating in kW)
            lowerString = PVsurface.lower()
            if "kw" in lowerString:
                srfCornerPts = srfCentroid = srfArea = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourData = northRad = northVec = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = HOYs = validInputData = printMsg = None
                validInputData = False
                printMsg = "\"Sunpath shading\" component does not accept Nameplate DC power rating as \"_PVsurface\" input. Input your actual surface from Rhino/Grasshopper instead."
                return srfCornerPts, srfCentroid, srfArea, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourData, northRad, northVec, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
            else:
                srfCornerPts = srfCentroid = srfArea = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourData = northRad = northVec = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = HOYs = validInputData = printMsg = None
                validInputData = False
                printMsg = "Something is wrong with your \"_PVsurface\" input. Input the surface you would like to populate with Photovoltaics"
                return srfCornerPts, srfCentroid, srfArea, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourData, northRad, northVec, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
    
    contextMeshes = []
    # context
    joinedMesh1, validContext1 = meshingGeometry(context)
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
    # Deutsche Gesellschaft Fr Sonnenenergie (Dgs), Dec 2007.
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
            srfCornerPts = srfCentroid = srfArea = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourData = northRad = northVec = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = HOYs = validInputData = printMsg = None
            validWeatherData = False
            printMsg = "Start and End time of your \"leaflessPeriod_\" input are the same. Please input a valid \"leaflessPeriod_\" input."
            return srfCornerPts, srfCentroid, srfArea, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourData, northRad, northVec, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
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
    
    if (north == None):
        northRad = 0  # default, in radians
        northVec = Rhino.Geometry.Vector3d(0,1,0)
    else:
        try:  # check if it's a number
            north = float(north)
            if north < 0 or north > 360:
                srfCornerPts = srfCentroid = srfArea = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourData = northRad = northVec = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = HOYs = validInputData = printMsg = None
                validInputData = False
                printMsg = "Please input north angle value from 0 to 360."
                return srfCornerPts, srfCentroid, srfArea, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourData, northRad, northVec, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
        except Exception, e:  # check if it's a vector
            north.Unitize()
        
        northRad, northVec = angle2northClockwise(north)
    
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
        legendPar = [None, None, None, [System.Drawing.Color.White, System.Drawing.Color.FromArgb(255,220,0), System.Drawing.Color.Red], None, None, None, None, None, None]
    
    if (len(ACenergyPerHour) != 0) and (ACenergyPerHour[0] is not ""):
        if len(ACenergyPerHour) == 8767:
            ACenergyPerHourData = ACenergyPerHour[7:]
        elif len(ACenergyPerHour) == 8760:
            ACenergyPerHourData = ACenergyPerHour
        if sum(ACenergyPerHourData) == 0:
            srfCornerPts = srfCentroid = srfArea = contextMeshes = validContextCategories = treesTransmissionIndices = leaflessPeriod = leaflessStartHOY = leaflessEndHOY = ACenergyPerHourData = northRad = northVec = scale = hoursPositionScale = precision = legendPar = monthsHOY = daysHOY = hoursHOY = HOYs = validInputData = printMsg = None
            validInputData = False
            printMsg = "The \"ACenergyPerHour_\" you inputted does not generate any AC energy (annual output = 0 kWh). Please input \"ACenergyPerHour_\" which does."
            return srfCornerPts, srfCentroid, srfArea, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourData, northRad, northVec, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg
    else:
        ACenergyPerHourData = []
    
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
    
    return srfCornerPts, srfCentroid, srfArea, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourData, northRad, northVec, scale, hoursPositionScale, precision, legendPar, monthsHOY, daysHOY, hoursHOY, validInputData, printMsg


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
    #hoursStrings = range(1,25)
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


def ACenergyQuadrantPercents(ACenergyPerHour):
    # percentage of annual AC output per solar window quadrant
    sunPsolarTimeL = [[] for i in range(25)]
    startSolarTimeHour = 1
    endSolarTimeHour = 24
    
    numberOfDaysInMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
    PacPerHourPerTwoMonthStrip = [] # six two month strips
    for i in range(6):
        subList = []
        #for k in range(len(sunPsolarTimeL)-1):
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
    
    sunWindowACenergySum = sum(eachQuadrantPac)  # instead of :ACenergyPerYear = sum(ACenergyPerHourData), use: sunWindowACenergySum
    
    eachQuadrantACpercent = [(Pac/sunWindowACenergySum)*100 for Pac in eachQuadrantPac]
    
    return eachQuadrantACpercent


def legendGeometry(legendPar, scale, testPt, eachQuadrantACpercent, validContextCategories):
    outerBaseCrv = Rhino.Geometry.Circle(testPt, 1.08*scale).ToNurbsCurve()
    
    # legend 1
    lowB, highB, numSeg, customColors, legend1BasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar, False)
    lb_visualization.calculateBB([outerBaseCrv])
    if legend1BasePoint == None:
        legend1BasePoint = lb_visualization.BoundingBoxPar[0]
    # generate the legend
    legendSrfs, legendText, legendTextSrfs, textPt, textSize = lb_visualization.createLegend(eachQuadrantACpercent, lowB, highB, numSeg, "Annual AC energy percentage", lb_visualization.BoundingBoxPar, legend1BasePoint, legendScale, legendFont, legendFontSize, legendBold)
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
                        if rayVector.Z >= 0:  # filter2 cull all rays bellow analysis analysisPt heiht
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
    
    if createSunWindowMesh == False:
        return annualShading, unweightedAnnualShading, Sep21toMar21Shading, Mar21toSep21Shading
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


def shadingPerEachHour(testPt, contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, scale, latitude, longitude, timeZone, years, months, days, hours):
    
    # lifting up the testPt due to MeshRay intersection
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    testPtLifted = Rhino.Geometry.Point3d(testPt.X, testPt.Y, testPt.Z+tol)
    
    shadingPerHourL = []
    for i in range(8760):
        sunZenithD, sunAzimuthD, sunAltitudeD = lb_photovoltaics.NRELsunPosition(latitude, longitude, timeZone, years[i], months[i], days[i], hours[i]-1)
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
                    shadingPerHourL.append(treesTransmissionIndex)
                    break
            # no hitting, the ray only hits the sky dome
            else:
                shadingPerHourL.append(1)
        
        elif sunZenithD > 90:  # bellow the horizon
            shadingPerHourL.append(0)  # always shaded
    
    return shadingPerHourL


def main(srfCornerPts, srfCentroid, contextMeshes, treesTransmissionIndices, eachQuadrantACpercent, latitude, northRad, northVec, scale, hoursPositionScale, precision, years, months, days, hoursHOY):
    northDeg = math.degrees(northRad)
    createSunWindowMesh = False
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


def shwshading(srfCornerPts, contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, scale, latitude, longitude, timeZone, years, months, days, hoursHOY):
    
    beamIndexPerHourLL = []
    for cornerPt in srfCornerPts:
        beamIndexPerHourL = shadingPerEachHour(cornerPt, contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, scale, latitude, longitude, timeZone, years, months, days, hoursHOY)
        beamIndexPerHourLL.append(beamIndexPerHourL)
    
    # averaging the beamIndexPerHour
    beamIndexPerHour = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "Beam irradiance transmission index", "unitless", "Hourly", (1, 1, 1), (12, 31, 24)]
    for i in range(8760):
        shadingRatioAdd = 0
        for k in range(len(beamIndexPerHourLL)):
            shadingRatioAdd += beamIndexPerHourLL[k][i]
        shadingRatio = shadingRatioAdd/(len(beamIndexPerHourLL))
        beamIndexPerHour.append(shadingRatio)
    
    if not ACenergyPerHour_:
        annualShading = Sep21toMar21Shading = Mar21toSep21Shading = unweightedAnnualShading = sunWindowShadedAreaPer = sunWindowCrvs = sunWindowMesh = legend = legendBasePt = quadrantCentroids = quadrantShadingPercents = quadrantACenergyPercents = hoursPositions = hours = "Please input \"ACenergyPerHour\" to calculate this output."
        return beamIndexPerHour, annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading, sunWindowShadedAreaPer, sunWindowCrvs, sunWindowMesh, legend, legendBasePt, quadrantCentroids, quadrantShadingPercents, quadrantACenergyPercents, hoursPositions, hours
    else:
        annualShading = Sep21toMar21Shading = Mar21toSep21Shading = unweightedAnnualShading = sunWindowShadedAreaPer = sunWindowCrvs = sunWindowMesh = legend = legendBasePt = quadrantCentroids = quadrantShadingPercents = quadrantACenergyPercents = hoursPositions = hours = None
        return beamIndexPerHour, annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading, sunWindowShadedAreaPer, sunWindowCrvs, sunWindowMesh, legend, legendBasePt, quadrantCentroids, quadrantShadingPercents, quadrantACenergyPercents, hoursPositions, hours


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


def printOutput(locationName, latitude, longitude, timeZone, elevation, northRad, srfArea, ACenergyPerHourData, treesTransmissionIndices, leaflessPeriod, scale, hoursPositionScale, precision, srfCornerPts):
    resultsCompletedMsg = "Sunpath shading component results successfully completed!"
    printOutputMsg = \
    """
Input data:

Location: %s
Latitude: %s
Longitude: %s
Time zone: %s
Elevation: %s
North: %s

Surface area (m2): %0.2f
ACenergyPerYear (kWh): %0.2f

Coniferous context trees transmission index for all year : %s
Deciduous context trees transmission index for in-leaf period: %s
Deciduous context trees transmission index for leaf-less period: %s 
leaflessPeriod: %s, %s

Scale: %s
Hours position scale: %s
Precision: %s
Number of shading analysis test points (PVsurface corner points): %s
    """ % (locationName, latitude, longitude, timeZone, elevation, math.degrees(northRad), srfArea, sum(ACenergyPerHourData), treesTransmissionIndices[0], treesTransmissionIndices[1][0], treesTransmissionIndices[1][1], leaflessPeriod[0], leaflessPeriod[1], scale, hoursPositionScale, precision, len(srfCornerPts))
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_meshpreparation = sc.sticky["ladybug_Mesh"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        lb_sunpath = sc.sticky["ladybug_SunPath"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        if _PVsurface:
            locationName, latitude, longitude, timeZone, elevation, years, validEpwData, printMsg = getEpwData(_epwFile)
            if validEpwData:
                srfCornerPts, srfCentroid, srfArea, contextMeshes, validContextCategories, treesTransmissionIndices, leaflessPeriod, leaflessStartHOY, leaflessEndHOY, ACenergyPerHourData, northRad, northVec, scale, hoursPositionScale, precision, legendPar, months, days, hoursHOY, validInputData, printMsg = checkInputData(_PVsurface, ACenergyPerHour_, context_, coniferousTrees_, deciduousTrees_, coniferousAllyearIndex_, deciduousInleafIndex_, deciduousLeaflessIndex_, leaflessPeriod_, latitude, north_, scale_, hoursPositionScale_, precision_, legendPar_)
                if validInputData:
                    # all inputs ok
                    if _runIt:
                        if ACenergyPerHour_:
                            beamIndexPerHour, annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading, sunWindowShadedAreaPer, sunWindowCrvs, sunWindowMesh, legend, legendBasePt, quadrantCentroids, quadrantShadingPercents, quadrantACenergyPercents, hoursPositions, hours = shwshading(srfCornerPts, contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, scale, latitude, longitude, timeZone, years, months, days, hoursHOY)
                            eachQuadrantACpercent = ACenergyQuadrantPercents(ACenergyPerHourData)
                            annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading, sunWindowShadedAreaPer, sunWindowCrvs, sunWindowMesh, legend, legendBasePt, quadrantCentroids, quadrantShadingPercents, quadrantACenergyPercents, hoursPositions, hours = main(srfCornerPts, srfCentroid, contextMeshes, treesTransmissionIndices, eachQuadrantACpercent, latitude, northRad, northVec, scale, hoursPositionScale, precision, years, months, days, hoursHOY)
                            if bakeIt_: bakingGrouping(locationName, sunWindowCrvs, sunWindowMesh, legend, quadrantCentroids, quadrantShadingPercents, srfCornerPts, srfCentroid, annualShading, hoursPositions, hours)
                        else:
                            beamIndexPerHour, annualShading, Sep21toMar21Shading, Mar21toSep21Shading, unweightedAnnualShading, sunWindowShadedAreaPer, sunWindowCrvs, sunWindowMesh, legend, legendBasePt, quadrantCentroids, quadrantShadingPercents, quadrantACenergyPercents, hoursPositions, hours = shwshading(srfCornerPts, contextMeshes, treesTransmissionIndices, leaflessStartHOY, leaflessEndHOY, scale, latitude, longitude, timeZone, years, months, days, hoursHOY)
                        printOutput(locationName, latitude, longitude, timeZone, elevation, northRad, srfArea, ACenergyPerHourData, treesTransmissionIndices, leaflessPeriod, scale_, hoursPositionScale_, precision, srfCornerPts)
                        annalysisPts = srfCornerPts; sunWindowCenPt = srfCentroid
                    else:
                        print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Sunpath shading component"
                else:
                    print printMsg
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please input a Surface (not a polysurface) to \"_PVsurface\"."
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