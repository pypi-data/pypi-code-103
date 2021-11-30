# -*- coding: UTF-8 -*-

import pkgutil

__version__ = '1.0.0'
__author__ = 'Hu Min'

def get_version():
    return __version__

def init():
    for _, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix='yqdata.'):
        if ispkg:
            continue
        try:
            __import__(modname)
        except ImportError:
            print("can not find mod [{}], ignored".format(modname))
            continue
        
init()