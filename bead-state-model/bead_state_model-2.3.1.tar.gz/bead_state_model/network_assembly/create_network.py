from abc import ABC, abstractmethod
from typing import Dict, Any, Union
import os
import json
import numpy as np
import logging

from .create_filament import collides, rotation_matrix


class CreateNetwork:
    """
    Base class for network generation algorithms. This class handles
    the output files, random number generation, and sets defaults
    for important attributes like ``CreateNetwork.acceptance_rate_handler``
    and ``CreateNetwork.nucleation_direction_func``.
    At least the ``CreateNetwork.run`` method has to be overwritten by
    derived classes.
    The filament/bead placement algorithm checks for overlap with other beads.
    If overlap is detected, the designated coordinates for placement are discarded
    and new ones are generated.
    Generation of possible coordinates for bead placement can be controlled via
    attribute ``CreateNetwork.acceptance_rate_handler``.
    Nucleation direction (i.e. the orientation of the first two beads of a filament)
    can be controlled via attribute ``CreateNetwork.nucleation_direction_func``.
    """

    def __init__(self, reserve_n_beads: int,
                 box: np.ndarray,
                 k_bend: float, k_stretch: float):
        self._rn_handler = RandomNumberHandler(2000)
        self.box = box
        self.coords = np.full((reserve_n_beads, 3), np.nan)
        self.filaments = []
        self.n_valid = 0

        if k_stretch < 1e-15:
            self.sigma_stretch = 2
        else:
            self.sigma_stretch = np.sqrt(1 / k_stretch)
        self.k_stretch = k_stretch
        if k_bend < 1e-15:
            self.sigma_theta = 2 * np.pi
        else:
            self.sigma_theta = np.sqrt(1 / k_bend)
        self.k_bend = k_bend

        #: Callable to randomly draw the initial direction of a filament. Has to accept
        #: a CreateNetwork instance as argument (to use its attributes/parameters), and
        #: has to return an array of 3 floats, the direction vector (x, y, z) pointing
        #: from first to second bead at nucleation of a filament. For example, see function
        #: :func:`~bead_state_model.network_assembly.create_network.nucleation_direction_func_quasi_2D`.
        self.nucleation_direction_func = _default_nucleation_direction_func

        #: Instance of a class that handles selection of coordinate candidates, when append beads to filaments.
        self.acceptance_rate_handler = _AcceptanceRateHandlerDefault(10)

    def run(self):
        raise RuntimeError("Overwrite the method CreateNetwork.run in derived classes!")

    def write(self, folder: str, minimum_image: bool=False,
              min_n_beads: int=3):
        """ Write generated polymers to files.

        Will generate 4 files:

        1. beads.txt -- contains complete information on beads including their bonds
           to other beads.
        2. filaments.txt -- information on filaments (what is the first bead (tail) of
           a filament). Has to be used in conjunction with beads.txt, in which information
           is stored, to which bead each tail is connected, and to which next bead and so on.
        3. config.json -- contains all important parameters that were used for network generation.
        4. info.json -- some information on the resulting network (how many filaments, how many
           beads per filament on average, etc.)
        """
        if not os.path.exists(folder):
            os.mkdir(folder)

        self._remove_short_filaments(min_n_beads)
        self._write_beads(os.path.join(folder, 'beads.txt'), minimum_image)
        self._write_filaments(os.path.join(folder, 'filaments.txt'))
        self._write_config(os.path.join(folder, 'config.json'))
        self._write_info(os.path.join(folder, 'info.json'))

    def get_info(self) -> Dict[str, Any]:
        n_beads = [len(f.items) for f in self.filaments]
        return {
            'n_filaments': len(self.filaments),
            'n_beads': n_beads,
            'n_beads_max': float(np.array(n_beads).max()),
            'n_beads_std': float(np.array(n_beads).std()),
            'n_beads_mean': float(np.array(n_beads).mean()),
            'n_beads_total': int(self.n_valid)
        }

    def _add_filament(self):
        end, start = self._add_beads_of_nucleated_filament()
        f = Filament(start, end)
        self.filaments.append(f)

    def _add_beads_of_nucleated_filament(self):
        start, end = self.n_valid, self.n_valid + 1
        self.coords[start] = self._get_random_location()
        self.n_valid += 1
        direction = self.nucleation_direction_func(self)
        self.coords[end] = self._get_append_bead_location(self.coords[start],
                                                          direction,
                                                          start)
        self.n_valid += 1
        return end, start

    def _get_random_location(self):
        n_trials = 10000
        n_batch = self.acceptance_rate_handler.n_batch
        for i in range(0, n_trials, n_batch):
            coords = np.random.rand(n_batch, 3) * self.box
            chosen_coords = self.acceptance_rate_handler(coords)
            for c in chosen_coords:
                if not collides(c, self.coords[:self.n_valid], 1.0, self.box):
                    return c
        msg = "Box too full or bad luck? Could not find an empty space in {} trials".format(
            n_trials)
        raise RuntimeError(msg)

    def _get_append_bead_location(self, start_location: np.ndarray,
                                  direction: np.ndarray, idx_previous: int):
        direction = direction / np.sqrt(np.sum(direction**2))
        n_trials = 10000
        n_batch = self.acceptance_rate_handler.n_batch
        for i in range(0, n_trials, n_batch):
            loop_factor = 1 + i/n_trials*5
            l = np.random.randn(n_batch) * self.sigma_stretch * loop_factor + 1
            theta = np.random.randn(n_batch) * self.sigma_theta * loop_factor
            gamma = np.random.rand(n_batch)*np.pi
            relative_positions = np.empty((n_batch, 3))
            relative_positions[:, 0] = l * np.cos(theta)
            relative_positions[:, 1] = l * np.sin(theta) * np.cos(gamma)
            relative_positions[:, 2] = l * np.sin(theta) * np.sin(gamma)
            coords = start_location + rotation_matrix(direction).dot(relative_positions.T).T
            chosen_coords = self.acceptance_rate_handler(coords)
            for c in chosen_coords:
                if not collides(c,
                                np.vstack([self.coords[:idx_previous],
                                           self.coords[idx_previous+1:self.n_valid]]),
                                1.0, self.box):
                    return c
        msg = "Box too full or bad luck? Could not find an empty space in {} trials".format(
            n_trials)
        raise RuntimeError(msg)

    def _add_bead(self, filament):
        prev = self.coords[filament.items[-2]]
        end = self.coords[filament.items[-1]]
        direction = self._get_minimum_image_vector(prev, end)
        new_bead = self._get_append_bead_location(end, direction, filament.items[-1])
        self.coords[self.n_valid] = new_bead
        filament.items.append(self.n_valid)
        self.n_valid += 1

    def _get_minimum_image_vector(self, u, v):
        w = v - u
        m = w - self.box * np.rint(w / self.box)
        return m

    def _remove_short_filaments(self, min_n_beads):
        indices_too_short_filaments = []
        for idx, fil in enumerate(self.filaments):
            if len(fil.items) < min_n_beads:
                indices_too_short_filaments.append(idx)
        indices_too_short_filaments.reverse()
        for idx in indices_too_short_filaments:
            self.filaments.pop(idx)

    def _write_beads(self, fname: str, minimum_image: bool = False):
        fp = open(fname, 'wt')
        n_written = 0
        if minimum_image:
            coords = self.coords.copy()
            coords = coords % self.box
        else:
            coords = self.coords

        for fil in self.filaments:
            items_in_write_order = []
            for i in range(len(fil.items)):
                if i == 0:
                    prev = -1
                else:
                    prev = n_written - 1
                current = n_written
                if i < len(fil.items) - 1:
                    nxt = n_written + 1
                else:
                    nxt = -1
                fp.write("{}\t".format(current))
                r = coords[fil.items[i]]
                fp.write("{}\t{}\t{}\t".format(r[0], r[1], r[2]))
                fp.write("{}\t{}\t{}\n".format(prev, nxt, -1))
                n_written += 1
                items_in_write_order.append(current)
            fil.items = items_in_write_order
        fp.close()

    def _write_filaments(self, fname):
        fp = open(fname, 'wt')
        for i, fil in enumerate(self.filaments):
            fp.write("{}\t{}\t{}\t{}\n".format(i,
                                               fil.items[0],
                                               fil.items[-1],
                                               len(fil.items)))
        fp.close()

    def _write_config(self, fname):
        with open(fname, 'wt') as fh:
            json.dump(self.get_config_as_dict(), fh)

    def _write_info(self, fname):
        with open(fname, 'wt') as fh:
            json.dump(self.get_info(), fh)

    def get_config_as_dict(self) -> Dict[str, Any]:
        d = {
            'box': list(self.box),
            'k_bend': self.k_bend,
            'k_stretch': self.k_stretch,
            'acceptance_rate_handler': self.acceptance_rate_handler.get_config_as_dict()
        }
        return d


