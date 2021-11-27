import numpy as np
from abc import ABC
from typing import List, Union
import astropy.units as un
import xarray as xr
import dask.array as da
from astropy.units import Quantity
from .transformer import Transformer
from ..reconstruction.convolution import CKernel
from ..reconstruction import Image
from ..units import lambdas_equivalencies
from ..base import MS


def bincount(weights, x):
    return np.bincount(x, weights)


def complex_bincount(weights, x):
    real_w = weights.real
    imag_w = weights.imag
    return np.bincount(x, real_w) + 1j * np.bincount(x, imag_w)


def next_power_of_2(x):
    return 1 if x == 0 else 1 << (x - 1).bit_length()


def calculate_pix(uvw, uvcellsize, imsize, freq=None):
    """

    Parameters
    ----------
    uvw : uvw position in Fourier space
    uvcellsize : Cell-size in Fourier space
    imsize : Image size
    freq : (Optional) : Frequency

    Returns
    -------
    idx : Pixel 1D index of the cells on which the uv coordinates fall

    """
    m = imsize[0]
    n = imsize[1]

    hermitian_symmetry = False

    if m != n:
        hermitian_symmetry = True

    if freq is not None:
        duv = uvcellsize.to(un.m, equivalencies=lambdas_equivalencies(freq))
    else:
        duv = uvcellsize

    if uvw.ndim == 3:
        uv = uvw[:, :, 0:2] / duv
    else:
        uv = uvw[:, 0:2] / duv

    if isinstance(uv, xr.DataArray):
        uv = xr.apply_ufunc(lambda x: x.value, uv, dask="parallelized", output_dtypes=[uv.dtype]).round().astype(
            np.int32)
    elif isinstance(uv, da.core.Array):
        uv = da.map_blocks(lambda x: x.value, uv, dtype=uv.dtype).round().astype(np.int32)
    else:
        raise TypeError("The array is not a dask nor xarray type")

    if uvw.ndim == 3:
        uv = uv.reshape((uv.shape[0] * uv.shape[1], uv.shape[2]))

    if hermitian_symmetry:
        u_pix = uv[:, 0]
        v_pix = uv[:, 1] + m // 2
    else:
        u_pix = uv[:, 0] + n // 2
        v_pix = uv[:, 1] + m // 2

    idx = n * v_pix + u_pix

    if isinstance(idx, xr.DataArray):
        return idx.data
    else:
        return idx


