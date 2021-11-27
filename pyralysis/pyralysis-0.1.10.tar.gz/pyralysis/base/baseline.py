import xarray as xr
import numpy as np
from .antenna import Antenna
import logging
from itertools import combinations
import xarray.ufuncs as xarrfunc
import dask.array as da
from typing import Union
import astropy.units as u


class Baseline:
    def __init__(self, antenna: Antenna = None, dask_idx: bool = False):
        """
        Class that represents the relationship between two antennas.
        The resulting baseline dataset has the following columns:
        - BASELINE_LENGTH
        - ANTENNA1
        - ANTENNA2

        Parameters
        ----------
        antenna : Antenna
                  Antenna object.
        dask_idx : bool
                   Boolean to use or not use indexes as dask arrays.
        """

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.dataset = None
        self.max_baseline = 0.0 * u.m
        self.min_baseline = 0.0 * u.m

        if antenna is not None:
            ids = antenna.dataset.ROWID.data.compute()
            combs = np.array(list(combinations(ids, 2)))

            antenna1 = antenna.dataset.sel(row=combs[:, 0])
            antenna2 = antenna.dataset.sel(row=combs[:, 1])

            baseline = antenna1.POSITION.data - antenna2.POSITION.data

            baseline_length = da.sqrt(baseline[:, 0] ** 2 + baseline[:, 1] ** 2 + baseline[:, 2] ** 2)
            baseline_length = baseline_length.astype(np.float32) * u.m

            row_id = np.arange(len(combs[:, 0]))
            ant1_id = combs[:, 0]
            ant2_id = combs[:, 1]
            if dask_idx:
                row_id = da.from_array(row_id)
                ant1_id = da.from_array(ant1_id)
                ant2_id = da.from_array(ant2_id)

            ds = xr.Dataset(
                data_vars=dict(
                    BASELINE_LENGTH=(["row"], baseline_length),
                    ANTENNA1=(["row"], ant1_id.astype(np.int32)),
                    ANTENNA2=(["row"], ant2_id.astype(np.int32)),

                ),
                coords=dict(
                    ROWID=(["row"], row_id.astype(np.int32)),
                ),
                attrs=dict(description="Baseline-Antenna relationship"))
            self.dataset = ds
            self.max_baseline = self.dataset.BASELINE_LENGTH.max().data.compute()
            self.min_baseline = self.dataset.BASELINE_LENGTH.min().data.compute()

    def filter_by_antennas(self, antenna1: Union[da.Array, xr.DataArray, np.array, int],
                           antenna2: Union[da.Array, xr.DataArray, np.array, int], drop: bool = True) -> xr.Dataset:
        """
        :param antenna1: Array or scalar of ids referencing ANTENNA1
        :param antenna2: Array or scalar of ids referencing ANTENNA2
        :param drop: Drop nan values when doing where on the dataset
        :return: Filtered xarray dataset
        """
        if self.dataset is not None:
            filtered_dataset = self.dataset.where((self.dataset.ANTENNA1.isin(antenna1)) &
                                                  (self.dataset.ANTENNA2.isin(antenna2)), drop=drop)
            return filtered_dataset
        else:
            raise TypeError("Cannot filter dataset, because it is None")
