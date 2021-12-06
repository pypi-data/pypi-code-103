from pathlib import Path

import typer
from ucode.helpers.clog import CLog

from ucode.models.problem import ProblemFolderFormat
from ucode.oj.codeforces.codeforces import Codeforces
from ucode.services.dsa.problem_service import ProblemService

app = typer.Typer()


@app.command(name="get")
def get_codeforce_problem(
        problem_url: str = typer.Argument(..., help='The id or url of the a Codeforces problem'),
        dir: Path = typer.Option(".", "--dir", "-d",
                                 help="Folder that contains the problem, default to current folder.",
                                 exists=True, file_okay=False),
        code: str = typer.Option("", "--code", "-c",
                                  help='Problem code to overwrite the Codeforces\'s name'),
        overwrite: bool = typer.Option(False, "--overwrite", "-F",
                                       help='Force overwriting existing folder'),
        split_input: bool = typer.Option(False, "--split_input", "-S",
                                         help='Split number in testcase input into separated lines')):
    """
    Get a codeforces problem and save as to a local folder

    Syntax:
    ucode cf get [-d {folder}] [-c {problem-code}] {codeforces-problem-url-or-id}

    Ex.:
    ucode cf get -d problems/ https://codeforces.com/problemset/problem/1257/D
    or:
    ucode cf get -d problems/ -c "Monster Killing" 1257D
    or:
    ucode cf get -d problems/ 1257/D

    """
    cf = Codeforces()
    CLog.info(f"Getting problem `{problem_url}`...")
    dsa_problem = cf.get_problem_from_url(problem_url)

    if split_input:
        ProblemService.split_testcases_input(dsa_problem)

    CLog.info(f"Got problem `{dsa_problem.name}`, saving to `{dir}`...")
    ProblemService.save(dsa_problem, base_folder=dir, problem_code=code, overwrite=overwrite)
    CLog.info(f"DONE")

