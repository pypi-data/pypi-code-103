import numba
import numpy as np
from numba.core import types
from numba.typed import Dict as NumbaDict

from actomyosin_analyser.analysis import geometry
from actomyosin_analyser.analysis.abstract_analyser import AbstractAnalyser


def _compute_filament_center_of_mass(
        filament_coordinates: np.ndarray,
        box: np.ndarray
) -> np.ndarray:
    relative_coords = geometry.get_minimum_image_vector(
        filament_coordinates,
        filament_coordinates[0],
        box
    )
    com = relative_coords.mean(0) + filament_coordinates[0]
    return com


class FilamentCenterOfMassGetter:

    def __init__(self, analyser: AbstractAnalyser):
        self.analyser = analyser

    def get(self) -> 'FilamentCenterOfMassTrajectories':
        coordinates = self.analyser.get_trajectories_filaments(minimum_image=False)
        filaments = self.analyser.get_filaments()
        simulation_box = self.analyser.read_simulation_box()

        com_trajectories = FilamentCenterOfMassTrajectories(coordinates.shape[0])
        for t, filaments_t in enumerate(filaments):
            coords_t = coordinates[t]
            for fil in filaments_t:
                coords_fil = coords_t[fil.items]
                center_of_mass = _compute_filament_center_of_mass(
                    coords_fil,
                    simulation_box
                )
                com_trajectories.set(fil.id, t, center_of_mass)
        return com_trajectories


class FilamentCenterOfMassTrajectories:

    def __init__(self, n_frames: int):
        self._n_frames = n_frames
        self._trajectories = NumbaDict.empty(types.int64, types.float64[:, :])

    def set(self, filament_id: int, frame: int, position: np.ndarray):
        _set_entry_in_trajectory_dict(self._trajectories, self._n_frames, filament_id, frame, position)

    def as_array(self) -> np.ndarray:
        return _trajectory_dict_to_array(self._trajectories, self._n_frames)


@numba.njit
def _trajectory_dict_to_array(d, n_frames) -> np.ndarray:
    trajectory_array = np.full((n_frames, len(d), 3), np.nan)
    for i, fil_id in enumerate(sorted(d.keys())):
        trajectory_array[:, i] = d[fil_id]
    return trajectory_array


@numba.njit()
def _set_entry_in_trajectory_dict(trajectory_dict, n_frames, filament_id, frame, position):
    if filament_id not in trajectory_dict:
        new_trajectory = np.full((n_frames, 3), np.nan)
        trajectory_dict[filament_id] = new_trajectory
    trajectory_dict[filament_id][frame] = position