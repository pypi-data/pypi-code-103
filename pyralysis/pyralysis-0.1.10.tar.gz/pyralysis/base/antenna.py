import xarray as xr
import logging
import astropy.units as u


class Antenna:
    def __init__(self, dataset: xr.Dataset = None):
        """
        Class that represents the antenna MS table of an interferometer

        Parameters
        ----------
        dataset : xarray.Dataset
                  Full antenna table xarray dataset.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.dataset = dataset

        self.max_diameter = 0.0 * u.m
        self.min_diameter = 0.0 * u.m
        if dataset is not None:
            self.max_diameter = self.dataset.DISH_DIAMETER.data.max().compute() * u.m
            self.min_diameter = self.dataset.DISH_DIAMETER.data.min().compute() * u.m
