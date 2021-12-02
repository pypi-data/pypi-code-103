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


"""Main module."""


import collections
import os
from typing import Dict, Union, List
import logging
import warnings

import numpy as np
from pandas import DataFrame, Series

from . import __path__
from .sensorspecs import get_LayerBandsAssignment


def RSR_reader(satellite, sensor, subsystem='',
               LayerBandsAssignment=None, sort_by_cwl=False, after_ac=False, no_thermal=False, no_pan=False,
               tolerate_missing=False, logger=None, v=False):
    # type: (str, str, str, list, bool, bool, bool, bool, bool, logging.Logger, bool) -> collections.OrderedDict
    """Read RSR for any sensor and return a dictionary containing band names as keys and RSR numpy arrays as values.

    :param satellite:       satellite to read the relative spectral response for
    :param sensor:          sensor to read the relative spectral response for
    :param subsystem:       subsystem to read the relative spectral response for
    :param LayerBandsAssignment:    custom list of bands to read, e.g., ['1', '3', '8']
    :param sort_by_cwl:     whether to sort the returned bands list by central wavelength position
                            (default: False)
    :param after_ac:        whether to ignore bands that are not available anymore after atmospheric correction
                            (default: False)
    :param no_thermal:      whether to exclude thermal bands from the returned bands list (default: False)
    :param no_pan:          whether to exclude panchromatic bands from the returned bands list (default: False)
    :param tolerate_missing:    If True, a warning is raised instead of a FileNotFoundError if a file is missing.
    :param logger:          instance of logging.Logger
    :param v:               verbose mode
    """
    RSR_dict = collections.OrderedDict()
    sat_dir = satellite if not satellite.startswith('RapidEye') else 'RapidEye'
    RSR_dir = os.path.join(__path__[0], 'data', sat_dir, sensor)

    LBA = LayerBandsAssignment or get_LayerBandsAssignment(satellite, sensor, subsystem,
                                                           no_thermal=no_thermal, no_pan=no_pan,
                                                           sort_by_cwl=sort_by_cwl, after_ac=after_ac)

    for band in LBA:
        bandname = 'band_%s' % band
        RSR_path = os.path.join(RSR_dir, bandname)
        try:
            RSR_dict[band] = np.loadtxt(RSR_path, skiprows=1)
            if v:
                msg = 'Reading RSR for %s %s, %s...' % (satellite, sensor, bandname)
                if logger:
                    logger.info(msg)
                else:
                    print(msg)

        except FileNotFoundError:
            msg = 'No spectral response functions found for %s %s %s at %s!'\
                  % (satellite, sensor, bandname, RSR_path)

            if tolerate_missing:
                msg = '%s >None< is returned.' % msg
                if logger:
                    logger.warning(msg)
                else:
                    warnings.warn(msg)
            else:
                raise FileNotFoundError(msg)

    return RSR_dict


