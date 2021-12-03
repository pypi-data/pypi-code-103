#! /usr/bin/python3.7
import numpy as np
from typing import Tuple

from bead_state_model.periodic_boundaries import get_minimum_image_vector


def collides(coords: np.ndarray, other_coords: np.ndarray,
             bead_diameter: float, box: np.ndarray) -> bool:
    if len(other_coords) == 0:
        return False
    dv = get_minimum_image_vector(other_coords, coords, box)
    distances_squared = (dv**2).sum(1)
    return (distances_squared < bead_diameter**2).any()


def rotation_matrix(v: np.ndarray) -> np.ndarray:
    """
    Rotation that maps (1, 0, 0) onto v, where norm(v) = 1.
    """
    theta = np.arccos(v[2])
    phi = np.arccos(v[0]/np.sin(theta))
    gamma = -np.pi/2 + theta
    cos = np.cos
    sin = np.sin
    return np.array([[cos(phi)*cos(gamma), -sin(phi), cos(phi)*sin(gamma)],
                     [sin(phi)*cos(gamma), cos(phi), sin(phi)*sin(gamma)],
                     [-sin(gamma), 0, cos(gamma)]])


def create_filament(n_beads: int,
                    box: np.ndarray,
                    k_stretch: float,
                    k_bend: float,
                    minimum_image: bool=False) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create coordinates of a discretized filament consisting of beads.

    :param n_beads: Number of beads in filament. 
    :param box:
        Extent of the box with origin [0, 0, 0] in which the first
        beads of the filaments are randomly placed. Appended beads can exceed this box.
        Set minimum_image=True if you want to project beads into box before their
        coordinates are returned.
    :param k_stretch: Modulus for harmonic stretching energy between beads,

                      .. code::

                          E_stretch_i = 0.5 * k_stretch * (l_i - 1)**2.

                      Used to determine the distribution from which to draw the
                      distances between beads.
    :param k_bend: Modulus for harmonic bending energy between beads,

                   .. code::

                       E_bend_i = 0.5 * k_bend * theta_i**2.

                   Used to determine the distribution from which to draw the
                   angles between beads.
    :param minimum_image:
        Set True to project beads into the specified box before they
        are returned.
    """
    coords = np.empty((n_beads, 3))
    links = np.full((n_beads, 3), -1, dtype=int)

    coords[0] = np.random.rand(3) * box
    direction = np.random.randn(3)

    resting_length = 1
    
    if k_stretch < 1e-15:
        sigma_l = resting_length*2
    else:
        sigma_l = np.sqrt(1/k_stretch)
        
    if k_bend < 1e-15:
        sigma_theta = 2*np.pi
    else:
        sigma_theta = np.sqrt(1/k_bend)
        
    i = 1
    while i < n_beads:
        direction = direction / np.sqrt(np.sum(direction**2))
        l = np.random.randn() * sigma_l + 1
        theta = np.random.randn() * sigma_theta
        gamma = np.random.rand() * np.pi
        relative_position = np.array([l * np.cos(theta), 
                                      l * np.sin(theta) * np.cos(gamma), 
                                      l * np.sin(theta) * np.sin(gamma)])
        coords[i] = coords[i-1] + rotation_matrix(direction).dot(relative_position)
        if not collides(coords[i], coords[:i], 1.0, box):
            direction = coords[i] - coords[i-1]
            i = i+1

    links[1:, 0] = np.arange(0, n_beads-1)
    links[:-1, 1] = np.arange(1, n_beads)

    if minimum_image:
        coords = coords % box

    return coords, links
    

def write_beads_file(fname, n_beads, coords, links):
    fbeads = open(fname, 'wt')

    for i in range(n_beads):
        fbeads.write("{}\t".format(i))
        fbeads.write("{}\t{}\t{}\t".format(coords[i, 0], coords[i, 1], coords[i, 2]))
        fbeads.write("{}\t{}\t{}\n".format(links[i, 0], links[i, 1], links[i, 2]))
    fbeads.close()


def write_filaments_file(fname, n_beads):
    ffilaments = open(fname, 'wt')
    ffilaments.write("0\t0\t{}\t{}".format(n_beads-1, n_beads))
    ffilaments.close()
