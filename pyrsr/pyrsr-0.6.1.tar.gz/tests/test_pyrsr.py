#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pyrsr, A package providing relative spectral response functions for remote sensing instruments.
#
# Copyright (C) 2019-2021
# - Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
# - Helmholtz Centre Potsdam - GFZ German Research Centre for Geosciences Potsdam,
#   Germany (https://www.gfz-potsdam.de/)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Tests for `pyrsr` package."""


import unittest

from pyrsr.rsr import RelativeSpectralResponse
from pyrsr.sensorspecs import get_LayerBandsAssignment


class TestRelativeSpectralResponse(unittest.TestCase):
    """Tests for `pyrsr.RelativeSpectralResponse` class."""

    def test_Landsat8(self):
        RelativeSpectralResponse(satellite='Landsat-8', sensor='OLI_TIRS')

    def test_Landsat7(self):
        RelativeSpectralResponse(satellite='Landsat-7', sensor='ETM+')

    def test_Landsat5(self):
        RelativeSpectralResponse(satellite='Landsat-5', sensor='TM')

    def test_Landsat4(self):
        RelativeSpectralResponse(satellite='Landsat-4', sensor='TM')

    def test_RapidEye(self):
        RelativeSpectralResponse(satellite='RapidEye', sensor='MSI')
        RelativeSpectralResponse(satellite='RapidEye-5', sensor='MSI')

    def test_Sentinel2A(self):
        RelativeSpectralResponse(satellite='Sentinel-2A', sensor='MSI')

    def test_Sentinel2B(self):
        RelativeSpectralResponse(satellite='Sentinel-2B', sensor='MSI')

    def test_Spot1(self):
        RelativeSpectralResponse(satellite='SPOT-1', sensor='HRV1')
        RelativeSpectralResponse(satellite='SPOT-1', sensor='HRV2')

    def test_Spot2(self):
        RelativeSpectralResponse(satellite='SPOT-2', sensor='HRV1')
        RelativeSpectralResponse(satellite='SPOT-2', sensor='HRV2')

    def test_Spot3(self):
        RelativeSpectralResponse(satellite='SPOT-3', sensor='HRV1')
        RelativeSpectralResponse(satellite='SPOT-3', sensor='HRV2')

    def test_Spot4(self):
        RelativeSpectralResponse(satellite='SPOT-4', sensor='HRVIR1')
        RelativeSpectralResponse(satellite='SPOT-4', sensor='HRVIR2')

    def test_Spot5(self):
        RelativeSpectralResponse(satellite='SPOT-5', sensor='HRG1')
        RelativeSpectralResponse(satellite='SPOT-5', sensor='HRG2')

    def test_Aster(self):
        RelativeSpectralResponse(satellite='Terra', sensor='ASTER')

    def test_TerraModis(self):
        RelativeSpectralResponse(satellite='Terra', sensor='MODIS')

    def test_AquaModis(self):
        RelativeSpectralResponse(satellite='Aqua', sensor='MODIS')

    def test_custom_LayerBandsAssignment(self):
        RSR = RelativeSpectralResponse(satellite='Sentinel-2A', sensor='MSI',
                                       LayerBandsAssignment=['1', '2', '3', '4', '5', '6', '7'])

        self.assertEqual(len(RSR.wvl), 7)

    def test_sort_by_cwl(self):
        RSR = RelativeSpectralResponse(satellite='Landsat-7', sensor='ETM+',
                                       sort_by_cwl=True, no_pan=False)

        self.assertEqual(list(sorted(RSR.wvl.tolist())), RSR.wvl.tolist())


class Test_get_LayerBandsAssignment(unittest.TestCase):
    def test_fullLBA(self):
        LBA = get_LayerBandsAssignment('Landsat-7', 'ETM+')
        self.assertEqual(len(LBA), 9)

    def test_nopan_nothermal(self):
        LBA = get_LayerBandsAssignment('Landsat-7', 'ETM+', no_pan=True)
        self.assertEqual(len(LBA), 8)

        LBA = get_LayerBandsAssignment('Landsat-7', 'ETM+', no_thermal=True)
        self.assertEqual(len(LBA), 7)

        LBA = get_LayerBandsAssignment('Landsat-7', 'ETM+', no_pan=True, no_thermal=True)
        self.assertEqual(len(LBA), 6)

    def test_sort_by_cwl(self):
        LBA = get_LayerBandsAssignment('Landsat-7', 'ETM+', no_thermal=True, sort_by_cwl=True)
        self.assertEqual(len(LBA), 7)
        self.assertEqual(LBA, ['1', '2', '3', '8', '4', '5', '7'])

    def test_after_ac(self):
        LBA = get_LayerBandsAssignment('Sentinel-2A', 'MSI', after_ac=True)
        self.assertEqual(len(LBA), 11)
        self.assertEqual(LBA, ['1', '2', '3', '4', '5', '6', '7', '8', '8A', '11', '12'])
