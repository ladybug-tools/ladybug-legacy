# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to generate lists of shading depths, numbers of shades, horizontal or vertical values, and shade angles for different cardinal directions to be plugged into the _depthOrVector, _numOfShds, _horOrVertical_, and _shdAngle_ inputs of the "ShadingDesigner" component.

-
Provided by Ladybug 0.0.52

    Args:
        _northDepth: Shading depth for north-facing glazing.
        _westDepth: Shading depth for west-facing glazing.
        _southDepth: Shading depth for south-facing glazing.
        _eastDepth: Shading depth for east-facing glazing.
        --------------------: ...
        _northNumOfShds: Number of shades to be generated for north-facing glazing.
        _westNumOfShds: Number of shades to be generated for west-facing glazing.
        _southNumOfShds: Number of shades to be generated for south-facing glazing.
        _eastNumOfShds: Number of shades to be generated for east-facing glazing.
        -------------------: ...
        _northHorOrVert_: Set to "True" to generate horizontal overhangs for north-facing glazing or set to "False" to generate vertical fins.
        _westHorOrVert_: Set to "True" to generate horizontal overhangs for west-facing glazing or set to "False" to generate vertical fins.
        _southHorOrVert_: Set to "True" to generate horizontal overhangs for south-facing glazing or set to "False" to generate vertical fins.
        _eastHorOrVert: Set to "True" to generate horizontal overhangs for east-facing glazing or set to "False" to generate vertical fins.
        ------------------: ...
        _northShdAngle_: If you have vertical shades, use this to rotate them towards the South by a certain value in degrees (negative values here on the north input will rotate shades to the North and be particularly helpful in blocking out early morning or late afternoon summer sun).  If you have horizontal shades on the north side, use this to angle shades downward, as in some versions of the brise soleil.
        _westShdAngle_: If you have vertical shades, use this to rotate them towards the South by a certain value in degrees, which, if applied positively here in the west direction, will let in more winter afternoon sun and block summer afternoon sun.  If you have horizontal shades, use this to angle shades downward, as in some versions of the brise soleil.
        _southShdAngle_: If you have horizontal shades, use this to angle shades downward, as in some versions of the brise soleil. If you have vertical shades, use this to rotate them further towards the South by a certain value in degrees.
        _eastShdAngle_: If you have vertical shades, use this to rotate them towards the South by a certain value in degrees, which, if applied positively here in the east direction, will let in more winter morning sun and block summer morning sun.  If you have horizontal shades, use this to angle shades downward, as in some versions of the brise soleil.
    Returns:
        readMe!: ...
        _depthList: A list of shade depths for different cardinal directions to be plugged into the _depthOrVector input of the "ShadingDesigner" component.
        _numOfShdsList: A list of numbers of shades for different cardinal directions to be plugged into the _numOfShds input of the "ShadingDesigner" component. 
        _horOrVertList_: A list of horizontal or vertical values for different cardinal directions to be plugged into the _horOrVertical_ input of the "ShadingDesigner" component.
        _shdAngleList_: A list of shade angles for different cardinal directions to be plugged into the _shdAngle_ input of the "ShadingDesigner" component. 
"""
ghenv.Component.Name = "Ladybug_Shading Parameters List"
ghenv.Component.NickName = 'shdParamList'
ghenv.Component.Message = 'VER 0.0.53\nJan_22_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import scriptcontext as sc

def giveWarning(message):
    print message
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, message)
        
def checkDepth(depth):
    if depth == None: return 0
    elif depth < sc.doc.ModelAbsoluteTolerance:
        giveWarning("Please put in shade depth values that are above your model's tolerance.")
        return 0
    else: return depth
    
northDepth = checkDepth(_northDepth)
westDepth = checkDepth(_westDepth)
southDepth = checkDepth(_southDepth)
eastDepth = checkDepth(_eastDepth)

def checkNumOfShds(numOfShds):
    if numOfShds == None: return 0
    elif numOfShds < 0:
        giveWarning("Please put in a positive value for the numOfShds.")
        return 0
    elif str(numOfShds-int(numOfShds))[1] != 0:
        giveWarning("Decimal value input for numOfShds. NumOfShds rounded to the nearest interger.")
        return int(numOfShds)
    else: return numOfShds

northNumOfShds = checkNumOfShds(_northNumOfShds)
westNumOfShds = checkNumOfShds(_westNumOfShds)
southNumOfShds = checkNumOfShds(_southNumOfShds)
eastNumOfShds = checkNumOfShds(_eastNumOfShds)

def checkHorOrVert(horOrVert):
    if horOrVert == None: return True
    else: return horOrVert

northHorOrVert = checkHorOrVert(_northHorOrVert_)
westHorOrVert = checkHorOrVert(_westHorOrVert_)
southHorOrVert = checkHorOrVert(_southHorOrVert_)
eastHorOrVert = checkHorOrVert(_eastHorOrVert_)

def checkShdAngle(shdAngle):
    if shdAngle == None: return 0
    elif shdAngle > 90 or shdAngle < -90:
        giveWarning("Please put in a value for shdAngle that is less than 90 degrees or greater than -90 degrees.")
        return 0
    else: return shdAngle

northShdAngle = checkShdAngle(_northShdAngle_)
westShdAngle = checkShdAngle(_westShdAngle_)
southShdAngle = checkShdAngle(_southShdAngle_)
eastShdAngle = checkShdAngle(_eastShdAngle_)



_depthList = northDepth, westDepth, southDepth, eastDepth
_numOfShdsList = northNumOfShds, westNumOfShds, southNumOfShds, eastNumOfShds
_horOrVertList_ = northHorOrVert, westHorOrVert, southHorOrVert, eastHorOrVert
_shdAngleList_ = northShdAngle, westShdAngle, southShdAngle, eastShdAngle