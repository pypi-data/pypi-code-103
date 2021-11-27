import xarray as xr
from astropy.units import Quantity
from typing import List, Union
from abc import ABCMeta, abstractmethod
from ..units.units_functions import check_units
import astropy.units as un


class Parameter(metaclass=ABCMeta):
    def __init__(self, data: xr.DataArray = None, cellsize: Union[List[Quantity], Quantity] = None, name: str = None,
                 noise: Quantity = None, chunks: tuple = None, data_gpu: bool = None):
        """
        Class that represents a parameter. This parameter can be passed to Optimizers in order to reconstruct them.
        :param data: Array with the data
        :param cellsize: Cell-size space between data points.
        :param name: Name of the parameter
        :param noise: Noise of the parameter
        :param chunks: Change the chunks of the dask array
        :param data_gpu: Whether to convert data to a cupy array.
        """
        self.data = data
        self.name = name
        self.noise = noise
        self.data_gpu = data_gpu

        if data is not None and chunks is not None:
            self.data = self.data.chunk(chunks)

        if cellsize is not None:
            if isinstance(cellsize, Quantity):
                if cellsize.size == 1:
                    self.cellsize = [cellsize.value, cellsize.value] * cellsize.unit
                else:
                    self.cellsize = cellsize
            else:
                same_units = all(element.unit == cellsize[0].unit for element in cellsize)
                if same_units:
                    self.cellsize = [element.value for element in cellsize] * cellsize[0].unit
                else:
                    raise ValueError("Elements don't have the same units")
        else:
            self.cellsize = cellsize

    @property
    def cellsize(self):
        return self.__cellsize

    @cellsize.setter
    def cellsize(self, val):
        if val is not None:
            if isinstance(val, Quantity):
                if val.size == 1:
                    self.__cellsize = [val.value, val.value] * val.unit
                else:
                    self.__cellsize = val
            else:
                same_units = all(element.unit == val[0].unit for element in val)
                if same_units:
                    self.__cellsize = [element.value for element in val] * val[0].unit
                else:
                    raise ValueError("Elements don't have the same units")
            area = self.__cellsize[0] * self.__cellsize[1]
            if check_units(area, un.steradian):
                self.__pixel_area = area.to(un.steradian)
        else:
            self.__cellsize = val

    @property
    def pixel_area(self):
        return self.__pixel_area

    @abstractmethod
    def calculate_noise(self):
        pass
