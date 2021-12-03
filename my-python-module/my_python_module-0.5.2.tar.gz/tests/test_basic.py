#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from my_python_module.common import str2pyobj


def test_str2pyobj():
    test_list = {}
    # test int
    test_list['int'] = '72'
    # test float
    test_list['float'] = '3.14'
    # test 'abc.html'
    test_list['str'] = 'abc.html'
    # test list
    test_list['list'] = '[1,2,3]'
    # test True
    test_list['bool'] = 'True'

    for t, inval in test_list.items():
        outval = str2pyobj(inval)
        assert str(type(outval)).split("\'")[1] == t
