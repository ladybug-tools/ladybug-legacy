# Tilt and orientation factor
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
This component calculates the Optimal Tilt, Optimal Orientation and TOF (Tilt and Orientation Factor) for PV modules or Solar water heating collectors.
TOF is a solar radiation at the actual tilt and orientation divided by the solar radiation at the optimum tilt and orientation.
-
Provided by Ladybug 0.0.62
    
    input:
        _epwFile: Input .epw file path by using the "File Path" parameter, or Ladybug's "Open EPW And STAT Weather Files" component.
        _PV_SWHsurface: - Input planar Grasshopper/Rhino Surface (not a polysurface) on which the PV modules/SWH collectors will be applied. If you have a polysurface, explode it (using "Deconstruct Brep" component) and then feed its Faces(F) output to _PV_SWHsurface. Surface normal should be faced towards the sun.
                        - Or create the Surface based on initial PV/SWH system size by using "PV SWH system size" component.
        annualShading_: Losses due to buildings, structures, trees, mountains or other objects that prevent solar radiation from reaching the PV module/Solar water heating collector.
                  Input range: 0 to 100(%), 0 being unshaded, and 100 being totally shaded PV module/SWH collector.
                  -
                  If not supplied default value of 0(%) will be used.
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        albedo_: A list of 8767 (with header) or 8760 (without the header) albedo values for each hour during a year.
                 Albedo (or Reflection coefficient) is an average ratio of the global incident solar radiation reflected from the area surrounding the PV surface.
                 It ranges from 0 to 1.
                 -
                 It depends on the time of the year/day, surface type, temperature, vegetation, presence of water, ice and snow etc.
                 -
                 If no list supplied, default value of 0.20 will be used, corrected(increased) for the presence of snow (if any).
                 -
                 Unitless.
        precision_: Represents the square root number of analysis field for the output "geometry" mesh. Ranges from 1-100.
                    Example - precision of 4, would mean that 4 fields in X direction (Azimuth) and 4 fields in Y direction (Tilt) = 16 fields, will be used to calculate the final "geometry" mesh.
                    For lower precision numbers (say < 20) even precision numbers are more accurate.
                    -
                    CAUTION!!! Precision numbers (10 >) require stronger performance PCs. If your PC is somewhat "weaker", the precision of < 10 will be just fine.
                    -
                    If not supplied, default value of 2 will be used.
        scale_: Scale of the overall geometry.
                -
                If not supplied, default value of 1 will be used.
        origin_: Origin for the final "geometry" output.
                -
                If not supplied, default point of (-15,0,0) will be used.
        legendPar_: Optional legend parameters from the Ladybug "Legend Parameters" component.
        bakeIt_: Set to "True" to bake the Tilt and orientation factor results into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
        
    output:
        readMe!: ...
        TOF: Tilt and Orientation Factor - solar radiation at the actual tilt and azimuth divided by the solar radiation at the optimum tilt and azimuth.
             In percent(%).
        TSRF: Total Solar Resource Fraction - the ratio of solar radiation available accounting for both annual shading and TOF, compared to the solar radiation available at a given location at the optimum tilt and azimuth and with no shading.
              Calculated according to the following equation:
              TSRF = TOF * (100-annualShading)/100
              Some USA states, like Oregon and Washington require TSRF to be minimum 75% in order for the PV system to be applicable for incentive programs.
              -
              In percent(%).
        PVsurfaceTilt: Tilt angle of the inputted PV_SWHsurface.
                       In degrees ().
        PVsurfaceAzimuth: Orientation angle of the inputted PV_SWHsurface.
                          In degrees ().
        optimalTilt: Optimal tilt of the PV_SWHsurface for a given location. Optimal tilt being the one that receives the most annual solar radiation.
                     In degrees ().
        optimalAzimuth: Optimal orientation of the PV_SWHsurface for a given location. Optimal azimuth being the one that receives the most annual solar radiation.
                        In degrees ().
        optimalRoofPitch: Optimal steepness of the PV_SWHsurface for a given location. Optimal steepness being the one that receives the most annual solar radiation.
                          In inches/inches
        optimalRadiation: Total solar radiation per square meter for a whole year received on a PV_SWHsurface of optimal tilt and azimuth, at given location.
                          In kWh/m2
        geometry: Geometry of the whole TOF mesh chart.
                  Connect this output to a Grasshopper's "Geo" parameter in order to preview the "geometry" separately in the Rhino scene.
        originPt: The origin point of the "geometry" output.
                  Use this point to move "geometry" output around in the Rhino scene with the grasshopper's "Move" component.
        analysisPt: A point indicating inputted PV_SWHsurface's Tilt/Azimuth position on the solar radiation table.
        legend: A legend for the annual total solar radiation (in kWh/m2). Connect this output to a Grasshopper's "Geo" parameter in order to preview the legend separately in the Rhino scene.  
        legendBasePt: Legend base point, which can be used to move the "legend" geometry with grasshopper's "Move" component.
