from abc import ABC
import logging
from .io import Io
from astropy.io import fits
import dask.array as da
import xarray as xr
from astropy.io.fits import Header
import astropy.units as un
import numpy as np
from typing import Union


class FITS(Io, ABC):
    def __init__(self, hdu: int = 0, memmap: bool = True, lazy_load_hdus: bool = False, use_dask: bool = True,
                 chunks: Union[int, tuple, str] = 'auto', **kwargs):
        """
        I/O class to handle FITS files.
        :param hdu: HDU of the FITS file
        :param memmap: Whether to use memory map or to load the whole image in memory
        :param lazy_load_hdus: Whether to load HDUs on a lazy manner
        :param use_dask: Whether to use dask arrays or not.
        :param chunks: How to chunk the array. Must be one of the following forms:
                - A blocksize like 1000.
                - A blockshape like (1000, 1000).
                - Explicit sizes of all blocks along all dimensions like
                ((1000, 1000, 500), (400, 400)).
                - A size in bytes, like "100 MiB" which will choose a uniform
                block-like shape
                - The word "auto" which acts like the above, but uses a configuration
                value ``array.chunk-size`` for the chunk size
                -1 or None as a blocksize indicate the size of the corresponding
                dimension.
        :param kwargs: IO arguments
        """
        super().__init__(**kwargs)
        self.hdu = hdu
        self.memmap = memmap
        self.lazy_load_hdus = lazy_load_hdus
        self.header = None
        self.use_dask = use_dask
        self.chunks = chunks
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def get_coordinates(self, hdul) -> dict:
        """
        Function that gets coordinates from header
        :param hdul: HDU List
        :return: Dictionary that represents the xarray coordinates
        """
        ndims = hdul[self.hdu].data.ndim
        m = self.header["NAXIS1"]
        n = self.header["NAXIS2"]
        if ndims == 3:
            z = self.header["NAXIS3"]
            cdelt3 = self.header["CDELT3"] * un.Hz
            crval3 = self.header["CRVAL3"] * un.Hz

        crpix1 = self.header["CRPIX1"]
        crpix2 = self.header["CRPIX2"]
        cdelt1 = self.header["CDELT1"] * un.deg
        cdelt2 = self.header["CDELT2"] * un.deg

        i_index_dask = da.arange(0, n, dtype=np.float32)
        j_index_dask = da.arange(0, m, dtype=np.float32)
        j_grid, i_grid = da.meshgrid(i_index_dask, j_index_dask)

        z_index = da.arange(0, z, dtype=np.float32)

        ra_dask = (j_index_dask - crpix1) * cdelt1
        dec_dask = (i_index_dask - crpix2) * cdelt2
        ra_grid, dec_grid = da.meshgrid(ra_dask, dec_dask)
        if ndims == 3:
            freqs = (z_index * cdelt3.value + crval3.value) * un.Hz
            coords = dict(
                Z=(["nu"], z_index.astype(np.int32)),
                FREQS=(["nu"], freqs),
                X=(["x", "y"], j_grid.astype(np.int32)),
                Y=(["x", "y"], i_grid.astype(np.int32)),
                RA=(["x", "y"], ra_grid),
                DEC=(["x", "y"], dec_grid),
            )
            return coords

        elif ndims == 2:
            coords = dict(
                X=(["x", "y"], j_grid.astype(np.int32)),
                Y=(["x", "y"], i_grid.astype(np.int32)),
                RA=(["x", "y"], ra_grid),
                DEC=(["x", "y"], dec_grid),
            )
            return coords

    def read(self):
        with fits.open(self.input_name, memmap=self.memmap, lazy_load_hdus=self.lazy_load_hdus) as hdul:
            self.header = hdul[self.hdu].header
            ndims = hdul[self.hdu].data.squeeze().ndim
            coords = self.get_coordinates(hdul)
            if ndims == 3:
                dims = ["nu", "x", "y"]
            elif ndims == 2:
                dims = ["x", "y"]
            if self.use_dask:
                data = da.from_array(hdul[self.hdu].data, chunks=self.chunks).squeeze()
            else:
                data = hdul[self.hdu].data.squeeze()
            return xr.DataArray(data, dims=dims, coords=coords,
                                attrs=dict(hdul[self.hdu].header))

    def write(self, fitsdata: xr.DataArray = None, output_name: str = None, overwrite: bool = True):

        if fitsdata is not None:
            data = fitsdata.data.compute()
        else:
            raise ValueError("Variable fitsdata cannot be Nonetype")

        if self.header is None:
            attrs = fitsdata.attrs
            if attrs:
                header = Header(attrs)
            else:
                header = None
        else:
            header = self.header

        if output_name is None:
            fits.writeto(filename=self.output_name, data=data, header=header, overwrite=overwrite)
        else:
            fits.writeto(filename=output_name, data=data, header=header, overwrite=overwrite)
