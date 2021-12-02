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
import logging
from ca_apm_agent.global_constants import LOGGER_NAME
from ca_apm_agent.connections.data import Data
from ca_apm_agent.utils import network

logger = logging.getLogger(LOGGER_NAME[0] + '.instruments.fork_handler')


def patch_method(target_func, host, port, instid, data_q, sleep_time):
    def function_template(*args, **kwargs):
        res = target_func(*args, **kwargs)
        try:
            if res == 0:
                # Change the logging file name
                tlogger = logging.getLogger(LOGGER_NAME[0])
                file_handler = None
                for x in tlogger.handlers:
                    if type(x).__name__ == 'RotatingFileHandler':
                        file_handler = x
                        break
                if file_handler:
                    t = file_handler.baseFilename.split('.')
                    processid = os.getpid()
                    containerid = network.getcontainerid()
                    if containerid:
                       processid = containerid
                    t[-2] = str(processid)
                    file_handler.baseFilename = '.'.join(t)
                    # Force a rollover so that the new logfile is created
                    file_handler.doRollover()
                    logger.debug('Changed logfile name')

                logger.info('Starting data connection for new process')
                data_conn = Data(host=host, port=port, instid=instid, data_msg_queue=data_q)
                data = threading.Thread(name='data_connection_worker', target=data_conn.worker,
                                        args=(sleep_time,))
                data.daemon = True
                data.start()
        except Exception as e:
            logger.error('Exception executing handler')
            logging.debug('Exception that was raised %s', str(e))
        finally:
            return res

    return function_template
