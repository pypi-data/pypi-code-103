from random import randint, choice

from .algorithm import Algorithm
from mazesforprogrammers import Grid


class Sidewinder(Algorithm):
    """
    Convert grid into a maze using Sidewinder algorithm
    Move through each row west to east and choose at each Cell east or north
    When east is chosen, link the cell and add the cell to the current run
    When north is chosen, link one of the cells in the current run to it's north neighbor
    Top row will alway be contiguous because you can't choose "north"
    """

    def apply(self, grid: Grid) -> None:
        for row in grid.each_row():
            run = []

            for cell in row:
                run.append(cell)

                at_eastern_boundary = True if cell.east is None else False
                at_northern_boundary = True if cell.north is None else False

                close_run = at_eastern_boundary\
                    or (not at_northern_boundary and randint(1, 2) == 2)

                if close_run:
                    run_cell = choice(run)
                    if run_cell.north:
                        run_cell.link(run_cell.north)
                    run = []
                else:
                    cell.link(cell.east)
