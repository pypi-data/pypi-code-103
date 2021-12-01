import os
from dataclasses import dataclass
from multiprocessing import Pool
from typing import Tuple, List, Sequence, Union

import numpy as np
from scipy.stats import gaussian_kde
import pandas as pd

from actomyosin_analyser.analysis.polymer_density import GridGenerator
from actomyosin_analyser.pipelines._pipeline import Pipeline
from actomyosin_analyser.tools.experiment_configuration import ExperimentConfiguration
from actomyosin_analyser.tools.experiment_iterator import GroupIterator, Simulation
from actomyosin_analyser.tools.group_results_container import GroupResultsContainer


class AveragePolymerDensity(Pipeline):

    def __init__(
            self,
            experiment_configuration: ExperimentConfiguration,
            number_of_processes: int
    ):
        super().__init__(experiment_configuration)

        self.output_files.update({
            "densities": os.path.join(experiment_configuration["ActinDensity"],
                                      "density.h5"),
            'bandwidth_table': os.path.join(experiment_configuration["ActinDensity"],
                                            "kde_bandwidths.h5")
        })
        self._n_processes = number_of_processes

    def run_analysis(
            self,
            frames: Sequence[int],
            x_grid_parameters: Tuple[float, float, int],
            y_grid_parameters: Tuple[float, float, int],
            z_grid_parameters: Tuple[float, float, int],
    ) -> '_DensityResults':
        """
        Computes actin density on specified grid. Gaussian kernel density
        estimate is used to estimate densities on the grid.
        Grid parameters have to be a tuple of starting point (float), ending point(float),
        and number of points (int) along the length from start to end.
        """
        return self.get_densities(
            frames,
            x_grid_parameters,
            y_grid_parameters,
            z_grid_parameters
        )

    def _validate_configuration(self):
        assert "ActinDensity" in self.experiment_configuration

    def get_densities(
            self,
            frames: Sequence[int],
            x_grid_parameters: Tuple[float, float, int],
            y_grid_parameters: Tuple[float, float, int],
            z_grid_parameters: Tuple[float, float, int],
            same_bandwidth_across_groups: bool=False
    ) -> '_DensityResults':
        """
        Computes actin density on specified grid. Gaussian kernel density
        estimate is used to estimate densities on the grid.
        Grid parameters have to be a tuple of starting point (float), ending point(float),
        and number of points (int) along the length from start to end.
        """
        gg = GridGenerator(x_grid_parameters, y_grid_parameters, z_grid_parameters)
        densities = _DensityResults()
        bandwidth = None
        bandwidth_hash = None

        groups = self.experiment_configuration.experiment_iterator.groups
        if same_bandwidth_across_groups:
            group = groups[0]
            dens = self.get_densities_of_group(group, gg, frames, bandwidth, bandwidth_hash)
            densities[group] = dens
            bandwidth = dens.bandwidth
            bandwidth_hash = dens.bandwidth_hash
            remaining_groups = groups[1:]
        else:
            remaining_groups = groups[:]

        pool = Pool(self._n_processes)

        average_density_getter = _AverageDensityGetter(
            self.experiment_configuration["ActinDensity"], frames,
            gg, bandwidth, bandwidth_hash
        )

        dens_results = pool.map(average_density_getter, remaining_groups)

        for i, g in enumerate(remaining_groups):
            densities[g] = dens_results[i]

        return densities

    def get_densities_of_group(
            self,
            group: GroupIterator,
            grid: 'GridGenerator',
            frames: Sequence[int],
            bandwidth: Union[None, float],
            bandwidth_hash: Union[None, int]
    ) -> 'KDEResult':
        adg = _AverageDensityGetter(
            self.experiment_configuration["ActinDensity"], frames,
            grid, bandwidth, bandwidth_hash
        )
        dens = adg(group)
        return dens


