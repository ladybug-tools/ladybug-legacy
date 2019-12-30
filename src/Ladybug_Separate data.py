# This component separates numbers and strings from an input list
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to separate the text strings from the numbers in the climate data streams output from the Import EPW component.
You can then perform mathamatical functions on the numerical climate data using the Grasshopper math components or quickly preview the numerical data stream using the Grasshopper "Quick Graph" component.
This component can also be used generally to separate any data stream that contains both numbers and text strings.
-
Provided by Ladybug 0.0.68
    
    Args:
        _inputList: A list of data that contains both text srtings and numbers.  For example, a data stream output from the Import EPW component.
    Returns:
        numbers: The numbers from in the _inputList data.  Note that the order of numbers in this list is the same as the _inputList.
        strings: The text strings from in the _inputList data.  Note that the order of text strings in this list is the same as the _inputList.
"""

ghenv.Component.Name = "Ladybug_Separate data"
ghenv.Component.NickName = 'strNum'
ghenv.Component.Message = 'VER 0.0.68\nJAN_01_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
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

for count, item in enumerate(_inputList):
    try:
        item = float(item)
        if count == 0: numfirst = True
        if lastOne == None: lastOne = "float"
        if lastOne!= "float":
            lastOne = "float"
            numPath += 1
        if numfirst == False:
            p = GH_Path(numPath-1)
            numbers.Add(item, p)
        else:
            p = GH_Path(numPath)
            numbers.Add(item, p)
    except:
        if count == 0: numfirst = False
        if lastOne == None: lastOne = "str"
        if lastOne!= "str":
            lastOne = "str"
            strPath += 1
        if numfirst == True:
            p = GH_Path(strPath-1)
            strings.Add(item, p)
        else:
            p = GH_Path(strPath)
            strings.Add(item, p)
