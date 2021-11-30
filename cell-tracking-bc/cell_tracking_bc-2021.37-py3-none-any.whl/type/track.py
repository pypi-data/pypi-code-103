# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from __future__ import annotations

import dataclasses as dtcl
from abc import ABC as abc_t
from abc import abstractmethod
from typing import Callable, ClassVar, Dict, Iterator, List
from typing import NamedTuple as named_tuple_t
from typing import Optional, Sequence, Tuple, Union

import networkx as grph

from cell_tracking_BC.in_out.text.uid import ShortID
from cell_tracking_BC.type.cell import cell_t, state_t


TIME_POINT = "time_point"


class unstructured_track_t(grph.DiGraph):
    in_degree: Callable[[cell_t], int]
    out_degree: Callable[[cell_t], int]

    # issues: Sequence[str] = None  # In self.graph["issues"] instead

    def Issues(self) -> Optional[Sequence[str]]:
        """"""
        output = []

        for cell in self.nodes:
            if (n_predecessors := self.in_degree(cell)) > 1:
                output.append(f"{cell}: {n_predecessors} predecessors; Expected=0 or 1")

        if output.__len__() == 0:
            output = None

        return output

    def RootCellWithTimePoint(self) -> Tuple[cell_t, int]:
        """"""
        output = tuple(
            _rcd for _rcd in self.nodes.data(TIME_POINT) if self.in_degree(_rcd[0]) == 0
        )

        if (n_roots := output.__len__()) != 1:
            raise ValueError(f"{n_roots}: Invalid number of root cells; Expected=1")

        return output[0]

    def LeafCellsWithTimePoints(self) -> Tuple[Sequence[cell_t], Sequence[int]]:
        """"""
        # TODO: Contact the Networkx team about the following comment (or check code on github)
        # /!\ It seems that networkx.DiGraph.nodes.data does not guarantee the node enumeration order. This could be
        # inconvenient for reproducibility checks.
        records = (
            _rcd
            for _rcd in self.nodes.data(TIME_POINT)
            if self.out_degree(_rcd[0]) == 0
        )
        leaves, time_points = zip(*records)

        leaves = tuple(leaves)
        time_points = tuple(time_points)

        return leaves, time_points

    @property
    def segments_iterator(self) -> Iterator[Tuple[int, cell_t, cell_t, bool]]:
        """"""
        time_points = grph.get_node_attributes(self, TIME_POINT)

        for edge in self.edges:
            time_point = time_points[edge[0]]
            is_last = self.out_degree(edge[1]) == 0
            yield time_point, *edge, is_last


@dtcl.dataclass(init=False, repr=False, eq=False)
class structured_track_t(abc_t):
    """
    Note: "pass" is used in abstract methods instead of "raise NotImplementedError"
    """

    labels: Sequence[int] = None

    root: cell_t = None
    leaves: Sequence[cell_t] = None

    root_time_point: int = None
    leaves_time_points: Sequence[int] = None

    lengths: Sequence[int] = None  # Segment-wise, not node-wise
    n_leaves: int = None

    issues: Sequence[str] = None

    def SetPostNewAttributes(self) -> None:
        """"""
        self.n_leaves = self.leaves.__len__()

    def Issues(
        self,
        max_root_time_point: int,
        min_length: int,
        /,
        *,
        min_min_length: int = 1,
        max_n_children: int = 2,
    ) -> Optional[List[str]]:
        """"""
        output = []

        if self.root_time_point > max_root_time_point:
            output.append(
                f"{self.root_time_point}: Invalid root time point; Expected<={max_root_time_point}"
            )
        if (longest := self.lengths[-1]) < min_length:
            output.append(
                f"{longest}: Invalid length of longest branch; Expected>={min_length}"
            )
        if self.root.state == state_t.dead:
            output.append('Root cell has a "dead" state')

        return output

    @abstractmethod
    def DividingCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        pass

    @property
    @abstractmethod
    def segments_iterator(self) -> Iterator[Tuple[int, cell_t, cell_t, bool]]:
        """"""
        pass

    @abstractmethod
    def Pieces(
        self, /, *, from_cell: cell_t = None, with_time_point: int = None
    ) -> Sequence[single_track_t]:
        """"""
        pass

    @property
    def single_tracks_iterator(self) -> Iterator[single_track_t]:
        """"""
        for leaf in self.leaves:
            yield self.TrackWithLeaf(leaf, safe_mode=False)

    @abstractmethod
    def TrackLabelWithLeaf(self, leaf: cell_t, /, *, safe_mode: bool = True) -> int:
        """"""
        pass

    @abstractmethod
    def TrackWithLeaf(
        self, leaf: cell_t, /, *, safe_mode: bool = True
    ) -> single_track_t:
        """"""
        pass

    @abstractmethod
    def AsSingleTrack(self) -> single_track_t:
        """"""
        pass

    def __str__(self) -> str:
        """"""
        if hasattr(self, "nodes"):
            cells = self.nodes
        else:
            cells = self
        cell_labels = tuple(_cll.label for _cll in cells)

        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}:\n"
            f"    {self.labels=}\n"
            f"    {self.root_time_point=}\n"
            f"    {self.leaves_time_points=}\n"
            f"    {self.lengths=}\n"
            f"    {cell_labels}"
        )


