#C to F
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Convert from C to F 
-
Provided by Ladybug 0.0.35
    
    Args:
        C: Input temperatures in C
    Returns:
        F: Output temperatures in F
"""

ghenv.Component.Name = "Ladybug_C2F"
ghenv.Component.NickName = 'C2F'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'

F = []
for num in C:
   if num == '°C': F.append('°F')
   else:
       try: F.append(float(num)*9/5 + 32)
       except: F.append(num)