class RandomNumberHandler:

    def __init__(self, n_batch: int):
        self.n_batch = n_batch
        self._random_directions = np.empty((n_batch, 3))
        self._n_used_directions = None

        self._generate_random_directions()

    def _generate_random_directions(self):
        """
        Use area-preserving projection from cylinder on a sphere, as described in
        https://math.stackexchange.com/a/44691 by Jim Belk.
        """
        theta = np.random.rand(self.n_batch) * 2 * np.pi
        z = np.random.rand(self.n_batch) * 2 - 1
        self._random_directions[:, 0] = np.sqrt(1 - z ** 2) * np.cos(theta)
        self._random_directions[:, 1] = np.sqrt(1 - z ** 2) * np.sin(theta)
        self._random_directions[:, 2] = z
        self._n_used_directions = 0

    def get_random_direction(self):
        if self._n_used_directions >= self.n_batch:
            self._generate_random_directions()
        self._n_used_directions += 1
        return self._random_directions[self._n_used_directions - 1]

    @staticmethod
    def get_poisson_events(rate, n_steps) -> np.ndarray:
        events_generated = False
        event_times = np.array([])
        cumsum = 0
        while not events_generated:
            expected_n_events = n_steps * rate
            intervals = - np.log(np.random.rand(int(expected_n_events * 1.2))) / rate
            event_times = np.hstack([event_times, np.cumsum(intervals) + cumsum])
            cumsum = event_times[-1]
            if event_times[-1] >= n_steps:
                events_generated = True
        return (event_times[event_times < n_steps] + 0.5).astype(int)


