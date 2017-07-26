# import cec photovoltaics module
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Jason Sensibaugh and Djordje Spasic <sensij@yahoo.com> and <djordjedspasic@gmail.com>
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
Use this component to import Photovoltaics module settings for particular module from "California Energy Commission (CEC) Modules" library.
Download library's newest version from the bottom of the following page:
https://sam.nrel.gov/libraries
-
Provided by Ladybug 0.0.65
    
    input:
        _modulesLibraryFile: Add "California Energy Commission (CEC) Modules" .csv file path to this input.
                             -
                             Download its newest version on the bottom of this web page
                             sam.nrel.gov/libraries
        moduleIndex_: An index corresponding to chosen module from "allModuleNames" output.
                      -
                      If nothing added to this input, "0" will be used as a default (the first module from the "allModuleNames" output will be chosen).
        newModuleMountType_: New mounting type (configuration) of the module.
                             Each module from "_modulesLibraryFile" input comes with predefined mounting type (configuration). You can see it in "moduleMountType" output.
                             If you would like to change that predefined mounting type, then use this input, and the following values:
                             -
                             0 = Insulated back (pv curtain wall, pv skylights, BIPV installations with obstructed backside airflow)
                             1 = Close (flush) roof mount (pv array mounted parallel and relatively close to the plane of the roof (between 5 and 15 centimenters))
                             2 = Open rack (ground mount array, flat/sloped roof array that is tilted, pole-mount solar panels, solar carports, solar canopies, BIPV installations with sufficient backside airflow)
                             -
                             This input is actually the same as "mountType" input of the Ladybug "Simplified Photovoltaics Module" component.
                             -
                             If nothing is added to this input, default mount type of the chosen module will be used (you can check which one by looking at the "moduleMountType" output).
        moduleHeightAboveGround_: Height (vertical distance) from ground surface to the lowest part of the module.
                                  -
                                  If not supplied, default value of 3 meters (10 feet) will be used.
                                  -
                                  In Rhino document units (meters, feet, inches...).
        moduleActiveAreaPercent_: Percentage of the module's area excluding module framing and gaps between cells. 
                                  -
                                  If not supplied, default value of 90(perc.) will be used.
                                  -
                                  In percent.
    
    output:
        readMe!: ...
        allModuleNames: Names of all crystalline silicon modules from the "_modulesLibraryFile" file.
        moduleName: Name of the chosen module, according to "moduleIndex_" input.
        moduleMaterial: Material of the chosen module.
        moduleMountType: Final mount type (configuration) of the chosen module.
                         This output can have two values:
                         -
                         a) default one: coming directly from "_modulesLibraryFile". This value will only appear if "newModuleMountType_" input is empty.
                         b) custom one: altered mounting type, according to "newModuleMountType_" input.
                         -
                         One of the following mount types will be shown:
                         -
                         0 = Insulated back (pv curtain wall, pv skylights, BIPV installations with obstructed backside airflow)
                         1 = Close (flush) roof mount (pv array mounted parallel and relatively close to the plane of the roof (between 5 and 15 centimenters))
                         2 = Open rack (ground mount array, flat/sloped roof array that is tilted, pole-mount solar panels, solar carports, solar canopies, BIPV installations with sufficient backside airflow)
        moduleArea: Area of the chosen module.
                    -
                    In square meters.
        modulePower: Module's power at maximum-power point of the chose module.
                     -
                     In Watts.
        moduleEfficiency: Module's aperture (active area) efficiency.
                          -
                          In percent (%).
        sourceNotes: Source notes corresponding to the chosen module.
                     It basically contains source from which the "PVmoduleSettings" output data has been generated, and date when it has been generated.
        PVmoduleSettings: A list of PV module settings. Plug it to "Photovoltaics surface" component's "PVmoduleSettings_" input.
