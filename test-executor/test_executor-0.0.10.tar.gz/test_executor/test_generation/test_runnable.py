import os
from typing import Callable

from test_executor.abstract_test.abstract_test import AbstractTest
from test_executor.abstract_test.test_result import TestResult, TestVerdict
from test_executor.common import DEFAULT_LOGS_FOLDER
from test_executor.logger_factory.logger_factory import LoggerFactory
import traceback


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
        result = TestResult(test_number=self._test_number)
        result.test_log = os.path.join(logs_folder, f"{self._test_number}_"
                                                    f"{self.__class__.__name__}.{self._test_function.__name__}",
                                       "test_log.log")

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
            self._test_function()
        except Exception as e:
            self.on_failed(result, reason=str(e))
            self._test_class.logger.error(f"Test Traceback:\n{traceback.format_exc()}")

        try:
            self._test_class.cleanup()
        except Exception as e:
            self.on_failed(result, reason=str(e))
            self._test_class.logger.error(f"Cleanup Traceback:\n{traceback.format_exc()}")

        return result

    def on_pass(self, result: TestResult):
        self._notify_listeners(result)

    def on_failed(self, result: TestResult, reason=""):
        result.verdict = TestVerdict.FAILED
        result.failure_reasons.append(reason)
        self._notify_listeners(result)

    def on_aborted(self, result: TestResult, reason=""):
        result.verdict = TestVerdict.ABORTED
        result.failure_reasons.append(reason)
        self._notify_listeners(result)

    def _notify_listeners(self, result):
        for listener in self._result_listeners:
            listener.notify(result)
