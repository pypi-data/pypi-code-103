# Copyright 2021 Vincent Texier
#
# This file is part of MADAM.
#
# MADAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MADAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MADAM.  If not, see <https://www.gnu.org/licenses/>.

"""
Madam main module
"""
import logging
import os
import sys
from pathlib import Path

from madam.domains.application import MainApplication
from madam.domains.entities import constants
from madam.slots.graphql import server

# get madam config filepath from env var or constants default
MADAM_CONFIG_PATH = os.getenv("MADAM_CONFIG_PATH", constants.MADAM_CONFIG_PATH)
# get python log level from env var or constants default
MADAM_LOG_LEVEL = os.getenv("MADAM_LOG_LEVEL", constants.MADAM_LOG_LEVEL).upper()

# set root logger level
logging.basicConfig(level=MADAM_LOG_LEVEL)


def main():
    """
    Create and run Madam main application instance

    :return:
    """
    if Path(MADAM_CONFIG_PATH).exists():
        # load configuration
        try:
            # create madam main application
            application = MainApplication(MADAM_CONFIG_PATH)
        except IOError as exception:
            logging.error(
                "error opening yaml config %s: %s", MADAM_CONFIG_PATH, exception
            )
            sys.exit(1)
        # Run GraphQL server
        server.run(application, MADAM_LOG_LEVEL)
    else:
        logging.error("Madam config file %s not found", MADAM_CONFIG_PATH)
        sys.exit(1)


if __name__ == "__main__":
    main()