@dataclass
class KDEResult:
    densities: List[np.ndarray]
    bandwidth: float
    bandwidth_hash: int
    grid_generator: GridGenerator

    def __getitem__(self, index: int) -> np.ndarray:
        return self.densities[index]


@dataclass
class _AverageDensityGetter:
    results_folder: str
    frames: Sequence[int]
    grid_generator: GridGenerator
    bandwidth: Union[None, float]
    bandwidth_hash: Union[None, int]

    def __call__(self, group: GroupIterator) -> 'KDEResult':
        return self._get_average_densities_single_group(group)

    def _get_average_densities_single_group(
            self,
            group: GroupIterator,
    ) -> 'KDEResult':
        avg_densities = []

        bandwidth = self.bandwidth
        bandwidth_hash = self.bandwidth_hash
        for f in self.frames:
            avg_f, bandwidth, bandwidth_hash = self._get_average_densities_at_frame(
                group,
                f,
                bandwidth,
                bandwidth_hash
            )
            avg_densities.append(avg_f)
        return KDEResult(avg_densities, bandwidth, bandwidth_hash, self.grid_generator)

    def _get_average_densities_at_frame(
            self,
            group: GroupIterator,
            frame: int,
            bandwidth: float,
            bandwidth_hash: int
    ) -> Tuple[np.ndarray, float, int]:
        label = group.get_label_from_values()
        avg_densities, bandwidth, bandwidth_hash = self._load_average_densities(
            label, frame, bandwidth, bandwidth_hash
        )
        if avg_densities is not None:
            print(f"loaded average densities of group {label}")
            return avg_densities, bandwidth, bandwidth_hash
        avg_densities, bandwidth, bandwidth_hash = self._compute_average_densities(
            group, frame, bandwidth, bandwidth_hash
        )
        self._save_average_densities(avg_densities, label,
                                     frame,
                                     bandwidth, bandwidth_hash)
        return avg_densities, bandwidth, bandwidth_hash

    def _compute_average_densities(
            self,
            group: GroupIterator,
            frame: int,
            bandwidth: Union[float, None],
            bandwidth_hash: Union[int, None]
    ) -> Tuple[np.ndarray, float, int]:
        simulations = [sim for sim in group]
        kdes = []
        for i, sim in enumerate(simulations):
            print(f"Computing KDE for group {group.label}, frame {frame}"
                  f"bandwidth is {bandwidth}: simulation {i+1:02}/{len(simulations)}")
            kde = self._get_kde(sim, frame, bandwidth)
            if bandwidth is None:
                bandwidth = kde.factor
            if bandwidth_hash is None:
                bandwidth_hash = hash(bandwidth)
            kdes.append(kde)

        X, Y, Z = self.grid_generator.generate()

        average_densities = np.zeros_like(X)

        for j, sim in enumerate(simulations):
            print(f"computing density for group {group.label}, frame {frame}, simulation {j+1:02}/{len(simulations)}")
            dens = self._get_density_grid_single(kdes[j], X, Y, Z)
            average_densities += dens
        average_densities /= len(simulations)

        return average_densities, bandwidth, bandwidth_hash

    def _save_average_densities(
            self,
            avg_densities: np.ndarray,
            label: str,
            frame: int,
            bandwidth: float,
            bandwidth_hash: int
    ) -> None:
        self._add_entry_to_bandwidth_table(bandwidth, bandwidth_hash, label)
        file_name, folder_name = self._construct_folder_and_file_name(bandwidth_hash, frame, label)
        os.makedirs(folder_name, exist_ok=True)
        np.save(file_name, avg_densities)

    def _construct_folder_and_file_name(self, bandwidth_hash, frame, label):
        frame_label = f'frame_{frame}'
        grid_label = f"grid_hash_{hash(self.grid_generator)}"
        bandwidth_label = f"bandwidth_hash_{bandwidth_hash}"
        folder_name = os.path.join(
            self.results_folder,
            label,
            frame_label,
            grid_label
        )
        file_name = os.path.join(folder_name, bandwidth_label)
        return file_name, folder_name

    def _add_entry_to_bandwidth_table(self, bandwidth, bandwidth_hash, label):
        table = self._load_bandwidth_table(label)
        if table is None:
            table = self._create_bandwidth_table()
        table.loc[hash(self.grid_generator)] = bandwidth_hash
        file_name = self._construct_bandwidth_table_name(label)
        dir_name = os.path.split(file_name)[0]
        os.makedirs(dir_name, exist_ok=True)
        self._write_bandwidth_to_file(bandwidth, bandwidth_hash, label)
        table['bandwidth_hash'] = table['bandwidth_hash'].astype(int)
        table.to_csv(file_name)

    def _load_bandwidth_table(self, label) -> Union[None, pd.DataFrame, object]:
        file_name = self._construct_bandwidth_table_name(label)
        if not os.path.exists(file_name):
            return None
        table = pd.read_csv(file_name, index_col=0)
        table['bandwidth_hash'] = table['bandwidth_hash'].astype(int)
        return table

    @staticmethod
    def _create_bandwidth_table() -> pd.DataFrame:
        index = pd.Series(name='grid_hash', dtype=int)
        table = pd.DataFrame(columns=['bandwidth_hash'], index=index)
        return table

    def _load_average_densities(
            self,
            label: str,
            frame: int,
            bandwidth: Union[None, float],
            bandwidth_hash: Union[None, int]
    ) -> Tuple[Union[None, np.ndarray],
               Union[None, float],
               Union[None, int]]:
        if bandwidth is None:
            bandwidth, bandwidth_hash = self._load_bandwidth_from_table(label)
        if bandwidth is None:
            return None, bandwidth, bandwidth_hash

        file_name, folder_name = self._construct_folder_and_file_name(bandwidth_hash, frame, label)
        if not os.path.exists(file_name):
            return None, bandwidth, bandwidth_hash
        return np.load(file_name), bandwidth, bandwidth_hash

    def _load_bandwidth_from_table(
            self,
            label: str
    ) -> Union[Tuple[None, None], Tuple[float, int]]:
        table = self._load_bandwidth_table(label)
        if table is None:
            return None, None
        if hash(self.grid_generator) not in table.index:
            return None, None
        bandwidth_hash = table.loc[hash(self.grid_generator)]
        bandwidth = self._load_bandwidth_from_file(label, bandwidth_hash)
        return bandwidth, bandwidth_hash

    @staticmethod
    def _get_kde(
            simulation: Simulation,
            frame: int,
            bandwidth: Union[float, None]
    ) -> gaussian_kde:
        return simulation.analyser.get_densities_gaussian_kde_scipy(frame, bandwidth)

    @staticmethod
    def _get_density_grid_single(
            kde: gaussian_kde,
            X: np.ndarray,
            Y: np.ndarray,
            Z: np.ndarray
    ) -> np.ndarray:
        positions = np.vstack([X.ravel(), Y.ravel(), Z.ravel()])
        dens = kde(positions)
        dens = dens.reshape(X.shape)
        return dens

    def _construct_bandwidth_table_name(self, label) -> str:
        return os.path.join(self.results_folder, label, 'bandwidth_hashes.csv')

    def _write_bandwidth_to_file(
            self,
            bandwidth,
            bandwidth_hash,
            label
    ) -> None:
        folder_name = os.path.join(self.results_folder, label)
        file_name = os.path.join(folder_name, f'bandwidth_{bandwidth_hash}.npy')
        os.makedirs(folder_name, exist_ok=True)
        np.save(file_name, np.array([bandwidth]))

    def _load_bandwidth_from_file(self, label: str, bandwidth_hash: int) -> float:
        folder_name = os.path.join(self.results_folder, label)
        file_name = os.path.join(folder_name, f'bandwidth_{bandwidth_hash}.npy')
        return np.load(file_name)[0]


_DensityResults = GroupResultsContainer[KDEResult]
