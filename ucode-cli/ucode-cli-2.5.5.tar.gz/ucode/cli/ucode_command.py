import os

import typer
from pathlib import Path

from ucode.helpers.clog import CLog
from ucode.services.dsa.problem_service import ProblemService
from ucode.ucode.ucode_srv import UCode

app = typer.Typer()


@app.command(name="upload")
def upload_problem_to_ucode(
        problem_folder: Path = typer.Argument(".", help="Problem folder to upload, default to current folder.",
                                              exists=True, file_okay=False),
        lesson_id: int = typer.Option(None, "--lesson", "-l",
                                      help='Lesson ID to which the problem will be added to if specified'),
        server: str = typer.Option("ucode.vn", "--server", "-s",
                                   help='Server (domain) of site to upload, default to `ucode.vn`'),
        env: str = typer.Option("prod", "--env", "-e",
                                help='prod|dev for ucode environment'),
):
    problem = ProblemService.load(os.path.abspath(problem_folder), load_testcase=True)
    CLog.important(f"Loaded problem `{problem.name}` with {len(problem.testcases)} testcases, "
              f"and {len(problem.testcases_sample)} sample testcases")
    ucode = UCode(env, domain=server)
    prob_id = ucode.create_problem(problem=problem, xp=-1, score=100)
    CLog.info(f"Uploaded problem with id #`{prob_id}` to `{server}`")
    if lesson_id:
        ucode.add_question_to_quiz(quiz_id=lesson_id, question_ids=[prob_id])
        CLog.info(f"Problem #{prob_id} added to quiz #{lesson_id}")


@app.command(name="upload_all")
def upload_all_problems_to_ucode(
        folder: Path = typer.Argument(".", help="Folder contain all problems to upload, default to current folder.",
                                              exists=True, file_okay=False),
        lesson_id: int = typer.Option(None, "--lesson", "-l",
                                      help='Lesson ID to which the problem will be added to if specified'),
        server: str = typer.Option("ucode.vn", "--server", "-s",
                                   help='Server (domain) of site to upload, default to `ucode.vn`'),
        env: str = typer.Option("prod", "--env", "-e",
                                help='prod|dev for ucode environment'),
        check: bool = typer.Option(False, "--check", "-c",
                                       help='Check problems without real uploading'),
):
    problems = ProblemService.read_all_problems(folder, nested_folder=False)
    CLog.info(f"Founded {len(problems)} problem folders in `{folder}`")

    uploaded = []
    for i, (problem_folder, problem) in enumerate(problems):
        problem = ProblemService.load(os.path.abspath(problem_folder), load_testcase=True)
        CLog.important(f"Loaded problem #{i+1}: `{problem.name}` with {len(problem.testcases)} testcases, "
                  f"and {len(problem.testcases_sample)} sample testcases")
        if not check:
            ucode = UCode(env, domain=server)
            prob_id = ucode.create_problem(problem=problem, xp=-1, score=100)
            uploaded.append(prob_id)
            CLog.info(f"Uploaded problem with id #`{prob_id}` to `{server}`")
            if lesson_id:
                ucode.add_question_to_quiz(quiz_id=lesson_id, question_ids=[prob_id])
                CLog.info(f"Problem #{prob_id} added to quiz #{lesson_id}")

    CLog.important(f"Total problems uploaded: {len(uploaded)}")

    if check:
        CLog.important(f"Checking mode only, no problems uploaded")


@app.command(name="login")
def login(email: str = typer.Argument(..., help='ucode.vn email'),
          password: str = typer.Argument(..., help='ucode.vn password'),
          server: str = typer.Option("ucode.vn", "--server", "-s",
                                   help='Server (domain) of site to upload, default to `ucode.vn`'),
          env: str = typer.Option("prod", "--env", "-e",
                                   help='prod|dev for ucode environment'),
          ):
    ucode = UCode(env, domain=server)
    ucode.login(email, password)


@app.command(name="get")
def get_ucode_problem(
        problem_id: str = typer.Argument(..., help='The id of the a uCode problem'),
        dir: Path = typer.Option(".", "--dir", "-d",
                                 help="Folder that contains the problem, default to current folder.",
                                 exists=True, file_okay=False),
        overwrite: bool = typer.Option(False, "--overwrite", "-F",
                                       help='Force overwriting existing folder'),
        split_input: bool = typer.Option(False, "--split_input", "-S",
                                       help='Split number in testcase input into separated lines'),
        testcase_format: str = typer.Option("ucode", "--test_format", "-t",
                                help='ucode|themis'),
        server: str = typer.Option("ucode.vn", "--server", "-s",
                                   help='Server (domain) of site to upload, default to `ucode.vn`'),
        env: str = typer.Option("prod", "--env", "-e",
                                help='prod|dev for ucode environment')):
    """
    Get a uCode problem and save as to a local folder

    Syntax:
    ucode svr get [-d {folder}] {ucode-problem-id}

    Ex.:
    ucode svr get -d problems/ 44242

    """
    CLog.error(f"This command is not supported anymore!")
    return 
    ucode = UCode(env, domain=server)
    CLog.info(f"Getting problem `{problem_id}`...")
    dsa_problem = ucode.get_question(problem_id, download_testcases=True)

    if split_input:
        ProblemService.split_testcases_input(dsa_problem)

    CLog.info(f"Got problem `{dsa_problem.name}`, saving to `{dir}`...")
    ProblemService.save(dsa_problem, base_folder=dir, overwrite=overwrite, testcase_format=testcase_format)
    CLog.info(f"DONE")


if __name__ == "__main__":
    app()