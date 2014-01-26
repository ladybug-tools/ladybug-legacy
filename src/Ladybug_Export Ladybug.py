# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component exports Ladybug/Honeybee components source code and create/update the userObjects
Thanks to Giulio Piacentino for a really helpful example
-
Provided by Ladybug 0.0.53
    
    Args:
        _components: Output of a series of Ladybug component or * to search all the components on canvas
        _targetFolder: A local folder. Source code will be saved at .\src and userObjects will be saved at .\userObjects
        _export: Set Boolean to True to export Ladybug to destination folder
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Ladybug_Export Ladybug"
ghenv.Component.NickName = 'exportLadybug'
ghenv.Component.Message = 'VER 0.0.53\nJan_25_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | Developers"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import Grasshopper.Kernel as gh
import scriptcontext as sc
import shutil
import os
import uuid

UOFolder = "C:\\Users\\" + os.getenv("USERNAME") + "\\AppData\\Roaming\\Grasshopper\\UserObjects\\"
cs = gh.GH_ComponentServer()

#gh.GH_ComponentServer

exposureDict = {0 : ghenv.Component.Exposure.dropdown,
                1 : ghenv.Component.Exposure.primary,
                2 : ghenv.Component.Exposure.secondary,
                3 : ghenv.Component.Exposure.tertiary,
                4 : ghenv.Component.Exposure.quarternary,
                5 : ghenv.Component.Exposure.quinary,
                6 : ghenv.Component.Exposure.senary,
                7 : ghenv.Component.Exposure.septenary
                }

def exportToUserObject(component, targetFolder, lb_preparation):
    targetFolder = os.path.join(targetFolder, "userObjects")
    if not os.path.isdir(targetFolder): os.mkdir(targetFolder)
    
    def isNewerVersion(currentUO, component):
        # check if the component has a newer version than the current userObjects
        # version of the connected component
        if component.Message == None: return True
        if len(component.Message.split("\n"))<2: return True
        
        ghVersion, ghDate = component.Message.split("\n")
        ghCompVersion = map(int, ghVersion.split("VER ")[1].split("."))
        month, day, ghYear  = ghDate.split("_")
        # print version, date
        month = lb_preparation.monthList.index(month.upper()) + 1
        ghCompDate = int(lb_preparation.getJD(month, day))
        
        # in case there was no date for the userobject
        # the file will be considered older and will be overwrittern
        ghComponent = currentUO.InstantiateObject()
        # this is not the best way but works for now!
        # should be a better way to compute the component and get the message
        componentCode = ghComponent.Code.split("\n")
        
        UODate = ghCompDate - 1
        # version of the file
        for lineCount, line in enumerate(componentCode):
            if lineCount > 200: break
            if line.strip().startswith("ghenv.Component.Message"):
                #print line
                # print line.split("=")[1].strip().split("\n")
                version, date = line.split("=")[1].strip().split("\\n")
                
                # in case the file doesn't have an standard Ladybug message let it be updated
                try: UOVersion = map(int, version.split("VER ")[1].split("."))
                except: return True
                month, day, UOYear  = date.split("_")
                month = lb_preparation.monthList.index(month.upper()) + 1
                UODate = int(lb_preparation.getJD(month, day))
                break
        
        # check if the version of the code is newer
        try:
            if int(ghYear.strip()) > int(UOYear[:-1].strip()):
                    return True
            elif ghCompDate > UODate:
                return True
            elif ghCompDate == UODate:
                for ghVer, UOVer in zip(UOVersion, UOVersion):
                    if ghVer < UOVer: return False
                return True
            else:
                print "\nThere is a newer userObject in Grasshopper folder that will be copied: " + currentUO.Path + "." + \
                      "\nUserObject version is: " +  version + " " + date + \
                      "\nThe component version is: "  +  ghVersion + " " + ghDate + ".\n"
                
                return False
        except:
            return True
            
    # check if the userObject is already existed in the folder
    try:
        filePath = os.path.join(UOFolder, component.Name + ".ghuser")
        currentUO = gh.GH_UserObject(filePath)
    except:
        # the userobject is not there so just create it
        currentUO = None
 
    if currentUO!=None:
        # if is newer remove
        if isNewerVersion(currentUO, component):
            # it has a newer version so let's remove the old one and creat a new userobject
            pass
            if not component.Category == "Maths":
                removeNicely = cs.RemoveCachedObject(filePath)
                if not removeNicely: os.remove(filePath)
        else:
            # there is already a newer version so just copy that to the folder instead
            # and return
            dstFullPath = os.path.join(targetFolder, component.Name + ".ghuser")
            shutil.copy2(filePath, dstFullPath)
            return
    
    # create the new userObject in Grasshopper folder
    uo = gh.GH_UserObject()
    uo.Icon = component.Icon_24x24
    
    try: uo.Exposure = exposureDict[int(component.AdditionalHelpFromDocStrings)]
    except: uo.Exposure = exposureDict[int(1)]
    
    uo.BaseGuid = component.ComponentGuid
    uo.Description.Name = component.Name
    uo.Description.Description = component.Description
    
    # if user hasn't identified the category then put it into honeybee as an unknown!
    if component.Category == "Maths":
        uo.Description.Category = "Honeybee"
    else:
        uo.Description.Category = component.Category
        
    if component.SubCategory == "Script":
        uo.Description.SubCategory = "UnknownBees"
    else:
        uo.Description.SubCategory = component.SubCategory
    
    uo.CreateDefaultPath(True)
    uo.SetDataFromObject(component)
    uo.SaveToFile()
    
    # copy the component over
    dstFullPath = os.path.join(targetFolder, component.Name + ".ghuser")
    shutil.copy2(filePath, dstFullPath)
    
    gh.GH_ComponentServer.UpdateRibbonUI()
    
    print "UserObject successfully added to: "
    
    

