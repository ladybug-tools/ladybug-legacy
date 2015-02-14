# Ground Temperature Calculator
# By Anton Szilasi with help from Chris Mackey
# ajszilasi@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate the hourly ground temperature at a specific depth.

-
Provided by Ladybug 0.0.58
    
    Args:
        _groundTemperatureData: ...
        _epwFile: An .epw file path on your system as a string
        visualisedata: Set to true to visualise data as a graph
    Returns:
        readMe!: ...
        groundtemp1st: In every epw file there are monthly ground temperatures at 3 different depths this is the 1st
        groundtemp2nd: In every epw file there are monthly ground temperatures at 3 different depths this is the 2nd
        groundtemp3rd: In every epw file there are monthly ground temperatures at 3 different depths this is the 3rd
        graphAxes , profileCrvs, graphdata, graphtext: All these combine to create graph outputs they dont need to be connected to any objects to work

"""
ghenv.Component.Name = "Ladybug_Import Ground Temp"
ghenv.Component.NickName = 'Importgroundtemp'
ghenv.Component.Message = 'VER 0.0.58\nFEB_14_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.58\nJAN_10_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import os
import itertools
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import Rhino as rc
import System

def main(_epw_file):
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
        
        if not os.path.isfile(_epw_file):
            warningM = "Failed to find the file: " + str(_epw_file)
            print warningM
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warningM)
            return -1
        locationData = lb_preparation.epwLocation(_epw_file)
        groundtemp = lb_preparation.groundTempData(_epw_file,locationData[0])
        
        
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
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "Please connect a valid epw file address to _epw_file input...")
    
# Graphing the ground temperature data 

if visualisedata_Season == True and visualisedata_Month == True:
    
    print "This component cannot draw both season and month curves please only set visualisedata_Season or visualisedata_Month to True but not both"
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "This component cannot draw both season and month curves please only set visualisedata_Season or visualisedata_Month to True but not both")
    
elif visualisedata_Season == True:

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
        
        groundtempall = groundtemp1st[8:] + groundtemp2nd[8:] + groundtemp3rd[8:] # Adding the ground temp data from each of the ground temp depths (1st,2nd and 3rd) in the epw file
    
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
    
        legPlane = rc.Geometry.Plane(rc.Geometry.Point3d(-3,0,-5), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(0,0,1))

        legPt = rc.Geometry.Point3d(-2,-1,0)
    
        textSrfs3 = lb_visualization.text2srf(['Depth'], [legPt],'Verdana', 0.3, False, legPlane)

        for txt in textSrfs3:
            graphtext.extend(txt)
        
        # Create title on horizontial axis
    
        legPlane1 = rc.Geometry.Plane(rc.Geometry.Point3d(3.5,0,1.5), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(1,0,1))

        legPt1 = rc.Geometry.Point3d(0,0,0)
    
        textSrfs4 = lb_visualization.text2srf(['Ground Temperature'], [legPt1],'Verdana', 0.3, False, legPlane1)

        for txt in textSrfs4:
            graphtext.extend(txt)
        return graphtext
        
    def drawprofileCrvs_Season(groundtemp1st,groundtemp2nd,groundtemp3rd):
        #Create a list of the depths that each list corresponds to.
        depthsList = [0.5, 2, 4]

        #Find the annual average temperature, which will be the temperature at very low depths.
        annualAvg = sum(groundtemp1st[8:])/12 ## [8:] denotes from 8th row in list onwards as in groundtemp1st,groundtemp2nd etc data starts in 8th row

        #Find the maximum deviation around this for get a scale for the horizontal axis.
        allValues = []
        allValues.extend(groundtemp1st[8:])
        allValues.extend(groundtemp2nd[8:])
        allValues.extend(groundtemp3rd[8:])
    
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
                        winter['0.5']= sum(groundtemp1st[8:10]+groundtemp1st[19:])/3

                        spring['0.5']= sum(groundtemp1st[10:13])/3

                        summer['0.5']= sum(groundtemp1st[13:16])/3

                        autumn['0.5']= sum(groundtemp1st[16:19])/3
                    
                    if count == 1: # Depth at 2 m 
                    
                        winter['2'] = sum(groundtemp2nd[8:10]+groundtemp2nd[19:])/3
    
                        spring['2'] = sum(groundtemp2nd[10:13])/3

                        summer['2'] = sum(groundtemp2nd[13:16])/3

                        autumn['2'] = sum(groundtemp2nd[16:19])/3
                    
                    if count == 2: # Depth at 4 m
                    
                        winter['4'] = sum(groundtemp3rd[8:10]+groundtemp3rd[19:])/3
    
                        spring['4'] = sum(groundtemp3rd[10:13])/3

                        summer['4'] = sum(groundtemp3rd[13:16])/3

                        autumn['4']= sum(groundtemp3rd[16:19])/3
                        
            else: # Site is in the Southern Hemisphere
                
                winter = {} 
                spring = {}
                summer = {}
                autumn = {}

                for count,i in enumerate(alllists):
                    
                    if count == 0: # Depth at 0.5 m
                    
                        winter['0.5']= sum(groundtemp1st[13:16])/3
                        
                        spring['0.5']= sum(groundtemp1st[16:19])/3
                
                        summer['0.5']= sum(groundtemp1st[8:10]+groundtemp1st[19:])/3
    
                        autumn['0.5']= sum(groundtemp1st[10:13])/3

                    if count == 1: # Depth at 2 m 
                    
                        winter['2']= sum(groundtemp2nd[13:16])/3
                        
                        spring['2']= sum(groundtemp2nd[16:19])/3
                   
                        summer['2']= sum(groundtemp2nd[8:10]+groundtemp2nd[19:])/3
    
                        autumn['2']= sum(groundtemp2nd[10:13])/3
                    
                    if count == 2: # Depth at 4 m
                    
                        winter['4']= sum(groundtemp3rd[13:16])/3
                        
                        spring['4']= sum(groundtemp3rd[16:19])/3
                    
                        summer['4']= sum(groundtemp3rd[8:10]+groundtemp3rd[19:])/3
    
                        autumn['4']= sum(groundtemp3rd[10:13])/3
                        
            return winter,spring,autumn,summer, # Return the seasons in this order
            
        seasons = orderbyseason(groundtemp1st,groundtemp2nd,groundtemp3rd)
       
        #Create the points for the season temperature curves
    
        ptsList = []
    
        crvColors = []
        
        colors = System.Drawing.Color.MediumBlue,System.Drawing.Color.SeaGreen,System.Drawing.Color.Yellow,System.Drawing.Color.Red #In order of summer,spring,autumn,winter
        
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
        
    def drawLegend(colors):
        
        dataMeshes = []
        # A function which draws the legend box in the Rhino Viewport
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
            
            # Color the mesh faces
            barMesh.VertexColors.CreateMonotoneMesh(color)
    
            dataMeshes.append(barMesh)
        
            return dataMeshes
            
        def draw_Legendboxlabel(x,z,text):
            
            legPlane = rc.Geometry.Plane(rc.Geometry.Point3d(x,0,z), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(1,0,1))

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
        
    divisionPts,divisionPts1,groundtempCtext,graphAxes = drawAxes(groundtemp1st,groundtemp2nd,groundtemp3rd)

    graphtext = drawText(divisionPts,divisionPts1,groundtempCtext)
    
    profileCrvs,crvColors,colors = drawprofileCrvs_Season(groundtemp1st,groundtemp2nd,groundtemp3rd)
    
    Legend = drawLegend(colors)

elif visualisedata_Month == True:

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
    
        groundtempall = groundtemp1st[8:] + groundtemp2nd[8:] + groundtemp3rd[8:] # Adding the ground temp data from each of the ground temp depths (1st,2nd and 3rd) in the epw file
    
        groundtempCtext = [] # The text (numbers) that will be shown as labels on the horzontial axis 
    
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
    
        legPlane = rc.Geometry.Plane(rc.Geometry.Point3d(-3,0,-5), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(0,0,1))

        legPt = rc.Geometry.Point3d(-2,-1,0)
    
        textSrfs3 = lb_visualization.text2srf(['Depth'], [legPt],'Verdana', 0.3, False, legPlane)

        for txt in textSrfs3:
            graphtext.extend(txt)
        
        # Create title on horizontial axis
    
        legPlane1 = rc.Geometry.Plane(rc.Geometry.Point3d(3.5,0,1.5), rc.Geometry.Vector3d(1,0,0),  rc.Geometry.Vector3d(1,0,1))

        legPt1 = rc.Geometry.Point3d(0,0,0)
    
        textSrfs4 = lb_visualization.text2srf(['Ground Temperature'], [legPt1],'Verdana', 0.3, False, legPlane1)

        for txt in textSrfs4:
            graphtext.extend(txt)
        return graphtext

    def drawprofileCrvs_Month(groundtemp1st,groundtemp2nd,groundtemp3rd):
    
        #Find the annual average temperature, which will be the temperature at very low depths.
        annualAvg = sum(groundtemp1st[8:])/12 ## [8:] denotes from 8th row in list onwards as in groundtemp1st,groundtemp2nd etc data starts in 8th row

        #Find the maximum deviation around this for get a scale for the horizontal axis.
        allValues = []
        allValues.extend(groundtemp1st[8:])
        allValues.extend(groundtemp2nd[8:])
        allValues.extend(groundtemp3rd[8:])
    
        allValues.sort()
        maxDiff = max(allValues) - annualAvg
        minDiff = annualAvg - min(allValues)

        if maxDiff > minDiff: diffFactor = maxDiff/4
        else: diffFactor = minDiff/4
        
        lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar_, False)
        print type(legendPar_)
        colors = lb_visualization.gradientColor(range(12), 0, 11, customColors)

        #Create the points for the temperature profile curves
        ptsList = []
        
        crvColors = []
        for count in range(12):
            pt1 = rc.Geometry.Point3d(rectangleCenterPt.X + (groundtemp1st[count+8]- annualAvg)/diffFactor, rectangleCenterPt.Y, rectangleCenterPt.Z-0.5)
            pt2 = rc.Geometry.Point3d(rectangleCenterPt.X + (groundtemp2nd[count+8]- annualAvg)/diffFactor, rectangleCenterPt.Y, rectangleCenterPt.Z-2)
            pt3 = rc.Geometry.Point3d(rectangleCenterPt.X + (groundtemp3rd[count+8]- annualAvg)/diffFactor, rectangleCenterPt.Y, rectangleCenterPt.Z-4)
            pt4 = rc.Geometry.Point3d(rectangleCenterPt.X, rectangleCenterPt.Y, rectangleCenterPt.Z-9)
            ptsList.append([pt1, pt2, pt3, pt4])
            
            crvColors.append(colors[count])
            
        #Create the ground profile curves.
        profileCrvs = []
        for list in ptsList:
            monthCrv = rc.Geometry.Curve.CreateInterpolatedCurve(list, 3)
            profileCrvs.append(monthCrv)
            
        return profileCrvs,crvColors
            
    divisionPts,divisionPts1,groundtempCtext,graphAxes = drawAxes(groundtemp1st,groundtemp2nd,groundtemp3rd)

    graphtext = drawText(divisionPts,divisionPts1,groundtempCtext)
    
    profileCrvs,crvColors = drawprofileCrvs_Month(groundtemp1st,groundtemp2nd,groundtemp3rd)
    
else: pass
