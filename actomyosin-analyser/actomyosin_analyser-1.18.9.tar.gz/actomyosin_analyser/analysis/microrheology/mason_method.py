from typing import Tuple, Union
import logging
import numpy as np
from scipy.optimize import leastsq
from scipy.special import gamma


def compute_G_advanced(lag_time: np.ndarray, msd: np.ndarray,
                       radius: float,
                       n_points_per_decade: int,
                       kT: float,
                       dimensionality: int, width: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute G for MSD with a linear-spaced log_lag_time.
    Based on the code of
    T. Maier, T. Haraszti (https://doi.org/10.1186/1752-153X-6-144).
    """

    log_lag_time, log_msd = get_logspaced_axes(lag_time, msd, n_points_per_decade)
    J = _compute_J(log_msd, radius, kT, dimensionality)

    J, log_lag_time = _get_valid_values(J, log_lag_time)

    N = len(log_lag_time)
    omega = np.full(N, np.nan)
    alpha = np.full(N, np.nan)
    g = np.full(N, np.nan)

    for i in range(N):
        alpha_i, g_i, om_i = _compute_g_i(J, i, log_lag_time, width)
        if g_i < 0 or not np.isfinite(g_i):
            print('invalid g_i for index i = {}'.format(i))
            continue
        g[i] = g_i
        omega[i] = om_i
        alpha[i] = alpha_i

    g2 = []
    omega2 = []

    for i in range(N):
        alphaI, alphaR, pre = _compute_alphaR_and_alphaI_and_pre(
            g, i, omega, width)

        g_i = g[i] * pre * complex(alphaR, alphaI)

        g2.append(g_i)
        omega2.append(omega[i])

    return np.array(omega2), np.array(g2)


def compute_G_danny_seara(
        tau: np.ndarray,
        msd: np.ndarray,
        bead_radius: float,
        dimensionality: int,
        kT: float,
        width: float,
        n_points_per_decade: int,
        clip: float=0.03
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Re-implementation of the matlab code on Danny Seara's github page
    https://github.com/dsseara/microrheology/blob/master/src/Moduli/calc_G.m .
    Originally code there was written by John C. Crocker and U. Penn.
    """

    tau, msd = get_logspaced_axes(tau, msd, n_points_per_decade)

    omega = 1/tau
    C = dimensionality*kT/(3*np.pi*bead_radius)
    pi_2_1 = np.pi/2 - 1

    m, d, dd = _logderive(tau, msd, width)

    G_laplace = C/((m * gamma(1+d)) * (1+(dd/2)))
    g, da, dda = _logderive(omega, G_laplace, width)

    alpha_real = np.cos((np.pi/2) * da) - pi_2_1 * da * dda
    alpha_imag = np.sin((np.pi/2) * da) - pi_2_1 * (1-da) * dda
    G_real = g * (1 / (1 + dda)) * alpha_real
    G_imag = g * (1 / (1 + dda)) * alpha_imag

    G_real[G_real < G_laplace * clip] = 0
    G_imag[G_imag < G_laplace * clip] = 0

    if np.abs(dd).max() > 0.15 or np.abs(dda).max() > 0.15:
        logging.warning("High curvature in data, moduli may be unreliable!")
    return omega, G_real + 1j * G_imag, dd, dda


def _logderive(
        x: np.ndarray,
        y: np.ndarray,
        width: float
):
    n_points = len(x)
    df = np.zeros(n_points)
    ddf = np.zeros(n_points)
    f2 = np.zeros(n_points)
    lx = np.log(x)
    ly = np.log(y)

    for i in range(n_points):
        w = np.exp(-(lx - lx[i])**2 / (2 * width**2))
        ww = w > 0.03
        p = np.polyfit(lx[ww], ly[ww], 2, w=w[ww])
        f2 = np.exp(p[2] + p[1] * lx[i] + p[0] * lx[i]**2)
        df[i] = p[1] + (2 * p[0] * lx[i])
        ddf[i] = 2 * p[0]

    return f2, df, ddf


def _compute_alphaR_and_alphaI_and_pre(g, i, omega, width):
    _pi_2 = np.pi / 2
    _pi_2_1 = _pi_2 - 1

    lo = np.log(omega)
    lg = np.log(g)
    w = np.exp(-(lo - lo[i])**2 / (2*width**2))
    ww = np.where(w > 0.03)
    fit = np.polyfit(lo[ww], lg[ww], 2, w=w[ww])
    c, b, a = fit
    beta = c
    alpha = b + 2 * c * np.log(omega[i])
    pre = 1.0 / (1 + beta)
    alphapi = _pi_2 * alpha
    alphaR = np.cos(alphapi - _pi_2_1 * alpha * beta)
    alphaI = np.sin(alphapi - _pi_2_1 * beta * (1 - alpha))
    return alphaI, alphaR, pre


def _compute_g_i(J, i, log_lag_time, width):

    lx = np.log(log_lag_time)
    w = np.exp(-(lx - lx[i])**2 / (2*width**2))
    ww = np.where(w > 0.03)
    coeffs = np.polyfit(lx[ww], np.log(J[ww]), 2, w=w[ww])
    a, b, c = coeffs
    beta = 2 * a
    alpha_i = b + 2 * a * np.log(log_lag_time[i])
    om_i = 1 / log_lag_time[i]
    yi = np.exp(c + b * lx[i] + a * lx[i]**2)
    g_i = 1 / (yi * gamma(1 + alpha_i))
    g_i = g_i / (1 + 0.5 * beta)
    return alpha_i, g_i, om_i


def _get_valid_values(J, log_lag_time):
    valid = (log_lag_time > 0) & np.isfinite(log_lag_time) & (J > 0) & np.isfinite(J)
    log_lag_time = log_lag_time[valid]
    J = J[valid]
    return J, log_lag_time


def get_logspaced_axes(
        t: np.ndarray,
        x: np.ndarray,
        n_points_per_decade: Union[int, float]
) -> Tuple[np.ndarray, np.ndarray]:
    if n_points_per_decade < 8:
        raise ValueError("number of points per decade has to be 8 or higher "
                         "for this method to work more reliably")
    ratio = t[-1]/t[0]
    powers = np.linspace(0, np.log10(ratio), int(n_points_per_decade * np.log10(ratio)) + 1)
    logspaced_t = 10**powers * t[0]
    logspaced_selection = np.searchsorted(t, logspaced_t)
    logspaced_selection = np.unique(logspaced_selection)
    logspaced_selection = logspaced_selection[logspaced_selection < len(t)]
    t = t[logspaced_selection]
    x = x[logspaced_selection]
    _validate_log_spacing_has_at_least_8_points_per_decade(t)
    return t, x


def _validate_log_spacing_has_at_least_8_points_per_decade(t: np.ndarray):
    """
    According to the code by Crocker and Penn that is on Danny Seara's
    github repository https://github.com/dsseara/microrheology/blob/master/src/Moduli/calc_G.m,
    we need at least 7-8 points per decade for this method to work.
    """
    ratio = t[-1]/t[0]
    powers = np.arange(0, int(np.log10(ratio)) + 1)
    decades = 10**powers
    edges = decades * t[0]
    for i in range(1, len(edges)):
        if ((t >= edges[i-1]) & (t < edges[i])).sum() < 8:
            raise RuntimeError("Need at least 8 data points per decade. The number of points"
                               " for your log-spacing is set too small.")


def _compute_J(msd, radius, kT, dim) -> np.ndarray:
    return 3/dim * np.pi * radius / kT * msd
