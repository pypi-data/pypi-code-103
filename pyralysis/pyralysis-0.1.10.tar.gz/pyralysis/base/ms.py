import logging
from .field import Field
from .polarization import Polarization
from .spectral_window import SpectralWindow
from .visibility import Visibility


class MS:
    def __init__(self, _id: int = None, field: Field = None, polarization: Polarization = None,
                 spectral_window: SpectralWindow = None, visibilities: Visibility = None):
        """
        Class that represents the partitioned Measurement Set. Remember that dask-ms partitions the whole MS
        into Fields and Spectral Windows.

        Parameters
        ----------
        _id : int
             ID for each MS partition
        field : Field
               Field object of this MS partition
        polarization : Polarization
                      Polarization object for this MS partition
        spectral_window : SpectralWindow
                         Spectral Window object for this MS partition
        visibilities : Visibility
                      Visibility object for this MS partition
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self._id = _id
        self.field = field
        self.polarization = polarization
        self.spectral_window = spectral_window
        self.visibilities = visibilities
