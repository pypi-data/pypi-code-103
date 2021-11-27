from astropy.coordinates import SkyCoord
import astropy.units as u
import xarray as xr
import logging


class Field:
    def __init__(self, _id: int = None, dataset: xr.Dataset = None):
        """
        Class that represents each field in the observation.

        Parameters
        ----------
        _id : int
             id of the field Object
        dataset : xarray.Dataset
                 xarray dataset of the field object
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self._id = _id
        self.dataset = dataset

        self.ref_dir = None
        self.phs_dir = None

        self.name = ""
        if dataset is not None and _id is not None:
            ref_dir = self.dataset.REFERENCE_DIR.data.squeeze().compute()
            self.ref_dir = SkyCoord(ra=ref_dir[0] * u.rad, dec=ref_dir[1] * u.rad)

            phs_dir = self.dataset.PHASE_DIR.data.squeeze().compute()
            self.phs_dir = SkyCoord(ra=phs_dir[0] * u.rad, dec=phs_dir[1] * u.rad)

            self.name = self.dataset.NAME.data.squeeze().compute()
