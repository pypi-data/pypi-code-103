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
from http.client import responses
from ca_apm_agent.python_modifiers.singleton import Singleton
from ca_apm_agent.connections.constants import CLASS, MESSAGE
from ca_apm_agent.global_constants import LOGGER_NAME
from ca_apm_agent.probes.aiohttp import http_error_status_code

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.aiohttp.aiohttp_server_http_error')


class AiohttpServerHTTPErrorProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        pass

    def finish(self, context):
        if context.args[0] and hasattr(context.args[0], '_match_info') and hasattr(context.args[0]._match_info, 'http_exception') and  \
           hasattr(context.args[0]._match_info.http_exception, 'status'):         
           statuscode = context.args[0]._match_info.http_exception.status
           if statuscode and statuscode > 399:
              cls = context.func_name
              msg = str(statuscode) + ': ' + responses[statuscode]
              context.set_exception({CLASS: cls, MESSAGE: msg})
              logger.debug('Set Exception Param %s', str(context.exc))

        status_reason = str(context.args[1])
        if status_reason:
          statuscode = http_error_status_code.get_http_status_code(status_reason)
          if statuscode and statuscode > 399:
            cls = context.func_name
            msg = str(statuscode) + ': ' + responses[statuscode]
            context.set_exception({CLASS: cls, MESSAGE: msg})
            logger.debug('Set Exception Param %s', str(context.exc))
              

