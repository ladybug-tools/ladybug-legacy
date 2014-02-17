# This component separates numbers and strings from an input list
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Separates numbers from strings
-
Provided by Ladybug 0.0.54
    
    Args:
        _inputList: List of input data
    Returns:
        numbers: List of numbers
        strings: List of strings
"""

ghenv.Component.Name = "Ladybug_Separate data"
ghenv.Component.NickName = 'separateData'
ghenv.Component.Message = 'VER 0.0.54\nFEB_16_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

num = []
str = []
lastOne = None

strPath = 0
numPath = 0

numbers = DataTree[Object]()
strings = DataTree[Object]()

for item in _inputList:
    try:
        item = float(item)
        if lastOne == None: lastOne = "float"
        if lastOne!= "float":
            lastOne = "float"
            numPath += 1
        p = GH_Path(numPath)
        numbers.Add(item, p)
    except:
        if lastOne == None: lastOne = "str"
        if lastOne!= "str":
            lastOne = "str"
            strPath += 1
        p = GH_Path(strPath)
        strings.Add(item, p)
