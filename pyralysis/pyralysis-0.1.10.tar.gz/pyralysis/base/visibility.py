import logging
import dask.array as da
import astropy.units as un
from ..units import lambdas_equivalencies
from ..units import xarray_unit_conversion
import xarray as xr


class Visibility:
    def __init__(self, dataset: xr.Dataset = None):
        """
        Class that represents the main table visibilities on the partitioned Measurement Set.

        Parameters
        ----------
        dataset : xarray.Dataset
                  xarray Dataset of the main table on the partitioned Measurement Set
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.nrows = 0

        self.dataset = dataset
        if dataset is not None:
            self.nrows = len(self.dataset.ROWID)
            self.rows = self.dataset.ROWID
            self.uvw = self.dataset.UVW * un.m
            self.weight = self.dataset.WEIGHT
            self.flag = self.dataset.FLAG
            self.data = self.dataset.DATA
            self.model = xr.zeros_like(self.data)
            self.antenna1 = self.dataset.ANTENNA1
            self.antenna2 = self.dataset.ANTENNA2
            self.baseline = self.dataset.BASELINE
            self.unflagged_rows, self.unflagged_chans, self.unflagged_corrs = da.nonzero(~self.flag.data)

    def get_column(self, column=None, as_xarray=True):
        if column is not None:
            if as_xarray:
                return self.dataset[column]
            else:
                return self.dataset[column].data.compute()

    def get_uvw_lambda(self, nu=None, as_xarray: bool = True):
        if nu is None:
            raise ValueError("Error: Input frequency is not present")

        if not as_xarray:
            return self.uvw.data.compute().to(un.lambdas, equivalencies=lambdas_equivalencies(restfreq=nu))
        else:
            # runs function decompose on a lazy manner over all items of the dask array
            uvw = xarray_unit_conversion(self.uvw, un.lambdas, lambdas_equivalencies(restfreq=nu))

            return uvw

    def get_uvw_distance(self, count_w: bool = True):
        u = self.uvw[:, 0]
        v = self.uvw[:, 1]
        if count_w:
            w = self.uvw[:, 2]
        else:
            w = 0
        distance = xr.ufuncs.sqrt(u ** 2 + v ** 2 + w ** 2)
        return distance
