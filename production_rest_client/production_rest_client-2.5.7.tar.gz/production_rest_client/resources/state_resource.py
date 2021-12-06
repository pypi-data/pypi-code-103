# coding=utf-8
# pylint: disable=import-error, eval-used
import json
from resources.models.helper import rest_get_call, rest_post_json_call


class StateResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out

    def get_state(self, type_="ALL"):
        url_ = "http://{0}:{1}/state/{2}".format(self.host, self.port, type_)
        result = rest_get_call(url_, self.session, self.time_out)
        if result["resource"]["data"] is not None and len(result["resource"]["data"]) > 3:
            result["resource"]["data"][3] = eval(result["resource"]["data"][3])
        return result["resource"]

    def update_state(self):
        url_ = "http://{0}:{1}/state".format(self.host, self.port)
        data = dict()
        result = rest_post_json_call(url_, self.session, json.dumps(data), self.time_out)
        return result["resource"]



