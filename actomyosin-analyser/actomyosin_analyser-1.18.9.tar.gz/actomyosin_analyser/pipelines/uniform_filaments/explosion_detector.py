from typing import List, Union
import os

import numpy as np
import pandas as pd

from .displacement_distribution import DisplacementDistribution, _GaussFitResult
from .filament_trajectories import FilamentTrajectories
from .._pipeline import Pipeline
from ..time import Time
from ...tools.experiment_configuration import ExperimentConfiguration
from ...tools.experiment_iterator import GroupIterator

_BooleanArray = np.ndarray


class ExplosionDetector(Pipeline):

    def run_analysis(self, fixed_filament_length: int, n_bins_histogram: int):
        displacement_pipeline = DisplacementDistribution(self.experiment_configuration)
        gauss_fits = displacement_pipeline.get_gauss_fits(fixed_filament_length, n_bins_histogram)
        passed_gauss_fit_check = self._perform_gauss_fit_check(gauss_fits)
        passed_filament_displacement_check = self._perform_filament_displacement_check(gauss_fits,
                                                                                       passed_gauss_fit_check,
                                                                                       fixed_filament_length)

        self._write_results_table(passed_gauss_fit_check, passed_filament_displacement_check)

    def get_number_of_displacements_exceeding_threshold(self, group, sigma, fixed_filament_length) -> np.ndarray:
        threshold = sigma * self.sigma_threshold_single_filaments
        exceeding = self._compute_number_of_displacements_exceeding_threshold(group, threshold, fixed_filament_length)
        return exceeding

    def _validate_configuration(self):
        assert "ExplosionCheck" in self.experiment_configuration

    def __init__(self, experiment_configuration: ExperimentConfiguration,
                 sigma_threshold_gauss_fit: float=5.,
                 sigma_threshold_single_filaments: float=5.,
                 threshold_n_exceeding_per_filament: int=2,
                 threshold_n_filaments_exceeding_per_simulation: int=2,
                 skip_n_frames: int=5):
        super().__init__(experiment_configuration)
        self.sigma_threshold_gauss_fit = sigma_threshold_gauss_fit
        self.sigma_threshold_single_filaments = sigma_threshold_single_filaments
        self.threshold_n_exceeding_per_filament = threshold_n_exceeding_per_filament
        self.threshold_n_filaments_exceeding_per_simulation = threshold_n_filaments_exceeding_per_simulation
        self.skip_n_frames = skip_n_frames

        self.output_files.update({
            "ExplosionCheck": os.path.join(self.experiment_configuration["ExplosionCheck"], 'explosion_check.csv')
        })
        self.trajectories_pipeline = FilamentTrajectories(experiment_configuration)

    def _perform_gauss_fit_check(self, gauss_fits: List[_GaussFitResult]) -> List[bool]:
        results = []
        for i, group in enumerate(self.experiment_configuration.experiment_iterator.groups):
            fit_result = gauss_fits[i]
            if fit_result is None:
                results.append(False)
                continue
            sigma = fit_result.optimized_parameters[1]
            r = self._gauss_fit_check_single_group(sigma, group)
            results.append(r)

        return results

    def _gauss_fit_check_single_group(self, sigma: float, group: GroupIterator) -> bool:
        t = Time(self.experiment_configuration).get_time(group)
        diff_t = t[1:] - t[:-1]
        if not np.isclose(diff_t, diff_t[0]).all():
            raise RuntimeError("Can't handle dynamic time deltas / frame rates.")
        delta_t = diff_t[0]
        expected_sigma = np.sqrt(6 * delta_t)
        if sigma > self.sigma_threshold_gauss_fit*expected_sigma:
            return False
        return True

    def _write_results_table(self, passed_gauss_fit_check: List[bool],
                             passed_filament_displacement_check: List[bool]):
        passed_gauss_fit_check = np.array(passed_gauss_fit_check)
        passed_filament_displacement_check = np.array(passed_filament_displacement_check)
        table = pd.DataFrame(index=self.experiment_configuration.experiment_iterator.create_index_from_groups(),
                             columns=['all checks passed', 'Gauss-fit-check passed',
                                      'filament-displacement-check passed'])
        table['Gauss-fit-check passed'] = passed_gauss_fit_check
        table['filament-displacement-check passed'] = passed_filament_displacement_check
        table['all checks passed'] = (passed_filament_displacement_check & passed_gauss_fit_check)

        table.to_csv(self.output_files["ExplosionCheck"])

    def _perform_filament_displacement_check(self, gauss_fits: List[_GaussFitResult],
                                             passed_previous_checks: List[bool],
                                             fixed_filament_length: int) -> List[Union[bool, None]]:
        groups = self.experiment_configuration.experiment_iterator.groups
        results = []
        for i, group in enumerate(groups):
            if not passed_previous_checks[i]:
                results.append(None)
                continue
            gf = gauss_fits[i]
            sigma = gf.optimized_parameters[1]
            r = self._filament_displacement_check_single_group(group, sigma, fixed_filament_length)
            results.append(r)
        return results

    def _filament_displacement_check_single_group(self, group: GroupIterator, sigma: float,
                                                  fixed_filament_length: int) -> bool:
        n_exceeding = self.get_number_of_displacements_exceeding_threshold(group, sigma, fixed_filament_length)
        n_exceeding_too_large = n_exceeding > self.threshold_n_exceeding_per_filament
        n_filaments_exceeding = np.sum(n_exceeding_too_large, axis=1)
        if (n_filaments_exceeding > self.threshold_n_filaments_exceeding_per_simulation).any():
            return False
        return True

    def _compute_number_of_displacements_exceeding_threshold(
            self, group, threshold, fixed_filament_length) -> np.ndarray:
        times, trajectories = self.trajectories_pipeline.get_trajectories_of_single_group(
            group, fixed_filament_length, [0, fixed_filament_length - 1])

        n_particles = trajectories.shape[2]

        displacements = np.abs(trajectories[:, self.skip_n_frames + 1:] - trajectories[:, self.skip_n_frames: -1])
        boolean = displacements > threshold
        n_exceeded = np.sum(boolean, axis=(1, 3))

        heads = n_exceeded[:, np.arange(0, n_particles, 2)]
        tails = n_exceeded[:, np.arange(1, n_particles, 2)]
        total = heads + tails

        return total
        # sim_fil_indices_exceeding = np.zeros((n_simulations, n_filaments), dtype=bool)
        # return sim_fil_indices_exceeding

