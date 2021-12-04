from pathlib import Path

import typer
from ucode.helpers.clog import CLog

from ucode.models.problem import ProblemFolderFormat
from ucode.services.dsa.problem_service import ProblemService
from ucode.services.testcase.testcase_service import TestcaseService

app = typer.Typer()


@app.command(name="create")
def create_dsa_problem(
        problem_name: str = typer.Argument(..., help='The name of the problem to be created, put in "..." '
                                                     'if there are spaces in the name.'),
        format: str = typer.Option("ucode", "--format", "-f",
                                  help='Testcase format: ucode,themis,hackerrank'),
        dir: Path = typer.Option(".", "--dir", "-d",
                                 help="Parent folder that contains new problem, default to current folder.",
                                 exists=True, file_okay=False),
        lang: str = typer.Option("vi", "--lang", "-l",
                                 help='Main problem statement language, default to "vi" for Vietnamese'),
        code: str = typer.Option("py", "--code", "-c",
                                 help='Programming language for solution and testcase, default to "py" for Python, '
                                      'available option: cpp|pas|py'),
        trans: str = typer.Option("", "--trans", "-t",
                                  help='List of additional statement languages, separated by commas, ex.: "en,ru"'),
        overwrite: bool = typer.Option(False, "--overwrite", "-F",
                                       help='Force overwriting existing folder'),
        sample: bool = typer.Option(False, "--sample", "-s",
                                       help='Generate sample problem data')
):
    """
    Create a problem boilerplate

    Syntax:
    ucode dsa create [-d {folder}] {problem name} [--overwrite]

    Ex.:
    ucode dsa create "Race Condition" -c py

    ucode dsa create -d problems -l en "Race Condition" --overwrite

    """
    tran_langs = []
    if trans.strip():
        tran_langs = trans.strip().split(",")
    ProblemService.create_problem(dir, problem_name, lang=lang, translations=tran_langs, overwrite=overwrite,
                                  programming_language=code, gen_sample=sample, testcase_format=format)
    # print("DSA create"))


@app.command(name="check")
def check_dsa_problem(problem_folder: Path = typer.Argument(".", help="Problem folder, default to current folder.",
                                                            exists=True, file_okay=False),
                      load: bool = False):
    """
    Check problem folder for proper format

    Syntax:
    ucode dsa check {problem-folder}

    Ex.:
    ucode dsa check ../problems/prob2

    """
    ProblemService.check_problem(str(problem_folder))
    if load:
        ProblemService.load(str(problem_folder), load_testcase=True)


@app.command(name="convert")
def convert_dsa_problem(problem_folder: Path = typer.Argument(".", help="Problem folder to be converted",
                                                              exists=True, file_okay=False),
                        _from: ProblemFolderFormat = typer.Option(ProblemFolderFormat.themis, "--from", "-f",
                                                                  help="From format"),
                        _to: ProblemFolderFormat = typer.Option(ProblemFolderFormat.ucode, "--to", "-t",
                                                                  help="To format"),
                        output: Path = typer.Option(None, "--output", "-o",
                                                    help="Output problem folder to be written to, "
                                                         "default to problem_folder"),
                        overwrite: bool = typer.Option(False, "--overwrite", "-F",
                                                       help='Force overwriting existing folder'),
                        testcases_only: bool = typer.Option(True, "--testcases_only", "-T",
                                                            help='Force overwriting existing folder')
                        ):
    if not output:
        output = ""
    ProblemService.convert(str(problem_folder), _from, _to, str(output),
                           overwrite=overwrite, convert_testcases_only=testcases_only)


@app.command(name="gentest")
def generate_testcase(
        problem_folder: Path = typer.Argument(".", help="Problem folder to generate test, default to current folder.",
                                                              exists=True, file_okay=False),
        # format: str = typer.Option("ucode", "--format", "-f",
        #                           help='Testcase format: ucode,themis,hackerrank'),
        num: int = typer.Option(20, "--num", "-n",
                                  help='Number of testcases to be generated'),
        code: str = typer.Option("cpp", "--code", "-c",
                                 help='Preferred programming language for solution and testcase,'
                                      'available options: cpp|pas|py'),
        overwrite: bool = typer.Option(False, "--overwrite", "-F",
                                       help='Force overwriting existing folder')):
    testcases = TestcaseService.generate_testcases(problem_folder=str(problem_folder),
                                                   testcase_count=num, overwrite=overwrite, programming_language=code)
    CLog.info(f"{len(testcases)} testcase(s) generated!")


if __name__ == "__main__":
    app()
