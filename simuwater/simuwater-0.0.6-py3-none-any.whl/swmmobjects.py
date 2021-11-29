# -*- coding: utf-8 -*-
"""
Created on Sun Nov 21 16:24:47 2021

@author: mumuz
"""

import importlib
from simuwater.simuwater import PySimuwaterException

class _SwmmObjs(object):
    
    def __init__(self, sim, inp_id, obj_type):
        if not sim._isOpen:
            raise PySimuwaterException('SWMM Model Within Simuwater Not Open')
        self._sim = sim
        self._inp_id = inp_id
        self._model = sim._model
        self._cur_index = 0
        self._nObjs = 0
        self._obj_type = obj_type
        self._obj_type_idx = -1
        if obj_type == 'Subcatchment':
            self._obj_type_idx = 0
        elif obj_type == 'Node':
            self._obj_type_idx = 1
        elif obj_type == 'Link':
            self._obj_type_idx = 2
        self._nObjs = self._model.simuwater_getSwmmObjCount(self._inp_id, self._obj_type_idx)
    
    def __len__(self):
        return self._nObjs
    
    def __contains__(self, obj_id):
        if self._model.simuwater_getSwmmObjIndex(self._inp_id, self._obj_type_idx,obj_id) < 0:
            return False
        return True
    
    def __getitem__(self, obj_id):
        if self.__contains__(obj_id):
            module = importlib.import_module('simuwater.swmmobjects')
            obj_class = getattr(module, self._obj_type)
            return obj_class(self._sim, self._inp_id, obj_id)
        else:
            raise PySimuwaterException('Node ID: {} Does not Exists'.format(obj_id))
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._cur_index < self._nObjs:
            obj = self.__getitem__(self._obj_id)
            self._cur_index += 1
            return obj
        else:
            raise StopIteration()
    
    next = __next__  # Python 2        


class SwmmSubcatchs(_SwmmObjs):
    
    def __init__(self, sim, inp_id):
        super().__init__(sim, inp_id, 'Subcatchment')
        

class SwmmNodes(_SwmmObjs):
    
    def __init__(self, sim, inp_id):
        super().__init__(sim, inp_id, 'Node')
        
class SwmmLinks(_SwmmObjs):
    
    def __init__(self, sim, inp_id):
        super().__init__(sim, inp_id, 'Link')

class _SwmmObj(object):
    
    def __init__(self, sim, inp_id, obj_type, obj_id):
        if not sim._isOpen:
            raise PySimuwaterException('SWMM Model Within Simuwater Not Open')
        obj_type_idx = -1
        if obj_type == 'Subcatchment':
            obj_type_idx = 0
        elif obj_type == 'Node':
            obj_type_idx = 1
        elif obj_type == 'Link':
            obj_type_idx = 2
        if sim._model.simuwater_getSwmmObjIndex(inp_id, obj_type_idx, obj_id) < 0:
            raise PySimuwaterException('ID Invalid')
        self._sim = sim
        self._model = sim._model
        self._inp_id = inp_id
        self._obj_id = obj_id
        
    @property
    def obj_id(self):
        return self._obj_id
    
class SwmmSubcatch(_SwmmObj):
    
    def __init__(self, sim, inp_id, subcatch_id):
        super().__init__(sim, inp_id, 'Subcatchment', subcatch_id)
    
    @property
    def area(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 0, self._obj_id, 0)[1]  
    
    @area.setter
    def area(self,value):
        self._model.simuwater_setSwmmParam(self._inp_id, 0, self._obj_id, 0 ,value)
    
    @property
    def width(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 0, self._obj_id, 1)[1] 
    
    @width.setter
    def width(self,value):
        self._model.simuwater_setSwmmParam(self._inp_id, 0, self._obj_id, 1 ,value)
    
    @property
    def frac_imperv(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 0, self._obj_id, 2)[1] 
    
    @frac_imperv.setter
    def frac_imperv(self,value):
        self._model.simuwater_setSwmmParam(self._inp_id, 0, self._obj_id, 2 ,value)
    
    @property
    def slope(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 0, self._obj_id, 3)[1] 
    
    @slope.setter
    def slope(self,value):
        self._model.simuwater_setSwmmParam(self._inp_id, 0, self._obj_id, 3 ,value)
    
    @property
    def curb_len(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 0, self._obj_id, 4)[1] 
    
    @curb_len.setter
    def curb_len(self,value):
        self._model.simuwater_setSwmmParam(self._inp_id, 0, self._obj_id, 4 ,value)
    
    @property
    def rainfall(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 0, self._obj_id, 0)[1]
    
    @property
    def snow_depth(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 0, self._obj_id, 1)[1]

    @property
    def evap(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 0, self._obj_id, 2)[1]

    @property
    def infil(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 0, self._obj_id, 3)[1]

    @property
    def runoff(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 0, self._obj_id, 4)[1]

    @property
    def gw_flow(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 0, self._obj_id, 5)[1]

    @property
    def gw_elev(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 0, self._obj_id, 6)[1]

    @property
    def soil_moist(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 0, self._obj_id, 7)[1]

