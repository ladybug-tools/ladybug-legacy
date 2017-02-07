# ENVI-Met Reader
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
This component generate readable output files of ENVI-Met v4.0 for Ladybug.
-
Component mainly based on:
https://www.researchgate.net/publication/281031049_Outdoor_Comfort_the_ENVI-BUG_tool_to_evaluate_PMV_values_point_by_point
-
Special thanks goes to MIT.
-
Provided by Ladybug 0.0.64
    
    Args:
        _outputFolder: ENVI-Met output folder path. E.g. 'C:\...\\NewSimulation_output'
        _studyFolder_: ENVI-Met sub-folder, connect a number from 0 to 4. Default value is 0.
        -
        0 = atmosphere
        1 = pollutants
        2 = radiation
        3 = soil
        4 = surface
        _selectItem_: Connect an integer number which represent the index of the file you want to read. Plug a panel to 'outputFiles' to see them.
        -
        Default value is 0, the first file in ENVI-Met model folder.
        _variable_: Select one variable.
        -
        1 = Flow u (m/s)
        2 = Flow v (m/s)
        3 = Flow w (m/s)
        4 = Wind Speed (m/s)
        5 = Wind Speed Change ()
        6 = Wind Direction (deg)
        7 = Pressure Perturbation (Diff)
        8 = Air Temperature (C)
        9 = Air Temperature Delta (K)
        10 = Air Temperature Change (K/h)
        11 = Spec. Humidity (g/kg)
        12 = Relative Humidity ()
        13 = TKE (m/m)
        14 = Dissipation (m/m)
        15 = Vertical Exchange Coef. Impuls (m/s)
        16 = Horizontal Exchange Coef. Impuls (m/s)
        17 = Vegetation LAD (m/m)
        18 = Direct Sw Radiation (W/m)
        19 = Diffuse Sw Radiation (W/m)
        20 = Reflected Sw Radiation (W/m)
        21 = Temperature Flux (Km/s)
        22 = Vapour Flux (g/kgm/s)
        23 = Water on Leafes (g/m)
        24 = Leaf Temperature (C)
        25 = Local Mixing Length (m)
        26 = Mean Radiant Temp. (C)
        27 = TKE normalised 1D ( )
        28 = Dissipation normalised 1D ( )
        29 = Km normalised 1D ( )
        30 = TKE Mechanical Turbulence Prod. ( )
        31 = Stomata Resistance (s/m)
        32 = CO2 (mg/m3)
        33 = CO2 (ppm)
        34 = Plant CO2 Flux (mg/kgm/s)
        35 = Div Rlw Temp change (K/h)
        ---------------: (...)
        readBuildings_: Set to "True" to read and visualize ENVI-Met buildings.
        _runIt: Set to "True" to run the component and perform ENVI-Met data visualization.
    Returns:
        readMe!: ...
        outputFiles: File list that you can read.
        resultFileAddress: Connect this output to "ENVI-Met visualizer".
