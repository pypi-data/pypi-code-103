"""Helpers for plotting genetic algorithm outputs."""

from matplotlib import pyplot as plt

from mpl_toolkits.axes_grid1 import make_axes_locatable

def plot_loss(loss_values, ax=None, fig=None):
    _fig = fig if fig is not None else plt.figure()
    _ax = ax if ax is not None else plt.axes()

    x = list(range(len(loss_values)))
    _ax.scatter(x, loss_values)


def plot_param(param, values, best_values, loss_values, ax=None, fig=None):
    _fig = fig if fig is not None else plt.figure()
    _ax = ax if ax is not None else plt.axes()

    population = len(values[0])
    iterations = len(values)
    x = list(range(iterations))
    for y in range(population):
        _ax.scatter(x, values[:,y], c='grey', s=2)

    _ax.plot(x, best_values, c='red', zorder=1)
    best_scatter = _ax.scatter(x, best_values, c=loss_values, vmin=0, vmax=1000, zorder=2)


    _ax.set_ylabel(param)
    _ax.set_xlabel('iterations')

    divider = make_axes_locatable(_ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    _fig.colorbar(best_scatter, cax=cax, ax=_ax)

def plot_param_compare(param_a, param_b, values_a, values_b, loss_values, ax=None, fig=None):
    _fig = fig if fig is not None else plt.figure()
    _ax = ax if ax is not None else plt.axes()

    # population = len(values[0])
    # iterations = len(values)
    # x = list(range(iterations))
    # for y in range(population):
    #     _ax.scatter(x, values[:,y], c='grey', s=2)

    # _ax.plot(x, best_values, c='red', zorder=1)
    scatter = _ax.scatter(values_a, values_b, c=loss_values, vmin=0, vmax=1000, zorder=1)


    _ax.set_xlabel(param_a)
    _ax.set_ylabel(param_b)

    divider = make_axes_locatable(_ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    _fig.colorbar(scatter, cax=cax, ax=_ax)