@dtcl.dataclass(init=False, repr=False, eq=False)
class single_track_t(structured_track_t, List[cell_t]):
    label: int = None
    leaf: cell_t = None
    leaf_time_point: int = None
    length: int = None  # Segment-wise, not node-wise
    affinities: Sequence[float] = None

    def __init__(self, *args, **kwargs) -> None:
        """"""
        list.__init__(self, *args, **kwargs)

    def SetPostNewAttributes(self) -> None:
        """"""
        structured_track_t.SetPostNewAttributes(self)

        self.label = self.labels[0]
        self.leaf = self.leaves[0]
        self.leaf_time_point = self.leaves_time_points[0]
        self.length = self.lengths[0]

    @classmethod
    def NewFromOrderedCells(
        cls,
        cells: Sequence[cell_t],
        affinities: Sequence[float],
        root_time_point: int,
        label: Optional[int],
        /,
    ) -> single_track_t:
        """
        This must be the only place where direct instantiation is allowed. Anywhere else, instantiation must be
        performed with this class method.

        label: Can be None only to accommodate the creation of branches as single tracks
        """
        instance = cls(cells)

        length = instance.__len__() - 1

        instance.labels = (label,)
        instance.root = instance[0]
        instance.leaves = (instance[-1],)
        instance.root_time_point = root_time_point
        instance.leaves_time_points = (instance.root_time_point + length,)
        instance.lengths = (length,)
        instance.affinities = affinities

        instance.SetPostNewAttributes()

        return instance

    def Issues(
        self, max_root_time_point: int, min_length: int, /, **_
    ) -> Optional[Sequence[str]]:
        """
        max_root_time_point: from 0, inclusive
        min_length: edge-wise, inclusive
        """
        output = structured_track_t.Issues(self, max_root_time_point, min_length)
        if output.__len__() == 0:
            output = None

        return output

    def DividingCells(
        self, /, *, _: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        return ()

    @property
    def segments_iterator(self) -> Iterator[Tuple[int, cell_t, cell_t, bool]]:
        """"""
        n_cells = self.length + 1
        for c_idx in range(1, n_cells):
            time_point = self.root_time_point + c_idx - 1
            is_last = c_idx == n_cells - 1
            yield time_point, *self[(c_idx - 1) : (c_idx + 1)], is_last

    def Pieces(self, /, **_) -> Sequence[single_track_t]:
        """"""
        return (self,)

    def TrackLabelsContainingCell(self, _: cell_t, /) -> Sequence[int]:
        """"""
        return (self.label,)

    def TrackLabelWithLeaf(self, leaf: cell_t, /, *, safe_mode: bool = True) -> int:
        """"""
        if (not safe_mode) or (leaf in self.leaves):
            return self.label

        raise ValueError(f"{leaf}: Not a leaf cell")

    def TrackWithLeaf(
        self, leaf: cell_t, /, *, safe_mode: bool = True
    ) -> single_track_t:
        """"""
        if (not safe_mode) or (leaf in self.leaves):
            return self

        raise ValueError(f"{leaf}: Not a leaf cell")

    def AsSingleTrack(self) -> single_track_t:
        """"""
        return self

    def AsRowsColsTimes(
        self, /, *, with_labels: bool = False
    ) -> Union[
        Tuple[Tuple[float, ...], Tuple[float, ...], Tuple[int, ...]],
        Tuple[Tuple[float, ...], Tuple[float, ...], Tuple[int, ...], Tuple[int, ...]],
    ]:
        """"""
        rows, cols = tuple(zip(*(_cll.centroid.tolist() for _cll in self)))
        times = tuple(
            range(self.root_time_point, self.root_time_point + self.length + 1)
        )

        if with_labels:
            labels = tuple(_cll.label for _cll in self)
            return rows, cols, times, labels

        return rows, cols, times


class forking_track_t(structured_track_t, grph.DiGraph):
    """
    Affinities are stored as edge attributes
    """

    SINGLE_TRACK_LABEL: ClassVar[str] = "single_track_label"

    in_degree: Callable[[cell_t], int]
    out_degree: Callable[[cell_t], int]

    def __init__(self, *args, **kwargs) -> None:
        """"""
        grph.DiGraph.__init__(self, *args, **kwargs)

    @classmethod
    def NewFromUnstructuredTrack(
        cls, track: unstructured_track_t, next_single_track_label: int, /
    ) -> Tuple[forking_track_t, int]:
        """"""
        instance = cls(track)

        root, root_time_point = track.RootCellWithTimePoint()
        instance.root = root
        instance.root_time_point = root_time_point

        leaves, leaves_time_points = track.LeafCellsWithTimePoints()
        instance.leaves = leaves
        instance.leaves_time_points = leaves_time_points

        labels = []
        for label, cell in enumerate(leaves, start=next_single_track_label):
            labels.append(label)
            # Adds attribute "forking_track_t.SINGLE_TRACK_LABEL" with value "label"
            # to leaf node indexed by "cell" (not to the cell itself).
            grph.set_node_attributes(
                instance,
                {cell: label},
                name=forking_track_t.SINGLE_TRACK_LABEL,
            )
        instance.labels = tuple(labels)

        lengths = []
        for leaf_time_point in leaves_time_points:
            lengths.append(leaf_time_point - root_time_point)
        instance.lengths = sorted(lengths)

        instance.SetPostNewAttributes()

        return instance, next_single_track_label + instance.n_leaves

    def Issues(
        self,
        max_root_time_point: int,
        min_length: int,
        /,
        *,
        min_min_length: int = 1,
        max_n_children: int = 2,
    ) -> Optional[Sequence[str]]:
        """
        max_root_time_point: from 0, inclusive
        min_length: edge-wise, longest branch, inclusive
        The remaining arguments are optional to ensure compatibility with single tracks.
        min_min_length: equivalent of min_length, but for shortest branch
        max_n_children: inclusive
        """
        output = structured_track_t.Issues(self, max_root_time_point, min_length)

        if (shortest := self.lengths[0]) < min_min_length:
            output.append(
                f"{shortest}: Invalid length of shortest branch; Expected>={min_length}"
            )
        for cell in self.nodes:
            if (n_children := self.out_degree(cell)) > max_n_children:
                output.append(
                    f"{cell}: {n_children} successors; Expected=0..{max_n_children}"
                )

        if output.__len__() == 0:
            output = None

        return output

    @property
    def affinities(self) -> Sequence[float]:
        """"""
        output = []

        for piece in self.Pieces():
            output.extend(piece.affinities)

        return output

    def DividingCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        if with_time_point:
            output = (
                _rcd
                for _rcd in self.nodes.data(TIME_POINT)
                if self.out_degree(_rcd[0]) > 1
            )
        else:
            output = (_cll for _cll in self.nodes if self.out_degree(_cll) > 1)

        return tuple(output)

    @property
    def segments_iterator(self) -> Iterator[Tuple[int, cell_t, cell_t, bool]]:
        """"""
        time_points = grph.get_node_attributes(self, TIME_POINT)

        for edge in self.edges:
            time_point = time_points[edge[0]]
            is_last = edge[1] in self.leaves
            yield time_point, *edge, is_last

    def Pieces(
        self, /, *, from_cell: cell_t = None, with_time_point: int = None
    ) -> Sequence[single_track_t]:
        """"""
        output = []

        if from_cell is None:
            piece = [self.root]
            root_time_point = self.root_time_point
        else:
            piece = [from_cell]
            root_time_point = with_time_point
        affinities = []

        while True:
            last_cell = piece[-1]

            neighbors = tuple(self.neighbors(last_cell))
            n_neighbors = neighbors.__len__()
            if n_neighbors == 0:
                label = self.TrackLabelWithLeaf(last_cell, safe_mode=False)
                output.append(
                    single_track_t.NewFromOrderedCells(
                        piece, affinities, root_time_point, label
                    )
                )
                break
            elif n_neighbors == 1:
                next_cell = neighbors[0]
                piece.append(next_cell)
                affinities.append(self[last_cell][next_cell]["affinity"])
            else:
                output.append(
                    single_track_t.NewFromOrderedCells(
                        piece, affinities, root_time_point, None
                    )
                )
                next_time_point = root_time_point + piece.__len__()
                for neighbor in neighbors:
                    pieces = self.Pieces(
                        from_cell=neighbor,
                        with_time_point=next_time_point,
                    )
                    for piece in pieces:
                        if piece[0] is neighbor:
                            cells = (last_cell,) + tuple(piece)
                            affinity = self[last_cell][neighbor]["affinity"]
                            affinities = (affinity,) + tuple(piece.affinities)
                            piece = single_track_t.NewFromOrderedCells(
                                cells,
                                affinities,
                                piece.root_time_point - 1,
                                piece.label,
                            )
                        output.append(piece)
                break

        return output

    def TrackLabelsContainingCell(self, cell: cell_t, /) -> Sequence[int]:
        """"""
        output = []

        for leaf in self.leaves:
            try:
                _ = grph.shortest_path(self, source=cell, target=leaf)
            except grph.NetworkXNoPath:
                continue
            output.append(self.nodes[leaf][forking_track_t.SINGLE_TRACK_LABEL])

        return output

    def TrackLabelWithLeaf(self, leaf: cell_t, /, *, safe_mode: bool = True) -> int:
        """
        TrackLabelWithLeaf: Implicitly, it is SingleTrackLabelWithLeaf
        """
        if (not safe_mode) or (leaf in self.leaves):
            return self.nodes[leaf][forking_track_t.SINGLE_TRACK_LABEL]

        raise ValueError(f"{leaf}: Not a leaf cell")

    def TrackWithLeaf(
        self, leaf: cell_t, /, *, safe_mode: bool = True
    ) -> single_track_t:
        """
        TrackWithLeaf: Implicitly, it is SingleTrackWithLeaf
        """
        if (not safe_mode) or (leaf in self.leaves):
            cells = grph.shortest_path(self, source=self.root, target=leaf)
            affinities = tuple(
                self[cells[_idx]][cells[_idx + 1]]["affinity"]
                for _idx in range(cells.__len__() - 1)
            )
            label = self.TrackLabelWithLeaf(leaf, safe_mode=False)
            output = single_track_t.NewFromOrderedCells(
                cells, affinities, self.root_time_point, label
            )

            return output

        raise ValueError(f"{leaf}: Not a leaf cell")

    def AsSingleTrack(self) -> single_track_t:
        """"""
        output = [self.root]

        affinities = []
        while True:
            last_cell = output[-1]

            neighbors = tuple(self.neighbors(last_cell))
            n_neighbors = neighbors.__len__()
            if n_neighbors == 0:
                label = self.TrackLabelWithLeaf(last_cell, safe_mode=False)
                break
            elif n_neighbors == 1:
                next_cell = neighbors[0]
                output.append(next_cell)
                affinity = self[last_cell][next_cell]["affinity"]
                affinities.append(affinity)
            else:
                raise ValueError(
                    f"Attempt to convert the forking track with root {self.root} and "
                    f"{self.n_leaves} leaves into a single track"
                )

        output = single_track_t.NewFromOrderedCells(
            output, affinities, self.root_time_point, label
        )

        return output


class cell_track_state_t(named_tuple_t):
    position: Sequence[int]
    divides: bool = False
    dies: bool = False


track_h = Union[single_track_t, forking_track_t]
single_track_descriptions_h = Dict[int, Sequence[cell_track_state_t]]
