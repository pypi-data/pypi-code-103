# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016-2020 European Synchrotron Radiation Facility
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
#############################################################################*/
"""Contains the ScanFactory class and dedicated functions"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "27/02/2019"


from .scanbase import TomoScanBase
from .esrf.edfscan import EDFTomoScan
from .esrf.hdf5scan import HDF5TomoScan
import json
import os


class ScanFactory:
    """
    Factory for TomoScanBase instances
    """

    @staticmethod
    def create_scan_object(scan_path: str) -> TomoScanBase:
        """

        :param str scan_path: path to the scan directory or file
        :return: ScanBase instance fitting the scan folder or scan path
        :rtype: TomoScanBase
        """
        # remove any final separator (otherwise basename might fail)
        scan_path = scan_path.rstrip(os.path.sep)
        if EDFTomoScan.is_tomoscan_dir(scan_path):
            return EDFTomoScan(scan=scan_path)
        elif HDF5TomoScan.is_tomoscan_dir(scan_path):
            return HDF5TomoScan(scan=scan_path)
        else:
            raise ValueError("%s is not a valid scan path" % scan_path)

    @staticmethod
    def create_scan_objects(scan_path: str) -> tuple:
        """

        :param str scan_path: path to the scan directory or file
        :return: all possible instances of TomoScanBase contained in the given
                 path
        :rtype: tuple
        """
        scan_path = scan_path.rstrip(os.path.sep)
        if EDFTomoScan.is_tomoscan_dir(scan_path):
            return (EDFTomoScan(scan=scan_path),)
        elif HDF5TomoScan.is_tomoscan_dir(scan_path):
            scans = []
            master_file = HDF5TomoScan.get_master_file(scan_path=scan_path)
            entries = HDF5TomoScan.get_valid_entries(master_file)
            for entry in entries:
                scans.append(HDF5TomoScan(scan=scan_path, entry=entry, index=None))
            return tuple(scans)

        raise ValueError("%s is not a valid scan path" % scan_path)

    @staticmethod
    def create_scan_object_frm_dict(_dict: dict) -> TomoScanBase:
        """
        Create a TomoScanBase instance from a dictionary. It should contains
        the TomoScanBase._DICT_TYPE_KEY key at least.

        :param _dict: dictionary to be converted
        :return: instance of TomoScanBase
        :rtype: TomoScanBase
        """
        if TomoScanBase.DICT_TYPE_KEY not in _dict:
            raise ValueError(
                "given dict is not recognized. Cannot find" "",
                TomoScanBase.DICT_TYPE_KEY,
            )
        elif _dict[TomoScanBase.DICT_TYPE_KEY] == EDFTomoScan._TYPE:
            return EDFTomoScan(scan=None).load_from_dict(_dict)
        else:
            raise ValueError(
                "Scan type", _dict[TomoScanBase.DICT_TYPE_KEY], "is not managed"
            )

    @staticmethod
    def is_tomoscan_dir(scan_path: str) -> bool:
        """

        :param str scan_path: path to the scan directory or file
        :return: True if the given path is a root folder of an acquisition.
        :rtype: bool
        """
        return HDF5TomoScan.is_tomoscan_dir(scan_path) or EDFTomoScan.is_tomoscan_dir(
            scan_path
        )

    @staticmethod
    def create_from_json(desc: dict) -> TomoScanBase:
        """Create a ScanBase instance from a json description"""
        data = json.load(desc)

        if TomoScanBase.DICT_TYPE_KEY not in data:
            raise ValueError("json not recognize")
        elif data[TomoScanBase.DICT_TYPE_KEY] == EDFTomoScan._TYPE:
            scan = EDFTomoScan(scan=None).load_from_dict(data)
            return scan
        else:
            raise ValueError("Type", data[TomoScanBase.type], "is not managed")
