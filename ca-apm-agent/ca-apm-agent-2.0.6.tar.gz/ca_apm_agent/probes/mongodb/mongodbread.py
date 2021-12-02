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
import socket
from ca_apm_agent.trace_enablers.context import Context
from ca_apm_agent.probes.mongodb import mongodbcontextinfo

# Constants
MONGODB_HOST = 'host'
MONGODB_PORT = 'port'
DATABASE = 'database'
DATABASE_NAME = 'dbname'
COLLECTION_NAME = 'collectionname'
COMMAND_TYPE = 'commandtype'
COMMAND = 'command'

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.mongodb.mongodbread')  

class MongodbReadProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        logger.debug('Function Arguments: %s **** %s', str(context.args), str(context.kwargs))
        
        request = str(context.args[0])
        host_pos = request.find("host")
        req_subStr1 = request[host_pos+7:]
        colon_pos = req_subStr1.find(":")
        hostName = req_subStr1[:colon_pos]
        if hostName in ('localhost', '127.0.0.1', '', ' '):
            hostName=socket.gethostbyaddr(socket.gethostname())[0]       
        req_subStr2 = req_subStr1[colon_pos+1:]
        CommandType = "Read Operations"
        context_length = len(context.args)
        if context_length < 2:
            Command = "find"
        else:
            Command = "find_one"
        
        portNum, dbname , collectionname = mongodbcontextinfo.get_context_info(req_subStr2)
        
        context.set_params({DATABASE: "MongoDB", DATABASE_NAME: dbname, COLLECTION_NAME: collectionname, MONGODB_HOST: hostName, MONGODB_PORT: portNum,
                           PYTHON_MODULE: "pymongo", COMMAND_TYPE: CommandType, COMMAND: Command, "ATTR_hostname": hostName, "ATTR_port": portNum,
                           "ATTR_ipAddress": hostName})

    def finish(self, context):
        pass
