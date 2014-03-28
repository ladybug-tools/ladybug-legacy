# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

#F to C
"""
Use this component to convert temperatures from Fahrenheit to Celcius.
-
Provided by Ladybug 0.0.57
    
    Args:
        _F: A temperature or list of temperatures in Fahrenheit.
    Returns:
        C: The input temperatures converted to Celcius.
"""

ghenv.Component.Name = "Ladybug_F2C"
ghenv.Component.NickName = 'F2C'
ghenv.Component.Message = 'VER 0.0.57\nMAR_26_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


C = []
for num in _F:
    if num == 'F': F.append('C')
    else:
        try: C.append((float(num)-32) * 5 / 9)
        except: C.append(num)
