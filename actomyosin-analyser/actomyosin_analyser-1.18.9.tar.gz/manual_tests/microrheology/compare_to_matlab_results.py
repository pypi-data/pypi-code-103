"""
The common method for microrheology analysis is the Mason (2000) method, usually
in the advanced version by Dasgupta et al. (2002).
We have implementations of that method for MATLAB in our lab. The file ``example_G.mat``
contains results from that implementation. I copied it for comparison with
my implementations of the method.
"""
import numpy as np
from scipy.io import loadmat
from scipy.constants import Boltzmann
import matplotlib.pyplot as plt

from actomyosin_analyser.analysis.microrheology.mason_method import (get_logspaced_axes, compute_G_advanced,
                                                                     compute_G_danny_seara)
from actomyosin_analyser.analysis.microrheology.paust_method import fit_msd, compute_G_via_fit_parameters

k = kB = 1.38065e-23
kT = k * 310.15  # T = 37 C in Kelvin
bead_radius = 0.35e-6  # Not sure whether it was 2 microns radius or diameter ...


def _compare_derivatives(dd_mat, dda_mat, dd, dda):
    fig, ax = plt.subplots(2, 1)

    ax[0].plot(dd_mat)
    ax[0].plot(dd)
    ax[0].set(
        title='dd'
    )

    ax[1].plot(dda_mat)
    ax[1].plot(dda)
    ax[1].set(
        title='dda'
    )


def main():
    mat = loadmat('example_G.mat')
    tau, msd = mat['tau'][0], mat['MSD'][:, 0]
    msd = msd * 1e-12
    tau_logspace_mat, msd_logspace_mat = mat['msdtau'][:, 0], mat['msdtau'][:, 1] * 1e-12
    Gp_mat, Gpp_mat = mat['Gp'][0], mat['Gpp'][0]
    dd_mat, dda_mat = mat['dd'][0], mat['dda'][0]
    omega_mat = 1 / tau_logspace_mat
    n_points_per_decade = 16  # That was the value stated in the comments of the matlab code.

    _plot_msd(msd, tau, tau_logspace_mat, msd_logspace_mat)

    _compare_log_spacing(tau, msd, tau_logspace_mat, n_points_per_decade)
    _compare_to_paust_method(tau, msd, omega_mat, Gp_mat, Gpp_mat)
    _compare_to_mason_method(tau, msd, omega_mat, Gp_mat, Gpp_mat, n_points_per_decade)
    dd, dda = _compare_to_seara_clone(tau, msd, omega_mat, Gp_mat, Gpp_mat, n_points_per_decade)

    _compare_derivatives(dd_mat, dda_mat, dd, dda)


def _compare_to_seara_clone(
        tau: np.ndarray,
        msd: np.ndarray,
        omega_mat: np.ndarray,
        Gp_mat: np.ndarray,
        Gpp_mat: np.ndarray,
        n_points_per_decade: int
):
    fig, ax = plt.subplots(1, 1)

    ax.plot(omega_mat, Gp_mat, '-C0', label='matlab')
    ax.plot(omega_mat, Gpp_mat, '--C0')

    for i, width in enumerate([0.7], start=1):
        omega, G, _dd, _dda = compute_G_danny_seara(tau, msd, bead_radius,
                                                    dimensionality=2, kT=kT, width=width,
                                                    n_points_per_decade=n_points_per_decade)
        if width == 0.7:
            dd = _dd
            dda = _dda

        ax.plot(omega, G.real, f'-C{i}', label=f'py, w={width}')
        ax.plot(omega, G.imag, f'--C{i}')

    ax.legend()
    ax.set(
        ylabel="$G'$ (solid) $G''$ (dashed)",
        xlabel='frequency',
        title='compare Seara clone',
        xscale='log',
        yscale='log'
    )
    fig.tight_layout()
    return dd, dda


def _compare_to_mason_method(
        tau: np.ndarray,
        msd: np.ndarray,
        omega_mat: np.ndarray,
        Gp_mat: np.ndarray,
        Gpp_mat: np.ndarray,
        n_points_per_decade: int
):
    fig, ax = plt.subplots(1, 1)

    ax.plot(omega_mat, Gp_mat, '-C0', label='matlab')
    ax.plot(omega_mat, Gpp_mat, '--C0')

    for i, width in enumerate([0.7], start=1):
        omega, G = compute_G_advanced(tau, msd, bead_radius, n_points_per_decade,
                                      kT, dimensionality=2, width=width)

        ax.plot(omega, G.real, f'-C{i}', label=f'py, w={width}')
        ax.plot(omega, G.imag, f'--C{i}')

    ax.legend()
    ax.set(
        ylabel="$G'$ (solid) $G''$ (dashed)",
        xlabel='frequency',
        title='compare Mason',
        xscale='log',
        yscale='log'
    )
    fig.tight_layout()


def _compare_to_paust_method(
        tau: np.ndarray,
        msd: np.ndarray,
        omega_mat: np.ndarray,
        Gp_mat: np.ndarray,
        Gpp_mat: np.ndarray
):
    fig, ax = plt.subplots(1, 1)

    ax.plot(omega_mat, Gp_mat, '-C0', label='Mason')
    ax.plot(omega_mat, Gpp_mat, '--C0')

    p_opt, p_cov = fit_msd(tau, msd)
    omega = 1 / tau
    G = compute_G_via_fit_parameters(omega, bead_radius, kT, *p_opt)

    ax.plot(omega, G.real, '-C1', label='Paust')
    ax.plot(omega, G.imag, '--C1')

    ax.legend()
    ax.set(
        ylabel="$G'$ (solid) $G''$ (dashed)",
        xlabel='frequency',
        title='compare to Paust',
        xscale='log',
        yscale='log'
    )
    fig.tight_layout()


def _compare_log_spacing(
        tau: np.ndarray,
        msd: np.ndarray,
        tau_logspace_mat: np.ndarray,
        n_points_per_decade: int
):
    tau_logspace, msd_logspace = get_logspaced_axes(tau, msd, n_points_per_decade)

    fig, ax = plt.subplots(1, 1)

    ax.plot(tau_logspace, 'o', label=f'python: {len(tau_logspace)} points')
    ax.plot(tau_logspace_mat, 'o', label=f'matlab: {len(tau_logspace_mat)} points')

    ax.legend()
    ax.set(
        title='logspaced time axis',
        yscale='log',
        xlabel='index',
        ylabel='time'
    )
    fig.tight_layout()


def _plot_msd(msd, tau, tau_log_space, mat_log_space):
    fig, ax = plt.subplots(1, 1)
    ax.plot(tau, msd)
    ax.plot(tau_log_space, mat_log_space, 'o')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set(
        title='MSD'
    )


if __name__ == '__main__':
    main()
    plt.show()
