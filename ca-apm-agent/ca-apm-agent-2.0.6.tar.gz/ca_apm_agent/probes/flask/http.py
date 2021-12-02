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
from ca_apm_agent.global_constants import LOGGER_NAME
from ca_apm_agent.python_modifiers.singleton import Singleton
from ca_apm_agent.connections.constants import TRACE_ID, CORR_ID, PYTHON_MODULE
from ca_apm_agent.correlation import correlation

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.flask.http')
# Constants
URL = 'url'
HOST_NAME = 'hostName'
HOST_PORT = 'hostPort'

class HTTPFlaskProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        environ = context.args[1]
        logger.debug("Flask Context Parameters : %s", str(environ))
        url = environ.get('RAW_URI')
        hostName = environ.get('HTTP_HOST')
        port = environ.get('SERVER_PORT')
        http_corid = environ.get('HTTP_CORID')
        
        if not http_corid:
           corId = correlation.get_new_corid_header()
           traceId = correlation.get_txn_traceid(corId)
           http_corid = corId
           context.cor_id = corId
        else:
           corId = correlation.upd_corid_header(http_corid)
           traceId = correlation.get_txn_traceid(corId)
           context.cor_id = corId
           
        if url is None:
           logger.debug("Flask URL is None setting to Default")
           url = "Default"
        else:
           logger.debug("Valid Flask request URL")  

        context.set_params({URL: url, HOST_NAME: hostName, HOST_PORT: port, TRACE_ID: traceId, CORR_ID: http_corid, PYTHON_MODULE: "Flask"})

    def finish(self, context):
        pass
