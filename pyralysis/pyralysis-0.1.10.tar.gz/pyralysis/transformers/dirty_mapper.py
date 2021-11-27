from .gridder import Gridder
from .gridder import bincount, complex_bincount, calculate_pix
from abc import ABC
import dask.array as da
import numpy as np
import xarray as xr
from typing import List, Union
import astropy.units as un
from more_itertools import locate
from ..units.lambda_units import lambdas_equivalencies
from ..units import array_unit_conversion
from ..reconstruction import Image
from astropy.units import Quantity


class DirtyMapper(Gridder, ABC):
    def __init__(self, stokes: Union[List[str], str] = None, **kwargs):
        """
        Object that transforms a dataset to a set of dirty images
        Parameters
        ----------
        stokes : Stokes parameters to reconstruct
        kwargs : Gridder type object parameters
        """
        super().__init__(**kwargs)

        if stokes is None:
            self.stokes = ["I", "Q", "U", "V"]
        else:
            if isinstance(stokes, str):
                self.stokes = stokes.split(',')

        if self.imsize is None:
            self.uvgridded_visibilities = None
            self.uvgridded_weights = None
        else:
            self.uvgridded_visibilities = np.zeros((len(self.stokes), self.imsize[0], self.imsize[1]),
                                                   dtype=np.complex64)
            self.uvgridded_weights = np.zeros((len(self.stokes), self.imsize[0], self.imsize[1]), dtype=np.float32)

    def transform(self) -> tuple[Image, Image]:
        idx_I = list(locate(self.stokes, lambda x: x == "I"))
        idx_Q = list(locate(self.stokes, lambda x: x == "Q"))
        idx_U = list(locate(self.stokes, lambda x: x == "U"))
        idx_V = list(locate(self.stokes, lambda x: x == "V"))

        for ms in self.input_data.ms_list:
            chans = ms.spectral_window.chans.compute()
            nchans = ms.spectral_window.nchans
            uvw = ms.visibilities.uvw
            weight = ms.visibilities.weight
            data = ms.visibilities.data
            flag = ms.visibilities.flag
            ncorrs = ms.polarization.ncorrs
            corr_names = ms.polarization.corrs_names

            uvw_broadcast = da.tile(uvw, nchans).reshape((len(uvw), nchans, 3))
            chans_broadcast = chans[np.newaxis, :, np.newaxis]

            # uvw_lambdas = da.map_blocks(
            #    lambda x: x.to(un.lambdas, equivalencies=lambdas_equivalencies(restfreq=chans_broadcast)).value,
            #    uvw_broadcast,
            #    dtype=np.float64)
            uvw_lambdas = array_unit_conversion(array=uvw_broadcast, unit=un.lambdas,
                                                equivalencies=lambdas_equivalencies(restfreq=chans_broadcast))

            uvw_lambdas = uvw_lambdas.reshape((len(uvw_lambdas)*nchans, 3))
            weight_broadcast = da.repeat(weight.data, nchans, axis=0)
            flag = flag.data.reshape((len(flag.data) * nchans, ncorrs))
            data = data.data.reshape((len(data.data) * nchans, ncorrs))
            weight_broadcast[flag] = 0.0

            idx_corrs = [key for key, value in corr_names.items()]
            idx = calculate_pix(uvw_lambdas, self.uvcellsize, self.imsize)

            bincount_m = idx.max().compute() + 1

            visibility_data = weight_broadcast * data

            bin_count_weights = da.apply_along_axis(bincount, 0, weight_broadcast, idx,
                                                    shape=(bincount_m,),
                                                    dtype=weight_broadcast.dtype)

            bin_count_visibilities = da.apply_along_axis(complex_bincount, 0, visibility_data,
                                                         idx,
                                                         shape=(bincount_m,),
                                                         dtype=visibility_data.dtype)

            idx = idx.compute()
            i_idx, j_idx = np.unravel_index(idx, (self.imsize[0], self.imsize[1]))

            for i in idx_corrs:
                gridded_data = bin_count_visibilities[idx, i].compute()
                gridded_weights = bin_count_weights[idx, i].compute()

                if corr_names[i] == "XX":
                    if idx_I:
                        self.uvgridded_visibilities[idx_I[0], i_idx, j_idx] += gridded_data
                        self.uvgridded_weights[idx_I[0], i_idx, j_idx] += gridded_weights

                    if idx_Q:
                        self.uvgridded_visibilities[idx_Q[0], i_idx, j_idx] += gridded_data
                        self.uvgridded_weights[idx_Q[0], i_idx, j_idx] += gridded_weights

                elif corr_names[i] == "XY":
                    if idx_U:
                        self.uvgridded_visibilities[idx_U[0], i_idx, j_idx] += gridded_data
                        self.uvgridded_weights[idx_U[0], i_idx, j_idx] += gridded_weights

                    if idx_V:
                        self.uvgridded_visibilities[idx_V[0], i_idx, j_idx] += -1.0j * gridded_data
                        self.uvgridded_weights[idx_V[0], i_idx, j_idx] += gridded_weights
                elif corr_names[i] == "YX":
                    if idx_U:
                        self.uvgridded_visibilities[idx_U[0], i_idx, j_idx] += gridded_data
                        self.uvgridded_weights[idx_U[0], i_idx, j_idx] += gridded_weights

                    if idx_V:
                        self.uvgridded_visibilities[idx_V[0], i_idx, j_idx] += 1.0j * gridded_data
                        self.uvgridded_weights[idx_V[0], i_idx, j_idx] += gridded_weights
                elif corr_names[i] == "YY":
                    if idx_I:
                        self.uvgridded_visibilities[idx_I[0], i_idx, j_idx] += gridded_data
                        self.uvgridded_weights[idx_I[0], i_idx, j_idx] += gridded_weights

                    if idx_Q:
                        self.uvgridded_visibilities[idx_Q[0], i_idx, j_idx] += -1.0 * gridded_data
                        self.uvgridded_weights[idx_Q[0], i_idx, j_idx] += gridded_weights
                elif corr_names[i] == "LL":

                    if idx_I:
                        self.uvgridded_visibilities[idx_I[0], i_idx, j_idx] += gridded_data
                        self.uvgridded_weights[idx_I[0], i_idx, j_idx] += gridded_weights

                    if idx_V:
                        self.uvgridded_visibilities[idx_V[0], i_idx, j_idx] += -1.0j * gridded_data
                        self.uvgridded_weights[idx_V[0], i_idx, j_idx] += gridded_weights
                elif corr_names[i] == "LR":
                    if idx_Q:
                        self.uvgridded_visibilities[idx_Q[0], i_idx, j_idx] += gridded_data
                        self.uvgridded_weights[idx_Q[0], i_idx, j_idx] += gridded_weights

                    if idx_U:
                        self.uvgridded_visibilities[idx_U[0], i_idx, j_idx] += 1.0j * gridded_data
                        self.uvgridded_weights[idx_U[0], i_idx, j_idx] += gridded_weights
                elif corr_names[i] == "RL":
                    if idx_Q:
                        self.uvgridded_visibilities[idx_Q[0], i_idx, j_idx] += gridded_data
                        self.uvgridded_weights[idx_Q[0], i_idx, j_idx] += gridded_weights

                    if idx_U:
                        self.uvgridded_visibilities[idx_U[0], i_idx, j_idx] += 1.0j * gridded_data
                        self.uvgridded_weights[idx_U[0], i_idx, j_idx] += gridded_weights
                elif corr_names[i] == "RR":
                    if idx_I:
                        self.uvgridded_visibilities[idx_I[0], i_idx, j_idx] += gridded_data
                        self.uvgridded_weights[idx_I[0], i_idx, j_idx] += gridded_weights

                    if idx_V:
                        self.uvgridded_visibilities[idx_V[0], i_idx, j_idx] += 1.0j * gridded_data
                        self.uvgridded_weights[idx_V[0], i_idx, j_idx] += gridded_weights
                else:
                    raise ValueError("The correlation does not exist")

        # Normalize gridded visibilities
        self.uvgridded_weights /= self.imsize[0] * self.imsize[1]
        idx_stokes, idx_i, idx_j = np.where(self.uvgridded_weights > 0.0)
        self.uvgridded_visibilities[idx_stokes, idx_i, idx_j] /= self.uvgridded_weights[idx_stokes, idx_i, idx_j]
        # Make a IFFT
        dirty_maps = np.zeros((len(self.stokes), self.imsize[0], self.imsize[0]),
                              dtype=np.float32)
        dirty_beams = np.zeros((len(self.stokes), self.imsize[0], self.imsize[0]),
                               dtype=np.float32)
        for idx_stokes in range(0, len(self.stokes)):
            if self.hermitian_symmetry:
                dirty_map = np.fft.fftshift(
                    np.fft.irfft2(np.fft.ifftshift(self.uvgridded_visibilities[idx_stokes], axes=0)))
                dirty_beam = np.fft.fftshift(
                    np.fft.irfft2(np.fft.ifftshift(self.uvgridded_weights[idx_stokes], axes=0)))
            else:
                dirty_map = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(self.uvgridded_visibilities[idx_stokes])))
                dirty_beam = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(self.uvgridded_weights[idx_stokes])))
            dirty_maps[idx_stokes] = dirty_map.real * self.uvcellsize[0] * self.uvcellsize[1]
            dirty_beams[idx_stokes] = dirty_beam.real / np.max(dirty_beam.real)
        sky_cellsize = self.uvcellsize.to(un.rad, equivalencies=lambdas_equivalencies()) / self.imsize
        self.uvgridded_visibilities = da.from_array(self.uvgridded_visibilities)
        self.uvgridded_weights = da.from_array(self.uvgridded_weights)
        return Image(data=xr.DataArray(da.from_array(dirty_maps)), cellsize=sky_cellsize), \
               Image(data=xr.DataArray(da.from_array(dirty_beams)), cellsize=sky_cellsize)
