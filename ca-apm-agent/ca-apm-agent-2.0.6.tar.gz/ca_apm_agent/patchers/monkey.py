__copyright__ = """
* Copyright (c) 2018 CA. All rights reserved.
*
* This software and all information contained therein is confidential and proprietary and
* shall not be duplicated, used, disclosed or disseminated in any way except as authorized
* by the applicable license agreement, without the express written permission of CA. All
* authorized reproductions must be marked with this language.
*
* EXCEPT AS SET FORTH IN THE APPLICABLE LICENSE AGREEMENT, TO THE EXTENT
* PERMITTED BY APPLICABLE LAW, CA PROVIDES THIS SOFTWARE WITHOUT WARRANTY
* OF ANY KIND, INCLUDING WITHOUT LIMITATION, ANY IMPLIED WARRANTIES OF
* MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT WILL CA BE
* LIABLE TO THE END USER OR ANY THIRD PARTY FOR ANY LOSS OR DAMAGE, DIRECT OR
* INDIRECT, FROM THE USE OF THIS SOFTWARE, INCLUDING WITHOUT LIMITATION, LOST
* PROFITS, BUSINESS INTERRUPTION, GOODWILL, OR LOST DATA, EVEN IF CA IS
* EXPRESSLY ADVISED OF SUCH LOSS OR DAMAGE.
"""
import sys
import logging
import importlib
import builtins
import time
import json
import socket
from ca_apm_agent.utils import json_helpers
from ca_apm_agent.global_constants import LOGGER_NAME
from ca_apm_agent.trace_enablers.virtual_stack import VirtualStack
from ca_apm_agent.trace_enablers.context import Context
from ca_apm_agent.connections.data import Data
from ca_apm_agent.instruments import import_hook
from ca_apm_agent.patchers.constants import *
from ca_apm_agent.connections.constants import PYTHON_MODULE, PYTHON_RASA_INTENT
import inspect
import asyncio

logger = logging.getLogger(LOGGER_NAME[0] + '.patchers.monkey')


