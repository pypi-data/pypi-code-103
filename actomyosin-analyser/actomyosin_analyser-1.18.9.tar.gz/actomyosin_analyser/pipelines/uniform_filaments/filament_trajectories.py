import os
from typing import Union, List, Tuple, Dict, Any

import h5py
import numpy as np
import matplotlib.pyplot as plt

from actomyosin_analyser.pipelines._pipeline import Pipeline
from actomyosin_analyser.pipelines.time import Time
from actomyosin_analyser.tools.experiment_configuration import ExperimentConfiguration
from actomyosin_analyser.tools.experiment_iterator import GroupIterator
from actomyosin_analyser.analysis.analyser import Analyser




class FilamentTrajectories(Pipeline):

    def __init__(self, experiment_configuration: ExperimentConfiguration):
        super().__init__(experiment_configuration)
        self.output_files.update({
            'SelectedTrajectories': os.path.join(experiment_configuration['FilamentTrajectories'],
                                                 'selected_trajectories.h5')
        })
        self.plot_files.update({
            'RandomSetOfTrajectories': os.path.join(experiment_configuration['FilamentTrajectories'],
                                                    'random_trajectories_{label}.svg')
        })

    def _validate_configuration(self):
        assert "FilamentTrajectories" in self.experiment_configuration

    def run_analysis(self, fixed_filament_length: int,
                     use_beads_of_filament: Union[List[int], np.ndarray]) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        return self.get_trajectories(fixed_filament_length, use_beads_of_filament)

    def get_trajectories(
            self, fixed_filament_length: int,
            use_beads_of_filament: Union[List[int], np.ndarray]
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        groups = self.experiment_configuration.experiment_iterator.groups
        times, trajectories = [], []
        for g in groups:
            time, traj = self.get_trajectories_of_single_group(
                g, fixed_filament_length,
                use_beads_of_filament
            )
            times.append(time)
            trajectories.append(traj)
        return times, trajectories

    def get_trajectories_of_single_group(
            self, group,
            fixed_filament_length,
            use_beads_of_filament
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get trajectories of filaments of a group of simulations. The beads of the
        filaments are selected via `use_beads_of_filaments`. The beads per filament
        has to be fixed, this number has to be specified via parameter `fixed_filament_length`.

        :return: (0) time. 1D array of time stamps.
                 (1) trajectories. 4D array of filament bead trajectories.
                     Dimensions: (0) Number of simulations in group,
                                 (1) number of recorded frames,
                                 (2) number of particles (len(use_beads_of_filament) * n_filaments)
                                 (3) 2 or 3 spatial coordinates (x, y, z)
        """
        time, traj = self._load_trajectories(group, fixed_filament_length, use_beads_of_filament)
        if traj is not None:
            return time, traj
        time = Time(self.experiment_configuration).get_time(group)
        traj = self._read_trajectories(group, fixed_filament_length, use_beads_of_filament)
        self._save_trajectories(time, traj, group, fixed_filament_length, use_beads_of_filament)
        return time, traj

    def plot_random_set_of_trajectories(self, trajectories: List[np.ndarray], n_trajectories: int,
                                        plot_kwargs: Dict[str, Any]={}):
        groups = self.experiment_configuration.experiment_iterator.groups
        for i in range(len(groups)):
            g = groups[i]
            traj = trajectories[i]
            self._plot_random_set_of_trajectories_group(traj, g, n_trajectories, plot_kwargs)

    def _plot_random_set_of_trajectories_group(self, trajectories: np.ndarray,
                                               group: GroupIterator, n_trajectories: int,
                                               plot_kwargs: Dict[str, Any]={}):
        _number_of_simulations = trajectories.shape[0]
        _number_of_particles = trajectories.shape[2]
        sim = np.random.randint(0, _number_of_simulations, n_trajectories)
        particle = np.random.randint(0, _number_of_particles, n_trajectories)
        selected_trajectories = trajectories[sim, :, particle]
        offset = selected_trajectories[:, 0, :]
        selected_trajectories = selected_trajectories - offset[:, None, :]

        fig, ax = plt.subplots(1, 1)

        for traj in selected_trajectories:
            ax.plot(traj[:, 0], traj[:, 1], **plot_kwargs)

        ax.set(
            aspect='equal',
            xlabel='x / x0',
            ylabel='y / x0',
            title=group.label
        )
        label = group.get_label_from_values()
        fname = self.plot_files['RandomSetOfTrajectories'].format(label=label)
        fig.tight_layout()
        fig.savefig(fname)

    @staticmethod
    def _read_trajectories(group: GroupIterator,
                           fixed_filament_length: int,
                           use_beads_of_filament: Union[List[int], np.ndarray]):
        trajectories = None
        mask = None
        for i, sim in enumerate(group):
            a = sim.analyser  # type: Analyser
            traj_i = a.get_trajectories_filaments(minimum_image=False)
            if mask is None:
                assert traj_i.shape[1] % fixed_filament_length == 0
                mask = []
                for b in use_beads_of_filament:
                    mask += list(range(b, traj_i.shape[1], fixed_filament_length))
                mask = np.array(mask)
            if trajectories is None:
                trajectories = np.full((len(group), traj_i.shape[0], len(mask), traj_i.shape[2]), np.nan)
            trajectories[i] = traj_i[:, mask]
        return trajectories

    def _load_trajectories(
            self, group: GroupIterator, fixed_filament_length: int,
            use_beads_of_filament: Union[List[int], np.ndarray]
    ) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[None, None]]:
        fname = self.output_files['SelectedTrajectories']
        if not os.path.exists(fname):
            return None, None
        with h5py.File(fname, 'r') as file:
            h5_group_name = FilamentTrajectories.create_label_from_parameters(
                fixed_filament_length,
                use_beads_of_filament
            )
            if h5_group_name not in file:
                return None, None
            h5_group = file[h5_group_name]
            label = group.get_label_from_values()
            if label not in h5_group:
                return None, None
            traj = h5_group[label]['trajectories'][:]
            time = h5_group[label]['time'][:]
        return time, traj

    def _save_trajectories(self, time: np.ndarray,
                           trajectories: np.ndarray,
                           group: GroupIterator, fixed_filament_length: int,
                           use_beads_of_filament: Union[List[int], np.ndarray]):
        with h5py.File(self.output_files['SelectedTrajectories'], 'a') as file:
            h5_group_name = FilamentTrajectories.create_label_from_parameters(fixed_filament_length,
                                                                              use_beads_of_filament)
            if h5_group_name in file:
                h5_group = file[h5_group_name]
            else:
                h5_group = file.create_group(h5_group_name)

            label = group.get_label_from_values()
            if label in h5_group:
                raise RuntimeError("trajectories of group seem to be already present "
                                   f"in {self.output_files['SelectedTrajectories']}"
                                   f":{h5_group_name}/{label}")
            h5_gg = h5_group.create_group(label)
            h5_gg['trajectories'] = trajectories
            h5_gg['time'] = time

    @staticmethod
    def create_label_from_parameters(fixed_filament_length: int,
                                     use_beads_of_filament: Union[List[int], np.ndarray]) -> str:
        if not isinstance(fixed_filament_length, int):
            raise TypeError("parameter fixed_filament_length has to be an integer")
        label = str(fixed_filament_length)
        for item in use_beads_of_filament:
            if not isinstance(item, int):
                raise TypeError("all items of list/array use_beads_of_filament have to be integers")
            label += '_' + str(item)
        return label
