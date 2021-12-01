import os
import traceback
from typing import Callable

from test_executor.abstract_test.abstract_test import AbstractTest
from test_executor.abstract_test.test_result import TestResult, TestVerdict
from test_executor.common import DEFAULT_LOGS_FOLDER
from test_executor.logger_factory.logger_factory import LoggerFactory


class ListenerNotSupported(Exception):
    """
    Exception that will be raised in case a listener is not supported
    """
    pass


class TestRunnable(object):
    """
    Represents a runnable test
    """
    _test_function: Callable
    _test_class: AbstractTest
    _test_number: int

    __test__ = False

    def __init__(self, test_function: Callable, test_class: AbstractTest, test_number: int):
        """
        :param test_function: the test's function to run
        :param test_class: the test's class object
        :param test_number: the test's number
        """
        self._test_function = test_function
        self._test_class = test_class
        self._test_number = test_number
        self._result_listeners = []

    def __repr__(self):
        return f"{self._test_class.__class__.__name__}.{self._test_function.__name__}"

    def run(self, logs_folder: str = DEFAULT_LOGS_FOLDER) -> TestResult:
        """
        Executes a test function with Setup & Cleanup flows.
        In case that Setup fails, Cleanup will be executed

        :param logs_folder: path to set logs to
        :return: the test's result
        """
        test_name = f"{self.__class__.__name__}.{self._test_function.__name__}"
        result = TestResult(test_number=self._test_number, test_name=test_name)
        result.test_log = os.path.join(logs_folder, f"{self._test_number}_{test_name}", "test_log.log")

        self._test_class.logger = LoggerFactory.generate_logger(result.test_log)

        try:
            self._test_class.setup()
        except Exception as e:
            self.on_failed(result, reason=str(e))
            traceback_exc = traceback.format_exc()
            try:
                self._test_class.cleanup()
            except Exception as e:
                self._test_class.logger.warning(f"Test cleanup failed with: {e}")
                self._test_class.logger.error(f"Cleanup Traceback:\n{traceback.format_exc()}")

            self._test_class.logger.error(f"Setup Traceback:\n{traceback_exc}")
            return result

        try:
            self._test_class.pre_test()
            self._test_function()
            self._test_class.post_test()
        except Exception as e:
            self.on_failed(result, reason=str(e))
            self._test_class.logger.error(f"Test Traceback:\n{traceback.format_exc()}")

        try:
            self._test_class.cleanup()
        except Exception as e:
            self.on_failed(result, reason=str(e))
            self._test_class.logger.error(f"Cleanup Traceback:\n{traceback.format_exc()}")

        self.on_pass(result)
        return result

    def on_pass(self, result: TestResult):
        """
        Executed on PASS status
        :param result: result of the test
        """
        self._notify_listeners(result)

    def on_failed(self, result: TestResult, reason=""):
        """
        Executed on FAIL status
        :param result: result of the test
        :param reason: reason of failure
        """
        result.verdict = TestVerdict.FAILED
        result.failure_reasons.append(reason)
        self._notify_listeners(result)

    def on_aborted(self, result: TestResult, reason: str = ""):
        """
        Executed on ABORTED status
        :param result: result of the test
        :param reason: reason of aborting
        """
        result.verdict = TestVerdict.ABORTED
        result.failure_reasons.append(reason)
        self._notify_listeners(result)

    def register_listener(self, listener):
        """
        Register a listener to the runnable

        :param listener: a listener to register
        """
        if not hasattr(listener, "notify"):
            err = f"The listener {listener} is not supported since it doesn't have a 'notify' method"
            self._test_class.logger.error(err)
            raise ListenerNotSupported(err)

        self._result_listeners.append(listener)

    def _notify_listeners(self, result):
        for listener in self._result_listeners:
            listener.notify(result)