class Filament:

    def __init__(self, first: int, last: int):
        self.items=[first, last]


def _default_nucleation_direction_func(system):
    return system._rn_handler.get_random_direction()


def nucleation_direction_func_quasi_2D(system: 'CreateNetwork'):
    """
    Returns a planar random direction (cos(phi), sin(phi), 0).
    phi is drawn from uniform random distribution between 0 and 2*pi.
    z component is always 0.
    """
    phi = np.random.rand() * 2 * np.pi
    return np.array([np.cos(phi), np.sin(phi), 0])


class _AcceptanceRateHandlerDefault:
    """
    Default acceptance rate handler; it does basically
    nothing, but serves as a place holder for more
    elaborate acceptance rate handler schemes.
    Batches of ``possible_coords`` are not selected via any method,
    they are simply returned as they are provided.
    """

    def __init__(self, n_batch):
        self.n_batch = n_batch

    def __call__(self, possible_coords):
        if len(possible_coords) > self.n_batch:
            msg = "Only use coordinate array with maximum number of lines "
            msg += "equal to or smaller than n_batch = {}".format(self.n_batch)
            raise ValueError(msg)
        return possible_coords[:self.n_batch]

    @staticmethod
    def get_config_as_dict() -> Dict[str, Any]:
        return {'type': 'default'}