class SwmmNode(_SwmmObj):
    
    def __init__(self, sim, inp_id, node_id):
        super().__init__(sim, inp_id, 'Node', node_id)
    
    @property
    def invert_elev(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 1, self._obj_id, 0)[1]
    
    @invert_elev.setter
    def invert_elev(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 1, self._obj_id, 0 ,value)
    
    @property
    def init_depth(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 1, self._obj_id, 1)[1]
    
    @init_depth.setter
    def init_depth(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 1, self._obj_id, 1 ,value)
    
    @property
    def full_depth(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 1, self._obj_id, 2)[1]
    
    @full_depth.setter
    def full_depth(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 1, self._obj_id, 2 ,value)
    
    @property
    def sur_depth(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 1, self._obj_id, 3)[1]
    
    @sur_depth.setter
    def sur_depth(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 1, self._obj_id, 3 ,value)
    
    @property
    def ponded_area(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 1, self._obj_id, 4)[1]
    
    @ponded_area.setter
    def ponded_area(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 1, self._obj_id, 4 ,value)
    
    @property
    def depth(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 1, self._obj_id, 0)[1]
    
    @depth.setter
    def depth(self, value):
        return self._model.simuwater_setSwmmNodeDepth(self._inp_id, self._obj_id, value)
    
    @property
    def head(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 1, self._obj_id, 1)[1]
    
    @property
    def volume(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 1, self._obj_id, 2)[1]
    
    @property
    def lateral_inflow(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 1, self._obj_id, 3)[1]
    
    @property
    def total_inflow(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 1, self._obj_id, 4)[1]
   
    @property
    def overflow(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 1, self._obj_id, 5)[1]
    
    def __set_external_inflow(self, ext_inflow):
        return self._model.simuwater_setSwmmExtInflow(self._inp_id, self._obj_id, ext_inflow)   
    
    external_inflow = property(None, __set_external_inflow)    # 控制参数
    
class SwmmJunction(SwmmNode):
    
    def __init__(self, sim, inp_id, junction_id):
        super().__init__(sim, inp_id, junction_id)
        
class SwmmOutfall(SwmmNode):
    
    def __init__(self, sim, inp_id, outfall_id):
        super().__init__(sim, inp_id, outfall_id)
        
    @property
    def has_flapgate(self):
        return self._model.simuwater_getSwmmNodeParam(self._inp_id, 1, self._obj_id, 0)[1]
    
    @has_flapgate.setter
    def has_flapgate(self, value):
        self._model.simuwater_setSwmmNodeParam(self._inp_id, 1, self._obj_id, 0, value)
    
    @property
    def fixed_stage(self):
        return self._model.simuwater_getSwmmNodeParam(self._inp_id, 1, self._obj_id, 1)[1]
    
    @fixed_stage.setter
    def fixed_stage(self, value):
        self._model.simuwater_setSwmmNodeParam(self._inp_id, 1, self._obj_id, 1, value)