"""

ghenv.Component.Name = "Ladybug_Import CEC Photovoltaics Module"
ghenv.Component.NickName = "ImportCECPhotovoltaicsModule"
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#ghenv.Component.SubCategory = "4 | Renewables"
#compatibleLBVersion = VER 0.0.64\nAPR_12_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System
import Rhino


def main(modulesLibraryFile_filePath, moduleIndex, newModuleMountType, moduleHeightAboveGroundRhinoUnits, moduleActiveAreaPercent):
    
    # find unitConversionFactor
    unitConversionFactor = lb_preparation.checkUnits()
    sc.doc = Rhino.RhinoDoc.ActiveDoc
    unitSystem = rs.UnitSystemName()
    sc.doc = ghdoc
    
    
    if (modulesLibraryFile_filePath == None):
        moduleNameL = moduleName = moduleMaterial = moduleMountType = moduleArea = nameplateDCpowerRating_m = moduleEfficiency = sourceNotes = PVmoduleSettings = None
        validInputData = False
        printMsg = "Add \"California Energy Commission (CEC) Modules\" .csv file path to \"_modulesLibraryFile\" input.\n" + \
                   "Download its newest version from the bottom of the following page:\n\n" + \
                   "https://sam.nrel.gov/libraries"
        return moduleNameL, moduleName, moduleMaterial, moduleMountType, moduleArea, nameplateDCpowerRating_m, moduleEfficiency, sourceNotes, PVmoduleSettings, validInputData, printMsg
    # testing if the "modulesLibraryFile_filePath" is valid:
    try:
        with open(modulesLibraryFile_filePath) as modulesCSVFile:
            pass
    except:
        moduleNameL = moduleName = moduleMaterial = moduleMountType = moduleArea = nameplateDCpowerRating_m = moduleEfficiency = sourceNotes = PVmoduleSettings = None
        validInputData = False
        printMsg = "The .csv file path you added to the \"_modulesLibraryFile\" input is invalid.\n" + \
                   "Download the newest version of \"California Energy Commission (CEC) Modules\" .csv file from the bottom of the following page:\n" + \
                   "https://sam.nrel.gov/libraries\n" + \
                   "And add its file path to the \"_modulesLibraryFile\" input."
        return moduleNameL, moduleName, moduleMaterial, moduleMountType, moduleArea, nameplateDCpowerRating_m, moduleEfficiency, sourceNotes, PVmoduleSettings, validInputData, printMsg
    
    
    if (newModuleMountType == None):
        pass
    elif (newModuleMountType < 0) or (newModuleMountType > 2):
        print "newModuleMountType: ", newModuleMountType
        moduleNameL = moduleName = moduleMaterial = moduleMountType = moduleArea = nameplateDCpowerRating_m = moduleEfficiency = sourceNotes = PVmoduleSettings = None
        validInputData = False
        printMsg = "\"newModuleMountType_\" input supports only the following values:\n" + \
                   "0 = Insulated back\n" + \
                   "1 = Close (flush) roof mount\n" + \
                   "2 = Open rack\n" + \
                   "Choose one of these three."
        return moduleNameL, moduleName, moduleMaterial, moduleMountType, moduleArea, nameplateDCpowerRating_m, moduleEfficiency, sourceNotes, PVmoduleSettings, validInputData, printMsg
    
    
    if (moduleHeightAboveGroundRhinoUnits == None) or (moduleHeightAboveGroundRhinoUnits < 0):
        moduleHeightAboveGroundM = 6  # default value: 6 meters, in meters
    else:
        moduleHeightAboveGroundM = moduleHeightAboveGroundRhinoUnits/unitConversionFactor  # in meters
    
    
    if (moduleActiveAreaPercent == None) or (moduleActiveAreaPercent <= 0) or (moduleActiveAreaPercent > 100):
        moduleActiveAreaPercent = 90  # default in %
    
    
    # define "ws_adjusted_factor" based on the height of module above the ground
    if (moduleHeightAboveGroundM <= 3):
        ws_adjusted_factor = 0.51  # unitless
    elif (moduleHeightAboveGroundM > 3):
        ws_adjusted_factor = 0.61  # unitless
    
    
    with open(modulesLibraryFile_filePath) as modulesCSVFile:
        moduleNameL = []
        materialL = []
        dateL = []
        versionL = []
        moduleAreaML = []
        Vmp_refL = []
        Imp_refL = []
        Voc_refL = []
        Isc_refL = []
        alpha_sc_refL = []
        beta_oc_refL = []
        IL_refL = []
        Io_refL = []
        Rs_refL = []
        Rsh_refL = []
        A_refL = []
        n_sL = []
        adjustL = []
        gamma_r_refL = []
        TnoctL = []
        mountType_libraryL = []
        nameplateDCpowerRating_mL = []
        moduleEfficiencyL = []
        
        lines = modulesCSVFile.readlines()
        for lineIndex, line in enumerate(lines):
            itemsPerLine = line.strip().split(",")
            if (lineIndex >= 3)  and  ((len(itemsPerLine[10]) > 0) and (len(itemsPerLine[19]) > 0)):  # "Yingli Energy (China) YL310P-35b" with lineIndex = 13817 is invalid (does not contain all "PVmoduleSettings" items)
                # lineIndex = 0,1,2 are column names, units, script variables names
                moduleName = itemsPerLine[0]  # "Name" from .csv file
                material = itemsPerLine[21]  # "Technology" from .csv file
                date = itemsPerLine[2]  # "Date" from .csv file
                version = itemsPerLine[19]  # "Version" from .csv file
                moduleAreaM = float(itemsPerLine[4])  # "Area"("cec_area") from .csv file. The total area of the module, including spaces between cells and the frame!!
                BIPVorNot = itemsPerLine[1].strip()  # "BIPV" from .csv file
                #if material in ["c-Si", "mono-Si", "mc-Si", "multi-Si", "EFG mc-Si",   "Si-Film", "HIT Si"]:  # only use mono and multi crystalline photovoltaics
                #if True:
                if not "Concentrator" in moduleName:
                    Vmp_ref = float(itemsPerLine[9])  # "cec_v_mp_ref" from .csv
                    Imp_ref = float(itemsPerLine[8])  # "cec_i_mp_ref" from .csv
                    Voc_ref = float(itemsPerLine[7])  # "cec_v_oc_ref" from .csv
                    Isc_ref = float(itemsPerLine[6])  # "cec_i_sc_ref" from .csv
                    alpha_sc_ref = float(itemsPerLine[10])  # "cec_alpha_sc" from .csv
                    beta_oc_ref = float(itemsPerLine[11])  # "cec_beta_oc" from .csv
                    IL_ref = float(itemsPerLine[13])  # "cec_i_l_ref" from .csv
                    Io_ref = float(itemsPerLine[14])  # "cec_i_o_ref" from .csv
                    Rs_ref = float(itemsPerLine[15])  # "cec_r_s" from .csv
                    Rsh_ref = float(itemsPerLine[16])  # "cec_r_sh_ref" from .csv
                    A_ref = float(itemsPerLine[12])  # "cec_a_ref" from .csv
                    n_s = float(itemsPerLine[5])  # "cec_n_s" from .csv
                    adjust = float(itemsPerLine[17])  # "cec_adjust" from .csv
                    gamma_r_ref = float(itemsPerLine[18])  # "cec_gamma_r" from .csv
                    Tnoct = float(itemsPerLine[3])  # "cec_t_noct" from .csv
                    
                    if (BIPVorNot == "Y"): mountType_library = 0  # (insulated back)
                    elif (BIPVorNot == "N"): mountType_library = 2  #(open rack)
                    
                    nameplateDCpowerRating_m = round( Imp_ref * Vmp_ref ,2)  # Power at maximum-power point of a single module, in W
                    moduleEfficiency = round( (Imp_ref * Vmp_ref) / (1000 * moduleAreaM * (moduleActiveAreaPercent/100))  * 100 ,2)  # in percent
                    
                    # add to lists
                    moduleNameL.append(moduleName)
                    materialL.append(material)
                    dateL.append(date)
                    versionL.append(version)
                    moduleAreaML.append(moduleAreaM)
                    Vmp_refL.append(Vmp_ref)
                    Imp_refL.append(Imp_ref)
                    Voc_refL.append(Voc_ref)
                    Isc_refL.append(Isc_ref)
                    alpha_sc_refL.append(alpha_sc_ref)
                    beta_oc_refL.append(beta_oc_ref)
                    IL_refL.append(IL_ref)
                    Io_refL.append(Io_ref)
                    Rs_refL.append(Rs_ref)
                    Rsh_refL.append(Rsh_ref)
                    A_refL.append(A_ref)
                    n_sL.append(n_s)
                    adjustL.append(adjust)
                    gamma_r_refL.append(gamma_r_ref)
                    TnoctL.append(Tnoct)
                    mountType_libraryL.append(mountType_library)
                    nameplateDCpowerRating_mL.append(nameplateDCpowerRating_m)  # in Watts
                    moduleEfficiencyL.append(moduleEfficiency)  # in percent
    modulesCSVFile.close()
    
    
    if (moduleIndex > (len(moduleNameL)-1)):
        moduleName = moduleMaterial = moduleMountType = moduleArea = nameplateDCpowerRating_m = moduleEfficiency = sourceNotes = PVmoduleSettings = None
        validInputData = False
        printMsg = "\"moduleIndex_\" input is higher than the number of modules from the \"_modulesLibraryFile\" file.\n" + \
                   "Use \"moduleIndex_\" input from 0 to %s." % (len(moduleNameL)-1)
        return moduleNameL, moduleName, moduleMaterial, moduleMountType, moduleArea, nameplateDCpowerRating_m, moduleEfficiency, sourceNotes, PVmoduleSettings, validInputData, printMsg
    
    
    # NOCT Cell Temperature Model
    # if NOTHING added to "newModuleMountType_" input: Tnoct_adj = Tnoct value from the .csv file
    # if something added to "newModuleMountType_" input: Tnoct_adj is corrected according to "newModuleMountType_" input
    if (newModuleMountType == None):
        # NOTHING inputted to "newModuleMountType_" input
        moduleMountType_final = mountType_library
        Tnoct_adj = TnoctL[moduleIndex]
    elif (newModuleMountType != None):
        # something added to "newModuleMountType_" input
        if (newModuleMountType == 0):
            moduleMountType_final = 0
            Tnoct_adj = TnoctL[moduleIndex] + 18  # Insulated back/BIPV without back airflow (for standoff distance: 0.5 in)
        elif (newModuleMountType == 1):
            moduleMountType_final = 1
            Tnoct_adj = TnoctL[moduleIndex] + 6  # Close (flush) mount (for standoff distance: 1.5 to 2.5 in)
        elif (newModuleMountType == 2):
            moduleMountType_final = 2
            Tnoct_adj = TnoctL[moduleIndex] + 0  # Open rack (for standoff distance: > 3.5 in)
        
    
    
    PVmoduleSettings = [
    moduleNameL[moduleIndex],
    materialL[moduleIndex],
    moduleMountType_final,
    moduleAreaML[moduleIndex],
    moduleActiveAreaPercent,
    nameplateDCpowerRating_mL[moduleIndex],
    moduleEfficiencyL[moduleIndex],
    Vmp_refL[moduleIndex],
    Imp_refL[moduleIndex],
    Voc_refL[moduleIndex],
    Isc_refL[moduleIndex],
    alpha_sc_refL[moduleIndex],
    beta_oc_refL[moduleIndex],
    IL_refL[moduleIndex],
    Io_refL[moduleIndex],
    Rs_refL[moduleIndex],
    Rsh_refL[moduleIndex],
    A_refL[moduleIndex],
    n_sL[moduleIndex],
    adjustL[moduleIndex],
    gamma_r_refL[moduleIndex],
    ws_adjusted_factor,
    Tnoct_adj]
    
    sourceNotes = versionL[moduleIndex] + ", " + dateL[moduleIndex]
    
    #print "__len(moduleNameL): ", len(moduleNameL)
    # deleting
    del modulesLibraryFile_filePath; del modulesCSVFile; del lines
    "del versionL"; "del moduleAreaML"; "del materialL"; del Vmp_refL; del Imp_refL; del Voc_refL; del Isc_refL; del alpha_sc_refL; del beta_oc_refL; del IL_refL;  del Io_refL; del Rs_refL; del Rsh_refL; del A_refL; del n_sL; del adjustL; del gamma_r_refL; del ws_adjusted_factor; "del nameplateDCpowerRating_mL"; "del moduleEfficiencyL"
    
    # printing
    resultsCompletedMsg = "Import CEC photovoltaics module component results successfully completed!"
    printOutputMsg = \
    """
