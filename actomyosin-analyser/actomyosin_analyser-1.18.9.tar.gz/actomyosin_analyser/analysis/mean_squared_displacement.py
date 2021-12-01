from dataclasses import dataclass
from typing import Optional

import numba
import numpy as np

from actomyosin_analyser.analysis import geometry


def compute_msd(
        trajectory: np.ndarray,
        simulation_box: Optional[np.ndarray]=None
) -> 'MeanSquaredDisplacement':
    """
    For M particle trajectories consisting of N frames, compute the ensemble MSD over all M particles.
    The ensemble MSD is computed as the mean over individual MSDs, the variance is computed as
    as the variance over the individual MSDs.

    :param trajectory: Array of shape (N, M, d), where d = 1, 2 or 3 is the dimensionality of your trajectories.
                       If M = 1, you can also provide an array of shape (N, d).
    :param simulation_box: If the origin of your data is a simulation with periodic boundaries, provide
                           the size of the box, such that the periodic boundaries are taking into account.
    :return: MSD object with attributes lag, msd and variance_of_msd.
    """
    msd_array = _numba_compute_msd(trajectory, simulation_box)
    return MeanSquaredDisplacement.from_array(msd_array)


@numba.njit
def _numba_compute_msd(trajectory: np.ndarray, simulation_box: Optional[np.ndarray]) -> np.ndarray:
    lags = np.arange(1, len(trajectory))
    msd = np.empty((len(lags), 3))
    for lag in lags:
        if simulation_box is None:
            displacements = trajectory[lag:] - trajectory[:-lag]
        else:
            displacements = geometry.get_minimum_image_vector(trajectory[lag:], trajectory[:-lag], simulation_box)
        squared_summed = np.sum(displacements**2, axis=-1)
        msd[lag-1, 0] = lag
        msd[lag-1, 1] = np.nanmean(squared_summed)
        msd[lag-1, 2] = np.nanvar(squared_summed)
    return msd


@dataclass
class MeanSquaredDisplacement:
    lag: np.ndarray
    msd: np.ndarray
    variance_of_msd: np.ndarray
    lag_time: Optional[np.ndarray] = None

    def as_array(self) -> np.ndarray:
        a = np.empty((len(self.lag), 3))
        a[:, 0] = self.lag
        a[:, 1] = self.msd
        a[:, 2] = self.variance_of_msd
        return a

    @staticmethod
    def from_array(msd_array: np.ndarray) -> 'MeanSquaredDisplacement':
        return MeanSquaredDisplacement(
            msd_array[:, 0],
            msd_array[:, 1],
            msd_array[:, 2]
        )
