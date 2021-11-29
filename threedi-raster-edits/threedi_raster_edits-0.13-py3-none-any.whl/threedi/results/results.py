# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 15:24:04 2021

@author: chris.kerklaan
"""

from .depth import HAS_THREEDIDEPTH
from .grid import HAS_THREEDIGRID


class ThreediResults:
    def __init__(self, results_folder, dem_path):
        self.results_folder = results_folder
        self.dem_path = dem_path

        if HAS_THREEDIDEPTH:
            from .depth import ThreediDepth

            self.depth = ThreediDepth(self.results_folder, dem_path)

        if HAS_THREEDIGRID:
            from .grid import Grid

            self.grid = Grid(self.results_folder)
