# This is a simple script that export orintation study parameters as a string
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component with the Ladybug "Radiation Analysis", "Sunlight Hours Analysis", or "View Analysis" component to set up the parameters for an Orientation Study.
You can use an Orientation Study to answer questions like "What orientation of my building will give me the highest or lowest radiation gain for my analysis period?"
Another question might be "What direction should I orient my static solar panel to get the maximum radiation during my analysis period?"
An Orientation Study will automatically rotate your geometry around several times based on the inputs made to this component and the results will be recorded in the corresponding Analysis component that this one is hooked up to.



-
Provided by Ladybug 0.0.58
    
    Args:
        _divisionAngle: A number between 0 and 180 that represents the degrees to rotate the geometry for each step of the Orientation Study.
        _totalAngle: A number between 0 and 360 that represents the degrees of the total rotation that the geometry will undergo over the course of the Orientation Study. This _totalAngle should be larger than the _divisionAngle and divisible by the _divisionAngle.
        basePoint_: Input a point here to change the center about which the Orientation Study will rotate the geometry. If no point is connected, the default point of rotation will be the center of the test geometry.
        rotateContext_: Input either a Boolean value or a set of context Breps that should be rotated along with the test geometry. If set this input to "True", all context Breps will be rotated with the test geometry.  The default is set to "False" to only rotate the test geometry.
        runTheStudy: Set to "True" to run the Orientation Study.  Note that both this input and the "_runIt" input of the corresponding Analysis component must be set to "True" for the Orientation Study to run.
                     Since an Orientation Study can take a long time, this extra confirmation request is included here to make sure that you really want to run an Oriantation Study before you end up waiting a long time.
    Returns:
        orientationStudyPar: A list of Orientation Study parameters that can be plugged into the Ladybug "Radiation Analysis", "Sunlight Hours Analysis", or "View Analysis" component.
"""

ghenv.Component.Name = "Ladybug_Orientation Study Parameters"
ghenv.Component.NickName = 'orientationStudyPar'
ghenv.Component.Message = 'VER 0.0.58\nAUG_20_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

def orientaionStr(divisionAngle, totalAngle):
    divisionAngle = float(divisionAngle)
    totalAngle = float(totalAngle)
    # check the numbers
    if divisionAngle> totalAngle:
        print "Division angle cannot be bigger than the total angle!"
        w = gh.GH_RuntimeMessageLevel.Error
        ghenv.Component.AddRuntimeMessage(w, "Division angle cannot be bigger than the total angle!")
        return 0
    elif totalAngle%divisionAngle!=0:
        print "Total angle should be divisible by the division angle!"
        w = gh.GH_RuntimeMessageLevel.Error
        ghenv.Component.AddRuntimeMessage(w, "Total angle should be divisible by the division angle!")
        return 0
    else:
        return [0] + rs.frange(0, totalAngle, divisionAngle)


# import the classes
def main(_divisionAngle, _totalAngle, basePoint_, rotateContext_, _runTheStudy):
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
            return
            
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        if rotateContext_==[] or rotateContext_[0]==False: rotateContext_ = False
        elif rotateContext_[0]==True: rotateContext_ = True
        else:
            # just carry the geometries to next component
            contextMesh, contextBrep = lb_preparation.cleanAndCoerceList(rotateContext_)
            rotateContext_ = contextMesh, contextBrep
        
        if not _runTheStudy!=None: _runTheStudy = False
        # if not basePoint!=None: basePoint = rc.Geometry.Point3d(0,0,0)
        if (_divisionAngle and _totalAngle):
            if orientaionStr(_divisionAngle, _totalAngle)!=0:
                orientationStudyPar = _runTheStudy, rotateContext_, basePoint_, orientaionStr(_divisionAngle, _totalAngle)
                return orientationStudyPar
        elif _divisionAngle == None and _totalAngle ==None:
            print "Please provide both a _divisionAngle and a _totalAngle."
        else:
            print "Either the _divisionAngle or the _totalAngle is missing."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Either the _divisionAngle or the _totalAngle is missing.")
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")


orientationStudyPar = main(_divisionAngle, _totalAngle, basePoint_, rotateContext_, _runTheStudy)
ghenv.Component.Params.Output[0].Hidden = True
