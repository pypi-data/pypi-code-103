
import numpy as np


def revert_minimum_image_projection(positions, box) -> np.ndarray:
    """
    :param positions: 3-Dimensional numpy array with axes (time, particle number, position)
    """
    box_indices = np.zeros_like(positions, dtype=int)
    displacements = positions[1:] - positions[:-1]
    box_index_changes = np.zeros_like(displacements, dtype=np.int8)
    box_index_changes[displacements > 0.5 * box] = -1
    box_index_changes[displacements < -0.5 * box] = 1
    box_indices[1:] = np.cumsum(box_index_changes, axis=0)
    reverted_positions = positions + box_indices * box

    return reverted_positions
