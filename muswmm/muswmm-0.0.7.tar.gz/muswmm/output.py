# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 16:21:18 2021

@author: mumuz
"""

import os
import muswmm.lib
import datetime


from Mumu.SWMM.Output import Output as Outp


class Output():
    
    def __init__(self):
        self._output = Outp()
        self._is_open = False
        self._n_period = 0
        self._n_pollut = 0
        self._start_date_time = 0
        self._report_step = 0
        
    @property
    def is_open(self):
        return self._is_open
    
    @property
    def n_period(self):
        return self._n_period
    
    @property
    def n_pollut(self):
        return self._n_pollut
    
    @property
    def start_date_time(self):
        return self.__time_fromReal(self._start_date_time)
    
    @property
    def end_date_time(self):
        print(self.start_date_time)
        return self.start_date_time + datetime.timedelta(seconds=self.report_step*self.n_period)
    
    @property
    def report_step(self):
        return self._report_step
        
    def open(self, out_path):
        if  self._output.Open(out_path) == 0:
            self._is_open = True
            self._n_period = self._output.NPeriods
            self._n_pollut = self._output.NPollut
            self._start_date_time = self._output.StartDate
            self._report_step = self._output.ReportStep
            return True
        else:
            self._is_open = False
            return False
    
    def get_result(self, obj_type, name, var_type, period):
        flag = False
        result = 0
        if not self._is_open:
            return False, result
        x = self._output.GetResultByName(obj_type, name,var_type, period, result)
        if x[0] == 1:
            flag = True
        else:
            flag = False
        result = x[1]
        return flag, result

    def get_results(self, obj_type, name, var_type):
        if not self._is_open:
            return False, None
        results = []
        for i in range(1, self.n_period+1):
            flag, result = self.get_result(obj_type, name, var_type, i)
            if not flag:
                return False, None
            results.append(result)
        return results
    
    def close(self):
        self._output.Close()
        
    # 数值型时间转日期型时间
    # private
    def __time_fromReal(self, time):
        return datetime.datetime.strptime('1899-12-30','%Y-%m-%d') + datetime.timedelta(time)
        