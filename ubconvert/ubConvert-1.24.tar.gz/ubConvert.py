# -*- coding: utf-8 -*-
# Created on Thu May 10 16:04:56 2020

from datetime import datetime, timedelta, date
import time


def main():
    """
    ubConvert conversion module
    Utility_Belt Designs, Tacoma, WA
    @author: ZennDogg

    ubConvert Unit Conversion Classes -

    - Temperatures()
    - Speed_Distance()
    - Weights()
    - Volumes()
    - Times()

    The functions for most classes can be called in two ways.
    First example, to convert Kelvin to Fahrenheit from class Temperatures():

        kelvin = 278.967
        kelvin_to_fahrenheit(kelvin) = 42.74059999999997

    The second way is with a number representing the rounding factor, where:
        - 0 = integer, 1 = one decimal place, 2 = two decimal places, etc.,

        kelvin = 278.967
        kelvin_to_fahrenheit(kelvin, 2) = 42.74, or,
        kelvin_to_fahrenheit(kelvin, 1) = 42.7

    For converting and formatting Light-Years and Astronomical Units to kilometers
    or miles, things are a little different. The first way returns an integer:

        lt_years = 2
        light_years_to_miles(lt_years) = 11758000000000

    The second instance returns a number with requested decimal places in
    scientific notation:

        lt_years = 2
        light_years_to_miles(lt_years, 4) = 1.1758e+13

    Because the answers are such large integers, the third way returns the number
    in comma separated format for easier reading (second arg = 0, third arg = 1):

        lt_years = 2
        light_years_to_miles(lt_years, 0, 1) = 11,758,000,000,000

    ..................................................................
    Example:

        import ubConvert as ub

        weights = ub.Weights()
        oz = weights.grams_to_ounces(28)
        oz = 1

    ..................................................................

    Functions: NOTE- use all lower case when calling functions, right?

    - Temperatures() function list            - Weights() function list

        Kelvin_to_Fahrenheit                      Grams_to_Ounces
        Kelvin_to_Celsius                         Ounces_to_Grams
        Fahrenheit_to_Kelvin                      Kilograms_to_Pounds
        Fahrenheit_to_Celsius                     Pounds_to_Kilograms
        Celsius_to_Fahrenheit                     Kilograms_to_Tons
        Celsius_to_Kelvin                         Tons_to_Kilograms
        Rankine_to_Fahrenheit                     Tons_to_Metric_Tonnes
        Fahrenheit_to_Rankine                     Metric_Tonnes_to_Tons

    - Speed_Distance() function list          - Volumes() function list

        MPH_to_KPH                                 Liters_to_Gallons
        KPH_to_MPH                                 Gallons_to_Liters
        MPH_to_Meters_per_Second                   Ounces_to_Milliliters
        Meters_per_Second_to_MPH                   Milliliters_to_Ounces
        Meters_per_Second_to_KPH                   Cubic_Centimeter_to_Cubic_Inch
        KPH_to_Meters_per_Second                   Cubic_Inch_to_Cubic_Centimeter
        Miles_to_Kilometers
        Kilometers_to_Miles                    - Times() function list
        Light_Years_to_Kilometers
        Kilometers_to_Light_Years                  Date_to_Timestamp
        Light_Years_to_Miles                       Timestamp_to_Date
        Miles_to_Light_Years
        Yards_to_Meters
        Meters_to_Yards
        Inch_to_Centimeter
        Centimeter_to_Inch
        Astronomical_Unit_to_Miles
        Miles_to_Astronomical_Unit
        Astronomical_Unit_to_Kilometers
        Kilometers_to_Astronomical_Unit
    """
    pass



class Temperatures(object):
    """
    Formulas for Temperature Conversions
    """

    def kelvin_to_fahrenheit(kelvin, num=-1):
        equation = 9 * float(kelvin) - (273 / 5) + 32
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def kelvin_to_celsius(kelvin, num=-1):
        equation = float(kelvin) - 273.15
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def fahrenheit_to_kelvin(fahrenheit, num=-1):
        equation = (float(fahrenheit) + 459.67) * (9 / 5)
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def celsius_to_fahrenheit(celsius, num=-1):
        equation = float(celsius) * (9 / 5)  + 32
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def celsius_to_kelvin(celsius, num=-1):
        equation = float(celsius) + 273.15
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def fahrenheit_to_celsius(fahrenheit, num=-1):
        equation = (float(fahrenheit) - 32) * (5 / 9)
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def fahrenheit_to_rankine(fahrenheit, num=-1):
        equation = float(fahrenheit) + 459.670000001
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def rankine_to_fahrenheit(rankine, num=-1):
        equation = float(rankine) - 459.670000001
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)


