# SPDX-License-Identifier: Apache-2.0

import logging
import os

if 'PYCHARM_HOSTED' in os.environ:
    # must before import logzero
    os.environ['LOGZERO_FORCE_COLOR'] = '1'

import logzero  # pylint: disable=wrong-import-order,wrong-import-position

# difference with logzero.DEFAULT_FORMAT: %(message)s%(end_color)s
# difference with logzero.DEFAULT_COLORS:
# - logging.DEBUG: ForegroundColors.CYAN,
# - logging.INFO: ForegroundColors.GREEN,
_ = logzero.DEFAULT_FORMAT
_ = logzero.DEFAULT_COLORS
logzero.formatter(logzero.LogFormatter(
    fmt=('%(color)s[%(levelname)1.1s %(asctime)s '
         '%(filename)s:%(lineno)d %(funcName)s()] %(message)s%(end_color)s'),
    colors={
        logging.DEBUG: logzero.ForegroundColors.WHITE,
        logging.INFO: logzero.ForegroundColors.BLUE,
        logging.WARNING: logzero.ForegroundColors.YELLOW,
        logging.ERROR: logzero.ForegroundColors.RED,
        logging.CRITICAL: logzero.ForegroundColors.RED
    }
))

logger: logging.Logger = logzero.logger  # pylint: disable=invalid-name
