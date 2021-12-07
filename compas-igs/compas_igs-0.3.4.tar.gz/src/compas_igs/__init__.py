"""
********************************************************************************
compas_igs
********************************************************************************

.. currentmodule:: compas_igs


.. toctree::
    :maxdepth: 1


"""

from __future__ import print_function

import os


__author__ = 'Tom Van Mele and others (see AUTHORS.md)'
__copyright__ = 'Copyright 2014-2021 - Block Research Group, ETH Zurich'
__license__ = 'MIT License'
__email__ = 'vanmelet@ethz.ch'
__version__ = "0.3.4"


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
