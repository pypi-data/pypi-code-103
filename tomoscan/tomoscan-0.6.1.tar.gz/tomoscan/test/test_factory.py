# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "24/01/2017"


import unittest
import os
from tomoscan.esrf.edfscan import EDFTomoScan
from tomoscan.esrf.hdf5scan import HDF5TomoScan
from tomoscan.scanfactory import ScanFactory
from tomoscan.test.utils import UtilsTest
import tempfile


class TestScanFactory(unittest.TestCase):
    """Make sure the Scan factory is correctly working. Able to detect the
    valid scan type for a given file / directory
    """

    def test_no_scan(self):
        """Make sure an error is raised if we try yo create a scan from an
        empty dir"""
        scan_dir = tempfile.mkdtemp()
        with self.assertRaises(ValueError):
            ScanFactory.create_scan_object(scan_dir)

    def test_scan_edf(self):
        """can we create a TomoScanBase object from a folder containing a
        valid .edf acquisition"""
        scan_dir = UtilsTest.getDataset("test10")
        scan = ScanFactory.create_scan_object(scan_dir)
        self.assertTrue(isinstance(scan, EDFTomoScan))

    def test_one_nx(self):
        """Can we create a TomoScanBase from a .nx master file containing
        one acquisition"""
        file_name = "frm_edftomomill_oneentry.nx"
        master_file = UtilsTest.getH5Dataset(file_name)
        scan = ScanFactory.create_scan_object(master_file)
        self.assertTrue(isinstance(scan, HDF5TomoScan))
        self.assertEqual(scan.path, os.path.dirname(master_file))
        self.assertEqual(scan.master_file, master_file)
        self.assertEqual(scan.entry, "entry")

    def test_one_two_nx(self):
        """Can we create a TomoScanBase from a .nx master file containing
        two acquisitions"""
        master_file = UtilsTest.getH5Dataset("frm_edftomomill_twoentries.nx")
        scan = ScanFactory.create_scan_object(master_file)
        self.assertTrue(isinstance(scan, HDF5TomoScan))
        self.assertEqual(scan.path, os.path.dirname(master_file))
        self.assertEqual(scan.master_file, master_file)
        self.assertEqual(scan.entry, "entry0000")

    def test_two_nx(self):
        """Can we create two TomoScanBase from a .nx master file containing
        two acquisitions using the ScanFactory"""
        master_file = UtilsTest.getH5Dataset("frm_edftomomill_twoentries.nx")
        scans = ScanFactory.create_scan_objects(master_file)
        self.assertEqual(len(scans), 2)
        for scan, scan_entry in zip(scans, ("entry0000", "entry0001")):
            self.assertTrue(isinstance(scan, HDF5TomoScan))
            self.assertEqual(scan.path, os.path.dirname(master_file))
            self.assertEqual(scan.master_file, master_file)
            self.assertEqual(scan.entry, scan_entry)
