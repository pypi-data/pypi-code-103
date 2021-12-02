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
import os
import threading
from ca_apm_agent.connections.constants import TRACE_ID
from ca_apm_agent.utils import network


class Context:
    def __init__(self, seq, function_name=None, trace_id=None, params_dict=None, function_id=None, corr_id=None, timestamp=None):
        processid = os.getpid()
        containerid = network.getcontainerid()
        
        if containerid:
           processid = containerid
           
        self.pid = processid
        self.tid = threading.get_ident()
        self.seq = seq
        self.func_name = function_name
        self.func_id = function_id
        self.trace_id = str(trace_id)
        self.params = params_dict
        self.args = None
        self.kwargs = None
        self.exc = None
        self.cor_id = corr_id
        self.timestamp = None
        if self.params is None:
            self.params = {TRACE_ID: self.trace_id}
        else:
            self.params.update({TRACE_ID: self.trace_id})

    def push_target_params(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def set_trace_id(self, trace_id):
        self.trace_id = str(trace_id)
        if self.params is None:
            self.params = {TRACE_ID: self.trace_id}
        else:
            self.params.update({TRACE_ID: self.trace_id})
        
    def set_timestamp(self, timestamp):
        self.timestamp = timestamp
       
    def set_params(self, params_dict):
        if self.params is None:
            self.params = params_dict
        else:
            self.params.update(params_dict)

    def reset_params(self, params_dict=None):
        self.params = params_dict

    def set_exception(self, exception_dict):
        if self.exc is not None:
            self.exc.update(exception_dict)
        else:
            self.exc = exception_dict
