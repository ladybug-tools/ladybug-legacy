# This is a simple script that export view field angles as a list
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Set up the parameters for view study
-
Provided by Ladybug 0.0.35
    
    Args:
        viewField1: Main view field angle
        viewField2: Secondary view field angle
    Returns:
        report: Report!!!
        vField: View field parameters
"""

ghenv.Component.Name = "Ladybug_View Study Parameters"
ghenv.Component.NickName = 'viewStudyPar'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'


from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

def viewFStr(viewField1, viewField2):
    try: viewField1 = float(viewField1)
    except: pass
    try: viewField2 = float(viewField2)
    except: pass
    # check the numbers
    if viewField1 +viewField2 > 90:
        print "Sum of viewFileds cannot be more than 90 degrees."
        w = gh.GH_RuntimeMessageLevel.Error
        ghenv.Component.AddRuntimeMessage(w, "Sum of viewFileds cannot be more than 90 degrees.")
        return
    else: 
        return viewField1, viewField2

if viewField1 and viewField2:
    vField = viewFStr(viewField1, viewField2)
else:
    print "Please provide both viewField1 and viewField2."
    ww = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(ww, "Please provide both viewField1 and viewField2.")