# This component separates numbers and strings from an input list
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Separates numbers from strings
-
Provided by Ladybug 0.0.35
    
    Args:
        inputList: List of input data
    Returns:
        report: Report!!!
        numbers: List of numbers
        strings: List of strings
"""

ghenv.Component.Name = "Ladybug_Separate data"
ghenv.Component.NickName = 'separateData'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'


num = []
str = []

for item in inputList:
    try: num.append(float(item))
    except: str.append(item)

numbers = num
strings = str