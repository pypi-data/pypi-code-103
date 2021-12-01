# coding=utf-8
# pylint: disable=import-error, broad-except
import json
from resources.models.helper import rest_post_json_call
from resources.models.helper import rest_get_call


class OakgateResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out

    def get_oakgate_device_list(self):
        url_ = "http://{0}:{1}/oakgate/device_list".format(self.host, self.port)
        result = rest_get_call(url_, self.session, self.time_out)
        return result["resource"]

