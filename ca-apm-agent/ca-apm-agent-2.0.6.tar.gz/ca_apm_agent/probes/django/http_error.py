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

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.error')


class HTTPErrorProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        pass

    def finish(self, context):
        if hasattr(context, 'res') and context.res.status_code > 399:
            cls = context.func_name
            msg = str(context.res.status_code) + ': ' + responses[context.res.status_code]
            context.set_exception({CLASS: cls, MESSAGE: msg})
            logger.debug('Set Exception Param %s', str(context.exc))
