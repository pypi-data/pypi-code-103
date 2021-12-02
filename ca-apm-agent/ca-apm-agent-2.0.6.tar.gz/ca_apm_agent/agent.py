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
import os
import sys
import threading

from ca_apm_agent.config import read_instrument_cfg, read_agent_cfg, configure_logger, agent_config_monitor, instrument_config_monitor
from ca_apm_agent.global_constants import LOGGER_NAME
from ca_apm_agent.connections.command import Command
from ca_apm_agent.connections.data import Data
from ca_apm_agent.patchers import fork_handler
from ca_apm_agent.patchers.monkey import Patcher
from ca_apm_agent.utils import network

logger = None


class Agent:
    patch = None

    def __init__(self, acfg, icfg, comm_q, data_q):
        # Below function sets attributes mentioned in CA_APM_PYTHON_ACFG
        self.apply_config(acfg)
        # After this is everything that are properties of the core agent that is static
        #  OR it cannot come through the agent config file
        processid = os.getpid()
        containerid = network.getcontainerid()
        
        if containerid:
           processid = containerid
           
        self.instid = processid
        self.icfg_mtime = icfg.pop()
        self.comm_q = comm_q
        self.data_q = data_q

        configure_logger(self.log, str(self.instid))

        # Logging can begin after this point.
        global logger
        logger = logging.getLogger(LOGGER_NAME[0] + '.agent')

        # After this all object instantiations
        self.comm_conn = Command(host=self.host, port=self.port, instid=self.instid, app_name=self.app_name,
                                 com_msg_queue=self.comm_q)
        self.data_conn = Data(host=self.host, port=self.port, instid=self.instid, data_msg_queue=self.data_q)
        self.patcher = Patcher(icfg, self.data_q)
        Agent.patch = self.patcher.patch

        # Logic to patch os.fork() - if it exists
        _os_ref = sys.modules['os']
        _fork_ref = getattr(_os_ref, 'fork', None)
        if _fork_ref:
            patched = fork_handler.patch_method(_fork_ref, self.host, self.port, self.instid, self.data_q,
                                                self.sleep_time)
            setattr(_os_ref, 'fork', patched)

        logger.debug('Agent attributes after creation %s', str(self.__dict__))

    def apply_config(self, cfg):
        for k, v in cfg.items():
            setattr(self, k, v)

    def start_agent(self):
        agent_config_monitor(self)
        instrument_config_monitor()
        comm = threading.Thread(name='command_connection_worker', target=self.comm_conn.worker)
        data = threading.Thread(name='data_connection_worker', target=self.data_conn.worker, args=(self.sleep_time,))
        comm.daemon = True
        data.daemon = True
        try:
            comm.start()
            data.start()
        except Exception as e:
            logger.error('Exception starting workers')
            logger.debug('Exception that was raised %s', str(e))
