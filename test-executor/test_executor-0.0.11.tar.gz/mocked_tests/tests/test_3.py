from test_executor.abstract_test.abstract_test import AbstractTest


class MockTest3(AbstractTest):
    def setup(self):
        self.logger.info(f"Setup 3")

    def cleanup(self):
        self.logger.info(f"Cleanup 3")

    def test_13(self):
        self.logger.info(f"Test 1")

    def test_23(self):
        self.logger.info(f"Test 2")
