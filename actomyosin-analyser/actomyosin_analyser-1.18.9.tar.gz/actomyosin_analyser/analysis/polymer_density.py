import os
from dataclasses import dataclass
from typing import Sequence, Union, Tuple

import numpy as np
import pandas as pd

from actomyosin_analyser.analysis.abstract_analyser import AbstractAnalyser


class PolymerDensityGetter:

    def __init__(
            self,
            grid: 'GridGenerator',
            analyser: AbstractAnalyser
    ):
        self._analyser = analyser
        self._results_dir = os.path.join(analyser.blob_root, 'polymer_density')
        os.makedirs(self._results_dir, exist_ok=True)
        self.grid_generator = grid

    def get(
            self,
            frames: Sequence[int],
            bandwidth: Union[float, None]
    ) -> Tuple[float, np.ndarray]:
        denstities = []
        for f in frames:
            dens, bandwidth = self._get_at_frame(f, bandwidth)
            denstities.append(dens[np.newaxis])
        return bandwidth, np.concatenate(denstities)

    def _get_at_frame(
            self,
            frame: int,
            bandwidth: Union[float, None]
    ) -> Tuple[np.ndarray, float]:
        if bandwidth is None:
            bandwidth = self._load_available_bandwidth(frame)
        density = self._load_density(frame, bandwidth)
        if density is not None:
            return density, bandwidth
        density, bandwidth = self._compute_density(frame, bandwidth)
        bandwidth = PolymerDensityGetter._emulate_loss_by_writing_and_rereading(bandwidth)
        self._save_bandwidth(frame, bandwidth)
        self._save_density(frame, density, bandwidth)
        return density, bandwidth

    def _load_density(self, frame: int, bandwidth: Union[None, float]) -> Union[None, np.ndarray]:
        if bandwidth is None:
            return None
        data_file_name = self._construct_data_file_name(frame, bandwidth)
        if not os.path.exists(data_file_name):
            return None
        return np.load(data_file_name)

    def _compute_density(
            self,
            frame: int,
            bandwidth: Union[None, float]
    ) -> Tuple[np.ndarray, float]:
        kde = self._analyser.get_densities_gaussian_kde_scipy(frame, bandwidth)
        bandwidth = kde.factor
        X, Y, Z = self.grid_generator.generate()
        positions = np.vstack([X.ravel(), Y.ravel(), Z.ravel()])
        dens = kde(positions)
        dens = dens.reshape(X.shape)
        return dens, bandwidth

    def _save_bandwidth(
            self,
            frame: int,
            bandwidth: float
    ) -> None:
        folder_name, file_name = self._construct_bandwidth_paths(
            frame, hash(bandwidth)
        )
        os.makedirs(folder_name, exist_ok=True)
        np.save(file_name, np.array([bandwidth]))
        self._add_entry_to_bandwidth_table(frame, bandwidth)

    def _construct_bandwidth_paths(
            self,
            frame: int,
            bandwidth_hash: int
    ) -> Tuple[str, str]:
        folder = self._construct_data_folder(bandwidth_hash, frame)
        file = os.path.join(folder, 'bandwidth.npy')
        return folder, file

    def _construct_data_folder(self, bandwidth_hash: int, frame):
        grid_folder = self._construct_grid_folder()
        folder = os.path.join(
            grid_folder,
            f'bandwidth_hash_{bandwidth_hash}',
            f'frame_{frame}'
        )
        return folder

    def _construct_grid_folder(self) -> str:
        return os.path.join(
            self._results_dir,
            f'grid_hash_{hash(self.grid_generator)}'
        )

    def _add_entry_to_bandwidth_table(
            self,
            frame: int,
            bandwidth: float
    ) -> None:
        grid_folder = self._construct_grid_folder()
        file = os.path.join(grid_folder, 'bandwidth_table.csv')
        if os.path.exists(file):
            table = pd.read_csv(file, index_col=0)
        else:
            table = pd.DataFrame(columns=['frame', 'bandwidth_hash'],
                                 dtype=int)
        index = 0 if len(table.index) == 0 else table.index.max()+1
        table.loc[index] = frame, hash(bandwidth)
        table.to_csv(file)

    def _save_density(
            self,
            frame: int,
            density: np.ndarray,
            bandwidth: float
    ) -> None:
        file_name = self._construct_data_file_name(frame, bandwidth)
        np.save(file_name, density)

    def _construct_data_file_name(
            self,
            frame: int,
            bandwidth: float
    ) -> str:
        data_folder = self._construct_data_folder(hash(bandwidth), frame)
        return os.path.join(
            data_folder, 'density.npy'
        )

    def _load_available_bandwidth(self, frame: int) -> Union[None, float]:
        bw_hash = self._get_bandwidth_hash_from_table(frame)
        if bw_hash is None:
            return None
        folder, file = self._construct_bandwidth_paths(frame, bw_hash)
        return np.load(file)[0]

    def _get_bandwidth_hash_from_table(self, frame: int) -> Union[None, int]:
        grid_folder = self._construct_grid_folder()
        file = os.path.join(grid_folder, 'bandwidth_table.csv')
        if not os.path.exists(file):
            return None
        table = pd.read_csv(file, index_col=0)
        at_frame = table[table['frame'] == frame]
        if len(at_frame) == 0:
            return None
        bw_hash = at_frame.iloc[0]['bandwidth_hash']
        return bw_hash

    @staticmethod
    def _emulate_loss_by_writing_and_rereading(bandwidth: float) -> float:
        tmp_file = '.tmp_bw.npy'
        np.save(tmp_file, np.array([bandwidth]))
        v = np.load(tmp_file)[0]
        os.remove(tmp_file)
        return v


@dataclass
class GridGenerator:
    """
    Handles setting up coordinates of a 3D grid.
    Spacings for each dimension have to be specified via tuples of three values:
    (minimum grid position, maximum grid position, number of equidistant
    points from min to max position (including min an max as outermost points)).
    """

    x_spacing: Tuple[float, float, int]
    y_spacing: Tuple[float, float, int]
    z_spacing: Tuple[float, float, int]

    def generate(self) -> Tuple[np.ndarray,
                                np.ndarray,
                                np.ndarray]:
        """
        Use ``numpy.mgrid`` to get arrays of X, Y, Z coordinates of points on the grid.

        :return: Tuple of 3 arrays: X, Y, Z coordinates of grid points.
        """
        X, Y, Z = np.mgrid[
                  self.x_spacing[0]: self.x_spacing[1]: self.x_spacing[2] * 1j,
                  self.y_spacing[0]: self.y_spacing[1]: self.y_spacing[2] * 1j,
                  self.z_spacing[0]: self.z_spacing[1]: self.z_spacing[2] * 1j
                  ]
        return X, Y, Z

    def __hash__(self):
        return hash((self.x_spacing, self.y_spacing, self.z_spacing))