class RelativeSpectralResponse(object):
    def __init__(self, satellite, sensor, subsystem='', wvl_unit='nanometers', specres_nm=1, format_bandnames=False,
                 LayerBandsAssignment=None, sort_by_cwl=False, after_ac=False, no_thermal=False, no_pan=False, v=False):
        # type: (str, str, str, str, float, bool, list, bool, bool, bool, bool, bool) -> None
        """RelativeSpectralResponse instance provides relative spectral response functions, wavelength positions, etc..

        :param satellite:           satellite to create the RelativeSpectralResponse instance for
        :param sensor:              sensor to create the RelativeSpectralResponse instance for
        :param wvl_unit:            the wavelengths unit to be used within RelativeSpectralResponse instance
                                    ('nanometers' or 'micrometers)
        :param specres_nm:          output spectral resolution of RSRs in nanometers
        :param format_bandnames:    whether to format default strings from LayerBandsAssignment as 'B01', 'B02' etc..
        :param LayerBandsAssignment:    custom list of bands to include, e.g., ['1', '3', '8']
        :param sort_by_cwl:         whether to sort the returned bands list by central wavelength position
                                    (default: False)
        :param after_ac:            whether to ignore bands that are not available anymore after atmospheric correction
                                    (default: False)
        :param no_thermal           whether to exclude thermal bands from the returned bands list
                                    (default: False)
        :param no_pan:              whether to exclude panchromatic bands from the returned bands list
                                    (default: False)
        :param v:                   verbose mode
        """
        # set defaults
        if wvl_unit not in ['micrometers', 'nanometers']:
            raise ValueError('Unknown wavelength unit %s.' % wvl_unit)

        self.rsrs_wvl = []  # wavelength positions with 1 nm precision
        self.rsrs = {}  # RSR values with 1 nm precision
        self.rsrs_norm01 = {}  # RSR values with 1 nm precision
        self.bands = []
        self.wvl = []
        self.fwhm = []
        self.wvl_unit = wvl_unit
        self.specres_nm = specres_nm
        self.format_bandnames = format_bandnames
        self.satellite = satellite
        self.sensor = sensor
        self.conv = {}
        self.LayerBandsAssignment = LayerBandsAssignment or []
        self.no_thermal = no_thermal
        self.no_pan = no_pan
        self.v = v

        self.from_satellite_sensor(satellite, sensor, subsystem,
                                   sort_by_cwl=sort_by_cwl, after_ac=after_ac,
                                   no_thermal=no_thermal, no_pan=no_pan, LayerBandsAssignment=LayerBandsAssignment, v=v)

    def from_satellite_sensor(self, satellite, sensor, subsystem='', **kwargs):
        rsr_dict = RSR_reader(satellite, sensor, subsystem, **kwargs)  # (ordered according to LBA)
        return self.from_dict(rsr_dict)

    def from_dict(self, rsr_dict):
        # type: (collections.OrderedDict) -> RelativeSpectralResponse
        """Create an instance of RelativeSpectralResponse from a dictionary.

        :param rsr_dict:    {'key_LayerBandsAssignment': <2D array: cols=[wvl,resp],rows=samples>}
        """
        from scipy.interpolate import interp1d

        is_nm = [300 < np.max(rsr_dict[band][:, 0]) < 15000 for band in rsr_dict]
        assert len(set(is_nm)) == 1, "'rsr_dict' must contain only one wavelength unit."
        scale_factor = 1 if is_nm[0] else 1000

        all_wvls = np.concatenate(list((arr[:, 0] for key, arr in rsr_dict.items()))) * scale_factor
        wvl = np.arange(all_wvls.min(), all_wvls.max() + self.specres_nm, self.specres_nm).astype(np.int16)

        df = DataFrame(index=wvl)
        bandnames = []
        for band in rsr_dict:  # = OrderedDict -> order follows LayerBandsAssignment
            bandname = band if not self.format_bandnames else ('B%s' % band if len(band) == 2 else 'B0%s' % band)
            bandnames.append(bandname)

            rsrs = rsr_dict[band][:, 1]
            wvls = np.array(rsr_dict[band][:, 0] * scale_factor)

            # interpolate input RSRs to target spectral resolution
            wvl_s = wvl[np.abs(wvl - min(wvls)).argmin()]
            wvl_e = wvl[np.abs(wvl - max(wvls)).argmin()]
            wvls_tgtres = np.arange(wvl_s, wvl_e + self.specres_nm, self.specres_nm).astype(np.int16)
            rsrs_tgtres = interp1d(wvls, rsrs, bounds_error=False, fill_value=0, kind='linear')(wvls_tgtres)

            # join RSR for the current band to df
            df = df.join(Series(rsrs_tgtres, index=wvls_tgtres, name=bandname))

        df = df.fillna(0)
        wvl = np.array(df.index.astype(float))
        rsrs_norm01 = df.to_dict(orient='series')  # type: Dict[Series]

        ################
        # set attributes
        ################

        for bN in rsrs_norm01:
            self.rsrs_norm01[bN] = rsr = np.array(rsrs_norm01[bN], dtype=float)
            self.rsrs[bN] = rsr / np.trapz(x=wvl, y=rsr)  # TODO seems like we NEED nanometers here; BUT WHY??

        self.rsrs_wvl = np.array(wvl)
        self.bands = bandnames
        self.LayerBandsAssignment = list(rsr_dict.keys())

        # FIXME this is not the GMS algorithm to calculate center wavelengths
        # calculate center wavelengths
        # TODO seems like we NEED nanometers here; BUT WHY??:
        self.wvl = np.array([np.trapz(x=self.rsrs_wvl, y=self.rsrs_wvl * self.rsrs[band]) for band in self.bands])
        # self.wvl = self.wvl if self.wvl_unit == 'micrometers' else np.array([int(i) for i in self.wvl])

        # calculate FWHM
        fwhm = []
        for band in self.bands:
            rsr_band = self.rsrs_norm01[band]
            rsr_halfmax = np.max(rsr_band) / 2.
            wvls_within_fullwidth = self.rsrs_wvl[rsr_band >= rsr_halfmax]
            fwhm.append(np.max(wvls_within_fullwidth) - np.min(wvls_within_fullwidth))
        self.fwhm = np.array(fwhm)

        # force nanometer output
        if self.wvl_unit == 'micrometers':
            self.rsrs_wvl *= 1000
            self.wvl *= 1000
            self.fwhm *= 1000

        self.conv.update({key: value for key, value in zip(self.bands, self.wvl)})
        self.conv.update({value: key for key, value in zip(self.bands, self.wvl)})

        return self

    def instrument(self, bands):
        return {
            'rspf': np.vstack([self[band] for band in bands]),
            'wvl_rsp': np.copy(self.rsrs_wvl),
            'wvl_inst': np.copy(self.wvl),
            'sol_irr': None
        }

    def convert_wvl_unit(self):
        """Convert the wavelength unit to nanometers if they are in micrometers or vice versa."""
        factor = 1/1000 if self.wvl_unit == 'nanometers' else 1000
        self.rsrs_wvl = self.rsrs_wvl * factor
        self.wvl = self.wvl * factor
        self.wvl_unit = 'nanometers' if self.wvl_unit == 'micrometers' else 'micrometers'

    def __call__(self, band):
        return self.rsrs[band]

    def __getitem__(self, band):
        return self.rsrs[band]

    def __iter__(self):
        for band in self.bands:
            yield self[band]

    def plot_rsrs(self, figsize: tuple = (15, 5), band: Union[str, List[str]] = None, normalize: bool = True):
        """Show a plot of all spectral response functions.

        :param figsize:     figure size of the plot
        :param band:        band key to plot a single band instead of all bands
        :param normalize:   normalize RSRs to 0-1 (default: True)
        """
        from matplotlib import pyplot as plt

        if band and band not in self.bands:
            raise ValueError("Parameter 'band' must be a string out of those: %s."
                             % ', '.join(self.bands))

        plt.figure(figsize=figsize)
        bands2plot = [band] if band else self.bands
        for band in bands2plot:
            rsrs = list(self.rsrs_norm01[band]) if normalize else list(self.rsrs[band])
            plt.plot(self.rsrs_wvl, rsrs, '-', label='Band %s' % band)
        plt.title(' '.join(['Spectral response functions', self.satellite, self.sensor]))
        plt.xlabel('wavelength [%s]' % self.wvl_unit)
        plt.ylabel('spectral response')
        plt.legend(loc='upper right')


RSR = RelativeSpectralResponse  # alias
