from typing import Sized

import numpy as np


def get_minimum_image_vector(v1: np.ndarray, v2: np.ndarray,
                             simulation_box: Sized):
    """
    Minimum image vector from coordinates v2 to v1.
    Either v1 or v2 needs to contain multiple coordinates, i.e. has
    to have ndim = 2. E.g., v1 is of shape (5, 3) (holds coordinates of
    5 particles), v2 is of shape (3,).
    """
    dv = v1 - v2
    for i in range(len(simulation_box)):
        size_i = simulation_box[i]
        dv[..., i] -= size_i * np.rint(dv[..., i] / size_i)
    return dv


def get_minimum_image_projection(box: np.ndarray, coordinates: np.ndarray) -> np.ndarray:
    """
    Project array of coordinates into periodic simulation box. Assumes
    zero-centered coordinates with box going from -box/2 to +box/2.
    :param box: Edge lengths of zero-centered 3D simulation box.
    :param coordinates: Array of coordinates, with x, y, z in the last axis.
    """
    projection = np.empty_like(coordinates)
    shifted = coordinates + box / 2
    for i in range(len(box)):
        s = shifted[..., i]
        projection[..., i] = s - np.floor(s / box[i]) * box[i]
    return projection - box / 2
