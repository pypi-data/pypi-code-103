"""
Visualization
-------------
The ``maica.data.visualization`` module provides various visualization tools for dataset analysis and evaluations.
This module was implemented based on ``matplotlib`` to serve a unified interface.
"""


import numpy
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.manifold import SpectralEmbedding
from maica.core.env import *
from maica.util.analysis import get_error_dist


def plot_pred_result(fig_name: str,
                     targets: numpy.ndarray,
                     preds: numpy.ndarray,
                     font_size: int = 16,
                     min_val: float = None,
                     max_val: float = None):
    if min_val is None:
        min_val = numpy.minimum(numpy.min(targets), numpy.min(preds))
        min_val -= 0.2 * min_val

    if max_val is None:
        max_val = numpy.maximum(numpy.max(targets), numpy.max(preds))
        max_val += 0.2 * max_val

    plt.tight_layout()
    plt.rcParams.update({'font.size': font_size})
    plt.title('Scatter Plot of Prediction Results')
    plt.xlabel('Target value')
    plt.ylabel('Predicted value')
    plt.grid(linestyle='--')
    plt.xlim([min_val, max_val])
    plt.ylim([min_val, max_val])
    plt.plot([min_val, max_val], [min_val, max_val], 'k', zorder=2)
    plt.scatter(targets, preds, edgecolor='k', zorder=3)
    plt.savefig(fig_name, bbox_inches='tight', dpi=500)
    plt.close()
