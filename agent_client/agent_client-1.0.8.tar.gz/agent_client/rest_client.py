# coding=utf-8
# pylint: disable=wrong-import-position, relative-import, import-error
import sys
import os
import requests
sys.path.append(os.path.join(os.path.dirname(__file__)))
from resources.dut_rest_resource import DutResource


class RestClient(object):

    def __init__(self, host, port=5000, time_out=5):
        __session = requests.Session()
        self.dut = DutResource(host, port, __session, time_out=time_out)

