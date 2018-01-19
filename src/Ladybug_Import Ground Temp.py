# Ground Temperature Calculator
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Anton Szilasi with help from Chris Mackey <ajszilasi@gmail.com> 
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
Use this component to visualise ground temperatures throughout the year at specific depths. Please note that epw files usually only provide ground temperature data at depths 0.5 meters, 2 meters and 4 meters thus data has been interpolated for all other depths. In particular this interpolation assumes that ground temperatures do not vary over the seasons once the depth has reach 9 meters below the ground surface.

-
Provided by Ladybug 0.0.66
    
    Args:
        _groundTemperatureData: ...
        _epwFile: An .epw file path on your system as a string
        visualisedata_Season: Set to true to visualise the ground temperature data as an average for every season
        visualisedata_Month: Set to true to visualise the ground temperature data for every month
        
    Returns:
        readMe!: ...
        groundtemp1st: In every epw file there are monthly ground temperatures at 3 different depths this is the 1st
        groundtemp2nd: In every epw file there are monthly ground temperatures at 3 different depths this is the 2nd
        groundtemp3rd: In every epw file there are monthly ground temperatures at 3 different depths this is the 3rd
        graphAxes: This output draws the axes of the graph it doesn't need to be connected to anything
        graphtext: This output draws the text of the graph it doesn't need to be connected to anything
        crvColors: This output draws the colours of the temperature curves connect it to S of the Grasshopper component Custom Preview
        profileCrvs: This output draws the curves of the temperature curves connect it to G of the Grasshopper component Custom Preview
