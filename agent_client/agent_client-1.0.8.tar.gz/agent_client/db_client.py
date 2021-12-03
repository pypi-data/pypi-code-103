# coding=utf-8
# pylint: disable=wrong-import-position, relative-import, import-error
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from resources.dut_database import DutDatabase


class DBClient(object):

    def __init__(self):
        self.dut_resource = DutDatabase()

    def __del__(self):
        del self.dut_resource
