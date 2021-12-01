import os
from abc import ABC, abstractmethod
from typing import Callable, Sequence, Any, Dict, List

import numpy as np
from actomyosin_analyser.model.bead import Filament
from scipy.stats import gaussian_kde


class AbstractAnalyser(ABC):

    def __init__(self, data_root: str):
        self._data_root = data_root
        if not os.path.isdir(self._data_root):
            raise FileNotFoundError(f"{self._data_root} folder does not exist")
        self.blob_root = os.path.join(self._data_root, 'analysis_blobs')
        os.makedirs(self.blob_root, exist_ok=True)

    def _get_blob_analysis_dataset(
            self,
            dset_name: str,
            compute_function: Callable[[], np.ndarray],
    ) -> np.ndarray:
        blob_file = os.path.join(self.blob_root, dset_name + '.npy')
        if os.path.exists(blob_file):
            return np.load(blob_file)
        data = compute_function()
        np.save(blob_file, data)
        return data

    def _get_nested_blob_analysis_dataset(
            self,
            dset_name: str,
            compute_function: Callable[[Any], np.ndarray],
            keyword_args: Dict[str, int]
    ):
        blob_folder = os.path.join(self.blob_root, dset_name)
        file_name_from_args = '_'.join([f'{key}_{keyword_args[key]}'
                                        for key in sorted(keyword_args.keys())])
        blob_file = os.path.join(blob_folder, file_name_from_args + '.npy')
        if os.path.exists(blob_file):
            return np.load(blob_file)
        data = compute_function(**keyword_args)
        os.makedirs(blob_folder, exist_ok=True)
        np.save(blob_file, data)
        return data

    @abstractmethod
    def get_links(self, frame: int) -> np.ndarray:
        ...

    @abstractmethod
    def get_trajectories_non_filament(self, minimum_image: bool) -> np.ndarray:
        ...

    @abstractmethod
    def get_positions_of_filaments_at_frames(
            self,
            frames: Sequence[int],
            minimum_image: bool
    ) -> np.ndarray:
        ...

    @abstractmethod
    def get_densities_gaussian_kde_scipy(
            self,
            frame: int,
            bandwidth: float
    ) -> gaussian_kde:
        ...

    @abstractmethod
    def get_filaments(self) -> List[List[Filament]]:
        ...

    @abstractmethod
    def get_trajectories_filaments(self, minimum_image: bool) -> np.ndarray:
        """
        Get trajectories of filaments. Filaments are represented by multiple coordinates,
        which corresponds to coordinates of beads in bead chains (e.g. from simulations
        with the ``bead_state_model`` framework)
        , or start and end points
        of segments in segment representations of filaments (e.g. from simulations with
        the ``cytosim`` framework).
        Which coordinates belong to which filament can be figured out with the return
        value of the ``get_filaments`` method.

        :param minimum_image: Set ``True`` to project coordinates that exceed
           the simulation box back into the simulation box.
        :return: Numpy array with 3 dimensions:
           (number of frames, number of filament particles, xyz-coordinates).
        """
        ...

    @abstractmethod
    def read_simulation_box(self) -> np.ndarray:
        ...
