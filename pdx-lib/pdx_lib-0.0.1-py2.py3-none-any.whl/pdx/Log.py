from pdx import Config
import time
import os
import logging


class Log:
    logLevel = None
    logFileDirectory = None
    logFileName = None
    logFilePath = None

    def get_unique_log_name(self, script_name):
        """Make a unique name for the log file"""
        datetime = time.strftime("%Y%m%d%H%M%S")
        self.logFileName = "{0}_{1}_{2}.log".format(script_name, Config.username, datetime)
        del datetime

    def get_log_directory(self):
        """Get the log directory path, and make sure it exists"""
        self.logFileDirectory = os.path.join(Config.pdx_home, 'logs')
        if not os.path.isdir(self.logFileDirectory):
            os.makedirs(self.logFileDirectory)

    # Initialize a Log object
    def __init__(self, script_name, level='info', version=None):
        # Determine log path
        self.get_unique_log_name(script_name)
        self.get_log_directory()
        self.logFilePath = os.path.join(self.logFileDirectory, self.logFileName)

        # Determine log level
        if level == 'info':
            self.logLevel = logging.INFO
        elif level == 'debug':
            self.logLevel = logging.DEBUG
        elif level == 'warn' or level == 'warning':
            self.logLevel = logging.WARNING
        elif level == 'error':
            self.logLevel = logging.ERROR
        else:
            self.logLevel = logging.INFO

        # Start logging
        logging.basicConfig(filename=self.logFilePath, format='%(levelname)s:%(message)s', level=self.logLevel)

        # If version was given, log the version being used
        if version is not None:
            logging.info("Using pdx-lib (v. {0})".format(version))

        if level == 'debug':
            logging.debug("Running in debug mode")
