import astropy.units as u
import astropy.constants as co
from typing import Union
from astropy.units import Quantity
import dask.array as da
import xarray as xr
from .units_functions import dask_unit_conversion, xarray_unit_conversion
from astropy.units.equivalencies import Equivalency

lambdas = u.def_unit('lambdas', format={'format': r'\lambda'}, prefixes=True, namespace=u.__dict__)


def lambdas_equivalencies(restfreq: Union[Quantity, da.core.Array, xr.DataArray] = None) -> Equivalency:
    """
    Creates the equivalencies given a rest frequency
    :param restfreq: Rest Frequency (can be a Quantity or an array)
    :return: Returns the equivalencies
    """
    if restfreq is not None:
        if isinstance(restfreq, Quantity):
            restfreq_hz = restfreq.to(u.Hz, equivalencies=u.spectral())
            restfreq_to_m = restfreq_hz.to(u.m, u.spectral())
        elif isinstance(restfreq, da.core.Array):
            restfreq_hz = dask_unit_conversion(restfreq, u.Hz, u.spectral())
            restfreq_to_m = dask_unit_conversion(restfreq, u.m, u.spectral())
        elif isinstance(restfreq, xr.DataArray):
            restfreq_hz = xarray_unit_conversion(restfreq, u.Hz, u.spectral())
            restfreq_to_m = xarray_unit_conversion(restfreq, u.m, u.spectral())
        else:
            raise ValueError("This equivalency only accepts Quantity, dask.array or xr.DataArray instances")

    # Beware that if restfreq is None then you cannot convert between lambdas-seconds or lambdas-meters

    eq = [
        (lambdas, u.s, lambda x: x / restfreq_hz, lambda x: x * restfreq_hz),
        (lambdas, u.m, lambda x: x * restfreq_to_m, lambda x: x / restfreq_to_m),
        (u.m, u.s, lambda x: x / co.c.to(u.m / u.s).value, lambda x: x * co.c.to(u.m / u.s).value),
        (u.one/lambdas, u.rad),
        (lambdas, u.one/u.rad),
        (lambdas, u.rad, lambda x: 1.0 / x, lambda x: 1.0 / x),
    ]

    return eq
