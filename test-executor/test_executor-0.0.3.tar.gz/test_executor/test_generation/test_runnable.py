import os
from typing import Callable

from test_executor.abstract_test.abstract_test import AbstractTest
from test_executor.abstract_test.test_result import TestResult
from test_executor.common import DEFAULT_LOGS_FOLDER
from test_executor.logger_factory.logger_factory import LoggerFactory
import traceback


class TestRunnable(object):
    """
    Represents a runnable test
    """
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

    def __repr__(self):
        return f"{self._test_class.__class__.__name__}.{self._test_function.__name__}"

    def run(self, logs_folder: str = DEFAULT_LOGS_FOLDER) -> TestResult:
        """
        Executes a test function with Setup & Cleanup flows.
        In case that Setup fails, Cleanup will be executed

        :param logs_folder: path to set logs to
        :return: the test's result
        """
        result = TestResult()
        result.test_log = os.path.join(logs_folder, f"{self._test_number}_"
                                                    f"{self.__class__.__name__}.{self._test_function.__name__}",
                                       "test_log.log")

        self._test_class.logger = LoggerFactory.generate_logger(result.test_log)

        try:
            self._test_class.setup()
        except Exception as e:
            AbstractTest.on_failed(result, reason=str(e))
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
            AbstractTest.on_failed(result, reason=str(e))
            self._test_class.logger.error(f"Test Traceback:\n{traceback.format_exc()}")

        try:
            self._test_class.cleanup()
        except Exception as e:
            AbstractTest.on_failed(result, reason=str(e))
            self._test_class.logger.error(f"Cleanup Traceback:\n{traceback.format_exc()}")

        return result