class SwmmStorage(SwmmNode):
    
    def __init__(self, sim, inp_id, storage_id):
        super().__init__(sim, inp_id, storage_id)
        
    @property
    def fevap(self):
        return self._model.simuwater_getSwmmNodeParam(self._inp_id, 2, self._obj_id, 0)[1]
    
    @fevap.setter
    def fevap(self, value):
        self._model.simuwater_setSwmmNodeParam(self._inp_id, 2, self._obj_id, 0, value)
    
    @property
    def area_const(self):
        return self._model.simuwater_getSwmmNodeParam(self._inp_id, 2, self._obj_id, 1)[1]
    
    @area_const.setter
    def area_const(self, value):
        self._model.simuwater_setSwmmNodeParam(self._inp_id, 2, self._obj_id, 1, value)
    
    @property
    def area_coef(self):
        return self._model.simuwater_getSwmmNodeParam(self._inp_id, 2, self._obj_id, 2)[1]
    
    @area_coef.setter
    def area_coef(self, value):
        self._model.simuwater_setSwmmNodeParam(self._inp_id, 2, self._obj_id, 2, value)
    
    @property
    def area_exp(self):
        return self._model.simuwater_getSwmmNodeParam(self._inp_id, 2, self._obj_id, 3)[1]
    
    @area_exp.setter
    def area_exp(self, value):
        self._model.simuwater_setSwmmNodeParam(self._inp_id, 2, self._obj_id, 3, value)

class SwmmDivider(SwmmNode):
    
    def __init__(self, sim, inp_id, divider_id):
        super().__init__(sim, inp_id, divider_id)
        
    @property
    def min_inflow(self):
        return self._model.simuwater_getSwmmNodeParam(self._inp_id, 3, self._obj_id, 0)[1]
    
    @min_inflow.setter
    def min_inflow(self,value):
        self._model.simuwater_setSwmmNodeParam(self._inp_id, 3, self._obj_id, 0,value)
    
    @property
    def height(self):
        return self._model.simuwater_getSwmmNodeParam(self._inp_id, 3, self._obj_id, 1)[1]
    
    @height.setter
    def height(self,value):
        self._model.simuwater_setSwmmNodeParam(self._inp_id, 3, self._obj_id, 1, value)
    
    @property
    def disc_coef(self):
        return self._model.simuwater_getSwmmNodeParam(self._inp_id, 3, self._obj_id, 2)[1]
    
    @disc_coef.setter
    def disc_coef(self,value):
        self._model.simuwater_setSwmmNodeParam(self._inp_id, 3, self._obj_id, 2, value)

class SwmmLink(_SwmmObj):
    
    def __init__(self, sim, inp_id, link_id):
        super().__init__(sim, inp_id, 'Link', link_id)
        
    @property
    def in_offset(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 2, self._obj_id, 0)[1]
    
    @in_offset.setter
    def in_offset(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 2, self._obj_id, 0 ,value)
    
    @property
    def out_offset(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 2, self._obj_id, 1)[1]
    
    @out_offset.setter
    def out_offset(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 2, self._obj_id, 1 ,value)

    @property
    def init_flow(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 2, self._obj_id, 2)[1]
    
    @init_flow.setter
    def init_flow(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 2, self._obj_id, 2 ,value)

    @property
    def limit_flow(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 2, self._obj_id, 3)[1]
    
    @limit_flow.setter
    def limit_flow(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 2, self._obj_id, 3 ,value)

    @property
    def inlet_loss_coef(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 2, self._obj_id, 4)[1]   
    
    @inlet_loss_coef.setter
    def inlet_loss_coef(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 2, self._obj_id, 4 ,value)

    @property
    def outlet_loss_coef(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 2, self._obj_id, 5)[1]  

    @outlet_loss_coef.setter
    def outlet_loss_coef(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 2, self._obj_id, 5 ,value)   
    
    @property
    def avg_loss_coef(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 2, self._obj_id, 6)[1]
    
    @avg_loss_coef.setter
    def avg_loss_coef(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 2, self._obj_id, 6 ,value)
    
    @property
    def seep_rate(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 2, self._obj_id, 7)[1]
    
    @seep_rate.setter
    def seep_rate(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 2, self._obj_id, 7 ,value)
    
    @property
    def has_flapgate(self):
        return self._model.simuwater_getSwmmParam(self._inp_id, 2, self._obj_id, 8)[1]
    
    @has_flapgate.setter
    def has_flapgate(self, value):
        self._model.simuwater_setSwmmParam(self._inp_id, 2, self._obj_id, 8 ,value)
        
    @property
    def flow(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 2, self._obj_id, 0)[1]
    
    @flow.setter
    def flow(self, value):
        return self._model.simuwater_setSwmmLinkFlow(self._inp_id, self._obj_id, value)
    
    @property
    def depth(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 2, self._obj_id, 1)[1]
    
    @depth.setter
    def depth(self, value):
        return self._model.simuwater_setSwmmLinkDepth(self._inp_id, self._obj_id, value)
    
    @property
    def velocity(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 2, self._obj_id, 2)[1]
    
    @property
    def volume(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 2, self._obj_id, 3)[1]
    
    @property
    def capacity(self):
        return self._model.simuwater_getSwmmResult(self._inp_id, 2, self._obj_id, 4)[1]
    
    @property
    def setting(self):
        return self._model.simuwater_getSwmmSetting(self._inp_id, self._obj_id)[1]    # 控制参数
        
    @setting.setter
    def setting(self, value):
        self._model.simuwater_setSwmmSetting(self._inp_id, self._obj_id, value)    
    
