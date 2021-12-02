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
import logging
import time
import os
from ca_apm_agent.global_constants import LOGGER_NAME
import ca_apm_agent.status
from ca_apm_agent.connections._connect import Connect
from ca_apm_agent.utils import network

logger = logging.getLogger(LOGGER_NAME[0] + '.connections.data')


class Data:
    def __init__(self, host, port, instid, data_msg_queue):
        self.host = host
        self.port = port
        self.instid = instid
        processid = os.getpid()
        containerid = network.getcontainerid()
        
        if containerid:
           processid = containerid
           
        self.pid = processid
        self.conn = Connect(host=self.host, port=self.port, logger=logger)
        self.conn_status = False
        self.msg_queue = data_msg_queue

    def connect(self, delay=10):
        if delay:
            time.sleep(delay)
        while (not ca_apm_agent.status.com_ready[0]) and (self.pid == self.instid):
            logger.debug('Waiting for Command Connection to be established')
            time.sleep(20)
        for i in range(3):
            if self.conn.connect():
                self.conn_status = True
                self.send_msg(self._create_conn_msg())
                break

    def send_msg(self, msg):
        if (not ca_apm_agent.status.com_ready[0]) and (self.pid == self.instid):
            self.conn_status = False
        if self.conn_status and (not ca_apm_agent.status.com_pause[0]):
            if not self.conn.send(msg):
                self.conn_status = False
                processid = os.getpid()
                containerid = network.getcontainerid()
                if containerid:
                   processid = containerid
                if processid == self.instid:
                    ca_apm_agent.status.com_restart[0] = True
                    ca_apm_agent.status.com_ready[0] = False

    def recv_msg(self):
        if not self.conn_status:
            return False
        else:
            return self.conn.receive()

    @staticmethod
    def create_msg(list_of_tuples):
        from ca_apm_agent.utils import json_helpers
        return json_helpers.to_json_string(list_of_tuples)

    def _create_conn_msg(self):
        from ca_apm_agent.connections.constants import OP, DATA_CONN, PROBE, PYTHON, VER, ARF_VER, INSTID, PID
        from ca_apm_agent.utils import json_helpers

        l = [(OP, DATA_CONN), (PROBE, PYTHON), (VER, ARF_VER), (INSTID, self.instid), (PID, self.pid)]
        msg = json_helpers.to_json_string(l)
        return msg

    @staticmethod
    def create_data_func_call_msg(pid, tid, seq, func_name=None, func_id=None, params=None):
        from ca_apm_agent.connections.constants import OP, FUNCTION_CALL, FUNCTION_NAME, FUNCTION_ID, TIMESTAMP, PID, TID, PRMS, SEQ
        from ca_apm_agent.utils import json_helpers
        l = [(OP, FUNCTION_CALL)]
        if func_name is not None:
            l.append((FUNCTION_NAME, func_name))
        if func_id is not None:
            l.append((FUNCTION_ID, func_id))
        l.extend([(TIMESTAMP, int(round(time.time() * 1000))), (PID, pid), (TID, tid), (SEQ, seq)])
        if params is not None:
            l.append((PRMS, params))
        msg = json_helpers.to_json_string(l)
        return msg

    @staticmethod
    def create_data_func_call_msg_with_context(context_obj):
        from ca_apm_agent.connections.constants import OP, FUNCTION_CALL, FUNCTION_NAME, FUNCTION_ID, TIMESTAMP, PID, TID, PRMS, SEQ
        from ca_apm_agent.utils import json_helpers
        l = [(OP, FUNCTION_CALL)]
        if context_obj.func_name is not None:
            l.append((FUNCTION_NAME, context_obj.func_name))
        if context_obj.func_id is not None:
            l.append((FUNCTION_ID, context_obj.func_id))
        if context_obj.timestamp is not None:
           l.extend([(TIMESTAMP, context_obj.timestamp), (PID, context_obj.pid), (TID, context_obj.tid),
                     (SEQ, context_obj.seq)])
        else:
            l.extend([(TIMESTAMP, int(round(time.time() * 1000))), (PID, context_obj.pid), (TID, context_obj.tid),
                      (SEQ, context_obj.seq)])
        if context_obj.params is not None:
            l.append((PRMS, context_obj.params))
        msg = json_helpers.to_json_string(l)
        return msg

    @staticmethod
    def create_data_func_return_msg(pid, tid, cseq, exception_dict=None):
        from ca_apm_agent.connections.constants import OP, FUNCTION_RET, TIMESTAMP, PID, TID, CSEQ, EXCEPTION
        from ca_apm_agent.utils import json_helpers
        l = [(OP, FUNCTION_RET)]
        l.extend([(TIMESTAMP, int(round(time.time() * 1000))), (PID, pid), (TID, tid), (CSEQ, cseq)])
        if exception_dict is not None:
            l.append((EXCEPTION, exception_dict))
        msg = json_helpers.to_json_string(l)
        return msg

    @staticmethod
    def create_data_func_return_msg_with_context(context_obj):
        from ca_apm_agent.connections.constants import OP, FUNCTION_RET, TIMESTAMP, PID, TID, CSEQ, EXCEPTION, PRMS
        from ca_apm_agent.utils import json_helpers
        l = [(OP, FUNCTION_RET)]
        l.extend([(TIMESTAMP, int(round(time.time() * 1000))), (PID, context_obj.pid), (TID, context_obj.tid),
                  (CSEQ, context_obj.seq)])
        if context_obj.exc is not None:
            l.append((EXCEPTION, context_obj.exc))
        msg = json_helpers.to_json_string(l)
        return msg

    def worker(self, sleep_time):
        logger.info('Worker started')
        import time
        self.connect()
        while True:
            if self.conn_status:
                while (not self.msg_queue.empty()) and (self.pid != self.instid or ca_apm_agent.status.com_ready[0]):
                    self.send_msg(self.msg_queue.get_nowait())
            else:
                self.conn.close()
                self.connect()
            if self.msg_queue.empty():
                time.sleep(sleep_time)
