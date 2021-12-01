from collections import Counter
import numpy as np
import itertools
from typing import List, Optional


# utility functions
def scale(x):
    return np.array(list(x)) / np.sum(list(x))


def is_leq_xmin(x, xmin):
    return False if xmin is None else x <= xmin


def is_geq_xmax(x, xmax):
    return False if xmax is None else x >= xmax


def to_distribution(cnt: Counter, xmin: int = 1, xmax: int = None):
    """ Convert counted frequencies to PDF """
    # add out-of-boundary frequencies up
    cnt2 = {x: f for x, f in cnt.items()
            if (not is_leq_xmin(x, xmin)) and (not is_geq_xmax(x, xmax))}
    if xmin:
        cnt2[xmin] = sum([f for x, f in cnt.items() if is_leq_xmin(x, xmin)])
    if xmax:
        cnt2[xmax] = sum([f for x, f in cnt.items() if is_geq_xmax(x, xmax)])

    # assign values
    xobs = np.arange(min(cnt2.keys()), max(cnt2.keys()) + 1, dtype=np.int32)
    freq = np.zeros(shape=xobs.shape, dtype=np.float32)
    for i, x in enumerate(xobs):
        freq[i] = cnt2.get(x, 0.0)

    pdf = scale(freq)
    return xobs, pdf, freq


def nodedist_distribution(nodedist: List[int],
                          xmin: Optional[int] = 1,
                          xmax: Optional[int] = None):
    """ The Distribution of node distances """
    if isinstance(nodedist[0], (tuple, list)):
        nodedist = list(itertools.chain(*nodedist))
    # count frequency of a specific node distance
    cnt = Counter(nodedist)
    # convert to distribution
    xobs, pdf, freq = to_distribution(cnt, xmin=xmin, xmax=xmax)
    return xobs, pdf, freq


def tokenvsnode_distribution(tokendist: List[int],
                             nodedist: List[int],
                             xmin: Optional[int] = None,
                             xmax: Optional[int] = None):
    """ The token position distance versus the node distance

    Interpretation:
    ---------------
        `(tokendist - nodedist) > 0` :
            Token stehen weit im Satz auseinandern,
            aber stehen syntaktisch nahe beinander.
        `(tokendist - nodedist) < 0` :
            Token stehen nahe beinander im Satz,
            aber haben syntaktisch weniger direkt miteinander zu tun.
    """
    if isinstance(tokendist[0], (tuple, list)):
        nodedist = list(itertools.chain(*nodedist))
    if isinstance(tokendist[0], (tuple, list)):
        tokendist = list(itertools.chain(*tokendist))
    # compute the difference btw. token distance and node distance
    node_vs_token_position = np.array(tokendist) - np.array(nodedist)
    cnt = Counter(node_vs_token_position)
    # convert to distribution
    xobs, pdf, freq = to_distribution(cnt, xmin=xmin, xmax=xmax)
    return xobs, pdf, freq
