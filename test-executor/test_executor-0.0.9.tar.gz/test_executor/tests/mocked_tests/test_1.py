import time

from abstract_test.abstract_test import AbstractTest


class MockTest1(AbstractTest):
    def setup(self):
        self.logger.info(f"Setup 1")

    def cleanup(self):
        self.logger.info(f"Cleanup 1")

    def test_1(self):
        self.logger.info(f"Test 1")
        time.sleep(3)

    def test_2(self):
        self.logger.info(f"Test 1")
        time.sleep(3)
