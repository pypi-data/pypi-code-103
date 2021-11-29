import os
import threading
from typing import List

from test_executor.common import DEFAULT_LOGS_FOLDER
from test_executor.logger_factory.logger_factory import LoggerFactory
from test_executor.test_generation.test_runnable import TestRunnable


class TestExecutor(object):
    """
    Class that executes a list of runnables
    """
    __test__ = False

    def __init__(self, logs_folder: str = DEFAULT_LOGS_FOLDER, concurrency_level: int = 1):
        """
        :param logs_folder: path to logs folder
        :param concurrency_level: concurrency level for executing the tests
        """
        self._logs_folder = logs_folder
        self._concurrency_level = concurrency_level
        self._results = []
        self._logger = LoggerFactory.generate_logger(os.path.join(self._logs_folder, "session.log"))

    def execute(self, test_runnables: List[TestRunnable]):
        """
        Executes that list of given test runnables.
        If concurrency is not 1, we will execute the tests in batches by their order.

        :param test_runnables: list of runnables
        """
        test_batches = self._get_test_batches(test_runnables)

        for batch in test_batches:
            batch_threads = []
            for test_runnable in batch:
                test_t = threading.Thread(target=self._run_single_runnable, args=(test_runnable,))
                test_t.start()
                batch_threads.append([test_t, test_runnable])

            while batch_threads:
                for i, batch_part in enumerate(batch_threads):
                    test_t, test_runnable = batch_part
                    test_t.join(timeout=1)
                    if not test_t.is_alive():
                        self._logger.info(f"The test '{test_runnable}' finished its execution")
                        del batch_threads[i]
                    else:
                        self._logger.info(f"The test '{test_runnable}' is still running")

    def _run_single_runnable(self, test_runnable: TestRunnable):
        result = test_runnable.run(logs_folder=self._logs_folder)
        self._results.append(result)

    def _get_test_batches(self, test_runnables):
        test_batches = []
        for i in range(0, len(test_runnables), self._concurrency_level):
            test_batches.append(test_runnables[i:i + self._concurrency_level])
        return test_batches
