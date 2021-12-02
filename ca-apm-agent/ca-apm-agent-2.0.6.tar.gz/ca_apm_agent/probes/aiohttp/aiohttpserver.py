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
import socket
from ca_apm_agent.global_constants import LOGGER_NAME
from ca_apm_agent.python_modifiers.singleton import Singleton
from ca_apm_agent.trace_enablers.virtual_stack import VirtualStack
from ca_apm_agent.connections.constants import TRACE_ID, CORR_ID, PYTHON_MODULE
from ca_apm_agent.correlation import correlation
from ca_apm_agent.utils import corrid_helpers
from pprint import pprint
from multidict import CIMultiDict

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.aiohttp.aiohttp')
# Constants
HTTP = 'http'
URL = 'url'
HOST_NAME = 'hostName'
HOST_PORT = 'hostPort'

class AiohttpServerProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        logger.debug('Python Agent- Aiohttp Server Probe Entered:')
        logger.debug('Function Arguments: %s **** %s', str(context.args), str(context.kwargs))
        
        obj1 = context.args[0]
        #pprint(vars(obj1))
        
#       Get the url, hostname and port details
        url = str(obj1._rel_url)
        
        host_name_port = str(obj1._headers["Host"])
        colon_pos = host_name_port.find(":")
        if colon_pos == -1:
          logger.debug('Host name and port are not properly reported')
        else:
          host_name = host_name_port[:colon_pos]
          host_port = host_name_port[colon_pos+1:]
          logger.debug('Successfully Captured Host name and port')

#        if host_name is None:
#            host_name = socket.gethostname()
#        if host_port is None:
#            host_port = "8999"

        hostName = socket.gethostname()
        port = "8999"
                    
#       Get the corId and tracId
        #http_corid = str(obj1._headers["CORID"])
        environ = obj1._headers
        http_corid = environ.get('CORID')

        if not http_corid:
           corId = correlation.get_new_corid_header()
           traceId = correlation.get_txn_traceid(corId)
           http_corid = corId
           context.cor_id = corId
        else:
           corId = correlation.upd_corid_header(http_corid)
           traceId = correlation.get_txn_traceid(corId)
           context.cor_id = corId
                   
        context.set_params({URL: url, HOST_NAME: host_name, HOST_PORT: host_port, TRACE_ID: traceId, CORR_ID: http_corid, PYTHON_MODULE: "Aiohttp Server API"})
        logger.debug('Pushed params: %s', str(context.params))
        
    def finish(self, context):
        pass
