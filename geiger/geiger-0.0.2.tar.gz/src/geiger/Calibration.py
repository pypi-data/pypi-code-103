from __future__ import annotations
import numpy as np
from typing import Union, List, Tuple


class Calibration:
    """
    A class containing calibration information for spectra or Q-matrices.

    This class handles all matters relating to calibrations, energy binning etc.

    Attributes
    ----------
    n_channels : int
        Number of channels
    coefficients : Array[length = 3]
        Calibration coefficients
    label : str
        Label for the energy scale, used for plotting. Default is "Energy, keV".

    Methods
    -------
    is_calibrated -> bool
        Property which returns True if calibration coefficients provided.
    channel_numbers -> np.ndarray
        Property which returns a 1D array of channel numbers for the calibration.
    energies -> np.ndarray
        Property which returns an array of energy values for the lower limits of each energy bin, if the calibration
        coefficients are supplied, otherwise it returns the channel numbers.
    bin_widths -> np.ndarray or None.
        Property which returns an array of bin widths in energy units if calibration coefficients are supplied,
        otherwise it returns None.
    lower_bin_limits -> np.ndarray or None
        Property which returns an array of energy values for the lower limits of each energy bin, if the calibration
        coefficients are supplied, otherwise it returns None.
    upper_bin_limits -> np.ndarray or None
        Property which returns an array of energy values for the upper limits of each energy bin, if the calibration
        coefficients are supplied, otherwise it returns None.
    all_bin_limits -> np.ndarray or None
        Property which returns an array of energy values for the upper and lower limits of each energy bin, if the
        calibration coefficients are supplied, otherwise it returns None.
    centre_bin_energies -> np.ndarray or None
        Property which returns an array of energy values for the centre of each energy bin, if the calibration
        coefficients are supplied, otherwise it returns None.
    find_channel(energy: float) -> int or None
        Method which returns the channel number in which a deposit of energy 'energy' would be counted. If calibration
        coefficients are not provided, or if the energy is outside the bounds of the energy scale, this method returns
        None.
    energy_mask(lower: float, upper: float) -> np.ndarray or None
        Method which returns a boolean array which can be applied as a boolean mask on arrays of the same length. The
        'lower' and 'upper' parameters set the lower and upper limits on the energy scale for which the mask is True.
        If no calibration coefficients are supplied, this method returns None.
    from_energies(energies: np.ndarray) -> Calibration
        Class method which returns a Calibration instance calibrated on the energy values in the 'energy' array.
    channel_numbers_only(n_channels: int) -> Calibration
        Class method which returns a Calibration instance without calibration coefficients, with label equal to
        'Channel #'
    """
    def __init__(
            self,
            n_channels: int = 1024,
            coefficients: Union[np.ndarray, Tuple[float, float, float], List[float], None] = None,
            label: Union[str, None] = None
    ):
        """
        Parameters
        ----------
        n_channels : int
            Number of channels, default = 1024.
        coefficients : Tuple[float, float, float]
            offset, linear and quadratic calibration coefficients which define the lower energy bound of each channel
        label : Optional[str]
            Label for the energy scale. Used when plotting. Default is "Energy, keV". Use this if energy is in different
            units.
        """

        self.n_channels = n_channels
        self._is_calibrated = coefficients is not None
        if self.is_calibrated:
            self.coefficients: Union[np.ndarray, None] = np.array(coefficients)
        else:
            self.coefficients: Union[np.ndarray, None] = None
        self.label = label if label is not None else 'Energy, keV'

    @property
    def is_calibrated(self) -> bool:
        """
        Property which returns True if calibration coefficients provided.

        Returns
        -------
        bool
        """
        return self._is_calibrated

    @property
    def channel_numbers(self) -> np.ndarray:
        """
        Property which returns a 1D array of channel numbers for the calibration.

        Returns
        -------
        np.ndarray
        """
        return np.arange(self.n_channels)

    @property
    def bin_widths(self) -> Union[np.ndarray, None]:
        """
        Property which returns an array of bin widths in energy units if calibration coefficients are supplied,
        otherwise it returns None.

        Returns
        -------
        np.ndarray or None
        """
        if self.is_calibrated:
            return self.upper_bin_limits - self.lower_bin_limits
        else:
            return None

    @property
    def lower_bin_limits(self) -> Union[np.ndarray, None]:
        """
        Property which returns an array of energy values for the lower limits of each energy bin, if the calibration
        coefficients are supplied, otherwise it returns None.

        Returns
        -------
        np.ndarray or None
        """
        if self.is_calibrated:
            return self.all_bin_limits[:-1]
        else:
            return None

    @property
    def upper_bin_limits(self) -> Union[np.ndarray, None]:
        """
        Property which returns an array of energy values for the upper limits of each energy bin, if the calibration
        coefficients are supplied, otherwise it returns None.

        Returns
        -------
        np.ndarray or None
        """
        if self.is_calibrated:
            return self.all_bin_limits[1:]
        else:
            return None

    @property
    def all_bin_limits(self) -> Union[np.ndarray, None]:
        """
        Property which returns an array of energy values for the upper and lower limits of each energy bin, if the
        calibration coefficients are supplied, otherwise it returns None.

        Returns
        -------
        np.ndarray or None
        """
        if self.is_calibrated:
            channels = np.arange(0., self.n_channels + 1)
            powers = np.power(channels[:, np.newaxis], np.arange(3)[np.newaxis, :])
            return (powers * self.coefficients[np.newaxis, :]).sum(axis=1)
        else:
            return None

    @property
    def centre_bin_energies(self) -> Union[np.ndarray, None]:
        """
        Property which returns an array of energy values for the centre of each energy bin, if the calibration
        coefficients are supplied, otherwise it returns None.

        Returns
        -------
        np.ndarray or None
        """
        if self.is_calibrated:
            return (self.lower_bin_limits + self.upper_bin_limits) / 2.
        else:
            return None

    @property
    def energies(self) -> np.ndarray:
        """
        Property which returns an array of energy values for the lower limits of each energy bin, if the calibration
        coefficients are supplied, otherwise it returns the channel numbers.

        Returns
        -------
        np.ndarray
        """
        if self.is_calibrated:
            return self.lower_bin_limits
        else:
            return self.channel_numbers

    def find_channel(self, energy: float) -> Union[int, None]:
        """
        Method which returns the channel number in which a deposit of energy 'energy' would be counted. If calibration
        coefficients are not provided, or if the energy is outside the bounds of the energy scale, this method returns
        None.

        Parameters
        ----------
        energy : float
            Energy in the same units as the calibration coefficients.

        Returns
        -------
        int or None
        """
        if self.is_calibrated:
            arr = np.arange(self.n_channels)[np.logical_and(self.lower_bin_limits <= energy,
                                                            self.upper_bin_limits > energy)]
            if arr.size == 0:
                return None
            else:
                return int(arr[0])
        else:
            return None

    def energy_mask(self, lower: float = None, upper: float = None) -> Union[np.ndarray, None]:
        """
        Method which returns a boolean array which can be applied as a boolean mask on arrays of the same length. The
        'lower' and 'upper' parameters set the lower and upper limits on the energy scale for which the mask is True.
        If no calibration coefficients are supplied, this method returns None.

        Parameters
        ----------
        lower : float or None
            Lower energy limit for the boolean mask
        upper : float or None
            Upper energy limit for the boolean mask

        Returns
        -------
        np.ndarray
        """
        if self.is_calibrated:
            mask = np.ones(self.n_channels, dtype=bool)
            if upper is not None:
                mask = np.logical_and(mask, self.energies < upper)
            if lower is not None:
                mask = np.logical_and(mask, self.energies >= lower)
            return mask
        else:
            return None

    def __eq__(self, other: Calibration) -> bool:
        return np.isclose(self.coefficients, other.coefficients).all() and self.n_channels == other.n_channels

    @classmethod
    def from_energies(cls, energies: np.ndarray, bin_label: str = 'lower') -> Calibration:
        """
        Class method which returns a Calibration instance calibrated on the energy values in the 'energy' array.

        Parameters
        ----------
        energies : np.ndarray
            Array of energy values from which to create a calibration object.
        bin_label : str
            Either 'upper', 'middle' or 'lower', specifying where in each bin the energy array is labelling.
        """

        upper = bin_label == 'upper'
        middle = bin_label == 'middle'
        lower = bin_label == 'lower'

        assert isinstance(energies, np.ndarray)
        try:
            assert upper or middle or lower
        except AssertionError as _:
            raise AssertionError(f"'bin_label' keyword argument to Classes.Calibration must be either 'upper', "
                                 f"'middle', or 'lower'. You gave '{bin_label}'")

        channels = energies.size
        grad = np.gradient(energies)
        linear = np.array_equal(grad[1:], grad[:-1])

        if middle:
            energies -= grad/2.
        elif upper:
            energies -= grad

        if linear:
            coefficients = np.array([energies[0], grad[0], 0])
        else:
            coefficients = np.polyfit(np.arange(channels), energies, 2)[::-1]

        return cls(channels, coefficients)

    @classmethod
    def channel_numbers_only(cls, n_channels: int) -> Calibration:
        """
        Class method which returns a Calibration instance without calibration coefficients, with label equal to
        'Channel #'

        Parameters
        ----------
        n_channels : int
            Number of channels.

        Returns
        -------
        Calibration
        """
        return cls(n_channels=n_channels, label='Channel #')
