"""
Crystal Structure
-----------------
This module provides data_old processing functions to convert the crystal structures into the mathematical graphs.
Like the molecular structure, the converted crystal structure are stored as a ``torch_geometric.Data`` object.
"""


import numpy
import torch
import pymatgen
import warnings
from torch_geometric.data import Data
from pymatgen.core.structure import Structure
from sklearn.metrics import pairwise_distances
from maica.chem.base import atom_nums
from maica.data.util import rbf


warnings.filterwarnings(action='ignore', category=UserWarning)


def get_crystal_graph(path_cif_file: str,
                      elem_feats: numpy.ndarray,
                      rbf_means: numpy.ndarray,
                      global_feats: numpy.ndarray = None,
                      target: float = None,
                      radius: float = 4.0):
    try:
        # Get Crystal object from the given CIF.
        crystal = Structure.from_file(path_cif_file)

        # Get the atomic information of the crystal structure.
        atom_coord, atom_feats = get_atom_info(crystal, elem_feats, global_feats, radius)

        # Get the bond information of the crystal structure.
        bonds, bond_feats = get_bond_info(atom_coord, rbf_means, radius)

        # Check isolated graph.
        if bonds is None:
            return None

        # Convert numpy.ndarray to torch.tensor.
        atom_feats = torch.tensor(atom_feats, dtype=torch.float)
        bonds = torch.tensor(bonds, dtype=torch.long).t().contiguous()
        bond_feats = torch.tensor(bond_feats, dtype=torch.float)

        # Check target property.
        if target is not None:
            target = torch.tensor(target, dtype=torch.float).view(1, 1)

        # Return a generated crystal graph as torch_geometric.Data object.
        return Data(x=atom_feats, edge_index=bonds, edge_attr=bond_feats, y=target)
    except RuntimeError:
        return None


def get_atom_info(crystal: pymatgen.core.Structure,
                  elem_feats: numpy.ndarray,
                  numeric_feats: numpy.ndarray,
                  radius: float):
    atoms = list(crystal.atomic_numbers)
    atom_coord = list()
    atom_feats = list()
    list_nbrs = crystal.get_all_neighbors(radius)

    # Get overall charge of the crystal structure.
    charge = crystal.charge

    # Get density in units of g/cc.
    density = float(crystal.density)

    # Get volume of the crystal structure.
    volume = crystal.volume

    coords = dict()
    for coord in list(crystal.cart_coords):
        coord_key = ','.join(list(coord.astype(str)))
        coords[coord_key] = True

    for i in range(0, len(list_nbrs)):
        nbrs = list_nbrs[i]

        for j in range(0, len(nbrs)):
            coord_key = ','.join(list(nbrs[j][0].coords.astype(str)))
            if coord_key not in coords.keys():
                coords[coord_key] = True
                atoms.append(atom_nums[nbrs[j][0].species_string])

    for coord in coords.keys():
        atom_coord.append(numpy.array([float(x) for x in coord.split(',')]))
    atom_coord = numpy.vstack(atom_coord)

    for i in range(0, len(atoms)):
        # Get elemental attributes of the atom.
        elem_attr = elem_feats[atoms[i] - 1, :]

        # Concatenate the given numerical features if they exist.
        if numeric_feats is None:
            atom_feats.append(numpy.hstack([elem_attr, charge, density, volume]))
        else:
            atom_feats.append(numpy.hstack([elem_attr, charge, density, volume, numeric_feats]))
    atom_feats = numpy.vstack(atom_feats).astype(float)

    return atom_coord, atom_feats


def get_bond_info(atom_coord: numpy.ndarray,
                  rbf_means: numpy.ndarray,
                  radius: float):
    bonds = list()
    bond_feats = list()
    pdist = pairwise_distances(atom_coord)

    # Calculate bond information.
    for i in range(0, atom_coord.shape[0]):
        for j in range(0, atom_coord.shape[0]):
            if i != j and pdist[i, j] <= radius:
                bonds.append([i, j])
                bond_feats.append(rbf(numpy.full(rbf_means.shape[0], pdist[i, j]), rbf_means, beta=0.5))

    if len(bonds) == 0:
        # If there is no bond in the given crystal structure.
        return None, None
    else:
        bonds = numpy.vstack(bonds)
        bond_feats = numpy.vstack(bond_feats)

        return bonds, bond_feats
