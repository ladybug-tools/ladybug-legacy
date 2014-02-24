#C to F
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Convert from C to F 
-
Provided by Ladybug 0.0.55
    
    Args:
        _C: Input temperatures in C
    Returns:
        F: Output temperatures in F
"""

ghenv.Component.Name = "Ladybug_C2F"
ghenv.Component.NickName = 'C2F'
ghenv.Component.Message = 'VER 0.0.55\nFEB_24_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


F = []
for num in _C:
   if num == 'C': F.append('F')
   else:
       try: F.append(float(num)*9/5 + 32)
       except: F.append(num)
