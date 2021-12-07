from dataclasses import dataclass, field
from itertools import cycle

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter

matplotlib.use('Pdf')


@dataclass(frozen=True, order=True, repr=False)
class PlotLevel:
    compare_value: int = field(init=False, repr=False, compare=True)
    string_representation: str = field(repr=True, init=True, compare=False)

    def __post_init__(self):
        mapping = {'all': 10, 'summary': 5, 'nothing': 0}
        try:
            object.__setattr__(self, 'compare_value', mapping[self.string_representation])
        except KeyError:
            raise ValueError(f"'{self.string_representation}' is not a correct plot level, "
                             f" should be a value from {', '.join(mapping.keys())}")

    def __str__(self) -> str:
        return self.string_representation

    def __repr__(self) -> str:
        return self.string_representation


PLOT_ALL = PlotLevel('all')
PLOT_SUMMARY = PlotLevel('summary')
PLOT_NOTHING = PlotLevel('nothing')


def histogram(values,
              name,
              title,
              xlab,
              ylab,
              color,
              xmin,
              xmax,
              binwidth,
              plot_type,
              xaxisticks=None,
              thresholds=None,
              ylog_scale=False):
    """
    General function to create a histogram for the given values.
    """
    assert xmin <= xmax
    plt.figure(figsize=(10, 10))
    plt.hist(values, alpha=0.5, color=color, bins=np.arange(xmin, xmax+2)-binwidth/2)
    if ylog_scale:
        plt.yscale('log')
        axes = plt.gca()
        axes.yaxis.set_major_formatter(ScalarFormatter())
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    xaxisticks = xaxisticks if xaxisticks else 1
    xlabs = [i for i in np.arange(xmin, xmax+1) if i % xaxisticks == 0]
    if not xlabs or not xlabs[0] == xmin:
        xlabs.insert(0, xmin)
    if not xlabs or not xlabs[-1] == xmax:
        xlabs.append(xmax)
        # Check if second to last xlabel is too close to last xlabel
        if xlabs[-2] >= xmax - xaxisticks/2:
            xlabs.pop(-2)
    plt.xticks(xlabs)
    plt.xlim([xmin-1, xmax+1])
    if thresholds:
        thresholds = list(thresholds)
        plt.axvline(x=thresholds.pop(0), color='gold')
        styling = cycle([{'color': 'darkorange', 'ls': 'dotted'},
                         {'color': 'chocolate', 'ls': 'solid'}])
        offset = cycle([0.2, -0.2])
        while thresholds:
            options = next(styling)
            plt.axvline(x=thresholds.pop()+next(offset), **options)
    plt.tight_layout()
    plt.savefig(name + f'.histogram.{plot_type}', format=plot_type)
    plt.close()


def barplot(x_values,
            height,
            name,
            title,
            xlab,
            ylab,
            color,
            plot_type,
            xaxisticks=None,
            hide_xlabels=False):
    plt.figure(figsize=(10, 10))
    plt.bar(x_values, height, align='center', alpha=0.5, color=color)
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    xaxisticks = xaxisticks if xaxisticks else 1
    xlabs = [i for n, i in enumerate(x_values) if n % xaxisticks == 0 or n == 0]
    plt.xticks(xlabs, xlabs)
    if hide_xlabels:
        plt.gca().get_xaxis().set_visible(not hide_xlabels)
    plt.tight_layout()
    plt.savefig(name + f'.barplot.{plot_type}', format=plot_type)
    plt.close()


def scatterplot(x_values,
                y_values,
                name,
                title,
                xlab,
                ylab,
                color,
                plot_type,
                rotate_xlabels=False,
                marker='o'):
    plt.figure(figsize=(10, 10))
    plt.scatter(x_values, y_values, alpha=0.5, color=color, marker=marker)
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.ylim(ymin=0)
    plt.xlim(xmin=0)
    if rotate_xlabels:
        plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(name + f'.scatter.{plot_type}', format=plot_type)
    plt.close()
