import logging
import os
from multiprocessing import Pool
from typing import List, Tuple, Union, Optional

import h5py
import numpy as np
import matplotlib.pyplot as plt
from actomyosin_analyser.tools.group_results_container import GroupResultsContainer
from scipy.stats import gaussian_kde

from ._pipeline import Pipeline
from ..tools.experiment_configuration import ExperimentConfiguration
from ..tools.experiment_iterator import GroupIterator, Simulation
from ..analysis import geometry

logger = logging.getLogger(__name__)
_KDE_XY_Pair = Tuple[np.ndarray, np.ndarray]


class LengthDistribution(Pipeline):

    def _validate_configuration(self):
        assert "SegmentLength" in self.experiment_configuration

    def __init__(self, experiment_configuration: ExperimentConfiguration,
                 n_processes: int = 1):
        super().__init__(experiment_configuration)
        self._n_processes = n_processes

        self.plot_files.update({
            "length_distributions": os.path.join(experiment_configuration["SegmentLength"],
                                                 'length_distributions_{frames}.svg')
        })
        self.output_files.update({
            "length_distributions": os.path.join(experiment_configuration["SegmentLength"],
                                                 'length_distributions.h5')
        })
        self._lengths_folder = os.path.join(experiment_configuration['SegmentLength'], 'blobs')
        os.makedirs(self._lengths_folder, exist_ok=True)

    def run_analysis(self, n_points_kde: int,
                     frames: List[int]):
        density_estimates_list = self.get_density_estimates(n_points_kde, frames)
        fig, ax = plt.subplots(len(frames), 1, sharex=True)
        self.plot_density_estimates(ax, density_estimates_list, frames)
        fig.savefig(self.plot_files["length_distributions"].format(
            frames='_'.join([str(f) for f in frames])
        ))

    def make_violin_plot(self, frames: List[int], key: str) -> Tuple[plt.Figure, plt.Axes]:
        lengths = self.get_lengths(frames)
        index = self.experiment_configuration.experiment_iterator.create_index_from_groups()

        data_arrays = []
        labels = []
        for idx in sorted(index.get_level_values(key).unique()):
            selected_groups = self.experiment_configuration.experiment_iterator.get(**{key: idx})
            if len(selected_groups) > 1:
                raise RuntimeError(f"More than one group were selected with query {key}={idx}.")
            group = selected_groups[0]
            values = lengths[group]
            data_arrays.append(values)
            labels.append(str(idx))

        fig, ax = plt.subplots(1, 1)
        ax.violinplot(data_arrays, showmeans=True)
        ax.set_xticks(list(range(1, len(labels)+1)))
        ax.set_xticklabels(labels)
        return fig, ax

    def get_lengths(self, frames: List[int]) -> GroupResultsContainer[np.ndarray]:
        container = GroupResultsContainer[np.ndarray]()
        iterator = self.experiment_configuration.experiment_iterator
        for group in iterator:
            lengths = []
            for f in frames:
                lengths_f = self.get_lengths_by_group(group, f)
                lengths.append(lengths_f)
            container[group] = np.concatenate(lengths)
        return container

    def plot_density_estimates(self, ax, density_estimates: List[List[_KDE_XY_Pair]],
                               frames: List[int]):
        for i, f in enumerate(frames):
            self._plot_distributions_single_frame(ax[i], density_estimates[i])
            if i == 0:
                ax[i].legend()
            ax[i].set(
                title=f'frame {f}',
                ylabel='density',
            )
            if i + 1 == len(frames):
                ax[i].set_xlabel('segment length / $x_0$')

    def get_density_estimates(
            self,
            n_points_kde: int,
            frames: List[int]
    ) -> List[List[_KDE_XY_Pair]]:

        result_xy_pairs = []
        for f in frames:
            result_xy_pairs.append(self._get_density_estimates_single_frame(n_points_kde, f))

        return result_xy_pairs

    def _get_density_estimates_single_frame(
            self,
            n_points_kde: int,
            frame: int
    ) -> List[_KDE_XY_Pair]:
        iterator = self.experiment_configuration.experiment_iterator
        result_xy_pairs = []
        for group in iterator:
            x, density_estimate = self._get_density_estimates_single_group(group, n_points_kde, frame)
            result_xy_pairs.append((x, density_estimate))

        return result_xy_pairs

    def _get_density_estimates_single_group(
            self,
            group: GroupIterator,
            n_points_kde: int,
            frame: int
    ) -> _KDE_XY_Pair:

        label = group.get_label_from_values()
        x, density_estimate = self._load_density_estimate(label, n_points_kde, frame)
        if x is not None:
            return x, density_estimate
        x, density_estimate = self._compute_density_estimate(group, n_points_kde, frame)
        self._save_density_estimate(x, density_estimate,
                                    label, n_points_kde, frame)
        return x, density_estimate

    def _load_density_estimate(
            self,
            label: str,
            n_points_kde: int,
            frame: int
    ) -> Union[_KDE_XY_Pair, Tuple[None, None]]:
        fname = self.output_files["length_distributions"]
        if not os.path.exists(fname):
            return None, None

        with h5py.File(fname, 'r') as file:
            if label not in file:
                return None, None
            g = file[label]
            if str(frame) not in g:
                return None, None
            gg = g[str(frame)]
            if str(n_points_kde) not in gg:
                return None, None
            ggg = gg[str(n_points_kde)]

            x = ggg['x'][:]
            de = ggg['density_estimate'][:]
            return x, de

    def _compute_density_estimate(
            self,
            group: GroupIterator,
            n_points_kde: int,
            frame: int
    ) -> _KDE_XY_Pair:
        lengths = self.get_lengths_by_group(group, frame)
        logger.warning("Saving lengths to lengths.npy, this is a debugging add-on."
                       " Remove it when bug is resolved!!")
        np.save('lengths.npy', lengths)
        kde = gaussian_kde(lengths)
        x = np.linspace(lengths.min(), lengths.max(), n_points_kde)
        return x, kde(x)

    def get_lengths_by_group(
            self,
            group: GroupIterator,
            frame: int
    ) -> np.ndarray:
        lengths = self._load_lengths(group, frame)
        if lengths is not None:
            return lengths
        lengths = self._compute_lengths(group, frame)
        self._save_lengths(lengths, group, frame)
        return lengths

    def _load_lengths(
            self,
            group: GroupIterator,
            frame: int
    ) -> Optional[np.ndarray]:
        file_name = self._get_lengths_file_name(frame, group)
        if not os.path.isfile(file_name):
            return None
        return np.load(file_name)

    def _save_lengths(
            self,
            lengths: np.ndarray,
            group: GroupIterator, frame: int
    ):
        file_name = self._get_lengths_file_name(frame, group)
        np.save(file_name, lengths)

    def _get_lengths_file_name(self, frame, group) -> str:
        file_name = os.path.join(
            self._lengths_folder,
            f'lengths_{group.get_label_from_values()}_{frame}.npy'
        )
        return file_name

    def _compute_lengths(
            self,
            group: GroupIterator,
            frame: int
    ):
        selected_simulations = [sim for sim in group]
        pool = Pool(self._n_processes)

        caller = _GetLengthsCaller(frame)

        lengths = pool.map(
            caller,
            selected_simulations
        )

        lengths = np.concatenate(lengths).flatten()
        return lengths

    def _save_density_estimate(
            self,
            x: np.ndarray,
            density_estimate: np.ndarray,
            label: str,
            n_points_kde: int,
            frame: int
    ):
        fname = self.output_files["length_distributions"]
        with h5py.File(fname, 'a') as file:
            if label in file:
                g = file[label]
            else:
                g = file.create_group(label)
            if str(frame) in g:
                gg = g[str(frame)]
            else:
                gg = g.create_group(str(frame))
            if str(n_points_kde) in gg:
                ggg = gg[str(n_points_kde)]
            else:
                ggg = gg.create_group(str(n_points_kde))

            ggg['x'] = x
            ggg['density_estimate'] = density_estimate

    def _plot_distributions_single_frame(
            self,
            ax: plt.Axes,
            density_estimate_pairs: List[_KDE_XY_Pair]
    ):
        iterator = self.experiment_configuration.experiment_iterator
        for i, group in enumerate(iterator):
            x, estimate = density_estimate_pairs[i]
            ax.plot(x, estimate, label=group.latex_label, color=group.color)


class _GetLengthsCaller:

    def __init__(self, frame: int):
        self.frame = frame

    def __call__(self, sim: Simulation) -> np.ndarray:
        return self._get_lengths_single_simulation(sim)

    def _get_lengths_single_simulation(
            self,
            simulation: Simulation
    ) -> np.ndarray:
        lengths = []
        coords = simulation.analyser.get_trajectories_filaments(minimum_image=False)[self.frame]
        filaments = simulation.analyser.get_filaments()[self.frame]

        box = simulation.analyser.data_reader.read_box_size()
        box = np.array([box[1, 0] - box[0, 0],
                        box[1, 1] - box[0, 1],
                        box[1, 2] - box[0, 2]])

        for f in filaments:
            fcoords = coords[f.items]
            v_segments = geometry.get_minimum_image_vector(
                fcoords[:-1], fcoords[1:], box)
            d = np.sqrt(np.sum(v_segments ** 2, 1))
            lengths.append(d)
        return np.array(lengths)
