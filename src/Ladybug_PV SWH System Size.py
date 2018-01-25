# PV SWH system size
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Djordje Spasic <djordjedspasic@gmail.com> 
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
Use this component to generate the PVsurface or SWHsurface for "Photovoltaics surface" or "Solar Water Heating surface" components, based on initial PV or SWH system sizes.
-
Provided by Ladybug 0.0.66
    
    input:
        _location: The output from the "importEPW" or "constructLocation" component.  This is essentially a list of text summarizing a location on the earth.
        systemSize_: 1) In case of PV array: DC (Direct current) power rating of the photovoltaic array in kilowatts (kW) at standard test conditions (STC). 
                     2) In case of SWH array: Capacity of the collectors array in thermal kilowatts (kw) at global or local testing conditions (ISO 9806, EN 12975, ASHRAE 93 ...)
                     -
                     If not supplied, 4 kW will be used as a default.
                     -
                     In kiloWatts (kW) or thermal kiloWatts (kWt).
        arrayTiltAngle_: An angle from horizontal of the inclination of the PV/SWH array plane. Example: 0 = horizontal, 90 = vertical. (range 0-180)
                         -
                         To get the maximal amount of energy, input the "optimalTilt" output from "Tilt And Orientation Factor"'s component.
                         -
                         If not supplied, location's latitude will be used as default value.
                         -
                         In degrees ().
        arrayAzimuthAngle_: The orientation angle (clockwise from the true north) of the PV/SWH array plane's normal vector. (range 0-360)
                            -
                            To get the maximal amount of energy, input the "optimalAzimuth" output from "Tilt And Orientation Factor"'s component.
                            -
                            If not supplied, the following values will be used as default: 180 (due south) for northern hemisphere, 0 (due north) for southern hemisphere.
                            -
                            In degrees().
        tiltedArrayHeight_: The height of the array, measured in the tilted plane.
                            It is depends on the height/width of the PV module/SWH collector. It also depends on the way modules/collectors are positioned in PV/SWH array (vertically or horizontally).
                            It can vary from 1 to 2.3 meters x number of modules/collectors in a single PV/SWH column.
                            -
                            If not supplied, default value of 1.6 meters (with a single PV module/SWH collector per row) will be used.
                            -
                            In meters.
        numberOfRows_: Number of rows to which PV or SWH array will be divided to.
                       -
                       If not supplied, 1 will be used as a default value (PV/SWH array will have only 1 row).
        skewRowsDistance_: Distance in meters by which PV/SWH rows will be skewed.
                           Use positive distance to skew the rows to the left.
                           And negative distance to skew the rows to the right.
                           -
                           It requires the "numberOfRows_" to be larger than 1 in order to be able to skew the rows.
                           -
                           If not supplied, 0 will be used as a default (no rows skewing).
        minimalSpacingPeriod_: Analysis period for which the minimal spacing distance between PV modules/SWH collector rows will derived of.
                               In general this analysis period is taken from 9 to 15 hour on a day at which sun is at its lowest position during a year. That is 21th December in Northern and 21th June in Southern hemisphere (winter and summer solstice).
                               However, this may not be economical for locations with higher latitudes due to low electricity generation during December/June.
                               -
                               So the following "minimalSpacingPeriod_" should be used based on location's latitude:
                               * latitude <= 44: 21. December (northern hemisphere) / 21. June (southern hemisphere). 9-15hours
                               * latitude 44 - 53: 15. November or 15. January (northern hemisphere) / 15. May or 15. July (southern hemisphere). 9-15hours
                               * latitude 53 - 57: 15. October or 15. February (northern hemisphere) / 15. April or 15. August (southern hemisphere). 9-15hours
                               * latitude > 57: 15. September or 15. March (for both northern and southern hemisphere). 9-15hours
                               -
                               It requires the "numberOfRows_" to be larger than 1 in order visualize the minimal spacing between rows.
                               -
                               Use Ladybug "Analysis Period" component to define this input.
                               -
                               If not supplied, it will be calculated based on upper mentioned criteria.
        baseSurface_: Surface on which PV/SWH array will be laid onto.
                      This can be a surface of an angled or flat roof. Or an angled or flat terrain. A facade of a building etc.
                      -
                      If not supplied, a regular horizontal surface in Rhino's XY plane will be used, as a default.
        arrayOriginPt_: UV coordinate of baseSurface_ at which PV_SWH array will start.
                        It ranges from 0 to 1.0 for both U and V coordinate.
                        Use grasshopper's "Construct Point" or "MD slider" components to input it.
                        -
                        If not supplied, (0.5,0,0) will be used as a default value.
        arrayOriginCorner_: Corner at which the PV/SWH array begins:
                            -
                            0 - center bottom
                            1 - left bottom
                            2 - right bottom
                            3 - center top
                            -
                            If not supplied, 0 will be used as a default (bottom center).
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        energyLoadPerHour_: A list of energy load values for each hour, during a year.
                            1) In case of PV array: Electrical energy used for any kind of load: heating, cooling, electric lights, solar water heating circulation pump etc.
                               Use Honeybee "Read EP Result" component or any other one to generate it.
                               -
                            2) In case of SWH array: Thermal heating energy (or electrical energy) required to heat domestic hot water and/or space heating load and/or space cooling load.
                               Use Ladybug "Residential Hot Water" or "Commercial Public Apartment Hot Water" components to calculate it (simply plugin their "heatingLoadPerHour" outputs).
                               -
                               The purpose of this input is to divide the energy loads to each PV/SWH array rows.
                            -
                            If not inputted, "energyLoadPerRowPerHour" output will not be calculated.
    
    output:
        readMe!: ...
        PV_SWHsurface: Surfaces on which PV modules/SWH collectors will be laid on.
        PV_SWHsurfacesArea: Total area of the PV_SWHsurfaces.
                            -
                            In Rhino documents units (meters, centimeters, feets...).
        minimalSpacing: Minimal distance between fixed (anchor) points of rows.
                        The distance is measured on the ground (or along the base surface if it has been inputted).
                        -
                        In meters.
        minimalSpacingDate: Exact date taken from "minimalSpacingPeriod_" input for which minimal spacing between rows has been calculated.
        originPt: Origin point of the PV / SWH array.
        energyLoadPerRowPerHour: "energyLoadPerHour_" input's data divided to rows.
