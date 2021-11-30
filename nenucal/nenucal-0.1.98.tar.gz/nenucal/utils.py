# Mixed utilities
#
# Author: F. Mertens

import numpy as np


color_cycle = ['#3465a4', '#4e9a06', '#cc0000', '#F57900', '#75507b', '#EDD400', '#555753']
blue, green, red, orange, magenta, yellow, black = color_cycle


def chunks(arr, n_max):
    n = int(np.ceil(len(arr) / np.ceil(len(arr) / n_max)))
    for i in range(0, len(arr), n):
        yield arr[i:i + n]


def factors(n):
    r = np.arange(1, int(n ** 0.5) + 1)
    x = r[np.mod(n, r) == 0]
    return np.unique(np.concatenate((x, n / x), axis=None))


def rmean(data, axis=0):
    '''Remove the mean in direction axis'''
    return data - np.mean(data, axis=axis)


def is_odd(num):
    return num & 0x1


def robust_freq_width(freqs):
    '''Return frequency width, robust to gaps in freqs'''
    dfs = np.diff(freqs)
    m, idx, c = np.unique(np.round(dfs * 1e-3) * 1e3, return_counts=True, return_inverse=True)
    return dfs[np.where(idx == np.argmax(c))].mean()


def nudft(x, y, M=None, w=None, dx=None):
    """Non uniform discrete Fourier transform

    Args:
        x (array): x axis
        y (array): y axis
        M (int, optional): Number of Fourier components that will be computed, default to len(x)
        w (array, optional): Tapper

    Returns:
        (array, array): k modes, Fourier transform of y
    """
    if M is None:
        M = len(x)

    if dx is None:
        dx = robust_freq_width(x)

    if w is not None:
        y = y * w

    df = 1 / (dx * M)
    k = df * np.arange(-(M // 2), M - (M // 2))

    X = np.exp(2 * np.pi * 1j * k * x[:, np.newaxis])

    return k, np.tensordot(y, X.conj().T, axes=[0, 1]).conj().T


def get_delay(freqs, M=None, dx=None, half=True):
    ''' Convert frequencies to delay '''
    if dx is None:
        dx = robust_freq_width(freqs)
    if M is None:
        M = len(freqs)

    df = 1 / (dx * M)
    delay = df * np.arange(-(M // 2), M - (M // 2))

    if half:
        M = len(delay)
        delay = delay[M // 2 + 1:]

    return delay


def get_wedge_delay(theta, bu, freq):
    return np.sin(theta) * bu / freq
