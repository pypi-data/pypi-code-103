from rdkit.Chem import Mol, GetDistanceMatrix

from reinvent_chemistry import Conversions, TransformationTokens
from reinvent_chemistry.link_invent.bond_breaker import BondBreaker


class LinkerDescriptors:
    """ Molecular descriptors specific for properties of the linker """
    def __init__(self):
        self._bond_breaker = BondBreaker()
        self._conversions = Conversions()
        self._tokens = TransformationTokens()

    def effective_length(self, labeled_mol: Mol) -> int:
        linker_mol = self._bond_breaker.get_linker_fragment(labeled_mol)
        ap_idx = [i[0] for i in self._bond_breaker.get_labeled_atom_dict(linker_mol).values()]
        distance_matrix = GetDistanceMatrix(linker_mol)
        effective_linker_length = distance_matrix[ap_idx[0], ap_idx[1]]
        return int(effective_linker_length)

    def max_graph_length(self, labeled_mol) -> int:
        linker_mol = self._bond_breaker.get_linker_fragment(labeled_mol)
        distance_matrix = GetDistanceMatrix(linker_mol)
        max_graph_length = distance_matrix.max()
        return int(max_graph_length)

    def length_ratio(self, labeled_mol: Mol) -> float:
        """
        ratio of the maximum graph length of the linker to the effective linker length
        """
        max_length = self.max_graph_length(labeled_mol)
        effective_length = self.effective_length(labeled_mol)
        return effective_length/ max_length * 100

    def effective_length_from_smile(self, linker_smile: str) -> int:
        linker_mol = self._conversions.smile_to_mol(linker_smile)
        distance_matrix = GetDistanceMatrix(linker_mol)
        (ap_idx_0, ), (ap_idx_1, ) = linker_mol.GetSubstructMatches(self._conversions.smile_to_mol(
            self._tokens.ATTACHMENT_POINT_TOKEN))
        effective_linker_length = distance_matrix[ap_idx_0, ap_idx_1] - 2
        # subtract connection to the attachment points to be consistent with method effective_length
        return int(effective_linker_length)

    def max_graph_length_from_smile(self, linker_smile: str) -> int:
        linker_mol = self._conversions.smile_to_mol(linker_smile)
        (ap_idx_0, ), (ap_idx_1, ) = linker_mol.GetSubstructMatches(self._conversions.smile_to_mol(
            self._tokens.ATTACHMENT_POINT_TOKEN))
        distance_matrix = GetDistanceMatrix(linker_mol)
        # ignore connection from attachment point to be consistent with method max_graph_length
        distance_matrix[[ap_idx_0, ap_idx_1], :] = 0
        distance_matrix[:, [ap_idx_0, ap_idx_1]] = 0
        max_graph_length = distance_matrix.max()
        return int(max_graph_length)

    def length_ratio_from_smile(self, linker_smile: str) -> float:
        max_length = self.max_graph_length_from_smile(linker_smile)
        effective_length = self.effective_length_from_smile(linker_smile)
        return effective_length / max_length * 100
