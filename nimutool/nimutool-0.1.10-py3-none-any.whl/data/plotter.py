import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from typing import List


class Plotter:

    def __init__(self, savepath: Path = None):
        self.figure_data = {}
        self.savepath = savepath

    def add_df_plot(self, figure_name: str, df: pd.DataFrame, title: str, ylabel: str = None):
        subplots = self.figure_data.setdefault(figure_name, [])
        data = {'data': df, 'title': title}
        if ylabel:
            data['ylabel'] = ylabel
        subplots.append(data)

    def add_twin_plot(self, figure_name: str, data1: np.ndarray, data2: np.ndarray, columns: List[str], title: str, ylim=None):
        subplots = self.figure_data.setdefault(figure_name, [])
        data = {
            'data': pd.DataFrame(np.hstack([data1, data2]), columns=columns),
            'title': title}
        if ylim:
            data['ylim'] = ylim
        subplots.append(data)

    def add_zoomed_plots(self, figure_name: str, data1: np.ndarray, data2: np.ndarray, columns: List[str], title: str):
        self.add_twin_plot(figure_name, data1, data2, columns, title)
        if 'acc' in figure_name:
            self.add_twin_plot(f"{figure_name}_zoom0", data1, data2, columns, f"{title} zoom0", ylim=(-0.75, 0.75))
            self.add_twin_plot(f"{figure_name}_zoomg", data1, data2, columns, f"{title} zoomg", ylim=(9.7, 10))
            self.add_twin_plot(f"{figure_name}_zoomg", data1, data2, columns, f"{title} zoomg", ylim=(-9.7, -10))
        else:
            self.add_twin_plot(f"{figure_name}_zoom0", data1, data2, columns, f"{title} zoom0", ylim=(-0.2, 0.2))
            self.add_twin_plot(f"{figure_name}_zoomw", data1, data2, columns, f"{title} zoomw", ylim=(1.5, 1.7))
            self.add_twin_plot(f"{figure_name}_zoomw", data1, data2, columns, f"{title} zoomw", ylim=(-1.5, -1.7))

    def _plot_one_figure(self, figname, figdata, sharey=False, color_by_sensor=True):
        datas = [data for data in figdata if not data['data'].empty]
        if len(datas) == 0:
            return
        fig, axes = plt.subplots(nrows=len(datas), ncols=1, figsize=(18, 8), sharex=True, sharey=sharey)
        colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k', 'coral', 'skyblue', 'lime')
        markers = ['-x', '-1', '-<', '--', '->']
        for ax, plot_data in zip(axes if isinstance(axes, np.ndarray) else [axes], datas):
            if plot_data['data'].empty:
                continue
            # ax.xaxis.set_major_locator(dates.MinuteLocator(byminute=range(0,24*60,10)))
            # ax.xaxis.set_minor_locator(dates.MinuteLocator(byminute=range(0,24*60,10)))
            # ax.xaxis.set_major_formatter(dates.DateFormatter('%M:%S'))
            naxes = plot_data.get('num_axes', 3)  # by default, assume that data is coming in triads
            nsensors = max(1, len(plot_data['data'].columns) // naxes)
            plot_colors = [colors[cind] for cind in range(nsensors) for marker in markers[:naxes]]
            plot_styles = [marker for cind in range(nsensors) for marker in markers[:naxes]]
            if color_by_sensor:
                plot_data['data'].plot(ax=ax, color=plot_colors, style=plot_styles, markevery=len(plot_data['data']) // 100, ms=8)
            else:
                plot_data['data'].plot(ax=ax)
            ax.grid('on')
            plt.tight_layout()
            ax.legend(ncol=nsensors)
            if 'title' in plot_data:
                ax.set_title(plot_data['title'])
            if 'xlabel' in plot_data:
                ax.set_xlabel(plot_data['xlabel'])
            if 'ylabel' in plot_data:
                ax.set_ylabel(plot_data['ylabel'])
            if 'ylim' in plot_data:
                ax.set_ylim(plot_data['ylim'])
        if self.savepath:
            self.savepath.mkdir(exist_ok=True)
            file = self.savepath / Path(f'{figname}.png')
            print(f'saving {file}')
            fig.savefig(file)

    def plot(self, sharey=False, color_by_sensor=True):
        for name, data in self.figure_data.items():
            self._plot_one_figure(name, data, sharey, color_by_sensor)
