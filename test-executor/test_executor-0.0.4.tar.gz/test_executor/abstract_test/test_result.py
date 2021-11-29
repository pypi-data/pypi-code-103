from enum import Enum

from typing import List


class TestVerdict(Enum):
    PASSED = "Passed"
    FAILED = "Failed"
    ABORTED = "Aborted"


class TestResult(object):
    verdict: TestVerdict
    failure_reasons: List[str]

    def __init__(self):
        self.verdict = TestVerdict.PASSED
        self.failure_reasons = []
        self.test_log = ""
