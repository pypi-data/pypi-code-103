import logging
import os
import time
from multiprocessing import Process, Event
from signal import SIGINT, SIGKILL
from typing import Callable, Union, Type
from unittest import TestCase

import multiprocessing_logging

from openmodule.core import shutdown_openmodule
from openmodule.utils.schema import Schema
from openmodule_test.health import HealthTestMixin


class ExceptionProcess(Process):
    def __init__(self, *args, **kwargs):
        is_finished = Event()
        super().__init__(*args, **kwargs)
        self.is_finished = is_finished

    def run(self):
        try:
            super().run()
            self.is_finished.set()
        except Exception as e:
            logging.exception(e)


class InterruptTestMixin(TestCase):
    """
    Helper class for testing interrupts and exceptions in code
    for usage, look at file tests/test_interrupt
    """

    def tearDown(self):
        super().tearDown()
        Schema.to_file()

    def wait_for_setup(self):
        pass

    def _wait_for_and_uninstall_mp_handler(self, logger=None):
        """
        waits until the multiprocessing logging handler has finished
        """
        if logger is None:
            logger = logging.getLogger()

        for handler in logger.handlers:
            if isinstance(handler, multiprocessing_logging.MultiProcessingHandler):
                handler.close()

        multiprocessing_logging.uninstall_mp_handler(logger)

    def signal_in_function(self, f: Callable, signal: Union[Type[KeyboardInterrupt], int], *,
                           raise_exception_after: float = 3.0, shutdown_timeout: float = 3.0):
        if signal == KeyboardInterrupt:
            signal = SIGINT
        multiprocessing_logging.install_mp_handler()
        process = ExceptionProcess(target=f)
        process.start()
        self.wait_for_setup()
        time.sleep(raise_exception_after)
        self.assertFalse(process.is_finished.is_set())
        os.kill(process.pid, signal)
        if process.is_finished.wait(timeout=shutdown_timeout):
            self._wait_for_and_uninstall_mp_handler()
            return
        else:
            if process.is_alive():
                os.kill(process.pid, SIGKILL)
                raise TimeoutError("Process took to long for shutdown")
            else:
                raise AssertionError("Process did not finish gracefully")


class MainTestMixin(HealthTestMixin, InterruptTestMixin):
    topics = ["healthz"]
    protocol = "tcp://"

    def wait_for_setup(self):
        self.wait_for_health()

    def tearDown(self):
        try:
            shutdown_openmodule()
        except AssertionError:
            pass
        super().tearDown()
