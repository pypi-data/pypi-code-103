from __future__ import annotations
import numpy as np
import logging
import os
from glob import glob
from typing import NoReturn, Union, List, Tuple, Type, Dict
from scipy.stats import norm as normal_dist
from copy import deepcopy
from tqdm import trange
import pickle

from randdpy.core.Calibration import Calibration
from randdpy.core.Spectrum import Spectrum, EmissionSpectrum
from randdpy.Algorithms.Deconvolution.DeconvolutionAlgorithmBase import DeconvolutionAlgorithm
from randdpy.Algorithms.Deconvolution.SheppVardi import SheppVardiDeconvolution


class ScatterMatrix:
    def __init__(self,
                 matrix: np.ndarray,
                 calibration: Calibration):
        self.matrix = matrix
        self.calibration = calibration

    def convolve_spectrum(self, spectrum: Spectrum) -> Spectrum:
        """ Method which convolves an incident spectrum with the scatter-matrix,
        and returns the scattered spectrum.

        Parameters
        ----------
        spectrum : Spectrum
            Spectrum to be convolved. Note, spectrum will be rebinned if not
            same calibration and size as the array of responses in the
            scatter-matrix.

        Returns
        -------
        Instance of core.Spectrum class
            Convolution of incident spectrum with Q-matrix.
        """
        # Check if same number of n_channels and calibration.
        if not spectrum.calibration == self.calibration:
            spectrum = spectrum.rebin(self.calibration)

        name = spectrum.name + " " if spectrum.name is not None else ""
        ret_spec = Spectrum(self.calibration.energies,
                            np.dot(self.matrix.T, spectrum.counts),
                            live_time=spectrum.live_time,
                            real_time=spectrum.real_time,
                            name=name + "convolved",
                            comment=spectrum.comment,
                            start_time=spectrum.start_time)
        return ret_spec

    def save(self, file_name: str):
        d = deepcopy(self.__dict__)
        d['calibration'] = self.calibration.__dict__
        with open(file_name, 'wb') as f:
            pickle.dump(d, f)

    @classmethod
    def from_engbin_directory(cls,
                              engbin_directory: str,
                              photons_per_engbin: int,
                              calibration: Calibration = None,
                              energy_column: int = 0,
                              counts_column: int = 1,
                              start_index: int = 0):
        engbin_files = glob(os.path.join(engbin_directory, "engbin*.eb"))
        matrix: ScatterMatrix = None if calibration is None else cls(np.zeros((calibration.n_channels,
                                                                               calibration.n_channels)),
                                                                     calibration)
        for i in trange(start_index, start_index+len(engbin_files)):
            engbin_spectrum = Spectrum.from_txt(os.path.join(engbin_directory, f"engbin{i}.eb"),
                                                energy_column=energy_column, counts_column=counts_column)

            if calibration is not None and engbin_spectrum.calibration != calibration:
                engbin_spectrum = engbin_spectrum.rebin(calibration)

            if matrix is None:
                matrix = cls(np.zeros((engbin_spectrum.calibration.n_channels,
                                       engbin_spectrum.calibration.n_channels)), engbin_spectrum.calibration)
            matrix.matrix[i - start_index] = engbin_spectrum.counts / photons_per_engbin
        return matrix

    @classmethod
    def load(cls, file_name: str) -> ScatterMatrix:
        with open(file_name, 'rb') as f:
            d = pickle.load(f)
        calibration = Calibration()
        calibration.__dict__ = d['calibration']
        matrix = ScatterMatrix(d['matrix'], calibration)
        return matrix


DeconvolutionAlgo = Type[DeconvolutionAlgorithm]


