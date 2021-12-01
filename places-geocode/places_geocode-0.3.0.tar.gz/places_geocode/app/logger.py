import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import pydantic


class LoggingSchema(pydantic.BaseModel):
    """dataclass for Logger Schema containing main functions"""
    level: Union[str, None]
    message: Union[str, None]
    formatter: Any
    handler: Any
    logger: Any


class LoggingData:

    """logging data main function"""

    def __init__(self, name, file, level, message):
        self.level = level
        self.message = message
        self.formatter = self._create_formatting()
        self.handler = self._create_handler(self.formatter, file)
        self.logger = logging.getLogger(name)

        # check if logger has handlers, avoids exceptions
        if not self.logger.hasHandlers():
            self.logger.addHandler(self.handler)

        # create the LoggingSchema model and convert to dictionary type
        self.model = LoggingSchema(level=self.level,
                                   message=self.message,
                                   formatter=self.formatter,
                                   handler=self.handler,
                                   logger=self.logger).dict()

    @staticmethod
    def _create_formatting():
        """create the logger formatter object"""
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        return formatter

    @staticmethod
    def _create_handler(formatter, file):
        """create the handler object for the logger process"""
        handler = logging.FileHandler(file)
        handler.setFormatter(formatter)
        return handler


class LoggingStrategy(ABC):
    """abstract base class for the general logging strategy"""

    @abstractmethod
    def create_strategy(self, logging_data: Dict) -> None:
        """create strategy for abstract method"""
        pass


class GeneralStrategy(LoggingStrategy):
    """general strategy for adding generic logging statements"""

    def create_strategy(self, logging_data: Dict) -> None:
        """create strategy for general logging"""
        logging_data['logger'].setLevel(logging_data['level'])
        logging_data['logger'].info(logging_data['message'])


class LogError:

    """log the error encountered during API Runtime"""

    def __init__(self, logging_strategy: LoggingStrategy):
        self.logging_strategy = logging_strategy

    def do_logging(self, name, file, level, message):
        """perform logging by implementing LoggingSchema dataclass and abstract base class"""
        logging_obj = LoggingData(name, file, level, message)
        model = logging_obj.model

        # perform logging
        try:
            self.logging_strategy.create_strategy(model)
        except BaseException:
            raise Exception('Error in Logging Module Occurred')


def log_error(name, file, level, message):
    """log error client function"""
    logger = LogError(GeneralStrategy())
    logger.do_logging(name, file, level, message)

# log_error('AddUserLogger', '/Users/martinmashalov/Documents/Python/PeekGeo/Logs/LoadPropertiesLogs.txt', "DEBUG", 'test message here')