class Gridder(Transformer, ABC):
    def __init__(self, image: Image = None, imsize: Union[List[int], int] = None,
                 cellsize: Union[List[float], float, Quantity] = None,
                 uvcellsize: Union[List[float], float, Quantity] = None,
                 ckernel_object: CKernel = None, hermitian_symmetry: bool = None, **kwargs):
        """
        Class that represents the interferometric gridding
        :param imsize: Image size
        :para cellsize: Cell size in Image-space
        :param uvcellsize: Cell size in Fourier-space
        :param ckernel_object: Convolution Kernel
        :param hermitian_symmetry : Indicated whether hermitian symmetry has been applied or not
        :param kwargs: Transformer arguments
        """
        super().__init__(**kwargs)
        self.ckernel_object = ckernel_object
        self.image = image
        self.hermitian_symmetry = hermitian_symmetry

        if self.hermitian_symmetry is None:
            self.hermitian_symmetry = False

        if image is None:
            self.imsize = imsize
            if cellsize is None and uvcellsize is not None:
                self.uvcellsize = uvcellsize
            elif cellsize is not None and uvcellsize is None:
                self.cellsize = cellsize
            elif cellsize is not None and uvcellsize is not None:
                self.cellsize = cellsize
            else:
                self.cellsize = cellsize
                self.uvcellsize = uvcellsize

        else:
            self.imsize = image.imsize
            self.cellsize = image.cellsize

    @property
    def imsize(self):
        return self.__imsize

    @imsize.setter
    def imsize(self, imsize):
        if isinstance(imsize, int):
            if self.hermitian_symmetry:
                self.__imsize = [imsize, imsize // 2 + 1]
            else:
                self.__imsize = [imsize, imsize]
        else:
            if self.hermitian_symmetry:
                if imsize[0] == imsize[1]:
                    self.__imsize = [imsize[0], imsize[1] // 2 + 1]
                else:
                    self.__imsize = imsize
            else:
                self.__imsize = imsize

    @property
    def cellsize(self):
        return self.__cellsize

    @cellsize.setter
    def cellsize(self, cellsize):
        if isinstance(cellsize, Quantity):
            if len(cellsize) > 1:
                self.__cellsize = cellsize
            else:
                self.__cellsize = Quantity([cellsize, cellsize])
        elif isinstance(cellsize, float):
            self.__cellsize = Quantity([cellsize * un.rad, cellsize * un.rad])
        elif isinstance(cellsize, list):
            if cellsize and len(cellsize) <= 2:
                self.__cellsize = Quantity(cellsize * un.rad)
            else:
                ValueError("The provided list for uvcellsize is too big for Gridder")
        else:
            self.__cellsize = cellsize

        if self.__cellsize is not None and self.__imsize is not None:
            if self.hermitian_symmetry:
                imsize = [self.__imsize[0], (self.__imsize[1] - 1) * 2]
            else:
                imsize = self.__imsize
            self.__uvcellsize = (1 / (imsize * self.__cellsize)).to(un.lambdas, equivalencies=lambdas_equivalencies())

    @property
    def uvcellsize(self):
        return self.__uvcellsize

    @uvcellsize.setter
    def uvcellsize(self, uvcellsize):
        if isinstance(uvcellsize, Quantity):
            if len(uvcellsize) > 1:
                self.__uvcellsize = uvcellsize
            else:
                self.__uvcellsize = Quantity([uvcellsize, uvcellsize])
        elif isinstance(uvcellsize, float):
            self.__uvcellsize = Quantity([uvcellsize * un.lambdas, uvcellsize * un.lambdas])
        elif isinstance(uvcellsize, list):
            if uvcellsize and len(uvcellsize) <= 2:
                self.__uvcellsize = Quantity(uvcellsize * un.lambdas)
            else:
                ValueError("The provided list for uvcellsize is too big for Gridder")
        else:
            self.__uvcellsize = uvcellsize

        if self.__uvcellsize is not None and self.imsize is not None:
            if self.hermitian_symmetry:
                imsize = [self.__imsize[0], (self.__imsize[1] - 1) * 2]
            else:
                imsize = self.__imsize
            self.__cellsize = (1 / (imsize * self.__uvcellsize)).to(un.rad, equivalencies=lambdas_equivalencies())

    def grid_weights(self, ms: MS = None, max_nu: Quantity = None):

        if max_nu is None:
            raise ValueError("Cannot grid weights without the maximum frequency parameter")

        if ms is not None:
            uvw = ms.visibilities.uvw
            weight = ms.visibilities.weight
            idx = calculate_pix(uvw, self.uvcellsize, self.imsize, max_nu)
            bincount_m = idx.max().compute() + 1
            bin_count = da.apply_along_axis(bincount, 0, weight.data, idx, shape=(bincount_m,),
                                            dtype=weight.data.dtype)
            w_k = bin_count[idx]  # Gridded weight for each non-gridded u,v coordinate
            return idx, bin_count, w_k

        else:
            raise ValueError("MS cannot be Nonetype")

    # This does the convolutional gridding
    def transform(self) -> None:

        for ms in self.input_data.ms_list:
            ref_freq = ms.spectral_window.ref_frequency
            uvw = ms.visibilities.uvw
            weight = ms.visibilities.weight
            data = ms.visibilities.data
            flag = ms.visibilities.flag

            idx = calculate_pix(uvw, self.uvcellsize, self.imsize, ref_freq)
            ncorrs = ms.polarization.ncorrs
            nchans = ms.spectral_window.nchans
            # chans = ms.spectral_window.chans.compute()
            baselines = da.unique(ms.visibilities.baseline.data).compute()
            weight_list = []
            data_list = []
            for baseline_id in baselines:
                row_id = da.argwhere(ms.visibilities.baseline.data == baseline_id).squeeze().compute()
                idx_per_baseline = idx[row_id]
                weight_per_baseline = weight[row_id]
                flag_per_baseline = flag[row_id]  # (rows, nchans, ncorrs)
                data_per_baseline = data[row_id]
                bincount_m = idx_per_baseline.max().compute() + 1
                # Grid the weights (rows, ncorrs)
                bin_count_weights = da.apply_along_axis(bincount, 0, weight_per_baseline.data, idx_per_baseline,
                                                        shape=(bincount_m,),
                                                        dtype=weight_per_baseline.data.dtype)
                gridded_weights = bin_count_weights[idx_per_baseline]

                # Grid the complex data (rows, nchans, ncorrs) (w * data)
                weight_broadcast = da.tile(weight_per_baseline, nchans).reshape(
                    (len(weight_per_baseline), nchans, ncorrs))
                weight_broadcast[flag_per_baseline] = 0.0
                visibility_data_per_baseline = weight_broadcast * data_per_baseline
                bin_count_visibilities = da.apply_along_axis(complex_bincount, 0, visibility_data_per_baseline.data,
                                                             idx_per_baseline,
                                                             shape=(bincount_m,),
                                                             dtype=visibility_data_per_baseline.data.dtype)

                bin_count_weight_broadcast = da.apply_along_axis(bincount, 0, weight_broadcast,
                                                                 idx_per_baseline,
                                                                 shape=(bincount_m,),
                                                                 dtype=weight_broadcast.dtype)
                gridded_data = bin_count_visibilities[idx_per_baseline] / bin_count_weight_broadcast[idx_per_baseline]
                weight_list.append(gridded_weights)
                data_list.append(gridded_data)
            print(data_list)
            break
