# Copyright (c) 2021 Mark Crowe <https://github.com/markcrowe-com>. All rights reserved.

from pandas import DataFrame
import matplotlib.pyplot as pyplot
import numpy as numpy
import seaborn as seaborn
import matplotlib.pyplot as pyplot


def plot_lines(dataframe: DataFrame, x_axis: str, y_line_configurations: list, size: list, x_axis_label: str, y_axis_label: str) -> None:
    pyplot.subplots(figsize=size)

    for column, color in y_line_configurations:
        pyplot.plot(dataframe[x_axis], dataframe[column],
                    color, label=column, marker='.')

    pyplot.xlabel(x_axis_label)
    pyplot.ylabel(y_axis_label)
    pyplot.legend()
    pyplot.show()


def display_correlation_matrix_pyramid_heatmap(correlated_dataframe: DataFrame, figure_size: tuple = (11, 9), is_drawing_duplicates: bool = False) -> tuple:
    """
    Display a correlation matrix pyramid heatmap.
    :param correlated_dataframe: The correlated dataframe to display.
    :param figure_size: The size of the figure.
    :param is_drawing_duplicates: Whether or not to draw duplicates.
    :return: The correlation matrix pyramid heatmap Figure and Axes.
    """
    figure, axes = pyplot.subplots(figsize=figure_size)

    color_map = "BrBG"  # Add diverging colormap from red to blue
    cbar_kws = {"shrink": .5}

    if is_drawing_duplicates:
        seaborn.heatmap(correlated_dataframe, annot=True, ax=axes, cmap=color_map,
                        cbar_kws=cbar_kws, linewidth=.5, square=True)
    else:
        # Exclude duplicate correlations by masking upper right values
        mask = numpy.zeros_like(correlated_dataframe, dtype=bool)
        mask[numpy.triu_indices_from(mask)] = True

        seaborn.heatmap(correlated_dataframe, annot=True, ax=axes, cmap=color_map,
                        cbar_kws=cbar_kws, linewidth=.5, square=True,
                        mask=mask)
    return figure, axes