"""

ghenv.Component.Name = "Ladybug_ENVI-Met Reader"
ghenv.Component.NickName = 'ENVI-MetReader'
ghenv.Component.Message = 'VER 0.0.64\nFEB_05_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import os
import re
import clr
import struct
import collections
import Rhino as rc
clr.AddReference("System.Xml")
import System.Xml
import scriptcontext as sc
import Grasshopper.Kernel as gh


studyFolderDict = {'0':'atmosphere', '1':'pollutants', '2':'radiation', '3':'soil', '4':'surface'}

inputsDict = {
0: ["_outputFolder", "ENVI-Met output folder path. E.g. 'C:\...\\NewSimulation_output'."],
1: ["_studyFolder_", "ENVI-Met sub-folder, connect a number from 0 to 4. Default value is 0.\n-\n0 = atmosphere\n1 = pollutants\n2 = radiation\n3 = soil\n4 = surface"],
2: ["_selectItem_", "Connect an integer number which represent the index of the file you want to read. Plug a panel to 'outputFiles' to see them.\n" + \
"-\nDefault value is 0, the first file in ENVI-Met model folder."],
3: ["_variable_", "Select one variable.\n-\n" + \
"1 = Flow u (m/s)\n2 = Flow v (m/s)\n3 = Flow w (m/s)\n4 = Wind Speed (m/s)\n5 = Wind Speed Change ()\n6 = Wind Direction (deg)\n7 = Pressure Perturbation (Diff)\n"+ \
"8 = Air Temperature (C)\n9 = Air Temperature Delta (K)\n10 = Air Temperature Change (K/h)\n11 = Spec. Humidity (g/kg)\n12 = Relative Humidity ()\n" + \
"13 = TKE (m/m)\n14 = Dissipation (m/m)\n15 = Vertical Exchange Coef. Impuls (m/s)\n16 = Horizontal Exchange Coef. Impuls (m/s)\n17 = Vegetation LAD (m/m)\n"+ \
"18 = Direct Sw Radiation (W/m)\n19 = Diffuse Sw Radiation (W/m)\n20 = Reflected Sw Radiation (W/m)\n21 = Temperature Flux (Km/s)\n22 = Vapour Flux (g/kgm/s)\n"+ \
"23 = Water on Leafes (g/m)\n24 = Leaf Temperature (C)\n25 = Local Mixing Length (m)\n26 = Mean Radiant Temp. (C)\n27 = TKE normalised 1D ( )\n28 = Dissipation normalised 1D ( )\n"+ \
"29 = Km normalised 1D ( )\n30 = TKE Mechanical Turbulence Prod. ( )\n31 = Stomata Resistance (s/m)\n32 = CO2 (mg/m3)\n33 = CO2 (ppm)\n34 = Plant CO2 Flux (mg/kgm/s)\n35 = Div Rlw Temp change (K/h)"],
4: ["---------------", "(...)"],
5: ["readBuildings_", "Set to \"True\" to read and visualize ENVI-Met buildings."],
6: ["_runIt", "Set to \"True\" to run the component and perform ENVI-Met data visualization."]
}

otherFolderDict = {
'0': "Select one variable.\n-\n" + \
"1 = Flow u (m/s)\n2 = Flow v (m/s)\n3 = Flow w (m/s)\n4 = Wind Speed (m/s)\n5 = Wind Speed Change ()\n6 = Wind Direction (deg)\n7 = Pressure Perturbation (Diff)\n"+ \
"8 = Air Temperature (C)\n9 = Air Temperature Delta (K)\n10 = Air Temperature Change (K/h)\n11 = Spec. Humidity (g/kg)\n12 = Relative Humidity ()\n" + \
"13 = TKE (m/m)\n14 = Dissipation (m/m)\n15 = Vertical Exchange Coef. Impuls (m/s)\n16 = Horizontal Exchange Coef. Impuls (m/s)\n17 = Vegetation LAD (m/m)\n"+ \
"18 = Direct Sw Radiation (W/m)\n19 = Diffuse Sw Radiation (W/m)\n20 = Reflected Sw Radiation (W/m)\n21 = Temperature Flux (Km/s)\n22 = Vapour Flux (g/kgm/s)\n"+ \
"23 = Water on Leafes (g/m)\n24 = Leaf Temperature (C)\n25 = Local Mixing Length (m)\n26 = Mean Radiant Temp. (C)\n27 = TKE normalised 1D ( )\n28 = Dissipation normalised 1D ( )\n"+ \
"29 = Km normalised 1D ( )\n30 = TKE Mechanical Turbulence Prod. ( )\n31 = Stomata Resistance (s/m)\n32 = CO2 (mg/m3)\n33 = CO2 (ppm)\n34 = Plant CO2 Flux (mg/kgm/s)\n35 = Div Rlw Temp change (K/h)",
'1': "Select one variable.\n-\n" + \
"1 = Objects\n2 = Flow u (m/s)\n3 = Flow v (m/s)\n4 = Flow w (m/s)\n5 = Wind Speed (m/s)\n6 = Wind Speed Change ()\n7 = Wind Direction (deg)\n8 = Pot. Temperature (K)\n9 Spec. Humidity (g/kg)\n"+ \
"10 = Relative Humidity ()\n11 = Vertical Exchange Coef. Impuls (m/s)\n12 = Horizontal Exchange Coef. Impuls (m/s)\n13 = PM2.5 Concentration (g/m3)\n14 PM2.5 Source (g/s)\n15 = PM2.5 Deposition velocity  (mm/s)\n"+ \
"16 = PM2.5 Total Deposed Mass (g/m2)\n17 = PM2.5 Reaction Term ()",
'2': "Select one variable.\n-\n" + \
"1 = Q_sw Direct (W/m)\n2 = Q_sw Direct Relative ()\n3 = Q_sw Diffuse (W/m)\n4 = Q_sw Reflected Upper Hemisphere (W/m)\n5 = Q_sw Reflected Lower Hemisphere (W/m)\n6 = Q_lw  Upper Hemisphere (W/m)\n7 = Q_lw  Lower Hemisphere (W/m)\n"+ \
"8 = ViewFactor Up Sky ( )\n9 = ViewFactor Up Buildings ( )\n10 = ViewFactor Up Vegetation ( )\n11 = ViewFactor Up Soil ( )\n12 = ViewFactor Down Sky ( )\n13 = ViewFactor Down Buildings ( )\n14 = ViewFactor Down Vegetation ( )\n15 = ViewFactor Down Soil ( )",
'3': "Select one variable.\n-\n" + \
"0 = Temperature (C)\n1 = Volumetic Water Content (m3 H20/m3)\n2 = Relative Soil Wetness related to sat ()\n3 = Local RAD (normalized) (m/m)\n4 = Local RAD Owner ()\n5 = Root Water Uptake (g H20/m31/s)",
'4': "Select one variable.\n-\n" + \
"0 =  Index Surface Grid ()\n1 = Soil Profile Type ()\n2 = z Topo (m)\n3 = Surface inclination ()\n4 = Surface exposition ()\n5 = Shadow Flag ()\n6 = T Surface (C)\n7 = T Surface Diff. (K)\n8 = T Surface Change (K/h)\n9 = q Surface (g/kg)\n"+ \
"10 = uv above Surface (m/s)\n11 = Sensible heat flux (W/m2)\n12 = Exchange Coeff. Heat (m2/s)\n13 = Latent heat flux (W/m2)\n14 = Soil heat Flux (W/m2)\n15 = Q_Sw Direct Horizontal (W/m2)\n16 = Q_Sw Diffuse Horizontal (W/m2)\n"+ \
"17 = Q_Sw Reflected Received Horizontal (W/m2)\n18 = Lambert Factor ()\n19 = Q_Lw emitted (W/m2)\n20 = Q_Lw budget (W/m2)\n21 = Q_Lw from Sky (W/m2)\n22 = Q_Lw from Buildings  (W/m2)\n23 = Q_Lw from Vegetation  (W/m2)\n" + \
"24 = Q_Lw Sum all Fluxes (W/m2)\n25 = Water Flux (g/(m2s))\n26 = SkyViewFaktor ()\n27 = Building Height (m)\n28 = Surface Albedo ()\n29 = Deposition Speed (mm/s)\n30 = Mass Deposed (g/m2)\n31 = z node Biomet ()\n"+ \
"32 = z Biomet (m)\n33 = T Air Biomet (C)\n34 = q Air Biomet (g/kg)\n35 = TMRT Biomet (C)\n36 = Wind Speed Biomet (m/s)\n37 = Mass Biomet (ug/m3)\n38 = Receptors ()" 
}

variables = [{'1' : 'Flow u (m/s)',
             '2' : 'Flow v (m/s)',
             '3' : 'Flow w (m/s)',
             '4' : 'Wind Speed (m/s)',
             '5' : 'Wind Speed Change ()',
             '6' : 'Wind Direction (deg)',
             '7' : 'Pressure Perturbation (Diff)',
             '8' : 'Air Temperature (C)',
             '9' : 'Air Temperature Delta (K)',
             '10' : 'Air Temperature Change (K/h)',
             '11' : 'Spec. Humidity (g/kg)',
             '12' : 'Relative Humidity ()',
             '13': 'TKE (m/m)',
             '14': 'Dissipation (m/m)',
             '15' : 'Vertical Exchange Coef. Impuls (m/s)',
             '16' : 'Horizontal Exchange Coef. Impuls (m/s)',
             '17' : 'Vegetation LAD (m/m)',
             '18' : 'Direct Sw Radiation (W/m)',
             '19' : 'Diffuse Sw Radiation (W/m)',
             '20' : 'Reflected Sw Radiation (W/m)',
             '21' : 'Temperature Flux (Km/s)',
             '22' : 'Vapour Flux (g/kgm/s)',
             '23' : 'Water on Leafes (g/m)',
             '24' : 'Leaf Temperature (C)',
             '25' : 'Local Mixing Length (m)',
             '26' : 'Mean Radiant Temp. (C)',
             '27' : 'TKE normalised 1D ( )',
             '28' : 'Dissipation normalised 1D ( )',
             '29' : 'Km normalised 1D ( )',
             '30' : 'TKE Mechanical Turbulence Prod. ( )',
             '31' : 'Stomata Resistance (s/m)',
             '32' : 'CO2 (mg/m3)',
             '33' : 'CO2 (ppm)',
             '34' : 'Plant CO2 Flux (mg/kgm/s)',
             '35' : 'Div Rlw Temp change (K/h)'},
             {'0' : 'z cart',
             '1' : 'Objects',
             '2' : 'Flow u (m/s)',
             '3' : 'Flow v (m/s)',
             '4' : 'Flow w (m/s)',
             '5' : 'Wind Speed (m/s)',
             '6' : 'Wind Speed Change ()',
             '7' : 'Wind Direction (deg)',
             '8' : 'Pot. Temperature (K)',
             '9' : 'Spec. Humidity (g/kg)',
             '10' : 'Relative Humidity ()',
             '11' : 'Vertical Exchange Coef. Impuls (m/s)',
             '12' : 'Horizontal Exchange Coef. Impuls (m/s)',
             '13' : 'PM2.5 Concentration (g/m3)',
             '14' : 'PM2.5 Source (g/s)',
             '15' : 'PM2.5 Deposition velocity  (mm/s)',
             '16' : 'PM2.5 Total Deposed Mass (g/m2)',
             '17' : 'PM2.5 Reaction Term ()'},
             {'1' : 'Q_sw Direct (W/m)',
             '2' : 'Q_sw Direct Relative ()',
             '3' : 'Q_sw Diffuse (W/m)',
             '4' : 'Q_sw Reflected Upper Hemisphere (W/m)',
             '5' : 'Q_sw Reflected Lower Hemisphere (W/m)',
             '6' : 'Q_lw  Upper Hemisphere (W/m)',
             '7' : 'Q_lw  Lower Hemisphere (W/m)',
             '8' : 'ViewFactor Up Sky ( )',
             '9' : 'ViewFactor Up Buildings ( )',
             '10' : 'ViewFactor Up Vegetation ( )',
             '11' : 'ViewFactor Up Soil ( )',
             '12' : 'ViewFactor Down Sky ( )',
             '13' : 'ViewFactor Down Buildings ( )',
             '14' : 'ViewFactor Down Vegetation ( )',
             '15' : 'ViewFactor Down Soil ( )'},
             {'0' : 'Temperature (C)',
             '1' : 'Volumetic Water Content (m3 H20/m3)',
             '2' : 'Relative Soil Wetness related to sat ()',
             '3' : 'Local RAD (normalized) (m/m)',
             '4' : 'Local RAD Owner ()',
             '5' : 'Root Water Uptake (g H20/m31/s)'},
             {'0' : 'Index Surface Grid ()',
             '1' : 'Soil Profile Type ()',
             '2' : 'z Topo (m)',
             '3' : 'Surface inclination ()',
             '4' : 'Surface exposition ()',
             '5' : 'Shadow Flag ()',
             '6' : 'T Surface (C)',
             '7' : 'T Surface Diff. (K)',
             '8' : 'T Surface Change (K/h)',
             '9' : 'q Surface (g/kg)',
             '10' : 'uv above Surface (m/s)',
             '11' : 'Sensible heat flux (W/m2)',
             '12' : 'Exchange Coeff. Heat (m2/s)',
             '13' : 'Latent heat flux (W/m2)',
             '14' : 'Soil heat Flux (W/m2)',
             '15' : 'Q_Sw Direct Horizontal (W/m2)',
             '16' : 'Q_Sw Diffuse Horizontal (W/m2)',
             '17' : 'Q_Sw Reflected Received Horizontal (W/m2)',
             '18' : 'Lambert Factor ()',
             '19' : 'Q_Lw emitted (W/m2)',
             '20' : 'Q_Lw budget (W/m2)',
             '21' : 'Q_Lw from Sky (W/m2)',
             '22' : 'Q_Lw from Buildings  (W/m2)',
             '23' : 'Q_Lw from Vegetation  (W/m2)',
             '24' : 'Q_Lw Sum all Fluxes (W/m2)',
             '25' : 'Water Flux (g/(m2s))',
             '26' : 'SkyViewFaktor ()',
             '27' : 'Building Height (m)',
             '28' : 'Surface Albedo ()',
             '29' : 'Deposition Speed (mm/s)',
             '30' : 'Mass Deposed (g/m2)',
             '31' : 'z node Biomet ()',
             '32' : 'z Biomet (m)',
             '33' : 'T Air Biomet (C)',
             '34' : 'q Air Biomet (g/kg)',
             '35' : 'TMRT Biomet (C)',
             '36' : 'Wind Speed Biomet (m/s)',
             '37' : 'Mass Biomet (ug/m3)',
             '38' : 'Receptors ()'}]


def setComponentInputs(newText):
    for input in range(7):
        if input == 3:
            ghenv.Component.Params.Input[input].NickName = '_variable_'
            ghenv.Component.Params.Input[input].Name = '_variable_'
            ghenv.Component.Params.Input[input].Description = newText
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]


def restoreComponentInputs():
    for input in range(7):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]


def checkInputs(outputFolder):
    if outputFolder == None:
        return False
    elif outputFolder:
        return True


def ENVIparser(fileName, metaname, dataname, folder, variable, variableHeader, date):
    # this is a modified version of this code here: https://github.com/jduggan1/envi2csv
    def scan_tree(node, metadata):
        metadata[str(node.tag)] = node.text
        for child in node:
            metadata = scan_tree(child, metadata)
        return metadata
    
    def findTxt(mf, key):
        return mf.GetElementsByTagName(key)[0].InnerText
    
    metafile = open(metaname, 'r')
    datafile = open(dataname, 'rb')
    metainfo = re.sub('[^\s()_<>/,\.A-Za-z0-9]+', '', metafile.read())
    
    fileCopy = os.path.join(folder, str(variable)+".EDX")
    with open(fileCopy, 'w+') as f:
        f.write(metainfo)
    
    metafile = System.Xml.XmlDocument()
    
    metafile.Load(fileCopy)
    root = metafile.DocumentElement
    
    elementList = metafile.GetElementsByTagName("name_variables")
    for item in elementList:
        varnames = item.InnerText.split(',')
    variables = {}
    
    # location
    projectName = findTxt(metafile, "projectname") + ',' + findTxt(metafile, "locationname") + ',' + date
    # dimension of the grid
    gridDimension = [findTxt(metafile, "spacing_x"), findTxt(metafile, "spacing_y"), findTxt(metafile, "spacing_z")]
    dimension = '\n'.join(gridDimension)
    # number of cells
    numOfCells = ','.join([findTxt(metafile,"nr_xdata"), findTxt(metafile, "nr_ydata"), findTxt(metafile, "nr_zdata")])
    
    xdim = int(findTxt(metafile, "nr_xdata"))
    ydim = int(findTxt(metafile, "nr_ydata"))
    zdim = int(findTxt(metafile, "nr_zdata"))
    
    with open(fileName, 'w') as f:
        f.write(variableHeader + '\n' + projectName + '\n' + numOfCells + '\n' + dimension + '\n')
        for varname in varnames:
            variables[varname] = struct.unpack('f'*xdim*ydim*zdim, datafile.read(4*xdim*ydim*zdim))
            data = '\n'.join(map(str, variables[varname]))
            if varname == varnames[variable]:
                f.write(data)


def ENVIGeometryParser(p, folder):
    
    def findINX(p):
        parts = p.split('\\')
        folderINX = '\\'.join(parts[:-1])
        for name in os.listdir(folderINX):
            if name[-3:] == 'INX':
                fullPathINX = os.path.join(folderINX, name)
        return fullPathINX    
    
    
    def findTxt(mf, key):
        return mf.GetElementsByTagName(key)[0].InnerText
    
    INXname = findINX(p)
    if INXname == None:
        print("File INX not found! Check ENVI-Met model folder.")
        return -1
    
    listWithoutAuthor = []
    file = open(INXname, 'r')
    for i, line in enumerate(file.readlines()):
        if i != 10:
            listWithoutAuthor.append(line)
    file = ''.join(listWithoutAuthor)
    
    metainfo = re.sub('[^\s()_<>/,\.A-Za-z0-9=""]+', '', file)
    
    fileCopy = os.path.join(folder, "geoData.INX")
    with open(fileCopy, 'w+') as f:
        f.write(metainfo)
    
    metafile = System.Xml.XmlDocument()
    
    metafile.Load(fileCopy)
    root = metafile.DocumentElement
    
    gridI, gridJ, gridZ = int(findTxt(metafile, "gridsI")), int(findTxt(metafile, "gridsJ")), int(findTxt(metafile, "gridsZ"))
    dx, dy, dz = float(findTxt(metafile, "dx"))/unitConversionFactor, float(findTxt(metafile, "dy"))/unitConversionFactor, float(findTxt(metafile, "dzbase"))/unitConversionFactor
    
    topBase = findTxt(metafile, "zTop")
    topBase = re.sub('[\r ]', '', topBase)
    topBase = re.split('\n', topBase)
    topBase = [l.split(',') for l in topBase if len(l) != 0]
    
    bottomBase = findTxt(metafile, "zBottom")
    bottomBase = re.sub('[\r ]', '', bottomBase)
    bottomBase = re.split('\n', bottomBase)
    bottomBase = [l.split(',') for l in bottomBase if len(l) != 0]
    
    # geometry
    points = []
    for i in range(gridI):
        rows = []
        for j in range(gridJ):
            pt = rc.Geometry.Point3d((i+1)*dx-(dx/2), (gridJ-j)*dy-(dy/2), 0)
            rows.append(pt)
        points.append(rows)
    points = [list(x) for x in zip(*points)]
    
    buildingData = []
    for lIndexT, lIndexB, lItem in zip(topBase, bottomBase, points):
        for indexT, indexB, item in zip(lIndexT, lIndexB, lItem):
            if indexB != '0':
                item.Z = int(indexB)
                indexT = int(indexT)-int(indexB)
            if indexT != '0':
                buildingData.append((int(indexT)/unitConversionFactor, int(indexB)/unitConversionFactor, item))
    
    xSize = rc.Geometry.Interval(-dx/2, dx/2)
    ySize = rc.Geometry.Interval(-dy/2, dy/2)
    buildings = [rc.Geometry.Box(rc.Geometry.Plane(b[2], rc.Geometry.Vector3d.ZAxis), xSize, ySize, rc.Geometry.Interval(0, b[0])) for b in buildingData]
    
    return buildings


def makeFolder(subFolder):
    # make a folder
    subFolder = subFolder + '\\'
    appdata = os.getenv("APPDATA")
    try:
        directory = os.path.join(appdata, "Ladybug\ENVIbug", subFolder)
        if not os.path.exists(directory):
            os.makedirs(directory)
    except:
        directory = os.path.join(appdata[:3], "Ladybug\ENVIbug", subFolder)
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    return directory


def main():
    if _selectItem_ == None: selectItem = 0
    else: selectItem = _selectItem_
    if _variable_ == None: variable = 2
    else: variable = _variable_
    
    
    try:
        varStr = variables[int(k)][str(variable)]
    except KeyError:
        warning = "Please, check '_variable_' input."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    print ("variable: {}".format(varStr))
    
    folderName = makeFolder(studyFolder)
    
    fileName = folderName + str(variable)+".txt"
    
    # folder
    outputFolder = os.path.join(_outputFolder, studyFolder)
    if not os.path.exists(outputFolder):
        print("Please connect a valid path.")
        return -1
    
    listFile = os.listdir(outputFolder)
    listFileW = [item[:-4] for item in listFile]
    listFileW = [item for item, count in collections.Counter(listFileW).items() if count == 2 if 'CHECK' not in item]
    outputFiles = sorted(listFileW)
    try:
        selItem = outputFiles[selectItem]
    except IndexError:
        print("There are just {} files in the folder.".format(len(outputFiles)))
        return -1
    print("you are reading this file: {}".format(selItem))
    
    metaname = os.path.join(outputFolder, outputFiles[selectItem] + '.EDX')
    dataname = os.path.join(outputFolder, outputFiles[selectItem] + '.EDT')
    
    if _runIt:
        ENVIparser(fileName, metaname, dataname, folderName, variable, varStr, selItem[-19:])
        if os.path.isfile(fileName):
            resultFileAddress = fileName
            if readBuildings_:
                folderName = makeFolder('geometry')
                buildings = ENVIGeometryParser(_outputFolder, folderName)
                return resultFileAddress, outputFiles, buildings
            else: return resultFileAddress, outputFiles, None
        else:
            print("File not found.")
            return -1
    else:
        print("Set runIt to True.")
        return None, outputFiles, None


initCheck = False
if sc.sticky.has_key('ladybug_release'):
    initCheck = True
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = True
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    lb_preparation = sc.sticky["ladybug_Preparation"]()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")


check = checkInputs(_outputFolder)

if _studyFolder_ == None: studyFolder = studyFolderDict['0']
else:
    try:
        studyFolder = studyFolderDict[_studyFolder_]
    except KeyError: studyFolder = studyFolderDict['0']

print("folder: {}".format(studyFolder))
for key, item in studyFolderDict.items():
    if item == studyFolder:
        k = key

if int(k) > 0: setComponentInputs(otherFolderDict[k])
else: restoreComponentInputs()

if check and initCheck:
    unitConversionFactor = lb_preparation.checkUnits()
    result = main()
    if result != -1:
        resultFileAddress, outputFiles, buildings = result
    else:
        print("Something went wrong!")
else:
    pass
    print("Please provide all inputs.")