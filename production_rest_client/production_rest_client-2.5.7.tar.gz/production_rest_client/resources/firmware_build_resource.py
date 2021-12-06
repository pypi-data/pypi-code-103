# coding=utf-8
# pylint: disable=import-error, broad-except
import json
from resources.models.helper import rest_post_json_call
from resources.models.helper import rest_get_call
from resources.models.helper import TestType


class FirmwareBuildResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out

    def build_firmware(self, url, branch, user, pwd, project):
        parameter = {
            "rep_url": url,
            "rep_branch": branch,
            "rep_user": user,
            "rep_password": pwd,
            "project": project
        }
        url_ = "http://{0}:{1}/firmware_build".format(self.host, self.port)
        result = rest_post_json_call(url_, self.session, json.dumps(parameter), self.time_out)
        return result["resource"]

    def get_async_result(self, key):
        url_ = "http://{0}:{1}/firmware_build/{2}".format(self.host, self.port, key)
        result = rest_get_call(url_, self.session, self.time_out)
        return result["resource"]
