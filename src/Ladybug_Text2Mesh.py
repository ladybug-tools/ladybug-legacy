import scriptcontext as sc
from System import Object

from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

ghenv.Component.Name = "Ladybug_Text2Mesh"
ghenv.Component.NickName = 'Text2Mesh'
ghenv.Component.Message = 'VER 0.0.63\n10_20_2016'
ghenv.Component.Category = "Ladybug"
#ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
ghenv.Component.SubCategory = "7 | WIP"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

lb_visualization = sc.sticky["ladybug_ResultVisualization"]()

font = "Verdana";
textSize= size;
zoneTextLabels= lb_visualization.text2srf(text, pts, font, textSize)

brepTxtLabels = DataTree[Object]()
for listCount, lists in enumerate(zoneTextLabels):
    for item in lists:
        brepTxtLabels.Add(item, GH_Path(listCount))

Text =brepTxtLabels