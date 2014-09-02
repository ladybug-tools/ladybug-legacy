# wind velocity profile
# By Djordje Spasic
# djordjedspasic@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to create wind velocity profile and calculate its speed values using power law function.
-
Provided by Ladybug 0.0.57
    
    input:

        _windSpeed: Supply the wind speed data (in meters/second). You can supply one of the following data:
            - 'windSpeed' output of the 'Ladybug_Import epw' component,
            - .epw File,
            - list of wind speed values (annual, monthly, daily)
            - a single wind speed value (annual mean, monthly mean, daily mean, per specific hour)
            - wind speed(s) .txt File
        terrain_: Terrain types:
            0 = City: large city centres, 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = Urban: suburbs, wooded areas.
            2 = Country: open, with scattered objects generally less than 10m high.
            3 = Water: Flat, unobstructed areas exposed to wind flowing over a large water body (no more than 500m inland).
        location_: ...
        origin_: Origin of the wind velocity profile
        scale_: Scale the overall wind velocity profile
        addArrows_: Add arrows to wind velocity profile curve
        bakeIt_: Set to "True" to bake the wind velocity profile into the Rhino scene.
    output:
        readMe!: ...
        profileHeight: Wind height with 0.5 meters vertical increment
        profileWindSpeed: Wind speed at each 0.5 meters vertical increment
        plotGeometry: Geometry of the wind final velocity profile
        plotOrigin: Origin of the final wind velocity profile
