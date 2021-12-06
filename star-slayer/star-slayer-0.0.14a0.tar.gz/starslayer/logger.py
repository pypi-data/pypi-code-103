"""
Logger Module. It cointains the GameLogger class,
from which is created the objects that logs events
of the program.
"""

import logging
from .consts import LOG_PATH


class GameLogger():
    """
    Class that registers game events.
    """

    def __init__(self,
                 *,
                 log_name: str="TheStarThatSlays",
                 log_level: int=logging.INFO,
                 format: str="[ %(asctime)s ] - %(levelname)s - %(message)s",
                 date_fmt: str="%d-%m-%Y %I:%M:%S %p") -> None:
        """
        Creates an instance of 'GameLogger'.
        """

        super().__init__()

        self._format = format
        self._date_fmt = date_fmt

        self._formatter = logging.Formatter(fmt=self._format, date_fmt=self._date_fmt)

        self.file_handler = logging.FileHandler(filename=LOG_PATH, encoding="utf-8")
        self.console_handler = logging.StreamHandler()
        self.update_formatter()

        self.logger = logging.Logger(name=log_name)
        self.logger.setLevel(log_level)
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)


    def update_formatter(self) -> None:
        """
        Sets the formatter for every handler that the logger has.
        """

        self.file_handler.setFormatter(self._formatter)
        self.console_handler.setFormatter(self._formatter)


    @property
    def formatter(self) -> logging.Formatter:

        return self._formatter

    @formatter.setter
    def formatter(self, new_formatter: logging.Formatter) -> None:
        """
        Updates automatically the formatter for every handler.
        """

        self._formatter = new_formatter
        self.update_formatter()


    @property
    def format(self) -> str:

        return self._format


    @format.setter
    def format(self, new_format) -> None:

        self._format = new_format
        self.formatter = logging.Formatter(format=self.format, datefmt=self.date_fmt)


    @property
    def date_fmt(self) -> str:

        return self._date_fmt

    
    @date_fmt.setter
    def date_fmt(self, new_date_fmt: str) -> None:

        self._date_fmt = new_date_fmt
        self.formatter = logging.Formatter(format=self.format, datefmt=self.date_fmt)


    def debug(self, message: str) -> None:
        """
        Registers an event of level DEBUG.
        """

        self.logger.debug(message)


    def info(self, message: str) -> None:
        """
        Registers an event of level INFO.
        """

        self.logger.info(message)


    def warning(self, message: str) -> None:
        """
        Registers an event of level WARNING.
        """

        self.logger.warning(message)


    def error(self, message: str) -> None:
        """
        Registers an event of level ERROR.
        """

        self.logger.error(message)

    def critical(self, message: str) -> None:
        """
        Registers an event of level CRITICAL.
        """

        self.logger.critical(message)