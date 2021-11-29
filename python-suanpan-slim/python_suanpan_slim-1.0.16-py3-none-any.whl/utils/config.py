# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import sys
import yaml


def loadConfig(path):
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def dumpConfig(data, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return path


def resourcepath(relativepath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basepath = sys._MEIPASS
    except Exception:
        basepath = os.path.abspath(".")

    return os.path.join(basepath, relativepath)
