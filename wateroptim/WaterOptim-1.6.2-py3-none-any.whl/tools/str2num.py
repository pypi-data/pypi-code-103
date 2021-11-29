# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 15:05:25 2021

@author: HEDI
"""
from .is_number import is_number
def str2num(val):
    if is_number(val):
        return float(val)
    return 0