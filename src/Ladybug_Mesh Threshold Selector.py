# This component makes a simple string for legend parameters
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
Use this component to delete out unwanted areas of a shade after a shade benefit evaluation has been run.  This will help turn your shade evaluation results into an actual shade brep based on a percentage of beneficial shade cells that you decide.

-
Provided by Ladybug 0.0.62
    
    Args:
        _inputMesh: The mesh for which you would like to highlight the portion that meets a threshold.
        _analysisResult: A numerical data set whose length corresponds to the number of faces in the _inputMesh.
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
ghenv.Component.Message = 'VER 0.0.62\nAUG_08_2016'
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
    if _inputMesh.Faces.Count == len(_analysisResult): checkData1 = True
    else:
        checkData1 = False
        print "The number of faces in the _inputMesh does not equal the number of values in the _analysisResult.  Are you sure that you connected a mesh that matches your input data?"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "The number of faces in the _inputMesh does not equal the number of values in the _analysisResult.  Are you sure that you connected a mesh that matches your input data?")
    
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
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "The percentToKeep_ must be a valude between 0 and 100.")
    
    #If eveything is good, return a result that says this.
    checkData = False
    if checkData1 == True and checkData2 == True: checkData = True
    
    return checkData, percent


def main(percent):
    #Make a list to keep track of all of the faces in the test mesh.
    faceNumbers = range(len(_analysisResult))
    
    #Sort the list of net effect along with the face numbers list and reverse it so the most valuable cells are at the top.
    faceNumbersSort = [x for (y,x) in sorted(zip(_analysisResult, faceNumbers))]
    faceNumbersSort.reverse()
    _analysisResult.sort()
    _analysisResult.reverse()
    
    #Remove the faces numbers that are harmful.
    faceNumbersHarm = []
    shadeNetEffectHelp = []
    for count, num in enumerate(_analysisResult):
        if num > 0: shadeNetEffectHelp.append(num)
        else: faceNumbersHarm.append(faceNumbersSort[count])
    
    # Take the specified percent of the helpful cells.
    shadeNetFinal = []
    if levelOfPerform_ == None:
        numToTake  = percent*(len(shadeNetEffectHelp))
        for count, num in enumerate(shadeNetEffectHelp):
            if count < numToTake: shadeNetFinal.append(num)
            else: faceNumbersHarm.append(faceNumbersSort[count])
    else:
        for count, num in enumerate(shadeNetEffectHelp):
            if num > levelOfPerform_: shadeNetFinal.append(num)
            else: faceNumbersHarm.append(faceNumbersSort[count])
    
    #Remove the unnecessary cells from the shade mesh.
    newMesh = _inputMesh
    newMesh.Faces.DeleteFaces(faceNumbersHarm)
    
    #Turn the new mesh into a brep snd get the area of each face.
    meshBrep = rc.Geometry.Brep.CreateFromMesh(newMesh, True)
    if meshBrep != None:
        areaList = []
        for surface in meshBrep.Faces:
            areaList.append(rc.Geometry.AreaMassProperties.Compute(surface).Area)
        
        #Try to simplify the brep.
        try:
            edgeCrv = meshBrep.DuplicateEdgeCurves(True)
            joinedCrv = rc.Geometry.Curve.JoinCurves(edgeCrv, sc.doc.ModelAbsoluteTolerance)
        except:
            joinedCrv = none
        
        #Calculate the total area and the energy saved by the new mesh.
        totalArea = sum(areaList)
        totalEnergyList = []
        for count, area in enumerate(areaList):
            totalEnergyList.append(shadeNetFinal[count]*area)
        totalEnergy = sum(totalEnergyList)
        
        return totalEnergy, totalArea, newMesh, joinedCrv
    else:
        return 0, 0, None, None


checkData = False
if _inputMesh != None and _analysisResult != [] and _analysisResult != [None]:
    checkData, percent = checkTheInputs()

if checkData == True and _inputMesh and _analysisResult != []:
    totalValue, areaMeetsThresh, newColoredMesh, newMeshOutline = main(percent)
ghenv.Component.Params.Output[3].Hidden = True