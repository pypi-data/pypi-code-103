# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 22:50:32 2021

@author: mumuz
"""

import os
import clr
import ctypes
import platform

LIB_PATH = os.path.abspath(os.path.dirname(__file__))

# 加载Mumu.SWMM.SwmmObjects.dll
clr.AddReference(LIB_PATH + '\\Mumu.SWMM.SwmmObjects.dll')
# 加载Mumu.SWMM.Output.dll
clr.AddReference(LIB_PATH + '\\Mumu.SWMM.Output.dll')
if platform.architecture()[0] == '32bit':
    LIB_PATH += '\\X86'
else:
    LIB_PATH += '\\X64'
SWMM5EX = ctypes.cdll.LoadLibrary(LIB_PATH + '\\swmm5ex.dll')