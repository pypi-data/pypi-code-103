def convert_c_to_f(temp):
    """
    Converts Celsius temperature to Fahrenheit.
    :param temp: Temperature in Celsius
    :return: Temperature in Fahrenheit

    >>> round(convert_c_to_f(0),2)
    32.0
    >>> round(convert_c_to_f(-24),2)
    -11.2
    >>> round(convert_c_to_f(14),2)
    57.2
    """
    return (temp * 1.8) + 32.0


def convert_c_to_k(temp):
    """
    Converts Celsius temperature to Kelvin
    :param temp: Temperature in Celsius
    :return: Temperature in Kelvin

    >>> round(convert_c_to_k(0),2)
    273.15
    >>> round(convert_c_to_k(-300),2)
    -26.85
    >>> round(convert_c_to_k(15),2)
    288.15
    """
    return temp + 273.15


def convert_f_to_c(temp):
    """
    Converts Fahrenheit temperature to Celsius
    :param temp: Temperature in Fahrenheit
    :return: Temperature in Celsius

    >>> round(convert_f_to_c(0.5),2)
    -17.5
    >>> round(convert_f_to_c(32),2)
    0.0
    >>> round(convert_f_to_c(59),2)
    15.0
    """
    return (temp - 32.0) / 1.8


def convert_f_to_k(temp):
    """
    Converts Fahrenheit temperature to Kelvin
    :param temp: Temperature in Fahrenheit
    :return: Temperature in Kelvin

    >>> round(convert_f_to_k(32),2)
    273.15
    >>> round(convert_f_to_k(-4),2)
    253.15
    >>> round(convert_f_to_k(212),2)
    373.15
    """
    return convert_c_to_k(convert_f_to_c(temp))


def convert_k_to_c(temp):
    """
    Converts Kelvin Temperature to Celsius
    :param temp: Temperature in Kelvin
    :return: Temperature in Celsius

    >>> round(convert_k_to_c(273.15),2)
    0.0
    >>> round(convert_k_to_c(-50),2)
    -323.15
    >>> round(convert_k_to_c(300.5),2)
    27.35
    """
    return temp - 273.15


def convert_k_to_f(temp):
    """
    Converts Kelvin temperature to Fahrenheit
    :param temp: Temperature in Kelvin
    :return: Temperature in Fahrenheit

    >>> round(convert_k_to_f(273.15),2)
    32.0
    >>> round(convert_k_to_f(-5),2)
    -468.67
    >>> round(convert_k_to_f(340.5),2)
    153.23
    """
    return convert_c_to_f(convert_k_to_c(temp))


def convert(temp, from_unit, to_unit):
    """
    Converts the given temperature from the unit given by the from_unit
    argument (Celsius (C), Farenheit (F), or Kelvin (K)) to the to_unit
    argument (Celsius (C), Farenheit (F), or Kelvin (K)).
    :param temp: Temperature to convert
    :param from_unit: Character unit of temp (C, F, or K)
    :param to_unit: Character unit for output temperature (C, F, or K)
    :return: converted temperature

    >>> round(convert(0, 'c', 'F'),2)
    32.0
    >>> round(convert(32, 'f', 'C'),2)
    0.0
    >>> round(convert(212, 'f', 'C'),2)
    100.0
    >>> round(convert(0, 'c', 'k'),2)
    273.15
    >>> round(convert(273.15, 'k', 'f'),2)
    32.0
    >>> round(convert(273.15, 'f', 'k'),2)
    407.12
    >>> round(convert(300, 'k', 'c'),2)
    26.85
    """
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()

    if from_unit == to_unit:
        return temp

    converters = {'C': {'F': convert_c_to_f, 'K': convert_c_to_k},
                  'F': {'C': convert_f_to_c, 'K': convert_f_to_k},
                  'K': {'C': convert_k_to_c, 'F': convert_k_to_f}}



    if from_unit in converters:
        if to_unit in converters[from_unit]:
            return converters[from_unit][to_unit](temp)
        else:
            raise Exception("to_unit unrecognized:  " + to_unit)
    else:
        raise Exception("from_unit unrecognized:  " + from_unit)
