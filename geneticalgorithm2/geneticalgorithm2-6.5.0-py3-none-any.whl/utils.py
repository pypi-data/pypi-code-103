


import os
from pathlib import Path


import numpy as np


def min_fast(a, b):
    '''
    1.5 times faster than row min(a, b)
    '''
    return  a if a < b else b

def max_fast(a, b):
    return a if a > b else b


def mkdir(folder: str):
    Path(folder).mkdir(parents = True, exist_ok=True)


def can_be_prob(value: float):
    return value >=0 and value <=1


def is_numpy(arg):
    return type(arg) == np.ndarray



def split_matrix(mat: np.ndarray):
    """
    splits wide pop matrix to variables and scores
    """
    return mat[:,:-1], mat[:, -1]


def union_to_matrix(variables_2D: np.ndarray, scores_1D: np.ndarray):
    """
    union variables and scores to wide pop matrix
    """
    return np.hstack((variables_2D, scores_1D[:, np.newaxis]))
















