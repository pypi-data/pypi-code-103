from dataclasses import dataclass
from typing import Union
import numpy as np
from scipy.signal import find_peaks


@dataclass
class G0Data:
    index: int
    omega: float
    G0: float


def compute_G0_via_saddle_point(omega: np.ndarray, G: np.ndarray) -> Union['G0Data', None]:
    location_saddle = _get_location_of_saddle_point(G.real)
    if len(location_saddle) != 1:
        print("No saddle or too many found.")
        print("Found:", len(location_saddle))
        return
    location_saddle = location_saddle[0]
    g0 = G0Data(location_saddle,
                (omega[location_saddle] + omega[location_saddle + 1]) / 2,
                (G.real[location_saddle] + G.real[location_saddle + 1]) / 2)
    return g0


def compute_G0_via_tangent_minimum(omega: np.ndarray, G: np.ndarray) -> 'G0Data':
    tangent = G.imag/G.real
    peaks, properties = find_peaks(-tangent)
    if len(peaks) != 1:
        raise RuntimeError('The tangent has no minimum')
    location = peaks[0]
    g0 = G0Data(location, omega[location], G.real[location])
    return g0


def _get_location_of_saddle_point(data: np.ndarray) -> np.ndarray:
    finite_diff = data[1:] - data[:-1]
    peaks, properties = find_peaks(finite_diff)
    return peaks

