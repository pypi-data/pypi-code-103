import pandas as pd
import numpy as np
import scipy.stats as stats

import warnings

import matplotlib.pyplot as plt

import bluebelt.core.helpers
import bluebelt.core.decorators

import bluebelt.data.resolution

import bluebelt.styles

@bluebelt.core.decorators.class_methods
class Effort():
    """
    Calculate the planning effort
    """
    def __init__(self, series, rule='iso_jaar-iso_week', **kwargs):
        
        self.series = series
        self.rule = rule

        self.calculate()

    def calculate(self):
        
        self.inter = bluebelt.data.resolution.GroupByDatetimeIndex(self.series, rule=self.rule).inter_scale().result
        self.intra = bluebelt.data.resolution.GroupByDatetimeIndex(self.series, rule=self.rule).intra_scale().result
        

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self.series.size:1.0f}, inter={self.inter.mean():1.4f}, intra={self.intra.mean():1.4f})')
    
    def plot(self, **kwargs):
        
        return _effort_plot(self, **kwargs)

def _effort_plot(_obj, **kwargs):
        
    style = kwargs.pop('style', bluebelt.styles.paper)
    title = kwargs.pop('title', f'{_obj.series.name} effort plot')
    
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (0, None))
    
    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    # bluebelt.core.graph.area(series=_obj.inter, ax=axes, style=style, label='inter')
    # bluebelt.core.graph.area(series=_obj.intra, ax=axes, style=style, label='intra')
    axes.fill_between(_obj.inter.index, 0, _obj.inter.values, **style.planning.fill_between_inter, label='inter')
    axes.plot(_obj.inter, **style.planning.plot_inter, **kwargs)

    axes.fill_between(_obj.intra.index, 0, _obj.intra.values, **style.planning.fill_between_intra, label='intra')
    axes.plot(_obj.intra, **style.planning.plot_intra, **kwargs)

    # format things
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    
    # title
    axes.set_title(title, **style.graphs.line.title)

    # legend
    axes.legend(loc='upper left')

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig