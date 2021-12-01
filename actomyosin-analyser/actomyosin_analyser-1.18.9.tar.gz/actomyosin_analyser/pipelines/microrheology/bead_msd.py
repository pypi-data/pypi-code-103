from typing import Tuple, List, Any, Union
import os
import json
import logging

import h5py
import matplotlib.pyplot as plt
import numpy as np
from .._pipeline import Pipeline
from ...analysis.mean_squared_displacement import MeanSquaredDisplacement
from ...tools.experiment_configuration import ExperimentConfiguration
from ...tools.experiment_iterator import Simulation, GroupIterator

logger = logging.getLogger(__name__)


class BeadMSD(Pipeline):

    def __init__(self, experiment_configuration: ExperimentConfiguration,
                 overwrite: bool = False):
        super().__init__(experiment_configuration)
        self.skip = experiment_configuration.skip_n_frames
        self.plot_files.update({
            'MSD': os.path.join(experiment_configuration['MSD'], 'ensemble_msds.svg'),
        })
        self.output_files.update({
            'MSD': os.path.join(experiment_configuration['MSD'], 'msd_ensemble.h5'),
        })

        if overwrite:
            self._remove_output_files()

    def run_analysis(self) -> Tuple[plt.Figure, plt.Axes]:
        msd_data = self.get_ensemble_msds()
        fig, ax = self._plot_msds(msd_data)
        return fig, ax

    def _validate_configuration(self):
        assert "MSD" in self.experiment_configuration

    def get_ensemble_msds(self) -> 'EnsembleMSDData':
        iterator = self.experiment_configuration.experiment_iterator
        data = EnsembleMSDData()
        for group in iterator:
            selected_simulations = [sim for sim in group]
            msd_ensemble = self._get_ensemble_msds_group(group, selected_simulations)

            radius, bead_diffusion_const = self._load_bead_diffusion_const(selected_simulations[0])
            data.append_data(
                msd_ensemble.lag_time,
                msd_ensemble.msd,
                radius,
                bead_diffusion_const,
                group.latex_label,
                group.color
            )
        return data

    def _plot_msds(self, data: 'EnsembleMSDData') -> Tuple[plt.Figure, plt.Axes]:
        filename = self.plot_files['MSD']
        fig, ax = data.plot(filename)
        return fig, ax

    def _load_bead_diffusion_const(self, sim: Simulation) -> Tuple[float, float]:
        dr = sim.data_reader
        if hasattr(dr, 'read_bead_diffusion_constant') and hasattr(dr, 'read_bead_radius'):
            return dr.read_bead_radius(), dr.read_bead_diffusion_constant()
        init_idx = dr.read_parameter('initial_state_index')
        format_string = BeadMSD._get_network_config_format_string(self.experiment_configuration.root_folder)
        init_config = format_string.format(init_idx)
        with open(init_config, 'rt') as fh:
            radius = json.load(fh)['acceptance_rate_handler']['bead_radius']
            bead_diffusion_const = 0.5 / radius
        return radius, bead_diffusion_const

    def _get_ensemble_msds_group(self, group: GroupIterator,
                                 selected_simulations) -> MeanSquaredDisplacement:
        h5_group_template = group.get_label_from_values() + f"_skip_{self.skip}"
        h5_group_name = h5_group_template.format(**group.values)
        filename = self.output_files['MSD']
        lag_time, msd_ensemble, var_ensemble = BeadMSD._load_ensemble_msds(filename, h5_group_name)
        if lag_time is not None:
            logger.info(f"Loaded MSD data of group {group.label} from file.")
            return MeanSquaredDisplacement(np.arange(1, len(lag_time)+1), msd_ensemble, var_ensemble, lag_time)

        logger.info(f"Computing MSD data of {group.label}, will save to file for next use.")
        msds = self._get_individual_msds(selected_simulations)
        lag_time = msds[0].lag_time
        msd_ensemble = self._get_mean_of_individuals(msds)
        BeadMSD._write_ensemble_msds(filename, h5_group_name, lag_time, msd_ensemble.msd, msd_ensemble.variance_of_msd)
        return msd_ensemble

    @staticmethod
    def _get_mean_of_individuals(msds: List[MeanSquaredDisplacement]) -> MeanSquaredDisplacement:
        mean_msd = np.full((len(msds), len(msds[0].msd)), np.nan)

        for i in range(len(msds)):
            mean_msd[i] = msds[i].msd

        var_msd = np.nanvar(mean_msd, axis=0)
        mean_msd = np.nanmean(mean_msd, axis=0)

        return MeanSquaredDisplacement(msds[0].lag, mean_msd, var_msd, msds[0].lag_time)

    @staticmethod
    def _write_ensemble_msds(filename, h5_group_name, lag_time, msd_ensemble, var_ensemble):
        with h5py.File(filename, 'a') as msds_file:
            h5_group = msds_file.create_group(h5_group_name)
            h5_group['log_msd'] = msd_ensemble
            h5_group['variance_of_msd'] = var_ensemble
            h5_group['log_lag_time'] = lag_time

    @staticmethod
    def _load_ensemble_msds(
            filename: str,
            h5_group_name: str
    ) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[None, None, None]]:
        if not os.path.exists(filename):
            return None, None, None
        with h5py.File(filename, 'r') as msds_file:
            if h5_group_name not in msds_file:
                return None, None, None
            h5_group = msds_file[h5_group_name]
            if 'log_msd' not in h5_group:
                return None, None, None
            if 'variance_of_msd' not in h5_group:
                return None, None, None
            return h5_group['log_lag_time'][:], h5_group['log_msd'][:], h5_group['variance_of_msd'][:]

    def _get_individual_msds(
            self, simulations: List[Simulation]
    ) -> List[MeanSquaredDisplacement]:
        lag_time = None
        msds = []
        for sim in simulations:
            a = sim.analyser
            n_non_filament = a.get_offset_filaments()
            msds_sim = a.get_msd(list(range(n_non_filament)), non_filament=True, skip=self.skip)

            t = a.get_time()
            delta_t = t[1] - t[0]
            lags = msds_sim[0].lag
            if lag_time is None:
                lag_time = lags * delta_t
            else:
                assert (lag_time == lags * delta_t).all()
            for msd_i in msds_sim:
                msd_i.lag_time = lag_time
            msds += msds_sim
        return msds

    @staticmethod
    def _get_network_config_format_string(root_folder: str) -> str:
        for i in range(6):
            guessed_folder_name = os.path.join(root_folder, 'initial_states', f'network{"0" * i}')
            if os.path.exists(guessed_folder_name):
                return os.path.join(root_folder, 'initial_states', 'network{:0' + str(i) + '}',
                                    'config.json')
        raise RuntimeError("Unable to guess folder name of initial network, tried initial_states/"
                           "network0 to initial_states/network000000. This algorithm checks only for up to"
                           " 6 digits.")


class EnsembleMSDData:

    def __init__(self):
        self.lag_times = []
        self.msds = []
        self.bead_radii = []
        self.bead_diffusion_constants = []
        self.labels = []
        self.colors = []

    def append_data(self, lag_time, msd, bead_radius, bead_diffusion_constant, label, color):
        self.lag_times.append(lag_time)
        self.msds.append(msd)
        self.bead_radii.append(bead_radius)
        self.bead_diffusion_constants.append(bead_diffusion_constant)
        self.labels.append(label)
        self.colors.append(color)

    def get_lag_time_and_msd(self, index: int) -> Tuple[np.ndarray, np.ndarray]:
        return self.lag_times[index], self.msds[index]

    @property
    def length(self) -> int:
        return len(self.lag_times)

    def plot(self, filename: str) -> Tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots(1, 1)

        global_max = 0
        for i in range(self.length):
            msd = self.msds[i]
            global_max = max(global_max, msd.max())
            ax.plot(
                self.lag_times[i],
                msd,
                color=self.colors[i],
                label=self.labels[i]
            )
        colors, unique_free_diffusions = self._get_unique_free_diffusions()
        for i, (c, u) in enumerate(zip(colors, unique_free_diffusions)):
            label = 'free diff.' if i == 0 else None
            ax.plot(self.lag_times[i], u, '--', color=c,
                    label=label, zorder=1, alpha=0.7)

        ax.set(
            xscale='log',
            yscale='log',
            xlabel='lag time $\\tau / t_0$',
            ylabel='MSD $\\langle \\Delta r^2 \\rangle / x_0^2$',
        )
        # ax.legend(bbox_to_anchor=[1.05, 1.0], loc='upper left')
        ax.legend(
            loc='upper left',  # bbox_to_anchor=(0.5, 1.05),
            ncol=2
        )
        ylim = ax.get_ylim()
        ax.set_ylim(ylim[0], global_max * 1.2)
        fig.tight_layout()
        fig.savefig(filename)
        return fig, ax

    def _get_unique_free_diffusions(self) -> Tuple[List[Any], List[np.ndarray]]:
        diff_consts = np.array(self.bead_diffusion_constants)
        uniques = np.unique(diff_consts)
        if len(uniques) == 1:
            return ['black'], [6 * self.lag_times[0] * uniques[0]]
        elif len(uniques) == self.length:
            return (self.colors,
                    [6 * self.lag_times[i] * self.bead_diffusion_constants[i] for i in range(self.length)])
        raise RuntimeError("Can only handle cases where all beads have same size or all beads have different size."
                           f" Your experiment has {self.length} ensemble MSDs "
                           f"and {len(uniques)} different bead sizes.")
