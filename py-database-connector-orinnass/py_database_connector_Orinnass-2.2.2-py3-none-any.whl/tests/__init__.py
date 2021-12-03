from unittest import TestSuite, TextTestRunner, makeSuite
from tests.main import TestVersion

if __name__ == '__main__':
    tests_suite = TestSuite()
    tests_suite.addTest(makeSuite(TestVersion))

    runner_tests = TextTestRunner()
    runner_tests.run(tests_suite)
