from dataclasses import dataclass
from typing import List, Tuple, Union
import os

import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from .filament_trajectories import FilamentTrajectories
from .._pipeline import Pipeline
from ...tools.experiment_configuration import ExperimentConfiguration
from ...tools.experiment_iterator import GroupIterator


class DisplacementDistribution(Pipeline):

    def run_analysis(self, fixed_filament_length: int, n_bins: int):
        histograms = self.get_displacement_histograms(fixed_filament_length, n_bins)
        gauss_fit_results = self.get_gauss_fits(fixed_filament_length, n_bins, histograms)
        self._plot_histograms(histograms, gauss_fit_results)

    def _validate_configuration(self):
        assert "FilamentDisplacement" in self.experiment_configuration

    def __init__(self, experiment_configuration: ExperimentConfiguration):
        super().__init__(experiment_configuration)
        self.output_files.update({
            "Histograms": os.path.join(self.experiment_configuration["FilamentDisplacement"],
                                       'displacement_histograms.h5')
        })
        self.plot_files.update({
            "Histogram": os.path.join(self.experiment_configuration["FilamentDisplacement"],
                                       'displacement_histogram_{label}.svg')
        })
        self.pipeline_trajectories = FilamentTrajectories(experiment_configuration)


    def get_displacement_histograms(
            self, fixed_filament_length: int, n_bins: int
    ) -> List['_HistogramData']:
        histograms = []
        for g in self.experiment_configuration.experiment_iterator:
            hg = self._get_histogram_group(g, fixed_filament_length, n_bins)
            histograms.append(hg)
        return histograms

    def _get_histogram_group(
            self, group: GroupIterator,
            fixed_filament_length: int,
            n_bins: int
    ) -> '_HistogramData':
        group_label = group.get_label_from_values()
        edges, histogram = self._load_histogram_group(group_label, fixed_filament_length, n_bins)
        if edges is not None:
            return _HistogramData(edges, histogram)
        time, trajectories = self.pipeline_trajectories.get_trajectories_of_single_group(
            group, fixed_filament_length, use_beads_of_filament=[0, fixed_filament_length-1])
        displacements = trajectories[:, 1:] - trajectories[:, :-1]
        histogram, edges = np.histogram(displacements.flatten(), bins=n_bins, density=True)

        self._save_histogram_group(group_label, fixed_filament_length, n_bins, edges, histogram)

        return _HistogramData(edges, histogram)

    def _load_histogram_group(
            self, label: str,
            fixed_filament_length: int,
            n_bins: int
    ) -> Union[Tuple[None, None], Tuple[np.ndarray, np.ndarray]]:
        filename = self.output_files["Histograms"]
        if not os.path.exists(filename):
            return None, None
        with h5py.File(filename, 'r') as h5_file:
            if label not in h5_file:
                return None, None
            group = h5_file[label]

            if group.attrs['fixed_filament_length'] != fixed_filament_length:
                raise ValueError(f"fixed_filament_length {group.attrs['fixed_filament_length']} stored in file is "
                                 f"different from your specified parameter ({fixed_filament_length}). A group has only one"
                                 " unambiguous filament length.")
            if str(n_bins) not in group:
                return None, None

            edges = group[str(n_bins)]['edges'][:]
            histogram = group[str(n_bins)]['histogram'][:]

        return edges, histogram

    def _save_histogram_group(self, label: str, fixed_filament_length: int,
                              n_bins: int, edges: np.ndarray, histogram: np.ndarray):
        filename = self.output_files["Histograms"]
        with h5py.File(filename, 'a') as h5_file:
            if label not in h5_file:
                group = h5_file.create_group(label)
                group.attrs['fixed_filament_length'] = fixed_filament_length
            else:
                group = h5_file[label]
                if group.attrs['fixed_filament_length'] != fixed_filament_length:
                    raise ValueError(f"fixed_filament_length {group.attrs['fixed_filament_length']} stored in file is "
                                     f"different from your specified parameter ({fixed_filament_length}). A group" 
                                     " has only one unambiguous filament length.")
            s_n_bins = str(n_bins)
            if s_n_bins in group:
                group_n = group[s_n_bins]
            else:
                group_n = group.create_group(s_n_bins)

            group_n['edges'] = edges
            group_n['histogram'] = histogram

    def _plot_histograms(self, histograms: List['_HistogramData'], gauss_fits: List['_GaussFitResult']):
        groups = self.experiment_configuration.experiment_iterator.groups
        for i, g in enumerate(groups):
            hist = histograms[i]
            gauss = gauss_fits[i]
            fig, ax = plt.subplots(1, 1)
            ax.step(hist.x, hist.histogram, where='mid')
            if gauss is not None:
                ax.plot(hist.x, gauss.predict(hist.x), label='gauss fit')
                ax.legend()
            ax.set(
                title=g.label,
                xlabel='displacements / $x_0$',
                ylabel='density'
            )
            fig.tight_layout()
            figname = self.plot_files['Histogram'].format(label=g.get_label_from_values())
            fig.savefig(figname)
            plt.close(fig)


    def get_gauss_fits(
            self, fixed_filament_length: int,
            n_bins: int, histograms: List['_HistogramData']=None
    ) -> List['_GaussFitResult']:
        if histograms is None:
            histograms = self.get_displacement_histograms(fixed_filament_length, n_bins)
        results = []
        for hist in histograms:
            r = _GaussFitResult.create_from_fit(hist.x, hist.histogram)
            results.append(r)
        return results



@dataclass
class _GaussFitResult:

    optimized_parameters: np.ndarray
    covariance_parameters: np.ndarray

    @staticmethod
    def _gauss(x: np.ndarray, mu: float, sigma: float, a: float) -> np.ndarray:
        return a*np.exp(-(x-mu)**2/2/sigma**2)

    def predict(self, x):
        return _GaussFitResult._gauss(x, *self.optimized_parameters)

    @staticmethod
    def create_from_fit(x: np.ndarray, y: np.ndarray) -> Union['_GaussFitResult', None]:
        try:
            popt, pcov = curve_fit(_GaussFitResult._gauss, x, y)
            return _GaussFitResult(popt, pcov)
        except RuntimeError:
            return None

    @property
    def error(self):
        return np.sqrt(np.diag(self.covariance_parameters))


@dataclass
class _HistogramData:
    edges: np.ndarray
    histogram: np.ndarray

    @property
    def x(self) -> np.ndarray:
        return (self.edges[1:] + self.edges[:-1]) / 2

