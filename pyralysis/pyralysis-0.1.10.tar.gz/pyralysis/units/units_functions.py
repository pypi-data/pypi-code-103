import xarray as xr
import dask.array as da
from astropy.units import Quantity
from astropy.units.equivalencies import Equivalency
from typing import Union


def xarray_unit_conversion(array: xr.DataArray = None, unit: Quantity = None, equivalencies: Equivalency = None,
                           dask: str = "parallelized") -> xr.DataArray:
    return xr.apply_ufunc(lambda x: x.to(unit, equivalencies=equivalencies), array, dask=dask,
                          output_dtypes=[array.dtype])


def dask_unit_conversion(array: da.core.Array = None, unit: Quantity = None, equivalencies: Equivalency = None) -> da.core.Array:
    return da.map_blocks(lambda x: x.to(unit, equivalencies), array, dtype=array.dtype)


def array_unit_conversion(array: Union[xr.DataArray, da.core.Array] = None, unit: Quantity = None, equivalencies: Equivalency = None) -> Union[xr.DataArray, da.core.Array]:
    if isinstance(array, xr.DataArray):
        return xarray_unit_conversion(array, unit, equivalencies)
    elif isinstance(array, da.core.Array):
        return dask_unit_conversion(array, unit, equivalencies)
    else:
        raise TypeError("The array is not a dask nor xarray type")


def check_units(var: Quantity, unit: Quantity) -> bool:
    """
    Checks if a variable unit is equivalent to some other unit
    :param var: The variable
    :param unit: The unit
    :return: True if the variable unit is equivalent, False if not
    """
    if var.unit.is_equivalent(unit):
        return True
    else:
        return False
