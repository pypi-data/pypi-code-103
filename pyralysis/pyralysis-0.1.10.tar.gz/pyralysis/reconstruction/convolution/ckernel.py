from abc import ABC
from ..parameter import Parameter
import dask.array as da
import xarray as xr
import numpy as np
from typing import List, Union


class CKernel(ABC):
    def __init__(self, amp: float = None, center=List[float], size=Union[List[int], int],
                 w: float = None, dask_array: bool = False):
        """
        Class that represents the convolution kernel
        :param amp: Amplitude of the kernel
        :param center: Center of the kernel
        :param size: Size of image containing the kernel
        :param w: Size of the kernel
        :param dask_array: Whether to store the kernel in a dask array
        """
        self.amp = amp
        self.x0 = center[0]
        self.y0 = center[1]
        self.support_x = None
        self.support_y = None
        if self.data is not None and self.data.ndims > 2:
            self.m = self.data.shape[0]
            self.n = self.data.shape[1]
            self.support_x = self.m // 2
            self.support_y = self.n // 2
        elif self.data is not None and size is not None:
            if isinstance(size, list):
                self.m = size[0]
                self.n = size[1]
            else:
                self.m = size
                self.n = size
            self.support_x = self.m // 2
            self.support_y = self.m // 2
            if dask_array:
                self.data = xr.DataArray(da.zeros((self.m, self.n)))
                self.data.data.compute_chunk_sizes()
            else:
                self.data = xr.DataArray(np.zeros((self.m, self.n)))

        self.w = w
        self.gcf = CKernel()