"""

ghenv.Component.Name = "Ladybug_Tilt And Orientation Factor"
ghenv.Component.NickName = "TOF"
ghenv.Component.Message = 'VER 0.0.62\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.61\nDEC_05_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System
import Rhino
import time
import math


def getEpwData(epwFile, annualShading, albedo, precision, scale, origin, legendPar):
    
    if epwFile:
        try:
            # location data
            locationName, latitude, longitude, timeZone, elevation, locationString = lb_preparation.epwLocation(epwFile)
            # weather data
            weatherData = lb_preparation.epwDataReader(epwFile, locationName)
            dryBulbTemperature, dewPointTemperature, relativeHumidity, windSpeed, windDirection, directNormalRadiation, diffuseHorizontalRadiation, globalHorizontalRadiation, directNormalIlluminance, diffuseHorizontalIlluminance, globalHorizontalIlluminance, totalSkyCover, liquidPrecipitationDepth, barometricPressure, modelYear = weatherData
            Ta = dryBulbTemperature[7:]
            
            if (annualShading == None) or (annualShading < 0) or (annualShading > 100):
                annualShading = 0  # default
            
            if (len(albedo) == 0) or (albedo[0] is ""):
                albedoL = lb_photovoltaics.calculateAlbedo(Ta)  # default
            elif (len(albedo) == 8767):
                albedoL = albedo[7:]
            elif (len(albedo) == 8760):
                albedoL = albedo
            else:
                locationName = latitude = longitude = timeZone = DNI = DHI = yearsHOY = monthsHOY = daysHOY = hoursHOY = HOYs = annualShading = albedoL = precision = scale = origin = originOffset = legendPar = None
                validEpwData = False
                printMsg = "Something is wrong with your \"albedo_\" list input.\n\"albedo_\" input accepts a list of 8767 (with header) or 8760 (without the header) abledo values."
                
                return locationName, latitude, longitude, timeZone, DNI, DHI, yearsHOY, monthsHOY, daysHOY, hoursHOY, HOYs, annualShading, albedoL, precision, scale, origin, originOffset, legendPar, validEpwData, printMsg
            
            if (precision == None) or (precision < 1) or (precision > 100):
                precision = 2  # default
            
            if (scale == None) or (scale <= 0):
                scale = 1
            
            if (origin == None):
                origin = Rhino.Geometry.Point3d(-15, 0, 0)
                originOffset = Rhino.Geometry.Point3d(origin.X+15, origin.Y, origin.Z)  # default 0,0,0 point
            else:
                originOffset = Rhino.Geometry.Point3d(origin.X+15, origin.Y, origin.Z)  # default 0,0,0 point
            
            if (len(legendPar) == 0):
                lowB = None; highB = None; numSeg = None; customColors = [System.Drawing.Color.FromArgb(98,20,0), System.Drawing.Color.FromArgb(204,79,0), System.Drawing.Color.FromArgb(255,174,52), System.Drawing.Color.FromArgb(254,255,255)]; legendBasePoint = None; legendScale = None; legendFont = None; legendFontSize = None; legendBold = None; decimalPlaces = 2; removeLessThan = False
                legendPar = [lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan]
            
            
            DNI = directNormalRadiation[7:]
            DHI = diffuseHorizontalRadiation[7:]
            yearsHOY = modelYear[7:]
            
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
            
            HOYs = range(1,8761)
            
            validEpwData = True
            printMsg = "ok"
            
            return locationName, float(latitude), float(longitude), float(timeZone), DNI, DHI, yearsHOY, monthsHOY, daysHOY, hoursHOY, HOYs, annualShading, albedoL, precision, scale, origin, originOffset, legendPar, validEpwData, printMsg
        
        except Exception, e:
            # something is wrong with "_epwFile" input
            locationName = latitude = longitude = timeZone = DNI = DHI = yearsHOY = monthsHOY = daysHOY = hoursHOY = HOYs = annualShading = albedoL = precision = scale = origin = originOffset = legendPar = None
            validEpwData = False
            printMsg = "Something is wrong with \"_epwFile\" input."
    else:
        locationName = latitude = longitude = timeZone = DNI = DHI = yearsHOY = monthsHOY = daysHOY = hoursHOY = HOYs = annualShading = albedoL = precision = scale = origin = originOffset = legendPar = None
        validEpwData = False
        printMsg = "Please supply .epw file path to \"_epwFile\" input."
    
    return locationName, latitude, longitude, timeZone, DNI, DHI, yearsHOY, monthsHOY, daysHOY, hoursHOY, HOYs, annualShading, albedoL, precision, scale, origin, originOffset, legendPar, validEpwData, printMsg


def PVsurfaceInputData(PV_SWHsurface):
    
    if (PV_SWHsurface == None):
        PVsurfaceInputType = srfArea = None
        validPVsurfaceData = False
        printMsg = "Please input a Surface (not polysurface) to \"_PV_SWHsurface\"."
        
        return PVsurfaceInputType, srfArea, validPVsurfaceData, printMsg
    
    # check PV_SWHsurface input
    PVsurfaceInputType = "brep"
    facesCount = PV_SWHsurface.Faces.Count
    if facesCount > 1:
        # inputted polysurface
        PVsurfaceInputType = srfArea = None
        validPVsurfaceData = False
        printMsg = "The brep you supplied to \"_PV_SWHsurface\" is a polysurface. Please supply a surface"
        
        return PVsurfaceInputType, srfArea, validPVsurfaceData, printMsg
    else:
        # inputted brep with a single surface
        srfArea = Rhino.Geometry.AreaMassProperties.Compute(PV_SWHsurface).Area  # in m2
        validPVsurfaceData = True
        printMsg = "ok"
        
        return PVsurfaceInputType, srfArea, validPVsurfaceData, printMsg


def main(latitude, longitude, timeZone, locationName, years, months, days, hours, HOYs, srfArea, srfTiltD, srfAzimuthD, correctedSrfAzimuthD, directNormalRadiation, diffuseHorizontalRadiation, albedoL, precision, originOffset):
    
    # TOF mesh Tilt, Azimuth values
    srfTiltTOFList = []
    srfAzimuthTOFList = []
    stepSrfTilt = 90/precision
    stepSrfAzimuth = 180/precision
    if anglesClockwise == True:  # angles clockwise
        for i in range(0,precision+1,1):
            srfTiltTOFList.append(stepSrfTilt*i)
        if latitude >= 0:
            for i in range(precision,-1,-1):
                srfAzimuthTOFList.append(90+stepSrfAzimuth*i)
        elif latitude < 0:
            for i in range(0,precision+1,1):
                srfAzimuth = 270+stepSrfAzimuth*i
                if srfAzimuth >= 360:
                    srfAzimuth = srfAzimuth-360
                srfAzimuthTOFList.append(srfAzimuth)
    elif anglesClockwise == False:  # angles counterclockwise
        for i in range(0,precision+1,1):
            srfTiltTOFList.append(stepSrfTilt*i)
        if latitude >= 0:
            for i in range(0,precision+1,1):
                srfAzimuthTOFList.append(90+stepSrfAzimuth*i)
        elif latitude < 0:
            for i in range(precision,-1,-1): 
                srfAzimuth = 270+stepSrfAzimuth*i
                if srfAzimuth >= 360:
                    srfAzimuth = srfAzimuth-360
                srfAzimuthTOFList.append(srfAzimuth)
    
    # TOF mesh generation (mesh width = 80, mesh height = 45)
    meshPtStepU = 80/(len(srfAzimuthTOFList)-1)
    meshPtStepV = 45/(len(srfTiltTOFList)-1)
    meshPts = []
    meshLiftedPts = []
    totalRadiationPerYearL = []
    for i,srfTiltTOF in enumerate(srfTiltTOFList):
        for k,srfAzimuthTOF in enumerate(srfAzimuthTOFList):
            totalRadiationPerYear = 0
            for g,hoy in enumerate(HOYs):
                sunZenithD, sunAzimuthD, sunAltitudeD = lb_photovoltaics.NRELsunPosition(latitude, longitude, timeZone, years[g], months[g], days[g], hours[g]-1)
                Epoa, Eb, Ed_sky, Eground, AOI_R = lb_photovoltaics.POAirradiance(sunZenithD, sunAzimuthD, srfTiltTOF, srfAzimuthTOF, directNormalRadiation[g], diffuseHorizontalRadiation[g], albedoL[g])
                totalRadiationPerYear += Epoa  # in Wh/m2
            totalRadiationPerYearL.append(totalRadiationPerYear)
            if anglesClockwise == True:  # angles clockwise
                meshPt = Rhino.Geometry.Point3d(originOffset.X + meshPtStepU*k, originOffset.Y + meshPtStepV*i, originOffset.Z)
                liftedMeshPt = Rhino.Geometry.Point3d(originOffset.X + meshPtStepU*k, originOffset.Y + meshPtStepV*i, originOffset.Z + totalRadiationPerYear/50000)
            elif anglesClockwise == False:  # angles counterclockwise
                meshPt = Rhino.Geometry.Point3d(originOffset.X + meshPtStepU*k, originOffset.Y + meshPtStepV*i, originOffset.Z)
                liftedMeshPt = Rhino.Geometry.Point3d(originOffset.X + meshPtStepU*k, originOffset.Y + meshPtStepV*i, originOffset.Z + totalRadiationPerYear/50000)
            meshPts.append(meshPt)
            meshLiftedPts.append(liftedMeshPt)
    
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    colors = lb_visualization.gradientColor(totalRadiationPerYearL, lowB, highB, customColors)
    
    mesh = lb_meshpreparation.meshFromPoints(precision+1, precision+1, meshPts, colors)
    meshLifted = lb_meshpreparation.meshFromPoints(precision+1, precision+1, meshLiftedPts, [])
    
    maximalTotalRadiationPerYear = max(totalRadiationPerYearL)
    minimalTotalRadiationPerYear = min(totalRadiationPerYearL)
    percents = [(totalRadiationPerYear/maximalTotalRadiationPerYear)*100 for totalRadiationPerYear in totalRadiationPerYearL]
    percentsAndPts = [((totalRadiationPerYear/maximalTotalRadiationPerYear)*100, meshLiftedPts[i]) for i,totalRadiationPerYear in enumerate(totalRadiationPerYearL)]
    minimalPercent = min(percents)
    maximalPercent = max(percents)  # always 100
    percentsAndPts.sort()
    minimalPt = percentsAndPts[0][1]
    maximalPt = percentsAndPts[-1][1]
    
    
    # isoCrvs
    planesAxisLine = Rhino.Geometry.Line(Rhino.Geometry.Point3d(0, 0, minimalPt.Z), Rhino.Geometry.Point3d(0, 0, maximalPt.Z))
    planesAxisCrv = Rhino.Geometry.Line.ToNurbsCurve(planesAxisLine)
    newDomain = Rhino.Geometry.Interval(minimalPercent, maximalPercent)
    planesAxisCrv.Domain = newDomain
    
    isoCrvPlanes = []
    isoCrvPercents = []
    projectedIsoCrvs = []
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    percents10 = [10,20,30,40,50,60,70,80,90,94,96,98,99]
    for p in percents10:
        if (p >= minimalPercent) and (p <= maximalPercent):
            plane = Rhino.Geometry.Plane( Rhino.Geometry.Point3d(planesAxisCrv.PointAt(p)), Rhino.Geometry.Vector3d(0,0,1) )
            isoCrvPlanes.append(plane)
            isoCrvPercents.append(p)
            isoPolylinesSublist = Rhino.Geometry.Intersect.Intersection.MeshPlane(meshLifted, plane)
            isoCrvsSubList = [Rhino.Geometry.Polyline.ToNurbsCurve(polyline) for polyline in isoPolylinesSublist]
            joinedIsoCrvsSubList = Rhino.Geometry.Curve.JoinCurves(isoCrvsSubList, tol)
            projectedIsoCrvsSubList = [Rhino.Geometry.Curve.ProjectToPlane(crv, Rhino.Geometry.Plane(Rhino.Geometry.Point3d(originOffset), Rhino.Geometry.Vector3d(0,0,1))) for crv in joinedIsoCrvsSubList]
            projectedIsoCrvs.append(projectedIsoCrvsSubList)
    # last (100%) isoCrv
    plane = Rhino.Geometry.Plane( Rhino.Geometry.Point3d(planesAxisCrv.PointAt(100-tol)), Rhino.Geometry.Vector3d(0,0,1) )
    lastIsoPolylines = Rhino.Geometry.Intersect.Intersection.MeshPlane(meshLifted, plane)
    lastIsoCrvs = [Rhino.Geometry.Polyline.ToNurbsCurve(polyline) for polyline in lastIsoPolylines]
    joinedLastIsoCrvs = Rhino.Geometry.Curve.JoinCurves(lastIsoCrvs, tol)
    projectedLastIsoCrvs = [Rhino.Geometry.Curve.ProjectToPlane(crv, Rhino.Geometry.Plane(Rhino.Geometry.Point3d(originOffset), Rhino.Geometry.Vector3d(0,0,1))) for crv in joinedLastIsoCrvs]
    
    
    # optimal Tilt, Azimuth
    planarMeshAboveLiftedPts = [Rhino.Geometry.Point3d(pt.X, pt.Y, maximalPt.Z+10) for pt in meshLiftedPts]
    planarMeshAboveLifted = lb_meshpreparation.meshFromPoints(precision+1, precision+1, planarMeshAboveLiftedPts, [])
    
    def meshesClosesPts(startingPt, mesh1, mesh2):
        pt1 = startingPt
        for k in range(300):
            pt2 = mesh2.ClosestMeshPoint(pt1,0.0).Point
            pt1 = mesh1.ClosestMeshPoint(pt2,0.0).Point
        return pt1
    
    if latitude >= 0:
        azimuthMeshStartValue = 90
    elif latitude < 0:
        azimuthMeshStartValue = 270
    meshLiftedCentroid = Rhino.Geometry.AreaMassProperties.Compute(meshLifted).Centroid
    optimalPt = meshesClosesPts(meshLiftedCentroid, meshLifted, planarMeshAboveLifted)
    if anglesClockwise == True:  # clockwise
        if latitude >= 0:
            optimalAzimuthD = round( 180-((optimalPt.X-originOffset.X) *180/80)+azimuthMeshStartValue, 1 )
        elif latitude < 0:
            optimalAzimuthD = round((180*(optimalPt.X - originOffset.X)/80 + azimuthMeshStartValue), 1)
            if optimalAzimuthD >= 360:
                optimalAzimuthD = optimalAzimuthD-360
    elif anglesClockwise == False:  # counterclockwise
        if latitude >= 0:
            optimalAzimuthD = round(((optimalPt.X-originOffset.X) *180/80)+azimuthMeshStartValue, 1 )
        elif latitude < 0:
            optimalAzimuthD = round(180-((optimalPt.X-originOffset.X) *180/80)+azimuthMeshStartValue, 1 )
            if optimalAzimuthD >= 360:
                optimalAzimuthD = optimalAzimuthD-360
    optimalTiltD = round(90*(optimalPt.Y - originOffset.Y)/45,1)
    
    # optimalRoofPitch
    optimalTiltTangent = math.tan(math.radians(optimalTiltD))
    optimalTiltNumerator = round(12*optimalTiltTangent,2)
    if optimalTiltNumerator % 1 == 0:
        optimalTiltNumerator = int(optimalTiltNumerator)
    optimalRoofPitch = "%s/12" % optimalTiltNumerator
    
    # analysisPt ("originOffset.Z+tol" due to overlap with "mesh")
    if anglesClockwise == True:  # clockwise
        if latitude >= 0:
            oppositeOriginOffset = Rhino.Geometry.Point3d(originOffset.X+15+80+15, originOffset.Y, originOffset.Z)
            analysisPt = Rhino.Geometry.Point3d( (oppositeOriginOffset.X-15-15) -((srfAzimuthD-azimuthMeshStartValue)*80/180), originOffset.Y+srfTiltD*45/90, originOffset.Z+tol)
        elif latitude < 0:
            if (srfAzimuthD >= 0) and  (srfAzimuthD < 270):
                srfAzimuthD = srfAzimuthD + 360
            analysisPt = Rhino.Geometry.Point3d(((srfAzimuthD-azimuthMeshStartValue)*80/180)+originOffset.X, originOffset.Y+srfTiltD*45/90, originOffset.Z+tol)
    elif anglesClockwise == False:  # counterclockwise
        if latitude >= 0:
            analysisPt = Rhino.Geometry.Point3d(((srfAzimuthD-azimuthMeshStartValue)*80/180)+originOffset.X, originOffset.Y+srfTiltD*45/90, originOffset.Z+tol)
        elif latitude < 0:
            if (srfAzimuthD >= 0) and  (srfAzimuthD <= 90):
                srfAzimuthD = srfAzimuthD + 360
            oppositeOriginOffset = Rhino.Geometry.Point3d(originOffset.X+15+80+15, originOffset.Y, originOffset.Z)
            analysisPt = Rhino.Geometry.Point3d( (oppositeOriginOffset.X-15-15) -((srfAzimuthD-azimuthMeshStartValue)*80/180), originOffset.Y+srfTiltD*45/90, originOffset.Z+tol)
    
    # totalRadiationPerYear of the inputted (analysed) surface
    totalRadiationPerYear = 0
    for i,hoy in enumerate(HOYs):
        sunZenithD, sunAzimuthD, sunAltitudeD = lb_photovoltaics.NRELsunPosition(latitude, longitude, timeZone, years[i], months[i], days[i], hours[i]-1)
        Epoa, Eb, Ed_sky, Eground, AOI_R = lb_photovoltaics.POAirradiance(sunZenithD, sunAzimuthD, srfTiltD, srfAzimuthD, directNormalRadiation[i], diffuseHorizontalRadiation[i], albedoL[i])
        totalRadiationPerYear += Epoa  # in Wh/m2
    
    # TOF, TSRF of the inputted (analysed) surface
    TOF = round((totalRadiationPerYear/maximalTotalRadiationPerYear)*100 ,1)  # in percent
    if TOF > 100:
        TOF = 100
    TSRF = round(TOF * ((100-annualShading)/100) ,1)  # in percent
    
    return totalRadiationPerYearL, int(maximalTotalRadiationPerYear/1000), int(totalRadiationPerYear/1000), meshPts, mesh, projectedIsoCrvs, projectedLastIsoCrvs, isoCrvPercents, optimalAzimuthD, optimalTiltD, optimalRoofPitch, analysisPt, TOF, TSRF


def createGeometry(totalRadiationPerYearL, totalRadiationPerYear, mesh, optimalTiltD, optimalAzimuthD, TOF, TSRF, projectedIsoCrvs, projectedLastIsoCrvs, isoCrvPercents, originOffset, legendPar, locationName, latitude, longitude):
    
    # isoCrvs text values origin points
    percentTextValuesOrigins = []
    cuttedProjectedIsoCrvs = []
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    for i,p in enumerate(isoCrvPercents):
        isoCrv = projectedIsoCrvs[i][0]
        midPt = isoCrv.PointAtLength(isoCrv.GetLength()/2)
        percentTextValuesOrigins.append(midPt)
        circleAroundRegionPercValues = Rhino.Geometry.Circle(midPt, 1.4).ToNurbsCurve()
        interevents = Rhino.Geometry.Intersect.Intersection.CurveCurve(isoCrv, circleAroundRegionPercValues, tol, tol)
        if len(interevents) != 0:
            t1 = interevents[0].ParameterA
            t2 = interevents[1].ParameterA
            isoCrvDomain = isoCrv.Domain
            dom1 = Rhino.Geometry.Interval(isoCrvDomain[0],t1)
            dom2 = Rhino.Geometry.Interval(t2,isoCrvDomain[1])
            crvBeginningPart = Rhino.Geometry.Curve.Trim(isoCrv,dom1)
            crvEndingPart = Rhino.Geometry.Curve.Trim(isoCrv,dom2)
            joinedSplittedIsoCrvs = Rhino.Geometry.Curve.JoinCurves([crvBeginningPart,crvEndingPart], tol)
            if isoCrv.IsClosed:
                cuttedProjectedIsoCrvs.append(joinedSplittedIsoCrvs[0])
            else:
                cuttedProjectedIsoCrvs.append(joinedSplittedIsoCrvs[0])
                cuttedProjectedIsoCrvs.append(joinedSplittedIsoCrvs[1])
            # add second curves, not labeled with isoCrvPercentsStrings
            if len(projectedIsoCrvs[i]) > 1:
                cuttedProjectedIsoCrvs.append(projectedIsoCrvs[i][1])
        else:
            # add cuttedProjectedIsoCrvs smaller than circleAroundRegionPercValues diameter
            cuttedProjectedIsoCrvs.append(projectedIsoCrvs[i][0])
    
    # xAxis, yAxis NotchValues
    if anglesClockwise == True:  # clockwise
        if latitude >= 0:
            xAxisNotchValues = ["270","240","210","180","150","120","90"]
        elif latitude < 0:
            xAxisNotchValues = ["270","300","330","0","30","60","90"]
    elif anglesClockwise == False:  # counterclockwise
        if latitude >= 0:
            xAxisNotchValues = ["90","120","150","180","210","240","270"]
        elif latitude < 0:
            xAxisNotchValues = ["90","60","30","0","330","300","270"]
    yAxisNotchValues = ["0","10","20","30","40","50","60","70","80","90"]
    
    # xAxis, yAxis NotchLines, NotchValuesOrigins
    xAxisNotchLines = []
    xAxisNotchValuesOrigins = []
    stepX = 80/(len(xAxisNotchValues)-1)
    for i in range(len(xAxisNotchValues)):
        xNotchLine = Rhino.Geometry.Line( Rhino.Geometry.Point3d(originOffset.X + stepX*i, originOffset.Y, originOffset.Z), Rhino.Geometry.Point3d(originOffset.X + stepX*i, originOffset.Y-2, originOffset.Z) )
        xNotchValueOrigin = Rhino.Geometry.Point3d(originOffset.X + stepX*i, originOffset.Y-3, originOffset.Z)
        xAxisNotchLines.append(xNotchLine)
        xAxisNotchValuesOrigins.append(xNotchValueOrigin)
    yAxisNotchLines = []
    yAxisNotchValuesOrigins = []
    stepY = 45/(len(yAxisNotchValues)-1)
    for i in range(len(yAxisNotchValues)):
        yNotchLine = Rhino.Geometry.Line( Rhino.Geometry.Point3d(originOffset.X, originOffset.Y + stepY*i, originOffset.Z), Rhino.Geometry.Point3d(originOffset.X-2, originOffset.Y + stepY*i, originOffset.Z) )
        yNotchValueOrigin = Rhino.Geometry.Point3d(originOffset.X-3, originOffset.Y + stepY*i, originOffset.Z)
        yAxisNotchLines.append(yNotchLine)
        yAxisNotchValuesOrigins.append(yNotchValueOrigin)
    
    # y2Axis NotchLines, NotchValuesOrigins
    y2AxisNotchLines = []
    y2AxisNotchValuesOrigins = []
    oddRoofPitchAnglesLabels = []
    roofPitchAnglesForNotches = [0, 4.5, 9.5, 14, 18.5, 22.5, 26.5, 30.5, 33.75, 37, 40, 42.5, 45, 49.4, 53.13, 56.31, 59.04, 61.39, 63.43]  # 0/12, 1/12, 2/12, 3/12, 4/12, 5/12, 6/12, 7/12, 8/12, 9/12, 10/12, 11/12, 12/12, 14/12, 16/12, 18/12, 20/12, 22/12, 24/12
    allRoofPitchAnglesLabels = ["0/12", "1/12", "2/12", "3/12", "4/12", "5/12", "6/12", "7/12", "8/12", "9/12", "10/12", "11/12", "12/12", "14/12", "16/12", "18/12", "20/12", "22/12", "24/12"]
    for i,angleD in enumerate(roofPitchAnglesForNotches):
        if i%2 == 0:
            y2AxisNotchLine = Rhino.Geometry.Line(Rhino.Geometry.Point3d(originOffset.X + 80, 45/90*angleD+originOffset.Y, originOffset.Z), Rhino.Geometry.Point3d(originOffset.X + 80+2, 45/90*angleD+originOffset.Y, originOffset.Z))
            y2AxisNotchValuesOrigin = Rhino.Geometry.Point3d(originOffset.X + 80+3, 45/90*angleD+originOffset.Y, originOffset.Z)
            label = allRoofPitchAnglesLabels[i]
        else:
            y2AxisNotchLine = Rhino.Geometry.Line(Rhino.Geometry.Point3d(originOffset.X + 80, 45/90*angleD+originOffset.Y, originOffset.Z), Rhino.Geometry.Point3d(originOffset.X + 80+1, 45/90*angleD+originOffset.Y, originOffset.Z))
        y2AxisNotchLines.append(y2AxisNotchLine)
        y2AxisNotchValuesOrigins.append(y2AxisNotchValuesOrigin)
        oddRoofPitchAnglesLabels.append(label)
    
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    if not legendFontSize: legendFontSize = 2
    
    # xAxis, yAxis, y2Axis LabelMeshes
    xAxisNotchValuesMeshes = lb_visualization.text2srf(xAxisNotchValues, xAxisNotchValuesOrigins, legendFont, legendFontSize, legendBold, None, 7)
    xAxisNotchValuesMeshes = [item for subList in xAxisNotchValuesMeshes for item in subList]
    yAxisNotchValuesMeshes = lb_visualization.text2srf(yAxisNotchValues, yAxisNotchValuesOrigins, legendFont, legendFontSize, legendBold, None, 5)
    yAxisNotchValuesMeshes = [item for subList in yAxisNotchValuesMeshes for item in subList]
    y2AxisNotchValuesMeshes = lb_visualization.text2srf(oddRoofPitchAnglesLabels, y2AxisNotchValuesOrigins, legendFont, legendFontSize*0.7, legendBold, None, 3)
    y2AxisNotchValuesMeshes = [item for subList in y2AxisNotchValuesMeshes for item in subList]
    
    # xAxis, yAxis, y2Axis LabelOrigin
    xAxisLabelOrigin = Rhino.Geometry.Point3d(originOffset.X+80/2, originOffset.Y-11, originOffset.Z)
    yAxisLabelOrigin = Rhino.Geometry.Point3d(originOffset.X-10, originOffset.Y + 45/2, originOffset.Z)
    y2AxisLabelOrigin = Rhino.Geometry.Point3d(originOffset.X + 80+12, originOffset.Y+45/2, originOffset.Z)
    
    # xAxis, yAxis, y2Axis LabelMeshes
    xAxisLabelMeshes = lb_visualization.text2srf(["Azimuth ()"], [xAxisLabelOrigin], legendFont, legendFontSize, legendBold, None, 1)[0]
    yAxisLabelMeshes = lb_visualization.text2srf(["Tilt ()"], [yAxisLabelOrigin], legendFont, legendFontSize, legendBold, None, 2)[0]
    y2AxisLabelMeshes = lb_visualization.text2srf(["Roof pitch"], [y2AxisLabelOrigin], legendFont, legendFontSize, legendBold, None, 3)[0]
    
    # title LabelOrigin
    titleLabelOrigin = Rhino.Geometry.Point3d(originOffset.X-6, originOffset.Y-15, originOffset.Z)
    descriptionLabelOrigin = Rhino.Geometry.Point3d(originOffset.X-6, originOffset.Y-22, originOffset.Z)
    TOFoptimal = 100  # always 100%
    TSRFoptimal = 100 # always 100%
    titleLabelText = "Annual total solar radiation as a function of panel tilt/orientation"
    titleLabelMeshes = lb_visualization.text2srf([titleLabelText], [titleLabelOrigin], legendFont, legendFontSize*1.6, legendBold, None, 6)[0]
    descriptionLabelText = "Location: %s, Latitude: %s, Longitude: %s\nOptimal: Tilt: %0.1f, Azimuth: %0.1f, Radiation: %s kWh/m2, TOF: %0.1f, TSRF: %0.1f\nAnalysed: Tilt: %0.1f, Azimuth: %0.1f, Radiation: %s kWh/m2, TOF: %0.1f, TSRF: %0.1f" %(locationName, latitude, longitude, optimalTiltD, optimalAzimuthD, maximalTotalRadiationPerYear, TOFoptimal, TSRFoptimal, srfTiltD, srfAzimuthD, totalRadiationPerYear, TOF, TSRF)
    descriptionLabelMeshes = lb_visualization.text2srf([descriptionLabelText], [descriptionLabelOrigin], legendFont, legendFontSize*1.3, legendBold, None, 6)[0]
    
    # region percent values
    isoCrvPercentsStrings = [str(p) for p in isoCrvPercents]
    percentTextValuesOriginsLifted = [Rhino.Geometry.Point3d(pt.X,pt.Y,pt.Z+tol) for pt in percentTextValuesOrigins]  # "pt.Z+tol" due to overlap with "mesh"
    regionPercentValuesMeshes = lb_visualization.text2srf(isoCrvPercentsStrings, percentTextValuesOriginsLifted, legendFont, legendFontSize*0.5, legendBold, None, 4)
    regionPercentValuesMeshes = [item for subList in regionPercentValuesMeshes for item in subList]
    
    # last (100%) region percent value
    lastIsoCrvTextValueOrigin = projectedLastIsoCrvs[0].PointAtLength(projectedLastIsoCrvs[0].GetLength()/2)
    lastIsoCrvTextValueOriginMoved = Rhino.Geometry.Point3d(lastIsoCrvTextValueOrigin.X+1.5, lastIsoCrvTextValueOrigin.Y, lastIsoCrvTextValueOrigin.Z+tol)
    lastRegionPercentValuesMeshes = lb_visualization.text2srf(["100"], [lastIsoCrvTextValueOriginMoved], legendFont, legendFontSize*0.5, legendBold, None, 4)
    lastRegionPercentValuesMeshes = [item for subList in lastRegionPercentValuesMeshes for item in subList]
    
    
    meshes = [mesh] + xAxisNotchValuesMeshes + yAxisNotchValuesMeshes + y2AxisNotchValuesMeshes + xAxisLabelMeshes + yAxisLabelMeshes + y2AxisLabelMeshes + titleLabelMeshes + descriptionLabelMeshes + regionPercentValuesMeshes + lastRegionPercentValuesMeshes
    xAxisNotchCrvs = [line.ToNurbsCurve() for line in xAxisNotchLines]
    yAxisNotchCrvs = [line.ToNurbsCurve() for line in yAxisNotchLines]
    y2AxisNotchCrvs = [line.ToNurbsCurve() for line in y2AxisNotchLines]
    curves = xAxisNotchCrvs + yAxisNotchCrvs + y2AxisNotchCrvs + cuttedProjectedIsoCrvs + projectedLastIsoCrvs
    geometry = meshes + curves
    
    # scaling
    if scale != 1:
        plane = sc.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
        plane.Origin = originOffset
        tmScale = Rhino.Geometry.Transform.Scale(plane, scale,scale,scale)
        for item in geometry+[analysisPt]:
            try:
                for subitem in item:
                    subitem.Transform(tmScale)
            except:
                item.Transform(tmScale)
    
    return geometry


def legendGeometry(legendPar, meshPts, totalRadiationPerYearL):
    
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    if legendBasePoint == None:
        legendBasePoint = Rhino.Geometry.Point3d(meshPts[precision].X+25, meshPts[precision].Y, meshPts[precision].Z)
    
    if scale != 1:
        plane = sc.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
        plane.Origin = originOffset
        tmScale = Rhino.Geometry.Transform.Scale(plane, scale,scale,scale)
        legendBasePoint.Transform(tmScale)
    
    # generate the legend
    totalRadiationPerYearLint = [annualEpoa/1000 for annualEpoa in totalRadiationPerYearL]
    lb_visualization.calculateBB([mesh])
    legendSrfs, legendText, legendTextSrfs, textPt, textSize = lb_visualization.createLegend(totalRadiationPerYearLint, lowB, highB, numSeg, "Annual radiation (kWh/m2)", lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    # generate legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    legend = [legendSrfs] + lb_preparation.flattenList(legendTextSrfs)
    legendPlusLegendBasePoint = legend + [legendBasePoint]
    
    # hide originPt, legendBasePt outputs
    ghenv.Component.Params.Output[12].Hidden= True
    ghenv.Component.Params.Output[15].Hidden= True
    
    return legend, legendBasePoint


def bakingGrouping(locationName, geometry, legend, analysisPt, TOF, TSRF):
    
    layerName = str(TOF) + "%_" + locationName
    layerIndex, l = lb_visualization.setupLayers(layerName, "LADYBUG", "TOF", "PHOTOVOLTAICS")
    
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex = layerIndex
    attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    attr.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
    
    geometry = geometry + legend + [Rhino.Geometry.Point(analysisPt)]
    # bake geometry, legend, analysisPt
    geometryIds = []
    for obj in geometry:
        id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj,attr)
        geometryIds.append(id)
    
    # grouping
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add("TOF_" + str(l) + "_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, geometryIds)


def printOutput(north, latitude, longitude, locationName, albedoL, srfArea, precision, scale, origin):
    resultsCompletedMsg = "Tilt and orientation factor component results successfully completed!"
    printOutputMsg = \
    """
