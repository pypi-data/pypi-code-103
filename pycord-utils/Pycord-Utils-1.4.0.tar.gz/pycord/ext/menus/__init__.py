"""
pycord.ext.menus
~~~~~~~~~~~~~~~~~
Pycord Menu Module

:copyright: 2021 Pycord
:license: MIT see LICENSE for more info
"""
import discord
import sys

# Pycord 2.1 Or discord.ext.menus Being Mirrored Here
try:
    from discord.ext.menus import *
except ImportError:
    print("Unable To Load Menus Module")
    sys.exit()
