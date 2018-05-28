# Bioclimatic Chart
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Abraham Yezioro <ayez@ar.technion.ac.il> 
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
This is the Bioclimactic Chart. It is based in the originally proposed chart by V. Olgyay and then in the chart presented in the book "Sun, Climate and Architecture" by Brown.
Use this component to draw a Bioclimatic chart in the Rhino scene and evaluate a set of temperatures and humidity ratios in terms of indoor comfort. Connected data can include either outdoor temperature and humidty ratios from imported EPW weather data, indoor temperature and humidity ratios from an energy simulation, or indivdual numerical inputs of temperature and humidity.  The input data will be plotted alongside polygons on the chart representing comfort as well as polygons representing the efects of passive building strategies on comfort.
References:
    1. Olgyay, V., 1963. Design with Climate. Bioclimatic Approach to Architectural Regionalism. Van Nostrand reinhold, New York.
    2. Givoni B., 1976. Man, Climate and Architecture. Applied Science Publishers, Ltd., London.
    3. Murray M. and Givoni B., 1979. Architectural Design Based on Climate in Watson D. (ed), 1979. Energy COnservation Through Building Design. McGraw Hill Book Company.
    4. Yezioro, A. & E. Shaviv. 1996. A Knowledge Based CAD System for Determining Thermal Comfort Design Strategies. Renewable Energy, 8: (1-4), (pp. 133-138).
    5. Brown G.Z. and DeKay M., 2001. Sun, WInd & Light. Architectural Design Strategies (2nd edition). John WIley  & Sons, Inc.

-
Provided by Ladybug 0.0.66
    
    Args:
        _dryBulbTemperature: A number representing the dry bulb temperature of the air in degrees Celcius. This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.  Indoor temperatures from Honeybee energy simulations are also possible inputs.
        _relativeHumidity: A number between 0 and 100 representing the relative humidity of the air in percentage. This input can also accept a list of relative humidity values representing conditions at different times or the direct output of relativeHumidity from of the Import EPW component.
        ------------------------------: ...
        metabolicRate_: A number representing the metabolic rate of the human subject in met. This input can also accept text inputs for different activities. Acceptable text inputs include Sleeping, Reclining, Sitting, Typing, Standing, Driving, Cooking, House Cleaning, Walking, Walking 2mph, Walking 3mph, Walking 4mph, Running 9mph, Lifting 10lbs, Lifting 100lbs, Shoveling, Dancing, and Basketball.  If no value is input here, the component will assume a metabolic rate of 1 met, which is the metabolic rate of a seated human being.
        clothingLevel_: A number representing the clothing level of the human subject in clo. If no value is input here, the component will assume a clothing level of 1 clo, which is roughly the insulation provided by a 3-piece suit. A person dressed in shorts and a T-shirt has a clothing level of roughly 0.5 clo and a person in a thick winter jacket can have a clothing level as high as 2 to 4 clo.
        passiveStrategy_: An optional text input of passive strategies to be laid over the Bioclimatic chart as polygons.  Text inputs include "Passive Solar Heating", "Evaporative Cooling", "Thermal Mass + Night Vent" and "Natural Ventilation". NOT WORKING RIGHT NOW!!
        ------------------------------: ...
        cullMesh_: Set to "True" to cull the colored mesh to where they have climatic data on them. See chartMesh output. Deafult "False"
        calculateCharts_: Set to "True" to calculate and show a column type graph showing the percentage of time each strategy is capable of providing comfort conditions. See resultsChart output. Deafult "False"
        ------------------------------: ...
        analysisPeriodWinter_: An optional analysis period from the Analysis Period component. If no Analysis period is given and epw data from the ImportEPW component has been connected, the analysis will be run for the enitre year. ONLY WORKS FOR THE WHOLE YEAR RIGHT NOW!!
        analysisPeriodSummer_: An optional analysis period from the Analysis Period component. If no Analysis period is given and epw data from the ImportEPW component has been connected, the analysis will be run for the enitre year. ONLY WORKS FOR THE WHOLE YEAR RIGHT NOW!!
        basePoint_: An optional base point that will be used to place the Bioclimatic Chart in the Rhino scene. If no base point is provided, the base point will be the Rhino model origin.
        scale_: An optional number to change the scale of the Bioclimatic chart in the Rhino scene. By default, this value is set to 1.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        _runIt: Set to "True" to run the component and calculate the adaptive comfort metrics.
    Returns:
        readMe!: ...
        ------------------------------: ...
        comfortResults: The number of hours and percent of the input data that are inside all comfort and passive strategy polygons.
        totalComfortOrNot: A list of 0's and 1's indicating, for each hour of the input data, if the hour is inside a comfort and/or strategy polygon (1) or not(0).
        strategyOrNot: A list of 0's and 1's indicating, for each hour of the input temperature and humidity ratio, if the hour is inside (1) or not(0), for each passive strategy and comfort polygons.  If there are multiple comfort polyogns or passive strategies connected to the passiveStrategy_ input, this output will be a grafted list for each polygon.
        ------------------------------: ...
        chartGridAndTxt: The grid and text labels of the Bioclimatic chart.
        chartMesh: A colored mesh showing the number of input hours happen in each part of the Bioclimatic chart.
        chartHourPoints: Points representing each of the hours of input temperature and humidity ratio.  By default, this ouput is hidden and, to see it, you should connect it to a Grasshopper preview component.
        hourPointColorsByComfort: Color the chartHourPoints above according to Comfort results. They can be hooked up to the "Swatch" input of a Grasshopper Preview component that has the hour points above connected as geometry.  By default, points are colored red if they lie inside comfort or strategy polygons and are colored blue if they do not meet such comfort criteria.
        hourPointColorsByMonth: Colors that the chartHourPoints above according to each month. They can be hooked up to the "Swatch" input of a Grasshopper Preview component that has the hour points above connected as geometry.  By default, points are colored red if they lie inside comfort or strategy polygons and are colored blue if they do not meet such comfort criteria.
        min_maxPoints: Plot each month's Minimal/Maximal values for Temperature and Relative Humidity. By default, this ouput is hidden and, to see it, you should connect it to a Grasshopper preview component.
        comfort_strategyPolygons: A tree of polygons representing the comfort and passive strategies areas of the chart made comfortable.
        legend: A colored legend showing the number of hours that correspond to each color for the chartMesh output.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the chart with the grasshopper "move" component.
        ------------------------------: ...
        resultsChart: A column type graph showing the percentage of time each strategy is capable of providing comfort conditions. These results are summarizing the whole year and each month. Each column shows three areas: 
        Comfort Zone (black), 
        Passive Solar Heating (yellow), as the only heating strategy for winter time
        Evaporative Cooling or High Termal Mass with Night Ventilation or Natural Ventilation (green, red, blue) as the possible cooling strategies for summer time.

