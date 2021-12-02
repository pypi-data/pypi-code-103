import os
import shutil
from typing import Union, List, Tuple
from datetime import timedelta
import logging
import numpy as np
import math
from scipy import stats
from matplotlib.axes._axes import Axes
import seaborn as sns

from ika.utilities import stable_against_known

"""
Global selection of the control chart aestheics and colour scheme 
more information on setting the chart aesthetics: https://seaborn.pydata.org/tutorial/aesthetics.html
selected colour scheme: https://colorbrewer2.org/?type=qualitative&scheme=Paired&n=4

run the next two lines to see what the current colour scheme looks like
    current_palette = sns.color_palette()
    sns.palplot(current_palette)
"""
sns.set(palette='colorblind')
_paired_palette = sns.color_palette(palette='Paired', n_colors=4)
_colour_1: tuple = _paired_palette[0]  # light blue
_colour_2: tuple = _paired_palette[1]  # dark blue
_colour_3: tuple = _paired_palette[2]  # light green
_colour_4: tuple = _paired_palette[3]  # dark green
sns.set_palette(_paired_palette)
sns.set_context(
    'notebook',
    rc={},
)
sns.set_style(
    style="ticks",
    rc={
        'axes.spines.right': False,
        'axes.spines.top': False,
    },
)

_point = 'o'

_solid = '-'
_dash = '--'
_dot_dash = '-.'
_dot = ':'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def plot_axes(
        axes: Axes,
        x: Union[List[float], List[timedelta]],
        y: List[float],
        axes_name: str,
        y_axis_label: str,
        x_axis_label: str = None,
        scatter: bool = True,
        scatter_style: str = _point,
        scatter_colour=_colour_2,
        line: bool = True,
        line_stye: str = _solid,
        line_colour=_colour_1,
):
    """
    Generic function for plotting data on a matplotlib axes, with the option to plot both or just one of a scatter or
    line plot of the data

    :param axes: matplotlib.axes._axes.Axes, is the axes to plot the chart onto
    :param x: 1d array of the x part of some data
    :param y: 1d array of the y part of some data
    :param str, axes_name: title for the axes chart
    :param str, y_axis_label: must be identical to the column heading that would be used in the tidy_data()
        function and thus the dataframe returned by tidy_data(), in order to extract the y data for this chart
    :param str, x_axis_label: if left as None, no x axis label will be added to the chart
    :param bool, scatter: True to add scatter points to the graph
    :param str, scatter_style:
    :param scatter_colour:
    :param bool, line: True to add a line through the points of the graph
    :param str, line_stye:
    :param line_colour:
    :return:
    """

    axes.set_title(axes_name)
    axes.set_ylabel(y_axis_label)

    if x_axis_label is not None:
        axes.set_xlabel(x_axis_label)

    # plot lines connecting points
    if line:
        sns.lineplot(x=x,
                     y=y,
                     color=line_colour,
                     ls=line_stye,
                     ax=axes,
                     markers=''
                     )
    # plot points
    if scatter:
        sns.scatterplot(x=x,
                        y=y,
                        markers=scatter_style,
                        color=scatter_colour,
                        ax=axes,
                        )

    return axes


def plot_plateau(
        axes: Axes,
        plateau_points: List[Tuple],
        y_min: float,
        y_max: float,
):
    """
    For a given axes, colour in the background based on found plateau points that indicate regions where the data for
    some graph plotted on the axes is stable. Colouring in means shading the background by a colour

    :param axes:
    :param List[Tuple], plateau_points: organized as an array of (x_ax_value_1, x_ax_value_2), where  x_ax_value_1
        is the first value along the x axis where some stable region starts, and the second value is where it ends
    :param y_min: minimum y value in the entire data set; to know the bounds for colouring in the background
    :param y_max: maximum y value in the entire data set; to know the bounds for colouring in the background
    :return:
    """
    for (plateau_start, plateau_stop) in plateau_points:
        axes.fill_between(
            x=[plateau_start, plateau_stop],
            y1=y_min,
            y2=y_max,
            color=_colour_3,
        )
    return axes


