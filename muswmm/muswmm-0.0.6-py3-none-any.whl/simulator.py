# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 09:41:18 2021

@author: mumuz
"""

import ctypes
from muswmm.lib import *
import datetime
import os


class Simulator:
    
    def __init__(self, inp, rpt = None, out = None):
        self._swmm = SWMM5EX
        self._inp = inp
        if rpt == None:
            rpt = os.path.dirname(inp) + '\\' + self.__path_getFileName(inp) + '.rpt'
        if out == None:
            out = os.path.dirname(inp) + '\\' + self.__path_getFileName(inp) + '.out'
        self._rpt = rpt
        self._out = out
        
    def __path_getFileName(self, file_name, with_suffix = False):
        if with_suffix:
            return os.path.split(file_name)[-1]
        else:
            return os.path.split(file_name)[-1].split('.')[0]
        
    def run(self):
        return self._swmm.swmm_run(self._inp.encode('utf-8'),
                                   self._rpt.encode('utf-8'),
                                   self._out.encode('utf-8'))
    
    def open(self):
        return self._swmm.swmm_open(self._inp.encode('utf-8'),
                                   self._rpt.encode('utf-8'),
                                   self._out.encode('utf-8'))
    
    def start(self, saveFlag):
        return self._swmm.swmm_start(ctypes.c_int(saveFlag))
    
    def step(self):
        if not hasattr(self, 'cur_date_time'):
            self.cur_date_time = 0.0
        elapsed_time = ctypes.c_double()
        err_code = self._swmm.swmm_step(ctypes.byref(elapsed_time))
        self.cur_date_time = elapsed_time.value
        return err_code, elapsed_time.value    
    
    def report(self):
        return self._swmm.swmm_report()
    
    def end(self):
        return self._swmm.swmm_end()
    
    def getMassBalErr(self):
        runoffErr = ctypes.c_float()
        flowErr = ctypes.c_float()
        qualErr = ctypes.c_float()
        err_code = self._swmm.swmm_getMassBalErr(ctypes.byref(runoffErr),
                                                     ctypes.byref(flowErr), 
                                                     ctypes.byref(qualErr))
        return err_code, runoffErr.value, flowErr.value, qualErr.value
    
    def close(self):
        return self._swmm.swmm_close()
    
    def getDateTime(self):
        start_date_time = ctypes.c_double()
        end_date_time = ctypes.c_double()
        err_code = self._swmm.swmm_getStartAndEndTime(ctypes.byref(start_date_time),
                                                         ctypes.byref(end_date_time))
        return err_code, self.__time_fromReal(start_date_time.value), self.__time_fromReal(end_date_time.value)
        
    def getCurrentTime(self):
        if not hasattr(self, 'cur_date_time'):
            self.cur_date_time = 0.0
        return self.getDateTime()[1] + datetime.timedelta(self.cur_date_time)
    
    # 数值型时间转日期型时间
    # private
    def __time_fromReal(self, time):
        return datetime.datetime.strptime('1899-12-30','%Y-%m-%d') + datetime.timedelta(time)
    
# 测试
if __name__ == '__main__':
    inp = r'C:\Users\mumuz\Desktop\muswmm\test\Example1.inp'
    rpt = r'C:\Users\mumuz\Desktop\muswmm\test\Example1.rpt'
    out = r'C:\Users\mumuz\Desktop\muswmm\test\Example1.out'
    sim = Simulator(inp, rpt, out)
    sim.open()
    sim.start(1)
    while(True):
        err_code, elapsed_time = sim.step()
        print(sim.getCurrentTime().strftime('%Y-%m-%d %H:%M:%S'))
        if err_code!=0 or elapsed_time == 0:
            break
    sim.end()
    sim.close()
    # swmm.swmm_run(inp, rpt, out)
    print("\nrun is successful.")