Input data:,

Module Name:  %s,
Module Material:  %s,
Module Area (m2):  %s,
Module Active Area Percent (perc.):  %s,
Module height above ground (%s):  %s

New Module Mount type:  %s,
Default Module Mount type:  %s,

Power at Max Power (W):  %s,
Module Efficiency (perc.):  %s,
Reference Max Power Voltage (V):  %s,
Reference Max Power Current (A):  %s,
Reference Open Circuit Voltage (V):  %s,
Reference Short Circuit Current (A):  %s,

Short circuit current temperature coefficient (A/C deg.):  %s,
Open circuit voltage temperature coefficient (V/C deg.):  %s,

Reference light current:  %s,
Reference diode saturation current:  %s,
Reference series resistance:  %s,
Reference shunt resistance:  %s,

Reference ideality factor:  %s,
Diode factor:  %s,

Temperature coefficient adjustment factor:  %s,
Temperature coefficient of Power (perc./C deg.):  %s,
Wind speed adjustment factor:  %s,
Normal operating cell temperature:  %s,
    """ % (PVmoduleSettings[0], PVmoduleSettings[1], PVmoduleSettings[3], PVmoduleSettings[4], unitSystem, moduleHeightAboveGroundM/unitConversionFactor,
    newModuleMountType, mountType_libraryL[moduleIndex], 
    PVmoduleSettings[5], PVmoduleSettings[6], PVmoduleSettings[7], PVmoduleSettings[8], PVmoduleSettings[9], PVmoduleSettings[10], 
    PVmoduleSettings[11], PVmoduleSettings[12],
    PVmoduleSettings[13], PVmoduleSettings[14], PVmoduleSettings[15], PVmoduleSettings[16],
    PVmoduleSettings[17], PVmoduleSettings[18],
    PVmoduleSettings[19], PVmoduleSettings[20], PVmoduleSettings[21], PVmoduleSettings[22])
    print resultsCompletedMsg
    print printOutputMsg
    
    
    validInputData = True
    printMsg = "ok"
    
    
    # testing (comment out line "300" first)
    """
    print "-------"
    print "testing"
    print " "
    print "Module Name: ", moduleNameL[moduleIndex], "_", PVmoduleSettings[0]
    print "Module Material: ", materialL[moduleIndex], "_", PVmoduleSettings[1]
    print "Default Module Mount type: ", mountType_libraryL[moduleIndex], "_"
    print "Module Area (m2): ", moduleAreaML[moduleIndex], "_", PVmoduleSettings[3]
    print "Module Active Area Percent (perc.): ", moduleActiveAreaPercent, "_", PVmoduleSettings[4]
    print " "
    print "Power at Max Power (W): ", nameplateDCpowerRating_mL[moduleIndex], "_", PVmoduleSettings[5]
    print "Module Efficiency (perc.): ", moduleEfficiencyL[moduleIndex], "_", PVmoduleSettings[6]
    print "Reference Max Power Voltage (V): ", Vmp_refL[moduleIndex], "_", PVmoduleSettings[7]
    print "Reference Max Power Current (A): ", Imp_refL[moduleIndex], "_", PVmoduleSettings[8]
    print "Reference Open Circuit Voltage (V): ", Voc_refL[moduleIndex], "_", PVmoduleSettings[9]
    print "Reference Short Circuit Current (A): ", Isc_refL[moduleIndex], "_", PVmoduleSettings[10]
    print " "
    print "Short circuit current temperature coefficient (A/C deg.): ", alpha_sc_refL[moduleIndex], "_", PVmoduleSettings[11]
    print "Open circuit voltage temperature coefficient (V/C deg.): ", beta_oc_refL[moduleIndex], "_", PVmoduleSettings[12]
    print " "
    print "Reference light current: ", IL_refL[moduleIndex], "_", PVmoduleSettings[13]
    print "Reference diode saturation current: ", Io_refL[moduleIndex], "_", PVmoduleSettings[14]
    print "Reference series resistance: ", Rs_refL[moduleIndex], "_", PVmoduleSettings[15]
    print "Reference shunt resistance: ", Rsh_refL[moduleIndex], "_", PVmoduleSettings[16]
    print " "
    print "Reference ideality factor: ", A_refL[moduleIndex], "_", PVmoduleSettings[17]
    print "Diode factor: ", n_sL[moduleIndex], "_", PVmoduleSettings[18]
    print " "
    print "Temperature coefficient adjustment factor: ", adjustL[moduleIndex], "_", PVmoduleSettings[19]
    print "Temperature coefficient of Power (perc./C deg.): ", gamma_r_refL[moduleIndex], "_", PVmoduleSettings[20]
    print "Wind speed adjustment factor: ", ws_adjusted_factor, "_", PVmoduleSettings[21]
    print "Normal operating cell temperature: ", Tnoct_adj, "_", PVmoduleSettings[22]
    """
    return moduleNameL, moduleNameL[moduleIndex], materialL[moduleIndex], moduleMountType_final, moduleAreaML[moduleIndex], nameplateDCpowerRating_mL[moduleIndex], moduleEfficiencyL[moduleIndex], sourceNotes, PVmoduleSettings, validInputData, printMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        allModuleNames, moduleName, moduleMaterial, moduleMountType, moduleArea, modulePower, moduleEfficiency, sourceNotes, PVmoduleSettings, validInputData, printMsg = main(_modulesLibraryFile, moduleIndex_, newModuleMountType_, moduleHeightAboveGround_, moduleActiveAreaPercent_)
        if not validInputData:
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
