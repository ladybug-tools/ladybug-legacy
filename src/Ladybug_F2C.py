# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

#F to C
"""
Convert from F to C 
-
Provided by Ladybug 0.0.54
    
    Args:
        _F: Input temperatures in F
    Returns:
        C: Output temperatures in C
"""

ghenv.Component.Name = "Ladybug_F2C"
ghenv.Component.NickName = 'F2C'
ghenv.Component.Message = 'VER 0.0.54\nFEB_16_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "4"

C = []
for num in _F:
    if num == 'F': F.append('C')
    else:
        try: C.append((float(num)-32) * 5 / 9)
        except: C.append(num)
