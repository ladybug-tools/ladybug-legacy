#C to F
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to convert temperatures from Celcius to Fahrenheit.
-
Provided by Ladybug 0.0.58
    
    Args:
        _C: A temperature or list of temperatures in Celcius.
    Returns:
        F: The input temperatures converted to Fahrenheit.
"""

ghenv.Component.Name = "Ladybug_C2F"
ghenv.Component.NickName = 'C2F'
ghenv.Component.Message = 'VER 0.0.58\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


F = []
for num in _C:
   if num == 'C': F.append('F')
   elif num == 'C': F.append('F')
   else:
       try: F.append(float(num)*9/5 + 32)
       except: F.append(num)
