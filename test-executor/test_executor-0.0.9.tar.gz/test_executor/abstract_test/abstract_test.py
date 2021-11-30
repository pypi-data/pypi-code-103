import logging
from abc import ABC, abstractmethod
from inspect import getmembers, ismethod

from typing import List

from abstract_test.test_result import TestResult
from common import DEFAULT_LOGS_FOLDER


class AbstractTest(ABC):
    """
    Abstract class for tests flow
    """

    test_result: TestResult
    abstract_test_methods: List[str]
    logger: logging.Logger

    _test_counter = 0
    abstract_test_methods = None

    def __init__(self):
        self.logger = None
        self._logs_folder = DEFAULT_LOGS_FOLDER
        self.test_results = []
        if AbstractTest.abstract_test_methods is None:
            AbstractTest.abstract_test_methods = [function_name
                                                  for function_name, _ in getmembers(AbstractTest, ismethod)]

    @abstractmethod
    def setup(self):
        """
        Implement any logic for setting up a test's execution
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Implement any logic for cleanup after a test's execution
        """
        pass

    def pre_test(self):
        """
        Specific pre_test logic that is not mandatory
        """
        pass

    def post_test(self):
        """
        Specific post_test logic that is not mandatory
        """
        pass
