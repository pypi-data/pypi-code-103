import numpy as np
from numba import vectorize
from abc import ABCMeta, abstractmethod
import astropy.units as u
from typing import List, Union
from astropy.units import Quantity
import dask.array as da
import xarray as xr
from ..units.units_functions import check_units


@vectorize
def evaluate_gaussian1D(x, amp, mu, sigma):
    return amp * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


class Gaussian1D(metaclass=ABCMeta):
    def __init__(self, amplitude: float = None, mu: float = None, sigma: float = None, fwhm: float = None):
        """
        Class that represents a 1D Gaussian
        :param amplitude: Amplitude of the Gaussian
        :param mu: Center of the Gaussian
        :param sigma: Standard deviation of the Gaussian
        :param fwhm: FWHM of the Gaussian
        """
        if amplitude is not None:
            self.amplitude = amplitude
        else:
            self.amplitude = 1.0

        if mu is not None:
            self.mu = mu
        else:
            self.mu = 0.0

        if fwhm is None and sigma is not None:
            self.sigma = sigma
        elif fwhm is not None:
            self.fwhm = fwhm

        if sigma is None and fwhm is None:
            self.sigma = 1.0

    @property
    def sigma(self):
        return self.__sigma

    @sigma.setter
    def sigma(self, val):
        self.__sigma = val
        val_fwhm = 2.0 * np.sqrt(2.0 * np.log(2.0))
        self.__fwhm = val * val_fwhm

    @property
    def fwhm(self):
        return self.__fwhm

    @fwhm.setter
    def fwhm(self, val):
        self.__fwhm = val
        val_fwhm = 2.0 * np.sqrt(2.0 * np.log(2.0))
        self.__sigma = val / val_fwhm

    def evaluate(self, x=None):
        if x is not None:
            return evaluate_gaussian1D(x, self.amplitude, self.mu, self.sigma)


class Gaussian2D(metaclass=ABCMeta):
    def __init__(self, amplitude: float = None, mu: Union[Quantity, float, List[float]] = None,
                 sigma: Union[Quantity, float, List[float]] = None, theta: Union[Quantity, float] = None,
                 fwhm: Union[Quantity, float, List[float]] = None):
        """
        Class that represents an analytical model of a 2D Elliptical Gaussian
        :param amplitude: Amplitude of the Gaussian
        :param mu: Center of the Gaussian
        :param sigma: Standard deviation of the Gaussian
        :param theta: Inclination angle of the Gaussian
        :param fwhm: FWHM of the Gaussian
        """
        if amplitude is not None:
            self.amplitude = amplitude
        else:
            self.amplitude = 1.0

        self.mu = mu

        if fwhm is None and sigma is not None:
            self.sigma = sigma
        elif fwhm is not None:
            self.fwhm = fwhm

        if sigma is None and fwhm is None:
            self.sigma = [1.0, 1.0]

        if theta is None:
            self.theta = 0.0 * u.rad
        else:
            if isinstance(theta, float):
                self.theta = theta * u.rad
            else:
                # Make sure theta is in radians -> Convert theta to radians
                self.theta = theta.to(u.rad)

    @property
    def mu(self):
        return self.__mu

    @mu.setter
    def mu(self, val):
        if val is not None:
            if isinstance(val, Quantity):
                if isinstance(val.value, float):
                    self.__mu = [val, val]
                else:
                    self.__mu = val
            elif isinstance(val, float):
                self.__mu = [val, val]
            else:
                self.__mu = val
        else:
            self.__mu = [0.0, 0.0]

    @property
    def sigma(self):
        return self.__sigma

    @sigma.setter
    def sigma(self, val):
        if val is not None:
            if isinstance(val, Quantity):
                if isinstance(val.value, float):
                    self.__sigma = [val, val]
                else:
                    self.__sigma = val
            elif isinstance(val, float):
                self.__sigma = [val, val]
            else:
                self.__sigma = val
        else:
            self.__sigma = [1.0, 1.0]
        self.__area = self.calculate_area()
        self.__fwhm = [2.0 * np.sqrt(2.0 * np.log(2.0)) * self.__sigma[0],
                       2.0 * np.sqrt(2.0 * np.log(2.0)) * self.__sigma[1]]

    @property
    def fwhm(self):
        return self.__fwhm

    @fwhm.setter
    def fwhm(self, val):
        self.__fwhm = val
        val_fwhm = 2.0 * np.sqrt(2.0 * np.log(2.0))
        if isinstance(val, Quantity):
            if val.size == 1:
                self.__sigma = Quantity([val / val_fwhm, val / val_fwhm])
            else:
                self.__sigma = Quantity([val[0] / val_fwhm, val[1] / val_fwhm])
        else:
            if isinstance(val, list):
                if len(val) == 2:
                    self.__sigma = [val[0] / val_fwhm, val[1] / val_fwhm]
                else:
                    raise ValueError("The length of the list must not be greater than zero")
            else:
                self.__sigma = [val / val_fwhm, val / val_fwhm]
        self.__area = self.calculate_area()

    @property
    def area(self):
        return self.__area

    def calculate_area(self):
        area = np.pi * self.sigma[0] * self.sigma[1] / (4. * np.log(2))
        if check_units(area, u.steradian):
            return area.to(u.steradian)

    def evaluate(self, x: Union[da.core.Array, xr.DataArray, np.ndarray, float] = None,
                 y: Union[da.core.Array, xr.DataArray, np.ndarray, float] = None):
        """
        Function that evaluates an x,y coordinate in the 2D Gaussian
        :param x: x coordinate
        :param y: y coordinate
        :return: Depending of the input it will return the evaluation in all the (x,y) coordinates
        """
        if x is not None and y is not None:
            a = np.cos(self.theta) ** 2 / self.sigma[0] ** 2 + np.sin(self.theta) ** 2 / self.sigma[1] ** 2
            b = np.sin(2.0 * self.theta) / self.sigma[0] ** 2 + np.sin(2.0 * self.theta) / self.sigma[1] ** 2
            c = np.sin(self.theta) ** 2 / self.sigma[0] ** 2 + np.cos(self.theta) ** 2 / self.sigma[1] ** 2
            exp_factor = -0.5 * (
                        a * (x - self.mu[0]) ** 2 + b * (x - self.mu[0]) * (y - self.mu[1]) + c * (y - self.mu[1]) ** 2)
            f_gauss = self.amplitude * np.exp(exp_factor)
            return f_gauss
