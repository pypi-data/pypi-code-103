# coding=utf-8
# pylint: disable=import-error, broad-except
import json
from resources.models.helper import rest_post_json_call
from resources.models.helper import rest_get_call
from resources.models.helper import TestType


class BenchmarkResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out

    def start_benchmark_test(self, parameters=None):
        benchmark_parameter = {
            "type": TestType.TestBenchmark,
            "parameters": parameters
        }
        url_ = "http://{0}:{1}/benchmark".format(self.host, self.port)
        result = rest_post_json_call(url_, self.session, json.dumps(benchmark_parameter), self.time_out)
        return result["resource"]

    def start_benchmark_group_test(self, test_name, parameters=None):
        group_parameter = {
            "type": TestType.TestBenchmarkGroup,
            "test_name": test_name,
            "parameters": parameters
        }
        url_ = "http://{0}:{1}/benchmark".format(self.host, self.port)
        result = rest_post_json_call(url_, self.session, json.dumps(group_parameter), self.time_out)
        return result["resource"]

    def get_async_result(self, key):
        url_ = "http://{0}:{1}/benchmark/results/{2}".format(self.host, self.port, key)
        result = rest_get_call(url_, self.session, self.time_out)
        return result["resource"]

    def get_iometer_script_list(self):
        url_ = "http://{0}:{1}/benchmark/iometer/testlist".format(self.host, self.port)
        result = rest_get_call(url_, self.session, self.time_out)
        return result["resource"]
