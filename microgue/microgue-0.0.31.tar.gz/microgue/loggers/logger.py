import logging


class Logger:
    def __init__(self, name=None, level=logging.DEBUG):
        logging.basicConfig(level=level)
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(level)

    def debug(self, message, priority=None):
        self.log(message, priority=priority, level=logging.DEBUG)

    def info(self, message, priority=None):
        self.log(message, priority=priority, level=logging.INFO)

    def error(self, message, priority=None):
        self.log(message, priority=priority, level=logging.ERROR)

    def warning(self, message, priority=None):
        self.log(message, priority=priority, level=logging.WARNING)

    def critical(self, message, priority=None):
        self.log(message, priority=priority, level=logging.CRITICAL)

    def log(self, message, priority=None, level=logging.DEBUG):
        if priority == 1:
            self.__logger.log(level, '########## {} ########################################'.format(message))
        elif priority == 2:
            self.__logger.log(level, '########## {} ##########'.format(message))
        elif priority == 3:
            self.__logger.log(level, '########## {}'.format(message))
        else:
            self.__logger.log(level, message)
