from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from .._pipeline import Pipeline
from ...analysis.microrheology.plateau_modulus import G0Data, compute_G0_via_saddle_point
from ...file_io.tables import merge_and_save_table
from ...tools.experiment_configuration import ExperimentConfiguration


class _GPipeline(Pipeline, ABC):

    def __init__(
            self, experiment_configuration: ExperimentConfiguration,
    ):
        super().__init__(experiment_configuration)
        self.skip = experiment_configuration.skip_n_frames

    @abstractmethod
    def get_omegas_and_Gs(self, *args, **kwargs):
        ...

    def _plot_Gs(
            self,
            omegas: List[np.ndarray],
            Gs: List[np.ndarray],
            save_file_name: str=None
    ) -> Tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots(1, 1)
        for i, g in enumerate(self.experiment_configuration.experiment_iterator):
            color = g.color
            label = g.latex_label
            omega = omegas[i]
            G = Gs[i]
            ax.plot(omega, G.real, '-', color=color, label=label)
            ax.plot(omega, G.imag, '--', color=color)

        _GPipeline._decorate_G_plot(ax)
        if save_file_name is not None:
            ax.legend(loc='upper left')
            fig.tight_layout()
            fig.savefig(save_file_name)
        return fig, ax

    def _plot_Gs_with_G0s(
            self,
            omegas: List[np.ndarray],
            Gs: List[np.ndarray],
            G0s: List[G0Data],
            save_file_name: str=None
    ) -> Tuple[plt.Figure, plt.Axes]:
        fig, ax = self._plot_Gs(omegas, Gs)
        _GPipeline._add_G0s_to_plot(ax, G0s, color='C2', label='$G_0$')
        if save_file_name is None:
            return fig, ax
        # fig.legend('off')
        fig.legend(loc='upper left', bbox_to_anchor=(0.14, 0.97))
        fig.tight_layout()
        fig.savefig(save_file_name)
        return fig, ax

    @staticmethod
    def _decorate_G_plot(ax: plt.Axes):
        ax.set(
            xlabel=r'frequency $\omega / (1/t_0)$',
            ylabel='moduli $G / (\\mathrm{kT}/x_0^3))$',
            xscale='log',
            yscale='log',
        )

    @staticmethod
    def _add_G0s_to_plot(ax: plt.Axes, G0s: List[G0Data],
                         color: str, label: str):
        omegas = [G0.omega for G0 in G0s if G0 is not None]
        _G0s = [G0.G0 for G0 in G0s if G0 is not None]
        ax.scatter(omegas, _G0s, c=color, zorder=100, label=label)

    def _create_G0_results_table(self) -> pd.DataFrame:
        index = self._create_group_index_with_skip_index()
        df = pd.DataFrame(index=index, columns=["omega", "G0"])
        return df

    def _create_group_index_with_skip_index(self):
        group_index = self.experiment_configuration.experiment_iterator.create_index_from_groups()
        arrays = [group_index.get_level_values(i) for i in range(group_index.nlevels)]
        arrays.append(pd.Index([self.skip] * len(self.experiment_configuration.experiment_iterator),
                               name='frames skipped'))
        for i in range(len(arrays)):
            a = arrays[i]
            if a.dtype == np.float:
                arrays[i] = pd.Series(a).round(decimals=3)
        index = pd.MultiIndex.from_arrays(arrays)
        return index

    def _find_G0_via_saddle_point_method(
            self, omegas,
            Gs, save_file_name: str
    ) -> List[G0Data]:
        G0_results = self._create_G0_results_table()
        G0s = []
        for i in range(len(omegas)):
            g0 = compute_G0_via_saddle_point(omegas[i], Gs[i])
            G0s.append(g0)
            if g0 is not None:
                G0_results.iloc[i] = g0.omega, g0.G0
        merge_and_save_table(save_file_name, G0_results)
        return G0s
