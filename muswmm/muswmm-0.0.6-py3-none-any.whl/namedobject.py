# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 23:54:35 2021

@author: mumuz
"""

import muswmm.lib
from muswmm.errors import *
from muswmm.geometry import *
import datetime

from Mumu.SWMM.SwmmObjects import Subcatchment as SwmmSubcatchment
from Mumu.SWMM.SwmmObjects import Subarea as SwmmSubarea
from Mumu.SWMM.SwmmObjects import Infiltration as SwmmInfiltration
from Mumu.SWMM.SwmmObjects import Polygon as SwmmPolygon
from Mumu.SWMM.SwmmObjects import Junction as SwmmJunction
from Mumu.SWMM.SwmmObjects import Outfall as SwmmOutfall
from Mumu.SWMM.SwmmObjects import Storage as SwmmStorage
from Mumu.SWMM.SwmmObjects import Divider as SwmmDivider
from Mumu.SWMM.SwmmObjects import Conduit as SwmmConduit
from Mumu.SWMM.SwmmObjects import Pump as SwmmPump
from Mumu.SWMM.SwmmObjects import Orifice as SwmmOrifice
from Mumu.SWMM.SwmmObjects import Weir as SwmmWeir
from Mumu.SWMM.SwmmObjects import Outlet as SwmmOutlet
from Mumu.SWMM.SwmmObjects import Coordinate as SwmmCoordinate
from Mumu.SWMM.SwmmObjects import Vertice as SwmmVertice
from Mumu.SWMM.SwmmObjects import Xsection as SwmmXsection
from Mumu.SWMM.SwmmObjects import RainGage as RainG
from Mumu.SWMM.SwmmObjects import Inflow
from Mumu.SWMM.SwmmObjects import AInflow
from Mumu.SWMM.SwmmObjects import ATimeSerie
from Mumu.SWMM.SwmmObjects import TimeSerie as TimeS

class _Namedobj():
    
    def __init__(self, project, obj_type, name):
        self._prj = project._prj
        self._objs = None
        self._name = name
        if obj_type == 'RainGage':
            self._objs = self._prj.RainGages
        elif obj_type == 'Subcatchment':
            self._objs = self._prj.Subcatchments
        elif obj_type == 'Junction':
            self._objs = self._prj.Junctions
        elif obj_type == 'Outfall':
            self._objs = self._prj.Outfalls
        elif obj_type == 'Storage':
            self._objs = self._prj.Storages
        elif obj_type == 'Divider':
            self._objs = self._prj.Dividers
        elif obj_type == 'Conduit':
            self._objs = self._prj.Conduits
        elif obj_type == 'Pump':
            self._objs = self._prj.Pumps
        elif obj_type == 'Orifice':
            self._objs = self._prj.Orifices
        elif obj_type == 'Weir':
            self._objs = self._prj.Weirs
        elif obj_type == 'Outlet':
            self._objs = self._prj.Outlets
        elif obj_type == 'TimeSerie':
            self._objs = self._prj.TimeSeries
        self._obj_type = obj_type
        self._obj = self._objs.GetItem(
                self._objs.GetIndex(name))
        
        self._geometry = None
        
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._objs.GetIndex(value) < 0:
            raise Exception(ERROR_IDNOTEXIST.format(value))
        self._obj.Name = value
        self._name = value    
        
    @property
    def description(self):
        return self._obj.Descrip
    
    @description.setter
    def description(self, value):
        self._obj.Descrip = value  
        
    def remove(self):
        return self._objs.Remove(self._name)        


class RainGage(_Namedobj):
    
    def __init__(self, project, name):
        super().__init__(project, 'RainGage', name)

    @property
    def data_format(self):
        return self._obj.Format
    
    @data_format.setter
    def data_format(self, value):
        self._obj.Format = value
        
    @property
    def interval(self):
        return self._obj.Interval
    
    @interval.setter
    def interval(self, value):
        self._obj.Interval = value

    @property
    def scf(self):
        return self._obj.SCF
    
    @scf.setter
    def scf(self, value):
        self._obj.SCF = value
        
    @property
    def source(self):
        return self._obj.Source
    
    @source.setter
    def source(self, value):
        self._obj.Source = value
        
    @property
    def ts(self):
        return self._obj.TS
    
    @ts.setter
    def ts(self, value):
        self._obj.TS = value
        
    @property
    def file(self):
        return self._obj.File
    
    @file.setter
    def file(self, value):
        self._obj.File = value
        
    @property
    def sta_id(self):
        return self._obj.StaID
    
    @sta_id.setter
    def sta_id(self, value):
        self._obj.StaID = value
        
    @property
    def units(self):
        return self._obj.Units
    
    @units.setter
    def units(self, value):
        self._obj.Units = value
        
    @staticmethod
    def new(project):
        new_gage = RainG()        
        new_gage.Name = project._prj.RainGages.NameControl.Create('RG_')
        project._prj.RainGages.Add(new_gage)
        return RainGage(project, new_gage.Name)

class Subcatchment(_Namedobj):
    
    def __init__(self, project, name):
        super().__init__(project, 'Subcatchment',name)
        self._subarea = self._prj.Subareas.GetItem(
                        self._prj.Subareas.GetIndex(self._name))
        self._infil = self._prj.Infiltrations.GetItem(
                      self._prj.Infiltrations.GetIndex(self._name))
        self._geometry = self._prj.Polygons.GetItem(
                         self._prj.Polygons.GetIndex(self._name))
    
    @property
    def outlet(self):
        return self._obj.Outlet
    
    @outlet.setter
    def outlet(self, value):
        self._obj.Outlet = value
        
    @property
    def gage(self):
        return self._obj.RainGage
    
    @gage.setter
    def gage(self,value):
        self._obj.RainGage = value
            
    @property
    def area(self):
        return self._obj.Area
    
    @area.setter
    def area(self, value):
        self._obj.Area = value
        
    @property
    def imperv(self):
        return self._obj.Imperv
    
    @imperv.setter
    def imperv(self,value):
        self._obj.Imperv = value
    
    @property
    def width(self):
        return self._obj.Width
    
    @width.setter
    def width(self,value):
        self._obj.Width = value

    @property
    def slope(self):
        return self._obj.Slope
    
    @slope.setter
    def slope(self,value):
        self._obj.Slope = value

    @property
    def curb_len(self):
        return self._obj.CurbLen
    
    @curb_len.setter
    def curb_len(self,value):
        self._obj.CurbLen = value

    @property
    def snow_pack(self):
        return self._obj.Imperv
    
    @snow_pack.setter
    def snow_pack(self,value):
        self._obj.SnowPack = value
        
    @property
    def max_rate(self):
        return self._infil.MaxRate
    
    @max_rate.setter
    def max_rate(self, value):
        self._infil.MaxRate = value
    
    @property
    def min_rate(self):
        return self._infil.MinRate
    
    @min_rate.setter
    def min_rate(self,value):
        self._infil.MinRate = value   
        
    @property
    def decay(self):
        return self._infil.Decay
    
    @decay.setter
    def decay(self,value):
        self._infil.Decay = value
        
    @property
    def dry_time(self):
        return self._infil.DryTime
    
    @dry_time.setter
    def dry_time(self,value):
        self._infil.DryTime = value   
        
    @property
    def max_infil(self):
        return self._infil.Decay
    
    @max_infil.setter
    def max_infil(self,value):
        self._infil.MaxInfil = value   

    @property
    def suction(self):
        return self._infil.Suction
    
    @suction.setter
    def suction(self,value):
        self._infil.Decay = value   
        
    @property
    def conduct(self):
        return self._infil.Conduct
    
    @conduct.setter
    def conduct(self,value):
        self._infil.Conduct = value   
        
    @property
    def init_defic(self):
        return self._infil.InitDefic
    
    @init_defic.setter
    def init_defic(self,value):
        self._infil.InitDefic = value   
        
    @property
    def curve_num(self):
        return self._infil.CurveNum
    
    @curve_num.setter
    def curve_num(self,value):
        self._infil.CurveNum = value 
        
    @property
    def infil_mode(self):
        return self._infil.InfilMode
    
    @infil_mode.setter
    def infil_mode(self,value):
        self._infil.InfilMode = value 
    
    @property
    def n_imperv(self):
        return self._subarea.NImperv
    
    @n_imperv.setter
    def n_imperv(self,value):
        self._subarea.NImperv = value 

    @property
    def n_perv(self):
        return self._subarea.NPerv
    
    @n_perv.setter
    def n_perv(self,value):
        self._subarea.NPerv = value 

    @property
    def s_imperv(self):
        return self._subarea.SImperv
    
    @s_imperv.setter
    def s_imperv(self,value):
        self._subarea.SImperv = value 

    @property
    def s_perv(self):
        return self._subarea.SPerv
    
    @s_perv.setter
    def s_perv(self,value):
        self._subarea.SPerv = value 
        
    @property
    def route_to(self):
        return self._subarea.RouteTo
    
    @route_to.setter
    def route_to(self,value):
        self._subarea.RouteTo = value 
        
    @property
    def pct_routed(self):
        return self._subarea.PctRouted
    
    @pct_routed.setter
    def pct_routed(self,value):
        self._subarea.PctRouted = value
        
    @property
    def polygon(self):
        points = Points()
        points.swmm_points = self._geometry.Collection
        return points
    
    @polygon.setter
    def polygon(self,value):
        if len(value) < 3:
            raise Exception(ERROR_POLYGONLESSVERTEX)
        self._geometry.Collection = value.swmm_points
    
    @staticmethod
    def new(project, polygon):
        if len(polygon) < 3:
            raise Exception(ERROR_POLYGONLESSVERTEX)
        new_subcatchment = SwmmSubcatchment()
        new_subarea = SwmmSubarea()
        new_infiltration = SwmmInfiltration(project._prj.Options.Infil)
        new_polygon = SwmmPolygon()
        new_subcatchment.Name = project._prj.NameControl_1.Create('S_')
        new_subarea.Name = new_subcatchment.Name
        new_infiltration.Name = new_subcatchment.Name
        new_polygon.Name = new_subcatchment.Name
        new_polygon.FromListPoint(polygon.swmm_points)
        project._prj.Subcatchments.Add(new_subcatchment)
        project._prj.Subareas.Add(new_subarea)
        project._prj.Infiltrations.Add(new_infiltration)
        project._prj.Polygons.Add(new_polygon)
        return Subcatchment(project, new_subcatchment.Name)        
    

class _Node(_Namedobj):
    
    def __init__(self, project, obj_type, name):
        super().__init__(project, obj_type, name)
        self._geometry = self._prj.Coordinates.GetItem(
                      self._prj.Coordinates.GetIndex(name))   

    @property
    def invert_elev(self):
        return self._obj.InvertElev
    
    @invert_elev.setter
    def invert_elev(self, value):
        self._obj.InvertElev = value

    @property
    def point(self):
        point = Point()
        point.swmm_point = self._geometry.Point
        return point
    
    @point.setter
    def point(self, value):
        self._geometry.Point = value.swmm_point
        
    def __get_inflow_param(self, constituent, param_type):
        inflow = None
        if self._prj.Inflows.GetIndex(self._name) >= 0:
            inflow = self._prj.Inflows.GetItem(
                    self._prj.Inflows.GetIndex(self._name))
        if inflow != None:
            for i in range(0, inflow.Collection.Count):
                ainflow = inflow.Collection.GetItem(i)
                if ainflow.Constituent == constituent:
                    if param_type == 'BASELINE':
                        return ainflow.BaseLine
                    elif param_type == 'TIMESERIE':
                        return ainflow.TimeSerie
                    elif param_type == 'TYPE':
                        return ainflow.Type
                    elif param_type == 'MFACTOR':
                        return ainflow.MFactor
                    elif param_type == 'SFACTOR':
                        return ainflow.SFactor
                    elif param_type == 'PATTERN':
                        return ainflow.Pattern
        if param_type == 'BASELINE':
            return 0.0
        elif param_type == 'TIMESERIE':
            return ''
        elif param_type == 'TYPE':
            return ''
        elif param_type == 'MFACTOR':
            return 0.0
        elif param_type == 'SFACTOR':
            return 0.0
        elif param_type == 'PATTERN':
            return ''
    
    def __set_inflow_param(self, constituent, param_type, value):
        inflow = None
        if self._prj.Inflows.GetIndex(self._name) >= 0:
            inflow = self._prj.Inflows.GetItem(
                    self._prj.Inflows.GetIndex(self._name))
        if inflow != None:
            flag = False
            for i in range(0, inflow.Collection.Count):
                ainflow = inflow.Collection.GetItem(i)
                if ainflow.Constituent == constituent:
                    if param_type == 'BASELINE':
                        ainflow.BaseLine = value
                    elif param_type == 'TIMESERIE':
                        ainflow.TimeSerie = value
                    elif param_type == 'TYPE':
                        ainflow.Type = value
                    elif param_type == 'MFACTOR':
                        ainflow.MFactor = value
                    elif param_type == 'SFACTOR':
                        ainflow.SFactor = value
                    elif param_type == 'PATTERN':
                        ainflow.Pattern = value
                    if ainflow.BaseLine <= 0.0 and ainflow.TimeSerie == '':
                        inflow.Collection.Remove(i)
                    flag = True
                    break
            if not flag:
                flag1 = False
                if param_type == 'BASELINE':
                    if value > 0.0:
                        flag1 = True
                elif param_type == 'TIMESERIE':
                    if value != '':
                        flag1 = True
                if not flag1:
                    return
                ainflow = AInflow()
                ainflow.Constituent = constituent
                if param_type == 'BASELINE':
                    ainflow.BaseLine = value
                elif param_type == 'TIMESERIE':
                    ainflow.TimeSerie = value
                if constituent != 'FLOW':
                    ainflow.Type = 'CONCEN'
                else:
                    ainflow.Type = 'FLOW'
                inflow.Collection.Add(ainflow)
        else:
            flag = False
            if param_type == 'BASELINE':
                if value > 0.0:
                    flag = True
            elif param_type == 'TIMESERIE':
                if value != '':
                    flag = True
            if not flag:
                return
            inflow = Inflow()
            inflow.Name = self._name
            ainflow = AInflow()
            ainflow.Constituent = constituent
            if param_type == 'BASELINE':
                ainflow.BaseLine = value
            elif param_type == 'TIMESERIE':
                ainflow.TimeSerie = value
            if constituent != 'FLOW':
                ainflow.Type = 'CONCEN'
            else:
                ainflow.Type = 'FLOW'
            inflow.Collection.Add(ainflow)
            self._prj.Inflows.Add(inflow)
    
    def get_inflow_baseline(self, constituent):
        return self.__get_inflow_param(constituent, 'BASELINE')
            
    def set_inflow_baseline(self, constituent, value):
        self.__set_inflow_param(constituent, 'BASELINE', value)
    
    def get_inflow_timeserie(self, constituent):
        return self.__get_inflow_param(constituent, 'TIMESERIE')
            
    def set_inflow_timeserie(self, constituent, value):
        self.__set_inflow_param(constituent, 'TIMESERIE', value)

    def get_inflow_type(self, constituent):
        return self.__get_inflow_param(constituent, 'TYPE')
            
    def set_inflow_type(self, constituent, value):
        self.__set_inflow_param(constituent, 'TYPE', value)
        
    def get_inflow_mfactor(self, constituent):
        return self.__get_inflow_param(constituent, 'MFACTOR')
            
    def set_inflow_mfactor(self, constituent, value):
        self.__set_inflow_param(constituent, 'MFACTOR', value)
        
    def get_inflow_sfactor(self, constituent):
        return self.__get_inflow_param(constituent, 'SFACTOR')
            
    def set_inflow_sfactor(self, constituent, value):
        self.__set_inflow_param(constituent, 'SFACTOR', value)
        
    def get_inflow_pattern(self, constituent):
        return self.__get_inflow_param(constituent, 'PATTERN')
            
    def set_inflow_pattern(self, constituent, value):
        self.__set_inflow_param(constituent, 'PATTERN', value)
        
    @staticmethod
    def new(project, obj_type, point):
        nodes = None
        new_node = None
        prefix = ''
        if obj_type == 'Junction':
            nodes = project._prj.Junctions
            new_node = SwmmJunction()
            prefix = 'J_'
        elif obj_type == 'Outfall':
            nodes = project._prj.Outfalls
            new_node = SwmmOutfall()
            prefix = 'OF_'
        elif obj_type == 'Storage':
            nodes = project._prj.Storages
            new_node = SwmmStorage()
            prefix = 'SU_'
        elif obj_type == 'Divider':
            nodes = project._prj.Dividers
            new_node = SwmmDivider()
            prefix = 'D_'
        else:
            return None
        new_node.Name = project._prj.NameControl_1.Create(prefix)
        new_coord = SwmmCoordinate()
        new_coord.Name = new_node.Name
        new_coord.Point = point.swmm_point
        nodes.Add(new_node)
        project._prj.Coordinates.Add(new_coord)
        if obj_type == 'Junction':
            return Junction(project, new_node.Name)
        elif obj_type == 'Outfall':
            return Outfall(project, new_node.Name)
        elif obj_type == 'Storage':
            return Storage(project, new_node.Name)
        elif obj_type == 'Divider':
            return Divider(project, new_node.Name)
        else:
            return None
    

class Junction(_Node):
    
    def __init__(self, project, name):
        super().__init__(project, 'Junction', name)
        
    @property
    def max_depth(self):
        return self._obj.MaxDepth
    
    @max_depth.setter
    def max_depth(self, value):
        self._obj.MaxDepth = value

    @property
    def init_depth(self):
        return self._obj.InitDepth
    
    @init_depth.setter
    def init_depth(self, value):
        self._obj.InitDepth = value

    @property
    def sur_depth(self):
        return self._obj.SurDepth
    
    @sur_depth.setter
    def sur_depth(self, value):
        self._obj.SurDepth = value

    @property
    def aponded(self):
        return self._obj.Aponded
    
    @aponded.setter
    def aponded(self, value):
        self._obj.Aponded = value
        
    @staticmethod
    def new(project, point):
        return _Node.new(project, 'Junction', point)
        

class Outfall(_Node):
    
    def __init__(self, project, name):
        super().__init__(project, 'Outfall', name)

    @property
    def outfall_type(self):
        return self._obj.Type
    
    @outfall_type.setter
    def outfall_type(self, value):
        self._obj.Type = value
        
    @property
    def fixed_stage(self):
        return self._obj.FixedStage
    
    @fixed_stage.setter
    def fixed_stage(self, value):
        self._obj.FixedStage = value
        
    @property
    def curve_name(self):
        return self._obj.curve_name
    
    @curve_name.setter
    def curve_name(self, value):
        self._obj.CurveName = value
        
    @property
    def series_name(self):
        return self._obj.SeriesName
    
    @series_name.setter
    def series_name(self, value):
        self._obj.SeriesName = value
        
    @property
    def gaged(self):
        return self._obj.Gaged
    
    @gaged.setter
    def gaged(self, value):
        self._obj.Gaged = value
        
    @property
    def routed_to(self):
        return self._obj.RoutedTo
    
    @routed_to.setter
    def routed_to(self, value):
        self._obj.RoutedTo = value
        
    @staticmethod
    def new(project, point):
        return _Node.new(project, 'Outfall', point)
        

class Storage(_Node):
    
    def __init__(self, project, name):
        super().__init__(project, 'Storage', name)
        
    @property
    def max_depth(self):
        return self._obj.MaxDepth
    
    @max_depth.setter
    def max_depth(self, value):
        self._obj.MaxDepth = value

    @property
    def init_depth(self):
        return self._obj.InitDepth
    
    @init_depth.setter
    def init_depth(self, value):
        self._obj.InitDepth = value

    @property
    def store_curve(self):
        return self._obj.StoreCurve
    
    @store_curve.setter
    def store_curve(self, value):
        self._obj.StoreCurve = value

    @property
    def fc_coef(self):
        return self._obj.FC_Coef
    
    @fc_coef.setter
    def fc_coef(self, value):
        self._obj.FC_Coef = value
        
    @property
    def fc_exp(self):
        return self._obj.FC_EXP
    
    @fc_exp.setter
    def fc_exp(self, value):
        self._obj.FC_EXP = value
        
    @property
    def fc_cons(self):
        return self._obj.FC_Cons
    
    @fc_cons.setter
    def fc_cons(self, value):
        self._obj.FC_Cons = value
        
    @property
    def tc_cn(self):
        return self._obj.TC_CN
    
    @tc_cn.setter
    def tc_cn(self, value):
        self._obj.TC_CN = value
        
    @property
    def fevap(self):
        return self._obj.FEvap
    
    @fevap.setter
    def fevap(self, value):
        self._obj.FEvap = value
        
    @property
    def suction(self):
        return self._obj.Suction
    
    @suction.setter
    def suction(self, value):
        self._obj.Suction = value        
    
    @property
    def init_defic(self):
        return self._obj.InitDefic
    
    @init_defic.setter
    def init_defic(self, value):
        self._obj.InitDefic = value        

    @property
    def conduct(self):
        return self._obj.Conduct
    
    @conduct.setter
    def conduct(self, value):
        self._obj.Conduct = value     
        
    @staticmethod
    def new(project, point):
        return _Node.new(project, 'Storage', point)
        
        
class Divider(_Node):
    
    def __init__(self, project, name):
        super().__init__(project, 'Divider', name)
        
    @property
    def max_depth(self):
        return self._obj.MaxDepth
    
    @max_depth.setter
    def max_depth(self, value):
        self._obj.MaxDepth = value

    @property
    def init_depth(self):
        return self._obj.InitDepth
    
    @init_depth.setter
    def init_depth(self, value):
        self._obj.InitDepth = value

    @property
    def aponded(self):
        return self._obj.Aponded
    
    @aponded.setter
    def aponded(self, value):
        self._obj.Aponded = value
        
    @property
    def divert_link(self):
        return self._obj.DivertLink
    
    @divert_link.setter
    def divert_link(self, value):
        self._obj.DivertLink = value
        
    @property
    def divider_type(self):
        return self._obj.Type
    
    @divider_type.setter
    def divider_type(self, value):
        self._obj.Type = value
        
    @property
    def cd_cutflow(self):
        return self._obj.CD_CutFlow
    
    @cd_cutflow.setter
    def cd_cutflow(self, value):
        self._obj.CD_CutFlow = value
        
    @property
    def td_cn(self):
        return self._obj.TD_CN
    
    @td_cn.setter
    def td_cn(self, value):
        self._obj.CD_CutFlow = value

    @property
    def wd_minflow(self):
        return self._obj.WD_MinFlow

    @wd_minflow.setter
    def wd_minflow(self, value):
        self._obj.WD_MinFlow = value                 
                
    @property
    def wd_maxdep(self):
        return self._obj.WD_MaxDep

    @wd_maxdep.setter
    def wd_maxdep(self, value):
        self._obj.WD_MaxDep = value 

    @property
    def wd_coef(self):
        return self._obj.WD_Coef

    @wd_coef.setter
    def wd_coef(self, value):
        self._obj.WD_Coef = value

    @staticmethod
    def new(project, point):
        return _Node.new(project, 'Divider', point)
        

class _Link(_Namedobj):
    
    def __init__(self, project, obj_type, name):
        super().__init__(project, obj_type, name)
        self._geometry = None
        if self._prj.Vertices.GetIndex(name) >= 0:          
            self._geometry = self._prj.Vertices.GetItem(
                          self._prj.Vertices.GetIndex(name))
        
    @property
    def from_node(self):
        return self._obj.FromNode
    
    @from_node.setter
    def from_node(self, value):
        self._obj.FromNode = value

    @property
    def to_node(self):
        return self._obj.ToNode
    
    @to_node.setter
    def to_node(self, value):
        self._obj.ToNode = value

    @property
    def polyline(self):
        points = Points()  
        from_point = Point()
        from_point.swmm_point = self._prj.Coordinates.GetItem(
                self._prj.Coordinates.GetIndex(self.from_node)).Point
        to_point = Point()
        to_point.point = self._prj.Coordinates.GetItem(
                self._prj.Coordinates.GetIndex(self.to_node)).Point
        points.add(from_point)
        if self._geometry is not None:
            for i in range(0, int(len(self._geometry.Collection.ToList()))):
                point = Point()
                point.swmm_point = self._geometry.Collection.ToList()[i]
                points.add(point)
        points.add(to_point)
        points.swmm_points = self._geometry.Collection
        return points
    
    @polyline.setter
    def polyline(self,value):
        if len(value) < 2:
            raise Exception(ERROR_POLYLINELESSVERTEX)
        points = Points()
        for i in range(1, len(value)-1):
            points.add(value[i])
        self._geometry.Collection = points.swmm_points

    @staticmethod
    def new(project, obj_type, from_node, to_node, vertice):
        links = None
        new_link = None
        new_xsect = None
        prefix = ''
        if obj_type == 'Conduit':
            links = project._prj.Conduits
            new_link = SwmmConduit()
            new_xsect = SwmmXsection()
            prefix = 'C_'
        elif obj_type == 'Pump':
            links = project._prj.Pumps
            new_link = SwmmPump()
            prefix = 'P_'
        elif obj_type == 'Orifice':
            links = project._prj.Orifices
            new_link = SwmmOrifice()
            new_xsect = SwmmXsection()
            prefix = 'OR_'
        elif obj_type == 'Weir':
            links = project._prj.Weirs
            new_link = SwmmWeir()
            new_xsect = SwmmXsection()
            prefix = 'W_'
        elif obj_type == 'Outlet':
            links = project._prj.Outlets
            new_link = SwmmOutlet()
            prefix = 'OL_'
        else:
            return None
        new_link.Name = project._prj.NameControl_1.Create(prefix)
        new_link.FromNode = from_node
        new_link.ToNode = to_node
        links.Add(new_link)
        if len(vertice) >= 3:
            points = Points()
            for i in range(1, len(vertice) - 1):
                points.add(vertice[i])
            new_vertice = SwmmVertice()
            new_vertice.Name = new_link.Name
            new_vertice.FromListPoint(points.swmm_points)
            project._prj.Vertices.Add(new_vertice)
        if new_xsect != None:
            new_xsect.Name = new_link.Name
            project._prj.Xsections.Add(new_xsect)
        if obj_type == 'Conduit':
            return Conduit(project,new_link.Name)
        elif obj_type == 'Pump':
            return Pump(project, new_link.Name)
        elif obj_type == 'Orifice':
            return Orifice(project, new_link.Name)
        elif obj_type == 'Weir':
            return Weir(project, new_link.Name)
        elif obj_type == 'Outlet':
            return Outlet(project, new_link.Name)
        else:
            return None  
        

class Conduit(_Link):
    
    def __init__(self, project, name):
        super().__init__(project, 'Conduit', name)
        self._xsect = self._prj.Xsections.GetItem(
                self._prj.Xsections.GetIndex(name))
    
    @property
    def length(self):
        return self._obj.Length
    
    @length.setter
    def length(self, value):
        self._obj.Length = value
        
    @property
    def roughness(self):
        return self._obj.Roughness
    
    @roughness.setter
    def roughness(self, value):
        self._obj.Roughness = value        
    
    @property
    def in_offset(self):
        return self._obj.InOffset
    
    @in_offset.setter
    def in_offset(self, value):
        self._obj.InOffset = value     
            
    @property
    def out_offset(self):
        return self._obj.OutOffset
    
    @out_offset.setter
    def out_offset(self, value):
        self._obj.OutOffset = value 
        
    @property
    def init_flow(self):
        return self._obj.InitFlow
    
    @init_flow.setter
    def init_flow(self, value):
        self._obj.InitFlow = value
        
    @property
    def max_flow(self):
        return self._obj.MaxFlow
    
    @max_flow.setter
    def max_flow(self, value):
        self._obj.MaxFlow = value 
    
    @property
    def xsect(self):
        return self._xsect.Xsect
    
    @xsect.setter
    def xsect(self,value):
        self._xsect.Xsect = value

    @property
    def geom1(self):
        return self._xsect.Geom1
    
    @geom1.setter
    def geom1(self,value):
        self._xsect.Geom1 = value

    @property
    def geom2(self):
        return self._xsect.Geom2
    
    @geom1.setter
    def geom2(self,value):
        self._xsect.Geom2 = value
        
    @property
    def geom3(self):
        return self._xsect.Geom3
    
    @geom3.setter
    def geom3(self,value):
        self._xsect.Geom3 = value

    @property
    def geom4(self):
        return self._xsect.Geom4
    
    @geom4.setter
    def geom4(self,value):
        self._xsect.Geom4 = value
        
    @property
    def barrel(self):
        return self._xsect.Barrel
    
    @barrel.setter
    def barrel(self,value):
        self._xsect.Barrel = value
        
    @property
    def culvert(self):
        return self._xsect.Culvert
    
    @culvert.setter
    def culvert(self,value):
        self._xsect.Culvert = value
        

class Pump(_Link):
    
    def __init__(self, project, name):
        super().__init__(project, 'Pump', name)
    
    @property
    def pump_curve(self):
        return self._obj.PumpCurve
    
    @pump_curve.setter
    def pump_curve(self, value):
        self._obj.PumpCurve = value
        
    @property
    def init_status(self):
        return self._obj.InitStatus
    
    @init_status.setter
    def init_status(self, value):
        self._obj.InitStatus = value
        
    @property
    def start_depth(self):
        return self._obj.StartDepth
    
    @start_depth.setter
    def start_depth(self, value):
        self._obj.StartDepth = value

    @property
    def shut_depth(self):
        return self._obj.ShutDepth
    
    @shut_depth.setter
    def shut_depth(self, value):
        self._obj.ShutDepth = value
        

class Orifice(_Link):
    
    def __init__(self, project, name):
        super().__init__(project, 'Orifice', name)
        self._xsect = self._prj.Xsections.GetItem(
                self._prj.Xsections.GetIndex(name))
    
    @property
    def orifice_type(self):
        return self._obj.Type
    
    @orifice_type.setter
    def orifice_type(self, value):
        self._obj.Type = value
        
    @property
    def offset(self):
        return self._obj.Offset
    
    @offset.setter
    def offset(self, value):
        self._obj.Offset = value
        
    @property
    def ds_coef(self):
        return self._obj.DsCoef
    
    @ds_coef.setter
    def ds_coef(self, value):
        self._obj.DsCoef = value

    @property
    def flap_gage(self):
        return self._obj.FlapGage
    
    @offset.setter
    def flag_gage(self, value):
        self._obj.FlapGage = value

    @property
    def close_time(self):
        return self._obj.CloseTime
    
    @close_time.setter
    def close_time(self, value):
        self._obj.CloseTime = value

    @property
    def xsect(self):
        return self._xsect.Xsect
    
    @xsect.setter
    def xsect(self,value):
        self._xsect.Xsect = value

    @property
    def geom1(self):
        return self._xsect.Geom1
    
    @geom1.setter
    def geom1(self,value):
        self._xsect.Geom1 = value

    @property
    def geom2(self):
        return self._xsect.Geom2
    
    @geom1.setter
    def geom2(self,value):
        self._xsect.Geom2 = value
        
    @property
    def geom3(self):
        return self._xsect.Geom3
    
    @geom3.setter
    def geom3(self,value):
        self._xsect.Geom3 = value

    @property
    def geom4(self):
        return self._xsect.Geom4
    
    @geom4.setter
    def geom4(self,value):
        self._xsect.Geom4 = value
        
    @property
    def barrel(self):
        return self._xsect.Barrel
    
    @barrel.setter
    def barrel(self,value):
        self._xsect.Barrel = value
        
    @property
    def culvert(self):
        return self._xsect.Culvert
    
    @culvert.setter
    def culvert(self,value):
        self._xsect.Culvert = value
        

class Weir(_Link):
    
    def __init__(self, project, name):
        super().__init__(project, 'Orifice', name)
        self._xsect = self._prj.Xsections.GetItem(
                self._prj.Xsections.GetIndex(name))
    
    @property
    def weir_type(self):
        return self._obj.Type
    
    @weir_type.setter
    def weir_type(self, value):
        self._obj.Type = value
        
    @property
    def offset(self):
        return self._obj.InOffset
    
    @offset.setter
    def offset(self, value):
        self._obj.InOffset = value
        
    @property
    def ds_coef(self):
        return self._obj.DsCoef
    
    @ds_coef.setter
    def ds_coef(self, value):
        self._obj.DsCoef = value

    @property
    def flap_gage(self):
        return self._obj.FlapGage
    
    @offset.setter
    def flag_gage(self, value):
        self._obj.FlapGage = value    

    @property
    def end_cont(self):
        return self._obj.EndCont
    
    @end_cont.setter
    def end_cont(self, value):
        self._obj.EndCont = value
        
    @property
    def end_coef(self):
        return self._obj.EndCoef
    
    @end_coef.setter
    def end_coef(self, value):
        self._obj.EndCoef = value
        
    @property
    def can_sur(self):
        return self._obj.CanSur
    
    @can_sur.setter
    def can_sur(self,value):
        self._obj.CanSur = value    
    
    @property
    def road_width(self):
        return self._obj.RoadWidth
    
    @road_width.setter
    def road_width(self,value):
        self._obj.RoadWidth = value   
        
    @property
    def road_surf(self):
        return self._obj.RoadSurf
    
    @road_surf.setter
    def road_surf(self,value):
        self._obj.RoadSurf = value   

    @property
    def coef_curve(self):
        return self._obj.CoefCurve
    
    @coef_curve.setter
    def coef_curve(self,value):
        self._obj.CoefCurve = value   

    @property
    def xsect(self):
        return self._xsect.Xsect
    
    @xsect.setter
    def xsect(self,value):
        self._xsect.Xsect = value

    @property
    def geom1(self):
        return self._xsect.Geom1
    
    @geom1.setter
    def geom1(self,value):
        self._xsect.Geom1 = value

    @property
    def geom2(self):
        return self._xsect.Geom2
    
    @geom1.setter
    def geom2(self,value):
        self._xsect.Geom2 = value
        
    @property
    def geom3(self):
        return self._xsect.Geom3
    
    @geom3.setter
    def geom3(self,value):
        self._xsect.Geom3 = value

    @property
    def geom4(self):
        return self._xsect.Geom4
    
    @geom4.setter
    def geom4(self,value):
        self._xsect.Geom4 = value
        
    @property
    def barrel(self):
        return self._xsect.Barrel
    
    @barrel.setter
    def barrel(self,value):
        self._xsect.Barrel = value
        
    @property
    def culvert(self):
        return self._xsect.Culvert
    
    @culvert.setter
    def culvert(self,value):
        self._xsect.Culvert = value
        

class Outlet(_Link):
    
    def __init__(self, project, name):
        super().__init__(project, 'Outlet', name)
        
    @property
    def offset(self):
        return self._obj.Offset
    
    @offset.setter
    def offset(self, value):
        self._obj.Offset = value

    @property
    def rate_curve(self):
        return self._obj.RateCurve
    
    @rate_curve.setter
    def rate_curve(self, value):
        self._obj.RateCurve = value

    @property
    def fc_coef(self):
        return self._obj.FC_Coef
    
    @fc_coef.setter
    def fc_coef(self, value):
        self._obj.FC_Coef = value
        
    @property
    def fc_exp(self):
        return self._obj.FC_Exp
    
    @fc_exp.setter
    def fc_exp(self, value):
        self._obj.FC_Exp = value

    @property
    def tc_cn(self):
        return self._obj.TC_CN
    
    @tc_cn.setter
    def tc_cn(self, value):
        self._obj.TC_CN = value

    @property
    def flap_gage(self):
        return self._obj.FlapGage
    
    @offset.setter
    def flag_gage(self, value):
        self._obj.FlapGage = value


class TimeSerie(_Namedobj):
    
    def __init__(self, project, name):
        super().__init__(project, 'TimeSerie', name)
        
    @property
    def is_file(self):
        return self._obj.IsFile
    
    @is_file.setter
    def is_file(self, value):
        self._obj.IsFile = value
        
    @property
    def file(self):
        return self._obj.File
    
    @file.setter
    def file(self, value):
        self._obj.File = value
        
    @property
    def ts(self):
        if self.is_file:
            return None
        dic = dict()
        for i in range(0, self._obj.Collection.Count):
            ats = self._obj.Collection.GetItem(i)
            dt = datetime.datetime.strptime(ats.Date + ' ' + ats.Time,'%m/%d/%Y %H:%M')
            dic[dt] = ats.Value
        return dic
    
    @ts.setter
    def ts(self, value):
        if self.is_file:
            return
        if not isinstance(value, dict):
            return
        if len(value) == 0:
            return
        self._obj.Collection.RemoveAll()
        for key in value:
            ats = ATimeSerie()
            ats.Date = key.strftime('%m/%d/%Y')
            ats.Time = key.strftime('%H:%M')
            ats.Value = value[key]
            self._obj.Collection.Add(ats)
            
    @staticmethod
    def new(project):
        new_ts = TimeS()
        new_ts.Name = project._prj.TimeSeries.NameControl.Create('TS_')
        project._prj.TimeSeries.Add(new_ts)
        return TimeSerie(project, new_ts.Name)