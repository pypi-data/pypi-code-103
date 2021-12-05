#!/usr/bin/python3

import os

__version__ = '0.1'

def get_root_path(root_dir_name = 'DeviceLinker', file = os.path.abspath(__file__)):
    if os.path.basename(file) == root_dir_name:
        return file
    return get_root_path(root_dir_name, os.path.dirname(file))
