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
from ca_apm_agent.trace_enablers.virtual_stack import VirtualStack
from ca_apm_agent.connections.constants import TRACE_ID, CORR_ID, REQUEST_TYPE
from ca_apm_agent.correlation import correlation
from ca_apm_agent.utils import corrid_helpers

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.urllib.http')
# Constants
URL = 'url'
HOST_NAME = 'hostName'
HOST_PORT = 'hostPort'

class HTTPUrllibProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        logger.debug('Function Arguments: %s **** %s', str(context.args), str(context.kwargs))
        req = context.args[2]
        url = req.full_url
        request_type = req.get_method()
        host_info = parse.urlparse(req.full_url)
        host_name = host_info.hostname
        host_port = host_info.port 

        corId = corrid_helpers.get_corid()
        traceId = correlation.get_txn_traceid(corId)
        correlationId = {'CORID':corId}
        req.unredirected_hdrs.update(correlationId)
        context.cor_id = corId
        http_corid = corId
        
        context.set_params({URL: url, HOST_NAME: host_name, HOST_PORT: host_port, TRACE_ID: traceId, CORR_ID: http_corid, REQUEST_TYPE: request_type})
        logger.debug('Pushed params: %s', str(context.params))           

    def finish(self, context):
        pass