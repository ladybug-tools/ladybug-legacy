# Construct Time
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Construct Time
-
Provided by Ladybug 0.0.56

    Args:
        _hour_: Hour [1-23]
        _minutes_: Minutes [1-60]
        _seconds_: Seconds [1-60]
    Returns:
        hour: Output hour

"""
ghenv.Component.Name = "Ladybug_Construct Time"
ghenv.Component.NickName = 'constructTime'
ghenv.Component.Message = 'VER 0.0.56\nMAR_22_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

hour = _hour_ + _minutes_/60 + _seconds_/3600