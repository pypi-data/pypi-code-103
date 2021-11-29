# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 15:04:28 2021

@author: HEDI
"""

def is_number(n):
    try:
        float(n)   # Type-casting the string to `float`.
                   # If string is not a valid `float`, 
                   # it'll raise `ValueError` exception
    except ValueError:
        return False
    return True