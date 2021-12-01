import numpy as np
import numba

BooleanArray = np.ndarray


def get_bounding_box(coords: np.ndarray) -> np.ndarray:
    bb = np.empty((3, 2))
    bb[:, 0] = coords.min(0)
    bb[:, 1] = coords.max(0)
    return bb


def bounding_boxes_might_be_in_proximity(proximity, bb,
                                         bb_other, min_img_box) -> BooleanArray:
    center = bb.sum(1) / 2
    d = bb[:, 1] - bb[:, 0]
    centers_other = bb_other.sum(2) / 2
    d_other = bb_other[:, :, 1] - bb_other[:, :, 0]

    cvector = np.abs(get_minimum_image_vector(center, centers_other, min_img_box))

    potential_proximity = (cvector - (d_other + d) / 2 - proximity) <= 0

    return potential_proximity.all(1)


@numba.jit
def get_minimum_image_vector(v1, v2, simulation_box):
    """
    Minimum image vector from coordinates v2 to v1.
    Either v1 or v2 needs to contain multiple coordinates, i.e. has
    to have ndim = 2. E.g., v1 is of shape (5, 3) (holds coordinates of
    5 particles), v2 is of shape (3,).
    """
    dv = v1 - v2
    for i in range(len(simulation_box)):
        size_i = simulation_box[i]
        dv[:, i] -= size_i * np.rint(dv[:, i] / size_i)
    return dv