"""
ghenv.Component.Name = "Ladybug_Import Ground Temp"
ghenv.Component.NickName = 'Importgroundtemp'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.58\nJAN_10_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import scriptcontext as sc
import os
import itertools
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import Rhino as rc
import System


def drawLegend(colors):
    # A function which draws the legend box in the Rhino Viewport
    dataMeshes = []
    
    def draw_Legendbox(x,z1,z2,color): 
        dataMeshes = []
        
        facePt1 = rc.Geometry.Point3d(rectangleCenterPt.X-5, rectangleCenterPt.Y, rectangleCenterPt.Z-z1)
        facePt2 = rc.Geometry.Point3d(rectangleCenterPt.X-5+x, rectangleCenterPt.Y, rectangleCenterPt.Z-z1)
        facePt3 = rc.Geometry.Point3d(rectangleCenterPt.X-5, rectangleCenterPt.Y, rectangleCenterPt.Z-z2)
        facePt4 = rc.Geometry.Point3d(rectangleCenterPt.X-5+x, rectangleCenterPt.Y, rectangleCenterPt.Z-z2)
    
        # Create the mesh of the bars themselves
        barMesh = rc.Geometry.Mesh()
        for point in [facePt1, facePt2, facePt3, facePt4]:
            barMesh.Vertices.Add(point)
        barMesh.Faces.AddFace(0, 1, 3, 2)
        
        barMesh.Flip(True, True, True)
        # Color the mesh faces
        barMesh.VertexColors.CreateMonotoneMesh(color)
        dataMeshes.append(barMesh)
    
        return dataMeshes
        
    def draw_Legendboxlabel(x,z,text):
        legPlane = rc.Geometry.Plane(rc.Geometry.Point3d(x,5,z), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(1,0,1))
        legPt = rc.Geometry.Point3d(x,0,z)
        textSrfs = lb_visualization.text2srf([text], [legPt],'Verdana', 0.3, False, legPlane)
        
        for txt in textSrfs:
            graphtext.extend(txt)
        return graphtext
    
    dataMeshes.extend(draw_Legendbox(2,10,10.5,colors[0]))
    dataMeshes.extend(draw_Legendbox(2,10.75,11.25,colors[1]))
    dataMeshes.extend(draw_Legendbox(2,11.5,12,colors[2]))
    dataMeshes.extend(draw_Legendbox(2,12.25,12.75,colors[3]))
    
    dataMeshes.extend(draw_Legendboxlabel(2.5,-10.25,'winter'))
    dataMeshes.extend(draw_Legendboxlabel(2.5,-11,'spring'))
    dataMeshes.extend(draw_Legendboxlabel(2.5,-11.75,'autumn'))
    dataMeshes.extend(draw_Legendboxlabel(2.5,-12.5,'summer'))
    
    return dataMeshes

def drawAxes(groundtemp1st,groundtemp2nd,groundtemp3rd):
    #Create a surface to represent the ground plane
    xyPlane = rc.Geometry.Plane.WorldXY
    rectangle = rc.Geometry.Rectangle3d(xyPlane, 10, 10)
    rectangleCurve = rectangle.ToNurbsCurve()
    
    rectangleBrep = rc.Geometry.Brep.CreatePlanarBreps(rectangleCurve)[0]
    
    global rectangleCenterPt
    
    rectangleCenterPt = rc.Geometry.AreaMassProperties.Compute(rectangleBrep).Centroid # Create a reference point for all lines to refere to
    
    #Create a line to represent the vertical axis.
    
    rectanglePt1 = rc.Geometry.Point3d(rectangleCenterPt.X-5, rectangleCenterPt.Y, rectangleCenterPt.Z)
    rectanglePt2 = rc.Geometry.Point3d(rectangleCenterPt.X-5, rectangleCenterPt.Y, rectangleCenterPt.Z-10)
    verticalAxis = rc.Geometry.LineCurve(rectanglePt1, rectanglePt2)
    
    #Create markings along this vertical axis every meter.
    divisionParams = rc.Geometry.Curve.DivideByLength(verticalAxis, 1, False)
    divisionPts = []
    for param in divisionParams:
        divisionPts.append(verticalAxis.PointAt(param))
    
    divisionLines = []
    for point in divisionPts:
        otherPt = rc.Geometry.Point3d(point.X+0.25, point.Y, point.Z)
        divisionLines.append(rc.Geometry.Line(point, otherPt))
    
    #Create a line that represents the horizontal axis.
    horizPt1 = rc.Geometry.Point3d(rectangleCenterPt.X+5, rectangleCenterPt.Y, rectangleCenterPt.Z)
    horizPt2 = rc.Geometry.Point3d(rectangleCenterPt.X-5, rectangleCenterPt.Y, rectangleCenterPt.Z)
    horizAxis = rc.Geometry.LineCurve(horizPt1, horizPt2) # Draw a line between these two points making the horizontail axis
    
    #Create markings along this horizontial axis every degree C.
    divisionParams1 = rc.Geometry.Curve.DivideByLength(horizAxis, 1, False)
    divisionPts1 = []
    for param in divisionParams1:
        divisionPts1.append(horizAxis.PointAt(param))
    
    divisionLines1 = []
    for point in divisionPts1:
        otherPt1 = rc.Geometry.Point3d(point.X, point.Y, point.Z-0.25)
        divisionLines1.append(rc.Geometry.Line(point, otherPt1))
    
    # Creating range of ground temp data to display on horizontial axis of graph
    global groundtempall
    groundtempall = groundtemp1st[7:] + groundtemp2nd[7:] + groundtemp3rd[7:] # Adding the ground temp data from each of the ground temp depths (1st,2nd and 3rd) in the epw file
    groundtempCtext = [] # The text (numbers) that will be shown as labels on the horzontial axis 
    global ratio
    ratio = (max(groundtempall)-min(groundtempall))/(len(divisionPts1)-1) # How many degrees C on the horzontial axis one Rhino square corresponds to
    groundtempCtext.append(min(groundtempall))
    tot = groundtempCtext[0]
    
    for i in range(len(divisionPts1)-1): 
        tot += ratio
        groundtempCtext.append(tot)
    
    #Put all of the above into a list for the graphAxes output.
    graphAxes = [rectangleBrep, verticalAxis, horizAxis]
    graphAxes.extend(divisionLines) # Markers on vertical axis
    graphAxes.extend(divisionLines1) # Markers on horizontial axis
    
    return divisionPts,divisionPts1,groundtempCtext,graphAxes

# These 3 function inputs are taken from drawAxes function
def drawText(divisionPts,divisionPts1,groundtempCtext): 
    graphtext = []
    
    # Drawing the labels on the vertical axis
    graphtextvert = []
    for point in divisionPts: 
        textPlane = rc.Geometry.Plane(rc.Geometry.Point3d(point[0]-1.5, point[1], point[2]), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(0,0,1)) # A new point is made to offset labels from vertical axis 
        textSrfs = lb_visualization.text2srf([str(point[2]) + ' m'], [rc.Geometry.Point3d(point[0]-1.5, point[1], point[2])],'Verdana', 0.25, False, textPlane)
        for txt in textSrfs:
            graphtextvert.extend(txt)
        
    # Drawing the labels on the horzontial axis
    graphtexthort = []
    divisionPts1.sort()
    
    for point,i in zip(divisionPts1,groundtempCtext):
        textPlane = rc.Geometry.Plane(rc.Geometry.Point3d(point[0], point[1], point[2]+0.3), rc.Geometry.Vector3d(1,1,1),  rc.Geometry.Vector3d(0,1,1))
        textSrfs2 = lb_visualization.text2srf([str(round(i,1)) + ' C'], [rc.Geometry.Point3d(point[0], point[1], point[2]+0.3)],'Verdana', 0.25, False, textPlane) # Point should be groundtemp data
        for txt in textSrfs2: # Adding text surfaces to graphtext so that they will be displayed in Rhino View ports
            graphtexthort.extend(txt)
        for labels in graphtexthort:
            xtozxrotation = rc.Geometry.Transform.Translation(0,0,0)
            labels.Transform(xtozxrotation)
    
    for txt in textSrfs:
        graphtext.extend(txt)
    
    graphtext = graphtexthort + graphtextvert 
    
    # Create title on vertical axis
    legPlane = rc.Geometry.Plane(rc.Geometry.Point3d(-3,5,-5), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(0,0,1))
    legPt = rc.Geometry.Point3d(-2,-1,0)
    textSrfs3 = lb_visualization.text2srf(['Depth'], [legPt],'Verdana', 0.3, False, legPlane)
    for txt in textSrfs3:
        graphtext.extend(txt)
    
    # Create title on horizontial axis
    legPlane1 = rc.Geometry.Plane(rc.Geometry.Point3d(3.5,5,1.5), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(1,0,1))
    legPt1 = rc.Geometry.Point3d(0,0,0)
    
    textSrfs4 = lb_visualization.text2srf(['Ground Temperature'], [legPt1],'Verdana', 0.3, False, legPlane1)
    for txt in textSrfs4:
        graphtext.extend(txt)
        
    return graphtext

def drawprofileCrvs_Season(groundtemp1st,groundtemp2nd,groundtemp3rd):
    #Create a list of the depths that each list corresponds to.
    depthsList = [0.5, 2, 4]
    #Find the annual average temperature, which will be the temperature at very low depths.
    annualAvg = sum(groundtemp1st[7:])/12 
    #Find the maximum deviation around this for get a scale for the horizontal axis.
    allValues = []
    allValues.extend(groundtemp1st[7:])
    allValues.extend(groundtemp2nd[7:])
    allValues.extend(groundtemp3rd[7:])

    # The function orderbyseason returns a list of dictionaries with temperatures for each season and their correponding depths
    def orderbyseason(groundtemp1st,groundtemp2nd,groundtemp3rd): 
        alllists = []
        alllists.append(groundtemp1st)
        alllists.append(groundtemp2nd)
        alllists.append(groundtemp3rd)
    
        #Before defining seasons test whether site is in Northern or Southern Hemisphere 
        if latitude.find("-") == -1: # If true site is in the Northern Hemisphere
            winter = {} 
            spring = {}
            summer = {}
            autumn = {}
            
            for count,i in enumerate(alllists):
                if count == 0: # Depth at 0.5 m
                    winter['0.5']= sum(groundtemp1st[7:9]+groundtemp1st[18:])/3
                    spring['0.5']= sum(groundtemp1st[9:12])/3
                    summer['0.5']= sum(groundtemp1st[12:15])/3
                    autumn['0.5']= sum(groundtemp1st[15:18])/3
                if count == 1: # Depth at 2 m 
                    winter['2'] = sum(groundtemp2nd[7:9]+groundtemp2nd[18:])/3
                    spring['2'] = sum(groundtemp2nd[9:12])/3
                    summer['2'] = sum(groundtemp2nd[12:15])/3
                    autumn['2'] = sum(groundtemp2nd[15:18])/3
                if count == 2: # Depth at 4 m
                    winter['4'] = sum(groundtemp3rd[7:9]+groundtemp3rd[18:])/3
                    spring['4'] = sum(groundtemp3rd[9:12])/3
                    summer['4'] = sum(groundtemp3rd[12:15])/3
                    autumn['4']= sum(groundtemp3rd[15:18])/3
        else: # Site is in the Southern Hemisphere
            winter = {} 
            spring = {}
            summer = {}
            autumn = {}
            
            for count,i in enumerate(alllists):
                if count == 0: # Depth at 0.5 m
                    winter['0.5']= sum(groundtemp1st[12:15])/3
                    spring['0.5']= sum(groundtemp1st[15:18])/3
                    summer['0.5']= sum(groundtemp1st[7:9]+groundtemp1st[18:])/3
                    autumn['0.5']= sum(groundtemp1st[9:12])/3
                if count == 1: # Depth at 2 m 
                    winter['2']= sum(groundtemp2nd[12:15])/3
                    spring['2']= sum(groundtemp2nd[15:18])/3
                    summer['2']= sum(groundtemp2nd[7:9]+groundtemp2nd[18:])/3
                    autumn['2']= sum(groundtemp2nd[9:12])/3
                if count == 2: # Depth at 4 m
                    winter['4']= sum(groundtemp3rd[12:15])/3
                    spring['4']= sum(groundtemp3rd[15:18])/3
                    summer['4']= sum(groundtemp3rd[7:9]+groundtemp3rd[18:])/3
                    autumn['4']= sum(groundtemp3rd[9:12])/3
        return winter,spring,autumn,summer, # Return the seasons in this order
        
    seasons = orderbyseason(groundtemp1st,groundtemp2nd,groundtemp3rd)
   
    #Create the points for the season temperature curves
    ptsList = []
    crvColors = []
    colors = System.Drawing.Color.LightBlue,System.Drawing.Color.ForestGreen,System.Drawing.Color.Yellow,System.Drawing.Color.Tomato 
    
    # Colors for season curves in order of winter,spring,autumn,summer 
    for i,season in enumerate(seasons): # Drawing season curves and their corresponding colours.
        pt1 = rc.Geometry.Point3d(rectangleCenterPt.X+((season['0.5']-min(groundtempall))/ratio)-4,rectangleCenterPt.Y, rectangleCenterPt.Z-0.5)
        pt2 = rc.Geometry.Point3d(rectangleCenterPt.X+((season['2']-min(groundtempall))/ratio)-4, rectangleCenterPt.Y, rectangleCenterPt.Z-2)
        pt3 = rc.Geometry.Point3d(rectangleCenterPt.X+((season['4']-min(groundtempall))/ratio)-4, rectangleCenterPt.Y, rectangleCenterPt.Z-4)
        pt4 = rc.Geometry.Point3d(rectangleCenterPt.X, rectangleCenterPt.Y, rectangleCenterPt.Z-9)
        ptsList.append([pt1, pt2, pt3,pt4])
    
        crvColors.append(colors[i]) # Appending colors to color curves in order of the list colors
    
    #Create the ground profile curves.
    profileCrvs = []
    for list in ptsList:
    
        seasonCrv = rc.Geometry.Curve.CreateInterpolatedCurve(list, 3)
        profileCrvs.append(seasonCrv)
    
    return profileCrvs,crvColors,colors

def drawprofileCrvs_Month(groundtemp1st,groundtemp2nd,groundtemp3rd):
    #Find the annual average temperature, which will be the temperature at very low depths.
    annualAvg = sum(groundtemp1st[7:])/12 
    
    #Find the maximum deviation around this for get a scale for the horizontal axis.
    allValues = []
    allValues.extend(groundtemp1st[7:])
    allValues.extend(groundtemp2nd[7:])
    allValues.extend(groundtemp3rd[7:])
    
    allValues.sort()
    maxDiff = max(allValues) - annualAvg
    minDiff = annualAvg - min(allValues)
    
    if maxDiff > minDiff: diffFactor = maxDiff/4
    else: diffFactor = minDiff/4
    
    # Originally readLegendParameters output 9 variables not it outputs 11 but this component only uses the first 
    # 9 so dummy variables were added as a work around for hte too many variables to unpack error.
    
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold,dummyvariable1,dummyvariable2 = lb_preparation.readLegendParameters([], False)
    
    # colors = lb_visualization.gradientColor(range(12), 0, 11, customColors) ophaned code, initally each month line was a different colour now colouring by season
    
    #Create the points for the temperature profile curves
    ptsList = []
    crvColors = []
    
    if latitude.find("-") == -1: # If true site is in the Northern Hemisphere
        for count in range(12):
            pt1 = rc.Geometry.Point3d(rectangleCenterPt.X + (groundtemp1st[count+7]- annualAvg)/diffFactor, rectangleCenterPt.Y, rectangleCenterPt.Z-0.5)
            pt2 = rc.Geometry.Point3d(rectangleCenterPt.X + (groundtemp2nd[count+7]- annualAvg)/diffFactor, rectangleCenterPt.Y, rectangleCenterPt.Z-2)
            pt3 = rc.Geometry.Point3d(rectangleCenterPt.X + (groundtemp3rd[count+7]- annualAvg)/diffFactor, rectangleCenterPt.Y, rectangleCenterPt.Z-4)
            pt4 = rc.Geometry.Point3d(rectangleCenterPt.X, rectangleCenterPt.Y, rectangleCenterPt.Z-9)
            ptsList.append([pt1, pt2, pt3, pt4])
            
            if (count == 0) or (count == 1) or (count == 11): # Winter in Northern Hemisphere
                crvColors.append(System.Drawing.Color.LightBlue)
            elif (count == 2) or (count == 3) or (count == 4):  # Spring in Northern Hemisphere
                crvColors.append(System.Drawing.Color.ForestGreen) 
            elif (count == 5) or (count == 6) or (count == 7):  # Summer in Northern Hemisphere
                crvColors.append(System.Drawing.Color.Tomato) 
            elif (count == 8) or (count == 9) or (count == 10):  # Autumn in Northern Hemisphere
                crvColors.append(System.Drawing.Color.Yellow) # Autumn
    else: # Site in Southern Hemisphere 
        for count in range(12):
            pt1 = rc.Geometry.Point3d(rectangleCenterPt.X + (groundtemp1st[count+7]- annualAvg)/diffFactor, rectangleCenterPt.Y, rectangleCenterPt.Z-0.5)
            pt2 = rc.Geometry.Point3d(rectangleCenterPt.X + (groundtemp2nd[count+7]- annualAvg)/diffFactor, rectangleCenterPt.Y, rectangleCenterPt.Z-2)
            pt3 = rc.Geometry.Point3d(rectangleCenterPt.X + (groundtemp3rd[count+7]- annualAvg)/diffFactor, rectangleCenterPt.Y, rectangleCenterPt.Z-4)
            pt4 = rc.Geometry.Point3d(rectangleCenterPt.X, rectangleCenterPt.Y, rectangleCenterPt.Z-9)
            ptsList.append([pt1, pt2, pt3, pt4])
            
            if (count == 0) or (count == 1) or (count == 11): # Summer in Southern Hemisphere
                crvColors.append(System.Drawing.Color.Tomato) 
            elif (count == 2) or (count == 3) or (count == 4):  # Autumn in Southern Hemisphere
                crvColors.append(System.Drawing.Color.Yellow) 
            elif (count == 5) or (count == 6) or (count == 7):  # Winter in Southern Hemisphere
                crvColors.append(System.Drawing.Color.LightBlue) 
            elif (count == 8) or (count == 9) or (count == 10):  # Spring in Northern Hemisphere
                crvColors.append(System.Drawing.Color.ForestGreen) 
    
    #Create the ground profile curves.
    profileCrvs = []
    for list in ptsList:
        monthCrv = rc.Geometry.Curve.CreateInterpolatedCurve(list, 3)
        profileCrvs.append(monthCrv)
        
    return profileCrvs,crvColors

def main(_epw_file):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
            
        # Create an instance of the lb_preparation class 
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        if not os.path.isfile(_epw_file):
            warningM = "Failed to find the file: " + str(_epw_file)
            print warningM
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warningM)
            return -1
        locationData = lb_preparation.epwLocation(_epw_file)
        groundtemp = lb_preparation.groundTempData(_epw_file,locationData[0])
        
        lb_preparation.printgroundTempData(lb_preparation.groundtemp)

        return locationData, groundtemp, lb_visualization, lb_preparation
    
    else:
        warningM = "First please let the Ladybug fly..."
        print warningM
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warningM)
        return -1


# Collecting Data from epw
if _epwFile and _epwFile.endswith('.epw') and  _epwFile != 'C:\Example.epw':
    result = main(_epwFile)
    if result!= -1:
        location, locName, latitude = result[0][-1], result[0][0], result[0][1]
        
        groundtemp1st,groundtemp2nd,groundtemp3rd = result[1][0],result[1][1],result[1][2]
     
        lb_visualization, lb_preparation = result[2], result[3]
elif _epwFile == 'C:\Example.epw': pass
else:
    print "Please connect a valid epw file address to _epw_file input..."

# Graphing the ground temperature data 

if visualisedata_Season == True and visualisedata_Month == True and (result!= -1):
    print "This component cannot draw both season and month curves please only set visualisedata_Season or visualisedata_Month to True but not both"
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "This component cannot draw both season and month curves please only set visualisedata_Season or visualisedata_Month to True but not both")
elif visualisedata_Season == True:
    divisionPts,divisionPts1,groundtempCtext,graphAxes = drawAxes(groundtemp1st,groundtemp2nd,groundtemp3rd)
    graphtext = drawText(divisionPts,divisionPts1,groundtempCtext)
    # Draw text above graph which shows location
    Plane = rc.Geometry.Plane(rc.Geometry.Point3d(3.5,5,2.5), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(0,0,1))
    textSrfs5 = lb_visualization.text2srf([str(location.split(",")[1])], [rc.Geometry.Point3d(-2,5,0)],'Verdana', 0.3, False, Plane)
    for txt in textSrfs5:
        graphtext.extend(txt)
    profileCrvs,crvColors,colors = drawprofileCrvs_Season(groundtemp1st,groundtemp2nd,groundtemp3rd)
    Legend = drawLegend(colors)
elif visualisedata_Month == True:
    # Draw graph axes 
    divisionPts,divisionPts1,groundtempCtext,graphAxes = drawAxes(groundtemp1st,groundtemp2nd,groundtemp3rd)
    # Draw graph text
    graphtext = drawText(divisionPts,divisionPts1,groundtempCtext)
    # Draw text above graph which shows location
    Plane = rc.Geometry.Plane(rc.Geometry.Point3d(3.5,5,2.5), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(0,0,1))
    textSrfs5 = lb_visualization.text2srf([str(location.split(",")[1])], [rc.Geometry.Point3d(-2,5,0)],'Verdana', 0.3, False, Plane)
    for txt in textSrfs5:
        graphtext.extend(txt)
    #locationtext = lb_visualization.text2srf([str() + ' m'], [rc.Geometry.Point3d(point[0]-1.5, point[1], point[2])],'Verdana', 0.25, False, textPlane)
    profileCrvs,crvColors = drawprofileCrvs_Month(groundtemp1st,groundtemp2nd,groundtemp3rd)
    # Create legend colours in order of winter, spring, Autumn and Summer
    Legendcolors = [System.Drawing.Color.LightBlue,System.Drawing.Color.ForestGreen,System.Drawing.Color.Yellow,System.Drawing.Color.Tomato]
    Legend = drawLegend(Legendcolors)
