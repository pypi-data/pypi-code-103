# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 22:41:09 2018
frozen dir
@author: yanhua
"""
import sys
import os
 
def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)