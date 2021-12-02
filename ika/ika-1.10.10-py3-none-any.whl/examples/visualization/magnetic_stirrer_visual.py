from pathlib import Path
from typing import Union, List, Tuple

from hein_utilities.datetime_utilities import datetimeManager
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from ika.magnetic_stirrer import MagneticStirrer
from .data_visualization import plot_axes, find_stable_against_known_custom_one_window, plot_plateau


class MagneticStirrerVisual(MagneticStirrer):
    """
    Subclass with additional functions to plot temperature over time graphs
    """
    _unit_seconds = datetimeManager._unit_seconds
    _unit_minutes = datetimeManager._unit_minutes
    _unit_hours = datetimeManager._unit_hours

    def __init__(self,
                 device_port: str,
                 save_path: Path = None,
                 datetime_format: str = '%Y_%m_%d_%H_%M_%S_%f',
                 safe_connect: bool = True,
                 ):
        super().__init__(
            device_port=device_port,
            save_path=save_path,
            datetime_format=datetime_format,
            safe_connect=safe_connect,
        )
        self.figure, self.axes = plt.subplots(nrows=1, ncols=1)

    def graph_temperature_time(self,
                               x_axis_units: Union[_unit_seconds, _unit_minutes, _unit_hours] = _unit_minutes,
                               scatter: bool = False,
                               line: bool = True,
                               ) -> Figure:
        graph_title = 'Temperature over time'

        # axis names
        x_axis_name = None
        if x_axis_units == self._unit_seconds:
            x_axis_name = 'Time (s)'
        elif x_axis_units == self._unit_minutes:
            x_axis_name = 'Time (min)'
        elif x_axis_units == self._unit_hours:
            x_axis_name = 'Time (hour)'
        y_axis_name = self.probe_temperature_column_heading

        times = self.state_data[x_axis_name].tolist()
        temperatures = self.state_data[self.probe_temperature_column_heading].tolist()

        axes = self.axes
        figure = self.figure
        axes = plot_axes(axes=axes,
                         x=times,
                         y=temperatures,
                         axes_name=graph_title,
                         x_axis_label=x_axis_name,
                         y_axis_label=y_axis_name,
                         scatter=scatter,
                         line=line,
                         )
        return figure

    def graph_temperature_time_stable_visualization(self,
                                                    x_axis_units: Union[_unit_seconds, _unit_minutes, _unit_hours] = _unit_minutes,
                                                    scatter: bool = False,
                                                    line: bool = True,
                                                    ):
        n = self.n
        std_max = self.std_max
        sem_max = self.sem_max
        upper_limit = self.upper_limit
        lower_limit = self.lower_limit
        r_min = self.r_min
        slope_upper_limit = self.slope_upper_limit
        slope_lower_limit = self.slope_lower_limit

        figure = self.graph_temperature_time(x_axis_units=x_axis_units,
                                             scatter=scatter,
                                             line=line,
                                             )

        # axis names
        x_axis_name = None
        if x_axis_units == self._unit_seconds:
            x_axis_name = 'Time (s)'
        elif x_axis_units == self._unit_minutes:
            x_axis_name = 'Time (min)'
        elif x_axis_units == self._unit_hours:
            x_axis_name = 'Time (hour)'

        times = self.state_data[x_axis_name].tolist()
        x_values = times
        temperatures = self.state_data[self.probe_temperature_column_heading].tolist()
        y_values = temperatures

        axes = figure.axes[0]
        y_max = max(temperatures)
        y_min = min(temperatures)

        total_range = y_max - y_min
        if upper_limit < 1 and self.relative_limits is True:
            upper_limit = self.upper_limit * total_range
        if lower_limit < 1 and self.relative_limits is True:
            lower_limit = self.lower_limit * total_range

        for temperature in self.set_temperatures:
            plateau_points: List[Tuple] = find_stable_against_known_custom_one_window(
                x=x_values,
                y=y_values,
                window_size=n,
                known=temperature,
                upper_limit=upper_limit,
                lower_limit=lower_limit,
                std_max=std_max,
                sem_max=sem_max,
                r_min=r_min,
                slope_upper_limit=slope_upper_limit,
                slope_lower_limit=slope_lower_limit,
            )
            axes = plot_plateau(
                axes=axes,
                plateau_points=plateau_points,
                y_min=y_min,
                y_max=y_max
            )

        return figure

    def save_graph_stable_visualized(self,
                                     file_name: str = None,
                                     ):
        figure = self.graph_temperature_time_stable_visualization()
        self.save_graph(figure=figure, file_name=file_name)

    def save_graph(self,
                   figure: Figure = None,
                   file_name: str = None,
                   ) -> Path:
        """
        Save the graph as a png

        :param matplotlib.figure.Figure, figure:
        :param str, file_name: title for the graph file

        :return:
        """
        if figure is None:
            figure = self.graph_temperature_time()
        if file_name is None:
            file_name = 'temperature_time_graph.png'
        if file_name[-4:] != '.png':
            file_name += '.png'
        graph_save_path: Path = self.save_path.joinpath(file_name)
        figure.savefig(f'{str(graph_save_path)}', bbox_inches='tight')
        return graph_save_path