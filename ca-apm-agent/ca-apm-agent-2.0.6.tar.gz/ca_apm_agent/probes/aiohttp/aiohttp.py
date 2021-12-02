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
from ca_apm_agent.connections.constants import TRACE_ID, CORR_ID, REQUEST_TYPE
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

class AiohttpProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        logger.debug('Python Agent- Aiohttp Probe Entered:')
        logger.debug('Function Arguments: %s **** %s', str(context.args), str(context.kwargs))
        
        #Get the url, hostname and port details
        url = context.args[1]
        host_info = parse.urlparse(url)
        host_name = host_info.hostname
        host_port = host_info.port

#        if host_name is None:
#            host_name = socket.gethostname()
#        if host_port is None:
#            host_port = "8998"

        hostName = socket.gethostname()
        port = "8998"
                            
        #Get the corId and tracId
        corId = corrid_helpers.get_corid()
        traceId = correlation.get_txn_traceid(corId)
        
        #Read the object attributes and update the header with corid
        obj1 = context.args[0]
        #pprint(vars(obj1))      ==> This pprint statment prints the object attributes and its values       
        obj1._default_headers["CORID"] = corId
        #pprint(vars(obj1)) 
        context.cor_id = corId
        http_corid = corId
        
        context.set_params({URL: url, HOST_NAME: host_name, HOST_PORT: host_port, TRACE_ID: traceId, CORR_ID: http_corid, REQUEST_TYPE: context.func_name[14:].upper()})
        logger.debug('Pushed params: %s', str(context.params))
        
    def finish(self, context):
        pass