class AcceptanceRateHandlerPotential(ABC):
    """
    Base class for potentials during network generation.
    The methods ``AcceptanceRateHandlerPotential.energy`` and
    ``AcceptanceRateHandlerPotential.get_config_as_dict`` need
    to be implemented/overwritten by derived classes.
    When an instance of this class is called and
    ``possible_coords`` are passed to it, coordinates are
    chosen via a Monte-Carlo-like algorithm. Coordinate candidates
    with higher energy have lower probability to be chosen.
    Probabilities based on energy are only determined across batches,
    i.e. increasing ``n_batch`` will on average lead to systems with lower
    energy.
    """

    def __init__(self, n_batch: int):
        self.n_batch = n_batch

    @abstractmethod
    def energy(self, coords: np.ndarray) -> np.ndarray:
        """
        Compute energy for each of the N positions in array ``coords``.
        For each position, a scalar energy has to be computed, leading to
        an array of length N as return value.
        This method has to be overwritten in child classes.

        :param coords: Array of possible coordinates of shape (N, 3).
        :return: Array of energies of shape (N,).
        """
        ...

    def __call__(self, possible_coords: np.ndarray) -> np.ndarray:
        exp_energy = np.exp(-self.energy(possible_coords))
        p = exp_energy / exp_energy.sum()
        n = len(p.nonzero()[0])
        indices = np.arange(len(possible_coords))
        valid = np.isfinite(p)
        if valid.sum() == 0:
            return np.array([])
        idx_chosen = np.random.choice(indices[valid], n,
                                      replace=False, p=p[valid])
        return possible_coords[idx_chosen]

    @abstractmethod
    def get_config_as_dict(self) -> Dict[str, Any]:
        """
        Convert the parameters that define this instance of
        ``AcceptanceRateHandlerPotential`` to a dictionary that
        can be written as json (i.e. the dict may only contain built-in python
        types like dicts, lists, strings, floats, integers, booleans).
        This is an abstract method that has to be overwritten in child classes.
        """
        ...


class AcceptanceRateHandlerBeadInNetwork(AcceptanceRateHandlerPotential):

    def __init__(self, n_batch: int,
                 radius: float,
                 k_repulsion: float,
                 position: np.ndarray):
        super().__init__(n_batch)
        self.radius = radius
        self.k = k_repulsion
        self.position = position

    def energy(self, coords: np.ndarray) -> np.ndarray:
        """

        :param coords: Has to be of shape (N, 3) with coordinates, where first dimension (rows)
                       are different particles, second dimension (columns) has to have
                       3 entries: x, y, z coordinates.
        :return:
        """
        distances = self.position - coords
        distances = np.sqrt((distances ** 2).sum(1))
        energies = np.zeros_like(distances)
        energies[distances < self.radius] = \
            0.5 * self.k * (self.radius - distances[distances < self.radius]) ** 2
        return energies

    def get_config_as_dict(self) -> Dict[str, Any]:
        return {
            'type': AcceptanceRateHandlerBeadInNetwork.__name__,
            'bead_position': list(self.position),
            'bead_radius': self.radius,
            'k_repulsion': self.k,
            'n_batch': int(self.n_batch)
        }


class AcceptanceRateHandlerZPotential(AcceptanceRateHandlerPotential):

    def __init__(self, layer_height: float, exponent: Union[int, float],
                 k: float, center_offset: float,
                 lower_bound, upper_bound, n_batch):
        AcceptanceRateHandlerPotential.__init__(self, n_batch)
        self.d = layer_height/2
        self.n = exponent
        self.k = k
        self.offset = center_offset
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def energy(self, coords: np.ndarray):
        z = coords[:, 2]
        warn_msg = "z outside of range [{}, {}]".format(self.lower_bound, self.upper_bound)
        if isinstance(z, (int, float)):
            if z > self.upper_bound:
                logging.warning(warn_msg)
            if z < self.lower_bound:
                logging.warning(warn_msg)
            if abs(z - self.offset) < self.d:
                return 0
            return self.k * (abs(z - self.offset) - self.d) ** self.n
        if (z > self.upper_bound).any():
            logging.warning(warn_msg)
        if (z < self.lower_bound).any():
            logging.warning(warn_msg)
        result = np.zeros_like(z)
        result[np.abs(z - self.offset) > self.d] = \
            self.k * (np.abs(z[np.abs(z - self.offset) > self.d] - self.offset) - self.d) ** self.n
        return result

    def get_config_as_dict(self) -> Dict[str, Any]:
        return {
            'type': AcceptanceRateHandlerZPotential.__name__,
            'height': self.d,
            'spring_constant': self.k,
            'power': self.n,
            'offset': self.offset,
            'lower_bound': self.lower_bound,
            'upper_bound': self.upper_bound,
            'n_batch': self.n_batch
        }
