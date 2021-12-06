# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 23:16:26 2021

@author: mumuz
"""

import importlib
from muswmm.errors import *

class _Namedobjs():
    
    def __init__(self, project, namedobjs, namedobj_type):
        self._prj = project
        self._objs = namedobjs
        self._cur_index = 0
        self._count = self._objs.Count
        self.obj_type = namedobj_type
        
    def __len__(self):
        return self._objs.Count
    
    def __contains__(self, name):
        if self._objs.GetIndex(name) < 0:
            return False
        else:
            return True
    
    def __getitem__(self, name):
        if self.__contains__(name):
            module = importlib.import_module('muswmm.namedobject')
            obj_class = getattr(module, self.obj_type)
            return obj_class(self._prj, name)
        else:
            raise Exception(ERROR_IDNOTEXIST.format(name))
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._cur_index < self._count:
            obj = self.__getitem__(self._name)
            self._cur_index += 1
            return obj
        else:
            raise StopIteration()
            
    @property
    def _name(self):
        return self._objs.GetItem(self._cur_index).Name
    
    def clear(self):
        self._objs.RemoveAll()


class RainGages(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.RainGages, 'RainGage')


class Subcatchments(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.Subcatchments, 'Subcatchment')

class Junctions(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.Junctions, 'Junction')
        
class Outfalls(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.Outfalls, 'Outfall')
        
class Storages(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.Storages, 'Storage')
        
class Dividers(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.Dividers, 'Divider')
        
class Conduits(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.Conduits, 'Conduit')
        
class Pumps(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.Pumps, 'Pump')
        
class Orifices(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.Orifices, 'Orifice')
        
class Weirs(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.Orifices, 'Weir')
        
class Outlets(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.Outlets, 'Outlet')
        
class TimeSeries(_Namedobjs):
    
    def __init__(self, project):
        super().__init__(project, project._prj.TimeSeries, 'TimeSerie')