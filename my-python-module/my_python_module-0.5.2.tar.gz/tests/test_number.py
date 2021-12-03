#!/usr/bin/env python
# -*-coding:utf-8-*-

import pytest
from my_python_module.number import radix_conversion
from my_python_module.exceptions import OutOfChoiceError


def test_number_radix_conversion():
    assert radix_conversion(10, 'bin') == '1010'
    assert radix_conversion('0xff', 2, 16) == '11111111'
    assert radix_conversion(0o77, 'hex') == '3f'
    assert radix_conversion(100, 10) == '100'
    with pytest.raises(OutOfChoiceError):
        radix_conversion(100, 1)