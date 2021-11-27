import numpy as np
import astropy.units as u
from astropy.units import Quantity
import dask.array as da
import xarray as xr
from astropy.constants import c
from .antenna import Antenna
from .baseline import Baseline
from .ms import MS
from ..reconstruction import PSF
from ..units.lambda_units import lambdas_equivalencies
from ..units import array_unit_conversion
from typing import List, Union
from more_itertools import locate
import logging


def calc_beam_size(s_uu, s_vv, s_uv) -> tuple:
    """

    Parameters
    ----------
    s_uu : float
          Weighted sum of u^2.
    s_vv : float
          Weighted sum of v^2.
    s_uv : float
          Weighted sum of u*v.

    Returns
    -------
    tuple
        Beam major, minor and position angle in radians.
    """
    with np.errstate(divide='ignore'):
        uv_squared = s_uv * s_uv
        uu_minus_vv = s_uu - s_vv
        uu_plus_vv = s_uu + s_vv
        sqrt_in = np.sqrt(4.0 * uv_squared + (uu_minus_vv * uu_minus_vv))
        bmaj = 2.0 * np.sqrt(np.log(2.0)) / np.pi / np.sqrt(uu_plus_vv - sqrt_in)  # Major axis in radians
        bmin = 2.0 * np.sqrt(np.log(2.0)) / np.pi / np.sqrt(uu_plus_vv + sqrt_in)  # Minor axis in radians
        bpa = -0.5 * np.arctan2(2.0 * s_uv, uu_minus_vv)  # Angle in radians
        return bmaj * u.rad, bmin * u.rad, bpa * u.rad


