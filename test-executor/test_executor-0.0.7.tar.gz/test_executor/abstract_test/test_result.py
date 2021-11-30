from enum import Enum

from typing import List


class TestVerdict(Enum):
    """
    Enum for test verdicts
    """
    PASSED = "Passed"
    FAILED = "Failed"
    ABORTED = "Aborted"


class TestResult(object):
    """
    This class is a class data that contains data about a test
    """
    verdict: TestVerdict
    failure_reasons: List[str]

    def __init__(self, test_number: int):
        self.verdict = TestVerdict.PASSED
        self.failure_reasons = []
        self.test_log = ""
        self.test_number = test_number
