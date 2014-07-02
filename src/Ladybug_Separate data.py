# This component separates numbers and strings from an input list
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to separate the text strings from the numbers in the climate data streams output from the Import EPW component.
You can then perform mathamatical functions on the numerical climate data using the Grasshopper math components or quickly preview the numerical data stream using the Grasshopper "Quick Graph" component.
This component can also be used generally to separate any data stream that contains both numbers and text strings.
-
Provided by Ladybug 0.0.57
    
    Args:
        _inputList: A list of data that contains both text srtings and numbers.  For example, a data stream output from the Import EPW component.
    Returns:
        numbers: The numbers from in the _inputList data.  Note that the order of numbers in this list is the same as the _inputList.
        strings: The text strings from in the _inputList data.  Note that the order of text strings in this list is the same as the _inputList.
"""

ghenv.Component.Name = "Ladybug_Separate data"
ghenv.Component.NickName = 'separateData'
ghenv.Component.Message = 'VER 0.0.57\nJUL_01_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


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
