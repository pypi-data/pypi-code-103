from __future__ import annotations
# Not necessary in Python 3.10>
from typing import List, Dict, Optional, Any

Links = Dict["Cell", bool]
CellList = List["Cell"]


class Cell():
    """Represent a cell"""

    @property
    def row(self) -> int:
        return self._row

    @property
    def column(self) -> int:
        return self._column

    @property
    def links(self) -> CellList:
        return list(self._links.keys())

    @property
    def neighbors(self) -> CellList:
        """Returns list of all neighbors (north, east, south, west)"""

        neighbors: CellList = []
        if self.north:
            neighbors.append(self.north)
        if self.east:
            neighbors.append(self.east)
        if self.south:
            neighbors.append(self.south)
        if self.west:
            neighbors.append(self.west)
        return neighbors

    def __init__(self, row: int, column: int) -> None:
        self._row: int = row
        self._column: int = column
        self._links: Dict[Cell, bool] = {}
        # TODO: Consider changing neighbor members into a dict?
        self.north: Optional[Cell] = None
        self.east: Optional[Cell] = None
        self.south: Optional[Cell] = None
        self.west: Optional[Cell] = None

    def __str__(self) -> str:
        return f'Cell row is {self._row} and column is {self._column}.'

    def __repr__(self) -> str:
        return f'Cell(row={self._row}, column={self._column})'

    def link(self, cell, bidirectional=True) -> Cell:
        self._links[cell] = True
        if bidirectional:
            cell.link(self, bidirectional=False)
        return self

    def unlink(self, cell, bidirectional=True) -> Cell:
        del self._links[cell]
        if bidirectional:
            cell.unlink(self, bidirectional=False)
        return self

    def linked(self, cell) -> bool:
        """Returns if cell is in _links of cell"""

        return cell in self._links


def is_cell(cell: Any) -> bool:
    return isinstance(cell, Cell)
