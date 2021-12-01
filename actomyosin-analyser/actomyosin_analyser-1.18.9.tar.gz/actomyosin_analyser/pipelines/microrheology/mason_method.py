from typing import Tuple, List
import os

import numpy as np

from ._g_pipeline import _GPipeline
from .bead_msd import BeadMSD
from ...analysis.microrheology.mason_method import compute_G_advanced, compute_G_danny_seara
from ...tools.experiment_configuration import ExperimentConfiguration


class MasonMethod(_GPipeline):

    def __init__(self, experiment_configuration: ExperimentConfiguration,
                 skip: int,
                 method: str,
                 overwrite: bool=False):
        super().__init__(experiment_configuration, skip)
        self.plot_files.update({
            'G': os.path.join(experiment_configuration['GMason'], f'G_{method}.svg'),
            'G0': os.path.join(experiment_configuration['G0Mason'], f'G_with_G0_{method}.svg')
        })
        self.output_files.update({
            'G0': os.path.join(experiment_configuration['G0Mason'], f'G0_{method}.csv')
        })
        self._bead_msd = BeadMSD(experiment_configuration, skip, overwrite)
        self.skip = skip
        if method not in ['maier', 'seara']:
            raise ValueError("method can only be 'maier' or 'seara'")
        self._method = method
        if overwrite:
            self._remove_output_files()

    def run_analysis(self, **kwargs):
        omegas, Gs = self.get_omegas_and_Gs(**kwargs)
        self._plot_Gs(omegas, Gs, self.plot_files['G'])
        G0s = self._find_G0_via_saddle_point_method(omegas, Gs, self.output_files['G0'])
        self._plot_Gs_with_G0s(omegas, Gs, G0s, self.plot_files['G0'])

    def _validate_configuration(self):
        assert "GMason" in self.experiment_configuration
        assert "G0Mason" in self.experiment_configuration

    def get_omegas_and_Gs(self, **kwargs) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        if 'kT' not in kwargs:
            kwargs['kT'] = 1
        if 'dimensionality' not in kwargs:
            kwargs['dimensionality'] = 3
        msd_data = self._bead_msd.get_ensemble_msds()
        if self._method == 'maier':
            compute_function = compute_G_advanced
        elif self._method == 'seara':
            compute_function = compute_G_danny_seara
        else:
            raise RuntimeError("method has to be 'maier' or 'seara'")
        omegas, Gs = [], []
        groups = self.experiment_configuration.experiment_iterator
        for i, group in enumerate(groups):
            lag_time, msd = msd_data.get_lag_time_and_msd(i)
            r = msd_data.bead_radii[i]
            omega, G = compute_function(lag_time, msd, r, **kwargs)
            omegas.append(omega)
            Gs.append(G)
        return omegas, Gs