"""

ghenv.Component.Name = "Ladybug_PV SWH System Size"
ghenv.Component.NickName = "PV_SWH_SystemSize"
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Renewables"
#compatibleLBVersion = VER 0.0.64\nAPR_12_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import Grasshopper as grass
import scriptcontext as sc
import Rhino
import math


def changeInputNamesAndDescriptions(inputIndex, inputtedOrNot):
    
    inputNickNames = [["_PVmoduleSettings", "-"], ["_SWHsystemSettings", "-"]]
    inputDescriptions = [ 
     ["A list of PV module settings. Use the \"Simplified Photovoltaics Module\" or \"Import CEC Photovoltaics Module\" or \"Import Sandia Photovoltaics Module\" components to generate them.", 
      "This inputt is not necessary. If you would like to calculate SWH surface, only the data you inputted to _SWHsystemSettings is required (not to this _PVmoduleSettings also)."],
     ["A list of all SWH system settings. Use the \"Solar Water Heating System\" or \"Solar Water Heating System Detailed\" components to generate them.",
      "This inputt is not necessary. If you would like to calculate PV surface, only the data you inputted to _PVmoduleSettings is required (not to this _SWHsystemSettings also)."]
     ]
    
    ghenv.Component.Params.Input[inputIndex].Name = inputNickNames[inputIndex-1][inputtedOrNot]
    ghenv.Component.Params.Input[inputIndex].NickName = inputNickNames[inputIndex-1][inputtedOrNot]
    ghenv.Component.Params.Input[inputIndex].Description = inputDescriptions[inputIndex-1][inputtedOrNot]


def checkInputData(location, PVmoduleSettings, SWHsystemSettings, systemSize, arrayTiltD, arrayAzimuthD, tiltedArrayHeight, numberOfRows, skewRowsDistance, minimalSpacingPeriod, baseBrep, arrayOriginPt, arrayOriginCorner, north, energyLoadPerHour, unitConversionFactor):
    
    if (location == None):
        locationName = latitude = longitude = timeZone = northDeg = systemSize = srfArea = arrayTiltR = arrayAzimuthR = arrayAzimuthVec = tiltedArrayHeight = numberOfRows = skewRowsDistance = days = months = hours = sunAltitudeR_L = sunAzimuthR_L = minimalSpacingPeriod1 = minimalSpacingPeriod2 = baseSurfaceUV = arrayOriginPt = groundTiltR = arrayOriginCorner = moduleEfficiency = moduleActiveAreaPercent = collectorOpticalEfficiency = collectorThermalLoss = collectorActiveAreaPercent = energyLoadPerRowPerHourDataTree = None
        validInputData = False
        printMsg = "Please input _location from \"Import EPW\" or \"Construct Location\" components."
        return locationName, latitude, longitude, timeZone, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, skewRowsDistance, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, minimalSpacingPeriod1, minimalSpacingPeriod2, baseSurfaceUV, arrayOriginPt, groundTiltR, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, energyLoadPerRowPerHourDataTree, validInputData, printMsg
    else:
        locationName, latitude, longitude, timeZone, elevation = lb_preparation.decomposeLocation(location)
        latitude = float(latitude)
        longitude = float(longitude)
        timeZone = float(timeZone)
    
    if (north == None):
        northDeg = 0
    else:
        northDeg = north
        # check if north is valid
        correctedSrfAzimuthD_dummy, northDeg, validNorth, printMsg = lb_photovoltaics.correctSrfAzimuthDforNorth(northDeg, 0)
        if (validNorth == False):
            locationName = latitude = longitude = timeZone = northDeg = systemSize = srfArea = arrayTiltR = arrayAzimuthR = arrayAzimuthVec = tiltedArrayHeight = numberOfRows = skewRowsDistance = days = months = hours = sunAltitudeR_L = sunAzimuthR_L = minimalSpacingPeriod1 = minimalSpacingPeriod2 = baseSurfaceUV = arrayOriginPt = groundTiltR = arrayOriginCorner = moduleEfficiency = moduleActiveAreaPercent = collectorOpticalEfficiency = collectorThermalLoss = collectorActiveAreaPercent = energyLoadPerRowPerHourDataTree = None
            validInputData = False
            return locationName, latitude, longitude, timeZone, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, skewRowsDistance, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, minimalSpacingPeriod1, minimalSpacingPeriod2, baseSurfaceUV, arrayOriginPt, groundTiltR, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, energyLoadPerRowPerHourDataTree, validInputData, printMsg
    
    if (systemSize == None) or (systemSize <= 0):
        systemSize = 4  # default value in kw
    
    if (arrayTiltD == None):
        #arrayTiltD = 3.7 + 0.69 * abs(latitude)   # initial optimal tilt angle by "Handbook of Photovoltaic Science and Engineering", A. Luque, S. Hegedus, Wiley, 2003.
        arrayTiltD = abs(latitude)  # default value
    arrayTiltR = math.radians(arrayTiltD)
    
    if (arrayAzimuthD == None):
        if latitude >= 0:
            # northern hemisphere
            arrayAzimuthD = 180  # due south, not explicitly 180 degrees (it can be changed according to north_ input)
        elif latitude < 0:
            # southern hemisphere
            arrayAzimuthD = 0  # due north, not explicitly 0 degrees (it can be changed according to north_ input)
    if arrayAzimuthD > 360: arrayAzimuthD = arrayAzimuthD - 360
    if arrayAzimuthD < 0: arrayAzimuthD = 360 - abs(arrayAzimuthD)
    
    if (arrayAzimuthAngle_ == None):
        # arrayAzimuthAngle_ NOT inputted
        correctedSrfAzimuthD, northDeg_dummy, validNorth, printMsg = lb_photovoltaics.correctSrfAzimuthDforNorth(northDeg, arrayAzimuthD)
    elif (arrayAzimuthAngle_ != None):
        # arrayAzimuthAngle_ inputted. Never correct the final "PV_SWHsurface" surface for north (northDeg = 0)
        correctedSrfAzimuthD, northDeg_dummy, validNorth, printMsg = lb_photovoltaics.correctSrfAzimuthDforNorth(0, arrayAzimuthD)
    
    arrayAzimuthRdummy, arrayAzimuthVec = lb_photovoltaics.angle2northClockwise(correctedSrfAzimuthD)
    arrayAzimuthR = math.radians(correctedSrfAzimuthD)
    
    
    if (tiltedArrayHeight == None) or (tiltedArrayHeight <= 0):
        tiltedArrayHeight = 1.6  # default, in meters
    else:
        tiltedArrayHeight = tiltedArrayHeight/unitConversionFactor
    
    if (numberOfRows == None) or (numberOfRows <= 0):
        numberOfRows = 1  # default
    
    if (skewRowsDistance == None):
        skewRowsDistance = 0  # default, no skewing
    else:
        skewRowsDistance = skewRowsDistance/unitConversionFactor
    
    if (baseBrep == None):
        xyPlane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,0), Rhino.Geometry.Vector3d(0,0,1))
        arrayRectangle = Rhino.Geometry.Rectangle3d(xyPlane, Rhino.Geometry.Interval(-tiltedArrayHeight,tiltedArrayHeight), Rhino.Geometry.Interval(0,-tiltedArrayHeight))
        baseBrep = Rhino.Geometry.Brep.CreatePlanarBreps([arrayRectangle.ToNurbsCurve()])[0]
        baseBrep.Flip()
    baseSurface = baseBrep.Faces[0]
    reparametarizedDomain = Rhino.Geometry.Interval(0,1)
    baseSurface.SetDomain(0,reparametarizedDomain)
    baseSurface.SetDomain(1,reparametarizedDomain)
    
    PVsurfaceAzimuthAngle = None  # arrayAzimuthD
    PVsurfaceInputType = "brep"
    srfAzimuthD, surfaceTiltDCalculated = lb_photovoltaics.srfAzimuthAngle(PVsurfaceAzimuthAngle, PVsurfaceInputType, baseBrep, latitude)
    PVsurfaceTiltAngle = None
    groundTiltD = lb_photovoltaics.srfTiltAngle(PVsurfaceTiltAngle, surfaceTiltDCalculated, PVsurfaceInputType, baseBrep, latitude)
    groundTiltR = math.radians(groundTiltD)
    
    if (len(minimalSpacingPeriod) != 0) and (minimalSpacingPeriod[0] != None):
        minimalSpacingPeriodHOYs, months, days = lb_preparation.getHOYsBasedOnPeriod(minimalSpacingPeriod, 1)
        minimalSpacingPeriodStartHOY = minimalSpacingPeriodHOYs[0]
        minimalSpacingPeriodEndHOY = minimalSpacingPeriodHOYs[-1]
        if minimalSpacingPeriodStartHOY == minimalSpacingPeriodEndHOY:
            locationName = latitude = longitude = timeZone = northDeg = systemSize = srfArea = arrayTiltR = arrayAzimuthR = arrayAzimuthVec = tiltedArrayHeight = numberOfRows = skewRowsDistance = days = months = hours = sunAltitudeR_L = sunAzimuthR_L = minimalSpacingPeriod1 = minimalSpacingPeriod2 = baseSurfaceUV = arrayOriginPt = groundTiltR = arrayOriginCorner = moduleEfficiency = moduleActiveAreaPercent = collectorOpticalEfficiency = collectorThermalLoss = collectorActiveAreaPercent = energyLoadPerRowPerHourDataTree = None
            validInputData = False
            printMsg = "Start and End time of your \"minimalSpacingPeriod_\" input are the same. Please input a valid \"minimalSpacingPeriod_\" input."
            return locationName, latitude, longitude, timeZone, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, skewRowsDistance, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, minimalSpacingPeriod1, minimalSpacingPeriod2, baseSurfaceUV, arrayOriginPt, groundTiltR, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, energyLoadPerRowPerHourDataTree, validInputData, printMsg
        else:
            # minimalSpacingPeriod input ok
            minimalSpacingPeriod1 = minimalSpacingPeriod2 = minimalSpacingPeriod
    
    else:
        # nothing inputted in "minimalSpacingPeriod_"
        if (arrayTiltR < groundTiltR):  ## specific for angled PV arrays attached to a vertical building wall, or highly angled building wall
            # highest sunAltitudeD angle
            if latitude >= 0:  # northern hemisphere
                # 21. June 9-15h
                minimalSpacingPeriod1 = [(6, 21, 9), (6, 21, 15)]
                minimalSpacingPeriod2 = [(6, 21, 9), (6, 21, 15)]
            elif latitude < 0:  # southern hemisphere
                # 21. December 9-15h
                minimalSpacingPeriod1 = [(12, 21, 9), (12, 21, 15)]
                minimalSpacingPeriod2 = [(12, 21, 9), (12, 21, 15)]
        
        else: ## for ground arrays, or lower angled roofs
            if (latitude >= 0):  # northern hemisphere
                if (latitude <= 44):
                    # 21. December 9-15h
                    minimalSpacingPeriod1 = [(12, 21, 9), (12, 21, 15)]
                    minimalSpacingPeriod2 = [(12, 21, 9), (12, 21, 15)]
                elif (latitude > 44) and (latitude <= 53):
                    # 15. January/November 9-15h
                    minimalSpacingPeriod1 = [(11, 15, 9), (11, 15, 15)]
                    minimalSpacingPeriod2 = [(1, 15, 9), (1, 15, 15)]
                elif (latitude > 53) and (latitude <= 57):
                    # 15. February/October 9-15h
                    minimalSpacingPeriod1 = [(10, 15, 9), (10, 15, 15)]
                    minimalSpacingPeriod2 = [(2, 15, 9), (2, 15, 15)]
                elif (latitude > 57):
                    # 15. March/September 9-15h
                    minimalSpacingPeriod1 = [(9, 15, 9), (9, 15, 15)]
                    minimalSpacingPeriod2 = [(3, 15, 9), (3, 15, 15)]
            
            elif latitude < 0:  # southern hemisphere
                if (latitude >= -44):
                    # 21. June 9-15h
                    minimalSpacingPeriod1 = [(6, 21, 9), (6, 21, 15)]
                    minimalSpacingPeriod2 = [(6, 21, 9), (6, 21, 15)]
                elif (latitude < -44) and (latitude >= -53):
                    # 15. May/July 9-15h
                    minimalSpacingPeriod1 = [(5, 15, 9), (5, 15, 15)]
                    minimalSpacingPeriod2 = [(7, 15, 9), (7, 15, 15)]
                elif (latitude < -53) and (latitude >= -57):
                    # 15. April/August 9-15h
                    minimalSpacingPeriod1 = [(4, 15, 9), (4, 15, 15)]
                    minimalSpacingPeriod2 = [(8, 15, 9), (8, 15, 15)]
                elif (latitude < -57):
                    # 15. March/September 9-15h
                    minimalSpacingPeriod1 = [(3, 15, 9), (3, 15, 15)]
                    minimalSpacingPeriod2 = [(9, 15, 9), (9, 15, 15)]
    
    if (arrayOriginPt == None):
        baseSurfaceUV = [(baseSurface.Domain(0)[0]+baseSurface.Domain(0)[1]) / 2, 0]
    else:
        baseSurfaceUV = [arrayOriginPt.X, arrayOriginPt.Y]
    arrayOriginPt = baseSurface.PointAt(baseSurfaceUV[0], baseSurfaceUV[1])
    # hide internalized "arrayOriginPt_" input's value
    ghenv.Component.Params.Input[12].Hidden = True
    
    if (arrayOriginCorner == None) or (arrayOriginCorner < 0) or (arrayOriginCorner > 3):
        arrayOriginCorner = 0  # bottom center origin
    
    
    len_PVmoduleSettings = ghenv.Component.Params.Input[1].VolatileDataCount
    len_SWHsystemSettings = ghenv.Component.Params.Input[2].VolatileDataCount
    # calculate srfArea
    if (len_PVmoduleSettings != 0) and (len_SWHsystemSettings != 0):  # data inputted into both PVmoduleSettings_ and SWHsystemSettings_ inputs
        # assign descriptions to _PVmoduleSettings and _SWHsystemSettings inputs
        changeInputNamesAndDescriptions(1, 0)
        changeInputNamesAndDescriptions(2, 0)
        locationName = latitude = longitude = timeZone = northDeg = systemSize = srfArea = arrayTiltR = arrayAzimuthR = arrayAzimuthVec = tiltedArrayHeight = numberOfRows = skewRowsDistance = days = months = hours = sunAltitudeR_L = sunAzimuthR_L = minimalSpacingPeriod1 = minimalSpacingPeriod2 = baseSurfaceUV = arrayOriginPt = groundTiltR = arrayOriginCorner = moduleEfficiency = moduleActiveAreaPercent = collectorOpticalEfficiency = collectorThermalLoss = collectorActiveAreaPercent = energyLoadPerRowPerHourDataTree = None
        validInputData = False
        printMsg = "Do not input data to _PVmoduleSettings, along with _SWHsystemSettings.\n\n" +\
                   "If you would like to calculate PV surface, input data to _PVmoduleSettings only (not to _SWHsystemSettings also).\n" +\
                   "If you would like to calculate SWH surface, input data to _SWHsystemSettings only (not to _PVmoduleSettings also).\n"
        return locationName, latitude, longitude, timeZone, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, skewRowsDistance, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, minimalSpacingPeriod1, minimalSpacingPeriod2, baseSurfaceUV, arrayOriginPt, groundTiltR, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, energyLoadPerRowPerHourDataTree, validInputData, printMsg
    
    if (len_PVmoduleSettings != 0) and (len_SWHsystemSettings == 0):  # data inputted to PVmoduleSettings_ but not to SWHsystemSettings_ input
        changeInputNamesAndDescriptions(2, 1)
        if (len_PVmoduleSettings == 9):
            # 4 items inputted into "PVmoduleSettings_"
            moduleModelName, mountTypeName, moduleMaterial, mountType, moduleActiveAreaPercent, moduleEfficiency, temperatureCoefficientFraction, a, b, deltaT = lb_photovoltaics.deconstruct_PVmoduleSettings(PVmoduleSettings)
            collectorOpticalEfficiency = collectorThermalLoss = collectorActiveAreaPercent = None
            
            activeArea = systemSize / (1 * (moduleEfficiency/100))  # area in m2
            srfArea = activeArea * (100/moduleActiveAreaPercent) / (unitConversionFactor*unitConversionFactor)  # area in Rhino document units, PV system srfArea
        elif (len_PVmoduleSettings == 23):
            moduleModelName, moduleName, material, moduleMountType, moduleAreaM, moduleActiveAreaPercent, nameplateDCpowerRating_m, moduleEfficiency, Vmp_ref, Imp_ref, Voc_ref, Isc_ref, alpha_sc_ref, beta_oc_ref, IL_ref, Io_ref, Rs_ref, Rsh_ref, A_ref, n_s, adjust, gamma_r_ref, ws_adjusted_factor, Tnoct_adj = lb_photovoltaics.deconstruct_PVmoduleSettings(PVmoduleSettings)
            collectorOpticalEfficiency = collectorThermalLoss = collectorActiveAreaPercent = None
            
            moduleEfficiency = round( (Imp_ref * Vmp_ref) / (1000 * moduleAreaM * (moduleActiveAreaPercent/100))  * 100 ,2) # in percent (formula from SAM Technical Reference equation (9.33))
            activeArea = systemSize / (1 * (moduleEfficiency/100))  # area in m2
            srfArea = activeArea * (100/moduleActiveAreaPercent) / (unitConversionFactor*unitConversionFactor)  # area in Rhino document units, PV system srfArea
        elif (len_PVmoduleSettings == 36):
            moduleModelName, moduleName, material, moduleMountType, moduleAreaM, moduleActiveAreaPercent, nameplateDCpowerRating_m, moduleEfficiency, Vmp_ref, Imp_ref, Voc_ref, Isc_ref, alpha_sc_ref, beta_oc_ref, beta_mp_ref, mu_betamp, s, n, Fd, a0, a1, a2, a3, a4, b0, b1, b2, b3, b4, b5, C0, C1, C2, C3, a, b, deltaT = lb_photovoltaics.deconstruct_PVmoduleSettings(PVmoduleSettings)
            collectorOpticalEfficiency = collectorThermalLoss = collectorActiveAreaPercent = None
            
            moduleEfficiency = round( (Imp_ref * Vmp_ref) / (1000 * moduleAreaM * (moduleActiveAreaPercent/100))  * 100 ,2) # in percent (formula from SAM Technical Reference equation (9.33))
            activeArea = systemSize / (1 * (moduleEfficiency/100))  # area in m2
            srfArea = activeArea * (100/moduleActiveAreaPercent) / (unitConversionFactor*unitConversionFactor)  # area in Rhino document units, PV system srfArea
        elif (len_PVmoduleSettings != 9) and (len_PVmoduleSettings != 23) and (len_PVmoduleSettings != 36):
            # not 4 items inputted into "PVmoduleSettings_"
            locationName = latitude = longitude = timeZone = northDeg = systemSize = srfArea = arrayTiltR = arrayAzimuthR = arrayAzimuthVec = tiltedArrayHeight = numberOfRows = skewRowsDistance = days = months = hours = sunAltitudeR_L = sunAzimuthR_L = minimalSpacingPeriod1 = minimalSpacingPeriod2 = baseSurfaceUV = arrayOriginPt = groundTiltR = arrayOriginCorner = moduleEfficiency = moduleActiveAreaPercent = collectorOpticalEfficiency = collectorThermalLoss = collectorActiveAreaPercent = energyLoadPerRowPerHourDataTree = None
            validInputData = False
            printMsg = "Your \"_PVmoduleSettings\" input is incorrect. Please use \"PVmoduleSettings\" output from \"Simplified Photovoltaics Module\" or \"Import CEC Photovoltaics Module\" or \"Import Sandia Photovoltaics Module\" component."
            return locationName, latitude, longitude, timeZone, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, skewRowsDistance, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, minimalSpacingPeriod1, minimalSpacingPeriod2, baseSurfaceUV, arrayOriginPt, groundTiltR, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, energyLoadPerRowPerHourDataTree, validInputData, printMsg
    
    elif (len_PVmoduleSettings == 0) and (len_SWHsystemSettings != 0):  # data not inputted to PVmoduleSettings_ but inputted to SWHsystemSettings_ input
        changeInputNamesAndDescriptions(1, 1)
        if (len_SWHsystemSettings == 23):
            # 23 items inputted into "SWHsystem_"
            collectorOpticalEfficiency = SWHsystemSettings[0]
            collectorThermalLoss = SWHsystemSettings[1]
            collectorActiveAreaPercent = SWHsystemSettings[2]
            workingFluidHeatCapacity = SWHsystemSettings[3]
            flowRatePerM2 = SWHsystemSettings[4]
            IAMcoefficient = SWHsystemSettings[5]
            skyViewFactor = SWHsystemSettings[6]
            beamIndexPerHourData = SWHsystemSettings[7]
            maxWorkingTemperature = SWHsystemSettings[8]
            dischargeTemperature = SWHsystemSettings[9]
            deliveryWaterTemperature = SWHsystemSettings[10]
            avrJanuaryColdWaterTemperature = SWHsystemSettings[11]
            mechanicalRoomTemperatureData = SWHsystemSettings[12]
            pipeLength = SWHsystemSettings[13]
            pipeDiameterMM = SWHsystemSettings[14]
            pipeInsulationThicknessMM = SWHsystemSettings[15]
            pipeInsulationConductivity = SWHsystemSettings[16]
            pumpPower = SWHsystemSettings[17]
            pumpEfficiency = SWHsystemSettings[18]
            tankSizeLiters = SWHsystemSettings[19]
            tankLoss = SWHsystemSettings[20]
            heightDiameterTankRatio = SWHsystemSettings[21]
            heatExchangerEffectiveness = SWHsystemSettings[22]
            moduleEfficiency = moduleActiveAreaPercent = None
            
            activeArea = (systemSize + (collectorThermalLoss * 30/1000))/collectorOpticalEfficiency  # area in m2
            srfArea = activeArea * (100/collectorActiveAreaPercent) / (unitConversionFactor*unitConversionFactor)  # area in Rhino document units, SWH system srfArea
        elif (len_SWHsystemSettings != 23):
            # not 23 items inputted into "SWHsystem_"
            locationName = latitude = longitude = timeZone = northDeg = systemSize = srfArea = arrayTiltR = arrayAzimuthR = arrayAzimuthVec = tiltedArrayHeight = numberOfRows = skewRowsDistance = days = months = hours = sunAltitudeR_L = sunAzimuthR_L = minimalSpacingPeriod1 = minimalSpacingPeriod2 = baseSurfaceUV = arrayOriginPt = groundTiltR = arrayOriginCorner = moduleEfficiency = moduleActiveAreaPercent = collectorOpticalEfficiency = collectorThermalLoss = collectorActiveAreaPercent = energyLoadPerRowPerHourDataTree = None
            validInputData = False
            printMsg = "Your \"_SWHsystemSettings\" input is incorrect. Please use \"SWHsystemSettings\" outputs from \"Solar Water Heating system\" or \"Solar Water Heating system detailed\" components."
            return locationName, latitude, longitude, timeZone, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, skewRowsDistance, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, minimalSpacingPeriod1, minimalSpacingPeriod2, baseSurfaceUV, arrayOriginPt, groundTiltR, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, energyLoadPerRowPerHourDataTree, validInputData, printMsg
    
    if (len_PVmoduleSettings == 0) and (len_SWHsystemSettings == 0):  # data inputted neither into both PVmoduleSettings_ nor SWHsystemSettings_ inputs
        locationName = latitude = longitude = timeZone = northDeg = systemSize = srfArea = arrayTiltR = arrayAzimuthR = arrayAzimuthVec = tiltedArrayHeight = numberOfRows = skewRowsDistance = days = months = hours = sunAltitudeR_L = sunAzimuthR_L = minimalSpacingPeriod1 = minimalSpacingPeriod2 = baseSurfaceUV = arrayOriginPt = groundTiltR = arrayOriginCorner = moduleEfficiency = moduleActiveAreaPercent = collectorOpticalEfficiency = collectorThermalLoss = collectorActiveAreaPercent = energyLoadPerRowPerHourDataTree = None
        validInputData = False
        printMsg = "If you would like to calculate PV surface, input data to _PVmoduleSettings (not to _SWHsystemSettings also).\n" +\
                   "If you would like to calculate SWH surface, input data to _SWHsystemSettings (not to _PVmoduleSettings also)."
        return locationName, latitude, longitude, timeZone, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, skewRowsDistance, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, minimalSpacingPeriod1, minimalSpacingPeriod2, baseSurfaceUV, arrayOriginPt, groundTiltR, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, energyLoadPerRowPerHourDataTree, validInputData, printMsg
    
    
    if (len(energyLoadPerHour) == 0) or (energyLoadPerHour[0] == None):
        energyLoadPerRowPerHour = []
    else:
        if (len(energyLoadPerHour) == 8767):
            energyLoadPerHourData = energyLoadPerHour[7:]
            header = energyLoadPerHour[:7]
        elif (len(energyLoadPerHour) == 8760):
            energyLoadPerHourData = energyLoadPerHour
            header = ["key:location/dataType/units/frequency/startsAt/endsAt", locationName, "unknown dataType", "unknown unit", "Hourly", (1, 1, 1), (12, 31, 24)]
        energyLoadPerRowPerHour = header + [value/numberOfRows for value in energyLoadPerHourData]
    
    
    # extracting HOYs from minimalSpacingPeriod periods
    minimalSpacingPeriodHOYs1, monthsDummy, daysDummy = lb_preparation.getHOYsBasedOnPeriod(minimalSpacingPeriod1, 1)
    minimalSpacingPeriodHOYs2, monthsDummy, daysDummy = lb_preparation.getHOYsBasedOnPeriod(minimalSpacingPeriod2, 1)
    
    # clockwise sunAzimuthD
    #northRad = math.radians(northDeg)
    northRad, northVec = lb_photovoltaics.angle2northClockwise(northDeg)
    northVec.Unitize()
    
    scale = 1
    lb_sunpath.initTheClass(latitude, northRad, arrayOriginPt, scale, longitude, timeZone)
    
    # extracting hours, days, months from HOYs
    solarTime = False
    days = []; months = []; hours = []
    sunAltitudeR_L = []; sunAzimuthR_L = []
    for i,hoy in enumerate(minimalSpacingPeriodHOYs1):
        d1, m1, h1 = lb_preparation.hour2Date(minimalSpacingPeriodHOYs1[i], True)
        days.append(d1)
        months.append(m1+1)
        hours.append(h1)
        lb_sunpath.solInitOutput(m1+1, d1, h1, solarTime)
        sunAltitudeR1 = lb_sunpath.solAlt
        sunAzimuthR1 = lb_sunpath.solAz
        # correct "sunAzimuthR1" for north_
        correctedSunAzimuthD = northDeg + math.degrees(sunAzimuthR1)
        if correctedSunAzimuthD > 360:
            correctedSunAzimuthD = correctedSunAzimuthD - 360
        correctedSunAzimuthR1 = math.radians(correctedSunAzimuthD)
        sunAltitudeR_L.append(sunAltitudeR1)
        sunAzimuthR_L.append(correctedSunAzimuthR1)
    
    for i,hoy in enumerate(minimalSpacingPeriodHOYs2):
        d2, m2, h2 = lb_preparation.hour2Date(minimalSpacingPeriodHOYs2[i], True)
        days.append(d2)
        months.append(m2+1)
        hours.append(h2)
        lb_sunpath.solInitOutput(m2+1, d2, h2, solarTime)
        sunAltitudeR2 = lb_sunpath.solAlt
        sunAzimuthR2 = lb_sunpath.solAz
        # correct "sunAzimuthR2" for north_
        correctedSunAzimuthD = northDeg + math.degrees(sunAzimuthR2)
        if correctedSunAzimuthD > 360:
            correctedSunAzimuthD = correctedSunAzimuthD - 360
        correctedSunAzimuthR2 = math.radians(correctedSunAzimuthD)
        sunAltitudeR_L.append(sunAltitudeR2)
        sunAzimuthR_L.append(correctedSunAzimuthR2)
    
    # split the energyLoadPerHour_ according to numberOfRows_
    energyLoadPerRowPerHourDataTree = grass.DataTree[object]()
    for i in range(numberOfRows):
        energyLoadPerRowPerHourDataTree.AddRange(energyLoadPerRowPerHour, grass.Kernel.Data.GH_Path(i))
    
    validInputData = True
    printMsg = "ok"
    
    return locationName, latitude, longitude, timeZone, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, skewRowsDistance, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, minimalSpacingPeriod1, minimalSpacingPeriod2, baseSurfaceUV, arrayOriginPt, groundTiltR, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, energyLoadPerRowPerHourDataTree, validInputData, printMsg


def main(srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, skewRowsDistance, arrayOriginPt, groundTiltR, arrayOriginCorner):
    
    smallestSunAltitudeR_and_otherData = []
    for i in range(len(sunAltitudeR_L)):
        sunAltitudeR = sunAltitudeR_L[i]
        sunAzimuthR = sunAzimuthR_L[i]
        
        if groundTiltR == 0: groundTiltR = 0.0000001  # fix for dividing with zero
        if (arrayTiltR < groundTiltR):  # specific for angled PV arrays attached to a vertical building wall, or highly angled building wall
            if arrayTiltR == 0: arrayTiltR = math.radians(0.0000001)  # fix for dividing with zero
        
        # arraySpacingDistance
        if (arrayTiltR == 0):
            # if arrayTiltAngle_ = 0
            minArrayAngledRowSpacing = tiltedArrayHeight
            horizontalProjectionOfTiltedArrayHeight = tiltedArrayHeight
        else:
            # based on: www.affordable-solar.com/Learning-Center/Building-a-System/Calculating-Tilted-Array-Spacing
            arraysBoundingBoxHeight = tiltedArrayHeight * math.sin(arrayTiltR)
            shadowDistance = arraysBoundingBoxHeight / math.tan(sunAltitudeR)
            if sunAzimuthR >= math.pi:
                # morning
                minArrayHorizontalRowSpacing = shadowDistance * math.cos(arrayAzimuthR-sunAzimuthR)
            else:
                # afternoon
                minArrayHorizontalRowSpacing = shadowDistance * math.cos(sunAzimuthR-arrayAzimuthR)
            if minArrayHorizontalRowSpacing < 0:
                minArrayHorizontalRowSpacing = abs(minArrayHorizontalRowSpacing)
            if (minArrayHorizontalRowSpacing == 0) and (sunAltitudeR != 0):
                minArrayHorizontalRowSpacing = tiltedArrayHeight
            
            horizontalProjectionOfTiltedArrayHeight = tiltedArrayHeight * math.cos(arrayTiltR)
            XZplaneProjectedSunAltitudeR = math.atan(arraysBoundingBoxHeight/minArrayHorizontalRowSpacing)
            firstSecondRowHeightDifference = (horizontalProjectionOfTiltedArrayHeight + minArrayHorizontalRowSpacing) / ((1/math.tan(groundTiltR)) + (1/math.tan(XZplaneProjectedSunAltitudeR)))
            minArrayAngledRowSpacing = firstSecondRowHeightDifference / math.sin(groundTiltR)
            smallestSunAltitudeR_and_otherData.append([minArrayAngledRowSpacing, sunAltitudeR, sunAzimuthR, days[i], months[i], hours[i]])
    
    # minimal spacing between rows will be take for the date with the longest minArrayAngledRowSpacing
    smallestSunAltitudeR_and_otherData.sort()
    minArrayAngledRowSpacing = smallestSunAltitudeR_and_otherData[-1][0]
    day = smallestSunAltitudeR_and_otherData[-1][3]
    month = smallestSunAltitudeR_and_otherData[-1][4]
    hour = smallestSunAltitudeR_and_otherData[-1][5]
    minimalSpacingDate = lb_preparation.hour2Date(lb_preparation.date2Hour(month, day, hour))
    
    
    minArrayHorizonalRowSpacing = math.cos(groundTiltR) * minArrayAngledRowSpacing
    horizontalProjectionOfTiltedArrayHeight = abs(horizontalProjectionOfTiltedArrayHeight)
    
    # generate PV SWH array surfaces
    arrayPlane = Rhino.Geometry.Plane(arrayOriginPt, Rhino.Geometry.Vector3d(0,0,1))
    arrayPlane.Rotate(-arrayTiltR, Rhino.Geometry.Vector3d(1,0,0))
    # clockwise
    arrayPlane.Rotate(-arrayAzimuthR, Rhino.Geometry.Vector3d(0,0,1))
    # counterclockwise
    #arrayPlane.Rotate(arrayAzimuthR, Rhino.Geometry.Vector3d(0,0,1))
    
    arraySideWidth = (srfArea/numberOfRows)/tiltedArrayHeight
    
    if arrayOriginCorner == 0:
        # center bottom origin
        arrayRectangle = Rhino.Geometry.Rectangle3d(arrayPlane, Rhino.Geometry.Interval(-arraySideWidth/2,arraySideWidth/2), Rhino.Geometry.Interval(0,-tiltedArrayHeight))
    elif arrayOriginCorner == 1:
        # left bottom origin
        arrayRectangle = Rhino.Geometry.Rectangle3d(arrayPlane, Rhino.Geometry.Interval(-arraySideWidth,0), Rhino.Geometry.Interval(0,-tiltedArrayHeight))
    elif arrayOriginCorner == 2:
        # right bottom origin
        arrayRectangle = Rhino.Geometry.Rectangle3d(arrayPlane, Rhino.Geometry.Interval(0,arraySideWidth), Rhino.Geometry.Interval(0,-tiltedArrayHeight))
    if arrayOriginCorner == 3:
        # center top origin
        arrayRectangle = Rhino.Geometry.Rectangle3d(arrayPlane, Rhino.Geometry.Interval(arraySideWidth/2,-arraySideWidth/2), Rhino.Geometry.Interval(0, tiltedArrayHeight))
    
    PV_SWH_surface = Rhino.Geometry.Brep.CreatePlanarBreps([arrayRectangle.ToNurbsCurve()])[0]  # first row array surface
    PV_SWH_surface.Flip()
    
    arrayAzimuthVec.Unitize()
    arrayAzimuthVec.Reverse()
    arrayAzimuthVec.Rotate(-groundTiltR, arrayPlane.XAxis)
    
    skewRowsMoveVector = Rhino.Geometry.Vector3d(arrayPlane.XAxis)
    skewRowsMoveVector.Unitize()
    skewRowsMoveVector = skewRowsMoveVector * skewRowsDistance
    
    transmatrix = Rhino.Geometry.Transform.Translation(arrayAzimuthVec*minArrayAngledRowSpacing + skewRowsMoveVector)
    
    PV_SWH_surfaceDataTree = grass.DataTree[object]()
    PV_SWH_surfaceDataTree.AddRange([PV_SWH_surface], grass.Kernel.Data.GH_Path(0))
    for i in range(numberOfRows-1):
        nextRowSurface = PV_SWH_surfaceDataTree.Branches[i][0].Duplicate()
        nextRowSurface.Transform(transmatrix)
        PV_SWH_surfaceDataTree.AddRange([nextRowSurface], grass.Kernel.Data.GH_Path(i+1))
    
    return PV_SWH_surfaceDataTree, abs(minArrayAngledRowSpacing), minimalSpacingDate


def printOutput(locationName, latitude, longitude, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, tiltedArrayHeight, numberOfRows, skewRowsDistance, minimalSpacingPeriod1, minimalSpacingPeriod2, groundTiltR, baseSurfaceUV, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent):
    resultsCompletedMsg = "PV SWH system size component results successfully completed!"
    arrayOriginCornerDescription = ["center bottom", "left bottom", "right bottom", "center top"][arrayOriginCorner]
    if moduleEfficiency != None:  # _PVmoduleSettings inputted:
        PVSWHmoduleSystemSettings = "Data taken from _PVmoduleSettings:\nModule efficiency (perc.):  %s\nModule active area percent (perc.):  %s" % (moduleEfficiency, moduleActiveAreaPercent)
    else:  # _SWHsystemSettings inputted:
        PVSWHmoduleSystemSettings = "Data taken from _SWHsystemSettings:\nCollector optical efficiency (-):  %s,\nCollector thermal loss (W/m2/C):  %s,\nCollector active area percent (perc.):  %s," % (collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent)
    if minimalSpacingPeriod1 == minimalSpacingPeriod2:
        minimalSpacingPeriodString = "%s" % (minimalSpacingPeriod1)
    else:
        minimalSpacingPeriodString = "%s or %s" % (minimalSpacingPeriod1, minimalSpacingPeriod2)
    printOutputMsg = \
    """
