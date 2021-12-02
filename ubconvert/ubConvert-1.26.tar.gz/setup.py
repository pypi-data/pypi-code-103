# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ubConvert', 'readme']
setup_kwargs = {
    'name': 'ubconvert',
    'version': '1.26',
    'description': 'Time, Temperature, Speed, Distance, Volume, Weight conversion module',
    'long_description': '\n    ubConvert Unit Conversion Classes -\n\n    - Temperatures()\n    - Speed_Distance()\n    - Weights()\n    - Volumes()\n    - Times()\n\n    The functions for most classes can be called in two ways.\n    First example, to convert Kelvin to Fahrenheit from class \n    Temperatures():\n\n        kelvin = 278.967\n        kelvin_to_fahrenheit(kelvin) = 42.74059999999997\n\n    The second way is with a number representing the rounding \n    factor, where:\n\n        - 0 = integer, 1 = one decimal place, 2 = two decimal \n        places, etc. For example:\n\n        kelvin = 278.967\n        kelvin_to_fahrenheit(kelvin, 2) = 42.74,\n        kelvin_to_fahrenheit(kelvin, 1) = 42.7,\n        kelvin_to_fahrenheit(kelvin, 0) = 43\n\n    For converting and formatting Light-Years and Astronomical \n    Units to kilometers or miles, things are a little different. \n    The first way returns an integer:\n\n        lt_years = 2\n        light_years_to_miles(lt_years) = 11758000000000\n\n    The second instance returns a number with requested decimal \n    places in scientific notation:\n\n        lt_years = 2\n        light_years_to_miles(lt_years, 4) = 1.1758e+13\n\n    Because the answers are such large integers, the third way \n    returns the number in comma separated format for easier \n    reading (second arg = 0, third arg = 1):\n\n        lt_years = 2\n        light_years_to_miles(lt_years, 0, 1) = 11,758,000,000,000\n\n    ..................................................................\n    Example:\n\n        import ubConvert as ub\n\n        weight = ub.Weights()\n        oz = weight.grams_to_ounces(28)\n        oz = 1\n\n    ..................................................................\n\n    Functions: NOTE- use all lower case for functions, right?\n\n    - Class Temperatures() function list           \t \t\n\n        Kelvin_to_Fahrenheit\n        Kelvin_to_Celsius    \n        Fahrenheit_to_Kelvin      \n        Fahrenheit_to_Celsius   \n        Celsius_to_Fahrenheit    \n        Celsius_to_Kelvin        \n        Rankine_to_Fahrenheit   \n        Fahrenheit_to_Rankine \n    \n\n    - Class Speed_Distance() function list\n\t\t\t\t\t\t\t     \n        MPH_to_KPH \n        KPH_to_MPH \n        MPH_to_Meters_per_Second\n        Meters_per_Second_to_MPH\n        Meters_per_Second_to_KPH \n        KPH_to_Meters_per_Second\n        Miles_to_Kilometers\n        Kilometers_to_Miles  \n        Light_Years_to_Kilometers\n        Kilometers_to_Light_Years  \n        Light_Years_to_Miles\n        Miles_to_Light_Years\n        Yards_to_Meters\n        Meters_to_Yards\n        Inch_to_Centimeter\n        Centimeter_to_Inch\n        Astronomical_Unit_to_Miles\n        Miles_to_Astronomical_Unit\n        Astronomical_Unit_to_Kilometers\n        Kilometers_to_Astronomical_Unit\n\n\n    - Class Weights() function list\n\n\t    Grams_to_Ounces\n        Ounces_to_Grams\n        Kilograms_to_Pounds\n        Pounds_to_Kilograms\n        Kilograms_to_Tons\n        Tons_to_Kilograms\n        Tons_to_Metric_Tonnes\n        Metric_Tonnes_to_Tons\n\n\n    - Class Volumes() function list\n\n\t    Liters_to_Gallons\n        Gallons_to_Liters\n        Ounces_to_Milliliters\n        Milliliters_to_Ounces\n        Cubic_Centimeter_to_Cubic_Inch\n        Cubic_Inch_to_Cubic_Centimeter\n\n        \n    - Class Times() function list\n\n\t    Date_to_Timestamp\n\t    Timestamp_to_Date\n',
    'author': 'ZennDogg, Utility_Belt Designs, Tacoma, WA',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
