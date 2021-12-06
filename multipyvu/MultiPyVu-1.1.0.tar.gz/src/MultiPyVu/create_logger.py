# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 09:36:10 2021

create_logger.py creates a custom logging event

@author: djackson
"""

import logging
import logging.handlers

from .project_vars import LOG_NAME


class log():
    def __init(self):
        self.logger = None
        self.handler = None
        self.verbose_handler = None

    def create(self,
               name: str,
               display_logger_name=True,
               log_file=LOG_NAME,
               ) -> logging.Logger:
        '''
        This creates a logging event that will make the text sent to the
        command line interface to have a similar appearance when using
        MultiVuServer.py and MultiVuClient.py by having each line
        start with the 'name' if display_logger_name is True.

        This also creates the logger to be used with the 'verbose' flag
        using a DEBUG level that saves to a file.

        Parameters
        ----------
        name : str
            Name to display at the start of each logging.info() event.
        display_logger_name : bool, optional
            When True, this will display the name, otherwise it will
            just display the message. This is helpful for when running
            the server in a single thread (no need to display the name)
            compared to running it with multi-threading, where the
            MultiVuServer and MultiVuClient might be running in the same
            program. The default is True.
        log_file : str, optional
            The filename used for logging when the 'verbose' flag is set.
            The default is 'MultiVuSocket.log'

        Returns
        -------
        logger : logging.Logger
            This is the logger after being properly configured.

        '''
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Configure the error handler for info messges to the std.out
        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.INFO)

        if display_logger_name:
            log_format = logging.Formatter('%(name)s - %(message)s')
        else:
            log_format = logging.Formatter('%(message)s')
        self.handler.setFormatter(log_format)

        self.logger.addHandler(self.handler)

        # Configure the error handler for debug messages (including
        # messages used with the 'verbose' flag) to a log file
        self.verbose_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=2**22,
            backupCount=2)
        self.verbose_handler.setLevel(logging.DEBUG)
        f = '%(asctime)-27s %(name)-20s %(levelname)-8s %(message)s'
        verbose_format = logging.Formatter(f)
        self.verbose_handler.setFormatter(verbose_format)

        self.logger.addHandler(self.verbose_handler)

        return self.logger

    def remove(self):
        if self.handler is not None:
            self.logger.removeHandler(self.handler)
            del self.handler
            self.handler = None

        if self.verbose_handler is not None:
            self.logger.removeHandler(self.verbose_handler)
            self.verbose_handler.close()
            del self.verbose_handler
            self.verbose_handler = None
