import numpy as np


class MayaviAnimator:

    def __init__(self):
        self.data_reader = None

    def show_at_t(self, t):
        raise NotImplementedError("Abstract base class")

    def _data_slice_to_coords(self, data_slice: np.ndarray):
        size = data_slice.shape[0] // 3
        x = np.empty(size)
        y = np.empty(size)
        z = np.empty(size)        

        for i in range(size):
            x[i] = data_slice[3 * i]
            y[i] = data_slice[3 * i + 1]
            z[i] = data_slice[3 * i + 2]
        return x, y, z
