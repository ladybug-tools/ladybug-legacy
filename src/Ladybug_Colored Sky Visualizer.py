# Visualize a Perez sky
# By Trygve Wastvedt and Chris Mackey
# Trygve.Wastvedt@gmail.com and Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to visualize a Perez sky as a colored mesh in the Rhino scene using the weather file location, a time and date, and an estimate of turbidity (or amount of particulates in the atmosphere.

-
Provided by Ladybug 0.0.58
    
    Args:
        north_: Input a vector to be used as a true North direction for the sky dome or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        --------------- : ...
        _hour_: A number between 1 and 24 (or a list of numbers) that represent hour(s) of the day to position sun on the sky dome.  The default is 12, which signifies 12:00 PM.
        _day_: A number between 1 and 31 (or a list of numbers) that represent days(s) of the month to position sun on the sky dome.  The default is 21, which signifies the 21st of the month (when solstices and equinoxes occur).
        _month_: A number between 1 and 12 (or a list of numbers) that represent months(s) of the year to position sun on the sky dome.  The default is 12, which signifies December.
        turbidity_: A number between 2 and 15 that represents the level of particulate matter in the atmosphere of the sky.  A rural location might have a low turbidity of 2 while a place like Beijing might have a turbidity as high as 10 or 12.  The default is set to 3 for a relatively clear sky without much pollution.
        --------------- : ...
        resolution_: An optional input for the resolution of the generated mesh.  A higher resolution will produce a less-splotchy image but will take longer to calculate.  The default is set to 10 for a realtively quick calculation.
        scale_: An optional input to scale the dome mesh.  The default is set to 1.
        centerPt_: An optional point to move the center of the sky dome mesh.  The default is set to the Rhino origin.
        domeOrRect_: Set to "True" to generate a sky color mesh that is in the shape of a dome and set to "False" to generate a sky as a flat rectangular mesh.  The default is set to "True" to generate the sky as a dome.
    Returns:
        readMe!: ...
        coloredMesh: A colored mesh of the sky.
        meshLabels: Time and date lables for the sky mesh.
        skyColorRGB: The RGB colors that correspond to the vertices of the mesh above.
        skyColorXYZ: The XYZ colors that correspond to the vertices of the mesh above.
