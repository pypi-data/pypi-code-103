from typing import List, Tuple, Union
import os

import h5py
import numpy as np
import matplotlib.pyplot as plt
from ._pipeline import Pipeline
from .time import Time
from ..tools.experiment_configuration import ExperimentConfiguration
from ..tools.experiment_iterator import GroupIterator
from ..analysis.analyser import Analyser


class Energy(Pipeline):

    def __init__(self, experiment_configuration: ExperimentConfiguration):
        super().__init__(experiment_configuration)
        self.plot_files.update({
            "energy": os.path.join(experiment_configuration["Energy"], 'energy.svg'),
            "individual_energies": os.path.join(experiment_configuration["Energy"],
                                                "energies_{label}.svg")
        })
        self.output_files.update({
            "energy": os.path.join(experiment_configuration['Energy'], 'energy.h5')
        })

    def run_analysis(self):
        times, energies = self.get_energies()
        self._plot_energies(times, energies)

    def _validate_configuration(self):
        assert "Energy" in self.experiment_configuration

    def get_mean_energies(self) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        times, mean_energies = [], []
        for group in self.experiment_configuration.experiment_iterator.groups:
            t, me = self._get_time_and_mean_energies_group(group)
            times.append(t)
            mean_energies.append(me)
        return times, mean_energies

    def _get_time_and_mean_energies_group(
            self,
            group: GroupIterator
    ) -> Tuple[np.ndarray, np.ndarray]:
        time, mean_e = self._load_time_and_mean_energies(group.get_label_from_values())
        if time is not None:
            return time, mean_e
        time = Time(self.experiment_configuration).get_time(group)
        energies = Energy._get_group_energy(group)
        mean_energies = energies.mean(0)
        self._save_time_and_mean_energies(
            group.get_label_from_values(),
            time, mean_energies
        )
        return time, mean_energies

    def get_energies(self) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        times = []
        energies = []
        iterator = self.experiment_configuration.experiment_iterator
        for group in iterator:
            time = Time(self.experiment_configuration).get_time(group)
            times.append(time)
            e_group = Energy._get_group_energy(group)
            energies.append(e_group)
        return times, energies

    @staticmethod
    def _get_group_energy(group: GroupIterator) -> np.ndarray:
        energy = None
        for i, sim in enumerate(group):
            a = sim.analyser  # type: Analyser
            e_i = a.get_energies_stretch_and_bend()
            k_bend = a.data_reader.read_parameter('k_bend')
            k_stretch = a.data_reader.read_parameter('k_stretch')
            e_i[:, 0] = e_i[:, 0] * k_stretch
            e_i[:, 1] = e_i[:, 1] * k_bend
            if energy is None:
                shape = [len(group)] + list(e_i.shape)
                energy = np.full(shape, np.nan)
            energy[i] = e_i
        return energy

    def _plot_energies(self, times: List[np.ndarray], energies: List[np.ndarray]):
        groups = self.experiment_configuration.experiment_iterator.groups
        fig, ax = plt.subplots(1, 1)
        label_stretch = '$E_\\mathrm{stretch}$, '
        label_bend = '$E_\\mathrm{bend}$, '
        for i in range(len(groups)):
            group = groups[i]
            color = group.color
            if color is None:
                color = f'C{i}'
            label = group.label
            e = energies[i]
            t = times[i]
            self._plot_individual_energies(e, group)
            mean_e = e.mean(0)
            ax.plot(t, mean_e[:, 0], '--', color=color, label=label_stretch)
            ax.plot(t, mean_e[:, 1], '-', color=color, label=label_bend + label)
            label_stretch = None
            label_bend = ''
        ax.legend()
        ax.set(
            xlabel='$t/t_0$',
            ylabel='$\\langle E \\rangle$ /kT',
            title="Energy"
        )
        fig.tight_layout()
        fig.savefig(self.plot_files['energy'])



    def _plot_individual_energies(self, energies: np.ndarray, group: GroupIterator):
        fig, ax = plt.subplots(1, 1)
        label = group.label
        file_label = group.get_label_from_values()
        label_stretch = '$E_\\mathrm{stretch}$'
        label_bend = '$E_\\mathrm{bend}$'
        for i, e_i in enumerate(energies):
            color = f'C{i}'
            ax.plot(e_i[:, 0], '--', color=color, label=label_stretch)
            ax.plot(e_i[:, 1], '-', color=color, label=label_bend)
            label_stretch = None
            label_bend = None
        ax.set(
            xlabel='frame',
            ylabel='$E$ / kT',
            title=label
        )
        ax.legend()
        fig.tight_layout()
        filename = self.plot_files['individual_energies'].format(label=file_label)
        fig.savefig(filename)

    def _load_time_and_mean_energies(
            self,
            group_label: str
    ) -> Union[Tuple[None, None], Tuple[List[np.ndarray], List[np.ndarray]]]:
        if not os.path.exists(self.output_files['energy']):
            return None, None
        with h5py.File(self.output_files['energy'], 'r') as file:
            if 'mean' not in file:
                return None, None
            mean_h5 = file['mean']
            if group_label not in mean_h5:
                return None, None
            times = mean_h5[group_label]['time'][:]
            mean_energies = mean_h5[group_label]['mean_energy'][:]
        return times, mean_energies

    def _save_time_and_mean_energies(
            self,
            group_label: str,
            times: np.ndarray,
            mean_energies: np.ndarray
    ):
        with h5py.File(self.output_files['energy'], 'w') as file:
            mean_h5 = file.create_group('mean')
            g_h5 = mean_h5.create_group(group_label)
            g_h5['time'] = times
            g_h5['mean_energy'] = mean_energies
