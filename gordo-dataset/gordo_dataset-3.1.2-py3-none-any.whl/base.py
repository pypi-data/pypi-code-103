# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import logging
from typing import Union, Dict, Any, Tuple

import pandas as pd
import numpy as np
import xarray as xr

from .dataset import get_dataset


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


class GordoBaseDataset(metaclass=ABCMeta):
    def __init__(self):
        self._metadata: Dict[Any, Any] = dict()
        # provided by @capture_args on child's __init__
        if not hasattr(self, "_params"):
            self._params = dict()

    @abstractmethod
    def get_data(
        self,
    ) -> Tuple[
        Union[np.ndarray, pd.DataFrame, xr.DataArray],
        Union[np.ndarray, pd.DataFrame, xr.DataArray],
    ]:
        """
        Return X, y data as numpy or pandas' dataframes given current state
        """

    def get_client_data(
        self, build_dataset_metadata: dict
    ) -> Tuple[
        Union[np.ndarray, pd.DataFrame, xr.DataArray],
        Union[np.ndarray, pd.DataFrame, xr.DataArray],
    ]:
        """
        The version of `get_data` used by gordo-client

        Parameters
        ----------
        build_dataset_metadata: dict
            build_metadata.dataset part of the metadata

        Returns
        -------

        """
        return self.get_data()

    def to_dict(self) -> dict:
        """
        Serialize this object into a dict representation, which can be used to
        initialize a new object using :func:`~GordoBaseDataset.from_dict`

        Returns
        -------
        dict
        """
        if not hasattr(self, "_params"):
            raise AttributeError(
                "Failed to lookup init parameters, ensure the "
                "object's __init__ is decorated with 'capture_args'"
            )
        # Update dict with the class
        params = self._params
        params_type = ""
        if hasattr(self, "__module__"):
            # Keep back-compatibility
            if self.__module__ != "gordo_dataset.datasets":
                params_type = self.__module__ + "."
        else:
            print("Not found __module__")
        params_type += self.__class__.__name__
        params["type"] = params_type
        for key, value in params.items():
            if hasattr(value, "to_dict"):
                params[key] = value.to_dict()
        return params

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "GordoBaseDataset":
        """
        Construct the dataset using a config from :func:`~GordoBaseDataset.to_dict`
        """
        return get_dataset(config)

    def get_metadata(self):
        """
        Get metadata about the current state of the dataset
        """
        return dict()
