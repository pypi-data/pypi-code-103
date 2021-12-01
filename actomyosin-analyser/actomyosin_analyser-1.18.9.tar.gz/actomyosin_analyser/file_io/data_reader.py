from abc import ABC, abstractmethod
from typing import Tuple, Dict, List
import numpy as np

from actomyosin_analyser.model.bead import Filament

_LinksArray = np.ndarray


class DataReader(ABC):
    """
    Template of a data reader class. Any derived class should
    implement the here defined abstract methods.
    This is a place holder to define the interface of a DataReader used
    by the Analyser class. Not all methods have to be overwritten, depending
    on the analyses you perform with the Analyser class. The most fundamental
    methods are marked as abstract methods (python will force you to
    implement these). Some additional methods are not implemented (raising
    exception when executed), but are not mandatory to implement (some
    analyses just won't work, when they remain not implemented).
    """

    @abstractmethod
    def __init__(self, source_file: str):
        ...

    @abstractmethod
    def get_filament_coordinates(self, minimum_image: bool) -> np.ndarray:
        pass

    def read_particle_positions(self, minimum_image: bool) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def read_time(self) -> np.ndarray:
        ...

    @abstractmethod
    def read_time_as_step_indices(self) -> np.ndarray:
        ...

    @abstractmethod
    def read_box_size(self) -> np.ndarray:
        """
        Read box size in shape (3, 2) where rows are x, y, z,
        columns are lower/upper bound.
        """
        ...

    def read_particle_types(self) -> Tuple[Dict[str, int], np.ndarray]:
        """
        Read particle types as an integer array.
        :return: Dictionary mapping particle type (str) to type as integer.
        :return: Integer array of particle types.
        """
        raise NotImplementedError

    @abstractmethod
    def get_filaments(self, frame: int) -> Tuple[List[Filament], _LinksArray]:
        ...

    @abstractmethod
    def get_filaments_all(self) -> List[List[Filament]]:
        """
        Read filament information for all frames.

        :return: Length of returned list is equal to number of recorded frames.
           For each frame, each item is a list containing Filament instances.
        """
        ...

    @abstractmethod
    def read_dt(self):
        ...

    def read_parameter(self, *args):
        raise NotImplementedError

    @abstractmethod
    def get_n_non_filament_particles(self) -> int:
        ...

    def get_motor_count(self) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def get_non_filament_coordinates(self, minimum_image):
        ...
