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
from ca_apm_agent.python_modifiers.singleton import Singleton
from ca_apm_agent.connections.constants import CLASS, MESSAGE
from ca_apm_agent.global_constants import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.error')


class ErrorProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        pass

    def finish(self, context):
        if hasattr(context, 'e'):
            cls = context.func_name
            msg = context.v.__class__.__name__ + '.' + str(context.v)
            context.set_exception({CLASS: cls, MESSAGE: msg})
            logger.debug('Set Exception Param %s', str(context.exc))
