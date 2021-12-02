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
import subprocess
from ca_apm_agent.global_constants import LOGGER_NAME
import ca_apm_agent.status
from ca_apm_agent.connections._connect import Connect
from ca_apm_agent.utils import network

logger = logging.getLogger(LOGGER_NAME[0] + '.connections.command')


class Command:
    def __init__(self, host, port, instid, app_name, com_msg_queue):
        self.host = host
        self.port = port
        self.instid = instid
        self.app_name = app_name
        self.conn = Connect(host=self.host, port=self.port, logger=logger)
        self.conn_status = False
        self.msg_queue = com_msg_queue  # Thread Safe - make sure to check this for multiprocessing
        self.keep_alive = None
        self.collector_version = None
        self.params = None
        self.container_id = network.getcontainerid()

    def connect(self):
        for i in range(3):
            if self.conn.connect():
                self.conn_status = True
                self.send_msg(self._create_conn_msg())
                ca_apm_agent.status.com_ready[0] = True
                ca_apm_agent.status.com_restart[0] = False
                ca_apm_agent.status.com_pause[0] = False
                break

    def send_msg(self, msg):
        if self.conn_status:
            if not self.conn.send(msg):
                self.conn_status = False
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
        from ca_apm_agent.connections.constants import OP, COMMAND_CONN, PROBE, PYTHON, VER, ARF_VER, INSTID, PGM, PRMS
        from ca_apm_agent.utils import json_helpers

        l = [(OP, COMMAND_CONN), (PROBE, PYTHON), (VER, ARF_VER), (INSTID, self.instid), (PGM, self.app_name)]
        if self.container_id:
            from ca_apm_agent.connections.constants import CONTAINER_ID
            if self.params is None:
                self.params = {}
            self.params[CONTAINER_ID] = self.container_id

        if self.params is not None:
            l.append((PRMS, self.params))

        msg = json_helpers.to_json_string(l)
        return msg

    def _create_keep_alive_msg(self):
        if self.keep_alive is None:
            from ca_apm_agent.connections.constants import OP, ARF
            from ca_apm_agent.utils import json_helpers
            l = [(OP, ARF)]
            self.keep_alive = json_helpers.to_json_string(l)
        return self.keep_alive

    def worker(self):
        logger.info('Worker started')
        import time
        from ca_apm_agent.utils import json_helpers
        from ca_apm_agent.connections.constants import OP, CONFIG, COLLECTOR, VERSION, MESSAGE, SPEAK, PAUSE, CONTINUE, CMD, PRMS
        self.connect()
        while True:
            # Data connection sets this when its broken
            if ca_apm_agent.status.com_restart[0]:
                self.conn_status = False

            if self.conn_status:
                if not self.msg_queue.empty():
                    self.send_msg(self.msg_queue.get_nowait())
                recv_string = self.recv_msg()
                if recv_string:
                    try:
                        msgs = json_helpers.from_json_string(recv_string)
                    except Exception as e:
                        logger.error('Error Parsing  message from collector')
                        logger.debug('Message =' + recv_string)
                        logger.debug(str(e))
                    else:
                        for msg in msgs:
                            if msg[OP] == CONFIG:
                                if MESSAGE in msg:
                                    if COLLECTOR in msg[MESSAGE]:
                                        if VERSION in msg[MESSAGE][COLLECTOR]:
                                            self.collector_version = str(msg[MESSAGE][COLLECTOR][VERSION])
                                            logger.info('Connected to Collector %s', self.collector_version)
                                elif CMD in msg and msg[CMD] == VERSION:
                                    self.collector_version = str(msg[PRMS][COLLECTOR])
                                    logger.info('Connected to Collector %s', self.collector_version)
                                else:
                                    pass
                            elif msg[OP] == SPEAK:
                                self.send_msg(self._create_keep_alive_msg())
                                logger.debug('Received Keep-Alive, Sent Alive')
                            elif msg[OP] == PAUSE:
                                ca_apm_agent.status.com_pause[0] = True
                                logger.info('Received Pause message')
                            elif msg[OP] == CONTINUE:
                                ca_apm_agent.status.com_pause[0] = False
                                logger.info('Received Continue message')
                            else:
                                pass
                else:
                    if type(recv_string) == bool:
                        # The connection was broken on the other side and we will attempt to re-establish
                        logger.info('Will attempt to re-establish connection')
                        ca_apm_agent.status.com_restart[0] = True
                        ca_apm_agent.status.com_ready[0] = False
                    else:
                        # There was no data to read and receive passed an empty string
                        pass
            else:
                self.msg_queue.queue.clear()
                self.conn.close()
                self.connect()
                time.sleep(7)
                continue
            if self.msg_queue.empty():
                time.sleep(30)
