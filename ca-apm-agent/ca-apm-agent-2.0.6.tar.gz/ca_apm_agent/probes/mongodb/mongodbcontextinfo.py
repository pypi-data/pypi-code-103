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

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.mongodb.mongodbcontextinfo')


def get_context_info(req_string):

    request = req_string
    
    if request is None:
      logger.error('Request Context Arguments Received is NULL')
    else:
      logger.debug('Request Context Arguments Received Successfuly')

    port = request[:5]

    par_pos1 = request.find(")")
    req_subStr2 = request[par_pos1+3:]

    req_subStr3 = req_subStr2.replace(')', '')
    database, collection = req_subStr3.split(", ")
    dbname = database.replace("'","")

    return port, dbname, collection
