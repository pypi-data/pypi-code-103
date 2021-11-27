from .transformer import Transformer
from abc import ABC, ABCMeta, abstractmethod
import xarray as xr
import astropy.units as un
import dask.array as da


class HermitianSymmetry(Transformer, metaclass=ABCMeta):
    def __init__(self, **kwargs):
        """

        Parameters
        ----------
        kwargs
               Transformer object arguments
        """
        super().__init__(**kwargs)

    def transform(self):
        """
        Applies hermitian symmetry to the dataset
        """
        for ms in self.input_data.ms_list:
            bool_array = xr.apply_ufunc(lambda x: x.value < 0.0, ms.visibilities.uvw[:, 0], dask="parallelized",
                                        output_dtypes=[bool])
            # This is faster than using the indexes as dask arrays
            idx = da.argwhere(bool_array).squeeze().compute()
            if len(idx) > 0:
                ms.visibilities.uvw = xr.where(bool_array, ms.visibilities.uvw * -1.0, ms.visibilities.uvw)
                ms.visibilities.data[idx] = da.conj(ms.visibilities.data[idx])
                ms.visibilities.model[idx] = da.conj(ms.visibilities.data[idx])