"""


ghenv.Component.Name = "Ladybug_Wind Velocity Profile"
ghenv.Component.NickName = 'windVelocityProfile'
ghenv.Component.Message = 'VER 0.0.57\nAUG_27_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Grasshopper.Kernel as gh
import scriptcontext as sc
import System
import Rhino
import time
import math

# Currently not necessary, as a Ladybug's method "text2crv" has been copied in here, and modified a bit.
# may or may not be used in future: https://github.com/mostaphaRoudsari/ladybug/pull/80
#lb_preparation = sc.sticky["ladybug_Preparation"]()


class windBProfile:

    def __init__(self, terrain, location, addArrows):

        # Default terrain value
        if not terrain:
            self.terrain = "city"
            self.gradientHeight = 200
            self.gradientHeightDiv = 401
        else:
            self.terrain = terrain

        # location values
        if location:
            try:
                self.location = str(location)
            except:
                self.location = str(location[:-1])
        else:
            pass

        # adding arrows to velocity profile polyline
        if not addArrows:
            self.addArrows = False
        else:
            if isinstance(addArrows, System.Boolean):
                self.addArrows = addArrows
            elif addArrows == 0:
                self.addArrows = False
            elif addArrows == 1:
                self.addArrows = True
            else:
                print "Please provide either 'True' or 'False' for 'addArrows'"

    def checkWindData(self, windSpeed, location):
        # checking for valid wind data from different sources
        if not location:
            self.location = "Location_1"
        else:
            self.location = location
        # 1) windSpeeds as list input
        try:
            # len(list) > 1
            if len(windSpeed) > 1:
                # from 'windSpeed' output of the 'Ladybug_Import epw' component
                if (windSpeed[0] == "key:location/dataType/units/frequency/startsAt/endsAt") and (windSpeed[2] == "Wind Speed"):
                    if not location: # overwrite the initial line 7
                        self.location = windSpeed[1]
                    windData = windSpeed[7:]
                    sum = 0
                    values = 0
                    for item in windData:
                        sum = sum + float(item)
                        values = values + 1
                    averageWindSpeed = sum/values
                    validWindData = True
                    printMsg = "Wind data successfully imported from .epw file"
                    return validWindData, averageWindSpeed, printMsg
                # from regular 'windSpeed' list
                else:
                    sum = 0
                    validValues = 0
                    for value in windSpeed:
                        if (len(str(value)) != 0) and (value != None):  # check for invalid values 1
                            try:  # check for invalid values 2
                                sum = sum + float(value)
                                validValues = validValues + 1
                            except:
                                continue
                    averageWindSpeed = sum/validValues
                    validWindData = True
                    printMsg = "Wind data successfully imported from .epw file"
                    return validWindData, averageWindSpeed, printMsg

            # single element in list (len(list) == 1)
            elif len(windSpeed) == 1:
                try:
                    averageWindSpeed = float(windSpeed[0])
                    validWindData = True
                    printMsg = "Wind data successfully imported from .epw file"
                    return validWindData, averageWindSpeed, printMsg
                except:
                    pass
        except:
            pass

        # 2) files inputted
        try: 
            openFile = open(windSpeed[0],"r")
            headline = openFile.readline()
            splittedHeadline = headline.split(",")
            # epwFile
            weatherDataSources = ["CTZ2","CWEC","CIBSE","CityUHK","CSWD","CTYW","ETMY","IGDG","IMGW","IMS","INETI","ISHRAE","ITMY","IWEC","KISR","NIWA","RMY","SWEC","SWERA","TMY","TMY2","TMY3"]
            for wSource in weatherDataSources:
                if (splittedHeadline[0] == "LOCATION") and (wSource in splittedHeadline[4]):
                    if not location:
                        self.location = splittedHeadline[1]+ splittedHeadline[2] + splittedHeadline[3]
                    wholeEpw = openFile.readlines()
                    noPrefaceEpw = wholeEpw[8:]
                    removeComma = []
                    for item in noPrefaceEpw:
                        removeComma.append(item.split(","))
                    sum = 0
                    values = 0
                    for item2 in removeComma:
                        sum = sum + float(item2[21])
                        values = values + 1
                    validWindData = True
                    averageWindSpeed = sum/values
                    printMsg = "Wind data successfully imported from .epw file"
                    return validWindData, averageWindSpeed, printMsg
            # windSpeed file
            else: 
                openFile = open(windSpeed[0],"r")
                lines = openFile.readlines()
                sum = 0
                validValues = 0
                for value in lines:
                    if (len(str(value)) != 0) and (value != None):  # check for invalid values 1
                        try:  # check for invalid values 2
                            sum = sum + float(value)
                            validValues = validValues + 1
                        except:
                            continue
                averageWindSpeed = sum/validValues
                validWindData = True
                printMsg = "Wind data successfully imported from .epw file"
                return validWindData, averageWindSpeed, printMsg
        except:
            validWindData = False
            printMsg = "Something is wrong with your input windSpeed data. Please provide a valid .Epw File or windSpeed data"
            return validWindData, None , printMsg

    def terrainType(self):
        # Atmospheric boundary layer parameters based on terrain type, and checking terrain type
        if self.terrain == "city" or int(self.terrain) == 0:
            self.terrain = "city terrain"
            self.gradientHeightDiv = 921
            self.d = 460
            self.a = 0.33
            self.yValues = range(0,500,50)
            self.yAxisMaxRhinoHeight = 92
            self.nArrows = 10
            printMsgT = "Terrain data accepted"
            validTerrain = True
        elif self.terrain == "urban" or int(self.terrain) == 1:
            self.terrain = "urban terrain"
            self.gradientHeightDiv = 741
            self.d = 370
            self.a = 0.22
            self.yValues = range(0,400,50)
            self.yAxisMaxRhinoHeight = 72
            self.nArrows = 8
            printMsgT = "Terrain data accepted"
            validTerrain = True
        elif self.terrain == "country" or int(self.terrain) == 2:
            self.terrain = "country terrain"
            self.gradientHeightDiv = 541
            self.d = 270
            self.a = 0.14
            self.yValues = range(0,300,50)
            self.yAxisMaxRhinoHeight = 52
            self.nArrows = 6
            printMsgT = "Terrain data accepted"
            validTerrain = True
        elif self.terrain == "water" or int(self.terrain) == 3:
            self.terrain = "water terrain"
            self.gradientHeightDiv = 421
            self.d = 210
            self.a = 0.10
            self.yValues = range(0,250,50)
            self.yAxisMaxRhinoHeight = 42
            self.nArrows = 5
            printMsgT = "Terrain data accepted"
            validTerrain = True
        else:
            printMsgT = "Please choose one of three terrain types: 0=city, 1=urban, 2=country 3=water"
            validTerrain = False
            self.gradientHeight = None
            self.gradientHeightDiv = None
        return validTerrain, self.d, self.gradientHeightDiv, self.yValues, self.yAxisMaxRhinoHeight, self.nArrows, printMsgT

    def genHeights(self, stop, values):
        # Height Z coordinates
        return [round( stop/(values-1)*i,2) for i in range(values)]

    def genwindSpeeds(self, heightL, averageWindSpeed):
        # Wind speed at each height - power law function
        return [((height / self.d) ** self.a) * (averageWindSpeed * (270 / 10) ** 0.14) for height in heightL]

    def text2crv(self, text, textPt, scale):
    # Thanks to Giulio Piacentino for his version of text to curve (taken from Mostapha's Ladybug_Ladybug component)

        if (str(text[-1]) == "450") or (str(text[-1]) == "350") or (str(text[-1]) == "250") or (str(text[-1]) == "200") or (str(text[-1]) == "Height (m)"):
            just = System.Enum.ToObject(Rhino.Geometry.TextJustification, 4)
        elif (str(text[-1]) == "Wind speed (m/s)"):
            just = System.Enum.ToObject(Rhino.Geometry.TextJustification, 2)
        else:
            just = System.Enum.ToObject(Rhino.Geometry.TextJustification, 262144)
        textCrvs = []
        textHeight = scale*1.5   # 1.5 scalling text curves
        for i,pt in enumerate(textPt):
            plane = Rhino.Geometry.Plane(pt, Rhino.Geometry.Vector3d(0,0,1))
            preText = Rhino.RhinoDoc.ActiveDoc.Objects.AddText(str(text[i]), plane, textHeight, "Verdana", True, False, just)
            
            postText = Rhino.RhinoDoc.ActiveDoc.Objects.Find(preText)
            TG = postText.Geometry
            crv = TG.Explode()
            for c in crv:
                textCrvs.append(c)
            Rhino.RhinoDoc.ActiveDoc.Objects.Delete(postText, True) # find and delete the text
        return textCrvs


    def createGeometry(self, H, S, yValues, yAxisMaxRhinoHeight, addArrows, nArrows, origin, scale, bake):
        # generate plot geometry, and prepare for baking
        if not origin:
            originOffset = Rhino.Geometry.Point3d(0,-70,0)
            origin = Rhino.Geometry.Point3d(-15,-70,0)
        else:
            originOffset = Rhino.Geometry.Point3d(origin.X+15, origin.Y, origin.Z)  # represents 0,0 point for y and x velocity profile axis

        if not scale:
            scale = 1

        maxSpeed = S[-1]
        condition = math.ceil(maxSpeed)-maxSpeed
        if condition <= 0.30:
            xAxisDiv = math.ceil(maxSpeed) + 1
        else:
            xAxisDiv = math.ceil(maxSpeed)
   
        yAxis = Rhino.Geometry.Line(originOffset, Rhino.Geometry.Point3d(originOffset.X, originOffset.Y+yAxisMaxRhinoHeight, originOffset.Z))
        xAxis = Rhino.Geometry.Line(originOffset, Rhino.Geometry.Point3d(originOffset.X+52, originOffset.Y, originOffset.Z))

        yAxisNotchLines = []
        yValuesOrigin = [Rhino.Geometry.Point3d(originOffset.X-1, originOffset.Y, originOffset.Z)]
        for i in range(1,len(yValues)):
            yVOrig = Rhino.Geometry.Point3d(originOffset.X-1, originOffset.Y+i*10, originOffset.Z)
            yValuesOrigin.append(yVOrig)
            yLn = Rhino.Geometry.Line(Rhino.Geometry.Point3d(originOffset.X, originOffset.Y+i*10, originOffset.Z), Rhino.Geometry.Point3d(originOffset.X+1, originOffset.Y+i*10, originOffset.Z))
            yAxisNotchLines.append(yLn)

        xAxisNotchLines = []
        xValues = [0]
        xValuesOrigin = [Rhino.Geometry.Point3d(originOffset.X, originOffset.Y-1, originOffset.Z)]
        for i in range(1,int(xAxisDiv)+1):
            xValues.append(i)
            xVOrig = Rhino.Geometry.Point3d(originOffset.X+(50/xAxisDiv)*i, originOffset.Y-1, originOffset.Z)
            xValuesOrigin.append(xVOrig)
            xLn = Rhino.Geometry.Line(Rhino.Geometry.Point3d(originOffset.X+(50/xAxisDiv)*i, originOffset.Y, originOffset.Z), Rhino.Geometry.Point3d(originOffset.X+(50/xAxisDiv)*i, originOffset.Y+1, originOffset.Z))
            xAxisNotchLines.append(xLn)
        # "Height (m)" and "Wind speed (m/s)" text origin points
        xAxisLabelOrigin = Rhino.Geometry.Point3d(originOffset.X+25, originOffset.Y-7, originOffset.Z)
        yAxisLabelOrigin = Rhino.Geometry.Point3d(originOffset.X-7, originOffset.Y+(yAxisMaxRhinoHeight/2), originOffset.Z)

        # X,Y axes arrow heads
        mesh1 = Rhino.Geometry.Mesh()
        mesh2 = Rhino.Geometry.Mesh()
        mesh1.Vertices.Add(Rhino.Geometry.Point3d(originOffset.X-1, originOffset.Y+yAxisMaxRhinoHeight, originOffset.Z))
        mesh1.Vertices.Add(Rhino.Geometry.Point3d(originOffset.X+1, originOffset.Y+yAxisMaxRhinoHeight, originOffset.Z))
        mesh1.Vertices.Add(Rhino.Geometry.Point3d(originOffset.X, originOffset.Y+yAxisMaxRhinoHeight+1.74, originOffset.Z))
        mesh2.Vertices.Add(Rhino.Geometry.Point3d(originOffset.X+52, originOffset.Y+1, originOffset.Z))
        mesh2.Vertices.Add(Rhino.Geometry.Point3d(originOffset.X+52, originOffset.Y-1, originOffset.Z))
        mesh2.Vertices.Add(Rhino.Geometry.Point3d(originOffset.X+52+1.74, originOffset.Y, originOffset.Z))
        mesh1.Faces.AddFace(0,1,2)
        mesh2.Faces.AddFace(0,1,2)
        arrayColor = System.Array[System.Drawing.Color]([System.Drawing.Color.Black, System.Drawing.Color.Black, System.Drawing.Color.Black])
        mesh1.VertexColors.SetColors(arrayColor)
        mesh2.VertexColors.SetColors(arrayColor)
        
        # the very velocity profile points
        boundaryCrvPts = []
        for i,pt in enumerate(H):
            boundaryCrvPts.append(Rhino.Geometry.Point3d(originOffset.X+((50*S[i])/xAxisDiv), originOffset.Y+(H[i]/5), originOffset.Z))
        
        # title origin point
        titleLabelOrigin = Rhino.Geometry.Point3d(origin.X+15, origin.Y-12, origin.Z)
        titleLabelText = "Wind velocity profile, " + str(self.location) + " - " + str(self.terrain)
        
        if addArrows:
            boundaryPolyline = Rhino.Geometry.Polyline(boundaryCrvPts)
            boundaryCrv = boundaryPolyline.ToNurbsCurve()
            arrowLines = []
            arrowMeshes = []
            for i in range(1,nArrows):
                arrowStartPt = Rhino.Geometry.Point3d(originOffset.X, originOffset.Y+5*((2*i)-1), originOffset.Z)
                plane = Rhino.Geometry.Plane(arrowStartPt, Rhino.Geometry.Vector3d(0,1,0))
                ie = Rhino.Geometry.Intersect.Intersection.CurvePlane(boundaryCrv, plane, 0.01)
                meshTipPt = ie[0].PointA
                mestPt1 = Rhino.Geometry.Point3d(meshTipPt.X-1.74, meshTipPt.Y+1, meshTipPt.Z)
                mestPt2 = Rhino.Geometry.Point3d(meshTipPt.X-1.74, meshTipPt.Y-1, meshTipPt.Z)
                mesh = Rhino.Geometry.Mesh()
                mesh.Vertices.Add(meshTipPt)
                mesh.Vertices.Add(mestPt1)
                mesh.Vertices.Add(mestPt2)
                mesh.Faces.AddFace(0,1,2)
                arrayColor = System.Array[System.Drawing.Color]([System.Drawing.Color.Blue, System.Drawing.Color.Blue, System.Drawing.Color.Blue])
                mesh.VertexColors.SetColors(arrayColor)
                arrowMeshes.append(mesh)
                arrowLine = Rhino.Geometry.Line(arrowStartPt, Rhino.Geometry.Point3d(meshTipPt.X-1.74, meshTipPt.Y, meshTipPt.Z))
                arrowLines.append(arrowLine)
                
            returnList = [xAxisNotchLines, yAxisNotchLines, xValuesOrigin, yValuesOrigin, xAxisLabelOrigin, yAxisLabelOrigin, titleLabelOrigin, [xAxis, yAxis, mesh1, mesh2], boundaryCrvPts, arrowLines, arrowMeshes]
        else:
            returnList = [xAxisNotchLines, yAxisNotchLines, xValuesOrigin, yValuesOrigin, xAxisLabelOrigin, yAxisLabelOrigin, titleLabelOrigin, [xAxis, yAxis, mesh1, mesh2], boundaryCrvPts]


        if scale != 1:
            plane = sc.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
            plane.Origin = originOffset
            tmScale = Rhino.Geometry.Transform.Scale(plane, scale,scale,scale)    #tm = Rhino.Geometry.Transform.Scale(plane, scale, scale, scale)
            for item in returnList:
                try:
                    for subitem in item:
                        subitem.Transform(tmScale)
                except:
                    item.Transform(tmScale)

        if bake:
            textHeight = scale*1.5    # 1.5 scalling text curves
            attr = Rhino.DocObjects.ObjectAttributes()
            attr.LayerIndex = 0   #attr.LayerIndex = layerIndex   - layerIndex dodati kao argument u ovoj funkciji
            justX = System.Enum.ToObject(Rhino.Geometry.TextJustification, 262144)
            justY = System.Enum.ToObject(Rhino.Geometry.TextJustification, 4)
            justXlabel = System.Enum.ToObject(Rhino.Geometry.TextJustification, 2)
            # add X,Y notch label text
            idsTextX = []
            idsTextY = []
            for i,pt in enumerate(xValuesOrigin):
                plane = Rhino.Geometry.Plane(pt, Rhino.Geometry.Vector3d(0,0,1))
                idTextX = Rhino.RhinoDoc.ActiveDoc.Objects.AddText(str(xValues[i]), plane, textHeight, "Verdana", True, False, justX, attr)
                idsTextX.append(idTextX)
            for k,pt in enumerate(yValuesOrigin):
                plane = Rhino.Geometry.Plane(pt, Rhino.Geometry.Vector3d(0,0,1))
                idTextY = Rhino.RhinoDoc.ActiveDoc.Objects.AddText(str(yValues[k]), plane, textHeight, "Verdana", True, False, justY, attr)
                idsTextY.append(idTextY)
            # add X,Y label text
            plane = Rhino.Geometry.Plane(xAxisLabelOrigin, Rhino.Geometry.Vector3d(0,0,1))
            idTextXLabel = Rhino.RhinoDoc.ActiveDoc.Objects.AddText("Wind speed (m/s)", plane, textHeight, "Verdana", True, False, justXlabel, attr)
            plane = Rhino.Geometry.Plane(yAxisLabelOrigin, Rhino.Geometry.Vector3d(0,0,1))
            idTextYLabel = Rhino.RhinoDoc.ActiveDoc.Objects.AddText("Height (m)", plane, textHeight, "Verdana", True, False, justY, attr)
            # add title label text
            plane = Rhino.Geometry.Plane(titleLabelOrigin, Rhino.Geometry.Vector3d(0,0,1))
            idTitleLabel = Rhino.RhinoDoc.ActiveDoc.Objects.AddText(titleLabelText, plane, textHeight*1.3, "Verdana", True, False, justX, attr)  # scale*1.3 - enlarge font size for titleLabel
            # add mesh (arrow heads)
            idMesh1 = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh1,attr)
            idMesh2 = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh2,attr)
            # add axis and notch lines
            notchLines = xAxisNotchLines + yAxisNotchLines + [xAxis] + [yAxis]
            lineIds = []
            for line in notchLines:
                lineId = Rhino.RhinoDoc.ActiveDoc.Objects.AddLine(line,attr)
                lineIds.append(lineId)
            # velocity profile curve (polyline):
            attr = Rhino.DocObjects.ObjectAttributes()
            attr.LayerIndex = 0
            attr.ObjectColor = System.Drawing.Color.Blue
            attr.PlotColor = System.Drawing.Color.Blue
            attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
            attr.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
            polylineId = Rhino.RhinoDoc.ActiveDoc.Objects.AddPolyline(boundaryCrvPts, attr)
            
            if addArrows:
                # arrows lines and meshes:
                arrowLnIds = []
                arrowMeshIds = []
                for line in arrowLines:
                    lineId = Rhino.RhinoDoc.ActiveDoc.Objects.AddLine(line, attr)
                    arrowLnIds.append(lineId)
                for mesh in arrowMeshes:
                    meshId = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh, attr)
                    arrowMeshIds.append(meshId)

            # group baked geometry
            if addArrows:
                ids = idsTextX + idsTextY + [idTextXLabel, idTextYLabel, idMesh1, idMesh2] + lineIds + [polylineId] + arrowLnIds + arrowMeshIds + [idTitleLabel]
            else:
                ids = idsTextX + idsTextY + [idTextXLabel, idTextYLabel, idMesh1, idMesh2] + lineIds + [polylineId] + [idTitleLabel]
            groupName = "windProfile_" + self.location + "_" + str(time.time())
            Rhino.RhinoDoc.ActiveDoc.Groups.Add(groupName)
            groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Find(groupName, True)
            Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, ids)


        if addArrows:
            return origin, xAxisNotchLines + yAxisNotchLines + [xAxis, yAxis, mesh1, mesh2] + arrowLines + arrowMeshes +\
                   self.text2crv(xValues, xValuesOrigin, scale) + self.text2crv(yValues, yValuesOrigin, scale) +\
                   self.text2crv(["Wind speed (m/s)"], [xAxisLabelOrigin], scale) + self.text2crv(["Height (m)"], [yAxisLabelOrigin], scale)+\
                   self.text2crv([titleLabelText], [titleLabelOrigin], scale*1.3)+\
                   [Rhino.Geometry.Polyline(boundaryCrvPts)]  # scale*1.3 - enlarge font size for titleLabel

        return origin, xAxisNotchLines + yAxisNotchLines + [xAxis, yAxis, mesh1, mesh2] +\
               self.text2crv(xValues, xValuesOrigin, scale) + self.text2crv(yValues, yValuesOrigin, scale) +\
               self.text2crv(["Wind speed (m/s)"], [xAxisLabelOrigin], scale) + self.text2crv(["Height (m)"], [yAxisLabelOrigin], scale)+\
               self.text2crv([titleLabelText], [titleLabelOrigin], scale*1.3)+\
               [Rhino.Geometry.Polyline(boundaryCrvPts)]  # scale*1.3 - enlarge font size for titleLabel


myWindBProfile = windBProfile(terrain_, location_, addArrows_)
level = gh.GH_RuntimeMessageLevel.Warning
if (_windSpeed):
    validWindData, averageWindSpeed, printMsg = myWindBProfile.checkWindData(_windSpeed, location_)
    validTerrain, gradientHeight, gradientHeightDiv, yValues, yAxisMaxRhinoHeight, nArrows, printMsgT = myWindBProfile.terrainType()
    if validWindData and validTerrain:
        profileHeight = myWindBProfile.genHeights(gradientHeight, gradientHeightDiv)
        profileWindSpeed = myWindBProfile.genwindSpeeds(profileHeight, averageWindSpeed)
        plotOrigin, plotGeometry = myWindBProfile.createGeometry(profileHeight, profileWindSpeed, yValues, yAxisMaxRhinoHeight, addArrows_, nArrows, origin_, scale_, bakeIt_)
        print "Wind velocity profile successfully created."
        #print "Boundary wind profile created."
    elif (not validWindData) and (validTerrain):
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
    elif (validWindData) and (not validTerrain):
        print printMsgT
        ghenv.Component.AddRuntimeMessage(level, printMsgT)
    elif (not validWindData) and (not validTerrain):
        print "Please provide an .Epw File/windSpeed data and one of three Terrain Types: 0=city, 1=urban, 2=country 3=water"
        ghenv.Component.AddRuntimeMessage(level, "Please provide an .Epw File/windSpeed data and one of three Terrain Types: 0=city, 1=urban, 2=country 3=water")
else:
    print "Please provide an .Epw File or windSpeed data"
    ghenv.Component.AddRuntimeMessage(level, "Please provide an .Epw File or windSpeed data")