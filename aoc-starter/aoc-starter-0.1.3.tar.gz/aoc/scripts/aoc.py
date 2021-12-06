import os
import pathlib
from typing import Optional

import click

from aoc.helpers import display_solution
from aoc.helpers import get_latest_year
from aoc.helpers import instantiate_solution
from aoc.solution_manager import SolutionManager


@click.group()
def cli() -> None:
    """Advent of Code"""


@cli.command()
def init() -> None:
    """Initialize a new solution folder"""
    curdir = pathlib.Path(os.getcwd())

    if os.listdir(curdir):
        click.echo("Please run this command from an empty directory")
        return

    pathlib.Path("input.txt").touch()
    pathlib.Path("requirements.txt").touch()


@cli.command()
@click.argument("day", type=int)
@click.option("--year", type=int, default=get_latest_year())
@click.option("--timeit", is_flag=True, default=False)
@click.option("--number", "-n", "number", type=int, default=1000)
@click.option("-i", "input_file", type=str, default="input.txt")
@click.option("-s", "solution_file", type=str, default=None)
def run(
    day: int,
    year: int,
    timeit: bool,
    number: int,
    input_file: str,
    solution_file: Optional[str],
) -> None:
    """Run a solution file"""
    if not input_file:
        click.echo("Please specify an input file.")
        return

    if not solution_file:
        solution_file = f"{year}/day{day:02}.py"

    input_path = pathlib.Path(input_file)
    solution_path = pathlib.Path(solution_file)

    solution = instantiate_solution(solution_path, input_path)
    display_solution(solution, timeit, number)


@cli.command()
@click.argument("day", type=int)
@click.option("--year", type=int, default=get_latest_year())
@click.option("--name", type=str)
def create(year: int, day: int, name: Optional[str]) -> None:
    """Create a soution module"""
    try:
        manager = SolutionManager(year, day, name).create()
    except FileExistsError:
        click.echo(f"Solution for day {day}, {year} already exists!")
        return

    click.echo(f"Created solution template at {manager.solution_filepath}")
