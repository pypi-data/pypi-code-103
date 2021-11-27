import logging
import astropy.units as u
import xarray as xr


class SpectralWindow:
    def __init__(self, _id: int = None, dataset: xr.Dataset = None):
        """
        Class that represents the Spectral Window table for the partitioned Measurement Set

        Parameters
        ----------
        _id : int
              ID of the Spectral Window
        dataset : xarray.Dataset
                  xarray Dataset representing the Spectral Window table
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self._id = _id
        self.dataset = dataset

        self.nchans = 0
        self.chans = []
        self.chan_width = []
        self.total_bandwidth = 0.0 * u.Hz
        self.ref_frequency = 0.0 * u.Hz
        if dataset is not None and _id is not None:
            self.nchans = int(dataset.NUM_CHAN.data.squeeze().compute())
            self.chans = dataset.CHAN_FREQ.data.squeeze(axis=0) * u.Hz
            self.chan_width = dataset.CHAN_WIDTH.data.squeeze(axis=0).compute() * u.Hz
            self.total_bandwidth = dataset.TOTAL_BANDWIDTH.data.squeeze().compute() * u.Hz
            self.ref_frequency = dataset.REF_FREQUENCY.data.squeeze().compute() * u.Hz