Input data:

Location:  %s,
Latitude (deg.):  %s,
Longitude (deg.):  %s,
North (deg.):  %s,

System size (kW):  %0.2f,
Surface area (m2):  %0.2f,
Array tilt angle (deg.):  %0.2f,
Array azimuth angle (deg.):  %0.2f,
Tilted array height (m):  %0.2f,
Number of rows:  %0.2f,
Skew rows distance (m):  %0.2f,
Minimal spacing period:  %s,
Base surface tilt angle(deg.):  %0.2f,
Array origin point:  %0.2f, %0.2f,
Array origin corner:  %s (%s),

%s
    """ % (locationName, latitude, longitude, northDeg, systemSize, srfArea, math.degrees(arrayTiltR), math.degrees(arrayAzimuthR), tiltedArrayHeight, numberOfRows, skewRowsDistance, minimalSpacingPeriodString, math.degrees(groundTiltR), baseSurfaceUV[0], baseSurfaceUV[1], arrayOriginCorner, arrayOriginCornerDescription, PVSWHmoduleSystemSettings)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_sunpath = sc.sticky["ladybug_SunPath"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        unitConversionFactor = lb_preparation.checkUnits()
        # assign descriptions to _PVmoduleSettings and _SWHsystemSettings inputs
        changeInputNamesAndDescriptions(1, 0)
        changeInputNamesAndDescriptions(2, 0)
        if _location:
            try:
                PVmoduleSettingsInput = [item.Value if (item != None) else None for item in list(ghenv.Component.Params.Input[1].VolatileData)]
            except:
                PVmoduleSettingsInput = []
            try:
                SWHsystemSettingsInput = [item2.Value if (item2 != None) else None for item2 in list(ghenv.Component.Params.Input[2].VolatileData)]
            except Exception, e:
                SWHsystemSettingsInput = []
            locationName, latitude, longitude, timeZone, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, skewRowsDistance, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, minimalSpacingPeriod1, minimalSpacingPeriod2, baseSurfaceUV, arrayOriginPt, groundTiltR, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent, energyLoadPerRowPerHourDataTree, validInputData, printMsg = checkInputData(_location, PVmoduleSettingsInput, SWHsystemSettingsInput, systemSize_, arrayTiltAngle_, arrayAzimuthAngle_, tiltedArrayHeight_, numberOfRows_, skewRowsDistance_, minimalSpacingPeriod_, baseSurface_, arrayOriginPt_, arrayOriginCorner_, north_, energyLoadPerHour_, unitConversionFactor)
            if validInputData:
                PV_SWHsurface, minimalSpacing, minimalSpacingDate = main(srfArea, arrayTiltR, arrayAzimuthR, arrayAzimuthVec, tiltedArrayHeight, numberOfRows, days, months, hours, sunAltitudeR_L, sunAzimuthR_L, skewRowsDistance, arrayOriginPt, groundTiltR, arrayOriginCorner)
                printOutput(locationName, latitude, longitude, northDeg, systemSize, srfArea, arrayTiltR, arrayAzimuthR, tiltedArrayHeight, numberOfRows, skewRowsDistance, minimalSpacingPeriod1, minimalSpacingPeriod2, groundTiltR, baseSurfaceUV, arrayOriginCorner, moduleEfficiency, moduleActiveAreaPercent, collectorOpticalEfficiency, collectorThermalLoss, collectorActiveAreaPercent)
                PV_SWHsurfacesArea = srfArea; energyLoadPerRowPerHour = energyLoadPerRowPerHourDataTree
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please input location from \"importEPW\" or \"constructLocation\" components."
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