class Speed_Distance(object):
    """
    Formulas for Speed and Distance Conversions
    """

    def mph_to_kph(mph, num=-1):
        equation = float(mph) * 1.60934
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def kph_to_mph(kph, num=-1):
        equation = float(kph) * 0.621371
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def meters_per_second_to_mph(meters_per_second, num=-1):
        equation = float(meters_per_second) * 2.23694
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def mph_to_meters_per_second(mph, num=-1):
        equation = float(mph) * 0.044704
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def meters_per_second_to_kph(meters_per_second, num=-1):
        equation = float(meters_per_second) * 3.6
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def kph_to_meters_per_second(kph, num=-1):
        equation = float(kph) * 0.2777777778
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def miles_to_kilometers(miles, num=-1):
        equation = float(miles) * 1.60934
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def kilometers_to_miles(kilometers, num=-1):
        equation = float(kilometers) * 0.62137
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def astronomical_unit_to_miles(astronomical_unit, num=-1, comma=0):
        equation = float(astronomical_unit) * 92955807.26743
        if comma == 1:
            return "{:,}".format(equation)
        elif num > 0 and not comma:
            return format(round(equation, num)), (
                "10." + str(num) + "e"
            )
        elif num == -1:
            return equation

    def astronomical_unit_to_kilometers(astronomical_unit, num=-1, comma=0):
        equation = float(astronomical_unit) * 149597870.7
        if comma == 1:
            return "{:,}".format(equation)
        elif num > 0 and not comma:
            return format(round(equation, num)), (
                "10." + str(num) + "e"
            )
        elif num == -1:
            return equation

    def miles_to_astronomical_unit(miles, num=-1):
        equation = float(miles) / 92955807.26743
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def kilometers_to_astronomical_unit(kilometers, num=-1):
        equation = float(kilometers) / 149597870.7
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def light_years_to_kilometers(light_years, num=-1, comma=0):
        equation = float(light_years) * 9.461e12
        if comma > 0:
            return "{:,}".format(equation)
        elif num > 0 and not comma:
            return format(round(equation, num)), (
                "10." + str(num) + "e"
            )
        elif num == -1:
            return equation

    def light_years_to_miles(light_years, num=-1, comma=0):
        equation = float(light_years) * 5.879e12
        if comma > 0:
            return "{:,}".format(equation)
        elif num > 0 and not comma:
            return format(round(equation, num)), (
                "10." + str(num) + "e"
            )
        elif num == -1:
            return equation

    def miles_to_light_years(miles):
        return format(float(miles) * 1.70108e-13), "10.5e"

    def kilometers_to_light_years(kilometers):
        return float(kilometers) * 1.057e-13

    def meters_to_yards(meters, num=-1):
        equation = float(meters) * 1.0936133
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def yards_to_meters(yards, num=-1):
        equation = float(yards) * 0.9144
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def inch_to_centimeter(inch, num=-1):
        equation = float(inch) * 2.54
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def centimeter_to_inch(centimeter, num=-1):
        equation = float(centimeter) * 0.393701
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)


class Weights(object):
    """
    Formulas for Weight Conversions
    """

    def grams_to_ounces(grams, num=-1):
        equation = float(grams) * 0.035274
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def ounces_to_grams(ounces, num=-1):
        equation = float(ounces) * 28.349
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def kilograms_to_pounds(kilograms, num=-1):
        equation = float(kilograms) * 2.2046
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def pounds_to_kilograms(pounds, num=-1):
        equation = float(pounds) * 0.454
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def kilograms_to_ton(kilograms, num=-1):
        equation = float(kilograms) * 0.0011
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def tons_to_kilograms(tons, num=-1):
        equation = float(tons) * 907.18
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def tons_to_metric_tonnes(tons, num=-1):
        equation = float(tons) * 0.907185
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def metric_tonnes_to_tons(metric_tonnes, num=-1):
        equation = float(metric_tonnes) * 1.102311
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)


class Volumes(object):
    """
    Formulas for Volume Conversions
    """

    def liters_to_gallons(liters, num=-1):
        equation = float(liters) * 0.264
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def gallons_to_liters(gallons, num=-1):
        equation = float(gallons) * 3.785
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def ounces_to_milliliters(ounces, num=-1):
        equation = float(ounces) * 29.57
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def milliliters_to_ounces(milliliters, num=-1):
        equation = float(milliliters) * 0.0338
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def cubic_centimeter_to_cubic_inch(cubic_centimeter, num=-1):
        equation = float(cubic_centimeter) * 0.0610237
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)

    def cubic_inch_to_cubic_centimeter(cubic_inch, num=-1):
        equation = float(cubic_inch) * 16.387064
        if num == -1:
            return equation
        elif num == 0:
            return int(equation)
        else:
            return round(equation, num)


class Times(object):
    """
    Formulas for Time Conversions
    """

    def timestamp_to_date(num: int):
        return datetime.fromtimestamp(int(num))

    def date_to_timestamp(year="", month="", day="", *args, **kwargs):
        return timedelta.total_seconds(
            datetime(year, month, day, *args, **kwargs) - datetime(1970, 1, 1)
        )


if __name__ == "__main__":
    main()
