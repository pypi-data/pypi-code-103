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
__date__ = "08/09/2020"


import unittest
import numpy.random
from tomoscan.scanbase import TomoScanBase
import shutil
import tempfile
from silx.io.url import DataUrl
import h5py
import os


class TestFlatFieldCorrection(unittest.TestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.scan = TomoScanBase(None, None)
        self.scan.set_normed_darks(
            {
                0: numpy.random.random(100).reshape((10, 10)),
            }
        )

        self.scan.set_normed_flats(
            {
                1: numpy.random.random(100).reshape((10, 10)),
                12: numpy.random.random(100).reshape((10, 10)),
                21: numpy.random.random(100).reshape((10, 10)),
            }
        )

        self._data_urls = {}
        projections = {}
        file_path = os.path.join(self.data_dir, "data_file.h5")

        for i in range(-2, 30):
            projections[i] = numpy.random.random(100).reshape((10, 10))
            data_path = "/".join(("data", str(i)))
            self._data_urls[i] = DataUrl(
                file_path=file_path, data_path=data_path, scheme="silx"
            )
            with h5py.File(file_path, mode="a") as h5s:
                h5s[data_path] = projections[i]

        self.scan.projections = projections

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def test_get_flats_weights(self):
        """test the _get_flats_weights function and insure flat weights
        are correct"""
        flat_weights = self.scan._get_flats_weights()
        self.assertTrue(isinstance(flat_weights, dict))
        self.assertEqual(len(flat_weights), 32)
        self.assertEqual(flat_weights.keys(), self.scan.projections.keys())
        self.assertEqual(flat_weights[-2], {1: 1.0})
        self.assertEqual(flat_weights[0], {1: 1.0})
        self.assertEqual(flat_weights[1], {1: 1.0})
        self.assertEqual(flat_weights[12], {12: 1.0})
        self.assertEqual(flat_weights[21], {21: 1.0})
        self.assertEqual(flat_weights[24], {21: 1.0})

        def assertAlmostEqual(ddict1, ddict2):
            self.assertEqual(ddict1.keys(), ddict2.keys())
            for key in ddict1.keys():
                self.assertAlmostEqual(ddict1[key], ddict2[key])

        assertAlmostEqual(flat_weights[2], {1: 10.0 / 11.0, 12: 1.0 / 11.0})
        assertAlmostEqual(flat_weights[10], {1: 2.0 / 11.0, 12: 9.0 / 11.0})
        assertAlmostEqual(flat_weights[18], {12: 3.0 / 9.0, 21: 6.0 / 9.0})

    def test_flat_field_data_url(self):
        """insure the flat_field is computed. Simple processing test when
        provided data is a DataUrl"""
        projections_keys = [key for key in self.scan.projections.keys()]
        projections_urls = [self.scan.projections[key] for key in projections_keys]
        self.scan.flat_field_correction(projections_urls, projections_keys)

    def test_flat_field_data_numpy_array(self):
        """insure the flat_field is computed. Simple processing test when
        provided data is a numpy array"""
        self.scan.projections = self._data_urls
        projections_keys = [key for key in self.scan.projections.keys()]
        projections_urls = [self.scan.projections[key] for key in projections_keys]
        self.scan.flat_field_correction(projections_urls, projections_keys)
