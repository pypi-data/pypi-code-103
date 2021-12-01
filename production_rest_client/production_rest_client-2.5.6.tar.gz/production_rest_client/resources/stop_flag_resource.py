# coding=utf-8
# pylint: disable=import-error,eval-used
import json
from resources.models.helper import rest_get_call
from resources.models.helper import rest_post_json_call
from resources.models.helper import rest_delete_call
from resources.models.helper import State
from resources.test_db_resource import TestDBResource


class StopFlagResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out

    def get_stop_flag(self):
        url_ = "http://{0}:{1}/stopflag".format(self.host, self.port)
        result = rest_get_call(url_, self.session, self.time_out)
        if result["resource"]["state"] == State.PASS:
            result["resource"]["data"] = eval(result["resource"]["data"][0])
        return result["resource"]

    def set_stop_flag(self, stop_flag):
        data = {"stop_flag": stop_flag}
        url_ = "http://{0}:{1}/stopflag".format(self.host, self.port)
        result = rest_post_json_call(url_, self.session, json.dumps(data), self.time_out)
        return result["resource"]