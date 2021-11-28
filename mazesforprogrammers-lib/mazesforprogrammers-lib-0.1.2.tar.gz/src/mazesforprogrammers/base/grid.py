from typing import List, Generator, Tuple, Optional, cast
import random
from .cell import Cell, is_cell

Key = Tuple[int, int]
CellList = List[Cell]


class Grid():

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def columns(self) -> int:
        return self._columns

    def __init__(self, rows, columns) -> None:
        if rows is None or rows < 2:
            raise ValueError("rows must be an int greater than 1")
        if columns is None or columns < 2:
            raise ValueError("columns must be an int greater than 1")

        self._rows: int = rows
        self._columns: int = columns
        self._grid: List[CellList] = self.prepare_grid()
        self.configure_cells()

    def prepare_grid(self) -> List[CellList]:
        """Setup 2d array in _grid of Cells with Cell(r,c)"""

        return [[Cell(r, c) for c in range(self._columns)] for r in range(self._rows)]

    def configure_cells(self):
        for row in range(self._rows):
            for column in range(self._columns):
                cell = self[row, column]

                cell.north = self[row - 1, column]
                cell.south = self[row + 1, column]
                cell.east = self[row, column + 1]
                cell.west = self[row, column - 1]

    def each_row(self) -> Generator[CellList, None, None]:
        for row in range(self.rows):
            yield self._grid[row]

    def each_cell(self) -> Generator:
        for row in self.each_row():
            for cell in row:
                yield cell

    def cell_at(self, row, column) -> Optional[Cell]:
        if self.index_is_in_range((row, column)):
            return self._grid[row][column]
        return None

    def set_cell_at(self, row: int, column: int, cell: Cell) -> None:
        self._grid[row][column] = cell

    def __getitem__(self, key: Key) -> Optional[Cell]:
        """Override [] accessor to return the Cell in _grid as long as it's within bounds"""

        if not is_key(key):
            raise IndexError('Only valid indexes ex. Grid[row,col] are supported')
        return self.cell_at(*key)

    def __setitem__(self, key: Key, new_cell: Cell) -> None:
        """Override [] setter to allow a key to set an item"""

        if not is_key(key) or not self.index_is_in_range(key):
            raise IndexError('Only valid indexes ex. Grid[row,col] are supported')
        if not is_cell(new_cell):
            raise ValueError('Only a Cell can be placed into the grid')
        self.set_cell_at(*key, new_cell)

    def random_cell(self) -> Cell:
        row = random.randrange(self.rows)
        column = random.randrange(self.columns)
        return cast(Cell, self[row, column])

    def index_is_in_range(self, key: Key) -> bool:
        """
        Check that a key[row, column] uses indexes in range
        """
        return key[0] in range(self.rows) and key[1] in range(self.columns)

    def print_grid(self) -> str:
        output = "+" + "---+" * self.columns + "\n"

        for row in self.each_row():
            top = "|"
            bottom = "+"
            for cell in row:
                body = "   "  # three spaces
                east_boundary = " " if cell.linked(cell.east) else "|"
                top += body + east_boundary

                south_boundary = "   " if cell.linked(cell.south) else "---"
                corner = "+"
                bottom += south_boundary + corner

            output += top + "\n"
            output += bottom + "\n"

        return output

    def __str__(self) -> str:
        return f'Grid with {self._rows} rows and {self._columns} columns.'

    def __repr__(self) -> str:
        return f'Grid(rows={self._rows}, columns={self._columns})'


def is_key(key: Key) -> bool:
    """
    Used to check that keys are valid format and in range
    """
    return type(key) == tuple and len(key) == 2 and all(type(value) == int for value in key)
