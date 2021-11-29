# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 12:42:59 2021

@author: mumuz
"""

import ctypes
import os
from simuwater.lib import *
import datetime


# 对象类型索引
SYSTEM = 0
SUBCATCH = 1
JUNCTION = 2
TANK = 3
OUTFALL = 4
SPLITTER = 5
REACTOR = 6
LID_MONO = 7
PIPE = 8
PUMP = 9
CONNECTION = 10
CONDUIT = 11
WEIR = 12

# 系统结果类型
SYSTEM_RAINFALL = 0
SYSTEM_EVAP = 1
SYSTEM_INFIL = 2
SYSTEM_RUNOFF = 3
SYSTEM_TOT_INFLOW = 4
SYSTEM_DIR_INFLOW = 5
SYSTEM_DWF = 6
SYSTEM_FLOOD = 7
SYSTEM_SWMM_INFLOW = 8
SYSTEM_OUTFLOW = 9
SYSTEM_SWMM_OUTFLOW = 10
SYSTEM_STORAGE = 11

# 子汇水区结果类型
SUBCATCH_RAINFALL = 0
SUBCATCH_EVAP = 1
SUBCATCH_INFIL = 2
SUBCATCH_RUNOFF = 3
SUBCATCH_QUAL = 4

# junction节点结果类型
JUNCTION_TOT_INFLOW = 0
JUNCTION_LAT_INFLOW = 1
JUNCTION_QUAL = 2

# tank节点结果类型
TANK_DEPTH = 0
TANK_VOL = 1
TANK_TOT_INFLOW = 2
TANK_LAT_INFLOW = 3
TANK_FLOOD = 4
TANK_QUAL = 5

# outfall节点结果类型
OUTFALL_TOT_INFLOW = 0
OUTFALL_LAT_INFLOW = 1
OUTFALL_QUAL = 2

# splitter节点结果类型
SPLITTER_TOT_INFLOW = 0
SPLITTER_LAT_INFLOW = 1
SPLITTER_OUTFLOW1 = 2
SPLITTER_OUTFLOW2 = 3
SPLITTER_QUAL = 4

# reactor节点结果类型
REACTOR_VOL = 0
REACTOR_TOT_INFLOW = 1
REACTOR_LAT_INFLOW = 2
REACTOR_OUTFLOW = 3
REACTOR_SURPASS = 4
REACTOR_EVAP = 5
REACTOR_INFIL = 6
REACTOR_EMPTY = 7
REACTOR_QUAL = 8

# lidmono节点结果类型
LID_MONO_TOT_INFLOW = 0
LID_MONO_LAT_INFLOW = 1
LID_MONO_RAINFALL = 2
LID_MONO_EVAP = 3
LID_MONO_SURF_OUTFLOW = 4
LID_MONO_STORAGE_EXFIL = 5
LID_MONO_STORAGE_DRAIN = 6
LID_MONO_SURF_DEPTH = 7
LID_MONO_SOIL_MOIST = 8
LID_MONO_STORAGE_DEPTH = 9
LID_MONO_PAVE_DEPTH = 10
LID_MONO_QUAL = 11

# pipe链接结果类型
PIPE_VOL = 0
PIPE_INFLOW = 1
PIPE_OUTFLOW = 2
PIPE_FLOOD = 3
PIPE_QUAL = 4

# pump链接结果类型
PUMP_FLOW = 0
PUMP_QUAL = 1

# connection链接结果类型
CONNECTION_INFLOW = 0
CONNECTION_OUTFLOW = 1
CONNECTION_QUAL = 2

# conduit链接结果类型
CONDUIT_DEPTH = 0
CONDUIT_VOL = 1
CONDUIT_VELOCITY = 2
CONDUIT_INFLOW = 3
CONDUIT_OUTFLOW = 4
CONDUIT_FLOOD = 5
CONDUIT_QUAL = 6

# weir链接结果类型
WEIR_FLOW = 0
WEIR_QUAL = 1


class Output():
    
    def __init__(self):
        self._output = OUTPUT
        self._is_open = False
        self._n_period = 0
        self._start_date_time = 0
        self._report_step = 0
        self._c_double_type = ctypes.POINTER(ctypes.c_double)
        self._c_float_type = ctypes.POINTER(ctypes.c_float)
        self._c_int_type = ctypes.POINTER(ctypes.c_int)
        
    @property
    def is_open(self):
        return self._is_open
    
    @property
    def n_period(self):
        return self._n_period
    
    @property
    def start_date_time(self):
        return self.__time_fromReal(self._start_date_time)
    
    @property
    def report_step(self):
        return self._report_step
        
    def open(self, swo_path):
        err_code = self._output.output_openSwoFile(swo_path.encode('utf-8'))
        if err_code == 0:
            n_period = 0    # 报告周期数量
            start_date_time = 0.0    # 报告开始时间（浮点型日期格式）
            report_step = 0    # 报告步长（sec）
            p_n_period = self._c_int_type(ctypes.c_int(n_period))
            p_start_date_time = self._c_double_type(ctypes.c_double(start_date_time))
            p_report_step = self._c_int_type(ctypes.c_int(report_step))
            self._output.output_getProjectParams(p_n_period, p_start_date_time, p_report_step)
            n_period = p_n_period[0]
            start_date_time = p_start_date_time[0]
            report_step = p_report_step[0]
            self._n_period = n_period
            self._start_date_time = start_date_time
            self._report_step = report_step
            self._is_open = True
            return True
        else:
            print(err_code)
            self._is_open = False
            return False
    
    def get_result(self, obj_type, name, var_type, period):
        flag = False
        value = 0
        p_value = self._c_float_type(ctypes.c_float(value))
        if not self._is_open:
            return False, value
        idx = self._output.output_getIndex(obj_type - 1, name.encode('utf-8'))
        print(idx)
        err_code = self._output.output_getSimuwaterResult(obj_type, idx, var_type, period, p_value)
        value = p_value[0]
        if err_code == 0:
            flag = True
        else:
            flag = False
        return flag, value

    def get_results(self, obj_type, name, var_type):
        if not self._is_open:
            return False, None
        results = []
        for i in range(1, self.n_period + 1):
            flag, result = self.get_result(obj_type, name, var_type, i)
            if not flag:
                return False, None
            results.append(result)
        return results
    
    def close(self):
        self._output.output_closeSwoFile()
        
        # 数值型时间转日期型时间
    # private
    def __time_fromReal(self, time):
        return datetime.datetime.strptime('1899-12-30','%Y-%m-%d') + datetime.timedelta(time)
        