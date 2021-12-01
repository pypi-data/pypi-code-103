# coding=utf-8
# pylint: disable=import-error, broad-except
import json
from resources.models.helper import rest_post_json_call


class GitResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out

    def update_code(self, user, key, target_version):
        data = {"user": user, "key":key, "target_version": target_version}
        url_ = "http://{0}:{1}/git".format(self.host, self.port)
        result = rest_post_json_call(url_, self.session, json.dumps(data), self.time_out)
        return result["resource"]
