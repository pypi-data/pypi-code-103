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
import time
import json
import socket
from ca_apm_agent.utils import json_helpers
from ca_apm_agent.global_constants import LOGGER_NAME
from ca_apm_agent.python_modifiers.singleton import Singleton
from ca_apm_agent.connections.constants import PYTHON_MODULE, PYTHON_RASA_INTENT

logger = logging.getLogger(LOGGER_NAME[0] + '.probes.rasa.rasa')

class RasaProbe(Singleton):
    def __init__(self):
        pass

    def start(self, context):
        logger.debug('Rasa Probe -Start Method')
        context_res=context.res
        message_id = 'Default'
        json_string = json_helpers.from_json_string(json.dumps(context.res))
        intent_name = json_string[0]['intent']['name']
        intent_confidence = json_string[0]['intent']['confidence']
        user_input = json_string[0]['text']
        hostName = socket.gethostname()
        port = "5005"
        context.set_params({"url": intent_name, "hostName": hostName, "hostPort": port, "Confidence": intent_confidence, "UserInput": user_input,
                            "MessageId": message_id, PYTHON_MODULE: "Rasa", PYTHON_RASA_INTENT: intent_name})


    def finish(self, context):
        logger.debug('Rasa Probe - Finish Method')
