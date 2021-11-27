from astropy import units as u
from ..utils.analytical_functions import Gaussian2D
from .transformer import Transformer
from ..units.units_functions import check_units
from ..units.lambda_units import lambdas_equivalencies
from ..base.dataset import Dataset
from abc import ABC
from astropy.units import Quantity
import xarray as xr
import numpy as np
import sys


class UVTaper(Transformer, Gaussian2D, ABC):
    def __init__(self, input_data: Dataset = None, amplitude: float = None, mu: Quantity = None,
                 sigma: Quantity = None, fwhm: Quantity = None, theta: Quantity = None):
        """
        Class that represents the UVTaper used in interferometry, the methods of this class will
        transform the weights of the input dataset according to the UVTaper features. UVTaper inherits from the
        Gaussian2D class.
        :param input_data: The input dataset to transform
        :param amplitude: Amplitude of the UVTaper
        :param mu: Center of the UVTaper
        :param sigma: Standard deviation of the UVTaper
        :param fwhm: FWHM of the UVTaper
        :param theta: Position Angle of the UVTaper
        """
        Transformer.__init__(self, input_data=input_data)

        # Check that sigmas and fwhm are in meters or units of lambdas
        if sigma is not None:
            if not check_units(sigma, u.m) and not check_units(sigma, u.lambdas) and not check_units(sigma, u.rad):
                raise ValueError("Sigma parameter for uvtaper must be whether in meters, units of lambdas or units of "
                                 "angle")
            else:
                # Make sure that units are in lambdas and not klambdas, Mlambdas, etc
                if check_units(sigma, u.lambdas):
                    sigma = sigma.to(u.lambdas)
                elif check_units(sigma, u.m):
                    sigma = sigma.to(u.m)
                else:
                    sigma = sigma.to(u.lambdas, equivalencies=lambdas_equivalencies())

        if fwhm is not None:
            if not check_units(fwhm, u.m) and not check_units(fwhm, u.lambdas) and not check_units(fwhm, u.rad):
                raise ValueError("FWHM parameter for uvtaper must be whether in meters, units of lambdas or units of "
                                 "angle")
            else:
                # Make sure that units are in lambdas and not klambdas, Mlambdas, etc
                if check_units(fwhm, u.lambdas):
                    fwhm = fwhm.to(u.lambdas)
                elif check_units(fwhm, u.m):
                    fwhm = fwhm.to(u.m)
                else:
                    fwhm = fwhm.to(u.lambdas, equivalencies=lambdas_equivalencies())

        # Check that theta is in units equivalent to radians

        if theta is not None:
            if not check_units(theta, u.rad):
                raise ValueError("Theta angle parameter for uvtaper must be in units of angles")

        Gaussian2D.__init__(self, amplitude, mu, sigma, theta, fwhm)

    def transform(self) -> None:
        """
        Evaluates the taper on the (u,v) positions and tapers the weights.
        """
        for ms in self.input_data.ms_list:
            if self.sigma.unit == u.m:
                u_xarray = ms.visibilities.uvw[:, 0]  # This is in meters
                v_xarray = ms.visibilities.uvw[:, 1]  # This is in meters
            else:
                uvw_lambdas = ms.visibilities.get_uvw_lambda(nu=ms.spectral_window.ref_frequency)
                u_xarray = uvw_lambdas[:, 0]  # This is in units of lambdas
                v_xarray = uvw_lambdas[:, 1]  # This is in units of lambdas

            u_xarray = u_xarray.astype('float32')  # Changing to float32 so the result from evaluate is a float32 array
            v_xarray = v_xarray.astype('float32')  # Changing to float32 so the result from evaluate is a float32 array
            gauss = xr.apply_ufunc(self.evaluate, u_xarray, v_xarray, dask="parallelized",
                                   output_dtypes=[ms.visibilities.weight.dtype])

            # This line gets values from unitless Quantity
            gauss = xr.apply_ufunc(lambda x: x.value, gauss, dask="parallelized", output_dtypes=[np.float32])
            ms.visibilities.weight *= gauss
