"""
Molecular Structure
-------------------
This module provides abstracted functions to convert the molecular structures into the mathematical graphs.
The converted molecular structure is stored as a ``torch_geometric.Data`` object.
"""


import torch
from torch_geometric.data import Data
from rdkit import Chem
from maica.chem.base import *
from maica.data.util import get_one_hot_feat


def get_mol_graph(smiles: str,
                  elem_feats: numpy.ndarray,
                  global_feats: numpy.ndarray = None,
                  target: float = None,
                  present_hydrogen = False):
    try:
        # Get RDKit.Mol object from the given SMILES.
        mol = Chem.MolFromSmiles(smiles)

        # Present hydrogens in the molecule object.
        if present_hydrogen:
            mol = Chem.AddHs(mol)

        # If SMILES was not converted normally, returns None object.
        if mol is None:
            return None

        # Global information of the molecule.
        n_rings = mol.GetRingInfo().NumRings()

        # Structural information of the molecular graph.
        atom_feats = list()
        bonds = list()
        bond_feats = list()

        # Generate node-feature matrix.
        for atom in mol.GetAtoms():
            # Get elemental features of the atom.
            elem_attr = elem_feats[atom.GetAtomicNum() - 1, :]

            # Get hybridization type of the atom.
            hbd_type = get_one_hot_feat(str(atom.GetHybridization()), cat_hbd)

            # Get formal charge of the atom.
            fc_type = get_one_hot_feat(str(atom.GetFormalCharge()), cat_fc)

            # Check whether the atom belongs to the aromatic ring in the molecule.
            mem_aromatic = 1 if atom.GetIsAromatic() else 0

            # Get the number of bonds.
            degree = atom.GetDegree()

            # Get the number of hydrogen bonds.
            n_hs = atom.GetTotalNumHs()

            # Concatenate the given numerical features if they exist.
            if global_feats is None:
                atom_feats.append(numpy.hstack([elem_attr, hbd_type, fc_type, mem_aromatic,
                                                degree, n_hs, n_rings]))
            else:
                atom_feats.append(numpy.hstack([elem_attr, hbd_type, fc_type, mem_aromatic,
                                                degree, n_hs, n_rings, global_feats]))

        # Generate bond-feature matrix.
        for bond in mol.GetBonds():
            bonds.append([bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()])
            bond_feats.append(get_one_hot_feat(str(bond.GetBondType()), cat_bond_types))

            bonds.append([bond.GetEndAtomIdx(), bond.GetBeginAtomIdx()])
            bond_feats.append(get_one_hot_feat(str(bond.GetBondType()), cat_bond_types))

        # Add self-loop.
        for i in range(0, len(atom_feats)):
            bonds.append([i, i])
            bond_feats.append(get_one_hot_feat('SELF', cat_bond_types))

        # Check isolated graph and raise a run time error.
        if len(bonds) == 0:
            raise RuntimeError

        # Convert numpy.ndarray to torch.Tensor.
        atom_feats = torch.tensor(atom_feats, dtype=torch.float)
        bonds = torch.tensor(bonds, dtype=torch.long).t().contiguous()
        bond_feats = torch.tensor(bond_feats, dtype=torch.float)

        # Check existence of target property.
        if target is not None:
            target = torch.tensor(target, dtype=torch.float).view(1, 1)

        return Data(x=atom_feats, edge_index=bonds, edge_attr=bond_feats, y=target)
    except RuntimeError:
        return None
