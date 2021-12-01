import os
from multiprocessing import Pool
from typing import Sequence

import numpy as np
from actomyosin_analyser.tools.experiment_iterator import GroupIterator, Simulation

from actomyosin_analyser.tools.group_results_container import GroupResultsContainer

from actomyosin_analyser.tools.experiment_configuration import ExperimentConfiguration

from actomyosin_analyser.pipelines._pipeline import Pipeline

EndToEndContainer = GroupResultsContainer[np.ndarray]


class EndToEndDistance(Pipeline):

    def __init__(self, experiment_configuration: ExperimentConfiguration, n_processes: int=1):
        super().__init__(experiment_configuration)
        self._blob_folder = os.path.join(experiment_configuration['EndToEndDistance'], 'blobs')
        self._n_processes = n_processes

    def run_analysis(self, frames: Sequence[int], n_beads: int) -> EndToEndContainer:
        return self.get_end_to_end_distances(frames, n_beads)

    def _validate_configuration(self):
        assert "EndToEndDistance" in self.experiment_configuration

    def get_end_to_end_distances(
            self,
            frames: Sequence[int],
            n_beads: int
    ) -> EndToEndContainer:
        container = EndToEndContainer()

        for group in self.experiment_configuration.experiment_iterator.groups:
            e2e = self._get_end_to_end_distances_of_group(group, frames, n_beads)
            container[group] = e2e

        return container

    def _get_end_to_end_distances_of_group(
            self,
            group: GroupIterator,
            frames: Sequence[int],
            n_beads: int
    ) -> np.ndarray:
        simulations = [sim for sim in group]

        caller = _E2ECaller(frames, n_beads)

        pool = Pool(self._n_processes)
        results = pool.map(
            caller,
            simulations
        )

        e2e_distances = np.concatenate(results)
        return e2e_distances


class _E2ECaller:

    def __init__(self, frames: Sequence[int], n_beads: int):
        self.frames = frames
        self.n_beads = n_beads

    def __call__(self, simulation: Simulation) -> np.ndarray:
        e2e_distances = []
        a = simulation.analyser

        for f in self.frames:
            e2e_f = a.get_end_to_end_distances(f, self.n_beads)
            e2e_distances.append(e2e_f)

        return np.concatenate(e2e_distances)
