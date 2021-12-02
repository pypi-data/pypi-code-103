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
from collections import OrderedDict
import json


def to_json_string(list_of_tuples):
    msg = json.dumps(OrderedDict(list_of_tuples))
    msg = msg.replace(', ', ',')
    msg = msg.replace(': ', ':')
    return msg


def from_json_string(string):
    string = string.replace('\r', '')
    string = string.replace('\n', '')
    string = string.replace('"{', '{')
    string = string.replace('}"', '}')
    string = string.replace('\\"', '"')
    string = string.split('}{')
    if len(string) > 1:
        string[0] = string[0] + '}'
        msg = [json.loads(string[0])]
        for i in range(1, len(string) - 1):
            string[i] = '{' + string[i] + '}'
            temp = json.loads(string[i])
            if temp != msg[-1]:
                msg.append(temp)
        string[-1] = '{' + string[-1]
        temp = json.loads(string[-1])
        if temp != msg[-1]:
            msg.append(temp)
        return msg
    msg = [json.loads(string[0])]
    return msg
