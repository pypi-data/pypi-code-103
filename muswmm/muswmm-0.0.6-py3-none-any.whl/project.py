# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 21:10:18 2021

@author: mumuz
"""

import os
import muswmm.lib

from Mumu.SWMM.SwmmObjects import Project as Proj
from muswmm.namedobjects import *
from muswmm.options import *

class Project():
    
    def __init__(self, inp_path):
        self.path = os.path.abspath(os.path.dirname(inp_path))
        self.name = os.path.split(inp_path)[-1].split('.')[0]
        self._prj = Proj()
        self._prj.Open(inp_path)
        self.title = self._prj.Title        
        
    def save(self):
        self._prj.Save()
        
    def save_as(self, path):
        self._prj.SaveAs(path)
    
    @property
    def options(self):
        return Options(self)
    
    @property
    def gages(self):
        return RainGages(self)
    
    @property
    def subcatchments(self):
        return Subcatchments(self)
    
    @property
    def junctions(self):
        return Junctions(self)
    
    @property
    def outfalls(self):
        return Outfalls(self)
    
    @property
    def storages(self):
        return Storages(self)
    
    @property
    def dividers(self):
        return Dividers(self)
    
    @property
    def conduits(self):
        return Conduits(self)
    
    @property
    def pumps(self):
        return Pumps(self)
    
    @property
    def orifices(self):
        return Orifices(self)
    
    @property
    def weirs(self):
        return Weirs(self)
    
    @property
    def outlets(self):
        return Outlets(self)
    
    @property
    def timeseries(self):
        return TimeSeries(self)