class Patcher:
    def __init__(self, cfg, data_queue):
        self.probe_dict = cfg.pop()
        self.to_instrument = cfg
        self.instrumented = []
        self.data_q = data_queue

    def patch(self):
        # Patches methods based on data in the instrument config file, CA_APM_PYTHON_ICFG env variable
        if not self.to_instrument:
            return
        i = 0
        while i < len(self.to_instrument):
            conf_dict = self.to_instrument[i]
            if not conf_dict[PATCHED]:
                _module = sys.modules.get(conf_dict[MODULE], None)
                if not _module:
                    i += 1
                    continue
                _class = None
                if conf_dict[CLASS] != 'None':
                    _class = getattr(_module, conf_dict[CLASS], None)
                    if not _class:
                        i += 1
                        continue
                _method = None
                if _class:
                    _method = getattr(_class, conf_dict[METHOD], None)
                else:
                    _method = getattr(_module, conf_dict[METHOD], None)
                if not _method:
                    i += 1
                    continue

                logger.debug('Disengaging import hook to import probes')
                builtins.__import__ = import_hook._wily_import_orig__
                probe_list = []
                for k in conf_dict[PROBE_KEYS]:
                    if not self.probe_dict[k][LOADED]:
                        self.probe_dict[k][LOADED] = getattr(importlib.import_module(self.probe_dict[k][PROBE_MODULE]),
                                                             self.probe_dict[k][PROBE_CLASS],
                                                             False)
                        if not self.probe_dict[k][LOADED]:
                            logger.error(
                                'Could not find probe class or module using provided probe module %s and class %s',
                                self.probe_dict[k][PROBE_MODULE], self.probe_dict[k][PROBE_CLASS])
                        else:
                            probe_list.append(self.probe_dict[k][LOADED])
                    else:
                        probe_list.append(self.probe_dict[k][LOADED])
                builtins.__import__ = import_hook.wily_import_hook
                logger.debug('Engaging import hook after attempting to import probes')
                if not probe_list:
                    logger.error(
                        'Unable to find any probe in instrumentation directive %s \nTherefore, not instrumenting',
                        str(conf_dict))
                    i += 1
                    continue

                if _class:
                    patched = self.patch_method(_class, _method, probe_list)
                    setattr(_class, conf_dict[METHOD], patched)
                else:
                    patched = self.patch_method(_module, _method, probe_list)
                    setattr(_module, conf_dict[METHOD], patched)
                conf_dict[PATCHED] = True
                self.instrumented.append(conf_dict)
                self.to_instrument.pop(i)
                import_hook.patch_list.discard(conf_dict[MODULE])
                logger.info('Instrumentation directive %s succeeded', str(conf_dict))

    def patch_method(self, target_class, target_func, probe_list):
        for i in range(0, len(probe_list)):
            probe_list[i] = probe_list[i]()

        def function_template(*args, **kwargs):
            function_name = target_class.__name__ + '.' + target_func.__name__
            try:
                logger.debug('Start Trace %s', str(target_func.__name__))
                vs = VirtualStack()
                trace_id = str(vs.get_trace_id())
                seq = vs.get_seq()
                logger.debug('Start Trace %s', str(function_name))
                context = Context(seq=seq, function_name=function_name, trace_id=trace_id)
                context.push_target_params(*args, **kwargs)
                vs.push(context)
                # call probe's start
                for probe in probe_list:
                    if function_name == 'Interpreter.parse' :
                       timestamp = int(round(time.time() * 1000))
                       context.set_timestamp(timestamp)
                    else:
                       probe.start(context)
                if function_name == 'Interpreter.parse' :
                   logger.debug('Captured Timestamp for Rasa in Probe start')
                else:
                   call_msg = Data.create_data_func_call_msg_with_context(context_obj=context)
                   self.data_q.put_nowait(call_msg)
            except Exception as e:
                logger.error('Error starting probes for %s ', function_name)
                logger.debug('Exception that was raised %s', str(e))
            finally:
                # Call the method that was actually called
                try:
                    context.res = target_func(*args, **kwargs)
                except Exception:
                    context.e, context.v, context.tb = sys.exc_info()
                    context.func_name = function_name
            try:
                logger.debug('Finish Trace %s', str(target_func.__name__))
                for probe in probe_list:
                     if function_name == 'Interpreter.parse' :
                       probe.start(context)
                       call_msg = Data.create_data_func_call_msg_with_context(context_obj=context)
                       self.data_q.put_nowait(call_msg)  
                       
                for probe in reversed(probe_list):
                    probe.finish(context)
                vs.pop()
                ret_msg = Data.create_data_func_return_msg_with_context(context_obj=context)
                self.data_q.put_nowait(ret_msg)
            except Exception as e:
                logger.error('Error finishing probes for %s ', function_name)
                logger.debug('Exception that was raised %s', str(e))
            finally:
                if hasattr(context, 'e'):
                    raise context.e(context.v).with_traceback(context.tb)
                else:
                    return context.res

        #return function_template
        async def async_function_template(*args, **kwargs):
            function_name = target_class.__name__ + '.' + target_func.__name__
            try:
                logger.debug('Start Trace %s', str(target_func.__name__))
                vs = VirtualStack()
                trace_id = str(vs.get_trace_id())
                seq = vs.get_seq()
                logger.debug('Start Trace %s', str(function_name))
                context = Context(seq=seq, function_name=function_name, trace_id=trace_id)
                context.push_target_params(*args, **kwargs)
                vs.push(context)
                # call probe's start
                for probe in probe_list:
                    if function_name == 'Interpreter.parse' :
                       timestamp = int(round(time.time() * 1000))
                       context.set_timestamp(timestamp)
                    else:
                       probe.start(context)
                if function_name == 'Interpreter.parse' :
                   logger.debug('Captured Timestamp for Rasa in Probe start')
                else:
                   call_msg = Data.create_data_func_call_msg_with_context(context_obj=context)
                   self.data_q.put_nowait(call_msg)
            except Exception as e:
                logger.error('Error starting probes for %s ', function_name)
                logger.debug('Exception that was raised %s', str(e))
            finally:
                # Call the method that was actually called
                try:
                    context.res = await target_func(*args, **kwargs)
                except Exception:
                    context.e, context.v, context.tb = sys.exc_info()
                    context.func_name = function_name
            try:
                logger.debug('Finish Trace %s', str(target_func.__name__))
                # call probe's start
                for probe in probe_list:
                     if function_name == 'Interpreter.parse' :
                       probe.start(context)
                       call_msg = Data.create_data_func_call_msg_with_context(context_obj=context)
                       self.data_q.put_nowait(call_msg)  
                       
                for probe in reversed(probe_list):
                    probe.finish(context)
                vs.pop()
                ret_msg = Data.create_data_func_return_msg_with_context(context_obj=context)
                self.data_q.put_nowait(ret_msg)
            except Exception as e:
                logger.error('Error finishing probes for %s ', function_name)
                logger.debug('Exception that was raised %s', str(e))
            finally:
                if hasattr(context, 'e'):
                    raise context.e(context.v).with_traceback(context.tb)
                else:
                    return context.res

        if inspect.iscoroutinefunction(target_func) == True:
            return async_function_template
        else:
            return function_template