"""
ghenv.Component.Name = "Ladybug_Bioclimatic Chart"
ghenv.Component.NickName = 'Bioclimatic Chart'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
#ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Grasshopper.Kernel as gh
import math
import scriptcontext as sc
import Rhino as rc
import rhinoscriptsyntax as rs
import System
from System import Object
from clr import AddReference as addr
addr("Grasshopper")

from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
###################################
import Rhino.Geometry as rg

#Define Model Tolerance
tol = sc.doc.ModelAbsoluteTolerance

meshingP = rc.Geometry.MeshingParameters.Coarse
meshingP.SimplePlanes = True
lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
lb_preparation = sc.sticky["ladybug_Preparation"]()

MonthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MonthDays = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
#MonthDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
StNames = ['ComfortZone', 'PassiveSolarHeating', 'EvaporativeCooling', 'HighTermalMass+NightVent', 'NaturalVentilation']

def checkInputs():
    #Define a value that will indicate whether someone has hooked up epw data.
    epwData = False
    epwStr = []
    
    checkData1 = False
    if _dryBulbTemperature and _relativeHumidity:
        try:
            #if str(_dryBulbTemperature[2]) == 'Dry Bulb Temperature' and \
            #   str(_relativeHumidity[2]) == 'Relative Humidity':
            if "Temperature" in _dryBulbTemperature[2] and "Humidity" in _relativeHumidity[2]:
                epwData = True
                epwStr = _dryBulbTemperature[0:7]
                checkData1 = True
            else: pass
        except: pass
    else:
        print 'Connect a temperature in degrees celcius for _dryBulbTemperature and relative humidity to the proper input items'

    #Check the metabolic rate.
    ##checkData2 = False
    #if len(metabolicRate_) > 0:
    #if metabolicRate_ > 9.5 or metabolicRate_ < 0.5:
        #print 'metabolicRate_ ', metabolicRate_
        #print 'You entered a probably invalid metabolic rate (%.1f met). Changed to Standing rate (1.2 met) ' (float(metabolicRate_))
        #metabolicRate_ = 1.2
        ##checkData2 = True
    #else:
        #print 'metabolicRate_ ', metabolicRate_
        ##checkData2 = True

    #Check the passive strategy inputs to be sure that they are correct.
    checkData3 = True
    if len(passiveStrategy_) > 0:
        for item in passiveStrategy_:
            if item == "Passive Solar Heating" or item == "Evaporative Cooling" or item == "Thermal Mass + Night Vent"  or item == "Natural Ventilation": pass
            else: checkData3 = False
    if checkData3 == False:
        warning = 'Input for passiveStrategy_ is not valid.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #If all of the checkDatas have been good to go, let's give a final go ahead.
    ##if checkData1 == True and checkData2 and checkData3 == True :
    if checkData1 == True and checkData3 == True :
        checkData = True
    else:
        checkData = False

    #print 'checkData ', checkData
    return checkData, epwData, epwStr


#Define colors for the following output situations (points and legends): Month colored (12 colors), comfortNOcomfort (2 colors).
def colors():
    customColors = [System.Drawing.Color.FromArgb(75, 107, 169),  System.Drawing.Color.FromArgb(115, 147, 202),
                    System.Drawing.Color.FromArgb(170, 200, 247), System.Drawing.Color.FromArgb(193, 213, 208),
                    System.Drawing.Color.FromArgb(245, 239, 103), System.Drawing.Color.FromArgb(252, 230, 74),
                    System.Drawing.Color.FromArgb(239, 156, 21),  System.Drawing.Color.FromArgb(234, 123, 0),
                    System.Drawing.Color.FromArgb(234, 74, 0),    System.Drawing.Color.FromArgb(234, 38, 0)]
                
    monthColors = [System.Drawing.Color.FromArgb(0, 0, 0),     System.Drawing.Color.FromArgb(0, 125, 0),
                   System.Drawing.Color.FromArgb(0, 255, 0),   System.Drawing.Color.FromArgb(0, 125, 125),
                   System.Drawing.Color.FromArgb(0, 125, 255), System.Drawing.Color.FromArgb(0, 255, 255),
                   System.Drawing.Color.FromArgb(0, 0, 125),   System.Drawing.Color.FromArgb(0, 0, 255),
                   System.Drawing.Color.FromArgb(125, 0, 0),   System.Drawing.Color.FromArgb(255, 0, 0),
                   System.Drawing.Color.FromArgb(125, 125, 0), System.Drawing.Color.FromArgb(255, 125, 0)]
    comfortNOcomfortColors = [System.Drawing.Color.FromArgb(75, 107, 169),    # Comfort 
                              System.Drawing.Color.FromArgb(234, 38, 0)]      # NoComfort
    
    strategiesColors = [System.Drawing.Color.FromArgb(50, 50, 50),    # CZ
                        System.Drawing.Color.FromArgb(200, 200, 0),   # PSH or (220, 220, 50)
                        System.Drawing.Color.FromArgb(50, 220, 50),   # EC
                        System.Drawing.Color.FromArgb(220, 50, 50),   # HTM
                        System.Drawing.Color.FromArgb(50, 50, 220)]   # NV
    
    return monthColors, comfortNOcomfortColors, strategiesColors


#Define a function to offset curves and return things that will stand out on the Bioclimatic chart.
def outlineCurve(curve):
    try:
        offsetCrv = curve.Offset(rc.Geometry.Plane.WorldXY, 0.25, sc.doc.ModelAbsoluteTolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
        finalBrep = (rc.Geometry.Brep.CreatePlanarBreps([curve, offsetCrv])[0])
    except:
        finalBrep = rc.Geometry.Brep.CreatePlanarBreps([curve])[0]
        warning = "Creating an outline of one of the comfort or strategy curves failed.  Component will return a solid brep."
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    return finalBrep


def createResultsLegend(orgX, orgY, orgZ, gridStep, monthStep, xLineValue, yLineValue, location, strategyNames, strategyPercent, strategyHours, lb_preparation, legendFontSize, legendBold, legendFont, strategiesColors):
    if legendFontSize == None: legendFontSize = 2
    
    #Make axis labels for the chart.
    xAxisLabels = []
    xAxisTxt = ["Comfort Strategies"]
    xAxisPt = [rc.Geometry.Point3d(orgX + 0., orgY - 5.0, 0)]
    xAxisLabels.extend(lb_visualization.text2srf(xAxisTxt, xAxisPt, legendFont, legendFontSize*1.25, legendBold)[0])

        
    # Make the percentage text for the chart Y axis.
    percentText = []
    percentLabels = []
    percentLabelBasePts = []
    percentNum = range(0, 110, 10)
    for count, percent in enumerate(percentNum):
        percentLabelBasePts.append(rc.Geometry.Point3d(orgX - 8, orgY + (percent)-0.75, 0))
        percentText.append(str(percent)+"%")
    for count, text in enumerate(percentText):
        percentLabels.extend(lb_visualization.text2srf([text], [percentLabelBasePts[count]], legendFont, legendFontSize*.75, legendBold)[0])

    # Make the Title at top.
    titleLabels = []
    titleTxt = "Year Results"
    titlePt = [rc.Geometry.Point3d(orgX + 0., (100 + orgY + 1), 0)]

    titleLabels.extend(lb_visualization.text2srf([titleTxt], [titlePt[0]], legendFont, legendFontSize*1.5, True)[0])
    
    #Months titles loop
    step = monthStep
    for m in range(0, len(MonthNames)):
        #titleLabels = []
        titleTxt = MonthNames[m]
        titlePt = [rc.Geometry.Point3d(orgX + step, (100 + orgY + 1), 0)]
        step += monthStep
        titleLabels.extend(lb_visualization.text2srf([titleTxt], [titlePt[0]], legendFont, legendFontSize*1.5, legendBold)[0])
    
    
    # Create legend with Strategies Names, at bottom right.
    legLabels = []
    legLabels1 = []
    legResultstText = []
    legPolygon = []
    legLabelBasePts = []
    legLabelBasePts1 = []
    legColorLabelBasePts = []
    legColorLabelBasePts1 = []
    legNum = range(int(orgY), 50, 8)
    radius = 2.0
    segments = 4
    for count, leg in enumerate(legNum):
        legLabelBasePts.append(rc.Geometry.Point3d(xLineValue[12] + 50, leg + 1.50, 0))
        legColorLabelBasePts.append(rc.Geometry.Point3d(xLineValue[12] + 46, leg + 1.25, 0))
        legColorLabelBasePts1.append(rc.Geometry.Point3d(xLineValue[12] + 50, leg - 1.0, 0)) ####
    for count, text in enumerate(strategyNames):
        combString = '%.1f%% - %d hours' % (strategyPercent[count], strategyHours[count])
        legResultstText.append(combString) #strategyPercent, strategyHours
    for count, text in enumerate(legResultstText):
        legLabels1.extend(lb_visualization.text2srf([text], [legColorLabelBasePts1[count]], legendFont, legendFontSize*.75, legendBold)[0])
        
    for count, text in enumerate(strategyNames):
        if   count == 0: colorP = strategiesColors[0]    # CZ
        elif count == 1: colorP = strategiesColors[1]    # PSH or (220, 220, 50)
        elif count == 2: colorP = strategiesColors[2]    # EC
        elif count == 3: colorP = strategiesColors[3]    # HTM
        elif count == 4: colorP = strategiesColors[4]    # NV
        else           : colorP = System.Drawing.Color.FromArgb(255, 255, 255, 255)
        
        legLabels.extend(lb_visualization.text2srf([text], [legLabelBasePts[count]], legendFont, legendFontSize*0.75, legendBold)[0])
        legPol = drawPolygon(legColorLabelBasePts[count], radius, segments, colorP)
        legPolygon.append(legPol)
    
    #Bring all legend and text together in one list.
    restText = []
    for item in percentLabels:
        restText.append(item)
    #for item in relHumidLabels:
    #    restText.append(item)
    for item in xAxisLabels:
        restText.append(item)
    #for item in yAxisLabels:
    #    restText.append(item)
    for item in titleLabels:
        restText.append(item)
    for item in legLabels:
        restText.append(item)
    for item in legLabels1:
        restText.append(item)
    for item in legPolygon:
        restText.append(item)
    
    return restText

def createChartLayout(orgX, orgY, orgZ, location, legendFont, legendFontSize, legendBold):
    if legendFontSize == None: legendFontSize = 2
    
    #Make axis labels for the chart.
    xAxisLabels = []
    xAxisTxt = ["Humidity Ratio"]
    #xAxisPt = [rc.Geometry.Point3d(orgX + 35., orgY - 10.0, 0)]
    xAxisPt = [rc.Geometry.Point3d(orgX, orgY - 10.0, 0)]
    xAxisLabels.extend(lb_visualization.text2srf(xAxisTxt, xAxisPt, legendFont, legendFontSize*1.25, True)[0])
        
    yAxisLabels = []
    yAxisTxt = ["Dry Bulb Temperature"]
    #yAxisPt = [rc.Geometry.Point3d(orgX - 10.0, orgY + 35., 0)]
    yAxisPt = [rc.Geometry.Point3d(orgX - 10.0, orgY, 0)]
    yAxisLabels.extend(lb_visualization.text2srf(yAxisTxt, yAxisPt, legendFont, legendFontSize*1.25, True)[0])
    #rotateTransf = rc.Geometry.Transform.Rotation(1.57079633, rc.Geometry.Point3d(orgX - 10.0, orgY + 35., 0))
    rotateTransf = rc.Geometry.Transform.Rotation(1.57079633, rc.Geometry.Point3d(orgX - 10.0, orgY, 0))
    for geo in yAxisLabels:
        geo.Transform(rotateTransf)
    
    #tempNum = range(orgY + 5, 55, 5)
    tempNum = range(int(orgY/2), 55, 5)
    relHumidNum = range(0, 110, 10)
    
    # Make the relative humidity text for the chart.
    relHumidBasePts = []
    relHumidTxt = []
    relHumidLabels = []
    for count, humid in enumerate(relHumidNum):
        #print 'count ', count, humid
        relHumidBasePts.append(rc.Geometry.Point3d(humid - 2, orgY - 3, 0))
        relHumidTxt.append(str(humid)+"%")
    for count, text in enumerate(relHumidTxt):
        relHumidLabels.extend(lb_visualization.text2srf([text], [relHumidBasePts[count]], legendFont, legendFontSize*.75, legendBold)[0])
    
    # Make the temperature text for the chart.
    tempText = []
    tempLabels = []
    tempLabelBasePts = []
    for count, temp in enumerate(tempNum):
        #print 'count ', count, temp
        tempLabelBasePts.append(rc.Geometry.Point3d(-5, (temp * 2)-0.75, 0))
        tempText.append(str(temp))
    for count, text in enumerate(tempText):
        tempLabels.extend(lb_visualization.text2srf([text], [tempLabelBasePts[count]], legendFont, legendFontSize*.75, legendBold)[0])
    
    titleLabels = []
    titleTxt = ["Bio Climatic Chart", location]
    titlePt = [rc.Geometry.Point3d(orgX, 108, 0), 
    rc.Geometry.Point3d(orgX, 103, 0)]
    for count, text in enumerate(titleTxt):
        titleLabels.extend(lb_visualization.text2srf([text], [titlePt[count]], legendFont, legendFontSize*1.5, legendBold)[0])
    
    #Bring all text and curves together in one list.
    chartLayout = []
    for item in tempLabels:
        chartLayout.append(item)
    for item in relHumidLabels:
        chartLayout.append(item)
    for item in xAxisLabels:
        chartLayout.append(item)
    for item in yAxisLabels:
        chartLayout.append(item)
    for item in titleLabels:
        chartLayout.append(item)
    
    return chartLayout

def createChartLegend(orgX, orgY, orgZ, strategyNames, lb_preparation, legendScale, legendFont, legendFontSize, legendBold, lb_visualization, strategiesColors, monthColors, comfortNOcomfortColors, customColors, totalComfortOrNot):
    if legendFontSize == None: legendFontSize = 2
    
    # ************** Generate a legend for strategies ***********
    legStrategyLabels = []
    legLabelBasePts = []
    finalLegPolyline = []
    
    legMonthLabels = []
    legMonthLabelBasePts = []
    
    legComfLabels = []
    legComfLabelBasePts = []

    shiftY = -20 #-15
    leg = int(orgY) + shiftY
    #legNum = range(int(orgY) + shiftY, -23 + shiftY, -3) # [-25, -28, -31, -34, -37] Need 5 values for 5 strategies

    legStrategyPolygons = []
    for count, text in enumerate(strategyNames):
        if   count == 0: color = strategiesColors[0]    # CZ
        elif count == 1: color = strategiesColors[1]    # PSH or (220, 220, 50)
        elif count == 2: color = strategiesColors[2]    # EC
        elif count == 3: color = strategiesColors[3]    # HTM
        elif count == 4: color = strategiesColors[4]    # NV
        else           : color = System.Drawing.Color.FromArgb(255, 0, 255, 255)
        
        legLinePt = []
        legLabelBasePts.append(rc.Geometry.Point3d(orgX + 10, leg + 0.0, 0)) # Base point for each strategy name
        points = [orgX, leg + 0.75, 0.0],[orgX + 9.0, leg + 0.75, 0.0], [orgX + 9.0, leg + 0.751, 0.0], [orgX, leg + 0.751, 0.0], \
                 [orgX, leg + 0.75, 0.0] # Coords for the line in the strategies legend
        for cc in range(0, len(points)):
            legLinePt.append(rc.Geometry.Point3d(points[cc][0], points[cc][1], points[cc][2]))
            
        legPolyline = rc.Geometry.PolylineCurve(legLinePt)
        leg += -3
        
        finalLegPolyline.append(outlineCurve(legPolyline)) # This is the element to use for coloring the legend
        
        legMesh = rc.Geometry.Mesh()
        legMesh.Append(rc.Geometry.Mesh.CreateFromBrep(finalLegPolyline[count])[0])
        legMesh.VertexColors.CreateMonotoneMesh(color)
        legStrategyPolygons.append(legMesh)
        
        # Draw the strategies names
        legStrategyLabels.extend(lb_visualization.text2srf([text], [legLabelBasePts[count]], legendFont, legendFontSize*0.75, legendBold)[0])
    # ************** End Legend of strategies ***********
    
    """
    # ************** Generate a legend for comfortOrNot Using Chris's way from Psychrometric chart ***********
    leg = int(orgY) + shiftY - 11.0
    ##pointColors = []
    legComfBasePts = rc.Geometry.Point3d(orgX + 45, leg, 0) # Base point comfortOrNot legend
    
    if str(totalComfortOrNot[0]) == "key:location/dataType/units/frequency/startsAt/endsAt":
        totalComfortOrNot = totalComfortOrNot[7:]
    ##pointColors.append(lb_visualization.gradientColor(totalComfortOrNot, 0, 1, customColors))
    
    legend = []
    #legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(totalComfortOrNot, 0, 1, 2, "Comfort", lb_visualization.BoundingBoxPar, legComfBasePts, legendScale, legendFont, legendFontSize, decimalPlaces, removeLessThan)
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(totalComfortOrNot, 0, 1, 2, "Comfort or Not", lb_visualization.BoundingBoxPar, legComfBasePts, .45, legendFont, 1.5, decimalPlaces, removeLessThan)
    legendColors = lb_visualization.gradientColor(legendText[:-1], 0, 1, customColors)
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    legend.append(legendSrfs)
    for list in legendTextCrv:
        for item in list:
            legend.append(item)
    # ************** End Legend of comfortOrNot ***********
    """
    
    radius = 0.7
    segments = 6
    
    # ************** Generate a legend for comfortOrNot ***********
    leg = int(orgY) + shiftY
    legComfCircle = []
    circCenter = []
    circPolyline = []
    for m in range(0, 2):   # 0 to 2 for Comfort or NoComfort possibilities
        if m == 0: text = "No Comfort"
        else     : text = "Comfort"
        circCenter.append(rc.Geometry.Point3d(orgX + 55, leg + radius/2, 0)) # Base point for each month circle
        legComfLabelBasePts.append(rc.Geometry.Point3d(orgX + 57, leg + 0.0, 0)) # Base point for each month name
        leg += -3
        # Draw the comfortOrNot circles and value
        cP, dataPolyline = circPoints(circCenter[m], radius, segments)
        
        circPolyline.append(outlineCurve(dataPolyline)) # This is the element to use for coloring the legend
        legMesh = rc.Geometry.Mesh()
        legMesh.Append(rc.Geometry.Mesh.CreateFromBrep(circPolyline[m])[0])
        legMesh.VertexColors.CreateMonotoneMesh(comfortNOcomfortColors[m])
        
        legComfCircle.append(legMesh)
        legComfLabels.extend(lb_visualization.text2srf([text], [legComfLabelBasePts[m]], legendFont, legendFontSize*0.75, legendBold)[0])
    # ************** End Legend of comfortOrNot ***********
    
    # ************** Generate a legend for Month colored ***********
    leg = int(orgY) + shiftY
    legMonthsCircle = []
    circCenter = []
    circPolyline = []
    for count, text in enumerate(MonthNames):
        circCenter.append(rc.Geometry.Point3d(orgX + 85, leg + radius/2, 0)) # Base point for each month circle
        legMonthLabelBasePts.append(rc.Geometry.Point3d(orgX + 87, leg + 0.0, 0)) # Base point for each month name
        leg += -3
        # Draw the Months circles and names
        cP, dataPolyline = circPoints(circCenter[count], radius, segments)
        
        circPolyline.append(outlineCurve(dataPolyline)) # This is the element to use for coloring the legend
        legMesh = rc.Geometry.Mesh()
        legMesh.Append(rc.Geometry.Mesh.CreateFromBrep(circPolyline[count])[0])
        legMesh.VertexColors.CreateMonotoneMesh(monthColors[count])
        
        legMonthsCircle.append(legMesh)
        legMonthLabels.extend(lb_visualization.text2srf([text], [legMonthLabelBasePts[count]], legendFont, legendFontSize*0.75, legendBold)[0])
    # ************** End Legend of Month colors ***********
    
    #Bring all text and curves together in one list.
    chartLegend = []
    for item in finalLegPolyline:
        chartLegend.append(item)
    for item in legStrategyPolygons:
        chartLegend.append(item)
    for item in legStrategyLabels:
        chartLegend.append(item)
    
    #for item in legend: # This is for Chris's way - Keep commented/uncommented together with the block above
    #    chartLegend.append(item)

    for item in legComfCircle:
        chartLegend.append(item)
    for item in legComfLabels:
        chartLegend.append(item)
    
    for item in legMonthsCircle:
        chartLegend.append(item)
    for item in legMonthLabels:
        chartLegend.append(item)
    
    return chartLegend

#def strategyDraw_Calc(name, shiftFactor, *points): # The x is for a list of points passed one by one
def strategyDraw_Calc(name, shiftFactor, points, hourPoints, tol, dryBulbTemperature, totalHrs, cR, cG, cB):
    strategyID = [0 for x in range(totalHrs)] 
    
    strategyPt = []
    for x in range(0, len(points)):
        strategyPt.append(rc.Geometry.Point3d(points[x][0], points[x][1] + shiftFactor, points[x][2] + 0.05))
    
    #Draw Polygon
    strategyPolyline = rc.Geometry.PolylineCurve(strategyPt)
    #meshedC = rc.Geometry.Mesh.CreateFromPlanarBoundary(strategyPolyline.ToNurbsCurve(), meshingP)
    
    #Turn the comfort curve into a brep that will show up well on the chart.
    #finalStrategyPolyline = []
    finalStrategyPolyline = outlineCurve(strategyPolyline)

    strategyPolygon  = rc.Geometry.Brep.CreatePlanarBreps(strategyPolyline)[0]
###    try: strategyPolygon  = rc.Geometry.Brep.CreatePlanarBreps(strategyPolyline)[0]
###    except: strategyPolygon  = None
    
    #Start STRATEGY statistics ********************************
    #Find the hours in the STRATEGY.
    strategyList = []
    n = 0
    for point in hourPoints:
        containment = strategyPolyline.Contains(point, rc.Geometry.Plane.WorldXY, tol)
        if str(containment) == 'Inside':
            strategyList.append(1)
            strategyID[n] = 1
        else: strategyList.append(0)
        n += 1
    
    #Find the STRATEGY Percentage.
    numStrHrs = sum(strategyList)
    totalHrs = len(dryBulbTemperature)
    strPercent = (numStrHrs / totalHrs)*100
    #End STRATEGY statistics ********************************

    #return numStrHrs, strPercent, strategyID, strategyPolygon
    return numStrHrs, strPercent, strategyID, strategyPolygon, finalStrategyPolyline
    
def drawColorResults(czPt, pshPt, stPt, colorCZ, colorPSH, colorST):
    
    alpha = 255 # 0 = Transparent, 255 = Opaque ... supposed to be so
    colResMesh = []
    for count in range(3):
        if count == 0:
            color = colorCZ
            #Draw each Result
            dataPolyline = rc.Geometry.PolylineCurve(czPt)
            meshedC = rc.Geometry.Mesh.CreateFromPlanarBoundary(dataPolyline.ToNurbsCurve(), meshingP)
        elif count == 1:
            color = colorPSH
            dataPolyline = rc.Geometry.PolylineCurve(pshPt)
            meshedC = rc.Geometry.Mesh.CreateFromPlanarBoundary(dataPolyline.ToNurbsCurve(), meshingP)
        elif count == 2:
            color = colorST
            dataPolyline = rc.Geometry.PolylineCurve(stPt)
            meshedC = rc.Geometry.Mesh.CreateFromPlanarBoundary(dataPolyline.ToNurbsCurve(), meshingP)

        # generate the color list for all the vertices
        repeatedColors = []
        for face in range(meshedC.Faces.Count):
            repeatedColors.append(color)
        
        #  use ladybug functions to color the circle
        ##colMesh = lb_visualization.colorMesh(repeatedColors, meshedC)
        if count == 0 :   colMesh1 = lb_visualization.colorMesh(repeatedColors, meshedC)
        elif count == 1 : colMesh2 = lb_visualization.colorMesh(repeatedColors, meshedC)
        elif count == 2 : colMesh3 = lb_visualization.colorMesh(repeatedColors, meshedC)
        
        ####colResMesh.append(colMesh)
        #colResMesh[count] = colMesh
        #print count, colMesh
        
    #Bring all legend and text together in one list.
    ##colMeshGGraph = []
    #for item in colResMesh:
    #for item in colMesh:
        #colMeshGGraph.append(item)
    ##return colMesh
    ####return colResMesh
    return colMesh1, colMesh2, colMesh3
    ##return colMeshGGraph
    
    
def graphResults(orgX, orgY, orgZ, gridStep, xLineValue, yLineValue, location, strategyNames, strategyPercent, strategyHours, lb_preparation, legendFontSize, legendFont, strategiesColors):
    
    czBot = orgY
    czTop = orgY + strategyPercent[0]
    pshBot = czTop
    pshTop = czTop + strategyPercent[1]
    firstX = orgX
    
    colorCZ = strategiesColors[0]  # CZ
    colorPSH = strategiesColors[1] # PSH
    
    stResGraph = []
    seeChartResults = []
    for count in range(2, len(strategyNames)): # Start from third strategy. First 2 are: CZ and PSH which are fixed
        if   count == 0: colorST = strategiesColors[0]    # CZ
        elif count == 1: colorST = strategiesColors[1]    # PSH
        elif count == 2: colorST = strategiesColors[2]    # EC
        elif count == 3: colorST = strategiesColors[3]    # HTM
        elif count == 4: colorST = strategiesColors[4]    # NV
        else           : colorST = [255, 255, 255]
        czPt = []
        pshPt = []
        stPt = []
        czPt.append(rc.Geometry.Point3d(firstX + 2.0, czBot, 0.0))
        czPt.append(rc.Geometry.Point3d(firstX + 8.0, czBot, 0.0))
        czPt.append(rc.Geometry.Point3d(firstX + 8.0, czTop, 0.0))
        czPt.append(rc.Geometry.Point3d(firstX + 2.0, czTop, 0.0))
        czPt.append(rc.Geometry.Point3d(firstX + 2.0, czBot, 0.0))
        
        pshPt.append(rc.Geometry.Point3d(firstX + 2.0, pshBot, 0.0))
        pshPt.append(rc.Geometry.Point3d(firstX + 8.0, pshBot, 0.0))
        pshPt.append(rc.Geometry.Point3d(firstX + 8.0, pshTop, 0.0))
        pshPt.append(rc.Geometry.Point3d(firstX + 2.0, pshTop, 0.0))
        pshPt.append(rc.Geometry.Point3d(firstX + 2.0, pshBot, 0.0))
        
        stTop = pshTop + strategyPercent[count]
        stPt.append(rc.Geometry.Point3d(firstX + 2.0, pshTop, 0.0))
        stPt.append(rc.Geometry.Point3d(firstX + 8.0, pshTop, 0.0))
        stPt.append(rc.Geometry.Point3d(firstX + 8.0, stTop, 0.0))
        stPt.append(rc.Geometry.Point3d(firstX + 2.0, stTop, 0.0))
        stPt.append(rc.Geometry.Point3d(firstX + 2.0, pshTop, 0.0))
        firstX = firstX + 10.0
        
        #Draw Polygon
        strategyPolyline = rc.Geometry.PolylineCurve(stPt)
        stResGraph.append(strategyPolyline)
        
        strategyPolyline = rc.Geometry.PolylineCurve(pshPt)
        stResGraph.append(strategyPolyline)
    
        strategyPolyline = rc.Geometry.PolylineCurve(czPt)
        stResGraph.append(strategyPolyline)
        
        #print colorCZ, colorPSH, colorST, colorKK
        
        ##colorResultsMesh = drawColorResults(czPt, pshPt, stPt, colorCZ, colorPSH, colorST) # Calling routine for drawing the results in color
        ##stResGraph.append(colorResultsMesh)
        colorResultsMesh1, colorResultsMesh2, colorResultsMesh3 = drawColorResults(czPt, pshPt, stPt, colorCZ, colorPSH, colorST) # Calling routine for drawing the results in color
        stResGraph.append(colorResultsMesh1)
        stResGraph.append(colorResultsMesh2)
        stResGraph.append(colorResultsMesh3)
        
    #Bring all legend and text together in one list.
    ##seeChartResults = []
    for item in stResGraph:
        seeChartResults.append(item)
    
    ##return seeChartResults
    return stResGraph


def graphResultsMonth(orgX, orgY, orgZ, gridStep, monthStep, xLineValue, yLineValue, location, strategyNames, strategyPercent, strategyHours, strategyMonth, lb_preparation, legendFontSize, legendFont, strategiesColors):
    
    colorCZ = strategiesColors[0]  # CZ
    colorPSH = strategiesColors[1] # PSH
    y = float()
    
    #Months titles loop
    step = 0
    seeChartResults = []
    stResGraph = []
    for month in range(0, len(MonthNames)):
        step += monthStep
        czBot  = orgY
        for line in strategyMonth[0][month][0:1]: 
            if line == 0:
                line = 0.01
            czTop  = orgY  + line # CZ & Percentage in the list
        pshBot = czTop
        for line in strategyMonth[1][month][0:1]:
            if line == 0:
                line = 0.01
            pshTop = czTop + line # PSH & Percentage in the list
        firstX = orgX + step

        ##for count in range(0, len(StNames)):
        for count in range(2, len(strategyNames)):
            #for count in range(2, len(strategyNames)): # Start from third strategy. First 2 are: CZ and PSH which are fixed
            if   count == 0: colorST = strategiesColors[0]    # CZ
            elif count == 1: colorST = strategiesColors[1]    # PSH
            elif count == 2: colorST = strategiesColors[2]    # EC
            elif count == 3: colorST = strategiesColors[3]    # HTM
            elif count == 4: colorST = strategiesColors[4]    # NV
            else           : colorST = [255, 255, 255]
            
            czPt = []
            pshPt = []
            stPt = []
            czPt.append(rc.Geometry.Point3d(firstX + 2.0, czBot, 0.0))
            czPt.append(rc.Geometry.Point3d(firstX + 8.0, czBot, 0.0))
            czPt.append(rc.Geometry.Point3d(firstX + 8.0, czTop, 0.0))
            czPt.append(rc.Geometry.Point3d(firstX + 2.0, czTop, 0.0))
            czPt.append(rc.Geometry.Point3d(firstX + 2.0, czBot, 0.0))
            
            pshPt.append(rc.Geometry.Point3d(firstX + 2.0, pshBot, 0.0))
            pshPt.append(rc.Geometry.Point3d(firstX + 8.0, pshBot, 0.0))
            pshPt.append(rc.Geometry.Point3d(firstX + 8.0, pshTop, 0.0))
            pshPt.append(rc.Geometry.Point3d(firstX + 2.0, pshTop, 0.0))
            pshPt.append(rc.Geometry.Point3d(firstX + 2.0, pshBot, 0.0))
            
            for line in strategyMonth[count][month][0:1]: 
                if line == 0:
                    line = 0.01
                stTop = pshTop + float(line) # Strategy & Percentage in the list
            #stTop = pshTop + strategyPercent[count]
            stPt.append(rc.Geometry.Point3d(firstX + 2.0, pshTop, 0.0))
            stPt.append(rc.Geometry.Point3d(firstX + 8.0, pshTop, 0.0))
            stPt.append(rc.Geometry.Point3d(firstX + 8.0, stTop, 0.0))
            stPt.append(rc.Geometry.Point3d(firstX + 2.0, stTop, 0.0))
            stPt.append(rc.Geometry.Point3d(firstX + 2.0, pshTop, 0.0))
            firstX = firstX + 10.0
            
            #Draw Polygon
            strategyPolyline = rc.Geometry.PolylineCurve(stPt)
            stResGraph.append(strategyPolyline)
            
            strategyPolyline = rc.Geometry.PolylineCurve(pshPt)
            stResGraph.append(strategyPolyline)
        
            strategyPolyline = rc.Geometry.PolylineCurve(czPt)
            stResGraph.append(strategyPolyline)
            
            ##colorResultsMesh = drawColorResults(czPt, pshPt, stPt, colorCZ, colorPSH, colorST) # Calling routine for drawing the results in color
            ##stResGraph.append(colorResultsMesh)
            colorResultsMesh1, colorResultsMesh2, colorResultsMesh3 = drawColorResults(czPt, pshPt, stPt, colorCZ, colorPSH, colorST) # Calling routine for drawing the results in color
            stResGraph.append(colorResultsMesh1)
            stResGraph.append(colorResultsMesh2)
            stResGraph.append(colorResultsMesh3)
        
    #Bring all legend and text together in one list.
    for item in stResGraph:
        seeChartResults.append(item)
    
    #return stResGraph
    return seeChartResults

    
def showResults(basePoint_, mainLegHeight, strategyNames, strategyPercent, strategyHours, strategyMonth, \
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, lb_preparation, lb_visualization, strategiesColors):
    gridLines = []
    resultsChart = []
    
    shiftRes = 45
    orgX = int(shiftRes + legendBasePoint[0])
    orgY = int(legendBasePoint[1])
    orgZ = int(legendBasePoint[2])
    
    monthStep = 40
    resLimitX = monthStep * 13
    
    boundBoxX = 40
    boundBoxY = abs(orgY) + 100
    scaleLegBox = mainLegHeight / 100
    #print 'BB = ', boundBoxX, boundBoxY, orgX, orgY, mainLegHeight, scaleLegBox
    gridStep = 10
    
    # Grid Lines *******************************
    #xLineValue = range(orgX, orgX + 50, 40)
    xLineValue = range(orgX, orgX + resLimitX + monthStep, monthStep)
    yLineValue = range(orgY, orgY + 110, gridStep)

    #for m in range(0, len(MonthNames)+1):


    for value in xLineValue: #Bottom to Top lines
        gridLines.append(rc.Geometry.Line(value, orgY, 0, value, (100 + orgY), 0))
        #print value-orgX
        
    for value in yLineValue: # Left to right lines
        #gridLines.append(rc.Geometry.Line(orgX, value, 0, orgX + 40, value, 0))
        gridLines.append(rc.Geometry.Line(orgX, value, 0, orgX + resLimitX, value, 0))
    # End Grid Lines ****************************
    # Print Title and legends in grid: X/Y axis ****************************
    location = 'Results'
    resText = createResultsLegend(orgX, orgY, orgZ, gridStep, monthStep, xLineValue, yLineValue, location, strategyNames, strategyPercent, strategyHours, lb_preparation, legendFontSize, legendBold, legendFont, strategiesColors)
    
    # This is for Year results --- in the future this and the monthly results should be unified in one single routine
    seeChartResults = graphResults(orgX, orgY, orgZ, gridStep, xLineValue, yLineValue, location, strategyNames, strategyPercent, strategyHours, lb_preparation, legendFontSize, legendFont, strategiesColors)
    # This is for monthly results
    seeMonthChartResults = graphResultsMonth(orgX, orgY, orgZ, gridStep, monthStep, xLineValue, yLineValue, location, strategyNames, strategyPercent, strategyHours, strategyMonth, lb_preparation, legendFontSize, legendFont, strategiesColors)
    
    # Collect all Results, Legend and Gridlines in one list.
    for item in gridLines:
        resultsChart.append(item)
    for item in resText:
        resultsChart.append(item)
    for item in seeChartResults:
        resultsChart.append(item)
    for item in seeMonthChartResults:
        resultsChart.append(item)
        
    bPt = rc.Geometry.Point3d(20., -2., 0.)
    #bPtSc = rc.Geometry.Point3d(0., 0., 0.)
    scale = rc.Geometry.Transform.Scale(bPt, scaleLegBox)
    move = rc.Geometry.Transform.Translation(bPt.X, bPt.Y, bPt.Z)
    transformMtx = scale * move
    for geo in resultsChart: geo.Transform(transformMtx)
    
    return resultsChart    

def circPoints(centerPt, radius, secs):
    dt = 2.0 * math.pi / secs
    div = 2*math.pi/secs
    ang = 0
    
    cP = []
    for n in range(0, secs+1):  # The +1 is to make the last point equal to the first, so the polygon will be closed
        if n == secs+1:
            ang = 0
        ptX = (centerPt.X + radius * math.cos(ang))
        ptY = (centerPt.Y + radius * math.sin(ang))
        ptZ = (centerPt.Z)+ 0.1
        cP.append(rc.Geometry.Point3d(ptX, ptY, ptZ))
        ang += div
        
    #Draw each climatic data
    dataPolyline = rc.Geometry.PolylineCurve(cP)
    
    return cP, dataPolyline
    
def drawPolygon(centerPt, radius, secs, color):
    dt = 2.0 * math.pi / secs
    div = 2*math.pi/secs
    ang = 0
    
    cP = []
    for n in range(0, secs+1):  # The +1 is to make the last point equal to the first, so the polygon will be closed
        if n == secs+1:
            ang = 0
        ptX = (centerPt.X + radius * math.cos(ang))
        ptY = (centerPt.Y + radius * math.sin(ang))
        ptZ = (centerPt.Z)+ 0.1
        cP.append(rc.Geometry.Point3d(ptX, ptY, ptZ))
        ang += div
        
    #Draw each climatic data
    dataPolyline = rc.Geometry.PolylineCurve(cP)
    meshedC = rc.Geometry.Mesh.CreateFromPlanarBoundary(dataPolyline.ToNurbsCurve(), meshingP)

    # generate the color list for all the vertices
    repeatedColors = []
    for face in range(meshedC.Faces.Count):
        repeatedColors.append(color)
    
    #  use ladybug functions to color the circle
    colMesh = lb_visualization.colorMesh(repeatedColors, meshedC)
    
    return colMesh

# Routine that gets monthly statistics and Min/Max values
def monthCalcs(totalHrs, comfID, pshID, ecID, htmID, nvID, dryBulbTemperature, relativeHumidity, monthPoints, monthColors, comfortNOcomfortColors):
    stM = 0
    pointMinMax = []
    geoMinMax = []
    allMinMax = []
    
    comfID_m = []
    pshID_m = []
    ecID_m = []
    htmID_m = []
    nvID_m = []
    
    colByComfort = []
    colByMonth = []
    
    for m in range(0, len(monthPoints)):
        geoMinMax.append([])
        
        comfID_m.append([])
        pshID_m.append([])
        ecID_m.append([])
        htmID_m.append([])
        nvID_m.append([])
        cfZ = pshZ = ecZ = htmZ = nvZ = 0
        colByComfort.append([])
        colByMonth.append([])
        
        minTemp = 50.0
        maxTemp = -50.0
        minHum = 100.0
        maxHum = 0.0
        
        monthHours = len(monthPoints[m])
        for n in range(stM, stM + len(monthPoints[m])):  #Start the counter from the previos month hour
            #for temp in dryBulbTemperature:
            if dryBulbTemperature[n] < minTemp:
                minTemp = dryBulbTemperature[n]
            if dryBulbTemperature[n] > maxTemp:
                maxTemp = dryBulbTemperature[n]
            if relativeHumidity[n] < minHum:
                minHum = relativeHumidity[n]
            if relativeHumidity[n] > maxHum:
                maxHum = relativeHumidity[n]
                
            # Summing up the points for each strategy
            if comfID[n] == 1: cfZ  += 1
            if pshID[n]  == 1: pshZ += 1
            if ecID[n]   == 1: ecZ  += 1
            if htmID[n]  == 1: htmZ += 1
            if nvID[n]   == 1: nvZ  += 1
            
            # See if the point is in any comfort strategy and the use a color for Comfort/NotComfort
            if comfID[n] == 1 or pshID[n]  == 1 or ecID[n]   == 1 or htmID[n]  == 1 or nvID[n]   == 1:
                colByComfort[m].append(comfortNOcomfortColors[1])
            else:
                colByComfort[m].append(comfortNOcomfortColors[0])
            
            #colByMonth[m].append(colorP)
            colByMonth[m].append(monthColors[m])
             
        # Calculate the effective percentage per month and number of comfort for each strategy
        czM_Perc = cfZ * 100 / len(monthPoints[m])
        comfID_m[m] = [czM_Perc, cfZ, monthHours]
        
        pshM_Perc = pshZ * 100 / len(monthPoints[m])
        pshID_m[m] = [pshM_Perc, pshZ, monthHours]
        
        ecM_Perc = ecZ * 100 / len(monthPoints[m])
        ecID_m[m] = [ecM_Perc, ecZ, monthHours]
        
        htmM_Perc = htmZ * 100 / len(monthPoints[m])
        htmID_m[m] = [htmM_Perc, htmZ, monthHours]
        
        nvM_Perc = nvZ * 100 / len(monthPoints[m])
        nvID_m[m] = [nvM_Perc, nvZ, monthHours]
        
        #print m, comfID_m[m], pshID_m[m], ecID_m[m], htmID_m[m], nvID_m[m]
        
        pointMinMax.append([minTemp * 2, maxTemp * 2, minHum, maxHum])
        stM = stM + len(monthPoints[m])
        geoMinMax[m].append(rc.Geometry.Line(pointMinMax[m][3], pointMinMax[m][0], 0, pointMinMax[m][2], pointMinMax[m][1], 0))    #Line connecting min-max
        
        colorP = System.Drawing.Color.FromArgb(0, 0, 0)
        minPt = rc.Geometry.Point3d(pointMinMax[m][3], pointMinMax[m][0], 0)
        maxPt = rc.Geometry.Point3d(pointMinMax[m][2], pointMinMax[m][1], 0)
        
        dataPolygon = drawPolygon (minPt, .8, 4, colorP)
        geoMinMax[m].append(dataPolygon)
        dataPolygon = drawPolygon (maxPt, .8, 4, colorP)
        geoMinMax[m].append(dataPolygon)
        
        #geoMinMax[m].append(rc.Geometry.Circle(minPt, 0.5))
        #geoMinMax[m].append(rc.Geometry.Circle(maxPt, 0.5))
        
    # Collect all monthly results for all strategies under one variable - in the future all calculations should be done under this variable
    strategyMonth = []
    for count in range(0, len(StNames)):
        strategyMonth.append([])
        for month in range(0, len(MonthNames)):
            strategyMonth[count].append([])
            if StNames[count]   == 'ComfortZone':
                strategyMonth[count][month] = comfID_m[month]
            elif StNames[count] == 'PassiveSolarHeating':
                strategyMonth[count][month] = pshID_m[month]
            elif StNames[count] == 'EvaporativeCooling':
                strategyMonth[count][month] = ecID_m[month]
            elif StNames[count] == 'HighTermalMass+NightVent':
                strategyMonth[count][month] = htmID_m[month]
            elif StNames[count] == 'NaturalVentilation':
                strategyMonth[count][month] = nvID_m[month]
            
        
    #Bring all set of lines and circles per month together in one list.
    for item in geoMinMax:
        allMinMax.append(item)
    
    #return allMinMax, strategyMonth, comfID_m, pshID_m, ecID_m, htmID_m, nvID_m
    return allMinMax, strategyMonth, colByComfort, colByMonth

def monthForHour(hour):
    for m in range(0, len(MonthNames)+1):
        if int(hour) < ((MonthDays[m] * 24)):
            hrCol = m
            break
    return hrCol

def seasonHours(period, totalHrs):
    x = period.split(' ')

    season = [[],[]]
    season[0].append(int(x[0]) - 1) # Month
    season[0].append(int(x[1]) - 1) # Day
    season[0].append(int(x[2]) - 1) # Hour

    season[1].append(int(x[3]) - 1) # Month
    season[1].append(int(x[4]) - 1) # Day
    season[1].append(int(x[5]) - 1) # Hour
    
    return season

def calcHourYear(season, i):
    #    print 'in calcHourYear  ----- ----- ----- season is ', season[i]
    JulDay = MonthDays[season[i][0]] + season[i][1]
    HourYear = (JulDay) * 24 + season[i][2]
    #    print '1. For month %d day %d hour %d Julian Day is %d HourYear is %d \n' % (season[i][0], season[i][1], season[i][2], JulDay, HourYear)
    return JulDay, HourYear

def assignHour2Season(start, end, totalHrs, iSeason, seasonID, dbtValue, rhValue):
    #    seasonHrs = [[],[],[]]

    if start > end:
        hrs = totalHrs - start
        numSeasHrs = hrs + end
    else:
        numSeasHrs = end - start
    #    print 'St, End, totalHrs, numHrs, Season ', start, end, totalHrs, numSeasHrs, iSeason

    ##############################
    if start > end:
        hrs = totalHrs - start
        numSeasHrs = hrs + end
        SeasHrs = range(start, totalHrs) + range(0, end + 1)
    else:
        numSeasHrs = end - start
        SeasHrs = range(start, end + 1)
    ##############################

    ##for id in range(start, end):  #to iterate between start to end
    for id, m in enumerate(SeasHrs):
        #        print 'Serial id - Choosen Hour m ', id, m
        seasonID[m] = iSeason
        
        #    return seasonHrs, seasonID
    return seasonID

def setSeasonID(dryBulbTemperature, relativeHumidity, totalHrs):
    #Define Model Tolerance
    tol = sc.doc.ModelAbsoluteTolerance
    
    #Plot Point Values.
    #******************
    dbtValue = []
    seasonID = [0 for x in range(totalHrs)] 

    for temp in dryBulbTemperature:
        dbtValue.append(temp)
    
    rhValue = []
    relativeHumidity = _relativeHumidity[7:]

    for temp in relativeHumidity:
        rhValue.append(temp)
    
    if analysisPeriodWinter_:
        stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriodWinter_, False)
        stringWinter = str(stMonth) + ' ' + str(stDay) + ' ' + str(stHour) + ' ' + str(endMonth) + ' ' + str(endDay) + ' ' + str(endHour)
        periodWinter = stringWinter
        
        winterSeason = seasonHours(periodWinter, totalHrs)
        
        #        # Calling function to calculate Day of Year and Hour of Year for START-END period
        JulDay1, hourWinterStart = calcHourYear(winterSeason, 0)
        JulDay2, hourWinterEnd   = calcHourYear(winterSeason, 1)
        #        seasonHrsWinter, seasonID = assignHour2Season(hourWinterStart, hourWinterEnd, totalHrs, 3, seasonID, dbtValue, rhValue)
        seasonID = assignHour2Season(hourWinterStart, hourWinterEnd, totalHrs, 3, seasonID, dbtValue, rhValue)
        ##        print 'Winter: Start %d End %d Total Hours %d \n' % (hourWinterStart, hourWinterEnd, hourWinterEnd - hourWinterStart + 1)
        #        print 'seasonHrsWinter ', seasonHrsWinter

    if analysisPeriodSummer_:
        stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriodSummer_, False)
        stringSummer = str(stMonth) + ' ' + str(stDay) + ' ' + str(stHour) + ' ' + str(endMonth) + ' ' + str(endDay) + ' ' + str(endHour)
        periodSummer = stringSummer
        
        summerSeason = seasonHours(periodSummer, totalHrs)

        # Calling function to calculate Day of Year and Hour of Year for START-END period
        JulDay1, hourSummerStart = calcHourYear(summerSeason, 0)
        JulDay2, hourSummerEnd   = calcHourYear(summerSeason, 1)
        #        seasonHrsSummer, seasonID = assignHour2Season(hourSummerStart, hourSummerEnd, totalHrs, 1, seasonID, dbtValue, rhValue)
        seasonID = assignHour2Season(hourSummerStart, hourSummerEnd, totalHrs, 1, seasonID, dbtValue, rhValue)
    ##        print 'Summer: Start %d End %d Total Hours %d \n' % (hourSummerStart, hourSummerEnd, hourSummerEnd - hourSummerStart + 1)
    #        print 'seasonHrsSummer ', seasonHrsSummer
    
    #    f = open("C:\WorkingFolder\Courses\Rhino-Grasshopper-Diva\PythonStuff\BioclimaticChart\dataTMP.csv","wr")
    #    f.write('SeasonID,Temperature,RelativeHumidity\n')
    #    for m in range(0, totalHrs):
    #        string = str(seasonID[m])+', '+str(dbtValue[m])+', '+str(rhValue[m])+','
    #        f.write(string+'\n')
    #    f.close()
             
    #    print 'winterSeason ', winterSeason
    #    print 'summerSeason ', summerSeason
    ##    return seasonID, winterSeason, summerSeason
    return seasonID

def createFrequencyMesh(orgY, dryBulbTemperature, relativeHumidity, cullMesh, lb_preparation, lb_visualization):
    #Read Legend Parameters
    if legendPar_ == None:
        legendPar = [None, None, None, None, None, None, None, None]
    else: legendPar = legendPar_
    
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale,\
    legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    
    hourPts = []
    for count, ratio in enumerate(relativeHumidity):
        hourPts.append(rc.Geometry.Point3d(dryBulbTemperature[count], relativeHumidity[count], 0))
    
    #Make a mesh.
    gridSize = 5
    joinedMesh = rc.Geometry.Mesh()
    
    meshPoints = []
    for yVal in range(orgY, 100, gridSize):
    #####for yVal in range(0, 100, gridSize):
        for xVal in range(0, 100, gridSize):
            point1 = rc.Geometry.Point3d(xVal, yVal, 0)
            point2 = rc.Geometry.Point3d(xVal+gridSize, yVal, 0)
            point3 = rc.Geometry.Point3d(xVal+gridSize, yVal+gridSize, 0)
            point4 = rc.Geometry.Point3d(xVal, yVal+gridSize, 0)
            meshPoints.append([point1, point2, point3, point4])
    
    for list in  meshPoints:
        mesh = rc.Geometry.Mesh()
        for point in list:
            mesh.Vertices.Add(point)
        
        mesh.Faces.AddFace(0, 1, 2, 3)
        joinedMesh.Append(mesh)
    
    polyCurveList = []
    for list in  meshPoints:
        pointList = [list[0], list[1], list[2], list[3],list[0]]
        polyLine = rc.Geometry.PolylineCurve(pointList)
        polyCurveList.append(polyLine)
    
    #Make a list to hold values for all of the mesh faces.
    meshFrequency = []
    for count, value in enumerate(range(orgY, 100, 5)):
    ####for count, value in enumerate(range(0, 100, 5)):
        meshFrequency.append([])
        for face in range(0, 100, 5):
            meshFrequency[count].append([])
    
    def getHumidityIndex(hour):
        if   relativeHumidity[hour] < 5:  index = 0
        elif relativeHumidity[hour] < 10: index = 1
        elif relativeHumidity[hour] < 15: index = 2
        elif relativeHumidity[hour] < 20: index = 3
        elif relativeHumidity[hour] < 25: index = 4
        elif relativeHumidity[hour] < 30: index = 5
        elif relativeHumidity[hour] < 35: index = 6
        elif relativeHumidity[hour] < 40: index = 7
        elif relativeHumidity[hour] < 45: index = 8
        elif relativeHumidity[hour] < 50: index = 9
        elif relativeHumidity[hour] < 55: index = 10
        elif relativeHumidity[hour] < 60: index = 11
        elif relativeHumidity[hour] < 65: index = 12
        elif relativeHumidity[hour] < 70: index = 13
        elif relativeHumidity[hour] < 75: index = 14
        elif relativeHumidity[hour] < 80: index = 15
        elif relativeHumidity[hour] < 85: index = 16
        elif relativeHumidity[hour] < 90: index = 17
        elif relativeHumidity[hour] < 95: index = 18
        else:                             index = 19
        
        return index
    
    addGridToIndex = abs(orgY/2)
    module = gridSize/2
    
    for hour, temp in enumerate(dryBulbTemperature):
        tempIndex = int((float(temp)+addGridToIndex) / module)
        humIndex = getHumidityIndex(hour)
        if tempIndex < 28:
            meshFrequency[tempIndex][humIndex].append(1)
        
        
    #Sum all of the lists together to get the frequency.
    finalMeshFrequency = []
    for templist in meshFrequency:
        for humidlist in templist:
            finalMeshFrequency.append(sum(humidlist))
    
    #Get a list of colors
    colors = lb_visualization.gradientColor(finalMeshFrequency, lowB, highB, customColors)
    
    # color the mesh faces.
    joinedMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Gray)
    
    for srfNum in range (joinedMesh.Faces.Count):
        joinedMesh.VertexColors[4 * srfNum + 0] = colors[srfNum]
        joinedMesh.VertexColors[4 * srfNum + 1] = colors[srfNum]
        joinedMesh.VertexColors[4 * srfNum + 3] = colors[srfNum]
        joinedMesh.VertexColors[4 * srfNum + 2] = colors[srfNum]
    
    # Remove the mesh faces that do not have any hour associated with them.
    if cullMesh == True:
        cullFaceIndices = []
        for count, freq in enumerate(finalMeshFrequency):
            if freq == 0:
                cullFaceIndices.append(count)
        joinedMesh.Faces.DeleteFaces(cullFaceIndices)
    
    #Return everything that's useful.
    return hourPts, joinedMesh, finalMeshFrequency

def raggedListToDataTree(rl):
    result = DataTree[System.Object]()
    for i, leg in enumerate(rl):
    #for i in range(len(rl)):
        path = GH_Path(i)
        temp = []
        for j, leg in enumerate(rl[i]):
            temp.append(rl[i][j])
            #print 'J ', j, rl[i][j]
        result.AddRange(temp, path)
    return result

def checkComfortOrNot(strategyNames, totalHrs, comfID, pshID, ecID, htmID, nvID, epwData, epwStr):
    totalComfortOrNot = []
    comfHours = 0
    for m in range(0, totalHrs):
        if comfID[m] == 1 or pshID[m] == 1 or ecID[m] == 1 or htmID[m] == 1 or nvID[m] == 1:
        #if comfID[m] == 1:
        #if pshID[m] == 1:
        #if ecID[m] == 1:
        #if htmID[m] == 1:
        #if nvID[m] == 1:
            totalComfortOrNot.append(1)
            comfHours += 1
        else: totalComfortOrNot.append(0)
    percComfTotal = comfHours / totalHrs * 100
    ##print 'Comfortable Hours %d, which are %.2f%%' % (comfHours, percComfTotal)
    #$#$comfortResults.append('CMF: ' + str(hrsCMF) + ' hours, ' + str(cmfPercent) + '%')
    
    totalComfortOrNot.insert(0, epwStr[6])
    totalComfortOrNot.insert(0, epwStr[5])
    totalComfortOrNot.insert(0, epwStr[4])
    totalComfortOrNot.insert(0, "Boolean Value")
    combString = '%.1f%% (%d hrs) Comfortable Hours in All Strategies,  ' % (percComfTotal, comfHours)
    totalComfortOrNot.insert(0, combString)
    totalComfortOrNot.insert(0, epwStr[1])
    totalComfortOrNot.insert(0, epwStr[0])
        
    #Calculate wheather each strategy is in comfort or not for each hour. For output "strategyOrNot"        
    #---------------------------------------------        
    strategyOrNotList = []
    comfHoursStrategy = []
    percComfStrategy = []
    for count, text in enumerate(strategyNames):
        if   count == 0: stComf = list(comfID) # CZ
        elif count == 1: stComf = list(pshID)  # PSH
        elif count == 2: stComf = list(ecID)   # EC
        elif count == 3: stComf = list(htmID)  # HTM
        elif count == 4: stComf = list(nvID)   # NV
        
        comfHours = 0
        strategyOrNotList.append([])
        for m in range(0, totalHrs):
            if stComf[m] == 1:
                strategyOrNotList[count].append(1)
                comfHours += 1
            else: strategyOrNotList[count].append(0)
        comfHoursStrategy.append(comfHours)
        percComfStrategy.append(comfHoursStrategy[count] / totalHrs * 100)
        
        #print 'Comfortable Hours %d, which are %.2f%%' % (comfHoursStrategy[count], percComfStrategy[count])
        strategyOrNotList[count].insert(0, epwStr[6])
        strategyOrNotList[count].insert(0, epwStr[5])
        strategyOrNotList[count].insert(0, epwStr[4])
        strategyOrNotList[count].insert(0, "Boolean Value")
        combString = '%.1f%% (%d hrs) Comfortable Hours in %s,  ' % (percComfStrategy[count], comfHoursStrategy[count], text)
        strategyOrNotList[count].insert(0, combString)
        strategyOrNotList[count].insert(0, epwStr[1])
        strategyOrNotList[count].insert(0, epwStr[0])
    #--------------------------------------------- 
    return totalComfortOrNot, strategyOrNotList
# ****** END DEF *********************
# ************************************

def main(epwData, epwStr):
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        # Read the legend parameters.
        lowB, highB, numSeg, customColors, legendBasePoint, legendScale, \
        legendFont, legendFontSize, legendBold, decimalPlaces, \
        removeLessThan= lb_preparation.readLegendParameters(legendPar_, False)
        
        if cullMesh_:
            cullMesh = cullMesh_
        else: 
            cullMesh = False
        
        # Fix MET and Clo factor for strategies position.
        lowActivity = 3
        highActivity = 4
        defMet = 1.3
        
        winterClo = 2
        SummerClo = 5
        defClo = 0.8
    
        if basePoint_ != None:
            basePoint = basePoint_
            xP = 0.0 #basePoint_.X
            yP = 0.0 #basePoint_.Y
            zP = 0.0 #basePoint_.Z
        else: 
            basePoint = rc.Geometry.Point3d(0,0,0)
            xP, yP, zP = 0.0, 0.0, 0.0

    
        if metabolicRate_ :
            metRate = metabolicRate_
            if metabolicRate_ >= 2.0:
                actShift = highActivity
            else:
                actShift = lowActivity
            shiftFactorMet = (defMet - metRate) * actShift # Proof of concept. Need to fix later
        else:
            metRate_ = defMet
            shiftFactorMet = 0
    
        if clothingLevel_:
            cloLevel = clothingLevel_
            shiftFactorClo = (defClo - clothingLevel_) * winterClo # Proof of concept. Need to fix later
        else:
            cloLevel_ = 0.8
            shiftFactorClo = 0
        
        shiftFactor = shiftFactorMet + shiftFactorClo
        #print 'shiftFactorMet %.2f, shiftFactorClo %.2f, shiftFactor %.2f' % (shiftFactorMet, shiftFactorClo, shiftFactor)
        
        #Define color palettes for outputs and legends.
        monthColors, comfortNOcomfortColors, strategiesColors = colors()
        
        #Make chart curves.
        
        #Plot Point Values.
        #******************
        strategyNames = []
        strategyNames.append('Comfort')
        strategyNames.append('Passive Solar Heating')
        strategyNames.append('Evaporative Cooling')
        strategyNames.append('Thermal Mass + Night Vent')
        strategyNames.append('Natural Ventilation')
        
        chartHourPoints = []
        hourPointColorsByComfort = []
        hourPointColorsByMonth = []
        min_maxPoints = []
        monthPoints = []
        comfort_strategyPolygons = []
        yPointValue = []
        dbtValue = []
        location = _dryBulbTemperature[1:2][0]
        dryBulbTemperature = _dryBulbTemperature[7:]
        totalHrs = len(dryBulbTemperature)
        minTemp = 0.0
        
        for temp in dryBulbTemperature:
            dbtValue.append(temp)
            if temp < minTemp:
                minTemp = temp
                #print 'minTemp ', minTemp
            yPointValue.append(temp*2 + yP)
        gridSize = 5.0
        addGrid = (int(math.ceil(abs(minTemp / gridSize))) * (-1) * gridSize) * 2 # This is for negative temperatures
        #print 'minTemp %.1f addGrid %d' % (minTemp, addGrid)
        
        # Grid Lines *******************************
        gridLines = []
        orgX = int(0 + xP)
        orgY = int(int(addGrid) + yP)
        orgZ = int(0 + zP)
        gridStep = 10
        #print 'orgY ', orgY
        
        xLineValue = range(orgX, orgX + 110, gridStep)
        yLineValue = range(orgY, 110, gridStep)
        #starLine = rc.Geometry.Line(0, 0, 0, 0, 100, 0)
        
        for value in xLineValue:
            gridLines.append(rc.Geometry.Line(value+xP, int(addGrid)+yP, 0+zP, value+xP, 100+yP, 0+zP))
            
        for value in yLineValue: # Left to right lines
            gridLines.append(rc.Geometry.Line(0+xP, value+yP, 0+zP, 100+xP, value+yP, 0+zP))
        # End Grid Lines ****************************
        # Print Title and legends in grid: X/Y axis ****************************

        chartLayout = createChartLayout(orgX, orgY, orgZ, location, legendFont, legendFontSize, legendBold)
        
        xPointValue = []
        rhValue = []
        relativeHumidity = _relativeHumidity[7:]
        for temp in relativeHumidity:
            rhValue.append(temp)
            xPointValue.append(temp + xP)
    
        #stringSummer, stringWinter, seasonID = setSeasonID(dryBulbTemperature, relativeHumidity, totalHrs)
        seasonID = setSeasonID(dryBulbTemperature, relativeHumidity, totalHrs)
        # print 'SeasonID ', seasonID # Winter = 3, Summer = 1
    
        hourPoints = []
        hourPointsCirc = []
        ##hourColor = []
        
        colPnt1  = []
        colPnt2  = []
        colPnt3  = []
        colPnt4  = []
        colPnt5  = []
        colPnt6  = []
        colPnt7  = []
        colPnt8  = []
        colPnt9  = []
        colPnt10 = []
        colPnt11 = []
        colPnt12 = []
        
        dataRadius = 0.4
        nVert = 4
        
        #    for count, xVal in enumerate(xPointValue):
        #        centerPt = rc.Geometry.Point3d(xVal+xP, yPointValue[count]+yP, 0+zP)
        for hour in range(0, totalHrs):
        ##for hour in range(0, totalHrs - 1):
            # Colors according to Season
            if seasonID[hour] == 3:    # Winter
                colorP = [50, 50, 255]
            elif seasonID[hour] == 1:    # Summer
                colorP = [255, 255, 50]
                
            centerPt = rc.Geometry.Point3d(xPointValue[hour], yPointValue[hour]+yP, 0+zP)
            hourPoints.append(rc.Geometry.Point3d(centerPt))
            hourPointsCirc = rc.Geometry.Circle(centerPt, 0.25)
            
            # Colors according to Month
            col = monthForHour(hour)
            ##hourColor.append(col)   # Here you get the month that the hour belongs to
            
            if   col == 0:  colPnt1.append(hourPointsCirc)
            elif col == 1:  colPnt2.append(hourPointsCirc)
            elif col == 2:  colPnt3.append(hourPointsCirc)
            elif col == 3:  colPnt4.append(hourPointsCirc)
            elif col == 4:  colPnt5.append(hourPointsCirc)
            elif col == 5:  colPnt6.append(hourPointsCirc)
            elif col == 6:  colPnt7.append(hourPointsCirc)
            elif col == 7:  colPnt8.append(hourPointsCirc)
            elif col == 8:  colPnt9.append(hourPointsCirc)
            elif col == 9:  colPnt10.append(hourPointsCirc)
            elif col == 10: colPnt11.append(hourPointsCirc)
            elif col == 11: colPnt12.append(hourPointsCirc)
            
        # Collect points according to MONTH
        monthPoints.append(colPnt1)
        monthPoints.append(colPnt2)
        monthPoints.append(colPnt3)
        monthPoints.append(colPnt4)
        monthPoints.append(colPnt5)
        monthPoints.append(colPnt6)
        monthPoints.append(colPnt7)
        monthPoints.append(colPnt8)
        monthPoints.append(colPnt9)
        monthPoints.append(colPnt10)
        monthPoints.append(colPnt11)
        monthPoints.append(colPnt12)
        
        hourPts, chartMesh, meshFaceValues = createFrequencyMesh(orgY, dryBulbTemperature, relativeHumidity, cullMesh, lb_preparation, lb_visualization)
        
        # Legend for Mesh of Colors from FrequencyMesh routine
        if legendBasePoint == None:
            ####legendBasePoint = lb_visualization.BoundingBoxPar[0]
            #legendBasePoint = (rc.Geometry.Point3d(lb_visualization.BoundingBoxPar[0], lb_visualization.BoundingBoxPar[1], 0))
            legendBasePoint = rc.Geometry.Point3d(orgX + 101, orgY, 0)

        legendChartMesh = []
        legendTitle = "Hours"
        legendScale = .6 
        #legendFontSize = 2
        #lb_visualization.calculateBB(chartText, True)
        lb_visualization.calculateBB(chartLayout[0:90], True) 

        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(meshFaceValues, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
        ##legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
        legendChartMesh.append(legendSrfs)
        for list in legendTextCrv:
            for item in list:
                legendChartMesh.append(item)

        legendBasePoint = rc.Geometry.Point3d(orgX + 105, orgY, 0)

        mainLegHeight = ((lb_visualization.BoundingBoxPar[2] / 10) * legendScale) * numSeg
            
        # ***********
        #   List of Comfort Coordinates **************************
        cf_Ptlist = [27.02+xP, 42.12+yP,0.0+zP],[18.27+xP,52.64+yP,0.0+zP], [64.03+xP,45.77+yP,0.0+zP],[80.00+xP,40.78+yP,0.0+zP],\
        [27.02+xP, 42.12+yP,0.0+zP]
        
        hrsCMF, cmfPercent, comfID, comfortPolygon, comfortPolyline = strategyDraw_Calc('COMF', shiftFactor, cf_Ptlist, hourPoints, tol, dryBulbTemperature, totalHrs, 30,30,30)
        ##print 'Comf hours %d, Comf Percentage %.2f' % (hrsCMF, cmfPercent)
        
        # List of Passive Solar Heating Coordinates **************************
        pshPtList = [1.07+xP,11.83+yP,0.00+zP],[1.07+xP,42.82+yP,0.00+zP],[98.97+xP,40.44+yP,0.00+zP],[98.97+xP,9.61+yP,0.00+zP], \
        [1.07+xP,11.83+yP,0.00+zP]
    
        hrsPSH, pshPercent, pshID, pshPolygon, pshPolyline = strategyDraw_Calc('PSH', shiftFactor, pshPtList, hourPoints, tol, dryBulbTemperature, totalHrs, 200, 200, 20)
        
        ##print 'PSH hours %d, PSH Percentage %.2f' % (hrsPSH, pshPercent)
        
        #List of Evaporative Cooling Coordinates **************************
        ec_Ptlist = [16.62+xP,42.42+yP,0.0+zP],[1.07+xP,57.79+yP,0.0+zP], [1.07+xP,82.21+yP,0.0+zP],[11.18+xP,82.21+yP,0.0+zP],\
        [80.0+xP,45.79+yP,0.0+zP],[80.0+xP,40.78+yP,0.0+zP],[64.03+xP,45.77+yP,0.0+zP],[18.27+xP,52.64+yP,0.0+zP],\
        [27.02+xP,42.12+yP,0.0+zP], [16.62+xP,42.42+yP,0.0+zP]
    
        hrsEC, ecPercent, ecID, ecPolygon, ecPolyline = strategyDraw_Calc('EC', shiftFactor, ec_Ptlist, hourPoints, tol, dryBulbTemperature, totalHrs, 20, 220, 20)
        ##print 'EC hours %d, EC Percentage %.2f' % (hrsEC, ecPercent)
    
        #List of High Termal Mass **************************
        htmPtlist = [19.80+xP,42.35+yP,0.0+zP],[7.86+xP,71.28+yP,0.0+zP],[30.08+xP,71.28+yP,0.0+zP],[46.95+xP,66.03+yP,0.0+zP],\
        [80.0+xP,49.12+yP,0.0+zP],[80.0+xP,40.78+yP,0.0+zP],[64.03+xP,45.77+yP,0.0+zP],[18.27+xP,52.64+yP,0.0+zP],\
        [27.02+xP,42.12+yP,0.0+zP],[19.80+xP,42.35+yP,0.0+zP]
    
        hrsHTM, htmPercent, htmID, htmPolygon, htmPolyline = strategyDraw_Calc('HTM', shiftFactor, htmPtlist, hourPoints, tol, dryBulbTemperature, totalHrs, 180, 50, 50)
        ##print 'HTM hours %d, HTM Percentage %.2f' % (hrsHTM, htmPercent)
    
        #List of Natural Ventilation **************************
        nvPtlist = [18.27+xP,52.64+yP,0.0+zP],[18.08+xP,62.56+yP,0.0+zP],[45.56+xP,62.56+yP,0.0+zP],[97.91+xP,53.79+yP,0.0+zP],\
        [97.91+xP,40.47+yP,0.+zP], [80.0+xP,40.78+yP,0.0+zP],[64.03+xP,45.77+yP,0.0+zP],[18.27+xP,52.64+yP,0.0+zP]
    
        hrsNV, nvPercent, nvID, nvPolygon, nvPolyline  = strategyDraw_Calc('NV', shiftFactor, nvPtlist, hourPoints, tol, dryBulbTemperature, totalHrs, 50, 50, 180)
        ##print 'NV hours %d, NV Percentage %.2f' % (hrsNV, nvPercent)
    
        # Collect all strategies and results
        ##comfort_strategyPolygons.append(comfortPolygon)
        ##comfort_strategyPolygons.append(pshPolygon)
        ##comfort_strategyPolygons.append(ecPolygon)
        ##comfort_strategyPolygons.append(htmPolygon)
        ##comfort_strategyPolygons.append(nvPolygon)
        
        #This block draws the polygons with the same color. The block below this draws the strategies colored
        #If wanted, uncomment this block and comment the block below
        ###comfort_strategyPolygons.append(comfortPolyline)
        ###comfort_strategyPolygons.append(pshPolyline)
        ###comfort_strategyPolygons.append(ecPolyline)
        ###comfort_strategyPolygons.append(htmPolyline)
        ###comfort_strategyPolygons.append(nvPolyline)
        
        comfortMesh = rc.Geometry.Mesh()
        comfortMesh.Append(rc.Geometry.Mesh.CreateFromBrep(comfortPolyline)[0])
        comfortMesh.VertexColors.CreateMonotoneMesh(strategiesColors[0])
        comfort_strategyPolygons.append(comfortMesh)
        
        pshMesh = rc.Geometry.Mesh()
        pshMesh.Append(rc.Geometry.Mesh.CreateFromBrep(pshPolyline)[0])
        pshMesh.VertexColors.CreateMonotoneMesh(strategiesColors[1])
        comfort_strategyPolygons.append(pshMesh)
        
        ecMesh = rc.Geometry.Mesh()
        ecMesh.Append(rc.Geometry.Mesh.CreateFromBrep(ecPolyline)[0])
        ecMesh.VertexColors.CreateMonotoneMesh(strategiesColors[2])
        comfort_strategyPolygons.append(ecMesh)
        
        htmMesh = rc.Geometry.Mesh()
        htmMesh.Append(rc.Geometry.Mesh.CreateFromBrep(htmPolyline)[0])
        htmMesh.VertexColors.CreateMonotoneMesh(strategiesColors[3])
        comfort_strategyPolygons.append(htmMesh)
        
        nvMesh = rc.Geometry.Mesh()
        nvMesh.Append(rc.Geometry.Mesh.CreateFromBrep(nvPolyline)[0])
        nvMesh.VertexColors.CreateMonotoneMesh(strategiesColors[4])
        comfort_strategyPolygons.append(nvMesh)


        #for count, value in enumerat(evapCooling):
        #    if comfortList[count] == 1:
        #        value = 0
        #    else: pass
        
        comfortResults = []
        comfortResults.append('CMF: ' + str(hrsCMF) + ' hours, ' + str(cmfPercent) + '%')
        comfortResults.append('PSH: ' + str(hrsPSH) + ' hours, ' + str(pshPercent) + '%')
        comfortResults.append('EC:  ' + str(hrsEC)  + ' hours, ' + str(ecPercent)  + '%')
        comfortResults.append('HTM: ' + str(hrsHTM) + ' hours, ' + str(htmPercent) + '%')
        comfortResults.append('NV:  ' + str(hrsNV)  + ' hours, ' + str(nvPercent)  + '%')
        
        strategyPercent = []
        strategyPercent.append(cmfPercent)
        strategyPercent.append(pshPercent)
        strategyPercent.append(ecPercent)
        strategyPercent.append(htmPercent)
        strategyPercent.append(nvPercent)
        
        strategyHours = []
        strategyHours.append(hrsCMF)
        strategyHours.append(hrsPSH)
        strategyHours.append(hrsEC)
        strategyHours.append(hrsHTM)
        strategyHours.append(hrsNV)
        
        min_maxPointsList, strategyMonth, colByComfortList, colByMonthList = monthCalcs(totalHrs, comfID, pshID, ecID, htmID, nvID, dryBulbTemperature, relativeHumidity, monthPoints, monthColors, comfortNOcomfortColors)
        
        #f = open("C:\WorkingFolder\Courses\Rhino-Grasshopper-Diva\PythonStuff\BioclimaticChart\dataTMP.csv","wr")
        #f.write('SeasonID,Temperature,RelativeHumidity, Comfort, PSH, EC, HTM, NV\n')
        #for m in range(0, totalHrs):
        #    string = str(seasonID[m])+', '+str(dbtValue[m])+', '+str(rhValue[m])+', '+str(comfID[m])+', '+str(pshID[m])+', '+str(ecID[m])+', '+str(htmID[m])+', '+str(nvID[m])+','
        #    f.write(string+'\n')
        #f.close()
        
        totalComfortOrNot, strategyOrNotList = checkComfortOrNot(strategyNames, totalHrs, comfID, pshID, ecID, htmID, nvID, epwData, epwStr)
        
        chartLegend = createChartLegend(orgX, orgY, orgZ, strategyNames, lb_preparation, legendScale, legendFont, legendFontSize, legendBold, lb_visualization, strategiesColors, monthColors, comfortNOcomfortColors, customColors, totalComfortOrNot)
        
        if calculateCharts_ == True:
            resultsChart = showResults(basePoint_, mainLegHeight, strategyNames, strategyPercent, strategyHours, strategyMonth, \
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, lb_preparation, lb_visualization, strategiesColors)
        else:
            resultsChart = None
             
        #If the user has selected to scale or move the geometry, scale it all and/or move it all.
        #if basePoint_ != None:
            #basePoint = basePoint_
        #else: basePoint = rc.Geometry.Point3d(0,0,0)
        
        if scale_ != None:
            scale = scale_
        else: scale = 1
        
        chartGridAndTxt = []
        for item in gridLines: chartGridAndTxt.append(item)
        for item in chartLayout: chartGridAndTxt.append(item) 
        for item in chartLegend: chartGridAndTxt.append(item) 
        
        scaleFinal = rc.Geometry.Transform.Scale(basePoint, scale)
        move = rc.Geometry.Transform.Translation(basePoint.X, basePoint.Y, basePoint.Z)
        transformMtx = scaleFinal * move
        for geo in comfort_strategyPolygons: geo.Transform(transformMtx)
        chartMesh.Transform(transformMtx)
        for geo in chartLayout: geo.Transform(transformMtx)
        for geo in chartLegend: geo.Transform(transformMtx)
        for geo in legendChartMesh: geo.Transform(transformMtx)
        legendBasePoint.Transform(transformMtx)
        for geo in gridLines: geo.Transform(transformMtx)
        for geoList in monthPoints:
            for geo in geoList:
                geo.Transform(transformMtx)
        for geoList in min_maxPointsList: 
            for geo in geoList:
                geo.Transform(transformMtx)
        if calculateCharts_ == True:
            for geo in resultsChart: geo.Transform(transformMtx)
        
        #hourPointColorsByComfort = []
        #hourPointColorsByMonth = []
        
        #Unpack the data tree of point colors. THIS WORKS FINE BUT I LEFT THE BELOW's OPTION.
        #hourPointColorsByComfort = DataTree[Object]()
        #for listCount, list in enumerate(colByComfortList):
        #    for item in list:
        #        hourPointColorsByComfort.Add(item, GH_Path(listCount))
        
        #print 'monthPoints ', len(monthPoints[0])
        chartHourPoints          = raggedListToDataTree(monthPoints)
        hourPointColorsByComfort = raggedListToDataTree(colByComfortList)
        hourPointColorsByMonth   = raggedListToDataTree(colByMonthList)
        
        strategyOrNot = raggedListToDataTree(strategyOrNotList)
        
        ##monthPointsTree = raggedListToDataTree(monthPoints)
        min_maxPoints            = raggedListToDataTree(min_maxPointsList)
        
        return comfortResults, totalComfortOrNot, strategyOrNot, \
        chartGridAndTxt, chartMesh, legendChartMesh, chartHourPoints, hourPointColorsByComfort, hourPointColorsByMonth, min_maxPoints, \
        comfort_strategyPolygons, legendComfortStrategies, legendBasePt, resultsChart
        
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1


#Check the inputs.
checkData = False
if _runIt == True:
    checkData, epwData, epwStr = checkInputs()

#If the inputs are good, run the function.
if checkData == True:
    comfortResults, totalComfortOrNot, strategyOrNot, \
    chartGridAndTxt, chartMesh, legendChartMesh, chartHourPoints, hourPointColorsByComfort, hourPointColorsByMonth, min_maxPoints, \
    comfort_strategyPolygons, legendComfortStrategies, legendBasePt, resultsChart = main(epwData, epwStr)
    
    
#Hide/Show outnputs
ghenv.Component.Params.Output[6].Hidden  = False # Grid and Text
ghenv.Component.Params.Output[7].Hidden  = True  # Chart Mesh
ghenv.Component.Params.Output[8].Hidden  = True  # legendChartMesh
ghenv.Component.Params.Output[9].Hidden  = True  # chartHourPoints
#ghenv.Component.Params.Output[10].Hidden  = True  # hourPointColorsByComfort - This is data
#ghenv.Component.Params.Output[11].Hidden  = True  # hourPointColorsByMonth - This is data
ghenv.Component.Params.Output[12].Hidden = True  # min/max Points
ghenv.Component.Params.Output[13].Hidden = False # StrategyPolygons
ghenv.Component.Params.Output[14].Hidden = True  # legend
ghenv.Component.Params.Output[17].Hidden = True  # Results Chart

