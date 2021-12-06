# coding=utf-8
# pylint: disable=wrong-import-position, relative-import, import-error
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from resources.benchmark_db_resource import BenchmarkDBResource
from resources.env_db_resource import EnvDBResource
from resources.test_db_resource import TestDBResource


class DBClient(object):

    def __init__(self):
        self.benchmark_resource = BenchmarkDBResource(db_name="performance_test")
        self.env_resource = EnvDBResource(db_name="nodes")
        self.test_resource = TestDBResource(db_name="production_test")

    def __del__(self):
        del self.benchmark_resource
        del self.env_resource
        del self.test_resource