class SwmmConduit(SwmmLink):

    def __init__(self, sim, inp_id, conduit_id):
        super().__init__(sim, inp_id,  conduit_id)
        
    @property
    def length(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 0, self._obj_id, 0)[1]
    
    @length.setter
    def length(self, value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 0, self._obj_id, 0, value)
        
    @property
    def roughness(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 0, self._obj_id, 1)[1]
    
    @roughness.setter
    def roughness(self, value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 0, self._obj_id, 1,value)
        
class SwmmPump(SwmmLink):
    
    def __init__(self, sim, inp_id, pump_id):
        super().__init__(sim, inp_id, pump_id)
        
    @property
    def init_setting(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 1, self._obj_id, 0)[1]
    
    @init_setting.setter
    def init_setting(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 1, self._obj_id, 0, value)
        
    @property
    def on_depth(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 1, self._obj_id, 1)[1]
    
    @on_depth.setter
    def on_depth(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 1, self._obj_id, 1, value)
        
    @property
    def off_depth(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 1, self._obj_id, 2)[1]
    
    @off_depth.setter
    def off_depth(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 1, self._obj_id, 2, value)
        
class SwmmOrifice(SwmmLink):
    
    def __init__(self, sim, inp_id, orifice_id):
        super().__init__(sim, inp_id, orifice_id)
        
    @property
    def disc_coef(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 2, self._obj_id, 0)[1]
    
    @disc_coef.setter
    def disc_coef(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 2, self._obj_id, 0, value)
    
    @property
    def open_rate(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 2, self._obj_id, 1)[1]
    
    @open_rate.setter
    def open_rate(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 2, self._obj_id, 1, value)
        
class SwmmWeir(SwmmLink):
    
    def __init__(self, sim, inp_id, weir_id):
        super().__init__(sim, inp_id, weir_id)

    @property
    def disc_1(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 3, self._obj_id, 0)[1]
    
    @disc_1.setter
    def disc_1(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 3, self._obj_id, 0, value)

    @property
    def disc_2(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 3, self._obj_id, 1)[1]
    
    @disc_2.setter
    def disc_2(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 3, self._obj_id, 1, value)

    @property
    def end_con(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 3, self._obj_id, 2)[1]
    
    @end_con.setter
    def end_con(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 3, self._obj_id, 2, value)

    @property
    def can_sur(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 3, self._obj_id, 3)[1]
    
    @can_sur.setter
    def can_sur(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 3, self._obj_id, 3, value)

    @property
    def road_width(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 3, self._obj_id, 4)[1]
    
    @road_width.setter
    def road_width(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 3, self._obj_id, 4, value)
        
class SwmmOutlet(SwmmLink):
    
    def __init__(self, sim, inp_id, outlet_id):
        super().__init__(sim, inp_id, outlet_id)
        
    @property
    def disc_coef(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 4, self._obj_id, 0)[1]
    
    @disc_coef.setter
    def disc_coef(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 4, self._obj_id, 0, value)    

    @property
    def disc_exp(self):
        return self._model.simuwater_getSwmmLinkParam(self._inp_id, 4, self._obj_id, 1)[1]
    
    @disc_exp.setter
    def disc_exp(self,value):
        self._model.simuwater_setSwmmLinkParam(self._inp_id, 4, self._obj_id, 1, value)  
