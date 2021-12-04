"""Transformers calculating string kernels."""
from __future__ import annotations

import collections
import logging
from collections import Counter
from typing import Callable, Dict, List

import numpy as np

logger = logging.getLogger(__name__)


def _multiset_kernel(
    x: np.ndarray,
    y: np.ndarray,
    callback: Callable,
) -> np.ndarray:
    """
    Helper function for all other kernels in this file.
    You probably don't want to use this method outside of this file.

    Args:
        x, y: a numpy array of documents
        callback: one of the kernel methods in this file
        **callback_kwargs: optional arguments to the callback

    Returns:
        a len(x) by len(y) matrix containing the kernel distances.
    """
    result = np.zeros((len(x), len(y)))
    x_counts: List[Dict] = [Counter(d) for d in x]
    y_counts: List[Dict] = [Counter(d) for d in y]
    for i, xc in enumerate(x_counts):
        for j, yc in enumerate(y_counts):
            result[i, j] = callback(xc, yc)
    return result


def presence_kernel(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Calculate the presence kernel, Ionescu & Popescu 2017.

    x and y are lists of documents. Each document must be an iterable of features that
    can be compared using ==.

    Returns:
        a matrix where each entry [i, j] represents the number of features that document
        x[i] and y[j] have in common.
    """
    return _multiset_kernel(x, y, lambda xc, yc: len(xc & yc))


def spectrum_kernel(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Calculate the spectrum kernel, Ionescu & Popescu 2017.

    x and y are lists of documents. Each document must be an iterable of features that
    can be compared using ==.

    Returns:
        a matrix where each entry [i, j] = sum(
           xc * yc for all xc, yc in (common features in x[i] and y[j])
        )
    """

    def inner(xc: collections.Counter, yc: collections.Counter) -> float:
        all_ngrams = set(xc.keys()).intersection(set(yc.keys()))
        return sum([xc[ngram] * yc[ngram] for ngram in all_ngrams])

    return _multiset_kernel(x, y, inner)


def intersection_kernel(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Calculate the intersection kernel, Ionescu & Popescu 2017.

    x and y are lists of documents. Each document must be an iterable of features that
    can be compared using ==.

    Returns:
        a matrix where each entry [i, j] = sum(
            min(xc, yc) for all xc, yc in (common features in x[i] and y[j])
        )
    """
    return _multiset_kernel(x, y, lambda xc, yc: sum((xc & yc).values()))


def pqgram_kernel(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Calculates a distance kernel based on the PQ-gram distance by Austen et al. 2010.
    """

    def pqgram_distance(xc: collections.Counter, yc: collections.Counter) -> float:
        union = sum((xc + yc).values())  # bag union
        intersection = sum((xc & yc).values())
        # eq. (2) and (3) of Augsten et al. 2010
        return (union - 2 * intersection) / (union - intersection)

    return _multiset_kernel(x, y, pqgram_distance)
