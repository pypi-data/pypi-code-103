#!/usr/bin/env python
# -*-coding:utf-8-*-

import math
from my_python_module.exceptions import OutOfChoiceError
from typing import Union

def radix_conversion(number:Union[int,str], output_radix, input_radix=10) -> str:
    """
    number radix conversion.

    number: input can be a number or string
    output_radix:
    input_radix: the input number radix, default is 10

    the radix support list: ['bin', 'oct', 'dec', 'hex', 2, 8, 10, 16]

>>> radix_conversion(10, 'bin')
'1010'
>>> radix_conversion('0xff', 2, 16)
'11111111'
>>> radix_conversion(0o77, 'hex')
'3f'
>>> radix_conversion(100, 10)
'100'
>>> radix_conversion(100,1)
Traceback (most recent call last):
......
my_python_module.exceptions.OutOfChoiceError: radix is out of choice.

    """
    name_map = {'bin': 2, 'oct': 8, 'dec': 10, 'hex': 16}

    for index, radix in enumerate([input_radix, output_radix]):
        if radix is None:
            continue

        if radix not in ['bin', 'oct', 'dec', 'hex', 2, 8, 10, 16]:
            raise OutOfChoiceError("radix is out of choice.")

        if radix in name_map.keys():
            if index == 0:
                input_radix = name_map[radix]
            elif index == 1:
                output_radix = name_map[radix]

    if isinstance(number, str) and input_radix:
        number = int(number, input_radix)

    if output_radix == 2:
        return f'{number:b}'
    elif output_radix == 8:
        return f'{number:o}'
    elif output_radix == 10:
        return f'{number:d}'
    elif output_radix == 16:
        return f'{number:x}'


def round_half_up(n, decimals=0):
    """
    实现常见的那种四舍五入，警告这只是一种近似，如果有精确的小数需求还是推荐使用decimal模块。
    """
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier