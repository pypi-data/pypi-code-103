# -*- coding: utf-8 -*-
import pytest

from zwutils.dateutils import *

def test_find_date():
    r = find_date('http://www.xinhuanet.com/politics/2020-07/21/c_1126266603.htm')
    assert str(r) == '2020-07-21 00:00:00'
