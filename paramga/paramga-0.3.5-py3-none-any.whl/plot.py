"""Helpers for plotting genetic algorithm outputs."""

from typing import List, Tuple
from matplotlib import pyplot as plt

from mpl_toolkits.axes_grid1 import make_axes_locatable


def plot_loss(loss_values, ax=None, fig=None):
    _fig = fig if fig is not None else plt.figure()
    _ax = ax if ax is not None else plt.axes()

    x = list(range(len(loss_values)))
    _ax.scatter(x, loss_values)
    return _fig, _ax


def plot_param(param, values, best_values, loss_values, ax=None, fig=None, vmin=0, vmax=1):
    _fig = fig if fig is not None else plt.figure()
    _ax = ax if ax is not None else plt.axes()

    population = len(values[0])
    iterations = len(values)
    x = list(range(iterations))
    for y in range(population):
        _ax.scatter(x, values[:, y], c='grey', s=2)

    _ax.plot(x, best_values, c='red', zorder=1)
    best_scatter = _ax.scatter(x, best_values, c=loss_values, vmin=vmin, vmax=vmax, zorder=2)

    _ax.set_ylabel(param)
    _ax.set_xlabel('iterations')

    divider = make_axes_locatable(_ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    _fig.colorbar(best_scatter, cax=cax, ax=_ax)
    return _fig, _ax


def plot_param_compare(
    param_a: str,
    param_b: str,
    values_a: List[float],
    values_b: List[float],
    loss_values: List[float],
    ax: plt.Axes=None,
    fig: plt.Figure=None,
    vmin: float=0,
    vmax: float=1,
    xlim: Tuple[float, float]=(0, 300),
    ylim: Tuple[float, float]=(0, 300),
):
    _fig = fig if fig is not None else plt.figure()
    _ax = ax if ax is not None else plt.axes()

    scatter = _ax.scatter(values_a, values_b, c=loss_values, vmin=vmin, vmax=vmax, zorder=1)

    _ax.set_xlabel(param_a)
    _ax.set_ylabel(param_b)

    _ax.set_xlim(xlim)
    _ax.set_ylim(ylim)

    divider = make_axes_locatable(_ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    _fig.colorbar(scatter, cax=cax, ax=_ax)
    return _fig, _ax


def plot_observed_compare(
    observed_values: List[float],
    modelled_values: List[float],
    ax: plt.Axes=None,
    fig: plt.Figure=None,
    vmin: float=0,
    vmax: float=1,
    xlim: Tuple[float, float]=(0, 300),
    ylim: Tuple[float, float]=(0, 300),
):
    _fig = fig if fig is not None else plt.figure()
    _ax = ax if ax is not None else plt.axes()

    scatter = _ax.scatter(observed_values, modelled_values, vmin=vmin, vmax=vmax, zorder=1)

    _ax.set_xlim(*xlim)
    _ax.set_ylim(*ylim)
    _ax.plot([xlim[0], xlim[1]], [ylim[0], ylim[1]])

    _ax.set_xlabel('observed')
    _ax.set_ylabel('modelled')

    # divider = make_axes_locatable(_ax)
    # cax = divider.append_axes('right', size='5%', pad=0.05)
    # _fig.colorbar(scatter, cax=cax, ax=_ax)
    return _fig, _ax
