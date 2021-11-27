from abc import ABC
import logging
import xarray
import dask.array as da
import numpy as np
import dask
from daskms import xds_from_table, xds_from_ms, xds_to_table
from pyralysis.io.io import Io
from ..base.antenna import Antenna
from ..base.baseline import Baseline
from ..base.dataset import Dataset
from ..base.field import Field
from ..base.ms import MS
from ..base.polarization import Polarization
from ..base.spectral_window import SpectralWindow
from ..base.visibility import Visibility
from typing import Union, List
import shutil
import os


class DaskMS(Io, ABC):
    def __init__(self, **kwargs):
        """
        I/O class to handle Measurements Sets v2 using Dask
        Parameters
        ----------
        kwargs : IO arguments
        """
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.ms_name_dask = self.input_name + "::"

    # This should look for CORRECTED_DATA and if does not exist then look for DATA
    def read(self, read_flagged_data: bool = False, datacolumn: str = None) -> Dataset:
        """
        Function that reads a Measurement Set v2 lazily using Dask.

        Parameters
        ----------
        read_flagged_data : Whether to read flagged_data or not.
        datacolumn : Data column to read. E.g: "corrected", "model", "data"

        Returns
        -------
        Returns a Pyralysis Dataset object
        """

        taql_query = ""
        if not read_flagged_data:
            taql_query = "!FLAG_ROW"

        # Creating antenna object
        antennas = xds_from_table(self.ms_name_dask + "ANTENNA", taql_where=taql_query)[0]
        antenna_obj = Antenna(dataset=antennas)

        # Creating baseline object
        baseline_obj = Baseline(antenna_obj)

        # Reading spectral window datasets (separated by different spectral windows)
        spws = xds_from_table(self.ms_name_dask + "SPECTRAL_WINDOW", taql_where=taql_query, group_cols="__row__")

        # Reading field datasets (separated by different fields)
        fields = xds_from_table(self.ms_name_dask + "FIELD", taql_where=taql_query, group_cols="__row__")

        # Reading data description dataset
        ddids = xds_from_table(self.ms_name_dask + "DATA_DESCRIPTION", taql_where=taql_query)[0]

        # Reading polarization datasets (separated by different polarization rows)
        pols = xds_from_table(self.ms_name_dask + "POLARIZATION", taql_where=taql_query, group_cols="__row__")

        # Reading MS main table indexing columns such as SCAN_NUMBER, TIME, ANTENNA1 and ANTENNA2
        # This returns a list of measurement sets partitioned by FIELDS and SPWS
        ms = xds_from_ms(self.input_name, taql_where=taql_query,
                         index_cols=["SCAN_NUMBER", "TIME", "ANTENNA1", "ANTENNA2"])

        # Check if datacolumn exists in the measurement set
        # Getting keys of the dataset
        ms_keys = ms[0].data_vars.keys()
        if datacolumn is None:
            if "CORRECTED_DATA" in ms_keys and "DATA" in ms_keys:
                datacolumn = "CORRECTED_DATA"
            elif "CORRECTED_DATA" in ms_keys:
                datacolumn = "CORRECTED_DATA"
            elif "DATA" in ms_keys:
                datacolumn = "DATA"
            else:
                self.logger.error("There is no valid column to read")
                raise ValueError
        else:
            if datacolumn not in ms_keys:
                self.logger.error("Column " + datacolumn + " does not exist")
                raise ValueError

        ms_list = []
        ms_id = 0
        for msds in ms:
            fdid = msds.attrs['FIELD_ID']
            ddid = msds.attrs['DATA_DESC_ID']
            spw_id = ddids["SPECTRAL_WINDOW_ID"][ddid].data.compute()
            pol_id = ddids["POLARIZATION_ID"][ddid].data.compute()
            field = fields[fdid]  # This is a field dataset
            spw = spws[spw_id]  # This is a spw dataset
            pol = pols[pol_id]  # This is a polarization dataset
            row_id = msds["ROWID"].data  # Row ID
            uvw = msds["UVW"].data  # UVW
            data = msds[datacolumn].data  # DATA
            weight = msds["WEIGHT"].data  # WEIGHT
            flag = msds["FLAG"].data  # FLAGS
            antenna1_ids = msds["ANTENNA1"].data  # ANTENNA 1 ID
            antenna2_ids = msds["ANTENNA2"].data  # ANTENNA 2 ID
            baseline_id = da.argmax((baseline_obj.dataset.ANTENNA1.data[None, :] == antenna1_ids[:, None]) & (
                    baseline_obj.dataset.ANTENNA2.data[None, :] == antenna2_ids[:, None]), axis=1).astype(np.int32)

            ds = xarray.Dataset(
                data_vars=dict(
                    UVW=(["row", "uvw"], uvw),
                    DATA=(["row", "chan", "corr"], data),
                    WEIGHT=(["row", "corr"], weight),
                    FLAG=(["row", "chan", "corr"], flag),
                ),
                coords=dict(
                    ROWID=(["row"], row_id),
                    ANTENNA1=(["row"], antenna1_ids),
                    ANTENNA2=(["row"], antenna2_ids),
                    BASELINE=(["row"], baseline_id)
                )
            )

            field_obj = Field(_id=fdid, dataset=field)
            spw_obj = SpectralWindow(_id=spw_id, dataset=spw)
            pol_obj = Polarization(_id=pol_id, dataset=pol)
            visibility_obj = Visibility(dataset=ds)
            ms_obj = MS(_id=ms_id, field=field_obj, polarization=pol_obj, spectral_window=spw_obj,
                        visibilities=visibility_obj)
            ms_list.append(ms_obj)
            ms_id += 1
        return Dataset(antenna=antenna_obj, baseline=baseline_obj, spectral_window_dataset=spws, ms_list=ms_list)

    def write_xarray_ds(self, dataset: Union[xarray.Dataset, List[xarray.Dataset]] = None, ms_name: str = None,
                        table_name: str = None,
                        columns: Union[List[str], str] = None) -> None:
        """
        Function that writes a xarray Dataset to a Measurement Set File
        Parameters
        ----------
        dataset : xarray Dataset to write
        ms_name : Name of the output Measurement Set
        table_name : Name of the table you might write. Default: None
        columns : Name of the columns to write to the table
        """
        if dataset is None:
            raise ValueError("Cannot write into Measurement Set without an xarray Dataset object")

        if ms_name is None:
            ms_name = self.input_name

        if table_name is not None:
            ms_name = ms_name + "::" + table_name

        if columns is None:
            columns = "ALL"

        writes = xds_to_table(dataset, table_name=ms_name, columns=columns)  # TODO: This could be returned and then
        # the compute can be done by the user
        dask.compute(writes)

    def write(self, dataset: Dataset = None, ms_name: str = None, columns: Union[List[str], str] = None) -> None:
        """
        Function that writes a Pyralysis Dataset (only ms_list) to a Measurement Set File
        Parameters
        ----------
        dataset : Pyralysis Dataset to write
        ms_name : Name of the output Measurement Set
        columns : Name of the columns to write to the table
        """
        if ms_name is None:
            ms_name = self.input_name
        else:
            if self.input_name != ms_name:
                if os.path.exists(ms_name):
                    shutil.rmtree(ms_name)
                shutil.copytree(self.input_name, ms_name)

        ms_datasets = [ms.visibilities.dataset for ms in dataset.ms_list]

        self.write_xarray_ds(dataset=ms_datasets, ms_name=ms_name, columns=columns)
