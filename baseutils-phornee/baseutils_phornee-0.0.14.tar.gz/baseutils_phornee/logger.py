import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time


class UTCFormatter(logging.Formatter):
    converter = time.gmtime


class Logger:

    def __init__(self, log_config):
        self.config = log_config

        self.homevar = "{}/var/{}".format(str(Path.home()), self.config['modulename'])

        if not os.path.exists(self.homevar):
            os.makedirs(self.homevar)

        self.setupLogger()

    def getLogPath(self):
        return os.path.join(self.homevar, self.config['logpath'], "{}.log".format(self.config['modulename']))

    def setupLogger(self):
        self.logger = logging.getLogger('{}_log'.format(self.config['modulename']))
        log_folder = os.path.join(self.homevar, self.config['logpath'])

        if not os.path.exists(log_folder):
            os.mkdir(log_folder)

        self.logger.setLevel(logging.INFO)
        fh = RotatingFileHandler(self.getLogPath(), maxBytes=10000, backupCount=10)

        # Uncomment for UTC logging
        #formatter = UTCFormatter('%(asctime)s-%(message)s', '%Y-%m-%d %H:%M:%S')

        formatter = logging.Formatter('%(asctime)s-%(message)s', '%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def getLog(self):
        with open(self.getLogPath(), 'r') as file:
            return file.read()

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

