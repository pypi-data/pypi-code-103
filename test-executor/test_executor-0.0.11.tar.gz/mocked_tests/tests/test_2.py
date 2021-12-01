from test_executor.abstract_test.abstract_test import AbstractTest


class MockTest2(AbstractTest):
    def setup(self):
        self.logger.info(f"Setup 2")

    def cleanup(self):
        self.logger.info(f"Cleanup 2")

    def test_12(self):
        self.logger.info(f"Test 1")

    def test_22(self):
        self.logger.info(f"Test 2")