Input data:

Location (): %s
Latitude (): %s
Longitude (): %s
North (): %s
Average annual albedo(-): %0.2f

Surface area (m2): %0.2f
Precision: %s
Scale: %s
Origin: %0.2f,%0.2f,%0.2f
    """ % (locationName, latitude, longitude, north, sum(albedoL)/8760, srfArea, precision, scale, origin.X, origin.Y, origin.Z)
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
            locationName, latitude, longitude, timeZone, directNormalRadiation, diffuseHorizontalRadiation, years, months, days, hours, HOYs, annualShading, albedoL, precision, scale, origin, originOffset, legendPar, validEpwData, printMsg = getEpwData(_epwFile, annualShading_, albedo_, precision_, scale_, origin_, legendPar_)
            if validEpwData:
                PVsurfaceInputType, srfArea, validPVsurfaceData, printMsg = PVsurfaceInputData(_PV_SWHsurface)
                if validPVsurfaceData:
                    # all inputs ok
                    if _runIt:
                        anglesClockwise = True; PVsurfaceTiltAngle_ = None; PVsurfaceAzimuthAngle_ = None
                        srfAzimuthD, surfaceTiltDCalculated = lb_photovoltaics.srfAzimuthAngle(PVsurfaceAzimuthAngle_, PVsurfaceInputType, _PV_SWHsurface, latitude)
                        correctedSrfAzimuthD, northDeg, validNorth, printMsg = lb_photovoltaics.correctSrfAzimuthDforNorth(north_, srfAzimuthD)
                        srfTiltD = lb_photovoltaics.srfTiltAngle(PVsurfaceTiltAngle_, surfaceTiltDCalculated, PVsurfaceInputType, _PV_SWHsurface, latitude)
                        totalRadiationPerYearL, maximalTotalRadiationPerYear, totalRadiationPerYear, meshPts, mesh, projectedIsoCrvs, projectedLastIsoCrvs, isoCrvPercents, optimalAzimuthD, optimalTiltD, optimalRoofPitch, analysisPt, TOF, TSRF = main(latitude, longitude, timeZone, locationName, years, months, days, hours, HOYs, srfArea, srfTiltD, srfAzimuthD, correctedSrfAzimuthD, directNormalRadiation, diffuseHorizontalRadiation, albedoL, precision, originOffset)
                        geometry = createGeometry(totalRadiationPerYearL, totalRadiationPerYear, mesh, optimalTiltD, optimalAzimuthD, TOF, TSRF, projectedIsoCrvs, projectedLastIsoCrvs, isoCrvPercents, originOffset, legendPar, locationName, latitude, longitude)
                        legend, legendBasePt = legendGeometry(legendPar, meshPts, totalRadiationPerYearL)
                        if bakeIt_: bakingGrouping(locationName, geometry, legend, analysisPt, TOF, TSRF)
                        printOutput(northDeg, latitude, longitude, locationName, albedoL, srfArea, precision, scale, origin)
                        PVsurfaceTilt = srfTiltD; PVsurfaceAzimuth = srfAzimuthD; optimalTilt = optimalTiltD; optimalAzimuth = optimalAzimuthD; optimalRadiation = maximalTotalRadiationPerYear; originPt = origin
                    else:
                        print "All inputs are ok. Please set the \"_runIt\" to True, in order to run the Tilt and orientation factor component."
                else:
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