def find_stable_against_known_custom_one_window(x,
                                                y,
                                                window_size,
                                                known,
                                                upper_limit=None,
                                                lower_limit=None,
                                                std_max=None,
                                                sem_max=None,
                                                r_min=None,
                                                slope_upper_limit=None,
                                                slope_lower_limit=None,
                                                ) -> List[Tuple]:
    """

    :param x: 1d array of the x part of some data
    :param y: 1d array of the y part of some data
    :param window_size: the number of data points to pass into the function to check for stability at a time
    :param float, known: a known reference value to compare the data to
    :param float, upper_limit: how much above the known value the mean and mode of the data can be to be determined
        stable
    :param float, lower_limit: how much below the known value the mean and mode of the data can be to be determined
        stable
    :param float, std_max: maximum standard deviation the data can have to be determined as stable
    :param float, sem_max: maximum standard error the data can have to be determined as stable
    :return: plateau points, organized as an array of (x_ax_value_1, x_ax_value_2), where  x_ax_value_1
        is the first value along the x axis where some stable region starts, and the second value is where it ends
    :param float, r_min: minimum r when doing a linear regression on the data required for the data =to be
        determined as stable
    :param float, slope_upper_limit: how much above zero the slope from doing a linear regression can be in order for
        the data to be determined as stable
     :param float, slope_lower_limit: how much below zero the slope from doing a linear regression can be in order for
        the data to be determined as stable
    """

    def function(x, y) -> bool:
        return stable_against_known(
            x=x,
            y=y,
            known=known,
            upper_limit=upper_limit,
            lower_limit=lower_limit,
            std_max=std_max,
            sem_max=sem_max,
            r_min=r_min,
            slope_upper_limit=slope_upper_limit,
            slope_lower_limit=slope_lower_limit,
        )
    return find_stable_one_window(x=x, y=y, window_size=window_size, function=function)


def find_stable_against_unknown_custom_one_window(x,
                                                  y,
                                                  window_size,
                                                  range_limit,
                                                  std_max=None,
                                                  sem_max=None,
                                                  r_min=None,
                                                  slope_upper_limit=None,
                                                  slope_lower_limit=None,
                                                  ) -> List[Tuple]:
    """

    :param x: 1d array of the x part of some data
    :param y: 1d array of the y part of some data
    :param window_size: the number of data points to pass into the function to check for stability at a time
     :param float, range_limit: the maximum allowed difference between the mode and mean of the data to be determined
        as stable, and the maximum difference allowed range the data can have
    :param float, std_max: maximum standard deviation the data can have to be determined as stable
    :param float, sem_max: maximum standard error the data can have to be determined as stable
    :return: plateau points, organized as an array of (x_ax_value_1, x_ax_value_2), where  x_ax_value_1
        is the first value along the x axis where some stable region starts, and the second value is where it ends
    :param float, r_min: minimum r when doing a linear regression on the data required for the data =to be
        determined as stable
    :param float, slope_upper_limit: how much above zero the slope from doing a linear regression can be in order for
        the data to be determined as stable
     :param float, slope_lower_limit: how much below zero the slope from doing a linear regression can be in order for
        the data to be determined as stable
    """

    def function(x, y) -> bool:
        return stable_against_unknown(
            x=x,
            y=y,
            range_limit=range_limit,
            std_max=std_max,
            sem_max=sem_max,
            r_min=r_min,
            slope_upper_limit=slope_upper_limit,
            slope_lower_limit=slope_lower_limit,
        )
    return find_stable_one_window(x=x, y=y, window_size=window_size, function=function)


def find_stable_two_windows(x, y, window_size, function) -> set:
    """
    :param x: 1d array of the x part of some data
    :param y: 1d array of the y part of some data
    :param window_size: the number of data points to pass into the function to check for stability at a time
    :param function: function that returns a bool based on if the data is stable or not
    :return:
    """
    plateau_points: List[Tuple] = []
    for index in range(len(y) - (2*window_size) + 1):
        window_1 = y[index:index+window_size]
        window_2 = y[index+window_size:index+(2*window_size)]
        plateau: bool = function(data_1=window_1, data_2=window_2)
        if plateau:
            start = x[index]
            stop = x[index+(2*window_size) -1]
            point = (start, stop)
            plateau_points.append(point)
    return plateau_points