class Dataset:
    def __init__(self, antenna: Antenna = None, baseline: Baseline = None,
                 spectral_window_dataset: List[xr.Dataset] = None, ms_list: List[MS] = None,
                 psf: Union[PSF, List[PSF]] = None, feed_kind: str = None):
        """

        Parameters
        ----------
        antenna : Full Antenna object
        baseline : Full Baseline object
        spectral_window_dataset : Full Spectral Window dataset
        ms_list : List of separated MS
        psf : PSF object of the dataset, or list of PSF objects for each one the Stokes parameters
        feed_kind : Kind of feed of the dataset. E.g "linear", "circular".
        """

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.antenna = antenna
        self.baseline = baseline
        self.spectral_window_dataset = spectral_window_dataset
        self.ms_list = ms_list
        self.psf = psf
        self.feed_kind = feed_kind

        self.max_nu = 0.0 * u.Hz  # Maximum frequency in Hz
        self.min_nu = 0.0 * u.Hz  # Minimum frequency in Hz
        self.ref_nu = 0.0 * u.Hz  # Reference frequency in Hz

        self.lambda_min = 0.0 * u.m  # Minimum wavelength in meters
        self.lambda_max = 0.0 * u.m  # Maximum wavelength in meters
        self.lambda_ref = 0.0 * u.m  # Reference wavelength in meters

        self.max_baseline = 0.0 * u.m  # Maximum baseline in meters
        self.min_baseline = 0.0 * u.m  # Minimum baseline in meters

        self.max_antenna_diameter = 0.0 * u.m  # Maximum antenna diameter in meters
        self.min_antenna_diameter = 0.0 * u.m  # Minimum antenna diameter in meters

        self.theo_resolution = 0.0 * u.rad  # Theoretical resolution in radians
        self.fov = 0.0 * u.rad  # Field-of-view in radians

        self.ndatasets = 0

        self.corr_weight_sum = None

        if spectral_window_dataset is not None:
            max_freqs = []
            min_freqs = []
            ref_freqs = []
            for spw in spectral_window_dataset:
                max_freqs.append(spw.CHAN_FREQ.max().data)
                min_freqs.append(spw.CHAN_FREQ.min().data)
                ref_freqs.append(spw.REF_FREQUENCY.data)

            max_freqs = list(da.compute(*max_freqs))
            min_freqs = list(da.compute(*min_freqs))

            self.max_nu = max(max_freqs) * u.Hz
            self.min_nu = min(min_freqs) * u.Hz
            self.ref_nu = np.median(np.array(ref_freqs)) * u.Hz

            self.lambda_min = c / self.max_nu
            self.lambda_min = self.lambda_min.to(u.m)
            self.lambda_max = c / self.min_nu
            self.lambda_max = self.lambda_max.to(u.m)
            self.lambda_ref = c / self.ref_nu
            self.lambda_ref = self.lambda_ref.to(u.m)

        if antenna is not None:
            self.max_antenna_diameter = antenna.max_diameter
            self.min_antenna_diameter = antenna.min_diameter

        if baseline is not None:
            self.max_baseline = baseline.max_baseline
            self.min_baseline = baseline.min_baseline

        if antenna is not None and baseline is not None and spectral_window_dataset is not None:
            self.theo_resolution = (self.lambda_min / self.max_baseline) * u.rad
            self.fov = (self.lambda_max / self.max_antenna_diameter) * u.rad

        if ms_list is not None:
            self.ndatasets = len(self.ms_list)
            self.check_feed()

            if self.psf is None:
                self.calculate_psf()

    def sum_weights_stokes(self) -> dict:
        stokes_dict = {'I': 0.0, 'Q': 0.0, 'U': 0.0, 'V': 0.0}
        if self.feed_kind == "linear":
            stokes_dict['I'] = self.corr_weight_sum['XX'] + self.corr_weight_sum['YY']
            stokes_dict['Q'] = self.corr_weight_sum['XX'] + self.corr_weight_sum['YY']
            stokes_dict['U'] = self.corr_weight_sum['XY'] + self.corr_weight_sum['YX']
            stokes_dict['V'] = self.corr_weight_sum['XY'] + self.corr_weight_sum['YX']
        elif self.feed_kind == "circular":
            stokes_dict['I'] = self.corr_weight_sum['LL'] + self.corr_weight_sum['RR']
            stokes_dict['Q'] = self.corr_weight_sum['RL'] + self.corr_weight_sum['LR']
            stokes_dict['U'] = self.corr_weight_sum['RL'] + self.corr_weight_sum['LR']
            stokes_dict['V'] = self.corr_weight_sum['LL'] + self.corr_weight_sum['RR']
        else:
            stokes_dict['I'] = self.corr_weight_sum['XX'] + self.corr_weight_sum['YY'] + self.corr_weight_sum['LL'] + self.corr_weight_sum['RR']
            stokes_dict['Q'] = self.corr_weight_sum['XX'] + self.corr_weight_sum['YY'] + self.corr_weight_sum['RL'] + self.corr_weight_sum['LR']
            stokes_dict['U'] = self.corr_weight_sum['XY'] + self.corr_weight_sum['YX'] + self.corr_weight_sum['RL'] + self.corr_weight_sum['LR']
            stokes_dict['V'] = self.corr_weight_sum['XY'] + self.corr_weight_sum['YX'] + self.corr_weight_sum['LL'] + self.corr_weight_sum['RR']

        return stokes_dict

    def check_feed(self) -> None:
        """
        Function to check if a feed of the dataset is
        linear, circular or mixed
        """
        feed_list = []
        for ms in self.ms_list:
            feed_list.append(ms.polarization.feed_kind)
        if all(x == "linear" for x in feed_list):
            self.feed_kind = "linear"
        elif all(x == "circular" for x in feed_list):
            self.feed_kind = "circular"
        else:
            self.feed_kind = "mixed"

    def max_ncorrs(self) -> int:
        ncorrs = []
        for ms in self.ms_list:
            ncorrs.append(ms.polarization.ncorrs)
        return max(ncorrs)

    def calculate_weights_sum(self) -> None:

        if self.feed_kind == "linear":
            weight_corr_dict = {'XX': 0.0, 'YX': 0.0, 'XY': 0.0, 'YY': 0.0}
        elif self.feed_kind == "circular":
            weight_corr_dict = {'LL': 0.0, 'RL': 0.0, 'LR': 0.0, 'RR': 0.0}
        else:
            weight_corr_dict = {'XX': 0.0, 'YX': 0.0, 'XY': 0.0, 'YY': 0.0, 'LL': 0.0, 'RL': 0.0, 'LR': 0.0, 'RR': 0.0}

        for ms in self.ms_list:
            weight = ms.visibilities.weight.data
            flag = ms.visibilities.flag.data
            ncorrs = ms.polarization.ncorrs
            nchans = ms.spectral_window.nchans
            corr_names = ms.polarization.corrs_names
            weight_broadcast = da.repeat(weight, nchans, axis=0)
            flag = flag.reshape((len(flag) * nchans, ncorrs))
            weight_broadcast[flag] = 0.0

            weight_sum = da.sum(weight_broadcast, axis=0)

            for idx_corr in range(0, ncorrs):
                weight_corr_dict[corr_names[idx_corr]] += weight_sum[idx_corr]

        weight_corr_dict = da.compute(weight_corr_dict)[0]

        self.corr_weight_sum = weight_corr_dict

    def calculate_psf(self, stokes: Union[List[str], str] = None) -> None:
        """
        Function that calculates the PSF properties (bmaj, bmin and bpa) analytically for different stokes using
        (u,v) positions and the weights
        """
        if stokes is None:
            stokes = ["I", "Q", "U", "V"]
        else:
            if isinstance(stokes, str):
                stokes = stokes.split(',')

        self.calculate_weights_sum()

        idx_I = list(locate(stokes, lambda x: x == "I"))
        idx_Q = list(locate(stokes, lambda x: x == "Q"))
        idx_U = list(locate(stokes, lambda x: x == "U"))
        idx_V = list(locate(stokes, lambda x: x == "V"))

        nstokes = len(stokes)

        s_uu = da.zeros(nstokes, dtype=np.float64)
        s_vv = da.zeros(nstokes, dtype=np.float64)
        s_uv = da.zeros(nstokes, dtype=np.float64)

        for ms in self.ms_list:
            chans = ms.spectral_window.chans.compute()
            nchans = ms.spectral_window.nchans
            uvw = ms.visibilities.uvw.data
            weight = ms.visibilities.weight.data
            flag = ms.visibilities.flag.data
            ncorrs = ms.polarization.ncorrs
            corr_names = ms.polarization.corrs_names

            uvw_broadcast = da.tile(uvw, nchans).reshape((len(uvw), nchans, 3))
            chans_broadcast = chans[np.newaxis, :, np.newaxis]

            uvw_lambdas = array_unit_conversion(array=uvw_broadcast, unit=u.lambdas,
                                                equivalencies=lambdas_equivalencies(restfreq=chans_broadcast))

            uvw_lambdas = da.map_blocks(lambda x: x.value, uvw_lambdas, dtype=np.float64)
            uvw_lambdas = uvw_lambdas.reshape((len(uvw_lambdas) * nchans, 3))
            weight_broadcast = da.repeat(weight, nchans, axis=0)
            flag = flag.reshape((len(flag) * nchans, ncorrs))
            weight_broadcast[flag] = 0.0

            idx_corrs = [key for key, value in corr_names.items()]
            _u = uvw_lambdas[:, 0, np.newaxis]
            _v = uvw_lambdas[:, 1, np.newaxis]

            _s_uu = da.sum(weight_broadcast * _u ** 2, axis=0)
            _s_vv = da.sum(weight_broadcast * _v ** 2, axis=0)
            _s_uv = da.sum(weight_broadcast * _u * _v, axis=0)

            for i in idx_corrs:
                if corr_names[i] == "XX":
                    if idx_I:
                        s_uu[idx_I[0]] += _s_uu[i]
                        s_vv[idx_I[0]] += _s_vv[i]
                        s_uv[idx_I[0]] += _s_uv[i]

                    if idx_Q:
                        s_uu[idx_Q[0]] += _s_uu[i]
                        s_vv[idx_Q[0]] += _s_vv[i]
                        s_uv[idx_Q[0]] += _s_uv[i]
                elif corr_names[i] == "XY":
                    if idx_U:
                        s_uu[idx_U[0]] += _s_uu[i]
                        s_vv[idx_U[0]] += _s_vv[i]
                        s_uv[idx_U[0]] += _s_uv[i]

                    if idx_V:
                        s_uu[idx_V[0]] += _s_uu[i]
                        s_vv[idx_V[0]] += _s_vv[i]
                        s_uv[idx_V[0]] += _s_uv[i]
                elif corr_names[i] == "YX":
                    if idx_U:
                        s_uu[idx_U[0]] += _s_uu[i]
                        s_vv[idx_U[0]] += _s_vv[i]
                        s_uv[idx_U[0]] += _s_uv[i]

                    if idx_V:
                        s_uu[idx_V[0]] += _s_uu[i]
                        s_vv[idx_V[0]] += _s_vv[i]
                        s_uv[idx_V[0]] += _s_uv[i]
                elif corr_names[i] == "YY":
                    if idx_I:
                        s_uu[idx_I[0]] += _s_uu[i]
                        s_vv[idx_I[0]] += _s_vv[i]
                        s_uv[idx_I[0]] += _s_uv[i]
                    if idx_Q:
                        s_uu[idx_Q[0]] += _s_uu[i]
                        s_vv[idx_Q[0]] += _s_vv[i]
                        s_uv[idx_Q[0]] += _s_uv[i]
                elif corr_names[i] == "LL":
                    if idx_I:
                        s_uu[idx_I[0]] += _s_uu[i]
                        s_vv[idx_I[0]] += _s_vv[i]
                        s_uv[idx_I[0]] += _s_uv[i]
                    if idx_V:
                        s_uu[idx_V[0]] += _s_uu[i]
                        s_vv[idx_V[0]] += _s_vv[i]
                        s_uv[idx_V[0]] += _s_uv[i]
                elif corr_names[i] == "LR":
                    if idx_Q:
                        s_uu[idx_Q[0]] += _s_uu[i]
                        s_vv[idx_Q[0]] += _s_vv[i]
                        s_uv[idx_Q[0]] += _s_uv[i]
                    if idx_U:
                        s_uu[idx_U[0]] += _s_uu[i]
                        s_vv[idx_U[0]] += _s_vv[i]
                        s_uv[idx_U[0]] += _s_uv[i]
                elif corr_names[i] == "RL":
                    if idx_Q:
                        s_uu[idx_Q[0]] += _s_uu[i]
                        s_vv[idx_Q[0]] += _s_vv[i]
                        s_uv[idx_Q[0]] += _s_uv[i]

                    if idx_U:
                        s_uu[idx_U[0]] += _s_uu[i]
                        s_vv[idx_U[0]] += _s_vv[i]
                        s_uv[idx_U[0]] += _s_uv[i]
                elif corr_names[i] == "RR":
                    if idx_I:
                        s_uu[idx_I[0]] += _s_uu[i]
                        s_vv[idx_I[0]] += _s_vv[i]
                        s_uv[idx_I[0]] += _s_uv[i]

                    if idx_V:
                        s_uu[idx_V[0]] += _s_uu[i]
                        s_vv[idx_V[0]] += _s_vv[i]
                        s_uv[idx_V[0]] += _s_uv[i]
                else:
                    raise ValueError("The correlation does not exist")

        weights_per_stokes = self.sum_weights_stokes()
        weights_per_selected_stokes = np.array(list(map(weights_per_stokes.get, stokes)))
        s_uu[weights_per_selected_stokes > 0.0] /= weights_per_selected_stokes[weights_per_selected_stokes > 0.0]
        s_vv[weights_per_selected_stokes > 0.0] /= weights_per_selected_stokes[weights_per_selected_stokes > 0.0]
        s_uv[weights_per_selected_stokes > 0.0] /= weights_per_selected_stokes[weights_per_selected_stokes > 0.0]

        s_uu, s_vv, s_uv = da.compute(s_uu, s_vv, s_uv)
        bmaj, bmin, bpa = calc_beam_size(s_uu, s_vv, s_uv)

        psf_objects = []
        for i in range(0, nstokes):
            if weights_per_selected_stokes[i] > 0.0:
                sigma = Quantity([bmaj[i], bmin[i]])
                psf_objects.append(PSF(sigma=sigma, theta=bpa[i]))
            else:
                psf_objects.append(None)

        if len(psf_objects) == 1:
            self.psf = psf_objects[0]
        else:
            self.psf = psf_objects
