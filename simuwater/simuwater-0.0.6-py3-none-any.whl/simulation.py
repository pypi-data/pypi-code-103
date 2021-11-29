# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 22:57:26 2021

@author: mumuz
"""

import os
from simuwater.simuwater import *

class Simulation(object):
    def __init__(self,
                 swi,
                 swr = None,
                 swo = None,
                 swmm_cpy_dll = ''):
        self._model = Simuwater(swmm_cpy_dll)
        if swr == None:
            swr = os.path.dirname(swi) + '\\' + self.__path_getFileName(swi) + '.swr'
        if swo == None:
            swo = os.path.dirname(swi) + '\\' + self.__path_getFileName(swi) + '.swo'
        self._model.simuwater_open(swi, swr, swo)
        self._isOpen = True
        self._advance_seconds = None
        self._isStarted = False
        self._terminate_request = False
        self._callbacks = {
            "before_start": None,
            "before_step": None,
            "after_step": None,
            "before_report": None,
            "after_report": None,
            "before_end": None,
            "after_end": None,
            "after_close": None
        }
    
    def __path_getFileName(self, file_name, with_suffix = False):
        if with_suffix:
            return os.path.split(file_name)[-1]
        else:
            return os.path.split(file_name)[-1].split('.')[0]
        
    def __enter__(self):
        return self

    def __iter__(self):
        return self

    def start(self):
        if not self._isStarted:
            if hasattr(self, "_initial_conditions"):
                self._initial_conditions()
            self._execute_callback(self.before_start())
            self._model.simuwater_start(1)
            self._isStarted = True

    def __next__(self):
        self.start()
        if self._terminate_request:
            self._execute_callback(self.before_end())
            raise StopIteration
        self._execute_callback(self.before_step())
        if self._advance_seconds is None:
            err_code, time = self._model.simuwater_step()
        else:
            err_code, time = self._model.simuwater_stride(self._advance_seconds)
        self._execute_callback(self.after_step())
        if time <= 0.0:
            self._execute_callback(self.before_end())
            raise StopIteration
        return self._model

    next = __next__  # Python 2

    def __exit__(self, *a):
        if self._isStarted:
            self._model.simuwater_report()
            self._model.simuwater_end()
            self._isStarted = False
            self._execute_callback(self.after_report())
            self._execute_callback(self.after_end())
        if self._isOpen:
            self._model.simuwater_close()
            self._isOpen = False
            self._execute_callback(self.after_close())

    @staticmethod
    def _is_callback(callable_object):
        if not callable(callable_object):
            error_msg = 'Requires Callable Object, not {}'.format(
                type(callable_object))
            raise (PySimuwaterException(error_msg))
        else:
            return True

    def _execute_callback(self, callback):
        if callback:
            try:
                callback()
            except PySimuwaterException:
                error_msg = "Callback Failed"
                raise PySimuwaterException((error_msg))

    def initial_conditions(self, init_conditions):
        if self._is_callback(init_conditions):
            self._initial_conditions = init_conditions

    def before_start(self):
        return self._callbacks["before_start"]

    def add_before_start(self, callback):
        if self._is_callback(callback):
            self._callbacks["before_start"] = callback

    def before_step(self):
        return self._callbacks["before_step"]

    def add_before_step(self, callback):
        if self._is_callback(callback):
            self._callbacks["before_step"] = callback

    def after_step(self):
        return self._callbacks["after_step"]

    def add_after_step(self, callback):
        if self._is_callback(callback):
            self._callbacks["after_step"] = callback

    def before_end(self):
        return self._callbacks["before_end"]

    def add_before_end(self, callback):
        if self._is_callback(callback):
            self._callbacks["before_end"] = callback

    def after_end(self):
        return self._callbacks["after_end"]
    
    def before_report(self):
        return self._callbacks["before_report"]
    
    def add_before_report(self, callback):
        if self._is_callback(callback):
            self._callbacks["before_report"] = callback
    
    def after_report(self):
        return self._callbacks["after_report"]

    def add_after_end(self, callback):
        if self._is_callback(callback):
            self._callbacks["after_end"] = callback

    def after_close(self):
        return self._callbacks["after_close"]

    def add_after_close(self, callback):
        if self._is_callback(callback):
            self._callbacks["after_close"] = callback

    def step_advance(self, advance_seconds):
        self._advance_seconds = advance_seconds

    def terminate_simulation(self):
        self._terminate_request = True

    def report(self):
        self._model.simuwater_report()

    def close(self):
        self.__exit__()

    def execute(self):
        self._model.simuwater_run()

    @property
    def runoff_error(self):
        return self._model.simuwater_getMassBalErr()[1]

    @property
    def flow_routing_error(self):
        return self._model.simuwater_getMassBalErr()[2]

    @property
    def quality_error(self):
        return self._model.simuwater_getMassBalErr()[3]

    @property
    def start_time(self):
        return self._model.simuwater_getDateTime()[1]

    @property
    def end_time(self):
        return self._model.simuwater_getDateTime()[2]

    @property
    def current_time(self):
        return self._model.simuwater_getCurrentTime()

    @property
    def percent_complete(self):
        dt = self.current_time - self.start_time
        total_time = self.end_time - self.start_time
        return float(dt.total_seconds()) / total_time.total_seconds()
    
    # 测试
if __name__ == '__main__':
    swi = r'C:\Users\mumuz\Desktop\simuwater\python\example\medium.swi'
    swr = r'C:\Users\mumuz\Desktop\simuwater\python\example\medium.swr'
    swo = r'C:\Users\mumuz\Desktop\simuwater\python\example\medium.swo'
    sim = Simulation(swi, swr, swo)
    sim.step_advance(300)
    for step in sim:
#        for node in SwmmNodes(sim, 'SWMM2'):
#            print(node.node_id)
#            print(node.inflow)
#            break
#        swmm_link = SwmmLink(sim,'SWMM2','P3')
#        swmm_link.set_setting(1.0)
#        print(swmm_link.flow)
#        for link in SwmmLinks(sim, 'SWMM2'):
#            print(link.link_id)
#            print(link.flow)
#            break
        print(sim.percent_complete)
    sim.close()
    print("run is successful.")