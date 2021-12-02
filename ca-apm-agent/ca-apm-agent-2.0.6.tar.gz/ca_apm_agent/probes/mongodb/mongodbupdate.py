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
spl_char = ':'
string_update_one = 'UpdateOne'
string_update_many = 'UpdateMany'
string_replace_one = 'ReplaceOne'

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.mongodb.mongodbupdate')

class MongodbUpdateProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        logger.debug('Function Arguments: %s **** %s', str(context.args), str(context.kwargs))
        
        request = str(context.args[0])
        
        req_subStr1 = request[39:]
        hostName = req_subStr1.partition(spl_char)[0]
        if hostName in ('localhost', '127.0.0.1', '', ' '):
            hostName=socket.gethostbyaddr(socket.gethostname())[0]
        request_string = req_subStr1.partition(spl_char)[2]
       
        CommandType = "Write Operations"
        
        bulk_request = context.args[1]
        
        bulk_write_flag = False
        bulk_updateone_flag = False
        bulk_updatemany_flag = False
        bulk_replace_flag = False

        if string_update_one in str(bulk_request):
          bulk_updateone_flag = True
        else:
          bulk_updateone_flag = False

        if string_update_many in str(bulk_request):
          bulk_updatemany_flag = True
        else:
          bulk_updatemany_flag = False

        if string_replace_one in str(bulk_request):
          bulk_replaceone_flag = True
        else:
          bulk_replaceone_flag = False
                  
        bulk_operations = (bulk_updateone_flag, bulk_updatemany_flag, bulk_replaceone_flag)
        bulk_write_flag = any(bulk_operations)
        
        if bulk_write_flag:
          for i in bulk_request:          
            if string_update_one in str(i):
               Command = "update_one"
               portNum, dbname , collectionname = mongodbcontextinfo.get_context_info(request_string)
               context.set_params({DATABASE: "MongoDB", DATABASE_NAME: dbname, COLLECTION_NAME: collectionname, MONGODB_HOST: hostName, MONGODB_PORT: portNum,
                                   PYTHON_MODULE: "pymongo", COMMAND_TYPE: CommandType, COMMAND: Command, "ATTR_hostname": hostName, "ATTR_port": portNum,
                                   "ATTR_ipAddress": hostName})               
            if string_update_many in str(i):
               Command = "update_many" 
               portNum, dbname , collectionname = mongodbcontextinfo.get_context_info(request_string)
               context.set_params({DATABASE: "MongoDB", DATABASE_NAME: dbname, COLLECTION_NAME: collectionname, MONGODB_HOST: hostName, MONGODB_PORT: portNum,
                                   PYTHON_MODULE: "pymongo", COMMAND_TYPE: CommandType, COMMAND: Command, "ATTR_hostname": hostName, "ATTR_port": portNum,
                                   "ATTR_ipAddress": hostName})               
            if string_replace_one in str(i):
               Command = "replace_one"
               portNum, dbname , collectionname = mongodbcontextinfo.get_context_info(request_string)
               context.set_params({DATABASE: "MongoDB", DATABASE_NAME: dbname, COLLECTION_NAME: collectionname, MONGODB_HOST: hostName, MONGODB_PORT: portNum,
                                   PYTHON_MODULE: "pymongo", COMMAND_TYPE: CommandType, COMMAND: Command, "ATTR_hostname": hostName, "ATTR_port": portNum,
                                   "ATTR_ipAddress": hostName})
        else:
            context_length = len(context.args)
            if context_length < 4:
               document_latestvalue = str(context.args[2])
               set_pos = document_latestvalue.find("$set")
               if set_pos == -1:
                   Command = "replace_one"
               else:
                   Command = "update_one"
            else:
                Command = "update_many"
        
            portNum, dbname , collectionname = mongodbcontextinfo.get_context_info(request_string)
            context.set_params({DATABASE: "MongoDB", DATABASE_NAME: dbname, COLLECTION_NAME: collectionname, MONGODB_HOST: hostName, MONGODB_PORT: portNum,
                               PYTHON_MODULE: "pymongo", COMMAND_TYPE: CommandType, COMMAND: Command, "ATTR_hostname": hostName, "ATTR_port": portNum,
                               "ATTR_ipAddress": hostName})

    def finish(self, context):
        pass