"""

ghenv.Component.Name = "Ladybug_Colored Sky Visualizer"
ghenv.Component.NickName = 'skyVizualizer'
ghenv.Component.Message = 'VER 0.0.58\nAUG_20_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import math
import Rhino as rc
import scriptcontext as sc
import System
import Grasshopper.Kernel as gh
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def checkTheInputs():
    #Set the Julian year to be used for the analysis.
    year = 2014
    
    #Read out the location data.
    latitude, longitude, timeZone, elevation = readLocation(_location)
    
    #Check if there is a day, month, and hour connected and, if not, set defaults to the winter solstice.
    checkData1 = True
    hours = []
    if _hour_ != []:
        for hour in _hour_:
            if hour <= 24 and hour > 0:
                hours.append(hour)
            else:
                checkData1 = False
        if checkData1 == False:
            warning = 'Hours must be between 0 and 24.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        hours.append(12)
    
    checkData2 = True
    days = []
    if _day_ != []:
        for day in _day_:
            if day <= 31 and day > 0:
                days.append(day)
            else:
                checkData2 = False
        if checkData2 == False:
            warning = 'Days must be between 0 and 31.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        days.append(21)
    
    checkData3 = True
    months = []
    if _month_ != []:
        for month in _month_:
            if month <= 12 and month > 0:
                months.append(month)
            else:
                checkData3 = False
        if checkData3 == False:
            warning = 'Months must be between 0 and 12.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        months.append(12)
    
    #Caclculate the day of the year for the inputs.
    doy = []
    daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if checkData1 == True and checkData2 == True and checkData3 == True:
        for month in months:
            for day in days:
                doy.append(sum(daysPerMonth[:month-1]) + day)
    
    #Check the turbidity.
    checkData4 = True
    if turbidity_ != None:
        if turbidity_ <= 15 and turbidity_ > 2:
            turbidity = turbidity_
        else:
            checkData4 = False
        if checkData4 == False:
            warning = 'Tubidity must be between 2 and 15.  Otherwise, you are either in outer sapce or on in the atmosphere of Venus.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        turbidity = 3
    
    #Check the scale input and set the default to "True" if nothing is connected.
    checkData5 = True
    if scale_ != None:
        if scale_ > 0:
            scale = scale_*19
        else:
            checkData5 = False
        if checkData5 == False:
            warning = 'Scale must be greater than 0.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else: scale = 19
    
    #Check the resolution input and set the default to 10 if nothing is connected.
    checkData6 = True
    if resolution_ != None:
        if resolution_ > 2:
            resolution = resolution_
        else:
            checkData6 = False
        if checkData6 == False:
            warning = 'Resolution must be greater than 2.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else: resolution = 10
    
    #Check the domeOrRect input and set the default to 1 if nothing is connected.
    if domeOrRect_ != None: domeOrRect = domeOrRect_
    else: domeOrRect = True
    
    #Check all of the inputs and return a single value that says whether everything is ok.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True:
        checkData = True
    else: checkData = False
    
    
    return checkData, domeOrRect, doy, days, months, year, hours, timeZone, latitude, longitude, turbidity, scale, resolution

def readLocation(location):
    locationStr = location.split('\n')
    newLocStr = ""
    #clean the idf file
    for line in locationStr:
        if '!' in line:
            line = line.split('!')[0]
            newLocStr  = newLocStr + line.replace(" ", "")
        else:
            newLocStr  = newLocStr + line
    
    newLocStr = newLocStr.replace(';', "")
    
    site, locationName, latitude, longitude, timeZone, elevation = newLocStr.split(',')
    
    return float(latitude), float(longitude), float(timeZone), float(elevation)

def createSkyDomeMesh(basePoint, resolution, scale):
    #Create a list of altitudes and azimuths based on the resolution.
    altitudes = []
    azimuths = []
    
    altitudes.append(0)
    for num in range(resolution):
        altitudes.append((90/resolution) + num*(90/resolution))
    
    azimuths.append(0)
    for num in range(4*resolution-1):
        azimuths.append((360/(4*resolution)) + num*(360/(4*resolution)))
    
    #Create the vertices of the mesh.
    meshPts = []
    startPt = rc.Geometry.Point3d(0, scale*10, 0)
    for alt in altitudes:
        for az in azimuths:
            newPt = rc.Geometry.Point3d(startPt)
            altRotate = rc.Geometry.Transform.Rotation(math.radians(alt), rc.Geometry.Vector3d.XAxis, rc.Geometry.Point3d.Origin)
            azRotate = rc.Geometry.Transform.Rotation(-math.radians(az), rc.Geometry.Vector3d.ZAxis, rc.Geometry.Point3d.Origin)
            newPt.Transform(altRotate)
            newPt.Transform(azRotate)
            meshPts.append(newPt)
    
    #Create the mesh.
    uncoloredMesh = rc.Geometry.Mesh()
    
    for point in meshPts:
        uncoloredMesh.Vertices.Add(point)
    
    numbersToWatch = range(0, len(meshPts), (resolution*4))
    for count, point in enumerate(numbersToWatch):
        numbersToWatch[count] = point -1
    
    for pointCount in range(len(meshPts) - (resolution*4)):
        if pointCount not in numbersToWatch:
            uncoloredMesh.Faces.AddFace(pointCount, pointCount+1, pointCount+(resolution*4)+1, pointCount+(resolution*4))
        else:
            uncoloredMesh.Faces.AddFace(pointCount, pointCount-(resolution*4)+1, pointCount+1, pointCount+(resolution*4))
    
    #Move the mesh from the origin to the base point location
    startPtTransform = rc.Geometry.Transform.Translation(basePoint.X, basePoint.Y, basePoint.Z)
    uncoloredMesh.Transform(startPtTransform)
    
    #Color the mesh with monotone colors.
    uncoloredMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Gray)
    
    return uncoloredMesh

def createRectangularMesh(basePoint, resolution, scale):
    #Create a list of altitudes and azimuths based on the resolution.
    altitudes = []
    azimuths = []
    
    altitudes.append(0)
    for num in range(resolution):
        altitudes.append((90/resolution) + num*(90/resolution))
    
    azimuths.append(0)
    for num in range(4*resolution-1):
        azimuths.append((360/(4*resolution)) + num*(360/(4*resolution)))
    
    #Create the vertices.
    meshPts = []
    startPt = rc.Geometry.Point3d(scale*20, scale*-5, 0)
    for alt in altitudes:
        for az in azimuths:
            newPt = rc.Geometry.Point3d(startPt)
            altTrans = rc.Geometry.Transform.Translation(0, (alt/9)*scale, 0)
            azTrans = rc.Geometry.Transform.Translation(-(az/9)*scale, 0, 0)
            newPt.Transform(altTrans)
            newPt.Transform(azTrans)
            meshPts.append(newPt)
    
    #Create the mesh.
    uncoloredMesh = rc.Geometry.Mesh()
    
    for point in meshPts:
        uncoloredMesh.Vertices.Add(point)
    
    numbersToWatch = range(0, len(meshPts), (resolution*4))
    for count, point in enumerate(numbersToWatch):
        numbersToWatch[count] = point -1
    
    for pointCount in range(len(meshPts) - (resolution*4)):
        if pointCount not in numbersToWatch:
            uncoloredMesh.Faces.AddFace(pointCount, pointCount+1, pointCount+(resolution*4)+1, pointCount+(resolution*4))
        else: pass
    
    #Move the mesh from the origin to the base point location
    startPtTransform = rc.Geometry.Transform.Translation(basePoint.X, basePoint.Y, basePoint.Z)
    uncoloredMesh.Transform(startPtTransform)
    
    #Color the mesh with monotone colors.
    uncoloredMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Gray)
    
    return uncoloredMesh


def main(domeOrRect, doy, days, months, year, hours, timeZone, latitude, longitude, turbidity, scale, resolution):
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
        lb_skyColor = sc.sticky["ladybug_SkyColor"]()
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        #Create lists to be output.
        skyColors = []
        skyColorsXYZ = []
        skyMeshes = []
        skyTextLabels = []
        
        #Generate a set of base points for the input hours.
        basePoints = []
        for dayCount, day in enumerate(doy):
            for hourCount, hour in enumerate(hours):
                if domeOrRect == True:
                    basePoints.append(rc.Geometry.Point3d(hourCount*25*scale, dayCount*25*scale, 0))
                else:
                    basePoints.append(rc.Geometry.Point3d(hourCount*45*scale, dayCount*12*scale, 0))
        
        #Generate meshes for the base points.
        uncoloredSkyMeshes = []
        for point in basePoints:
            if domeOrRect == True:
                uncoloredSkyMeshes.append(createSkyDomeMesh(point, resolution, scale))
            else:
                uncoloredSkyMeshes.append(createRectangularMesh(point, resolution, scale))
        
        #If the user has specified a north angle and the visualization is set to dome, rotate the dome.
        if domeOrRect == True and north_ != None:
            northAngle, northVector = lb_preparation.angle2north(north_)
            for domeCount, dome in enumerate(uncoloredSkyMeshes):
                northRotation = rc.Geometry.Transform.Rotation(northAngle, rc.Geometry.Vector3d.ZAxis, basePoints[domeCount])
                dome.Transform(northRotation)
        
        #Create a function to split up lists into chunks based on the resolution.
        def chunks(l, n):
            if n < 1:
                n = 1
            return [l[i:i + n] for i in range(0, len(l), n)]
        
        #Create the skies.
        for dayCount, day in enumerate(doy):
            for hourCount, hour in enumerate(hours):
                #Get the color values for the sky and create the mesh.
                sky = lb_skyColor.createSky(day, year, hour, timeZone, latitude, longitude, turbidity)
                fullSkyRGB, fullSkyXYZ = lb_skyColor.calcFullSky(int(resolution))
                fullSkyXYZ = chunks(fullSkyXYZ, resolution+1)
                fullSkyRGB = chunks(fullSkyRGB, resolution+1)
                finalFullSkyRGB = []
                finalFullSkyXYZ = []
                for count, item in enumerate(fullSkyRGB[0]):
                    for list in fullSkyRGB:
                        finalFullSkyRGB.append(list[count])
                    for list in fullSkyXYZ:
                        finalFullSkyXYZ.append(list[count])
                skyColors.append(finalFullSkyRGB)
                skyColorsXYZ.append(finalFullSkyXYZ)
                skyMesh = uncoloredSkyMeshes[dayCount*hourCount+hourCount]
                for vertxCount, color in enumerate(finalFullSkyRGB):
                    skyMesh.VertexColors[vertxCount] = color
                skyMeshes.append(skyMesh)
                
                #Create the text labels for the sky.
                legendFont = "Verdana"
                lb_visualization.calculateBB([skyMesh], True)
                dateText = str(lb_preparation.hour2Date(day*24+hour))
                textSrf = lb_visualization.text2srf([dateText], [lb_visualization.BoundingBoxPar[5]], legendFont, scale/2.1)
                skyTextLabels.extend(textSrf)
                
                #Print the information for each sky
                lb_skyColor.info()
        
        #If the user has specified a base point, move all of the geometry.
        if centerPt_ != None:
            transformMtx = rc.Geometry.Transform.Translation(centerPt_.X, centerPt_.Y, centerPt_.Z)
            for geo in skyMeshes: geo.Transform(transformMtx)
            for list in skyTextLabels:
                for geo in list: geo.Transform(transformMtx)
        
        
        return skyMeshes, skyColors, skyColorsXYZ, skyTextLabels
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return [], [[]], [[]], [[]]


checkData = False
if _location:
    checkData, domeOrRect, doy, day, month, year, hour, timeZone, latitude,\
    longitude, turbidity, scale, resolution = checkTheInputs()

if checkData == True:
    results = main(domeOrRect, doy, day, month, year, hour, timeZone, latitude, longitude, turbidity, scale, resolution)
    
    if results!=-1:
        coloredMesh, colorsRGB, colorXYZ, skyTextLabels = results
        
        #Unpack the lists of colors and text surfaces.
        skyColorRGB = DataTree[Object]()
        for count, list in enumerate(colorsRGB):
            for item in list:
                skyColorRGB.Add(item, GH_Path(count))
        
        skyColorXYZ = DataTree[Object]()
        for count, list in enumerate(colorXYZ):
            for item in list:
                skyColorXYZ.Add(item, GH_Path(count))
        
        meshLabels = DataTree[Object]()
        for count, list in enumerate(skyTextLabels):
            for item in list:
                meshLabels.Add(item, GH_Path(count))