# SPDX-License-Identifier: Apache-2.0

import wataash_utils._exp
import wataash_utils.argparse
import wataash_utils.click
import wataash_utils.json
import wataash_utils.logging
import wataash_utils.python
import wataash_utils.pycharm
import wataash_utils.str

try:
    import wataash_utils.requests
except ImportError:  # requests
    pass
try:
    import wataash_utils.selenium
except ImportError:  # selenium
    pass

# -----------------------------------------------------------------------------
# misc

from wataash_utils.logging import logger


def warn_cr(file: str, txt: str) -> None:
    pos_cr = txt.find('\r')
    if pos_cr != -1:
        msg = (f'file {file}: '
               f'carriage-return (CR; 0x0d) character found at byte:{pos_cr} '
               f'(made on Windows?); '
               f'only line-feed (LF; 0x0a) is supported as the new-line '
               f'character')
        logger.warning(msg)


del logger
