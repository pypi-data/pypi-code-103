# -*- coding: utf-8 -*-
"""
Path handling.
"""

import inspect
from pathlib import Path

import vaccontrib


def get_package_root():
    """Get the path of the package repository."""
    package_path = Path(inspect.getfile(vaccontrib))
    pkg_root = package_path.parents[0]
    return pkg_root

def get_data_dir():
    """Get the path of the package's data directory."""
    return get_package_root() / 'data'

if __name__ == "__main__":
    print(get_data_dir())
