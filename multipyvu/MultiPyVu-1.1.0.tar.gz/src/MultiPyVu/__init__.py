# -*- coding: utf-8 -*-
"""
MultiPyVu provides the ability to control the temperature, magnetic field,
and chamber status of Quantum Design, Inc. products using python.  This
module includes MultiVuServer(), which runs on the same computer as MultiVu,
and MultiVuClient(), which is where one writes the python script to control
MultiVu.  MultiVuClient() can be used within the same script as
MultiVuServer(), or within its own script that runs either on the same
computer as MultiVu, or any other computer that has TCP access to the
computer running MultiVuServer().

This folder also contains all of the supporting files for the two projects.

Created on Thu Sep 30 20:48:37 2021

@author: Damon D Jackson
"""


from .__version import __version__

__version__ = __version__
__author__ = 'Damon D Jackson'
__credits__ = 'Quantum Design, Inc.'
__license__ = 'MIT'

__all__ = (
    "MultiVuServer",
    "MultiVuClient",
    )
