# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2015-2020 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

"""
"""

__authors__ = [
    "H. Payno",
]
__license__ = "MIT"
__date__ = "23/02/2021"


import logging
import argparse
from nxtomomill.io import generate_default_h5_config
from nxtomomill.io import TomoHDF5Config

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def main(argv):
    """ """
    parser = argparse.ArgumentParser(description="Create a default configuration file")
    parser.add_argument("output_file", help="output .cfg file")
    parser.add_argument(
        "--from-title-names",
        help="Provide minimalistic configuration to make a conversion from "
        "titles names. (FRAME TYPE section is ignored). \n"
        "Exclusive with `from-scan-urls` option",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--from-scan-urls",
        help="Provide minimalistic configuration to make a conversion from "
        "scan urls. (ENTRIES and TITLES section is ignored).\n"
        "Exclusive with `from-title-names` option",
        action="store_true",
        default=False,
    )

    options = parser.parse_args(argv[1:])
    configuration = generate_default_h5_config()
    if options.from_title_names:
        if options.from_scan_urls:
            raise ValueError(
                "`from-title-names` and `from-scan-urls` are " "exclusive options"
            )
        del configuration[TomoHDF5Config.FRAME_TYPE_SECTION_DK]
    elif options.from_scan_urls:
        del configuration[TomoHDF5Config.ENTRIES_AND_TITLES_SECTION_DK]
    TomoHDF5Config.dict_to_cfg(file_path=options.output_file, dict_=configuration)
