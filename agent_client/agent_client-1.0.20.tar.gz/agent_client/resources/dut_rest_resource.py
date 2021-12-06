# coding=utf-8
# pylint: disable=import-error, eval-used
import json
from resources.models.helper import rest_get_call, rest_post_json_call


class DutResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out

    def update_status(self):
        url_ = "http://{0}:{1}/dut/status".format(self.host, self.port)
        data = dict()
        result = rest_post_json_call(url_, self.session, json.dumps(data), self.time_out)
        return result["resource"]
