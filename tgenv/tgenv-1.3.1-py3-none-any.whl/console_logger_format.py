"""    This file is part of tgenv.

    tgenv is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    tgenv is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with tgenv.  If not, see <https://www.gnu.org/licenses/>."""

import logging
from logging import Formatter

class ConsoleLoggingFormat(Formatter):
    """ A logging format for stdout
    """

    STANDARD_FORMAT = "%(message)s"
    ERROR_FORMAT = "\033[0;31m%(message)s\033[0m"
    WARNING_FORMAT = "\033[1;33m%(message)s\033[0m"

    def __init__(self):
        Formatter.__init__(self, fmt="\t%(msg)s", style='%')

    # pylint: disable=protected-access
    def format(self, record):
        """ Overrides the default format
        """
        org_fmt = self._style._fmt

        if record.levelno == logging.DEBUG:
            self._style._fmt = ConsoleLoggingFormat.STANDARD_FORMAT

        elif record.levelno == logging.INFO:
            self._style._fmt = ConsoleLoggingFormat.STANDARD_FORMAT

        elif record.levelno == logging.ERROR:
            self._style._fmt = ConsoleLoggingFormat.ERROR_FORMAT

        elif record.levelno == logging.WARNING:
            self._style._fmt = ConsoleLoggingFormat.WARNING_FORMAT

        self._style._fmt = org_fmt

        return logging.Formatter.format(self, record)
    # pylint: enable=protected-access