def find_stable_one_window(x, y, window_size, function) -> List[Tuple]:
    """
    :param x: 1d array of the x part of some data
    :param y: 1d array of the y part of some data
    :param window_size: the number of data points to pass into the function to check for stability at a time
    :param function: function that returns a bool based on if the data is stable or not
    :return:
    """
    plateau_points: List[Tuple] = []
    for index in range(len(y) - window_size + 1):
        window_x = x[index:index+window_size]
        window_y = y[index:index+window_size]
        plateau: bool = function(window_x, window_y)
        if plateau:
            start = x[index]
            stop = x[index + window_size-1]
            point = (start, stop)
            plateau_points.append(point)
    return plateau_points


def stable_against_unknown(x,
                           y,
                           range_limit: float = 0.1,
                           std_max: float = 0.05,
                           sem_max: float = 0.05,
                           r_min: float = None,
                           slope_upper_limit: float = None,
                           slope_lower_limit: float = None,
                           ) -> bool:
    """
    Custom method for determining if data is stable without comparison against a known value. Based on if it falls
    within some limits. For the data, it must have a standard deviation less than std_max, the difference between the
    mean and mode must be less than the range limit, and the range of the data is less than the range limit. And if the
    r value from doing a linear regression is less than r_min and the slope from doing a linear regression is
    plus/minus slope upper and lower limits.

    :param x: 1d array of the x part of some data
    :param y: 1d array of the y part of some data
    :param float, range_limit: the maximum allowed difference between the mode and mean of the data to be determined
        as stable, and the maximum difference allowed range the data can have
    :param float, std_max: maximum standard deviation the data can have to be determined as stable
    :param float, sem_max: maximum standard error the data can have to be determined as stable
    :param float, r_min: minimum r when doing a linear regression on the data required for the data =to be
        determined as stable
    :param float, slope_upper_limit: how much above zero the slope from doing a linear regression can be in order for
        the data to be determined as stable
     :param float, slope_lower_limit: how much below zero the slope from doing a linear regression can be in order for
        the data to be determined as stable
    :return:
    """
    if r_min is None:
        r_min = 0
    if slope_upper_limit is None:
        slope_upper_limit: float = 999
    if slope_lower_limit is None:
        slope_lower_limit: float = 999
    n = len(y)
    data_mean = np.mean(y)
    data_mode = stats.mode(y)
    data_mode = data_mode.mode[0]
    mean_mode_difference = abs(data_mean - data_mode)
    data_std = np.std(y)
    data_sem = data_std/(math.sqrt(n))
    range = max(y) - min(y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    mean_mode_difference_good = mean_mode_difference <= range_limit
    std_good = data_std <= std_max
    sem_good = data_sem <= sem_max
    range_good = range <= range_limit
    r_good = r_min < r_value
    slope_good = (-1 * slope_lower_limit) <= slope <= slope_upper_limit

    if mean_mode_difference_good and std_good and sem_good and range_good and r_good and slope_good:
        return True
    else:
        return False


def subset_folder_file(folder_path, step):
    """
    Create a folder with a subset of all the files in the passed in folder. The subset is determined by taking every
    file in the passed in folder, and getting every file at step intervals away from the first file
    i.e. if step is 2, then the 1st, 3rd, 5th... files will be copied into the second folder
    :param str, folder_path:
    :return:
    """
    input_folder: str = folder_path
    output_folder: str = input_folder + f'_subset_step_{step}'
    os.mkdir(output_folder)

    no_files = len(os.listdir(input_folder))

    for index, filename_with_extension in enumerate(os.listdir(input_folder)):
        if index % step == 0:
            logger.info(f'{index} out of {no_files}')
            file = os.path.join(input_folder, filename_with_extension)
            output_location = os.path.join(output_folder, filename_with_extension)
            shutil.copy(file, output_location)


