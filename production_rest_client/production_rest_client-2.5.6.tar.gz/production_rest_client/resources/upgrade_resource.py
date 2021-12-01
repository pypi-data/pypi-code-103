import json
from resources.models.helper import rest_post_json_call


class UpgradeResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out

    def run(self, execute_name, parameters):
        data = {"execute_name": execute_name, "parameters":parameters}
        url_ = "http://{0}:{1}/upgrade".format(self.host, self.port)
        result = rest_post_json_call(url_, self.session, json.dumps(data), self.time_out)
        return result["resource"]