class QMatrix:
    def __init__(
            self,
            measurement_calibration: Calibration = Calibration(),
            incident_calibration: Calibration = Calibration(),
            q_matrix: np.ndarray = None,
            engbins: Union[np.ndarray, None] = None,
            efficiency_data: Union[np.ndarray, None] = None,
            photons_per_engbin: float = 1.,
            additional_data: Union[Dict, None] = None
    ):
        self.m_calibration = measurement_calibration
        self.i_calibration = incident_calibration
        if q_matrix is None:
            self.q_matrix = np.zeros((self.i_calibration.n_channels, self.m_calibration.n_channels))
        else:
            self.q_matrix = q_matrix

        if engbins is None:
            self.engbins = np.zeros((self.i_calibration.n_channels, self.m_calibration.n_channels))
        else:
            self.engbins = engbins

        if efficiency_data is None:
            self.eff_data = np.zeros(self.i_calibration.n_channels)
        else:
            self.eff_data = efficiency_data
        self.photons_per_engbin = photons_per_engbin
        self.lld = 0

        self.additional_info = additional_data

        self.log = logging.getLogger(self.__class__.__name__)

    def set_engbin(self, engbin: np.ndarray, engbin_num: int) -> NoReturn:
        if engbin.size != self.m_calibration.n_channels:
            self.log.error(f"Engbin the wrong size. Got an array of size {engbin.size}. "
                           f"Expected {self.m_calibration.n_channels}")
            raise Exception("Engbin wrong size!")
        self.engbins[engbin_num, :] = engbin[:]

    def set_q_response(self, response: np.ndarray, response_num: int) -> NoReturn:
        if response.size != self.m_calibration.n_channels or len(response.shape) != 1:
            self.log.error(f"Response the wrong size. Got an array of shape {response.shape}. "
                           f"Expected {self.m_calibration.n_channels}")
            raise Exception("Response wrong size!")
        self.engbins[response_num, :] = response[:]

    def engbin_as_spectrum(self, engbin_num: int) -> Spectrum:
        return Spectrum(self.m_calibration, self.engbins[engbin_num])

    def q_response_as_spectrum(self, q_response_num: int) -> Spectrum:
        return Spectrum(self.m_calibration, self.q_matrix[q_response_num])

    def __broaden(self, sigmas: np.ndarray) -> NoReturn:
        """ Broaden engbins with sigma (gaussian standard deviation) values
        in units of n_channels numbers for each channel. Saves broadened
        responses to self.qmatrix, overwriting previous values.

        Parameters
        ----------
        sigmas : numpy.ndarray
            Array of sigma values.
        """
        if (self.engbins == 0.).all():
            self.log.warning("You are trying to broaden an empty engbin matrix...")

        def norm(mu: float, sigma: float, num: int):
            x = np.arange(num+1)
            cdf = normal_dist.cdf(x - 0.5, loc=mu, scale=sigma)
            return cdf[1:] - cdf[:-1]

        self.q_matrix[:, :] = 0.
        for ch, sig in enumerate(sigmas):
            broad = norm(ch, sig, self.m_calibration.n_channels)
            for i in range(self.i_calibration.n_channels):
                self.q_matrix[i] += self.engbins[i, ch] * broad

    def broaden(self, fwhms: np.ndarray) -> NoReturn:
        """ Broaden engbins with fwhm values in units of energy for each
        channel. Saves broadened responses to self.qmatrix, overwriting
        previous values.

        Parameters
        ----------
        fwhms : numpy.ndarray
            Array of fwhm values.
        """
        de = self.m_calibration.bin_widths
        sigmas = np.absolute(fwhms / (2.35 * de))
        self.__broaden(sigmas)

    def broaden_poly(self, fwhm_poly: Union[np.ndarray, List]) -> NoReturn:
        """ Broaden engbins with gaussians whose FWHM vary as a quadratic
        polynomial as a function of energy. Saves broadened responses to
        self.qmatrix, overwriting previous values. The FWHM as a function of
        energy is specified by a polynomial equation with coefficients in
        fwhm_poly.

        Parameters
        ----------
        fwhm_poly : list or numpy.ndarray
            quadratic coefficients (c0, c1, c2, c3),

                where FWHM(E) = c0 + c1*E + c2*E**2 + c3*E**3
        """
        energies = self.m_calibration.energies[:, np.newaxis]
        powers = np.arange(4)[np.newaxis, :]
        fwhm_poly = np.array(fwhm_poly)[np.newaxis, :]
        fwhms = (fwhm_poly[3] * np.power(energies, powers)).sum(axis=1)

        self.broaden(fwhms)

    def broaden_exp(self, fwhm_exp: Union[np.ndarray, List]) -> NoReturn:
        """ Broaden engbins with gaussians whose FWHM vary as a exponential as
        a function of energy. Saves broadened responses to self.qmatrix,
        overwriting previous values. The FWHM as a function of energy is
        specified by an exponential equation with coefficients in
        fwhm_exp.

        Parameters
        ----------
        fwhm_exp : list or numpy.ndarray
            exponential coefficients (c0, c1, c2),

                where FWHM(E) = c0 + c1*E**c2
        """

        fwhms = fwhm_exp[1] * self.m_calibration.energies ** fwhm_exp[2]
        fwhms[np.isnan(fwhms)] = 1E-20
        fwhms += fwhm_exp[0]

        self.broaden(fwhms)

    def set_photons_per_engbin(self, photons: float) -> NoReturn:
        """ Function that sets the number of
        photons incident on the detector per engbin. This number is used to
        normalise the engbins before convolutions/deconvolutions.

        Parameters
        ----------
        photons : int
            Number of photons per engbin.
        """
        self.photons_per_engbin = photons

    def set_lld(self, lld_energy: float) -> NoReturn:
        """ Function which sets the lower level discriminator, in units of
        energy.

        Parameters
        ----------
        lld_energy : float
            Low level discriminator in units of energy.
        """
        for i in range(self.m_calibration.n_channels):
            if lld_energy < self.m_calibration.energies[i]:
                self.lld = i
                return

    def get_lld(self) -> float:
        """ Function which returns the low level discriminator for the
        convolution and deconvolution algorithms, in units of energy.

        Returns
        -------
        float
            Lld in units of energy.
        """
        return self.m_calibration.energies[self.lld]

    def generate_eff_data(self) -> NoReturn:
        """ Function which generates efficiency data for saving to sqf
        """
        self.eff_data = self.engbins.sum(axis=1) / self.photons_per_engbin

    def convolve_spectrum(self, spectrum: Spectrum, matrix: str = "q_matrix", with_errors=False) -> Spectrum:
        """ Function which convolves an incident spectrum with the Q-matrix,
        and returns the convolved spectrum.

        Parameters
        ----------
        spectrum : Spectrum
            Spectrum to be convolved. Note, spectrum will be rebinned if not
            same calibration and size as the array of responses in the
            Q-matrix.
        matrix : str
            Either 'q_matrix' (default) or 'engbins'

        Returns
        -------
        Instance of core.Spectrum class
            Convolution of incident spectrum with Q-matrix.
        """
        # Check if same number of n_channels and calibration.
        if not spectrum.calibration == self.i_calibration:
            spectrum = spectrum.rebin(self.i_calibration)

        mat = getattr(self, matrix)
        normalised_responses = (mat.T / self.photons_per_engbin).copy()
        normalised_responses[:int(self.lld)] = 0
        # Generate convolution spectrum
        name = spectrum.name + " " if spectrum.name is not None else ""
        ret_spec = Spectrum(self.m_calibration.energies,
                            np.dot(normalised_responses, spectrum.counts),
                            live_time=spectrum.live_time,
                            real_time=spectrum.real_time,
                            error=np.sqrt(np.dot(normalised_responses**2, spectrum.error**2)) if with_errors else None,
                            name=name + "convolved",
                            comment=spectrum.comment,
                            start_time=spectrum.start_time)
        return ret_spec

    def generate_spectrum_from_lara_text(self,
                                         lara_txt_file: str,
                                         n: int = 1.0E6,
                                         scatter: ScatterMatrix = None) -> Spectrum:
        """ Method for generating a modelled spectrum from lara isotope data.
        Data can be downloaded here:
            http://www.nucleide.org/Laraweb/index.php

        Parameters
        ----------
        lara_txt_file : str
            Path to the lara text file.
        n : int
            Number of photons incident on the detector
        scatter : ScatterMatrix
            Optional scatter matrix to convolve the incident spectrum with before q-matrix convolution.

        Returns
        -------
            Spectrum
        """
        inc = EmissionSpectrum.from_lara_decay_data_file(lara_txt_file, self.i_calibration)
        inc.counts *= n
        if scatter is not None:
            inc = scatter.convolve_spectrum(inc)
        return self.convolve_spectrum(inc)

    def generate_spectrum_from_lara_online(self,
                                           isotope: str = "Cs-137",
                                           n: int = 1.0E6,
                                           scatter: ScatterMatrix = None) -> Spectrum:
        """ Method for generating a modelled spectrum from lara isotope data.
        Data can be downloaded here:
            http://www.nucleide.org/Laraweb/index.php

        Parameters
        ----------
        isotope : str
            Isotope in this format: "Cs-137"
        n : int
            Number of photons incident on the detector
        scatter : ScatterMatrix
            Optional scatter matrix to convolve the incident spectrum with before q-matrix convolution.

        Returns
        -------
            Spectrum
        """
        inc = EmissionSpectrum.from_lara_online(isotope, self.i_calibration)
        inc.counts *= n
        if scatter is not None:
            inc = scatter.convolve_spectrum(inc)
        return self.convolve_spectrum(inc)

    def rebin_measurement_axis(self, new_calibration):
        new_qmatrix = deepcopy(self)
        new_qmatrix.q_matrix = np.zeros((self.i_calibration.n_channels, new_calibration.n_channels))
        new_qmatrix.engbins = np.zeros((self.i_calibration.n_channels, new_calibration.n_channels))
        for i in range(new_qmatrix.i_calibration.n_channels):
            engbin = self.engbin_as_spectrum(i)
            new_qmatrix.engbins[i, :] = engbin.rebin(new_calibration).counts[:]
            q_response = self.q_response_as_spectrum(i)
            new_qmatrix.q_matrix[i, :] = q_response.rebin(new_calibration).counts[:]
        new_qmatrix.m_calibration = new_calibration
        return new_qmatrix

    def find_deconvolution_channel(self, energy: float) -> int:
        return self.i_calibration.find_channel(energy)

    def find_measurement_channel(self, energy: float) -> int:
        return self.m_calibration.find_channel(energy)

    def deconvolve_spectrum(
            self,
            spectrum: Spectrum,
            iterations: int = 1000,
            init: np.ndarray = None,
            method: DeconvolutionAlgo = SheppVardiDeconvolution
    ) -> Tuple[Spectrum, Spectrum]:
        """ Method for deconvolving a spectrum using this Q-matrix. Uses the Shepp and Vardi MLEM algorithm by default.

        Parameters
        ----------
        spectrum : Spectrum
            Spectrum to be deconvolved
        iterations: int
        init : np.ndarray
        method: DeconvolutionAlgorithm

        Returns
        -------
        Tuple[Spectrum, Spectrum]
        """
        # Check if same number of n_channels and calibration.
        if not spectrum.calibration == self.m_calibration:
            spectrum = spectrum.rebin(self.m_calibration)

        normalised_responses = self.q_matrix.T / (self.photons_per_engbin if self.photons_per_engbin > 0 else 1.)
        normalised_responses[:int(self.lld)] = 0
        name = spectrum.name + " " if spectrum.name is not None else ""

        deconvolver = method(normalised_responses)

        decon_counts, recon_counts = deconvolver.deconvolve_measurement(spectrum.counts, iterations, init)

        decon_spec = Spectrum(self.i_calibration.energies,
                              decon_counts,
                              name=name + "deconvolved",
                              live_time=spectrum.live_time,
                              real_time=spectrum.real_time)
        recon_spec = Spectrum(self.m_calibration.energies,
                              recon_counts,
                              name=name + "reconvolved",
                              live_time=spectrum.live_time,
                              real_time=spectrum.real_time)
        return decon_spec, recon_spec

    def bootstrap_deconvolve_spectrum(
            self,
            spectrum: Spectrum,
            iterations: int = 1000,
            bootstraps: int = 100,
            init: np.ndarray = None,
            method: DeconvolutionAlgo = SheppVardiDeconvolution,
            progress: bool = False
    ) -> Tuple[Spectrum, Spectrum]:
        # Check if same number of n_channels and calibration.
        if not spectrum.calibration == self.m_calibration:
            spectrum = spectrum.rebin(self.m_calibration)

        normalised_responses = self.q_matrix.T / (self.photons_per_engbin if self.photons_per_engbin > 0 else 1.)
        normalised_responses[:int(self.lld)] = 0
        name = spectrum.name + " " if spectrum.name is not None else ""

        deconvolver = method(normalised_responses)

        decon_counts, recon_counts, decon_err, recon_err = deconvolver.bootstrap_deconvolve_measurement(
            spectrum.counts,
            spectrum.error,
            iterations,
            bootstraps,
            init,
            progress
        )

        decon_spec = Spectrum(self.i_calibration.energies,
                              decon_counts,
                              name=name + "deconvolved",
                              live_time=spectrum.live_time,
                              real_time=spectrum.real_time,
                              error=decon_err)
        recon_spec = Spectrum(self.m_calibration.energies,
                              recon_counts,
                              name=name + "reconvolved",
                              live_time=spectrum.live_time,
                              real_time=spectrum.real_time,
                              error=recon_err)
        return decon_spec, recon_spec

    @classmethod
    def from_engbin_directory(cls, engbin_directory: str, incident_calibration: Calibration,
                              measurement_calibration: Calibration = None, energy_column: int = 0,
                              counts_column: int = 1, start_index: int = 0):
        engbin_files = glob(os.path.join(engbin_directory, "engbin*.eb"))
        q_matrix = None
        for i in range(start_index, start_index+len(engbin_files)):
            engbin_spectrum = Spectrum.from_txt(os.path.join(engbin_directory, f"engbin{i}.eb"),
                                                energy_column=energy_column, counts_column=counts_column)
            if q_matrix is None:
                q_matrix = cls(engbin_spectrum.calibration if measurement_calibration is None
                               else measurement_calibration, incident_calibration)
            q_matrix.set_engbin(engbin_spectrum.counts, i - start_index)
        if q_matrix is None:
            raise ValueError(f"No engbins found in {engbin_directory}")
        return q_matrix
