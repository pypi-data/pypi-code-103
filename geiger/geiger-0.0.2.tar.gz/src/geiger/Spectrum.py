from __future__ import annotations

import os
import numpy as np
from datetime import datetime
from typing import Union, List, Tuple, Generator, Iterator, Any
from scipy.stats import norm
import pickle
import matplotlib.pyplot as plt
import struct
import requests

from randdpy.core.Calibration import Calibration
from randdpy.core.BaseClasses import MeasurementBase, TickedMeasurement, ArrayBase, TickedArrayBase
from randdpy.core.Counts import Counts, CountsArray, TickedCounts, TickedCountsArray
from randdpy.Utilities.Multiplot import SpectrumPlotter


class Spectrum(MeasurementBase):
    """
    Class which stores a counts array and calibration for spectra.

    Parameters
    ----------
    energies : numpy.ndarray, Calibration or None
        Energy values for each channel, or energy calibration as a Calibration object. If None, an uncalibrated
        Calibration object is used (with a default of 1024 channels if no count data is provided).
    counts : numpy.ndarray or None
        Count values for each channel. If None, a numpy array of zeros is used, with the same number of channels as
        the energies or Calibration object used.
    live_time : float
        Live time in seconds. Default is 1.0 seconds.
    real_time : float
        Real time in seconds. Default is 1.0 seconds.
    name : str
        Label for the spectrum.
    bin_label : str
        'upper', 'middle' or 'lower'. If 'energies' argument is an energy array, this specifies what part of each
        bin each value labels, otherwise, this argument is ignored.
    comment : str
        Optional comment to attach to the spectrum.
    start_time : datetime or None
        Optional start time for the measurement.

    Attributes
    ----------
    calibration : Calibration
        Energy calibration as a Calibration object.
    counts : numpy.ndarray
        Count values for each channel.
    live_time : float
        Live time in seconds.
    real_time : float
        Real time in seconds.
    name : str
        Label for the spectrum.
    comment : str
        Optional comment to attach to the spectrum.
    start_time : datetime or None
        The time at which the acquisition began

    Methods
    -------
    energies -> np.ndarray
        Property which returns a numpy array of energy values which define the lower bin limits of the energy bins.
    n_channels -> int
        Property which returns the number of channels for the spectrum.
    channel_numbers -> np.ndarray
        Property which returns a numpy array of channel numbers.
    count_rate -> np.ndarray
        Property which returns a numpy array of count rate values for each channel.
    error -> np.ndarray
        Property which returns a numpy array of uncertainties for each channel.
    end_time -> datetime
        Property which returns the time at which the acquisition ended. Requires the start_time attribute to be filled.
    reset_poissonian_errors() -> Spectrum
        Method which rests the errors to the default Poisson values.
    find_channel(energy: float)-> int
        Method which returns the channel number into which a deposit of energy 'energy' would be counted.
    add_counts(energy: float, n_counts: float)
        Method which adds 'n_counts' counts of energy 'energy' to the spectrum.
    get_summed_counts(lower_lim, upper_lim, use_energy) -> Counts
        Method which returns a Counts instance, summed counts from the spectrum. 'lower_lim' and 'upper_lim' set the
        limits in channel numbers, or energies if 'use_energies' is set to True.
    rebin(new_calib: Calibration) -> Spectrum
        Method which rebins the spectrum to a new calibration.
    resample(scale: float = 1.0) -> Spectrum
        Method which uses the current spectrum (scaled by the 'scale' parameters) as the expectation for a new spectrum,
        sampled from either a normal or Poisson distribution.
    subtract_background(background_spectrum: Spectrum, negative: bool = True) -> Spectrum
        Method which subtracts a background spectrum (live time scaled) from the current spectrum, returning a new
        spectrum. The returned spectrum may contain negative values if the 'negative' parameter is True (default), but
        these are set to 0 if 'negative' is set to False.
    consecutive_addition(other: Spectrum) -> Spectrum
        Method which adds Count data to the current Spectrum, equivalent to adding two consecutive measurements
        together, adding their counts and live and real times together.
    simultaneous_addition(other: Spectrum) -> Spectrum
        Method which adds Count data to the current Spectrum, equivalent to adding two simultaneous measurements
        together, adding their counts together, scaling 'other' spectrum to have equal live time.
    consecutive_subtraction(other: Spectrum) -> Spectrum
        Method which subtracts Count data from the current Spectrum, equivalent to subtracting a subsection of a
        measurement. TBH this is never done, but I added the method for completeness.
    simultaneous_subtraction(other: Spectrum) -> Spectrum
        Method which subtracts Count data from the current Spectrum, equivalent to subtracting a signal present
        throughout the measurement, e.g. the background.
    copy_me() -> Spectrum
        Method which returns a deep  copy of the current spectrum.
    broaden(fwhms: np.ndarray) -> Spectrum
        Method which broadens the current spectrum, taking 'fwhms', an array of FWHM values for each channel of the
        spectrum.
    broaden_poly(fwhm_poly: Tuple[float, float, float, float]) -> Spectrum
        Method which broadens the current spectrum, using a polynomial (whose coefficients are given by the 'fwhm_poly'
        parameter). The equation is given by FWHM(E) = c0 + c1*E + c2*E**2 + c3*E**3.
    broaden_exp(fwhm_exp: Tuple[float, float, float]) -> Spectrum
        Method which broadens the current spectrum, using an exponential equation (whose coefficients are given by the
        'fwhm_exp' parameter). The equation is given by FWHM(E) = c0 + c1*E**c2.
    plot(*other_spectra: Spectrum, **kwargs)
        Method which plots the current spectrum and any other spectra passed as positional arguments. Keyword arguments
        are passed to the Multiplotter class.
    save(filename: str)
        Method which saves the current spectrum, using pickle, to the file name passed as an argument.
    load(filename: str) -> Spectrum
        Class method which loads a spectrum saved using the save() method above.
    from_txt(filename: str, **kwargs) -> Spectrum
        Class method which loads a spectrum in a txt file with energy and counts columns. Keyword arguments are passed
        to numpy.load_txt method which reads the file.
    """
    def __init__(self,
                 energies: Union[np.ndarray, Calibration, None] = None,
                 counts: Union[np.ndarray, None] = None,
                 live_time: float = 1.,
                 real_time: float = 1.,
                 error: Union[np.ndarray, None] = None,
                 name: str = '',
                 bin_label: str = 'lower',
                 comment: str = '',
                 start_time: Union[datetime, None] = None):
        """
        """
        if counts is None:
            if energies is None:
                self.calibration = Calibration.channel_numbers_only(1024)
            elif isinstance(energies, Calibration):
                self.calibration = energies
            elif isinstance(energies, np.ndarray):
                self.calibration = Calibration.from_energies(energies, bin_label)
            self.counts = np.zeros(self.calibration.n_channels)
        else:
            if energies is None:
                self.calibration = Calibration.channel_numbers_only(counts.size)
            elif isinstance(energies, Calibration):
                self.calibration = energies
            elif isinstance(energies, np.ndarray):
                self.calibration = Calibration.from_energies(energies, bin_label)
            self.counts = counts
        assert self.counts.size == self.calibration.n_channels

        if error is not None:
            assert error.size == self.n_channels

        self._error = error
        super(Spectrum, self).__init__(live_time=live_time, real_time=real_time, name=name, comment=comment,
                                       start_time=start_time)

    @property
    def energies(self) -> np.ndarray:
        """
        Property which returns a numpy array of energy values which define the lower bin limits of the energy bins.

        Returns
        -------
        np.ndarray
        """
        return self.calibration.energies

    @property
    def n_channels(self) -> int:
        """
        Property which returns the number of channels for the spectrum.

        Returns
        -------
        int
        """
        return self.calibration.n_channels

    @property
    def channel_numbers(self) -> np.ndarray:
        """
        Property which returns a numpy array of channel numbers.

        Returns
        -------
        np.ndarray
        """
        return self.calibration.channel_numbers

    @property
    def count_rate(self) -> np.ndarray:
        """
        Property which returns a numpy array of count rate values for each channel.

        Returns
        -------
        np.ndarray
        """
        return self.counts / self.live_time

    @property
    def error(self) -> np.ndarray:
        """
        Property which returns a numpy array of uncertainties for each channel.

        Returns
        -------
        np.ndarray
        """
        if self._error is None:
            assert (self.counts >= 0.).all()
            self._error = self.counts**0.5
            self.log.debug("Using Poisson errors")
        return self._error

    def reset_poissonian_errors(self) -> Spectrum:
        """
        Method which rests the errors to the default Poisson values.

        Errors inherited from convolution processes may be non-Poissonian.
        If we want to assume Poisson errors, call this method.

        Returns
        -------
        None
        """
        self._error = None
        return self

    def find_channel(self, energy: float) -> int:
        """
        Method which returns the channel number into which a deposit of energy 'energy' would be counted.

        Parameters
        ----------
        energy : float
            Energy of the deposit

        Returns
        -------
        int
        """
        return self.calibration.find_channel(energy)

    def add_counts(self, energy: float, n_counts: float = 1.0):
        """
        Method which adds 'n_counts' counts of energy 'energy' to the spectrum.

        Parameters
        ----------
        energy : float
            Energy of the deposit
        n_counts : int
            Number of deposits
        Returns
        -------
        None
        """
        channel = self.find_channel(energy)
        if channel is None:
            return
        self.counts[channel] += n_counts

    def get_summed_counts(self,
                          lower_lim: Union[int, float, None] = None,
                          upper_lim: Union[int, float, None] = None,
                          use_energy: bool = False
                          ) -> Counts:
        """
        Method which returns the total number of counts in the spectrum with optional upper and lower channel limits.
        The upper and lower limits can be specified as energy values if the 'use_energy' parameter is set to True.

        Parameters
        ----------
        lower_lim : int or float
            Lower channel (or lower energy) limit for count sum. Optional. Int by default. Float if using energy units.
        upper_lim : int or float
            Upper channel  (or lower energy) limit for count sum. Optional. Int by default. Float if using energy units.
        use_energy : bool
            Boolean switch determining whether energy units used in channel limiting.

        Returns
        -------
        Counts
        """

        c_mask = np.ones(self.n_channels, dtype=bool)
        if use_energy:
            if lower_lim is None:
                lower_lim = 0.
            if upper_lim is None:
                upper_lim = self.energies[-1] + self.calibration.coefficients[1]
            e0 = lower_lim
            de = upper_lim - lower_lim
            cal = Calibration(1, [e0, de, 0.])
            s = self.copy_me().rebin(cal)
            return s.get_summed_counts()
        if lower_lim is not None:
            c_mask = np.logical_and(c_mask, np.arange(self.n_channels) >= lower_lim)
        if upper_lim is not None:
            c_mask = np.logical_and(c_mask, np.arange(self.n_channels) < upper_lim)
        return Counts(self.counts[c_mask].sum(),
                      live_time=self.live_time,
                      real_time=self.real_time,
                      start_time=self.start_time,
                      error=np.sqrt(np.square(self.error[c_mask]).sum()),
                      name=self.name,
                      comment=self.comment)

    def rebin(self, new_calibration: Calibration) -> Spectrum:
        """
        Function which rebins spectrum with new calibration coefficients and number of channels.

        Parameters
        ----------
        new_calibration : Calibration
            Calibration of required rebinned spectrum.

        Returns
        -------
        new_spectrum : Spectrum
            Rebinned spectrum with calibration equal to 'new_calibration'.
        """

        # Get upper and lower energy values for each current channel
        energies_upper = self.calibration.upper_bin_limits
        energies_lower = self.calibration.lower_bin_limits

        # Get upper and lower energy values for each new channel
        new_energies_upper = new_calibration.upper_bin_limits
        new_energies_lower = new_calibration.lower_bin_limits

        # Generate empty array for new counts
        new_spectrum = self.copy_me()
        new_spectrum.calibration = new_calibration
        new_spectrum.counts = np.zeros(new_calibration.n_channels)
        new_spectrum._error = None if self._error is None else np.zeros(new_calibration.n_channels)

        # Check there will be counts in the new spectrum
        assert self.energies[0] < new_energies_upper[-1] and self.energies[-1] > new_energies_upper[0]

        zeros = np.zeros(new_calibration.n_channels)
        # Distribute the counts in each channel to the new spectrum
        for channel in range(self.n_channels):
            w_max = energies_upper[channel]
            w_min = energies_lower[channel]

            energy_overlap = np.maximum(np.minimum(new_energies_upper, w_max) -
                                        np.maximum(new_energies_lower, w_min),
                                        zeros)
            new_spectrum.counts += self.counts[channel] * energy_overlap / (w_max - w_min)
            if self._error is not None:
                new_spectrum._error += self._error[channel]**2 * energy_overlap / (w_max - w_min)

        if self._error is not None:
            new_spectrum._error = np.sqrt(new_spectrum._error)

        # Return the new spectrum
        return new_spectrum

    def resample(self, factor: float = 1.0) -> Spectrum:
        """
        Method which uses the current spectrum (scaled by the 'scale' parameters) as the expectation for a new spectrum,
        sampled from either a normal or Poisson distribution.

        Parameters
        ----------
        factor : float
            Multiplication factor for the expectations of the new spectral counts.

        Returns
        -------
        new_spectrum : Spectrum
            The resampled spectrum
        """
        new_spectrum = self.copy_me()
        if self._error is None:
            new_spectrum.counts[self.counts >= 0.] = np.random.poisson(self.counts[self.counts >= 0.]*factor)
        else:
            error = np.sqrt(np.square(self.error)*factor)
            new_spectrum.counts = np.random.normal(self.counts*factor, error)
            new_spectrum.counts[new_spectrum.counts < 0.] = 0.
            new_spectrum._error = error
        return new_spectrum

    def subtract_background(self, bg_spec: Spectrum, negative: bool = False) -> Spectrum:
        """
        Function which takes a background spectrum and subtracts it, scaled by the correct live time.

        Parameters
        ----------
        bg_spec : Spectrum class instance
            Background spectrum to be subtracted.
        negative : bool
            If set to False, the function sets all negative values in the subtracted spectrum to zero. Default: False.

        Returns
        -------
        Spectrum
        """
        sub = self.simultaneous_subtraction(bg_spec)
        if not negative:
            sub.counts[sub.counts < 0.] = 0.
        return sub

    def _check_other_spectrum(self, other: Spectrum) -> Spectrum:
        if other.calibration != self.calibration:
            other = other.rebin(self.calibration)
        return other

    def consecutive_addition(self, other: Spectrum) -> Spectrum:
        """
        Method which adds Count data to the current Spectrum, equivalent to adding two consecutive measurements
        together, adding their counts and live and real times together.

        Parameters
        ----------
        other : Spectrum
            Spectrum which should be added.

        Returns
        -------
        Spectrum
        """
        other = self._check_other_spectrum(other)
        return Spectrum(self.calibration, self.counts + other.counts,
                        live_time=self.live_time + other.live_time,
                        real_time=self.real_time + other.real_time,
                        start_time=self.start_time,
                        comment=self.comment,
                        error=np.sqrt(np.square(self.error) + np.square(other.error)),
                        name=self.name)

    def simultaneous_addition(self, other: Spectrum) -> Spectrum:
        """
        Method which adds Count data to the current Spectrum, equivalent to adding two simultaneous measurements
        together, adding their counts together, scaling 'other' spectrum to have equal live time.

        Parameters
        ----------
        other : Spectrum
            Spectrum which should be added

        Returns
        -------
        Spectrum
        """
        other = self._check_other_spectrum(other)
        scale = self.live_time / other.live_time
        return Spectrum(self.calibration,
                        self.counts + other.counts*scale,
                        live_time=self.live_time, real_time=self.real_time,
                        start_time=self.start_time,
                        comment=self.comment,
                        error=np.sqrt(np.square(self.error) + np.square(other.error*scale)),
                        name=self.name)

    def consecutive_subtraction(self, other: Spectrum) -> Spectrum:
        """
        Method which subtracts Count data from the current Spectrum, equivalent to subtracting a subsection of a
        measurement. TBH this is never done, but I added the method for completeness.

        Parameters
        ----------
        other : Spectrum
            Spectrum to be subtracted.

        Returns
        -------
        Spectrum
        """
        other = self._check_other_spectrum(other)
        return Spectrum(self.calibration, self.counts-other.counts,
                        live_time=self.live_time-other.live_time,
                        real_time=self.real_time-other.real_time,
                        start_time=self.start_time,
                        comment=self.comment,
                        error=np.sqrt(np.square(self.error) + np.square(other.error)),
                        name=self.name)

    def simultaneous_subtraction(self, other: Spectrum) -> Spectrum:
        """
        Method which subtracts Count data from the current Spectrum, equivalent to subtracting a signal present
        throughout the measurement, e.g. the background.

        Parameters
        ----------
        other : Spectrum
            Spectrum to be subtracted

        Returns
        -------
        Spectrum
        """
        other = self._check_other_spectrum(other)
        scale = self.live_time / other.live_time
        return Spectrum(self.calibration,
                        self.counts - other.counts*scale,
                        live_time=self.live_time, real_time=self.real_time,
                        start_time=self.start_time,
                        comment=self.comment,
                        error=np.sqrt(np.square(self.error) + np.square(other.error*scale)),
                        name=self.name)

    def __broaden(self, sigmas: np.ndarray) -> Spectrum:
        """
        Broaden spectrum with sigma (gaussian standard deviation) values in units of n_channels numbers for each
        channel.

        Parameters
        ----------
        sigmas : numpy.ndarray
            Array of sigma values.

        Returns
        -------
        Spectrum
        """

        def normal_dist(mu, sig, num):
            x = np.arange(num + 1)
            cdf = norm.cdf(x - 0.5, loc=mu, scale=sig)
            return cdf[1:] - cdf[:-1]

        assert isinstance(sigmas, np.ndarray)
        assert sigmas.size == self.n_channels

        new_spectrum = Spectrum(self.calibration, live_time=self.live_time, real_time=self.real_time, name=self.name)
        for ch, sigma in enumerate(sigmas):
            broad = normal_dist(ch, sigma, self.n_channels)
            new_spectrum.counts += self.counts[ch] * broad
        return new_spectrum

    def broaden(self, fwhms: np.ndarray) -> Spectrum:
        """
        Method which broadens the current spectrum, using an exponential equation (whose coefficients are given by the
        'fwhm_exp' parameter). The equation is given by FWHM(E) = c0 + c1*E**c2.

        Parameters
        ----------
        fwhms : numpy.ndarray
            Array of fwhm values.

        Returns
        -------
        Spectrum
        """
        assert isinstance(fwhms, np.ndarray)
        assert fwhms.size == self.n_channels

        delta_e = self.calibration.bin_widths
        sigmas = np.absolute(fwhms / (2.35 * delta_e))
        return self.__broaden(sigmas)

    def broaden_poly(self, fwhm_poly: Union[List, Tuple, np.ndarray]) -> Spectrum:
        """
        Method which broadens the current spectrum, using a polynomial (whose coefficients are given by the 'fwhm_poly'
        parameter). The equation is given by FWHM(E) = c0 + c1*E + c2*E**2 + c3*E**3.

        Parameters
        ----------
        fwhm_poly : numpy.ndarray, tuple or list
            Coefficients for broadening function.
        """
        assert len(fwhm_poly) == 4

        powers = np.arange(4)[np.newaxis, :]
        fwhms = (np.array(fwhm_poly)[np.newaxis, :] * np.power(self.energies[:, np.newaxis], powers)).sum(axis=1)
        new_spectrum = self.broaden(fwhms)
        new_spectrum.comment += "Broadened with polynomial coefficients: {}, {}, {}, {}; ".format(*fwhm_poly)
        return new_spectrum

    def broaden_exp(self, fwhm_exp: Union[List, Tuple, np.ndarray]) -> Spectrum:
        """
        Method which broadens the current spectrum, using an exponential equation (whose coefficients are given by the
        'fwhm_exp' parameter). The equation is given by FWHM(E) = c0 + c1*E**c2.

        Parameters
        ----------
        fwhm_exp : numpy.ndarray or list
            Coefficients for broadening function.

        Returns
        -------
        Spectrum
        """
        assert len(fwhm_exp) == 3

        fwhms = np.zeros(self.energies.size)
        fwhms[self.energies >= 0.] += fwhm_exp[1] * np.power(self.energies[self.energies >= 0.], fwhm_exp[2])
        fwhms += fwhm_exp[0]
        new_spectrum = self.broaden(fwhms)
        new_spectrum.comment += "Broadened with exponential coefficients: {}, {}, {}; ".format(*fwhm_exp)
        return new_spectrum

    def plot(self, *other_spectra: Spectrum, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """
        Method which plots the current spectrum and any other spectra passed as positional arguments. Keyword arguments
        are passed to the Multiplotter class.

        Parameters
        ----------
        other_spectra : Spectrum
            Other spectra to be plotted.
        kwargs : Keyword Arguments
            These will be passed to the Multiplotter class.

        Returns
        -------
        Pyplot figure and axes
        """
        return SpectrumPlotter(spectra=[self, *other_spectra], **kwargs).plot()

    def save(self, file_name: str):
        """
        Method which saves the current spectrum, using pickle, to the file name passed as an argument.

        Parameters
        ----------
        file_name : str
            The file name to which the spectrum will be saved.

        Returns
        -------
        None
        """
        calib_less_dict = dict((k, v) for k, v in self.__dict__.items() if k != 'calibration')
        with open(file_name, 'wb') as f:
            pickle.dump((self.calibration.__dict__, calib_less_dict), f)

    @classmethod
    def load(cls, file_name: str) -> Spectrum:
        """
        Class method which loads a spectrum saved using the save() method above.

        Parameters
        ----------
        file_name : str
            File name of the pickled spectrum.

        Returns
        -------
        Spectrum
        """
        with open(file_name, 'rb') as f:
            calib_dict, spec_dict = pickle.load(f)
        if 'n_channels' not in calib_dict:
            n_channels = calib_dict['channels']
        else:
            n_channels = calib_dict['n_channels']
        if 'coefficients' not in calib_dict:
            spec = cls(Calibration(n_channels, calib_dict['coeffs']))
        else:
            spec = cls(Calibration(calib_dict['n_channels'], calib_dict['coefficients']))
        spec.__dict__.update(spec_dict)
        return spec

    @classmethod
    def from_txt(cls, file_name: str, **kwargs) -> Spectrum:
        """
        Class method which generates a Spectrum object from counts and energy values in an ASCII text file.

        Parameters
        ----------
        file_name : str
            File name of text file.

        Other Parameters
        ----------------
        energy_column : int
            Column number of energy values. Optional, default = 0
        counts_column : int
            Column number of count values. Optional, default = 1
        skiprows : int
            Number of rows to be skipped at the top of the file. Optional,
            default = 0
        delim : str
            Delimiter of the columns in the ascii file. Optional, default is
            same as that of numpy.loadtxt function.
        """
        kwlib = dict(energy_column=0, counts_column=1, skiprows=0, calib=None, delim=None)
        kwlib.update(kwargs)
        e, c = np.loadtxt(file_name, delimiter=kwlib["delim"],
                          skiprows=kwlib["skiprows"],
                          usecols=(kwlib["energy_column"],
                                   kwlib["counts_column"])).T

        return cls(e, c, name=file_name.split("\\")[-1].split("/")[-1])


class EmissionSpectrum:
    @classmethod
    def from_lara_decay_data_file(cls,
                                  filename: str,
                                  calibration: Calibration = Calibration(1024, (0., 3., 0.))) -> Spectrum:
        """
        Class method which generates an emission spectrum for a specific
        isotope using data saved in the .lara format. E.g. available at
            http://www.nucleide.org/DDEP_WG/DDEPdata.htm

        Parameters
        ----------
        filename : str
            Filename of the .lara file to read
        calibration : Calibration
            Calibration instance specifying the calibration of the generated spectrum.
            Optional, default n_channels=1024, coeffs=(0., 3., 0.)

        Returns
        -------
            Spectrum object
        """
        with open(filename) as f:
            spectrum = cls._from_lara_decay_data(f.read().splitlines(), calibration)
        spectrum.comment = "Emission spectrum generated from: " + os.path.basename(filename)
        return spectrum

    @classmethod
    def from_lara_online(cls,
                         isotope: str = "Cs-137",
                         calibration: Calibration = Calibration(1024, [0., 3., 0.])) -> Spectrum:
        """
        Class method which generates an emission spectrum for a specific isotope using data collected from laraweb.

        Parameters
        ----------
        isotope : str
            Isotope in the format "Cs-137".
        calibration : Calibration
            Calibration for the generated spectrum.

        Returns
        -------
        Spectrum
        """
        data = requests.get(f"http://www.nucleide.org/Laraweb/Results/{isotope}.txt")
        return cls._from_lara_decay_data(data.text.splitlines(), calibration)

    @classmethod
    def _from_lara_decay_data(cls, data_lines: List[str], calibration: Calibration = Calibration(1024, [0., 3., 0.])):
        e = []
        i = []
        nuclide = (f"{data_lines.pop(0).split(';')[-1].strip()} "
                   f"({data_lines.pop(0).split(';')[-1].strip()}, "
                   f"Z = {data_lines.pop(0).split(';')[-1].strip()})")
        while " (keV) ; " not in data_lines.pop(0):
            pass
        while 1:
            line = data_lines.pop(0)
            if line.startswith("="):
                break
            line = line.replace(',', '.').split(" ; ")
            if line[4].startswith("g") or line[4].startswith("X"):
                e.append(float(line[0]))
                i.append(float(line[2]) / 100.)

        counts = np.zeros(calibration.n_channels)
        for j in range(len(e)):
            channel = calibration.find_channel(e[j])
            if channel is not None:
                counts[channel] += i[j]
        return Spectrum(calibration, counts, name=nuclide)


class MaestroSpectrum:
    @classmethod
    def chn_to_spectrum(cls, filename: str) -> Spectrum:
        """
        Class method which generates a Spectrum object from a Maestro .chn file.

        Parameters
        ----------
        filename : str
            Filename of the .chn file to read.
        """
        header_shape = '3h 2s 2i 8s 4s 2h'
        tail_shape = '2h 6f 228s B 63s B 63s 128s'

        with open(filename, 'rb') as f:
            header = struct.unpack(header_shape, f.read(32))
            spec = np.array(struct.unpack(f'{header[9]}i', f.read(4 * header[9])))
            info = struct.unpack(tail_shape, f.read(512))

        calibration = Calibration(header[9], (info[2], info[3], info[4]))
        return Spectrum(calibration, spec, live_time=header[5] * 0.02, real_time=header[4] * 0.02,
                        name=os.path.basename(filename))


class SpectrumArray(ArrayBase):
    """
    An array of Spectrum instances.

    Parameters
    ----------
    spectra : List[Spectrum]
        List of spectra to add to the array.

    Attributes
    ----------
    elements : OrderedDict[str, Spectrum]
        OrderedDict, mapping measurements by their names.

    Methods
    -------
    names() -> List[str]
        Property which returns a list of the measurement names which are keys to the mapping.
    number_of_members() -> int
        Property which returns the number of members of the array.
    start_times() -> List[datetime]
        Property which returns a list of datetime instances which give the times at which each member of the array
        began to be collected.
    contains_all(names: List[str]) -> bool
        Method which returns True if all the strings in the argument match the names of elements in the array.
    names_match(other: ArrayBase) -> bool
        Method which returns True if all the names of the other array are present in this array, and vice-versa.
    consecutive_addition(other: SpectrumArray) -> SpectrumArray
        Method which returns the consecutive sum of the CountsArray with another Array.
    simultaneous_addition(other: SpectrumArray) -> SpectrumArray
        Method which returns the simultaneous sum of the CountsArray with another Array.
    consecutive_subtraction(other: SpectrumArray) -> SpectrumArray
        Method which returns the consecutive subtraction of another CountsArray from the Array.
    simultaneous_subtraction(other: SpectrumArray) -> SpectrumArray
        Method which returns the simultaneous subtraction of another CountsArray from the Array.
    subtract_backgrounds(backgrounds: SpectrumArray) -> SpectrumArray:
        Method which subtracts the background from each member of the array, using the array of background counts
        supplied as the argument.
    simultaneous_sum() -> Spectrum
        Simultaneously sum all members of the array.
    consecutive_sum() -> Spectrum
        Consecutive sum of all members of the array.
    resample(factor: float) -> SpectrumArray
        Method which returns a new array with each member resampled after scaling by the factor parameter.
    masked_array(names: List[str]) -> SpectrumArray
        Method which returns a new array consisting only of members with the names in the given list of names.
    summed_counts_array(lower_lim: Union[int, float, None] = None,
                        upper_lim: Union[int, float, None] = None,
                        use_energy: bool = False) -> CountsArray
        Convert the SpectrumArray into a CountsArray, with optional upper and lower channel or energy bounds.
    plot(**kwargs):
        Plot the spectra on the same axes.
    """
    def __init__(self, spectra: List[Spectrum]):
        """
        """
        super(SpectrumArray, self).__init__(spectra)

    def __getitem__(self, item: str) -> Spectrum:
        return super(SpectrumArray, self).__getitem__(item)

    def get(self, item: str, default_val: Any = Spectrum()) -> Spectrum:
        return super().get(item, default_val)

    def __iter__(self) -> Iterator[Spectrum]:
        return super(SpectrumArray, self).__iter__()

    def consecutive_addition(self, other: SpectrumArray) -> SpectrumArray:
        """
        Consecutively add a SpectrumArray to this one.

        Parameters
        ----------
        other : SpectrumArray

        Returns
        -------
        SpectrumArray
        """
        return super(SpectrumArray, self).consecutive_addition(other)

    def consecutive_subtraction(self, other: SpectrumArray) -> SpectrumArray:
        """
        Consecutively subtract a SpectrumArray from this one.

        Parameters
        ----------
        other : SpectrumArray

        Returns
        -------
        SpectrumArray
        """
        return super(SpectrumArray, self).consecutive_subtraction(other)

    def simultaneous_addition(self, other: SpectrumArray) -> SpectrumArray:
        """
        Simultaneously add a SpectrumArray to this one.

        Parameters
        ----------
        other : SpectrumArray

        Returns
        -------
        SpectrumArray
        """
        return super(SpectrumArray, self).simultaneous_addition(other)

    def simultaneous_subtraction(self, other: SpectrumArray) -> SpectrumArray:
        """
        Simultaneously subtract a SpectrumArray from this one.

        Parameters
        ----------
        other: SpectrumArray

        Returns
        -------
        SpectrumArray
        """
        return super(SpectrumArray, self).simultaneous_subtraction(other)

    def simultaneous_sum(self, calibration: Calibration = None) -> Spectrum:
        """
        Simultaneously sum all members of the array.

        Parameters
        ----------
        calibration : Optional[Calibration]
            Calibration to use for the summed spectrum. If not specified, the first member of the array's calibration
            will be used.

        Returns
        -------
        Spectrum
        """
        if self.number_of_members == 0:
            return Spectrum(energies=calibration)
        if calibration is None:
            calibration = list(self.elements.values())[0].calibration
        spec = 0
        for s in self:
            if spec == 0:
                spec = s.rebin(calibration)
            else:
                spec = spec.simultaneous_addition(s)
        spec.name = ', '.join(self.names)
        return spec

    def consecutive_sum(self, calibration: Calibration = None) -> Spectrum:
        """
        Consecutive sum of all members of the array.

        Parameters
        ----------
        calibration : Optional[Calibration]
            Calibration to use for the summed spectrum. If not specified, the first member of the array's calibration
            will be used.

        Returns
        -------
        Spectrum
        """
        if self.number_of_members == 0:
            return Spectrum(energies=calibration)
        if calibration is None:
            calibration = list(self.elements.values())[0].calibration
        spec = 0
        for s in self:
            if spec == 0:
                spec = s.rebin(calibration)
            else:
                spec = spec.consecutive_addition(s)
        spec.name = ', '.join(self.names)
        return spec

    def summed_counts_array(self,
                            lower_lim: Union[int, float, None] = None,
                            upper_lim: Union[int, float, None] = None,
                            use_energy: bool = False
                            ) -> CountsArray:
        """
        Convert the SpectrumArray into a CountsArray, with optional upper and lower channel or energy bounds.

        Parameters
        ----------
        lower_lim : int or float
            Optional channel (default) or energy for lower bound of the sum.
        upper_lim : int or float
            Optional channel (default) or energy for upper bound of the sum.
        use_energy : bool
            Use energy values for the bounds, rather than channel number.

        Returns
        -------
        CountsArray
        """
        counts = [spec.get_summed_counts(lower_lim=lower_lim, upper_lim=upper_lim, use_energy=use_energy)
                  for spec in self]
        return CountsArray(counts)

    def plot(self, **kwargs):
        """
        Plot the spectra on the same axes.

        Parameters
        ----------
        kwargs
            Keyword arguments to pass to Multiplotter class.

        Returns
        -------
        plt.Figure, plt.Axes
        """
        return SpectrumPlotter(spectra=list(self.elements.values()), **kwargs).plot()

    def resample(self, factor: float) -> SpectrumArray:
        """
        Method which returns a new array with each member resampled after scaling by the factor parameter.

        Parameters
        ----------
        factor : float
            Scale by which the measurements will be scaled before resampling.

        Returns
        -------
        Array
        """
        return super(SpectrumArray, self).resample(factor)


class WindowSpectrumArray(SpectrumArray):
    """
    An array of Spectrum instances, generated by a rolling window.

    Parameters
    ----------
    spectra : List[Spectrum]
        List of spectra to add to the array.
    time : datetime
        Time label associated to the window.
    width : int
        Length of the window in ticks.

    Attributes
    ----------
    elements : OrderedDict[str, Spectrum]
        OrderedDict, mapping measurements by their names.
    time : datetime
        Time label associated to the window.
    window_width : int
        Length of the window in ticks.

    Methods
    -------
    names() -> List[str]
        Property which returns a list of the measurement names which are keys to the mapping.
    number_of_members() -> int
        Property which returns the number of members of the array.
    start_times() -> List[datetime]
        Property which returns a list of datetime instances which give the times at which each member of the array
        began to be collected.
    contains_all(names: List[str]) -> bool
        Method which returns True if all the strings in the argument match the names of elements in the array.
    names_match(other: ArrayBase) -> bool
        Method which returns True if all the names of the other array are present in this array, and vice-versa.
    consecutive_addition(other: SpectrumArray) -> SpectrumArray
        Method which returns the consecutive sum of the CountsArray with another Array.
    simultaneous_addition(other: SpectrumArray) -> SpectrumArray
        Method which returns the simultaneous sum of the CountsArray with another Array.
    consecutive_subtraction(other: SpectrumArray) -> SpectrumArray
        Method which returns the consecutive subtraction of another CountsArray from the Array.
    simultaneous_subtraction(other: SpectrumArray) -> SpectrumArray
        Method which returns the simultaneous subtraction of another CountsArray from the Array.
    subtract_backgrounds(backgrounds: SpectrumArray) -> SpectrumArray:
        Method which subtracts the background from each member of the array, using the array of background counts
        supplied as the argument.
    simultaneous_sum() -> Spectrum
        Simultaneously sum all members of the array.
    consecutive_sum() -> Spectrum
        Consecutive sum of all members of the array.
    resample(factor: float) -> SpectrumArray
        Method which returns a new array with each member resampled after scaling by the factor parameter.
    masked_array(names: List[str]) -> SpectrumArray
        Method which returns a new array consisting only of members with the names in the given list of names.
    summed_counts_array(lower_lim: Union[int, float, None] = None,
                        upper_lim: Union[int, float, None] = None,
                        use_energy: bool = False) -> CountsArray
        Convert the SpectrumArray into a CountsArray, with optional upper and lower channel or energy bounds.
    plot(**kwargs):
        Plot the spectra on the same axes.
    """
    def __init__(self, spectra: List[Spectrum], time: datetime, width: int = -1):
        super().__init__(spectra)

        # 'Time' label for the window
        self.time = time
        self.window_width = width


class TickedSpectrum(TickedMeasurement):
    """
    Spectrum class with ticks.

    Parameters
    ----------
    energies : numpy.ndarray, Calibration or None
        Energy values for each channel, or energy calibration as a Calibration object. If None, an uncalibrated
        Calibration object is used (with a default of 1024 channels if no count data is provided).
    tick_times : Array[datetime]
        Numpy array of datetime objects, labelling the times at which the ticks occurred.
    ticks : 2DArray[float]
        Counts in each energy bin for each tick.



    Attributes
    ----------
    ticks : 2DArray[float]
        Counts in each energy bin for each tick.
    calibration : Calibration
        Energy calibration as a Calibration object.
    tick_times : Array[datetime]
        Numpy array of datetime objects, labelling the times at which the ticks occurred.
    live_times : Array[float]
        Numpy array of floats, determining the live times of each tick.
    real_times : Array[float]
        Numpy array of floats, determining the real times of each tick.
    msg_times : np.ndarray
        Possible array of datetime instances, marking the times at which the tick messages arrived.
    blank_rate : np.ndarray
        Possible array of floats, marking the rate of blanking pulses measured during each tick.
    live_time : float
        The total live time of the measurement
    real_time : float
        The total real time of the measurement
    name : str
        Optional name to attach to the measurement.
    comment : str
        Optional comment to attach to the measurement.
    start_time : datetime
        Optional time at which the measurement began.
    log : logging.Logger
        Logger for logging loggable log logs.

    Methods
    -------
    energies() -> np.ndarray
        Property which returns the lower energy bound foreach channel in the spectrum.
    n_channels() -> int
        Property which returns the number of channels in each spectrum per tick.
    errors() -> np.ndarray
        Property which returns the uncertainties for each channel of each tick.
    n_ticks() -> int
        Property which returns the number of ticks in the measurement.
    end_time() -> datetime or None
        Property returning the end time of the measurement. "The end times are nigh."
    copy_me() -> TickedSpectrum
        Method which returns a deep copy of the measurement.
    resample(factor: float = 1.0) -> TickedSpectrum
        Must be implemented by subclasses.
    subtract_background(background: Spectrum) -> TickedSpectrum
        Method which subtracts a background signal from the measurement.
    consecutive_addition(other: TickedSpectrum) -> TickedSpectrum
        Method which consecutively sums another TickedSpectrum instance to this one.
    simultaneous_addition(other: Spectrum) -> TickedSpectrum
        Method which simultaneously sums a Spectrum or another TickedSpectrum to this TickedSpectrum.
    consecutive_subtraction(other: MeasurementBase) -> Measurement
        This method cannot be used for ticked types. Raises TypeError always.
    simultaneous_subtraction(other: Spectrum) -> TickedSpectrum
        Method which simultaneously subtracts a Spectrum or another TickedSpectrum from this TickedSpectrum.
    get_single_tick(tick_number: int) -> Spectrum
        Method which retrieves a single tick.
    sum_ticks(start: datetime = None, end: datetime = None) -> Spectrum
        Method which returns a summed spectrum with optional start and end
        times.
    get_ticked_counts(lower_lim: float = None, upper_lim: float = None, start: datetime = None, end: datetime = None,
                      use_energy: bool = False) -> TickedCounts
        Method which sums channels in each tick's spectrum to make a TickedCounts instance.
    simple_windowed_spectra_iterations(tick_window_width: int = 1, mode: int = 0) -> int
        Method which calculates the number of iterations for a rolling window of a given length and mode.
    simple_windowed_spectra(tick_window_width: int = 1, mode: int = 0) -> Generator[Spectrum]
        Simple generator of variable length windowed spectra, equivalent to a rolling window across the time space
    resample(factor: float = 1.0) -> TickedSpectrum
        Method which uses the current spectrum (scaled by the 'scale' parameters) as the expectation for a new spectrum,
        sampled from either a normal or Poisson distribution.
    rebin(new_calibration: Calibration) -> TickedSpectrum
        Function which rebins spectrum with new calibration coefficients and number of channels.
    """
    def __init__(self,
                 energies: Union[np.ndarray, Calibration],
                 tick_times: np.ndarray,
                 ticks: np.ndarray,
                 live_times: Union[np.ndarray, None] = None,
                 real_times: Union[np.ndarray, None] = None,
                 errors: Union[np.ndarray, None] = None,
                 name: str = '',
                 bin_label: str = 'lower',
                 comment: str = '',
                 start_time: Union[datetime, None] = None,
                 msg_times: Union[np.ndarray, None] = None,
                 blank_rate: Union[np.ndarray, None] = None):

        if live_times is None:
            n_gaps = (tick_times.size - 1)
            live_times = np.ones(tick_times.size) * (tick_times[-1] - tick_times[0]).total_seconds() / n_gaps
        if real_times is None:
            real_times = live_times

        super().__init__(tick_times=tick_times, live_times=live_times, real_times=real_times, name=name,
                         comment=comment, start_time=start_time)

        if energies is None:
            self.calibration = Calibration.channel_numbers_only(ticks.shape[1])
        elif isinstance(energies, Calibration):
            self.calibration = energies
        elif isinstance(energies, np.ndarray):
            self.calibration = Calibration.from_energies(energies, bin_label)
        self.ticks = ticks
        self.blank_rate = blank_rate
        self.msg_times = msg_times
        self._errors = errors

    @property
    def energies(self) -> np.ndarray:
        """
        Property which returns the lower energy bound foreach channel in the spectrum.

        Returns
        -------
        np.ndarray
        """
        return self.calibration.energies

    @property
    def n_channels(self) -> int:
        """
        Property which returns the number of channels in each spectrum per tick.

        Returns
        -------
        int
        """
        return self.calibration.n_channels

    @property
    def errors(self) -> np.ndarray:
        """
        Property which returns the uncertainties for each channel of each tick.

        Returns
        -------
        np.ndarray
        """
        if self._errors is None:
            assert (self.ticks >= 0.).all()
            self._errors = self.ticks**0.5
            self.log.debug("Using Poisson errors")
        return self._errors

    def get_single_tick(self, tick_number: int) -> Spectrum:
        """
        Method which retrieves a single tick.

        Parameters
        ----------
        tick_number : int
            Index of the tick to be retrieved.

        Returns
        -------
        Spectrum
        """
        return Spectrum(self.calibration, self.ticks[tick_number],
                        live_time=self.live_times[tick_number], real_time=self.real_times[tick_number],
                        error=self.errors[tick_number], name=self.name, comment=self.comment)

    def sum_ticks(self,
                  start: Union[datetime, None] = None,
                  end: Union[datetime, None] = None) -> Spectrum:
        """
        Method which returns a summed spectrum with optional start and end
        times.

        Parameters
        ----------
        start : datetime
            Start time for the spectrum sum. Optional.
        end : datetime
            End time for the spectrum sum. Optional.

        Returns
        -------
        Spectrum
        """
        t_mask = np.ones(self.tick_times.size, dtype=bool)
        if start is not None:
            t_mask = np.logical_and(t_mask, self.tick_times >= start)
        if end is not None:
            t_mask = np.logical_and(t_mask, self.tick_times < end)
        return Spectrum(self.calibration,
                        self.ticks[t_mask].sum(axis=0),
                        name=self.name,
                        live_time=self.live_times[t_mask].sum(),
                        real_time=self.real_times[t_mask].sum(),
                        error=np.sqrt(np.square(self.errors[t_mask]).sum(axis=0)),
                        comment=self.comment, start_time=self.start_time)

    def get_ticked_counts(self,
                          lower_lim: Union[int, float, None] = None,
                          upper_lim: Union[int, float, None] = None,
                          start: Union[datetime, None] = None,
                          end: Union[datetime, None] = None,
                          use_energy: bool = False) -> TickedCounts:
        """
        Method which sums channels in each tick's spectrum to make a TickedCounts instance.

        Parameters
        ----------
        lower_lim : int or float
            Optional channel (default) or energy for lower bound of the sum.
        upper_lim : int or float
            Optional channel (default) or energy for upper bound of the sum.
        start : datetime
            Start time for the spectrum sum. Optional.
        end : datetime
            End time for the spectrum sum. Optional.
        use_energy : bool
            Use energy values for the bounds, rather than channel number.

        Returns
        -------
        TickedCounts
        """
        c_mask = np.ones(self.n_channels, dtype=bool)
        t_mask = np.ones(self.tick_times.size, dtype=bool)

        if use_energy:
            if lower_lim is not None:
                c_mask = np.logical_and(c_mask, self.energies >= lower_lim)
            if upper_lim is not None:
                c_mask = np.logical_and(c_mask, self.energies < upper_lim)
        else:
            if lower_lim is not None:
                c_mask = np.logical_and(c_mask, np.arange(self.n_channels) >= lower_lim)
            if upper_lim is not None:
                c_mask = np.logical_and(c_mask, np.arange(self.n_channels) < upper_lim)

        if start is not None:
            t_mask = np.logical_and(t_mask, self.tick_times >= start)
        if end is not None:
            t_mask = np.logical_and(t_mask, self.tick_times < end)
        return TickedCounts(self.ticks[t_mask][:, c_mask].sum(axis=1),
                            self.tick_times[t_mask],
                            name=self.name,
                            live_times=self.live_times[t_mask],
                            real_times=self.real_times[t_mask],
                            msg_times=self.msg_times,
                            blank_rate=self.blank_rate,
                            errors=np.sqrt(np.square(self.errors).sum(axis=1)),
                            start_time=self.start_time)

    def subtract_background(self, background_spectrum: Spectrum) -> TickedSpectrum:
        """
        Function which takes a background spectrum and subtracts it,
        tick by tick, scaled by the correct live times.

        Parameters
        ----------
        background_spectrum : Spectrum
            Background spectrum to be subtracted.

        Returns
        -------
        TickedSpectrum
        """
        return self.simultaneous_subtraction(background_spectrum)

    def simple_windowed_spectra_iterations(self, tick_window_width: int = 1, mode: int = 0) -> int:
        """
        Method which calculates the number of iterations for a rolling window of a given length and mode.

        Parameters
        ----------
        tick_window_width : int
            Window width in whole ticks.
        mode : int
            Mode 0, 1, or 2

        Returns
        -------
        int
        """
        if mode == 0:
            return self.ticks.shape[0] - tick_window_width + 1
        elif mode == 1:
            return self.ticks.shape[0]
        elif mode == 2:
            return self.ticks.shape[0] + tick_window_width - 1

    def simple_windowed_spectra(self, tick_window_width: int = 1, mode: int = 0) -> Generator[Spectrum]:
        """
        Simple generator of variable length windowed spectra, equivalent to a rolling window across the time space

        Parameters
        ----------
        tick_window_width : int
            width of the window, in ticks. Default: 1.
        mode : int
            sets the mode of the rolling window. default: 0.


        Modes
        -----
        0. windows are always full. For a TickedSpectrum with N ticks, there will be N - tick_window_width + 1
        spectra yielded.
        1. windows are always at least half full. For a TickedSpectrum with N ticks, there will be N spectra
        yielded.
        2. windows are always at least one tick full. For a TickedSpectrum with N ticks, there will be
        N + tick_window_width - 1 spectra yielded.
        """
        size = self.simple_windowed_spectra_iterations(tick_window_width, mode)
        if mode == 0:
            for i in range(size):
                yield Spectrum(self.calibration, self.ticks[i:i+tick_window_width].sum(axis=0), name=self.name,
                               error=np.sqrt(np.square(self.errors[i:i+tick_window_width]).sum(axis=0)),
                               comment=self.comment, live_time=self.live_times[i:i+tick_window_width].sum(),
                               real_time=self.real_times[i:i+tick_window_width].sum(),
                               start_time=self.tick_times[i])
        elif mode == 1:
            offset = -int(tick_window_width / 2)
            for i in range(offset, size + offset):
                yield Spectrum(self.calibration, self.ticks[max(i, 0):i+tick_window_width].sum(axis=0), name=self.name,
                               error=np.sqrt(np.square(self.errors[max(i, 0):i+tick_window_width]).sum(axis=0)),
                               comment=self.comment, live_time=self.live_times[max(i, 0):i+tick_window_width].sum(),
                               real_time=self.real_times[max(i, 0):i+tick_window_width].sum(),
                               start_time=self.tick_times[max(i, 0)])
        elif mode == 2:
            offset = -tick_window_width + 1
            for i in range(offset, size + offset):
                yield Spectrum(self.calibration, self.ticks[max(i, 0):i+tick_window_width].sum(axis=0), name=self.name,
                               error=np.sqrt(np.square(self.errors[max(i, 0):i+tick_window_width]).sum(axis=0)),
                               comment=self.comment, live_time=self.live_times[max(i, 0):i+tick_window_width].sum(),
                               real_time=self.real_times[max(i, 0):i+tick_window_width].sum(),
                               start_time=self.tick_times[max(i, 0)])
        yield None

    def resample(self, factor: float = 1.0) -> TickedSpectrum:
        """
        Method which uses the current spectrum (scaled by the 'scale' parameters) as the expectation for a new spectrum,
        sampled from either a normal or Poisson distribution.

        Parameters
        ----------
        factor : float
            Multiplication factor for the expectations of the new spectral counts.

        Returns
        -------
        new_ticked_spectrum : TickedSpectrum
            The resampled spectrum
        """
        new_ticked_spectrum = self.copy_me()
        if self._errors is None:
            new_ticked_spectrum.counts[self.ticks >= 0.] = np.random.poisson(self.ticks[self.ticks >= 0.] * factor)
        else:
            errors = np.sqrt(self.errors**2*factor)
            new_ticked_spectrum.counts = np.random.normal(self.ticks * factor, errors)
            new_ticked_spectrum.counts[new_ticked_spectrum.counts < 0.] = 0.
            new_ticked_spectrum._errors = errors
        return new_ticked_spectrum

    def consecutive_addition(self, other: TickedSpectrum) -> TickedSpectrum:
        """
        Method which consecutively sums another TickedSpectrum instance to this one.

        Parameters
        ----------
        other : TickedSpectrum
            TickedSpectrum instance to sum to this one.

        Returns
        -------
        TickedSpectrum
        """
        if self.calibration != other.calibration:
            other = other.rebin(self.calibration)
        return TickedSpectrum(energies=self.energies,
                              ticks=np.concatenate((self.ticks, other.ticks)),
                              tick_times=np.concatenate((self.tick_times, other.tick_times)),
                              live_times=np.concatenate((self.live_times, other.live_times)),
                              real_times=np.concatenate((self.real_times, other.real_times)),
                              name=self.name,
                              msg_times=None if self.msg_times is None or other.msg_times is None else np.concatenate(
                                  (self.msg_times, other.msg_times)
                              ),
                              blank_rate=(None if self.blank_rate is None or other.blank_rate is None else
                                          np.concatenate((self.blank_rate, other.blank_rate))),
                              errors=None if self._errors is None and other._errors is None else np.concatenate(
                                  (self.errors, other.errors)
                              ),
                              start_time=self.start_time,
                              comment=self.comment)

    def _simultaneous_addition_spectrum(self, spectrum: Spectrum) -> TickedSpectrum:
        if spectrum.calibration != self.calibration:
            spectrum = spectrum.rebin(self.calibration)
        scales = (self.live_times / spectrum.live_time)[:, np.newaxis]
        return TickedSpectrum(
            self.calibration,
            self.tick_times,
            self.ticks + spectrum.counts * scales,
            live_times=self.live_times,
            real_times=self.real_times,
            errors=np.sqrt(np.square(self.errors) + np.square(spectrum.error * scales)),
            name=self.name,
            comment=self.comment,
            start_time=self.start_time,
            msg_times=self.msg_times,
            blank_rate=self.blank_rate
        )

    def _simultaneous_addition_ticked_spectrum(self, other: TickedSpectrum) -> TickedSpectrum:
        if self.calibration != other.calibration:
            other = other.rebin(self.calibration)
        if self.tick_times.size != other.tick_times.size:
            self.log.warning(f'{self.name} has {self.tick_times.size} ticks, but {other.name} has '
                             f'{self.tick_times.size} ticks. The longer sequence will be shortened.')
        n_ticks = min(self.tick_times.size, other.tick_times.size)
        scales = (self.live_times[:n_ticks] / other.live_times[:n_ticks])[:, np.newaxis]
        return TickedSpectrum(
            self.calibration,
            self.tick_times,
            self.ticks[:n_ticks] + other.ticks[:n_ticks] * scales,
            live_times=self.live_times[:n_ticks],
            real_times=self.real_times[:n_ticks],
            errors=np.sqrt(np.square(self.errors[:n_ticks]) + np.square(other.errors[:n_ticks]) * scales),
            name=self.name,
            comment=self.comment,
            start_time=self.start_time,
            msg_times=None if self.msg_times is None else self.msg_times[:n_ticks],
            blank_rate=None if self.blank_rate is None else self.blank_rate[:n_ticks]
        )

    def _simultaneous_subtraction_spectrum(self, spectrum: Spectrum) -> TickedSpectrum:
        if spectrum.calibration != self.calibration:
            spectrum = spectrum.rebin(self.calibration)
        scales = (self.live_times / spectrum.live_time)[:, np.newaxis]
        return TickedSpectrum(
            self.calibration,
            self.tick_times,
            self.ticks - spectrum.counts * scales,
            live_times=self.live_times,
            real_times=self.real_times,
            errors=np.sqrt(np.square(self.errors) + np.square(spectrum.error * scales)),
            name=self.name,
            comment=self.comment,
            start_time=self.start_time,
            msg_times=self.msg_times,
            blank_rate=self.blank_rate
        )

    def _simultaneous_subtraction_ticked_spectrum(self, other: TickedSpectrum) -> TickedSpectrum:
        if self.calibration != other.calibration:
            other = other.rebin(self.calibration)
        if self.tick_times.size != other.tick_times.size:
            self.log.warning(f'{self.name} has {self.tick_times.size} ticks, but {other.name} has '
                             f'{self.tick_times.size} ticks. The longer sequence will be shortened.')
        n_ticks = min(self.tick_times.size, other.tick_times.size)
        scales = (self.live_times[:n_ticks] / other.live_times[:n_ticks])[:, np.newaxis]
        return TickedSpectrum(
            self.calibration,
            self.tick_times,
            self.ticks[:n_ticks] - other.ticks[:n_ticks] * scales,
            live_times=self.live_times[:n_ticks],
            real_times=self.real_times[:n_ticks],
            errors=np.sqrt(np.square(self.errors[:n_ticks]) + np.square(other.errors[:n_ticks]) * scales),
            name=self.name,
            comment=self.comment,
            start_time=self.start_time,
            msg_times=None if self.msg_times is None else self.msg_times[:n_ticks],
            blank_rate=None if self.blank_rate is None else self.blank_rate[:n_ticks]
        )

    def simultaneous_addition(self, other: Union[TickedSpectrum, Spectrum]) -> TickedSpectrum:
        """
        Method which simultaneously sums a Spectrum or another TickedSpectrum to this TickedSpectrum.

        Parameters
        ----------
        other : Spectrum or TickedSpectrum

        Returns
        -------
        TickedSpectrum
        """
        if isinstance(other, TickedSpectrum):
            return self._simultaneous_addition_ticked_spectrum(other)
        else:
            return self._simultaneous_addition_spectrum(other)

    def simultaneous_subtraction(self, other: Union[TickedSpectrum, Spectrum]) -> TickedSpectrum:
        """
        Method which simultaneously subtracts a Spectrum or another TickedSpectrum from this TickedSpectrum.

        Parameters
        ----------
        other : Spectrum or TickedSpectrum

        Returns
        -------
        TickedSpectrum
        """
        if isinstance(other, TickedSpectrum):
            return self._simultaneous_subtraction_ticked_spectrum(other)
        else:
            return self._simultaneous_subtraction_spectrum(other)

    def rebin(self, new_calibration: Calibration) -> TickedSpectrum:
        """
        Function which rebins spectrum with new calibration coefficients and number of channels.

        Parameters
        ----------
        new_calibration : Calibration
            Calibration of required rebinned spectrum.

        Returns
        -------
        new_spectrum : Spectrum
            Rebinned spectrum with calibration equal to 'new_calibration'.
        """

        # Get upper and lower energy values for each current channel
        energies_upper = self.calibration.upper_bin_limits
        energies_lower = self.calibration.lower_bin_limits

        # Get upper and lower energy values for each new channel
        new_energies_upper = new_calibration.upper_bin_limits
        new_energies_lower = new_calibration.lower_bin_limits

        # Generate empty array for new counts
        new_ticked_spectrum = self.copy_me()
        new_ticked_spectrum.calibration = new_calibration
        new_ticked_spectrum.ticks = np.zeros((new_calibration.n_channels, self.tick_times.size))
        new_ticked_spectrum._errors = None if self._errors is None else np.zeros((new_calibration.n_channels,
                                                                                  self.tick_times.size))

        # Check there will be counts in the new spectrum
        assert self.energies[0] < new_energies_upper[-1] and self.energies[-1] > new_energies_upper[0]

        zeros = np.zeros(new_calibration.n_channels)
        # Distribute the counts in each channel to the new spectrum
        for channel in range(self.n_channels):
            w_max = energies_upper[channel]
            w_min = energies_lower[channel]

            energy_overlap = np.maximum(np.minimum(new_energies_upper, w_max) -
                                        np.maximum(new_energies_lower, w_min),
                                        zeros)[np.newaxis, :]
            new_ticked_spectrum.ticks += self.ticks[:, channel] * energy_overlap / (w_max - w_min)
            if self._errors is not None:
                new_ticked_spectrum._errors += self._errors[channel]**2 * energy_overlap / (w_max - w_min)

        if self._errors is not None:
            new_ticked_spectrum._errors = np.sqrt(new_ticked_spectrum._errors)

        # Return the new spectrum
        return new_ticked_spectrum


class TickedSpectrumArray(TickedArrayBase):
    """
    Array of TickedSpectrum instances.

    Attributes
    ----------
    elements : OrderedDict[str, TickedSpectrum]
        OrderedDict, mapping measurements by their names.

    Methods
    -------
    tick_times() -> Array[datetime]
        Property which returns a list of datetime instances labelling the time at which each tick occurred.
    n_ticks() -> int
        Property which returns the number of ticks in the first member of the array.
    names() -> List[str]
        Property which returns a list of the measurement names which are keys to the mapping.
    number_of_members() -> int
        Property which returns the number of members of the array.
    start_times() -> List[datetime]
        Property which returns a list of datetime instances which give the times at which each member of the array
        began to be collected.
    contains_all(names: List[str]) -> bool
        Method which returns True if all the strings in the argument match the names of elements in the array.
    names_match(other: ArrayBase) -> bool
        Method which returns True if all the names of the other array are present in this array, and vice-versa.
    consecutive_addition(other: TickedSpectrumArray) -> TickedSpectrumArray
        Method which returns the consecutive sum of the TickedSpectrum with another Array.
    simultaneous_addition(other: TickedSpectrumArray) -> TickedSpectrumArray
        Method which returns the simultaneous sum of the TickedSpectrum with another Array.
    simultaneous_subtraction(other: Union[SpectrumArray, TickedSpectrumArray]) -> TickedSpectrumArray:
        Method which returns the simultaneous subtraction of another CountsArray from the Array.
    subtract_backgrounds(self, backgrounds: SpectrumArray) -> TickedSpectrumArray:
        Method which subtracts the background from each member of the array, using the array of background counts
        supplied as the argument.
    simultaneous_sum() -> TickedSpectrum
        Method which simultaneously sums each member of the array into a single TickedSpectrum instance.
    consecutive_sum() -> TickedSpectrum
        Must be implemented by subclasses.
    resample(factor: float) -> TickedSpectrumArray
        Method which returns a new array with each member resampled after scaling by the factor parameter.
    masked_array(names: List[str]) -> TickedSpectrumArray
        Method which returns a new array consisting only of members with the names in the given list of names.
    get_single_tick(tick_num: int) -> SpectrumArray
        Method which retrieves a SpectrumArray of Spectra for a single tick of the TickedSpectrumArray.
    sum_ticks(start: datetime, end: datetime) -> SpectrumArray
        Must be implemented by subclasses.
    get_ticked_counts_array() -> TickedCountsArray
        Method which sums channels  with optional channel or energy limits, into a TickedCountsArray with optional
        timing limits.
    simple_windowed_spectrum_arrays_iterations(tick_window_width: int = 1, mode: int = 0) -> int
        Method which calculates the number of iterations for a rolling window of a given length and mode.
    simple_windowed_spectrum_arrays(tick_window_width: int = 1, mode: int = 0) -> Iterator[SpectrumArray]
        Simple generator of variable length windowed SpectrumArrays, equivalent to a rolling window across the time
        space.
    sum_ticks(start: Union[datetime, None] = None, end: Union[datetime, None] = None) -> SpectrumArray
        Sum the ticks within optional time limits.
    consecutive_sum(self) -> TickedSpectrum
        Method which consecutively sums the members of the array.
    """
    def __init__(self, t_spectra: List[TickedSpectrum]):
        super(TickedSpectrumArray, self).__init__(t_spectra)

    def __getitem__(self, item) -> TickedSpectrum:
        return super(TickedSpectrumArray, self).__getitem__(item)

    def get_single_tick(self, tick_num: int) -> SpectrumArray:
        """
        Method which retrieves a SpectrumArray of Spectra for a single tick of the TickedSpectrumArray.

        Parameters
        ----------
        tick_num : int
            Index of the tick to retrieve

        Returns
        -------
        SpectrumArray
        """
        return SpectrumArray([ts.get_single_tick(tick_num) for ts in self.elements.values()])

    def simultaneous_sum(self) -> TickedSpectrum:
        """
        Method which simultaneously sums each member of the array into a single TickedSpectrum instance.

        Returns
        -------
        TickedSpectrum
        """
        result = None
        for ticked_spectrum in self:
            if result is None:
                result = ticked_spectrum
            else:
                result = result.simultaneous_addition(ticked_spectrum)
        return result

    def get_ticked_counts_array(self,
                                lower_lim: Union[int, float, None] = None,
                                upper_lim: Union[int, float, None] = None,
                                start: Union[datetime, None] = None,
                                end: Union[datetime, None] = None,
                                use_energy: bool = False) -> TickedCountsArray:
        """
        Method which sums channels  with optional channel or energy limits, into a TickedCountsArray with optional
        timing limits.

        Parameters
        ----------
        lower_lim : Union[int, float]
            Optional lower channel (default) or energy limit for the sum.
        upper_lim : Union[int, float]
            Optional upper channel (default) or energy limit for the sum.
        start : datetime
            optional time defining the start of the TickedCountsArray
        end : datetime
            optional time defining the end of the TickedCountsArray
        use_energy : bool
            Sets the limits to be energy values rather than channel numbers.

        Returns
        -------
        TickedCountsArray
        """
        return TickedCountsArray([self[det].get_ticked_counts(lower_lim, upper_lim, start, end, use_energy)
                                  for det in self.names])

    def simple_windowed_spectrum_arrays_iterations(self, tick_window_width: int = 1, mode: int = 0) -> int:
        """
        Method which calculates the number of iterations for a rolling window of a given length and mode.

        Parameters
        ----------
        tick_window_width : int
            Window width in whole ticks.
        mode : int
            Mode 0, 1, or 2

        Returns
        -------
        int
        """
        return self[self.names[0]].simple_windowed_spectra_iterations(tick_window_width, mode)

    def simple_windowed_spectrum_arrays(self, tick_window_width: int = 1, mode: int = 0) -> Iterator[SpectrumArray]:
        """
        Simple generator of variable length windowed SpectrumArrays, equivalent to a rolling window across the time
        space.

        Parameters
        ----------
        tick_window_width : int
            width of the window, in ticks. Default: 1.
        mode : int
            sets the mode of the rolling window. default: 0.
            Modes:
                0 - windows are always full. For a TickedSpectrum with N ticks, there will be N - tick_window_width + 1
                    spectra yielded.
                    |====================================================| Ticks
                    |====|----------------------------------------->|====| Windows
                1 - windows are always at least half full. For a TickedSpectrum with N ticks, there will be N spectra
                    yielded.
                      |====================================================| Ticks
                    |====|--------------------------------------------->|====| Windows
                2 - windows are always at least one tick full. For a TickedSpectrum with N ticks, there will be
                    N + tick_window_width - 1 spectra yielded.
                         |====================================================| Ticks
                    |====|--------------------------------------------------->|====| Windows
        """
        generators = [self[d].simple_windowed_spectra(tick_window_width, mode) for d in self.names]
        while 1:
            spectra = [next(gen) for gen in generators]
            if spectra[0] is None:
                break
            yield SpectrumArray(*spectra)

    def sum_ticks(self, start: Union[datetime, None] = None, end: Union[datetime, None] = None) -> SpectrumArray:
        """
        Sum the ticks within optional time limits.

        Parameters
        ----------
        start : datetime
            Optional start time for the sum.
        end : datetime
            Optional end time for the sum.

        Returns
        -------
        SpectrumArray
        """
        return SpectrumArray([self[det].sum_ticks(start, end) for det in self.names])

    def consecutive_sum(self) -> TickedSpectrum:
        """
        Method which consecutively sums the members of the array.

        Returns
        -------
        TickedSpectrum
        """
        result = None
        for ticked_spectrum in self:
            if result is None:
                result = ticked_spectrum
            else:
                result = result.consecutive_addition(ticked_spectrum)
        return result
