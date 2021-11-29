# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 13:23:13 2021

@author: mumuz
"""

from simuwater.simuwater import PySimuwaterException

class _Obj(object):
    
    def __init__(self, sim, obj_type, obj_id):
        if not sim._isOpen:
            raise PySimuwaterException('Simuwater Not Open')
        obj_type_idx = -1
        if obj_type == 'Subcatchment':
            obj_type_idx = 0
        elif obj_type == 'Node':
            obj_type_idx = 1
        elif obj_type == 'Link':
            obj_type_idx = 2
        if sim._model.simuwater_findObject(obj_type_idx, obj_id) < 0:
            raise PySimuwaterException('ID Invalid')
        self._sim = sim
        self._model = sim._model
        self._obj_id = obj_id

    @property
    def obj_id(self):
        return self._obj_id

class Subcatch(_Obj):
    
    def __init__(self, sim, subcatch_id):
        super().__init__(sim, 'Subcatchment', subcatch_id)
        
    @property
    def area(self):
        return self._model.simuwater_getParam(1, self._obj_id, 0)
    
    @area.setter
    def area(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 0, value)
    
    @property
    def width(self):
        return self._model.simuwater_getParam(1, self._obj_id, 1)
    
    @width.setter
    def width(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 1, value)

    @property
    def imperv(self):
        return self._model.simuwater_getParam(1, self._obj_id, 2)
    
    @imperv.setter
    def imperv(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 2, value)

    @property
    def slope(self):
        return self._model.simuwater_getParam(1, self._obj_id, 3)
    
    @slope.setter
    def slope(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 3, value)

    @property
    def nimperv(self):
        return self._model.simuwater_getParam(1, self._obj_id, 4)
    
    @nimperv.setter
    def nimperv(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 4, value)

    @property
    def nperv(self):
        return self._model.simuwater_getParam(1, self._obj_id, 5)
    
    @nperv.setter
    def nperv(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 5, value)

    @property
    def dsimperv(self):
        return self._model.simuwater_getParam(1, self._obj_id, 6)
    
    @dsimperv.setter
    def dsimperv(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 6, value)

    @property
    def dsperv(self):
        return self._model.simuwater_getParam(1, self._obj_id, 7)
    
    @dsperv.setter
    def dsperv(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 7, value)

    @property
    def fmax(self):
        return self._model.simuwater_getParam(1, self._obj_id, 8)
    
    @fmax.setter
    def fmax(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 8, value)

    @property
    def fmin(self):
        return self._model.simuwater_getParam(1, self._obj_id, 9)
    
    @fmin.setter
    def fmin(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 9, value)    
        
    @property
    def decay(self):
        return self._model.simuwater_getParam(1, self._obj_id, 10)
    
    @decay.setter
    def decay(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 10, value)    
    
    @property
    def regen(self):
        return self._model.simuwater_getParam(1, self._obj_id, 11)
    
    @regen.setter
    def regen(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 11, value)    
    
    @property
    def max_infil(self):
        return self._model.simuwater_getParam(1, self._obj_id, 12)
    
    @max_infil.setter
    def max_infil(self, value):
        return self._model.simuwater_setParam(1, self._obj_id, 12, value)    
    
    @property
    def rainfall(self):
        return self._model.simuwater_getResult(1, self._obj_id, 0)

    @property
    def evap(self):
        return self._model.simuwater_getResult(1, self._obj_id, 1)
    
    @property
    def infil(self):
        return self._model.simuwater_getResult(1, self._obj_id, 2)
    
    @property
    def runoff(self):
        return self._model.simuwater_getResult(1, self._obj_id, 3)


class Node(_Obj):
    
    def __init__(self, sim, node_id):
        super().__init__(sim, 'Node', node_id)
        self._node_type = self._model.simuwater_getNodeType(node_id)
        
    @property
    def node_type(self):
        if self._node_type == 0:    # junction
            return 'Junction'
        elif self._node_type == 1:    # tank
            return 'Tank'
        elif self._node_type == 2:    # outfall
            return 'Outfall'
        elif self._node_type == 3:    # splitter
            return 'Splitter'
        elif self._node_type == 5:    # reactor
            return 'Reactor'
        elif self._node_type == 6:    # lid_mono
            return 'LID_Mono'
        else:
            return None        
        
    @property
    def tot_inflow(self):
        if self._node_type == 0:    # junction
            return self._model.simuwater_getResult(2, self._obj_id, 0)
        elif self._node_type == 1:    # tank
            return self._model.simuwater_getResult(3, self._obj_id, 2)
        elif self._node_type == 2:    # outfall
            return self._model.simuwater_getResult(4, self._obj_id, 0)
        elif self._node_type == 3:    # splitter
            return self._model.simuwater_getResult(5, self._obj_id, 0)
        elif self._node_type == 5:    # reactor
            return self._model.simuwater_getResult(6, self._obj_id, 1)
        elif self._node_type == 6:    # lid_mono
            return self._model.simuwater_getResult(7, self._obj_id, 0)
        else:
            return None
        
    @property
    def lat_inflow(self):
        if self._node_type == 0:    # junction
            return self._model.simuwater_getResult(2, self._obj_id, 1)
        elif self._node_type == 1:    # tank
            return self._model.simuwater_getResult(3, self._obj_id, 3)
        elif self._node_type == 2:    # outfall
            return self._model.simuwater_getResult(4, self._obj_id, 1)
        elif self._node_type == 3:    # splitter
            return self._model.simuwater_getResult(5, self._obj_id, 1)
        elif self._node_type == 5:    # reactor
            return self._model.simuwater_getResult(6, self._obj_id, 2)
        elif self._node_type == 6:    # lid_mono
            return self._model.simuwater_getResult(7, self._obj_id, 1)
        else:
            return None      
    
class Junction(Node):
    
    def __init__(self, sim, junction_id):
        super().__init__(sim, junction_id)
        
class Tank(Node):
    
    def __init__(self, sim, tank_id):
        super().__init__(sim, tank_id)
        
    @property
    def max_depth(self):
        return self._model.simuwater_getParam(3, self._obj_id, 0)
    
    @max_depth.setter
    def max_depth(self, value):
        return self._model.simuwater_setParam(3, self._obj_id, 0, value)
    
    @property
    def init_depth(self):
        return self._model.simuwater_getParam(3, self._obj_id, 1)

    @init_depth.setter
    def init_depth(self, value):
        return self._model.simuwater_setParam(3, self._obj_id, 1, value)
    
    @property
    def depth(self):
        return self._model.simuwater_getResult(3, self._obj_id, 0)
    
    @depth.setter
    def depth(self, value):
        return self._model.simuwater_setTankDepth(self._obj_id, value)
    
    @property
    def vol(self):
        return self._model.simuwater_getResult(3, self._obj_id, 1)
    
    @property
    def flood(self):
        return self._model.simuwater_getResult(3, self._obj_id, 4)
        
class Splitter(Node):
    
    def __init__(self, sim, splitter_id):
        super().__init__(sim, splitter_id)

    @property
    def splitted_type(self):
        return self._model.simuwater_getParam(5, self._obj_id, 0)

    @splitted_type.setter
    def splitted_type(self, value):
        return self._model.simuwater_setParam(5, self._obj_id, 0, value)

    @property
    def splitted_value(self):
        return self._model.simuwater_getParam(5, self._obj_id, 1)

    @splitted_value.setter
    def splitted_value(self, value):
        return self._model.simuwater_setParam(5, self._obj_id, 1, value)

    @property
    def splitted_flow_ratio(self):
        return self._model.simuwater_getParam(5, self._obj_id, 2)

    @splitted_flow_ratio.setter
    def splitted_flow_ratio(self, value):
        return self._model.simuwater_setParam(5, self._obj_id, 2, value)
    @property
    def outflow1(self):
        return self._model.simuwater_getResult(5, self._obj_id, 2)
    
    @property
    def outflow2(self):
        return self._model.simuwater_getResult(5, self._obj_id, 3)
        
class Link(_Obj):
    
    def __init__(self, sim, link_id):
        super().__init__(sim, 'Link', link_id)
        self._link_type = self._model.simuwater_getLinkType(link_id)
    
    @property
    def link_type(self):
        if self._link_type == 0:
            return 'Pipe'
        elif self._link_type == 1:
            return 'Pump'
        elif self._link_type == 2:
            return 'Connection'
        elif self._link_type == 3:
            return 'Conduit'
        elif self._link_type == 4:
            return 'Weir'
        elif self._link_type == 5:
            return 'Orifice'
        else:
            return None  
    
    @property
    def flow(self):
        if self._link_type == 0:
            return self._model.simuwater_getParam(8, self._obj_id, 2)
        elif self._link_type == 1:
            return self._model.simuwater_getResult(9, self._obj_id, 0)
        elif self._link_type == 2:
            return self._model.simuwater_getResult(10, self._obj_id, 1)   
        elif self._link_type == 3:
            return self._model.simuwater_getResult(11, self._obj_id, 3)  
        elif self._link_type == 4:
            return self._model.simuwater_getResult(12, self._obj_id, 0)
        elif self._link_type == 5:
            return self._model.simuwater_getResult(13, self._obj_id, 0)
        else:
            return None 

    @flow.setter
    def flow(self, value):
        return self._model.simuwater_setLinkFlow(self._obj_id, value)        
    
    @property
    def setting(self):
        return self._model.simuwater_getSetting(self._obj_id)
    
    @setting.setter
    def setting(self, value):
        return self._model.simuwater_setSetting(self._obj_id, value)
        
class Pipe(Link):
    
    def __init__(self, sim, pipe_id):
        super().__init__(sim, pipe_id)
        
    @property
    def k(self):
        return self._model.simuwater_getParam(8, self._obj_id, 0)

    @k.setter
    def k(self, value):
        return self._model.simuwater_setParam(8, self._obj_id, 0, value)
    
    @property
    def n(self):
        return self._model.simuwater_getParam(8, self._obj_id, 1)

    @n.setter
    def n(self, value):
        return self._model.simuwater_setParam(8, self._obj_id, 1, value)
    
    @property
    def x(self):
        return self._model.simuwater_getParam(8, self._obj_id, 2)

    @x.setter
    def x(self, value):
        return self._model.simuwater_setParam(8, self._obj_id, 2, value)

    @property
    def max_flow(self):
        return self._model.simuwater_getParam(8, self._obj_id, 3)

    @max_flow.setter
    def max_flow(self, value):
        return self._model.simuwater_setParam(8, self._obj_id, 3, value)

    @property
    def vol(self):
        return self._model.simuwater_getParam(8, self._obj_id, 0)
    
    @property
    def inflow(self):
        return self._model.simuwater_getParam(8, self._obj_id, 1)

    @property
    def outflow(self):
        return self._model.simuwater_getParam(8, self._obj_id, 2)

    @property
    def flood(self):
        return self._model.simuwater_getParam(8, self._obj_id, 3)

class Pump(Link):
    
    def __init__(self, sim, pump_id):
        super().__init__(sim, pump_id) 
        
    @property
    def init_setting(self):
        return self._model.simuwater_getParam(9, self._obj_id, 0)

    @init_setting.setter
    def init_setting(self, value):
        return self._model.simuwater_setParam(9, self._obj_id, 0, value)

    @property
    def start_depth(self):
        return self._model.simuwater_getParam(9, self._obj_id, 1)

    @start_depth.setter
    def start_depth(self, value):
        return self._model.simuwater_setParam(9, self._obj_id, 1, value)

    @property
    def shut_depth(self):
        return self._model.simuwater_getParam(9, self._obj_id, 2)

    @shut_depth.setter
    def shut_depth(self, value):
        return self._model.simuwater_setParam(9, self._obj_id, 2, value)
        
class Connection(Link):
    
    def __init__(self, sim, connection_id):
        super().__init__(sim, connection_id)
        
    @property
    def delay_sec(self):
        return self._model.simuwater_getParam(10, self._obj_id, 0)

    @delay_sec.setter
    def delay_sec(self, value):
        return self._model.simuwater_setParam(10, self._obj_id, 0, value)
    
    @property
    def inflow(self):
        return self._model.simuwater_getResult(10, self._obj_id, 0)
    
    @property
    def outflow(self):
        return self._model.simuwater_getResult(10, self._obj_id, 1)   
        
class Conduit(Link):
    
    def __init__(self, sim, conduit_id):
        super().__init__(sim, conduit_id)
        
    @property
    def conduit_type(self):
        return self._model.simuwater_getParam(11, self._obj_id, 0)

    @conduit_type.setter
    def conduit_type(self, value):
        return self._model.simuwater_setParam(11, self._obj_id, 0, value)
    
    @property
    def geom1(self):
        return self._model.simuwater_getParam(11, self._obj_id, 1)

    @geom1.setter
    def geom1(self, value):
        return self._model.simuwater_setParam(11, self._obj_id, 1, value)
    
    @property
    def geom2(self):
        return self._model.simuwater_getParam(11, self._obj_id, 2)

    @geom2.setter
    def geom2(self, value):
        return self._model.simuwater_setParam(11, self._obj_id, 2, value)

    @property
    def depth(self):
        return self._model.simuwater_getResult(11, self._obj_id, 0)   

    @property
    def vol(self):
        return self._model.simuwater_getResult(11, self._obj_id, 1)   

    @property
    def inflow(self):
        return self._model.simuwater_getResult(11, self._obj_id, 2)   

    @property
    def outflow(self):
        return self._model.simuwater_getResult(11, self._obj_id, 3)   
    
    @property
    def velocity(self):
        return self._model.simuwater_getResult(11, self._obj_id, 4)   

    @property
    def flood(self):
        return self._model.simuwater_getResult(11, self._obj_id, 5)   
        
class Weir(Link):
    
    def __init__(self, sim, weir_id):
        super().__init__(sim, weir_id)

    @property
    def weir_type(self):
        return self._model.simuwater_getParam(12, self._obj_id, 0)

    @weir_type.setter
    def weir_type(self, value):
        return self._model.simuwater_setParam(12, self._obj_id, 0, value)

    @property
    def disc_coef(self):
        return self._model.simuwater_getParam(12, self._obj_id, 1)

    @disc_coef.setter
    def disc_coef(self, value):
        return self._model.simuwater_setParam(12, self._obj_id, 1, value)
    
    @property
    def width(self):
        return self._model.simuwater_getParam(12, self._obj_id, 2)

    @width.setter
    def width(self, value):
        return self._model.simuwater_setParam(12, self._obj_id, 2, value)

    @property
    def bottom_offset(self):
        return self._model.simuwater_getParam(12, self._obj_id, 3)

    @bottom_offset.setter
    def bottom_offset(self, value):
        return self._model.simuwater_setParam(12, self._obj_id, 3, value)

    @property
    def height(self):
        return self._model.simuwater_getParam(12, self._obj_id, 4)

    @height.setter
    def height(self, value):
        return self._model.simuwater_setParam(12, self._obj_id, 4, value)
    
class Orifice(Link):
    
    def __init__(self, sim, orifice_id):
        super().__init__(sim, orifice_id)

    @property
    def orifice_type(self):
        return self._model.simuwater_getParam(13, self._obj_id, 0)

    @orifice_type.setter
    def orifice_type(self, value):
        return self._model.simuwater_setParam(13, self._obj_id, 0, value)

    @property
    def geom1(self):
        return self._model.simuwater_getParam(13, self._obj_id, 1)

    @geom1.setter
    def geom1(self, value):
        return self._model.simuwater_setParam(13, self._obj_id, 1, value)
    
    @property
    def geom2(self):
        return self._model.simuwater_getParam(13, self._obj_id, 2)

    @geom2.setter
    def geom2(self, value):
        return self._model.simuwater_setParam(13, self._obj_id, 2, value)
    
    @property
    def disc_coef(self):
        return self._model.simuwater_getParam(13, self._obj_id, 3)

    @disc_coef.setter
    def disc_coef(self, value):
        return self._model.simuwater_setParam(13, self._obj_id, 3, value)
    
    @property
    def bottom_offset(self):
        return self._model.simuwater_getParam(13, self._obj_id, 4)

    @bottom_offset.setter
    def bottom_offset(self, value):
        return self._model.simuwater_setParam(13, self._obj_id, 4, value)