# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ubConvert', 'readme']
setup_kwargs = {
    'name': 'ubconvert',
    'version': '1.23',
    'description': 'Time, Temperature, Speed, Distance, Volume, Weight conversion module',
    'long_description': '"""\n    ubConvert Unit Conversion Classes -\n\n    - Temperatures()\n    - Speed_Distance()\n    - Weights()\n    - Volumes()\n    - Times()\n\n    The functions for most classes can be called in two ways.\n    First example, to convert Kelvin to Fahrenheit from class Temperatures():\n\n        kelvin = 278.967\n        kelvin_to_fahrenheit(kelvin) = 42.74059999999997\n\n    The second way is with a number representing the rounding factor, where:\n        - 0 = integer, 1 = one decimal place, 2 = two decimal places, etc.,\n\n        kelvin = 278.967\n        kelvin_to_fahrenheit(kelvin, 2) = 42.74,\n        kelvin_to_fahrenheit(kelvin, 1) = 42.7,\n\t\tkelvin_to_fahrenheit(kelvin, 0) = 43\n\n    For converting and formatting Light-Years and Astronomical Units to kilometers\n    or miles, things are a little different. The first way returns an integer:\n\n        lt_years = 2\n        light_years_to_miles(lt_years) = 11758000000000\n\n    The second instance returns a number with requested decimal places in\n    scientific notation:\n\n        lt_years = 2\n        light_years_to_miles(lt_years, 4) = 1.1758e+13\n\n    Because the answers are such large integers, the third way returns the number\n    in comma separated format for easier reading (second arg = 0, third arg = 1):\n\n        lt_years = 2\n        light_years_to_miles(lt_years, 0, 1) = 11,758,000,000,000\n\n    ..................................................................\n    Example:\n\n        import ubConvert as ub\n\n        weights = ub.Weights()\n        oz = weights.grams_to_ounces(28)\n        oz = 1\n\n    ..................................................................\n\n    Functions: NOTE- use all lower case when calling functions, right?\n\n    - Temperatures() function list           \t \t- Weights() function list\n\n        Kelvin_to_Fahrenheit                      \t    Grams_to_Ounces\n        Kelvin_to_Celsius                         \t    Ounces_to_Grams\n        Fahrenheit_to_Kelvin                     \t    Kilograms_to_Pounds\n        Fahrenheit_to_Celsius                     \t    Pounds_to_Kilograms\n        Celsius_to_Fahrenheit                    \t    Kilograms_to_Tons\n        Celsius_to_Kelvin                        \t    Tons_to_Kilograms\n        Rankine_to_Fahrenheit                     \t    Tons_to_Metric_Tonnes\n        Fahrenheit_to_Rankine                     \t    Metric_Tonnes_to_Tons\n\n    - Speed_Distance() function list         \t\t- Volumes() function list\n\t\t\t\t\t\t\t     \n        MPH_to_KPH                                 \t    Liters_to_Gallons\n        KPH_to_MPH                                \t    Gallons_to_Liters\n        MPH_to_Meters_per_Second                            Ounces_to_Milliliters\n        Meters_per_Second_to_MPH                   \t    Milliliters_to_Ounces\n        Meters_per_Second_to_KPH                  \t    Cubic_Centimeter_to_Cubic_Inch\n        KPH_to_Meters_per_Second                  \t    Cubic_Inch_to_Cubic_Centimeter\n        Miles_to_Kilometers\n        Kilometers_to_Miles                   \t\t- Times() function list\n        Light_Years_to_Kilometers\n        Kilometers_to_Light_Years                  \t    Date_to_Timestamp\n        Light_Years_to_Miles                       \t    Timestamp_to_Date\n        Miles_to_Light_Years\n        Yards_to_Meters\n        Meters_to_Yards\n        Inch_to_Centimeter\n        Centimeter_to_Inch\n        Astronomical_Unit_to_Miles\n        Miles_to_Astronomical_Unit\n        Astronomical_Unit_to_Kilometers\n        Kilometers_to_Astronomical_Unit',
    'author': 'ZennDogg, Utility_Belt Designs, Tacoma, WA',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
