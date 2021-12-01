"""
Features - Simple
=================

Functions and class transforming a signal into an matrix of
simple features. The features were inspired by the following
article : Electromyography (EMG) Data-Driven Load Classification using Empirical Mode Decomposition and Feature Analysis

The computed features are from the Feature Extraction of Unprocessed
Signal.

AUTHOR
    Itokiana Rafidinarivo, itokiana.rafidinarivo@edu.esiee.fr

LAST MODIFIED
    Wed. 01 Dec. 2021
"""

# External packages
import typing  #  typing for documentation
import numpy as np  # array operations
import scipy.stats as stats  # statistical operations


def mean(signal: typing.Union[np.array, list]) -> float:
    """
    Return the mean value of a given signal.

    Parameters
    ----------
        signal (array-like) Given signal

    Returns
    -------
        (float) mean of the signal

    Example
    -------
    >>> a = [1, 2, 3, 4]
    >>> mean(a)
    2.5
    """
    return np.mean(signal)


def std(signal: typing.Union[np.array, list]) -> float:
    """
    Return the standard deviation value of a given signal.

    Parameters
    ----------
        signal (array-like) Given signal

    Returns
    -------
        (float) standard deviation of the signal

    Example
    -------
    >>> a = [1, 2, 3, 4]
    >>> round(std(a), 2)
    1.12
    """
    return np.std(signal)


def kurtosis(signal: typing.Union[np.array, list]) -> float:
    """
    Return the kurtosis measure value of a given signal.

    Parameters
    ----------
        signal (array-like) Given signal

    Returns
    -------
        (float) kurtosis measure of the signal

    Example
    -------
    >>> a = [1, 2, 3, 4]
    >>> round(kurtosis(a), 2)
    -1.36
    """
    return stats.kurtosis(signal)


def peak_to_peak(signal: typing.Union[np.array, list]) -> float:
    """
    Return the peak to peak value which is :
    max value minus min value.

    Parameters
    ----------
        signal (array-like) Given signal

    Returns
    -------
        (float) peak to peak value of the signal

    Example
    -------
    >>> a = [1, 2, 3, 4]
    >>> peak_to_peak(a)
    3
    """
    return np.max(signal) - np.min(signal)


def root_mean_square(signal: typing.Union[np.array, list]) -> float:
    """
    Return the root mean square (RMS) of the signal.

    Parameters
    ----------
        signal (array-like) Given signal

    Returns
    -------
        (float) root mean square of the signal

    Example
    -------
    >>> a = [1, 2, 3]
    >>> round(root_mean_square(a), 2)
    2.16
    """
    return np.sqrt(np.mean(np.power(signal, 2)))


def shape_factor(signal: typing.Union[np.array, list]) -> float:
    """
    Return the shape factor (SF) of the signal.

    Parameters
    ----------
        signal (array-like) Given signal

    Returns
    -------
        (float) shape factor of the signal

    Example
    -------
    >>> a = [1, 2, 3]
    >>> round(shape_factor(a), 2)
    1.08
    """
    return root_mean_square(signal) / np.mean(np.abs(signal))


def extract_features(signal: typing.Union[np.array, list]) -> dict:
    """
    Return features extracted from a given signal.

    Parameters
    ----------
        signal (array-like) Given signal

    Returns
    -------
        (dict) dictionary with feature abbreviations as key and value

    Example
    -------
    >>> features = extract_features([1, 2, 3, 4])
    >>> features['Mean']
    2.5
    >>> round(features['Std'], 2)
    1.12
    >>> round(features['KR'], 2)
    -1.36
    >>> features['P2P']
    3
    >>> round(features['RMS'], 2)
    2.74
    >>> round(features['SP'], 2)
    1.1
    """
    features = dict(
        Mean=mean(signal),
        Std=std(signal),
        KR=kurtosis(signal),
        P2P=peak_to_peak(signal),
        RMS=root_mean_square(signal),
        SP=shape_factor(signal)
    )

    return features


if __name__ == "__main__":
    # Package for doctest running
    import doctest

    # Launch tests and get results
    no_failures, no_tests = doctest.testmod()

    # Print results
    print(f"No. failures  : {no_failures}")
    print(f"No. successes : {no_tests - no_failures}")
    print(f"No. tests     : {no_tests}")

    # Check
    assert no_failures == 0
