"""
Helper classes and functions do illustrate contribution matrices
as segments of circles.
"""
import numpy as np
import matplotlib.pyplot as pl
import bfmplot as bp

import vaccontrib as vc

_colors = list(bp.epipack)
_colors[0], _colors[1], _colors[2] = _colors[1], _colors[2], _colors[0]


def plot_contribution_matrix(C, width=0.4,ax=None, xlabels=None):
    """
    Plot a contribution matrix as a bar chart where entries in different
    columns are plotted behind each other.
    """
    N = C.shape[0]
    if ax is None:
        fig, ax = pl.subplots(1,1)
    dx = 0.5/(N)
    bins = np.arange(N)
    lower = -N//2 + N % 2

    for i, d in zip(range(N),range(lower,N//2+1)):
        these_colors = [ bp.brighter(_colors[j],base=i+1) for j in range(N) ]
        ax.bar(bins+dx/2*(1-N%2)+d*dx,
               C[i,:],
               width=width,
               ec='w',
               color=these_colors,
              )
    bp.strip_axis(ax)
    ax.set_ylabel('contribution to R')
    ax.set_xticks(bins)
    if xlabels is not None:
        ax.set_xticklabels(xlabels)
    bp.nice_ticks(ax,'y')

    return ax

def plot_reduced_contribution_matrix(C,width=0.4,ax=None):
    """
    Plot a reduced vaccinated-susceptible (2-dimensional)
    contribution matrix as a bar chart where entries in different
    columns are plotted behind each other.
    """
    assert(C.shape==(2,2))

    return plot_contribution_matrix(C,width,ax,['by unvaccinated','by vaccinated'])

def plot_contribution_matrix_stacked(C,width=0.8,ax=None,xlabels=None):
    """
    Plot contribution matrix as a bar chart where entries in different
    columns are stacked on top of each other.
    """
    C_ = C[::-1,:]
    C_cum = C_.cumsum(axis=0)
    C_cum = C_cum[::-1,:]
    N = C_cum.shape[0]
    if ax is None:
        fig, ax = pl.subplots(1,1)
    bins = np.arange(N)
    for i in range(N):
        these_colors = [ bp.brighter(_colors[j],base=i+1) for j in range(N) ]
        ax.bar(bins,
               C_cum[i,:],
               width=width,
               color=these_colors,
               ec='w')
    bp.strip_axis(ax)
    ax.set_ylabel('contribution to R')
    ax.set_xticks(bins)
    if xlabels is not None:
        ax.set_xticklabels(xlabels)
    bp.nice_ticks(ax,'y')

    return ax

def plot_reduced_contribution_matrix_stacked(C,width=0.8,ax=None):
    """
    Plot a reduced vaccinated-susceptible (2-dimensional)
    contribution matrix as a bar chart where entries in different
    columns are stacked on top of each other.
    """
    assert(C.shape==(2,2))

    return plot_contribution_matrix_stacked(C,width,ax,['by unvaccinated','by vaccinated'])

if __name__=="__main__":

    def get_homogeneous_contribution_matrix(variant,R0,):
        v, s, r = vc.io.get_homogeneous_vaccination_parameters(variant=variant)
        C_red = vc.get_homogeneous_contribution_matrix(R0, v, s, r)
        return C_red


    Chom = get_homogeneous_contribution_matrix('alpha',[4.,4.])
    C = vc.covid.get_reduced_vaccinated_susceptible_contribution_matrix_covid([4.,4,4,4,4],variant='alpha')

    ax = plot_reduced_contribution_matrix(Chom,0.6)
    ax = plot_reduced_contribution_matrix_stacked(Chom)
    ax = plot_reduced_contribution_matrix(C,0.6)
    ax = plot_reduced_contribution_matrix_stacked(C)

    C = vc.covid.get_reduced_contribution_matrix_covid([0.5,6,6,6,6],variant='delta')
    ax = plot_contribution_matrix(C,0.3)
    ax = plot_contribution_matrix_stacked(C)

    pl.show()
