# This component makes a simple string for legend parameters
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to select out the part of a colored mesh that meets a certain conditional statement.  This has multiple uses: The generation of a custom shade from a shade benefit analysis, Quantifying the daylight area from a daylight analysis, Selecting out the portion of a roof with enough solar radiation for PV panels, and much more.

-
Provided by Ladybug 0.0.68
    
    Args:
        _inputMesh: The mesh for which you would like to highlight the portion that meets a threshold.
        _analysisResult: A numerical data set whose length corresponds to the number of faces in the _inputMesh.
        _operator_: A text string representing an operator for the the conditional statement.  The default is set to be greater than (>).  This must be an operator in python and examples include:
            > - Greater Than
            < - Less Than
            >= - Greater or Equal
            <= - Less or Equal
            == - Equals
        percentToKeep_: A number between 0 and 100 that represents the percentage of the mesh faces that you would like to include in the resulting newColoredMesh.  By default, this is set to 25%.
        levelOfPerform_: An optional number that represents the threshold above which a given mesh face is included in the newColoredMesh.  An input here will override the percent input above.
    Returns:
        readMe!: ...
        totalValue: The sum of all of the values that meet the criteria multiplied by the mesh face area.  For example, if the _inputMesh is a radiation study mesh, this is equal to the total radiation falling on the newColoredMesh.  For an energy shade benefit mesh, this is the total energy saved by a shade of this size.
        areaMeetsThresh: The area of the newColoredMesh in Rhino model units.
        newColoredMesh: A new colored mesh with the vlues below the threshold deleted out of it.
        newMeshOutline: A set of curves outlining the portion of the mesh that is above the threshold.
"""

ghenv.Component.Name = "Ladybug_Mesh Threshold Selector"
ghenv.Component.NickName = 'MeshSelector'
ghenv.Component.Message = 'VER 0.0.68\nJAN_01_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh



def checkTheInputs():
    #Check to make sure that the number of shade mesh faces matches the length of the shade New Effect.
    checkData1 = True
    if _inputMesh.Faces.Count != len(_analysisResult) and _inputMesh.Vertices.Count != len(_analysisResult):
        checkData1 = False
        print "The number of faces in the _inputMesh does not equal the number of values in the _analysisResult.  Are you sure that you connected a mesh that matches your input data?"
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "The number of faces in the _inputMesh does not equal the number of values in the _analysisResult.  Are you sure that you connected a mesh that matches your input data?")
    
    #Check to see if the user has hooked up a percent to keep and, if not, set it to 50%.
    if percentToKeep_ == None:
        percent = 0.25
        checkData2 = True
    else:
        if percentToKeep_ <= 100 and percentToKeep_ >= 0:
            checkData2 = True
            percent = percentToKeep_/100
        else:
            checkData2 = False
            percent = None
            print "The percentToKeep_ must be a valude between 0 and 100."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "The percentToKeep_ must be a valude between 0 and 100.")
    
    # Check the operator.
    if _operator_ == None:
        operator = ">"
    else:
        operator = _operator_
        if levelOfPerform_ == None and operator == "==":
            warning = "The equality operator cannot be used with the percentToKeep_ method. \n Operatorhas been changed to be greater than."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #If eveything is good, return a result that says this.
    checkData = False
    if checkData1 == True and checkData2 == True: checkData = True
    
    return checkData, percent, operator


def main(percent, operator):
    #Make a list to keep track of all of the faces in the test mesh.
    faceNumbers = range(len(_analysisResult))
    
    #Sort the list of net effect along with the face numbers list and reverse it so the most valuable cells are at the top.
    faceNumbersSort = [x for (y,x) in sorted(zip(_analysisResult, faceNumbers))]
    _analysisResult.sort()
    if ">" in operator or operator == "==":
        faceNumbersSort.reverse()
        _analysisResult.reverse()
    
    #Remove the faces numbers that are harmful.
    faceNumbersHarm = []
    faceNumbersKept = []
    
    # Take the specified percent of the helpful cells.
    shadeNetFinal = []
    if levelOfPerform_ == None:
        numToTake  = percent*(len(_analysisResult))
        for count, num in enumerate(_analysisResult):
            if count < numToTake:
                shadeNetFinal.append(num)
                faceNumbersKept.append(faceNumbersSort[count])
            else:
                faceNumbersHarm.append(faceNumbersSort[count])
    else:
        for count, num in enumerate(_analysisResult):
            if eval(str(num) + operator + str(levelOfPerform_)):
                shadeNetFinal.append(num)
                faceNumbersKept.append(faceNumbersSort[count])
            else:
                faceNumbersHarm.append(faceNumbersSort[count])
    
    # Check to see if no values meet the conditional statement.
    if len(shadeNetFinal) == 0:
        warning = "No values meet the conditional statement."
        print warning
    
    #Remove the unnecessary cells from the shade mesh.
    newMesh = _inputMesh
    areaList = []
    if _inputMesh.Faces.Count == len(_analysisResult):
        for fnum in faceNumbersKept:
            face = newMesh.Faces[fnum]
            if face.IsQuad:
                srfBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(newMesh.Vertices[face.A]), rc.Geometry.Point3d(newMesh.Vertices[face.B]), rc.Geometry.Point3d(newMesh.Vertices[face.C]), rc.Geometry.Point3d(newMesh.Vertices[face.D]), sc.doc.ModelAbsoluteTolerance)
            else:
                srfBrep = rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(newMesh.Vertices[face.A]), rc.Geometry.Point3d(newMesh.Vertices[face.B]), rc.Geometry.Point3d(newMesh.Vertices[face.C]), sc.doc.ModelAbsoluteTolerance)
            if type(srfBrep) != rc.Geometry.Brep:
                pass
            else:
                areaList.append(rc.Geometry.AreaMassProperties.Compute(srfBrep).Area)
        # Delete unwanted faces.
        newMesh.Faces.DeleteFaces(faceNumbersHarm)
    else:
        newMesh.Vertices.Remove(faceNumbersHarm, True)
    
    #Try to simplify the brep.
    try:
        edgeCrv = newMesh.GetNakedEdges()
        joinedCrv = rc.Geometry.Curve.JoinCurves(edgeCrv, sc.doc.ModelAbsoluteTolerance)
    except:
        try:
            edgeCrv = newMesh.GetNakedEdges()
            nurbsCrvs = []
            for curve in edgeCrv:
                nurbsCrvs.append(curve.ToNurbsCurve())
            joinedCrv = rc.Geometry.Curve.JoinCurves(nurbsCrvs, sc.doc.ModelAbsoluteTolerance)
        except:
            joinedCrv = None
    
    #Calculate the total area and the energy saved by the new mesh.
    if _inputMesh.Faces.Count == len(_analysisResult):
        totalArea = sum(areaList)
        totalEnergyList = []
        for count, area in enumerate(areaList):
            totalEnergyList.append(shadeNetFinal[count]*area)
        totalEnergy = sum(totalEnergyList)
    else:
        totalArea = rc.Geometry.AreaMassProperties.Compute(newMesh).Area
        if totalArea>0:
            totalEnergy = (sum(shadeNetFinal)/len(shadeNetFinal))*totalArea
        else:
            totalEnergy=0
    
    return totalEnergy, totalArea, newMesh, joinedCrv


checkData = False
if _inputMesh != None and _analysisResult != [] and _analysisResult != [None]:
    checkData, percent, operator = checkTheInputs()

if checkData == True and _inputMesh and _analysisResult != []:
    totalValue, areaMeetsThresh, newColoredMesh, newMeshOutline = main(percent, operator)
ghenv.Component.Params.Output[3].Hidden = True