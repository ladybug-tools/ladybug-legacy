# Comfort Mannequin
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to color a mannequin based on their relation to a comfort temperature.
-
Provided by Ladybug 0.0.62
    
    Args:
        _ambientTemperature: The temperture around the mannequin, which can be either UTCI (outdoor comfort), Standard Effective Temperature (PMV comfort), or Operative Temperature (Adaptive Comfort).
        targetTemperature_: The target comfort temperature that the mannequin wants to be at.  The default is set to 20C
        comfortRange_: The number of degrees above and below the target temperture that the subject will still find comfortable.  The default is set to 3C, which is pretty common for many comfort metrics.
        -------------------------: ...
        bodyPosture_: An interger to set the posture of the comfort mannequin, which can have a large effect on the radiation striking the mannequin.  0 = Standing, 1 = Sitting, and 2 = Lying Down.  The default is set to 1 for sitting.
        rotationAngle_: An optional rotation angle in degrees.  Use this number to adjust the angle of the comfort mannequin in space.  The angle of the mannequin in relation to the sun can have a large effect on the amount of radiation that falls on it and thus largely affect the resulting mean radiant temperature.
        bodyLocation_: An optional point that sets the position of the comfort mannequin in space.  Use this to move the comfort mannequin around in relation to contextShading_ connected below. The default is set to the Rhino origin.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
    Returns:
        mannequinMesh: A colored mesh of a comfort mannequin showing the amount of radiation falling over the mannequin's body.
        legend: A legend that corresponds to the colors on the mannequinMesh and shows the relative W/m2.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the chart with the grasshopper "move" component.

"""
ghenv.Component.Name = "Ladybug_Comfort Mannequin"
ghenv.Component.NickName = 'ComfortMannequin'
ghenv.Component.Message = 'VER 0.0.62\nFEB_07_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Rhino as rc
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math


def checkTheInputs():
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            #if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
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
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        
        #Check the ambient Temperature.
        checkData1 = True
        if _ambientTemperature == None:
            print "Connect a value for _ambientTemperature."
            checkData1 = False
            ambTemp = None
        else: ambTemp = _ambientTemperature
        
        #Check the target temperture.
        if targetTemperature_ == None: targetTemp = 20
        else: targetTemp = targetTemperature_
        print "Target temperture is set to " + str(targetTemp)
        
        #Check the target temperture.
        if comfortRange_ == None: comfRange = 3
        else: comfRange = comfortRange_
        print "Comfort range is set to " + str(comfRange)
        
        #Check the bodyPosture_ input to be sure that it is a valid interger.
        if bodyPosture_ != 0 and bodyPosture_ != 1 and bodyPosture_ != 2 and bodyPosture_ != None:
            checkData2 = False
            warning = 'Input for bodyPosture_ is not an accepted input interger.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else: checkData2 = True
        if bodyPosture_ == None: bodyPosture = 1
        else: bodyPosture = bodyPosture_
        
        #Convert the rotation angle to radians or set a default of 0 if there is none.
        if rotationAngle_ != None:
            rotateAngle = rotationAngle_*0.0174532925
        else:
            rotateAngle = 0.0
        
        #Create the comfort mannequin.
        if checkData2 == True:
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
        
        
        #Check if everything is good.
        if checkData1 == True and checkData2 == True:
            checkData = True
        else:
            checkData = False
        
        return checkData, ambTemp, targetTemp, comfRange, mannequinMesh, lb_preparation, lb_visualization
    else:
        return -1


def main(ambTemp, targetTemp, comfRange, mannequinMesh, lb_preparation, lb_visualization):
    # read legend parameters
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar_, False)
    
    if lowB == "min":
        lowB = targetTemp - (comfRange)
    if highB == "max":
        highB = targetTemp + (comfRange)
    range = [lowB, highB]
    
    #Join the Mesh
    joinedManMesh = rc.Geometry.Mesh()
    for mesh in mannequinMesh:
        joinedManMesh.Append(mesh)
    
    # Get the mannequin color
    color = lb_visualization.gradientColor([ambTemp], lowB, highB, customColors)
    
    # color the mesh faces.
    joinedManMesh.VertexColors.CreateMonotoneMesh(color[0])
    
    #Create a legend.
    legendTitle = "C"
    lb_visualization.calculateBB(mannequinMesh, True)
    # create legend geometries
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(range
        , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
    # generate legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    
    lengdTxt = []
    for list in legendTextCrv:
        for item in list:
            lengdTxt.append(item)
    
    if legendBasePoint == None:
        legendBasePoint = lb_visualization.BoundingBoxPar[0]
    
    
    return joinedManMesh, [legendSrfs, lengdTxt], legendBasePoint



#Check the inputs
checkData = False
legend = []
results = checkTheInputs()

if results!= -1:
    checkData, ambTemp, targetTemp, comfRange, mannequinMesh, lb_preparation, lb_visualization = results

#Run the analysis.
if checkData == True:
    result = main(ambTemp, targetTemp, comfRange, mannequinMesh, lb_preparation, lb_visualization)
    if result != -1:
        mannequinMesh, legendInit, legendBasePt = result
        legend.append(legendInit[0])
        for item in legendInit[1]:
            legend.append(item)

#Hide the legend base point.
ghenv.Component.Params.Output[2].Hidden = True