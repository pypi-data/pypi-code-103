# coding=utf-8
# pylint: disable=wrong-import-position, relative-import, import-error
import sys
import os
import requests
sys.path.append(os.path.join(os.path.dirname(__file__)))
from resources.test_resource import TestResource
from resources.operation_resource import OperationResource
from resources.state_resource import StateResource
from resources.remote_resource import RemoteResource
from resources.benchmark_resource import BenchmarkResource
from resources.oakgate_resource import OakgateResource
from resources.stop_flag_resource import StopFlagResource
from resources.git_resource import GitResource
from resources.upgrade_resource import UpgradeResource
from resources.firmware_build_resource import FirmwareBuildResource


class RestClient(object):

    def __init__(self, host, port=5000, time_out=5):
        __session = requests.Session()
        self.test = TestResource(host, port, __session, time_out=time_out)
        self.operation = OperationResource(host, port, __session, time_out=time_out)
        self.state = StateResource(host, port, __session, time_out=time_out)
        self.remote = RemoteResource(host, port)
        self.benchmark = BenchmarkResource(host, port, __session, time_out)
        self.oakgate = OakgateResource(host, port, __session, time_out)
        self.stop_flag = StopFlagResource(host, port, __session, time_out)
        self.git = GitResource(host, port, __session, time_out)
        self.upgrade = UpgradeResource(host, port, __session, time_out)
        self.firmware_build = FirmwareBuildResource(host, port, __session, time_out)


# if __name__ == '__main__':
#     rest = RestClient("172.29.131.62")
#     # ret = rest.firmware_build.build_firmware("https://github.gtie.dell.com/RedTail/redtail_fw_joint.git",
#     #                                    "origin/master",
#     #                                    "shaobin_shu99",
#     #                                    "bc46a34fd88899d39e902576b8a9721029ce8bbb")
#     # print(ret)
#
#     result = rest.firmware_build.get_async_result("Ku3bwh2W6F")
#     print(result)
#     pass
# rest
