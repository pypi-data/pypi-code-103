import time

from abstract_test.abstract_test import AbstractTest


class MockTest3(AbstractTest):
    def setup(self):
        self.logger.info(f"Setup 3")

    def cleanup(self):
        self.logger.info(f"Cleanup 3")

    def test_1(self):
        self.logger.info(f"Test 3")
        time.sleep(1)

    def test_2(self):
        self.logger.info(f"Test 3")
        time.sleep(1)
