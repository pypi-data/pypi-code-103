# -*- coding: utf-8 -*-
"""
Created on Sat Sep 18 19:35:19 2021

@author: mumuz
"""

import ctypes
from simuwater.lib import *
import datetime


class SimuwaterException(Exception):
    def __init__(self, error_code, error_message):
        self.warning = False
        self.args = (error_code, )
        self.message = error_message

    def __str__(self):
        return self.message

class PySimuwaterException(Exception):

    def __init__(self, error_message):
        self.warning = False
        self.message = error_message

    def __str__(self):
        return self.message

class Simuwater:
    
    def __init__(self, SWMM_CPY_DLL = ''):
        self._simuwater = SIMUWATER
        self._simuwater.simuwater_initSwmmDll((LIB_PATH+'\\swmm5ex.dll').encode('utf-8'),SWMM_CPY_DLL.encode('utf-8'))
        
    def simuwater_run(self, swi, swr, swo):
        return self._simuwater.simuwater_run(swi.encode('utf-8'),
                                             swr.encode('utf-8'),
                                             swo.encode('utf-8'))
        
    def simuwater_open(self, swi, swr, swo):
        return self._simuwater.simuwater_open(swi.encode('utf-8'),
                                              swr.encode('utf-8'),
                                              swo.encode('utf-8'))
        
    def simuwater_start(self, save_results):
        return self._simuwater.simuwater_start(save_results)
    
    def simuwater_step(self):
        if not hasattr(self, 'cur_date_time'):
            self.cur_date_time = 0.0
        elapsed_time = ctypes.c_double()
        err_code = self._simuwater.simuwater_step(ctypes.byref(elapsed_time))
        self.cur_date_time = elapsed_time.value
        return err_code, elapsed_time.value
    
    def simuwater_stride(self, advance_sec):
        if not hasattr(self, 'cur_date_time'):
            self.cur_date_time = 0.0
        cur_time = self.cur_date_time
        advance_day = advance_sec / 86400.0
        err_code = 0
        err_code, routing_step = self.simuwater_getRoutingStep()
        while self.cur_date_time <= cur_time + advance_day - routing_step / 86400.0 / 2.0:
            err_code, elapsed_time = self.simuwater_step()
            if err_code != 0 or elapsed_time == 0:
                return err_code, 0.0
            self.cur_date_time = elapsed_time
        return err_code, elapsed_time
            
    def simuwater_report(self):
        return self._simuwater.simuwater_report()
    
    def simuwater_end(self):
        return self._simuwater.simuwater_end()
    
    def simuwater_close(self):
        return self._simuwater.simuwater_close()
    
    def simuwater_getMassBalErr(self):
        runoffErr = ctypes.c_float()
        flowErr = ctypes.c_float()
        qualErr = ctypes.c_float()
        err_code = self._simuwater.swmm_getMassBalErr(ctypes.byref(runoffErr),
                                                     ctypes.byref(flowErr), 
                                                     ctypes.byref(qualErr))
        return err_code, runoffErr.value, flowErr.value, qualErr.value
    
    def simuwater_setExtInflow(self, obj_id, ext_inflow):
        return self._simuwater.simuwater_setExtInflow(obj_id.encode('utf-8'),
                                                      ctypes.c_double(ext_inflow))
        
    def simuwater_setExtLoad(self, obj_id, pollut_id, ext_load):
        return self._simuwater.simuwater_setExtLoad(obj_id.encode('utf-8'),
                                                    pollut_id.encode('utf-8'),
                                                    ctypes.c_double(ext_load))
    
    def simuwater_setSetting(self, obj_id, setting_value):
        return self._simuwater.simuwater_setSetting(obj_id.encode('utf-8'),
                                                    ctypes.c_double(setting_value))
        
    def simuwater_getSetting(self, obj_id):
        setting_value = ctypes.c_double()
        self._simuwater.simuwater_getSetting(obj_id.encode('utf-8'),
                                             ctypes.byref(setting_value))
        return setting_value.value
    
    def simuwater_getResult(self, obj_type, obj_id, var_type):
        result_value = ctypes.c_double()
        err_code = self._simuwater.simuwater_getResult(ctypes.c_int(obj_type),
                                                       obj_id.encode('utf-8'),
                                                       ctypes.c_int(var_type),
                                                       ctypes.byref(result_value))
        return result_value.value
    
    def simuwater_getParam(self, obj_type, obj_id, param_type):
        result_value = ctypes.c_double()
        self._simuwater.simuwater_getParam(ctypes.c_int(obj_type),
                                                      obj_id.encode('utf-8'),
                                                      ctypes.c_int(param_type),
                                                      ctypes.byref(result_value))
        return result_value.value
    
    def simuwater_setParam(self, obj_type, obj_id, param_type, value):
        return self._simuwater.simuwater_setParam(ctypes.c_int(obj_type),
                                                  obj_id.encode('utf-8'),
                                                  ctypes.c_int(param_type),
                                                  ctypes.c_double(value))
    
    def simuwater_setTankDepth(self, obj_id, value):
        return self._simuwater.simuwater_setTankDepth(obj_id.encode('utf-8'),
                                                      ctypes.c_double(value))
        
    def simuwater_setLinkFlow(self, obj_id, value):
        return self._simuwater.simuwater_setLinkFlow(obj_id.encode('utf-8'),
                                                     ctypes.c_double(value))
        
    def simuwater_getNodeType(self, obj_id):
        node_type = ctypes.c_int()
        self._simuwater.simuwater_getNodeType(obj_id.encode('utf-8'),
                                                     ctypes.byref(node_type))
        return node_type.value
    
    def simuwater_getLinkType(self, obj_id):
        link_type = ctypes.c_int()
        self._simuwater.simuwater_getLinkType(obj_id.encode('utf-8'),
                                                     ctypes.byref(link_type))
        return link_type.value
    
    def simuwater_setSwmmExtInflow(self, inp_id, obj_id, extInflow):
        return self._simuwater.simuwater_setSwmmExtInflow(inp_id.encode('utf-8'),
                                                          obj_id.encode('utf-8'),
                                                          ctypes.c_double(extInflow))
        
    def simuwater_setSwmmExtLoad(self, inp_id, obj_id, pollut_id, extLoad):
        return self._simuwater.simuwater_setSwmmExtLoad(inp_id.encode('utf-8'),
                                                        obj_id.encode('utf-8'),
                                                        pollut_id.encode('utf-8'),
                                                        ctypes.c_double(extLoad))
    
    def simuwater_setSwmmSetting(self, inp_id, obj_id, setting_value):
        return self._simuwater.simuwater_setSwmmSetting(inp_id.encode('utf-8'),
                                                        obj_id.encode('utf-8'),
                                                        ctypes.c_double(setting_value))
        
    def simuwater_getSwmmResult(self, inp_id, obj_type, obj_id, var_type):
        result_value = ctypes.c_double()
        err_code = self._simuwater.simuwater_getSwmmResult(inp_id.encode('utf-8'),
                                                           ctypes.c_int(obj_type),
                                                           obj_id.encode('utf-8'),
                                                           ctypes.c_int(var_type),
                                                           ctypes.byref(result_value))
        return err_code, result_value.value
    
    def simuwater_getSwmmParam(self, inp_id, obj_type, obj_id, param_type):
        result_value = ctypes.c_double()
        err_code = self._simuwater.simuwater_getSwmmParam(inp_id.encode('utf-8'),
                                                                        ctypes.c_int(obj_type),
                                                                        obj_id.encode('utf-8'),
                                                                        ctypes.c_int(param_type),
                                                                        ctypes.byref(result_value))
        return err_code, result_value.value
    
    def simuwater_setSwmmParam(self, inp_id, obj_type, obj_id, param_type,value):
        return self._simuwater.simuwater_setSwmmParam(inp_id.encode('utf-8'),
                                                      ctypes.c_int(obj_type),
                                                      obj_id.encode('utf-8'),
                                                      ctypes.c_int(param_type),
                                                      ctypes.c_double(value))
        
    def simuwater_getSwmmNodeParam(self, inp_id, node_type, obj_id, param_type):
        result_value = ctypes.c_double()
        err_code = self._simuwater.simuwater_getSwmmNodeParam(inp_id.encode('utf-8'),
                                                              ctypes.c_int(node_type),
                                                              obj_id.encode('utf-8'),
                                                              ctypes.c_int(param_type), 
                                                              ctypes.byref(result_value))
        return err_code, result_value.value
    
    def simuwater_setSwmmNodeParam(self, inp_id, node_type, obj_id, param_type, value):
        return self._simuwater.simuwater_setSwmmNodeParam(inp_id.encode('utf-8'),
                                                          ctypes.c_int(node_type),
                                                          obj_id.encode('utf-8'),
                                                          ctypes.c_int(param_type), 
                                                          ctypes.c_double(value))
        
    def simuwater_getSwmmLinkParam(self, inp_id, link_type, obj_id, param_type):
        result_value = ctypes.c_double()
        err_code = self._simuwater.simuwater_getSwmmLinkParam(inp_id.encode('utf-8'),
                                                              ctypes.c_int(link_type),
                                                              obj_id.encode('utf-8'),
                                                              ctypes.c_int(param_type), 
                                                              ctypes.byref(result_value))
        return err_code, result_value.value
    
    def simuwater_setSwmmLinkParam(self, inp_id, link_type, obj_id, param_type, value):
        return self._simuwater.simuwater_setSwmmLinkParam(inp_id.encode('utf-8'),
                                                          ctypes.c_int(link_type),
                                                          obj_id.encode('utf-8'),
                                                          ctypes.c_int(param_type), 
                                                          ctypes.c_double(value))
        
    def simuwater_setSwmmNodeDepth(self, inp_id, obj_id, value):
        return self._simuwater.simuwater_setSwmmNodeDepth(inp_id.encode('utf-8'),
                                                obj_id.encode('utf-8'),
                                                ctypes.c_double(value))
    
    def simuwater_setSwmmLinkDepth(self, inp_id, obj_id, value):
        return self._simuwater.simuwater_setSwmmLinkDepth(inp_id.encode('utf-8'),
                                                obj_id.encode('utf-8'),
                                                ctypes.c_double(value))
        
    def simuwater_setSwmmLinkFlow(self, inp_id, obj_id, value):
        return self._simuwater.simuwater_setSwmmLinkFlow(inp_id.encode('utf-8'),
                                                obj_id.encode('utf-8'),
                                                ctypes.c_double(value))
    
    def simuwater_findObject(self, obj_type, obj_id):
        return self._simuwater.simuwater_findObject(ctypes.c_int(obj_type),
                                                    obj_id.encode('utf-8'))
        
    def simuwater_isInEvent(self, gage):
        return self._simuwater.simuwater_isInEvent(gage.encode('utf-8'))
        
    def simuwater_getDateTime(self):
        start_date_time = ctypes.c_double()
        end_date_time = ctypes.c_double()
        err_code = self._simuwater.simuwater_getDateTime(ctypes.byref(start_date_time),
                                                         ctypes.byref(end_date_time))
        return err_code, self.__time_fromReal(start_date_time.value), self.__time_fromReal(end_date_time.value)
    
    def simuwater_getCurrentTime(self):
        if not hasattr(self, 'cur_date_time'):
            self.cur_date_time = 0.0
        return self.simuwater_getDateTime()[1] + datetime.timedelta(self.cur_date_time)
    
    def simuwater_getRoutingStep(self):
        routing_step = ctypes.c_double()
        err_code = self._simuwater.simuwater_getRoutingStep(ctypes.byref(routing_step))
        return err_code, routing_step.value
    
    def simuwater_getSwmmObjCount(self, inp_id, obj_type):        
        return self._simuwater.simuwater_getSwmmObjCount(inp_id.encode('utf-8'),obj_type)
        
    def simuwater_getSwmmObjID(self, inp_id, obj_type, obj_index):
        ID = ctypes.create_string_buffer(259)
        err_code = self._simuwater.simuwater_getSwmmObjID(inp_id.encode('utf-8'),
                                                          obj_type,
                                                          obj_index,
                                                          ctypes.byref(ID))
        return err_code, ID.value.decode("utf-8")
    
    def simuwater_getSwmmObjIndex(self, inp_id, obj_type, ID):
        return self._simuwater.simuwater_getSwmmObjIndex(inp_id.encode('utf-8'), obj_type, ID.encode('utf-8'))
    
    # 数值型时间转日期型时间
    # private
    def __time_fromReal(self, time):
        return datetime.datetime.strptime('1899-12-30','%Y-%m-%d') + datetime.timedelta(time)
    
# 测试
if __name__ == '__main__':
    pysw = Simuwater()
    swi = r'C:\Users\mumuz\Desktop\simuwater\python\example\medium.swi'
    swr = r'C:\Users\mumuz\Desktop\simuwater\python\example\medium.swr'
    swo = r'C:\Users\mumuz\Desktop\simuwater\python\example\medium.swo'
    pysw.simuwater_open(swi, swr, swo)
    err_code, start_date_time, end_date_time = pysw.simuwater_getDateTime()
    pysw.simuwater_start(1)
    while(True):
        pysw.simuwater_setSwmmExtInflow('SWMM2','101WS3573',2.0)
        print(pysw.simuwater_getSwmmResult('SWMM2',1,'101WS3573',4))
        err_code, elapsed_time = pysw.simuwater_step()
        print(pysw.simuwater_getCurrentTime())
        if err_code!=0 or elapsed_time == 0:
            break
    pysw.simuwater_report()
    pysw.simuwater_end()
    pysw.simuwater_close()
    print("run is successful.")