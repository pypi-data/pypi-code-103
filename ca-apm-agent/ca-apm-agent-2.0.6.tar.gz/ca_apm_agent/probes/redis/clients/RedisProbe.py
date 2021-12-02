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
from ca_apm_agent.connections.constants import PYTHON_MODULE
# Constants
REDIS_HOST = 'host'
REDIS_PORT = 'port'
DATABASE = 'database'
DATABASE_NAME = 'dbname'
COMMAND = 'command'
SQL = 'query'

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.redis.RedisProbe')

class RedisProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        logger.debug('Function Arguments: %s **** %s', str(context.args), str(context.kwargs))
        pool = context.args[0].connection_pool
        operation = context.args[1]
        command = str(context.args[2:])
        context.set_params({DATABASE: "Redis DB", DATABASE_NAME: pool.connection_kwargs['db'], REDIS_HOST: pool.connection_kwargs['host'], REDIS_PORT: pool.connection_kwargs['port'], COMMAND: operation, SQL: command, PYTHON_MODULE: "redis-py", "ATTR_Hostname": pool.connection_kwargs['host'], "ATTR_ipAddress": pool.connection_kwargs['host']})
        logger.debug('Pushed params: %s', str(context.params))

    def finish(self, context):
        pass
