# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 15:13:16 2021

@author: HEDI
"""
from .__obj__ import dict2obj
import copy

def var(main_frame,attr={}):
    obj = dict2obj(copy.deepcopy(main_frame.config.var_schema.toJSON()))
    for k,v in attr.items():
        setattr(obj,k,v)
    return obj