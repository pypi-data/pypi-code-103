from typing import List
import os
import numpy as np
import matplotlib.pyplot as plt
from .._pipeline import Pipeline
from ...tools.experiment_configuration import ExperimentConfiguration
from ...tools.experiment_iterator import GroupIterator


class BeadDisplacement(Pipeline):

    def __init__(self, experiment_configuration: ExperimentConfiguration):
        super().__init__(experiment_configuration)
        self.plot_files.update({
            'BeadDisplacement': os.path.join(experiment_configuration['BeadDisplacement'],
                                             'bead_displacement_{label}.svg')
        })

    def _validate_configuration(self):
        assert "BeadDisplacement" in self.experiment_configuration

    def run_analysis(self, *args, **kwargs):
        displacements = self._get_displacements()
        self._plot_displacements(displacements)

    def _get_displacements(self) -> List[List[np.ndarray]]:
        displacements = []
        for group in self.experiment_configuration.experiment_iterator:
            displacements_group = BeadDisplacement._get_displacements_group(group)
            displacements.append(displacements_group)
        return displacements

    @staticmethod
    def _get_displacements_group(group: GroupIterator) -> List[np.ndarray]:
        displacements = []
        for sim in group:
            a = sim.analyser
            pos = a.get_trajectories_non_filament()[:, 0]
            displacements_sim = np.sqrt(np.sum((pos[1:] - pos[:-1])**2, axis=1))
            displacements.append(displacements_sim)
        return displacements

    def _plot_displacements(self, displacements: List[List[np.ndarray]]):
        groups = self.experiment_configuration.experiment_iterator.groups
        for i, g in enumerate(groups):
            fig, ax = plt.subplots(1, 1)
            title = g.label
            file_label = g.get_label_from_values()
            d_group = displacements[i]
            for d, idx in zip(d_group, g.index):
                ax.plot(d, label=f'sim {idx:03}')
            ax.set(
                title=title,
                xlabel='frame',
                ylabel='displacements / $x_0$'
            )
            fig.tight_layout()
            filename = self.plot_files['BeadDisplacement'].format(label=file_label)
            fig.savefig(filename)

