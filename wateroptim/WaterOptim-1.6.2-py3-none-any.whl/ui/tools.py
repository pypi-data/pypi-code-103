# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 21:27:05 2021

@author: HEDI
"""
import uuid
def uuid_gen(uuids=[],n=8):
    def gen():
        return str(str(uuid.uuid1())[:n])
    s=gen()
    while s in uuids:
        s=gen()
    uuids.append(s)
    return s