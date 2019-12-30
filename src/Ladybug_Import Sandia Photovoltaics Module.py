# import sandia photovoltaics module
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Jason Sensibaugh and Djordje Spasic <sensij@yahoo.com> and <djordjedspasic@gmail.com>
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
Use this component to import Photovoltaics module settings for particular module from "Sandia National Laboratories Modules" library.
Download library's newest version from the bottom of the following page:
https://sam.nrel.gov/libraries
-
Provided by Ladybug 0.0.68
    
    input:
        _modulesLibraryFile: Add "Sandia National Laboratories Modules" .csv file path to this input.
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

ghenv.Component.Name = "Ladybug_Import Sandia Photovoltaics Module"
ghenv.Component.NickName = "ImportSandiaPhotovoltaicsModule"
ghenv.Component.Message = 'VER 0.0.68\nJAN_01_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Renewables"
#compatibleLBVersion = VER 0.0.64\nAPR_12_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
import System


def main(modulesLibraryFile_filePath, moduleIndex, newModuleMountType, moduleActiveAreaPercent):
    
    if (modulesLibraryFile_filePath == None):
        moduleNameL = moduleName = moduleMaterial = moduleMountType = moduleArea = nameplateDCpowerRating_m = moduleEfficiency = sourceNotes = PVmoduleSettings = None
        validInputData = False
        printMsg = "Add \"Sandia National Laboratories Modules\" .csv file path to \"_modulesLibraryFile\" input.\n" + \
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
                   "Download the newest version of \"Sandia National Laboratories Modules\" .csv file from the bottom of the following page:\n" + \
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
    
    
    if (moduleActiveAreaPercent == None) or (moduleActiveAreaPercent <= 0) or (moduleActiveAreaPercent > 100):
        moduleActiveAreaPercent = 90  # default in %
    
    
    
    # Sandia Cell Temperature Model
    # each of three factors is a list of two items: The first item is for (mono, poly...) crystalline silicon. The second item is for thin-film modules
    if (newModuleMountType == 0):   # insulated back: (2 x glass/cell/polymer sheet)
        a_customL = [-2.81, -2.81]
        b_customL = [-0.0455, -0.0455]
        deltaT_customL = [0, 0]
    elif (newModuleMountType == 1):   # close roof mount: (2 x glass/cell/glass)
        a_customL = [-2.98, -2.98]
        b_customL = [-0.0471, -0.0471]
        deltaT_customL = [1, 1]
    elif (newModuleMountType == 2):   # open rack: (glass/cell/polymer sheet, polymer/thin-film/steel)
        a_customL = [-3.56, -3.58]
        b_customL = [-0.0750, -0.113]
        deltaT_customL = [3, 3]
    
    
    
    with open(modulesLibraryFile_filePath) as modulesCSVFile:
        moduleNameL = []
        materialL = []
        moduleAreaML = []
        sourceL = []
        Vmp_refL = []
        Imp_refL = []
        Voc_refL = []
        Isc_refL = []
        alpha_sc_refL = []
        beta_oc_refL = []
        beta_mp_refL = []
        mu_betampL = []
        sL = []
        nL = []
        FdL = []
        a0L = []
        a1L = []
        a2L = []
        a3L = []
        a4L = []
        b0L = []
        b1L = []
        b2L = []
        b3L = []
        b4L = []
        b5L = []
        C0L = []
        C1L = []
        C2L = []
        C3L = []
        a_libraryL = []
        b_libraryL = []
        deltaT_libraryL = []
        mountType_libraryL = []
        nameplateDCpowerRating_mL = []
        moduleEfficiencyL = []
        
        lines = modulesCSVFile.readlines()
        for lineIndex, line in enumerate(lines):
            itemsPerLine = line.strip().split(",")
            if (lineIndex >= 3):
                # lineIndex = 0,1,2 are column names, units, script variables names
                moduleName = itemsPerLine[0]  # "Name" from .csv file
                material = itemsPerLine[3]  # "Material" from .csv file
                moduleAreaM = float(itemsPerLine[2])  # "Area" from .csv file. The total area of the module, including spaces between cells and the frame!! (this information comes from SAM 2013 help file)
                #if material in ["c-Si", "mono-Si", "mc-Si", "multi-Si", "EFG mc-Si",   "Si-Film", "HIT Si"]:  # only use mono and multi crystalline photovoltaics
                #if True:
                if not "Concentrator" in moduleName:
                    source = itemsPerLine[42]  # "Notes" from .csv file
                    Vmp_ref = float(itemsPerLine[9])  # "Vmpo" from .csv file (reference Max Power Voltage)
                    Imp_ref = float(itemsPerLine[8])  # "Impo" from .csv file (reference Max Power Current)
                    Voc_ref = float(itemsPerLine[7])  # "Voco" from .csv file (reference Open Circuit Voltage)
                    Isc_ref = float(itemsPerLine[6])  # "Isco" from .csv file (reference Short Circuit Current)
                    alpha_sc_ref = float(itemsPerLine[10])  # "Aisc" from .csv file (short circuit temperature coefficient)
                    beta_oc_ref = float(itemsPerLine[14])  # "Bvoco" from .csv file (open circuit temperature coefficient)
                    beta_mp_ref = float(itemsPerLine[16])  # "Bvmpo" from .csv file (maximum power voltage temperature coefficient)
                    
                    gamma_mp_ref_percentPerDegree = float(itemsPerLine[11])*1000  #  "Aimp" from .csv file (maximum power temperature coefficient in promile fraction??). It is not used for Sandia Module Model!!
                    
                    mu_betamp = float(itemsPerLine[17])  # "Mbvmp" from .csv file (relates "beta_mp_ref" to effective irradiance)
                    s = float(itemsPerLine[4])  # "Cells in Series" from .csv file (number of cells in series)
                    n = float(itemsPerLine[18])  # "N" from .csv file (diode factor)
                    Fd = float(itemsPerLine[33])  # "FD" from .csv file (fraction of diffuse irradiance used by module)
                    # air mass coefficients
                    a0 = float(itemsPerLine[21])
                    a1 = float(itemsPerLine[22])
                    a2 = float(itemsPerLine[23])
                    a3 = float(itemsPerLine[24])
                    a4 = float(itemsPerLine[25])
                    # incidence angle modifier coefficients
                    b0 = float(itemsPerLine[26])
                    b1 = float(itemsPerLine[27])
                    b2 = float(itemsPerLine[28])
                    b3 = float(itemsPerLine[29])
                    b4 = float(itemsPerLine[30])
                    b5 = float(itemsPerLine[31])
                    C0 = float(itemsPerLine[12])
                    C1 = float(itemsPerLine[13])
                    C2 = float(itemsPerLine[19])
                    C3 = float(itemsPerLine[20])
                    
                    a_library = float(itemsPerLine[34])
                    b_library = float(itemsPerLine[35])
                    deltaT_library = float(itemsPerLine[32])
                    
                    if (deltaT_library > 1): mountType_library = 2  # deltaT = 2 or 3 (open rack)
                    elif (deltaT_library == 1): mountType_library = 1  # deltaT = 1 (close (flush) roof mount)
                    elif (deltaT_library < 1): mountType_library = 0  # deltaT = 0 (insulated back)
                    
                    nameplateDCpowerRating_m = round( Imp_ref * Vmp_ref ,2)  # Power at maximum-power point of a single module, in W
                    moduleEfficiency = round( (Imp_ref * Vmp_ref) / (1000 * moduleAreaM * (moduleActiveAreaPercent/100))  * 100 ,2)  # in percent
                    
                    # add to lists
                    moduleNameL.append(moduleName)
                    materialL.append(material)
                    moduleAreaML.append(moduleAreaM)
                    sourceL.append(source)
                    Vmp_refL.append(Vmp_ref)
                    Imp_refL.append(Imp_ref)
                    Voc_refL.append(Voc_ref)
                    Isc_refL.append(Isc_ref)
                    alpha_sc_refL.append(alpha_sc_ref)
                    beta_oc_refL.append(beta_oc_ref)
                    beta_mp_refL.append(beta_mp_ref)
                    mu_betampL.append(mu_betamp)
                    sL.append(s)
                    nL.append(n)
                    FdL.append(Fd)
                    a0L.append(a0)
                    a1L.append(a1)
                    a2L.append(a2)
                    a3L.append(a3)
                    a4L.append(a4)
                    b0L.append(b0)
                    b1L.append(b1)
                    b2L.append(b2)
                    b3L.append(b3)
                    b4L.append(b4)
                    b5L.append(b5)
                    C0L.append(C0)
                    C1L.append(C1)
                    C2L.append(C2)
                    C3L.append(C3)
                    a_libraryL.append(a_library)
                    b_libraryL.append(b_library)
                    deltaT_libraryL.append(deltaT_library)
                    mountType_libraryL.append(mountType_library)
                    nameplateDCpowerRating_mL.append(nameplateDCpowerRating_m)
                    moduleEfficiencyL.append(moduleEfficiency)
    modulesCSVFile.close()
    
    
    if (moduleIndex > (len(moduleNameL)-1)):
        moduleName = moduleMaterial = moduleMountType = moduleArea = nameplateDCpowerRating_m = moduleEfficiency = sourceNotes = PVmoduleSettings = None
        validInputData = False
        printMsg = "\"moduleIndex_\" input is higher than the number of modules from the \"_modulesLibraryFile\" file.\n" + \
                   "Use \"moduleIndex_\" input from 0 to %s." % (len(moduleNameL)-1)
        return moduleNameL, moduleName, moduleMaterial, moduleMountType, moduleArea, nameplateDCpowerRating_m, moduleEfficiency, sourceNotes, PVmoduleSettings, validInputData, printMsg
    
    
    # if NOTHING added to "newModuleMountType_" input: use a,b,deltaT values from the .csv file
    # if something added to "newModuleMountType_" input: use predefined a,b,deltaT values based on this input.
    if (newModuleMountType == None):
        # NOTHING inputted to "newModuleMountType_" input
        a_final = a_libraryL[moduleIndex]
        b_final = b_libraryL[moduleIndex]
        deltaT_final = deltaT_libraryL[moduleIndex]
        moduleMountType = mountType_libraryL[moduleIndex]
    else:
        # something added to "newModuleMountType_" input
        if materialL[moduleIndex] in ["c-Si", "mono-Si", "mc-Si", "multi-Si", "EFG mc-Si",   "Si-Film", "HIT Si"]:  # mono and multi crystalline photovoltaics
            PVtype = 0  # crystalline photovoltaics
        else:
            PVtype = 1  # thin film
        
        a_final = a_customL[PVtype]
        b_final = b_customL[PVtype]
        deltaT_final = deltaT_customL[PVtype]
        moduleMountType = newModuleMountType
        
        if (PVtype == 1) and (newModuleMountType != 2):
            PVmoduleSettings = []
            validInputData = False
            printMsg = "When thin-film module is chosen through \"moduleIndex_\", then \"newModuleMountType_\" input can only be set to \"2\".\n" + \
                       "-\n" + \
                       "This means that thin-film's custom mounting configuration can only be set to Open rack.\n" + \
                       "If you do not wish to use an Open rack thin-film module, then either:\n" + \
                       "a) do not add anything to \"newModuleMountType_\" input, in which case you will be using the default mounting configuration of that module (check the \"moduleMountType\" output), or\n" + \
                       "b) do not add anything to \"newModuleMountType_\" input and choose another module (through \"moduleIndex_\" input) which may have different default mounting configuration."
            return moduleNameL, moduleNameL[moduleIndex], materialL[moduleIndex], moduleMountType, moduleAreaML[moduleIndex], nameplateDCpowerRating_mL[moduleIndex], moduleEfficiencyL[moduleIndex], sourceL[moduleIndex], PVmoduleSettings, validInputData, printMsg
    
    
    PVmoduleSettings = [
    moduleNameL[moduleIndex],
    materialL[moduleIndex],
    moduleMountType,
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
    beta_mp_refL[moduleIndex],
    mu_betampL[moduleIndex],
    sL[moduleIndex],
    nL[moduleIndex],
    FdL[moduleIndex],
    a0L[moduleIndex],
    a1L[moduleIndex],
    a2L[moduleIndex],
    a3L[moduleIndex],
    a4L[moduleIndex],
    b0L[moduleIndex],
    b1L[moduleIndex],
    b2L[moduleIndex],
    b3L[moduleIndex],
    b4L[moduleIndex],
    b5L[moduleIndex],
    C0L[moduleIndex],
    C1L[moduleIndex],
    C2L[moduleIndex],
    C3L[moduleIndex],
    a_final,
    b_final,
    deltaT_final]
    
    nameplateDCpowerRating_m = nameplateDCpowerRating_mL[moduleIndex]  # in W
    moduleEfficiency = moduleEfficiencyL[moduleIndex]  # in percent
    
    ####print "len(moduleNameL): ", len(moduleNameL)
    # deleting
    del modulesLibraryFile_filePath; del modulesCSVFile; del lines
    "del sourceL"; "del moduleAreaML"; "del materialL"; del Vmp_refL; del Imp_refL; del Voc_refL; del Isc_refL; del FdL; del alpha_sc_refL; del beta_oc_refL; del beta_mp_refL; del mu_betampL; del nL; del sL; del a0L; del a1L; del a2L; del a3L; del a4L; del b0L; del b1L; del b2L; del b3L; del b4L; del b5L; del C0L; del C1L; del C2L; del C3L; del a_libraryL; del b_libraryL; del deltaT_libraryL; del nameplateDCpowerRating_mL; "del moduleEfficiencyL"
    
    # printing
    resultsCompletedMsg = "Import Sandia photovoltaics module component results successfully completed!"
    printOutputMsg = \
    """
Input data:,

Module Name:  %s,
Module Material:  %s,
Module Area (m2):  %s,
Module Active Area Percent (perc.):  %s,

New Module Mount type:  %s,
Default Module Mount type:  %s,

Power at Max Power (W):  %s,
Module Efficiency (perc.):  %s,
Reference Max Power Voltage (V):  %s,
Reference Max Power Current (A):  %s,
Reference Open Circuit Voltage (V):  %s,
Reference Short Circuit Current (A):  %s,
Short circuit temperature coefficient:  %s,
Open circuit temperature coefficient:  %s,
Maximum power voltage temperature coefficient:  %s,
Relates Maximum power voltage temperature coefficient to Effective irradiance:  %s,

Number of cells in series:  %s,
Diode factor:  %s,
Fraction of diffuse irradiance used by module:  %s,

Air mass coefficient 0:  %s,
Air mass coefficient 1:  %s,
Air mass coefficient 2:  %s,
Air mass coefficient 3:  %s,
Air mass coefficient 4:  %s,
Incidence angle modifier coefficient 0:  %s,
Incidence angle modifier coefficient 1:  %s,
Incidence angle modifier coefficient 2:  %s,
Incidence angle modifier coefficient 3:  %s,
Incidence angle modifier coefficient 4:  %s,
Incidence angle modifier coefficient 5:  %s,
Coefficients relating Reference Max Power Current to Effective irradiance 0:  %s,
Coefficients relating Reference Max Power Current to Effective irradiance 1:  %s,
Coefficients relating Reference Max Power Voltage to Effective irradiance 0:  %s,
Coefficients relating Reference Max Power Voltage to Effective irradiance 1:  %s,

Upper limit coefficient for module temperature at low wind speeds and high solar irradiance:  %s,
Coefficient for rate at which module temperature drops as wind speed increases:  %s,
Temperature difference between the cell and the module back surface:  %s,
    """ % (PVmoduleSettings[0], PVmoduleSettings[1], PVmoduleSettings[3], PVmoduleSettings[4],
    newModuleMountType, mountType_libraryL[moduleIndex], 
    PVmoduleSettings[5], PVmoduleSettings[6], PVmoduleSettings[7], PVmoduleSettings[8], PVmoduleSettings[9], PVmoduleSettings[10], PVmoduleSettings[11], PVmoduleSettings[12], PVmoduleSettings[13], PVmoduleSettings[14],
    PVmoduleSettings[15], PVmoduleSettings[16], PVmoduleSettings[17],
    PVmoduleSettings[18], PVmoduleSettings[19], PVmoduleSettings[20], PVmoduleSettings[21], PVmoduleSettings[22],
    PVmoduleSettings[23], PVmoduleSettings[24], PVmoduleSettings[25], PVmoduleSettings[26], PVmoduleSettings[27], PVmoduleSettings[28],
    PVmoduleSettings[29], PVmoduleSettings[30], PVmoduleSettings[31], PVmoduleSettings[32],
    PVmoduleSettings[33], PVmoduleSettings[34], PVmoduleSettings[35])
    print resultsCompletedMsg
    print printOutputMsg
    
    
    validInputData = True
    printMsg = "ok"
    
    """
    # testing
    print "-------"
    print "moduleName: ", moduleNameL[moduleIndex], "_", PVmoduleSettings[0]
    print "material: ", materialL[moduleIndex], "_", PVmoduleSettings[1]
    print "final moduleMountType: ", moduleMountType, "_", PVmoduleSettings[2]
    print "moduleAreaM: ", moduleAreaML[moduleIndex], "_", PVmoduleSettings[3]
    print "moduleActiveAreaPercent: ", moduleActiveAreaPercent, "_", PVmoduleSettings[4]
    print "nameplateDCpowerRating: ", nameplateDCpowerRating_mL[moduleIndex], "_", PVmoduleSettings[5]
    print "moduleEfficiency: ", moduleEfficiencyL[moduleIndex], "_", PVmoduleSettings[6]
    print "Vmp_ref: ", Vmp_refL[moduleIndex], "_", PVmoduleSettings[7]
    print "Imp_ref: ", Imp_refL[moduleIndex], "_", PVmoduleSettings[8]
    print "Voc_ref: ", Voc_refL[moduleIndex], "_", PVmoduleSettings[9]
    print "Isc_ref: ", Isc_refL[moduleIndex], "_", PVmoduleSettings[10]
    print "alpha_sc_ref: ", alpha_sc_refL[moduleIndex], "_", PVmoduleSettings[11]
    print "beta_oc_ref: ", beta_oc_refL[moduleIndex], "_", PVmoduleSettings[12]
    print "beta_mp_ref: ", beta_mp_refL[moduleIndex], "_", PVmoduleSettings[13]
    print "mu_betamp: ", mu_betampL[moduleIndex], "_", PVmoduleSettings[14]
    print " "
    print "s: ", sL[moduleIndex], "_", PVmoduleSettings[15]
    print "n: ", nL[moduleIndex], "_", PVmoduleSettings[16]
    print "Fd: ", FdL[moduleIndex], "_", PVmoduleSettings[17]
    print " "
    print "a0: ", a0L[moduleIndex], "_", PVmoduleSettings[18]
    print "a1: ", a1L[moduleIndex], "_", PVmoduleSettings[19]
    print "a2: ", a2L[moduleIndex], "_", PVmoduleSettings[20]
    print "a3: ", a3L[moduleIndex], "_", PVmoduleSettings[21]
    print "a4: ", a4L[moduleIndex], "_", PVmoduleSettings[22]
    print "b0: ", b0L[moduleIndex], "_", PVmoduleSettings[23]
    print "b1: ", b1L[moduleIndex], "_", PVmoduleSettings[24]
    print "b2: ", b2L[moduleIndex], "_", PVmoduleSettings[25]
    print "b3: ", b3L[moduleIndex], "_", PVmoduleSettings[26]
    print "b4: ", b4L[moduleIndex], "_", PVmoduleSettings[27]
    print "b5: ", b5L[moduleIndex], "_", PVmoduleSettings[28]
    print "C0: ", C0L[moduleIndex], "_", PVmoduleSettings[29]
    print "C1: ", C1L[moduleIndex], "_", PVmoduleSettings[30]
    print "C2: ", C2L[moduleIndex], "_", PVmoduleSettings[31]
    print "C3: ", C3L[moduleIndex], "_", PVmoduleSettings[32]
    print " "
    print "a: ", a_libraryL[moduleIndex], "_", PVmoduleSettings[33], "      _ may be different if something added to \"newModuleMountType_\" input"
    print "b: ", b_libraryL[moduleIndex], "_", PVmoduleSettings[34], "      _ may be different if something added to \"newModuleMountType_\" input"
    print "deltaT: ", deltaT_libraryL[moduleIndex], "_", PVmoduleSettings[35], "      _ may be different if something added to \"newModuleMountType_\" input"
    """
    return moduleNameL, moduleNameL[moduleIndex], materialL[moduleIndex], moduleMountType, moduleAreaML[moduleIndex], nameplateDCpowerRating_m, moduleEfficiencyL[moduleIndex], sourceL[moduleIndex], PVmoduleSettings, validInputData, printMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        
        allModuleNames, moduleName, moduleMaterial, moduleMountType, moduleArea, modulePower, moduleEfficiency, sourceNotes, PVmoduleSettings, validInputData, printMsg = main(_modulesLibraryFile, moduleIndex_, newModuleMountType_, moduleActiveAreaPercent_)
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
