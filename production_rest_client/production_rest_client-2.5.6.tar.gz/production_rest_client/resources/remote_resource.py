# coding=utf-8
# pylint: disable=import-error, broad-except
# pylint: disable=wrong-import-position, relative-import
from resources.models.remoter import RemoteCtrl

class RemoteResource(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        cfg_file = './comConfig.yaml'
        self.remote = RemoteCtrl(host, ini=cfg_file)

    def list(self, filter_):
        '''
        get all test cases
        '''
        pass

    def run(self, test_case):
        module = "test_run"
        ret = self.remote.power_test(module, test_case)
        print(ret)

    def get_async_result(self, key):
        module = "test_query"
        ret = self.remote.power_test(module, key)
        print(ret)

    def stop_tests(self, key=None):
        module = "test_stop"
        ret = self.remote.power_test(module, key)
        print(ret)

if __name__ == '__main__':
    REMOTE = RemoteResource("172.29.130.89", 5000)
    REMOTE.run("test_fio_windows:TestFioWindows.test_rand_mix_rw_70_30")
    #time.sleep(1)
    #remote.stop_tests("SFqK9IJO0D")
