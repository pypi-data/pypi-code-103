#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from .app_product import product
import logging


class AppLogger:
    """
    日志级别仅保留
    - DEBUG
    - ERROR
    """

    def __init__(self):
        # LOG FILE
        logging.basicConfig(level=logging.ERROR)
        self.log = logging.getLogger("ROI")
        # LOG LEVEL
        self.log.setLevel(logging.ERROR)
        # IS DEBUG
        if product.is_debug:
            self.log.setLevel(logging.DEBUG)

    def debug(self, data):
        try:
            self.log.debug("++LOGGERDEBUG++++++++++++++++++++++++++++++++++")
            self.log.debug("")
            self.log.debug(data)
            self.log.debug("")
            self.log.debug("++LOGGERDEBUG++++++++++++++++++++++++++++++++++\n")
        except Exception as e:
            self.log.error(e)

    def error(self, data):
        try:
            self.log.error("++LOGGERERROR++++++++++++++++++++++++++++++++++")
            self.log.error("")
            self.log.error(data)
            self.log.error("")
            self.log.error("++LOGGERERROR++++++++++++++++++++++++++++++++++\n")
        except Exception as e:
            self.log.error(e)


# EXPORT LOGGER
logger = AppLogger()
