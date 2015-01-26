# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

#Wh to BTU
"""
Use this component to convert energy values in Wh to BTU or Wh/m2 to BTU/ft2.
-
Provided by Ladybug 0.0.58
    
    Args:
        _Wh: An energy value or list of energy values in Wh or Wh/m2.  Note that, for the component to recognize flux or floor normalization, the input must have a Ladybug header.
    Returns:
        BTU: The input enervy values converted to BTU.
"""

ghenv.Component.Name = "Ladybug_Wh2BTU"
ghenv.Component.NickName = 'Wh2BTU'
ghenv.Component.Message = 'VER 0.0.58\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

floorNorm = False
BTU = []
for num in _Wh:
    if num == 'Wh/m2':
        BTU.append('BTU/ft2')
        floorNorm = True
    elif num == 'Wh':
        BTU.append('BTU')
        floorNorm = False
    elif num == 'kWh':
        BTU.append('kBTU')
        floorNorm = False
    elif num == 'kWh/m2':
        BTU.append('kBTU/ft2')
        floorNorm = True
    else:
        if floorNorm == True:
            try: BTU.append(float(num)/0.316998331)
            except: BTU.append(num)
        else:
            try: BTU.append(float(num)/3.41214163)
            except: BTU.append(num)
