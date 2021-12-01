#! python
# -*- coding: utf-8 -*-
import mwx
import unittest
from testools import inspect_args


## $ 未サポート
## $(kwonlyargs) = ['key', 'value']
## $(kwonlydefaults) = {'value': 0}
## 
## @inspect_args
## def func(self, a, b, c=0, *args, key:int, value:int=0, **kwargs)->int:
##     """This function uses new syntax"""
##     print("(a,b,c) =", (a,b,c))
##     pass


@inspect_args
def func(self, a, b, c=0, *args, **kwargs):
    """Test func"""
    print("(a,b,c) =", (a,b,c))
    pass

f = mwx.funcall(func)
print(inspect_args(f))
## f(None, -1) # TypeError: func() missing 1 required positional argument: 'b'
f(None, -1, -2) # ok
f(None, -1, -2, -3) # ok
f(None, -1, -2, -3, -4) # ok