def exportToFile(component, targetFolder, lb_preparation):
    
    targetFolder = os.path.join(targetFolder, "src")
    if not os.path.isdir(targetFolder): os.mkdir(targetFolder)
    
    def isNewerVersion(componentCode, fileName):
        # check if the component has a newer version of source code
        # version of the connected component
        if component.Message == None: return True
        if len(component.Message.split("\n"))<2: return True
        
        ghVersion, ghDate = component.Message.split("\n")
        ghCompVersion = map(int, ghVersion.split("VER ")[1].split("."))
        month, day, ghYear  = ghDate.split("_")
        # print version, date
        month = lb_preparation.monthList.index(month.upper()) + 1
        ghCompDate = int(lb_preparation.getJD(month, day))
        
        # in case there was no date in the file
        # the file will be considered older and will be overwrittern
        # 
        pyFileDate = ghCompDate - 1
        
        # version of the file
        with open(os.path.join(targetFolder,fileName), "r") as pyFile:
            for lineCount, line in enumerate(pyFile):
                if lineCount > 200: break
                if line.strip().startswith("ghenv.Component.Message"):
                    # print line
                    # print line.split("=")[1].strip().split("\n")
                    version, date = line.split("=")[1].strip().split("\\n")
                    try:
                        pyFileVersion = map(int, version.split("VER ")[1].split("."))
                    except:
                        # in case the file doesn't have an standard Ladybug message
                        return True
                    month, day, pyYear  = date.split("_")
                    month = lb_preparation.monthList.index(month.upper()) + 1
                    pyFileDate = int(lb_preparation.getJD(month, day))
                    break
        
        # check if the version of the code is newer
        if int(ghYear.strip()) > int(pyYear[:-1].strip()):
                return True
        elif ghCompDate > pyFileDate:
            return True
        elif ghCompDate == pyFileDate:
            for ghVer, pyVer in zip(ghVersion, pyFileVersion):
                if ghVer < pyVer: return False
            return True
        else:
            print "\nThere is already a newer version in the folder for: " + fileName + "." + \
                  "\nCurrent file version is: " +  version + " " + date + \
                  "\nThe component version is: "  +  ghVersion + " " + ghDate + ".\n"
            
            return False
            
    if component.Name.find("Honeybee")>=0 or component.Name.find("Ladybug")>=0:
        
        fileName = component.Name + ".py"
        
        # code inside the component
        code = component.Code
        
        # check if the file already exist
        if os.path.isfile(os.path.join(targetFolder, fileName)):
            if not isNewerVersion(code, fileName):
                return False
                
        with open(os.path.join(targetFolder, fileName), "w") as pyoutf:
            if isinstance(code, unicode):
                code = code.encode('ascii','ignore').replace("\r", "")
            pyoutf.write(code)
        
        print "Exported " + fileName + " to: " + os.path.join(targetFolder, fileName)
        return True

def getAllTheComponents(onlyGHPython = True):
    components = []
    
    document = ghenv.Component.OnPingDocument()
    
    for component in document.Objects:
        if onlyGHPython and type(component)!= type(ghenv.Component):
            pass
        else:
            components.append(component)
    
    return components

def getListOfConnectedComponents(componentInputParamIndex = 0, onlyGHPython = True):
    # this function is edited version of Guilio's code from here:
    # [github link]
    components = []
    
    param = ghenv.Component.Params.Input[componentInputParamIndex]
    sources = param.Sources
    if sources.Count == 0: return components
    
    for source in sources:
        attr = source.Attributes
        if (attr is None) or (attr.GetTopLevel is None):
            pass
        else:
            component = attr.GetTopLevel.DocObject
    
    if component == None or (onlyGHPython and type(component) != type(ghenv.Component)):
            #collect only python components
            pass
    else:
        components.append(component)
    
    return components

def main(components, targetFolder):
    if not sc.sticky.has_key('ladybug_release'): return "you need to let Ladybug fly first!"
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    if not os.path.isdir(targetFolder): os.mkdir(targetFolder)
        
    if components[0] == "*":
        ghComps = getAllTheComponents()
    else:
        ghComps = getListOfConnectedComponents()
    
    if len(ghComps)== 0: return "Found 0 components!"
    
    for ghComp in ghComps:
        fileExported = exportToFile(ghComp, targetFolder, lb_preparation)
        if fileExported:
            exportToUserObject(ghComp, targetFolder, lb_preparation)
        

if _export and len(_components)!=0 and _targetFolder!=None:
    msg = main(_components, _targetFolder)
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
else:
    print "At the minimum one of the components are missing!"