# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 12:08:11 2021

@author: mumuz
"""


class Options():
    
    def __init__(self, project):
        self._prj = project._prj
        self._options = self._prj.Options
    
    @property
    def flow_unit(self):
        return self._options.FlowUnit
    
    @flow_unit.setter
    def flow_unit(self, value):
        self._options.FlowUnit = value
        
    @property
    def infil(self):
        return self._options.Infil
    
    @infil.setter
    def infil(self, value):
        self._options.Infil = value
    
    @property
    def flow_route(self):
        return self._options.FlowRoute
    
    @flow_route.setter
    def flow_route(self, value):
        self._options.FlowRoute = value

    @property
    def start_date(self):
        return self._options.StartDate
    
    @start_date.setter
    def start_date(self, value):
        self._options.StartDate = value

    @property
    def start_time(self):
        return self._options.StartTime
    
    @start_time.setter
    def start_time(self, value):
        self._options.StartTime = value
        
    @property
    def end_date(self):
        return self._options.EndDate
    
    @end_date.setter
    def end_date(self, value):
        self._options.EndDate = value
    
    @property
    def end_time(self):
        return self._options.EndTime
    
    @end_time.setter
    def end_time(self, value):
        self._options.EndTime = value
    
    @property
    def report_start_date(self):
        return self._options.ReportStartDate
    
    @report_start_date.setter
    def report_start_date(self, value):
        self._options.ReportStartDate = value
        
    @property
    def report_start_time(self):
        return self._options.ReportStartTime
    
    @report_start_time.setter
    def report_start_time(self, value):
        self._options.ReportStartTime = value
        
    @property
    def sweep_start(self):
        return self._options.SweepStart
    
    @sweep_start.setter
    def sweep_start(self, value):
        self._options.SweepStart = value
        
    @property
    def sweep_end(self):
        return self._options.SweepEnd
    
    @sweep_end.setter
    def sweep_end(self, value):
        self._options.SweepEnd = value
        
    @property
    def dry_days(self):
        return self._options.DryDays
    
    @dry_days.setter
    def dry_days(self, value):
        self._options.DryDays = value
        
    @property
    def wet_step(self):
        return self._options.WetStep
    
    @wet_step.setter
    def wet_step(self, value):
        self._options.WetStep = value
        
    @property
    def dry_step(self):
        return self._options.DryStep
    
    @dry_step.setter
    def dry_step(self, value):
        self._options.DryStep = value
        
    @property
    def route_step(self):
        return self._options.RouteStep
    
    @route_step.setter
    def route_step(self, value):
        self._options.RouteStep = value
        
    @property
    def rule_step(self):
        return self._options.RuleStep
    
    @rule_step.setter
    def rule_step(self, value):
        self._options.RuleStep = value
        
    @property
    def report_step(self):
        return self._options.ReportStep
    
    @report_step.setter
    def report_step(self, value):
        self._options.ReportStep = value
        
    @property
    def allow_pond(self):
        return self._options.AllowPond
    
    @allow_pond.setter
    def allow_pond(self, value):
        self._options.AllowPond = value
        
    @property
    def inert_damp(self):
        return self._options.InertDamp
    
    @inert_damp.setter
    def inert_damp(self, value):
        self._options.InertDamp = value
        
    @property
    def var_step(self):
        return self._options.VarStep
    
    @var_step.setter
    def var_step(self, value):
        self._options.VarStep = value
        
    @property
    def normal_flow_limited(self):
        return self._options.NormalFlowLimited
    
    @normal_flow_limited.setter
    def normal_flow_limited(self, value):
        self._options.NormalFlowLimited = value
        
    @property
    def len_step(self):
        return self._options.LenStep
    
    @len_step.setter
    def len_step(self, value):
        self._options.LenStep = value
        
    @property
    def min_sur_area(self):
        return self._options.MinSurArea
    
    @min_sur_area.setter
    def min_sur_area(self, value):
        self._options.MinSurArea = value

    @property
    def skip_steady_state(self):
        return self._options.SkipSteadyState
    
    @skip_steady_state.setter
    def skip_steady_state(self, value):
        self._options.SkipSteadyState = value
        
    @property
    def ignore_rainfall(self):
        return self._options.IgnoreRainfall
    
    @ignore_rainfall.setter
    def ignore_rainfall(self, value):
        self._options.IgnoreRainfall = value
        
    @property
    def force_main_equ(self):
        return self._options.ForceMainEqu
    
    @force_main_equ.setter
    def force_main_equ(self, value):
        self._options.ForceMainEqu = value
        
    @property
    def sur_method(self):
        return self._options.SurMethod
    
    @sur_method.setter
    def sur_method(self, value):
        self._options.SurMethod = value
        
    @property
    def link_offset(self):
        return self._options.LinkOffset
    
    @link_offset.setter
    def link_offset(self, value):
        self._options.LinkOffset = value
        
    @property
    def min_slope(self):
        return self._options.MinSlope
    
    @min_slope.setter
    def min_slope(self, value):
        self._options.MinSlope = value
        
    @property
    def ignore_snowmelt(self):
        return self._options.IgnoreSnowmelt
    
    @ignore_snowmelt.setter
    def ignore_snowmelt(self, value):
        self._options.IgnoreSnowmelt = value
        
    @property
    def ignore_groundwater(self):
        return self._options.IgnoreGroundWater
    
    @ignore_groundwater.setter
    def ignore_groundwater(self, value):
        self._options.IgnoreGroundWater = value
        
    @property
    def ignore_route(self):
        return self._options.IgnoreRoute
    
    @ignore_route.setter
    def ignore_route(self, value):
        self._options.IgnoreRoute = value

    @property
    def ignore_quality(self):
        return self._options.IgnoreQuality
    
    @ignore_quality.setter
    def ignore_quality(self, value):
        self._options.IgnoreQuality = value
        
    @property
    def max_trials(self):
        return self._options.MaxTrials
    
    @max_trials.setter
    def max_trials(self, value):
        self._options.MaxTrials = value
        
    @property
    def head_tol(self):
        return self._options.HeadTol
    
    @head_tol.setter
    def head_tol(self, value):
        self._options.HeadTol = value
        
    @property
    def sys_flow_tol(self):
        return self._options.SysFlowTol
    
    @sys_flow_tol.setter
    def sys_flow_tol(self, value):
        self._options.SysFlowTol = value

    @property
    def lat_flow_tol(self):
        return self._options.LatFlowTol
    
    @lat_flow_tol.setter
    def lat_flow_tol(self, value):
        self._options.LatFlowTol = value
        
    @property
    def ignore_rdii(self):
        return self._options.IgnoreRDII
    
    @ignore_rdii.setter
    def ignore_rdii(self, value):
        self._options.IgnoreRDII = value
        
    @property
    def min_route_step(self):
        return self._options.MinRouteStep
    
    @min_route_step.setter
    def min_route_step(self, value):
        self._options.MinRouteStep = value
        
    @property
    def thread(self):
        return self._options.Thread
    
    @thread.setter
    def thread(self, value):
        self._options.Thread = value

    @property
    def core_count(self):
        return self._options.CoreCount
    
    @core_count.setter
    def core_count(self, value):
        self._options.CoreCount = value
    