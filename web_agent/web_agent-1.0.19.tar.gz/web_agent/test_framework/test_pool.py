import threading
import time
import os
import string
import random
from datetime import datetime, timezone, timedelta
from test_framework.test_case import TestCase
from test_framework.test_suite import TestSuite
from test_framework.firmware_download import FirmwareDownloader
from rest_server.resource.models.helper import MyThread
from test_framework.state import State
from test_framework.state import TestType
from test_framework.database.database import decorate_add_tests, decorate_update_test_state
from test_framework.database.dut_database import agent_heart_beat
from test_framework.state import AgentState
from test_framework.dut.dut import Dut
from utils import log


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner


@singleton
class TestPool(object):

    def __init__(self):
        self.thread_pool = list()
        self.test_pool = list()
        self._stop_flag = True
        self.run_manage_thread()
        self.all_test_case = self.get_all_test_case()
        self.all_test_suite = self.get_all_test_suite()

    @staticmethod
    def refresh_dut():
        dut = Dut()
        dut.refresh()

    @property
    def stop_flag(self):
        return self._stop_flag

    @stop_flag.setter
    def stop_flag(self, stop_flag):
        self._stop_flag = stop_flag
        log.INFO(type(self._stop_flag))
        log.INFO("set stop flag to {}".format(self._stop_flag))

    def get_all_test_case(self):
        test_case = TestCase()
        lists = test_case.list_and_filter_tests("all")
        return lists

    def get_all_test_suite(self):
        test_suite = TestSuite()
        lists = test_suite.list_and_filter_tests("all")
        return lists

    def run_manage_thread(self):
        thread_p = threading.Thread(target=self.thread_pool_manage)
        thread_p.setDaemon(True)
        thread_p.start()
        thread_t = threading.Thread(target=self.test_pool_manage)
        thread_t.setDaemon(True)
        thread_t.start()
        thread_t = threading.Thread(target=self.dut_state_manage)
        thread_t.setDaemon(True)
        thread_t.start()

    def thread_pool_manage(self):
        while True:
            for index, thread_ in enumerate(self.thread_pool):
                if thread_["state"] == State.NOT_START:
                    p_thread, test_object = self._start_test_thread(thread_)
                    self.thread_pool[index]["pthread"] = p_thread
                    self.thread_pool[index]["test_object"] = test_object
                    self.thread_pool[index]["state"] = State.RUNNING
                    self._update_test_pool_state(thread_["key"], State.RUNNING, None)
                elif thread_["state"] == State.RUNNING:
                    if thread_["pthread"].is_alive() is False:
                        test_result = thread_["pthread"].get_result()
                        state = self.get_state_from_result(test_result)
                        self.thread_pool[index]["state"] = state
                        if (state == State.FAIL) and (self._stop_flag is True):
                            log.INFO("Test failed, abort not start case")
                            self._abort_not_start_tests()
                        self._update_test_pool_state(thread_["key"], state, test_result)
                elif thread_["state"] in [State.PASS, State.FAIL, State.BLOCK, State.ERROR_UNHEALTHY]:
                    self.thread_pool.pop(index)
                elif thread_["state"] == State.ABORT:
                    self.thread_pool.pop(index)
            time.sleep(2)

    def get_state_from_result(self, results):
        if results is not None:
            if len(results) > 1:
                fail_result = [result for result in results if result["result"] is State.FAIL]
                state = State.FAIL if fail_result else State.PASS
            else:
                state = results[0]["result"]
        else:
            state = State.ERROR_BASE_EXCEPTION
        return state

    def test_pool_manage(self):
        while True:
            time.sleep(5)
            try:
                self.add_new_test_to_run()
            except Exception as all_exception:
                log.ERR(all_exception)

    def dut_state_manage(self):
        self.refresh_dut()
        while True:
            time.sleep(5)
            try:
                self.timing_refresh_dut()
                self.heart_beat_check_env_state()
            except Exception as all_exception:
                log.ERR(all_exception)

    def add_new_test_to_run(self):
        ret = self._has_running_test()
        if ret is False:
            for index, test in enumerate(self.test_pool):
                if test["state"] == State.NONE:
                    self._add_test_to_thread_pool(test)
                    self.test_pool[index]["state"] = State.NOT_START
                    break

    def timing_refresh_dut(self):
        now = datetime.now(timezone(timedelta(hours=+8)))
        if (now.hour == 23 and now.minute == 59 and now.second in range(49, 59)) or\
                (now.hour == 0 and now.minute == 0 and now.second in range(0, 10)):
            self.refresh_dut()

    def get_current_agent_state(self):
        tests = [test for test in self.test_pool if test["state"] in [State.NOT_START, State.RUNNING, State.NONE]]
        if tests:
            agent_state = AgentState.Running
        else:
            agent_state = AgentState.Online
        return agent_state

    def _add_test_to_thread_pool(self, test):
        test_thread = {
            "key": test["key"],
            "pthread": None,
            "test_object": None,
            "test_name": test["test_name"],
            "test_type": test["test_type"],
            "state": State.NOT_START,
            "thread_type": "test",
            "test_parameters": test["test_parameters"]
            }
        log.INFO("add test case {}".format(test["test_name"]))
        self.thread_pool.append(test_thread)

    def _has_running_test(self):
        result = True if self.thread_pool else False
        return result

    def _abort_not_start_tests(self, key=None):
        for test_ in self.test_pool:
            if test_["state"] in [State.NOT_START, State.NONE]:
                if key is None or test_["key"] == key:
                    self._update_test_pool_state(test_["key"], State.ABORT, None)

    @decorate_update_test_state
    def _update_test_pool_state(self, test_key, state, test_result):
        for index, thread_ in enumerate(self.test_pool):
            if thread_["key"] == test_key:
                self.test_pool[index]["state"] = state
                self.test_pool[index]["test_result"] = test_result

    def _start_test_thread(self, thread_info):
        test_name = thread_info["test_name"]
        test_type = thread_info["test_type"]
        test_parameters = thread_info["test_parameters"]
        thread_ = None
        test_object = None
        if test_type == TestType.TestCase:
            self.set_test_parameters(test_parameters)
            thread_, test_object = self._start_test_case_thread(test_name, test_parameters)
        elif test_type == TestType.TestSuite:
            self.set_test_parameters(test_parameters)
            thread_, test_object = self._start_test_suite_thread(test_name, test_parameters)
        elif test_type == TestType.DownloadSerial:
            thread_, test_object = self._start_download_serial_thread(test_name, test_parameters)
        return thread_, test_object

    def _start_test_suite_thread(self, test_name, test_parameters):
        test_suite = TestSuite()
        thread_ts = MyThread(target=test_suite.run, args=(test_name, test_parameters,))
        thread_ts.setDaemon(True)
        thread_ts.start()
        return thread_ts, test_suite

    def _start_test_case_thread(self, test_name, test_parameters):
        test_case = TestCase(test_name)
        thread_tc = MyThread(target=test_case.run, args=(test_name, test_parameters,))
        thread_tc.setDaemon(True)
        thread_tc.start()
        return thread_tc, test_case

    def _start_download_serial_thread(self, execute_name, test_parameters):
        downloader = FirmwareDownloader(execute_name)
        thread_tc = MyThread(target=downloader.run, args=(test_parameters,))
        thread_tc.setDaemon(True)
        thread_tc.start()
        return thread_tc, downloader

    def _get_unique_code(self):
        letter_len = 10
        code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(letter_len))
        return code

    def _stop_running_test_process(self, test_object):
        ret = 0
        if test_object is not None:
            ret = test_object.stop()
        return ret

    def _stop_running_tests(self):
        result = True
        ret_stop_test = -1
        for index, thread_ in enumerate(self.thread_pool):
            print(thread_)
            if thread_["thread_type"]=="test" and thread_["state"]==State.RUNNING:
                test_object = thread_["test_object"]
                self.thread_pool[index]["state"] = State.ABORT
                self._update_test_pool_state(thread_["key"], State.ABORT, None)
                for index_ in range(10):
                    ret_stop_test = self._stop_running_test_process(test_object)
                    log.INFO("Stop test thread loop %s, ret %s", index_, ret_stop_test)
                    if ret_stop_test == 0:
                        break
                time.sleep(1)
                count = 0
                while thread_["pthread"].is_alive() is True and count < 2:
                    log.INFO("Stop thread loop ")
                    thread_["pthread"].stop()
                    time.sleep(1)
                    count = count + 1
        return result

    def _check_test_is_exist(self, test_name, test_type):
        if test_type == TestType.TestSuite:
            ret = True if test_name in self.all_test_suite else False
        elif test_type == TestType.TestCase:
            ret = True if test_name in self.all_test_case else False
        else:
            ret = True
        return ret

    @decorate_add_tests
    def add_test(self, test_name, test_type, test_parameters=None):
        if self._check_test_is_exist(test_name, test_type):
            unique_code = self._get_unique_code()
            if test_parameters is not None:
                test_parameters["key"] = unique_code
            test_dict = {"test_name": test_name,
                         "test_type": test_type,
                         "state": State.NONE,
                         "test_result": None,
                         "thread_type": "test",
                         "key": unique_code,
                         "test_parameters": test_parameters}
            self.test_pool.append(test_dict)
        else:
            unique_code = None
        return unique_code

    def stop_test(self, key=None):
        if key is None:
            result = self._stop_all_tests()
        else:
            result = self._stop_test_by_key(key)
        return result

    def _stop_all_tests(self):
        self._abort_not_start_tests()
        result = self._stop_running_tests()
        return result

    def _stop_test_by_key(self, key):
        result = True
        test_case = self.find_test_state_by_key(key)
        if test_case is not None:
            test_state = test_case["state"]
            if test_state in [State.NOT_START, State.NONE]:
                self._abort_not_start_tests(key)
            elif test_state == State.RUNNING:
                self._abort_not_start_tests(key)
                result = self._stop_running_tests()
        return result

    def find_test_state_by_key(self, key):
        test_case = None
        for index, test_ in enumerate(self.test_pool):
            if self.test_pool[index]["key"] == key:
                test_case = test_
        return test_case

    def get_state_by_key(self, key):
        test = list(filter(lambda X: X["key"] == key, self.test_pool))
        if test:
            result = test[0]["test_result"]
            state = test[0]["state"]
        else:
            log.ERR("Test:%s, did not found", key)
            state = State.ERROR_NOT_FOUND
            result = None
        return result, state

    @agent_heart_beat
    def heart_beat_check_env_state(self):
        status = self.get_current_agent_state()
        return status

    @staticmethod
    def set_test_parameters(parameters):
        if type(parameters) is dict:
            for key in parameters.keys():
                os.environ[key] = parameters[key]

    def test_set_parameters(self, parameters):
        print("Custom global parameters: ")
        if type(parameters) is dict:
            for key in parameters.keys():
                print("parametesr: ", key, os.environ[key])


if __name__ == '__main__':
    pass
