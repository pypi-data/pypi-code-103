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
from typing import Iterator, List, Optional, Sequence, Tuple, Union, cast

import networkx as grph

from cell_tracking_BC.in_out.text.uid import ShortID
from cell_tracking_BC.type.cell import cell_t
from cell_tracking_BC.type.track import (
    TIME_POINT,
    cell_track_state_t,
    forking_track_t,
    single_track_descriptions_h,
    single_track_t,
    track_h,
    unstructured_track_t,
)


@dtcl.dataclass(repr=False, eq=False)
class tracks_t(List[Union[single_track_t, forking_track_t]]):
    @classmethod
    def NewFromUnstructuredTracks(
        cls, tracks: unstructured_tracks_t, /
    ) -> Tuple[tracks_t, Optional[Sequence[unstructured_track_t]]]:
        """"""
        instance = cls()

        invalids = []
        next_single_track_label = 1
        for track in tracks.track_iterator:
            issues = track.Issues()
            if issues is None:
                (
                    forking_track,
                    next_single_track_label,
                ) = forking_track_t.NewFromUnstructuredTrack(
                    track, next_single_track_label
                )

                if forking_track.n_leaves > 1:
                    instance.append(forking_track)
                else:
                    single_track = forking_track.AsSingleTrack()
                    instance.append(single_track)
            else:
                track.graph["issues"] = issues
                invalids.append(track)

        if invalids.__len__() == 0:
            invalids = None

        return instance, invalids

    def RootCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        if with_time_point:
            output = ((_tck.root, _tck.root_time_point) for _tck in self)
        else:
            output = (_tck.root for _tck in self)

        return tuple(output)

    def DividingCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        output = []

        for track in self:
            if isinstance(track, forking_track_t):
                output.extend(track.DividingCells(with_time_point=with_time_point))

        return output

    def LeafCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        leaves = []
        time_points = []
        for track in self:
            leaves.extend(track.leaves)
            time_points.extend(track.leaves_time_points)

        if with_time_point:
            return tuple(zip(leaves, time_points))

        return tuple(leaves)

    def TrackWithRoot(self, root: cell_t, /) -> track_h:
        """"""
        for track in self:
            if root is track.root:
                return track

        raise ValueError(f"{root}: Not a root cell")

    def TrackWithLeaf(self, leaf: cell_t, /) -> single_track_t:
        """
        TrackWithLeaf: Implicitly, it is SingleTrackWithLeaf
        """
        for track in self:
            for cell in track.leaves:
                if leaf is cell:
                    return track.TrackWithLeaf(cell, safe_mode=False)

        raise ValueError(f"{leaf}: Not a leaf cell")

    @property
    def single_tracks_iterator(self) -> Iterator[single_track_t]:
        """"""
        for track in self:
            for single_track in track.single_tracks_iterator:
                yield single_track

    def TrackLabelsContainingCell(
        self, cell: cell_t, /, *, safe_mode: bool = True
    ) -> Optional[Sequence[int]]:
        """"""
        for track in self:
            if cell in track:
                return track.TrackLabelsContainingCell(cell)

        if safe_mode:
            return None

        raise ValueError(f"{cell}: Not a tracked cell")

    def TrackLabelWithLeaf(self, leaf: cell_t, /) -> int:
        """
        TrackLabelWithLeaf: Implicitly, it is SingleTrackLabelWithLeaf
        """
        track = self.TrackWithLeaf(leaf)

        return track.label

    def SingleTrackDescriptions(self) -> single_track_descriptions_h:
        """"""
        output = {}

        for track in self.single_tracks_iterator:
            dividing_cells = track.DividingCells()
            description = []
            for cell in track:
                divides = cell in dividing_cells
                cell_track_state = cell_track_state_t(
                    position=cell.centroid, divides=divides
                )
                description.append(cell_track_state)

            output[track.label] = description

        return output

    def Print(self) -> None:
        """"""
        for track in self:
            print(track)

    def __str__(self) -> str:
        """"""
        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}: {self.__len__()=}"
        )


class unstructured_tracks_t(grph.DiGraph):
    def AddTrackSegment(
        self,
        src_cell: cell_t,
        tgt_cell: cell_t,
        src_time_point: int,
        affinity: float,
        /,
    ) -> None:
        """"""
        time_point = {TIME_POINT: src_time_point}
        time_point_p_1 = {TIME_POINT: src_time_point + 1}
        self.add_node(src_cell, **time_point)
        self.add_node(tgt_cell, **time_point_p_1)
        self.add_edge(src_cell, tgt_cell, affinity=affinity)

    def Issues(self) -> Optional[Sequence[str]]:
        """"""
        return unstructured_track_t.Issues(cast(unstructured_track_t, self))

    @property
    def track_iterator(self) -> Iterator[unstructured_track_t]:
        """"""
        for cells in grph.weakly_connected_components(self):
            track_view = self.subgraph(cells)
            # Copy or re-instantiation is necessary since the subgraph is a view
            yield unstructured_track_t(track_view)
