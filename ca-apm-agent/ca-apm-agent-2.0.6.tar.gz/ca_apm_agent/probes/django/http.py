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
from ca_apm_agent.connections.constants import TRACE_ID, CORR_ID, HTTP_CORID, PYTHON_MODULE
from ca_apm_agent.correlation import correlation

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.django.http')
# Constants
HTTP = 'http'
URL = 'url'
HOST_NAME = 'hostName'
HOST_PORT = 'hostPort'

class HTTPProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        logger.debug('Function Arguments: %s **** %s', str(context.args), str(context.kwargs))
        request = context.args[1]
        context.func_name = HTTP + '.' + request.method
        host_info = request.get_host()
        http_corid = request.META.get(HTTP_CORID)

        if not http_corid:
           corId = correlation.get_new_corid_header()
           traceId = correlation.get_txn_traceid(corId)
           request.META[HTTP_CORID] = corId
           http_corid = corId
           context.cor_id = corId
        else:
           corId = correlation.upd_corid_header(http_corid)
           traceId = correlation.get_txn_traceid(corId)
           request.META[HTTP_CORID] = corId
           context.cor_id = corId

        try:
            host, port = host_info.split(':')
        except ValueError:
            host = host_info
            port = '0'
        url = request.get_full_path()
        context.set_params({URL: str(url), HOST_NAME: host, HOST_PORT: port, TRACE_ID: traceId, CORR_ID: http_corid, PYTHON_MODULE: "Django"})
        logger.debug('Pushed params: %s', str(context.params))

    def finish(self, context):
        pass
