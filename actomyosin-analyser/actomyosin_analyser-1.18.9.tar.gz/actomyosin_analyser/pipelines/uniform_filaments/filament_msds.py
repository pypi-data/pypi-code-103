from typing import Union, List, Tuple
import os
from multiprocessing.pool import ThreadPool
import logging

import h5py
import numpy as np

from actomyosin_analyser.pipelines._pipeline import Pipeline
from actomyosin_analyser.pipelines.uniform_filaments.filament_trajectories import FilamentTrajectories
from actomyosin_analyser.tools.experiment_configuration import ExperimentConfiguration
from actomyosin_analyser.tools.experiment_iterator import GroupIterator

logger = logging.getLogger(__name__)


class FilamentMSDs(Pipeline):

    def __init__(self, experiment_configuration: ExperimentConfiguration, overwrite: bool=False):
        super().__init__(experiment_configuration)
        self._trajectories = FilamentTrajectories(experiment_configuration)
        self.output_files.update({
            'SelectedMSDs': os.path.join(experiment_configuration['FilamentMSDs'],
                                         'selected_msds.h5')
        })
        self.skip = experiment_configuration.skip_n_frames

        if overwrite:
            self._remove_output_files()

    def run_analysis(self, fixed_filament_length: int, use_beads_of_filament: Union[List[int], np.ndarray],
                     number_of_parallel_processes: int = 1) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
        return self.get_msds(fixed_filament_length, use_beads_of_filament, number_of_parallel_processes)

    def _validate_configuration(self):
        assert 'FilamentMSDs' in self.experiment_configuration

    def get_msds(self, fixed_filament_length: int, use_beads_of_filament: Union[List[int], np.ndarray],
                 number_of_parallel_processes: int = 1) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
        if number_of_parallel_processes > 1:
            return self._get_msds_parallel(number_of_parallel_processes,
                                           fixed_filament_length, use_beads_of_filament)
        lag_times, msds, variances = [], [], []
        for group in self.experiment_configuration.experiment_iterator:
            lag_time, msd, var_msd = self.get_msds_of_single_group(group, fixed_filament_length,
                                                                   use_beads_of_filament)
            lag_times.append(lag_time)
            msds.append(msd)
            variances.append(var_msd)
        return lag_times, msds, variances

    def get_msds_of_single_group(
            self, group: GroupIterator,
            fixed_filament_length: int,
            use_beads_of_filament: Union[List[int], np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        h5_group_name = FilamentTrajectories.create_label_from_parameters(
            fixed_filament_length, use_beads_of_filament
        )
        lag_time, msd, var_msd = self._load_msds(group, h5_group_name)
        if lag_time is not None:
            return lag_time, msd, var_msd
        time, trajectory = self._trajectories.get_trajectories_of_single_group(
            group, fixed_filament_length, use_beads_of_filament
        )
        if self.skip == 0:
            lag_time = time[1:]
        else:
            lag_time = time[1:-self.skip]
        trajectory = trajectory[:, self.skip:]
        msd, var_msd = self._compute_msds_of_single_group(trajectory)
        self._save_msds_of_single_group(group, h5_group_name, lag_time, msd, var_msd)
        return lag_time, msd, var_msd

    @staticmethod
    def _compute_msds_of_single_group(
            trajectory: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        _number_of_simulations = trajectory.shape[0]
        _number_of_frames = trajectory.shape[1]
        shape = (_number_of_simulations,
                 _number_of_frames - 1)
        msd = np.empty(shape)
        var_msd = np.empty(shape)
        for lag in range(1, _number_of_frames):
            diff = trajectory[:, lag:] - trajectory[:, :-lag]
            displacements = (diff ** 2).sum(3)
            d_reshaped = displacements.reshape((displacements.shape[0], -1))
            msd[:, lag - 1] = np.mean(d_reshaped, axis=1)
            var_msd[:, lag - 1] = np.var(d_reshaped, axis=1)
        return msd, var_msd

    def _load_msds(
            self, group: GroupIterator,
            h5_group_name: str
    ) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray],
               Tuple[None, None, None]]:
        fname = self.output_files["SelectedMSDs"]
        if not os.path.exists(fname):
            return None, None, None
        with h5py.File(fname, 'r') as file:
            group_skip_name = f'frames_skipped_{self.skip}'
            if group_skip_name not in file:
                return None, None, None
            group_skip = file[group_skip_name]
            if h5_group_name not in group_skip:
                return None, None, None
            h5_group = group_skip[h5_group_name]
            label = group.get_label_from_values()
            if label not in h5_group:
                return None, None, None
            msd = h5_group[label]['msd'][:]
            lag_time = h5_group[label]['lag_time'][:]
            var_msd = h5_group[label]['var_msd'][:]
        return lag_time, msd,  var_msd

    def _save_msds_of_single_group(
            self, group: GroupIterator,
            h5_group_name: str,
            lag_time: np.ndarray,
            msd: np.ndarray,
            var_msd: np.ndarray
    ):
        with h5py.File(self.output_files["SelectedMSDs"], 'a') as file:
            name_group_skip = f'frames_skipped_{self.skip}'
            if name_group_skip in file:
                group_skip = file[name_group_skip]
            else:
                group_skip = file.create_group(name_group_skip)
            if h5_group_name in group_skip:
                h5_group = group_skip[h5_group_name]
            else:
                h5_group = group_skip.create_group(h5_group_name)
            label = group.get_label_from_values()
            if label in h5_group:
                raise RuntimeError("msd of group seem to be already present "
                                   f"in {self.output_files['SelectedTrajectories']}"
                                   f":{h5_group_name}/{label}")
            h5_gg = h5_group.create_group(label)
            h5_gg['msd'] = msd
            h5_gg['lag_time'] = lag_time
            h5_gg['var_msd'] = var_msd

    def _get_msds_parallel(
            self,
            number_of_parallel_processes,
            fixed_filament_length,
            use_beads_of_filament
    ) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
        lag_times, msds, variances = [], [], []
        groups = self.experiment_configuration.experiment_iterator
        h5_group_name = FilamentTrajectories.create_label_from_parameters(
            fixed_filament_length, use_beads_of_filament
        )
        for group in groups:
            t, msd, var_msd = self._load_msds(group, h5_group_name)
            lag_times.append(t)
            msds.append(msd)
            variances.append(var_msd)

        groups_not_loaded = []
        indices_not_loaded = []
        for i, group in enumerate(groups):
            if lag_times[i] is None:
                groups_not_loaded.append(group)
                indices_not_loaded.append(i)

        lag_times_compute, trajectories = [], []
        for group in groups_not_loaded:
            t, traj = self._trajectories.get_trajectories_of_single_group(
                group,
                fixed_filament_length,
                use_beads_of_filament
            )
            t = t[1:-self.skip]
            traj = traj[:, self.skip:]
            lag_times_compute.append(t)
            trajectories.append(traj)

        pool = ThreadPool(number_of_parallel_processes)
        results = pool.map(FilamentMSDs._compute_msds_of_single_group, trajectories)

        for i, idx in enumerate(indices_not_loaded):
            lag = lag_times_compute[i]
            msd, var_msd = results[i]
            group = groups_not_loaded[i]
            self._save_msds_of_single_group(group, h5_group_name,
                                            lag, msd, var_msd)
            lag_times[idx] = lag
            msds[idx] = msd
            variances[idx] = var_msd
        return lag_times, msds, variances
