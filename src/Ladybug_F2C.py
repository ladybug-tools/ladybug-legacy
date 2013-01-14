# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

#F to C
"""
Convert from F to C 
-
Provided by Ladybug 0.0.35
    
    Args:
        F: Input temperatures in F
    Returns:
        C: Output temperatures in C
"""

ghenv.Component.Name = "Ladybug_F2C"
ghenv.Component.NickName = 'F2C'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'

C = []
for num in F:
    if num == '°F': F.append('°C')
    else:
        try: C.append((float(num)-32) * 5 / 9)
        except: C.append(num)