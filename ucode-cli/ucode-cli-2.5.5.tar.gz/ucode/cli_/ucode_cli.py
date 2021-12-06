import os
from datetime import datetime

import click

from ucode.helpers.clog import CLog
from ucode.services.dsa.problem_service import ProblemService
from ucode.ucode.ucode_srv import UCode


@click.group()
def cli():
    """
    uCode.vn CLI tools - ucode CLI tools by Thuc Nguyen (https://github.com/thucnc)
    """
    click.echo("uCode.vn CLI tools - ucode CLI tools by Thuc Nguyen (https://github.com/thucnc)")


@cli.group(name='srv')
def ucode_group():
    """
    ucode server tools
    """
    click.echo("ucode server tools")


@cli.group(name='dsa')
def dsa_group():
    """
    DSA problem tools
    """
    click.echo("Common DSA tools")




@dsa_group.command(name='convert')
@click.option('--overwrite/--no-overwrite', default=False, help='Overwrite existing folder, default - No')
@click.option('-o', '--output', default='', type=click.STRING, help='Output problem folder for the converted problem')
@click.argument('problem_folder', metavar='{problem_folder}')
def convert_problem(problem_folder, overwrite, output):
    """
    Convert problem folder to proper ucode format
    WARN: this will OVERWRITE current problem folder

    Syntax:
    ucode dsa convert {problem-folder}

    Ex.:
    ucode dsa convert  ../problems/prob2

    """
    problem_folder = os.path.abspath(problem_folder)
    if not output:
        output = problem_folder

    problem = ProblemService.load(problem_folder, load_testcase=True)

    print(problem.name, problem.code)

    base_folder = os.path.dirname(problem_folder)
    problem_folder = os.path.basename(problem_folder)

    # print(base_folder, problem_folder)
    ProblemService.save(problem, base_folder=base_folder, problem_folder=output, overwrite=overwrite)


@ucode_group.command(name="create")
@click.option('-c', '--credential', default='credentials.ini',
              type=click.Path(dir_okay=False, exists=True),
              prompt='Credential file', help='Configuration file that contain hackerrank user name/pass')
@click.option('-l', '--lesson', type=click.INT, help='Lesson id')
@click.option('-s', '--score', default=100, type=click.INT, help='Score of this question')
@click.option('-x', '--xp', default=100, type=click.INT, help='XP of this question')
@click.argument('problem_folder', metavar='{problem_folder}')
def ucode_create_problem(lesson, credential, score, problem_folder, xp):
    """
    Create problem on ucode.vn

    Syntax:
    ucode srv create [--upload-testcases] -l {lesson_id} -s {score} {dsa_problem_folder}

    """
    api_url, token = UCode.read_credential(credential)
    if not api_url or not token:
        CLog.error(f'Username and/or password are missing in {credential} file')
        return

    ucode = UCode(api_url, token)

    problem = ProblemService.load(problem_folder, load_testcase=True)
    problem_id = ucode.create_problem(lesson, problem, score=score, xp=xp)

    if problem:
        CLog.important(f'Problem `{problem_id}` created')


@ucode_group.command(name="create-all")
@click.option('-c', '--credential', default='credentials.ini',
              type=click.Path(dir_okay=False, exists=True),
              prompt='Credential file', help='Configuration file that contain hackerrank user name/pass')
@click.option('-l', '--lesson', type=click.INT, help='Lesson id')
@click.option('-s', '--score', default=100, type=click.INT, help='Score of this question')
@click.option('-x', '--xp', default=100, type=click.INT, help='XP of this question')
@click.argument('base_folder', metavar='{base_folder}')
def ucode_create_problems(lesson, credential, score, base_folder, xp):
    """
    Create multiple problems on ucode.vn

    Syntax:
    ucode create-all [--upload-testcases] -l {lesson_id} -s {score} {dsa_problem_folder}

    """
    api_url, token = UCode.read_credential(credential)
    if not api_url or not token:
        CLog.error(f'Username and/or password are missing in {credential} file')
        return

    ucode = UCode(api_url, token)

    problems = ProblemService.read_all_problems_v1(base_folder, load_testcase=True)

    for problem_tuple in problems:
        problem = problem_tuple[1]
        problem_id = ucode.create_problem(lesson, problem, score=score, xp=xp)
        if problem:
            CLog.important(f'Problem `{problem_id}` created')


if __name__ == "__main__":
    problem_folder = "/home/thuc/projects/ucode/ucode-cli/problems/string_changes"

    problem = ProblemService.load(problem_folder, load_testcase=True)

    base_folder = os.path.dirname(problem_folder)
    problem_folder = os.path.basename(problem_folder)

    # print(base_folder, problem_folder)
    ProblemService.save(problem, base_folder=base_folder, problem_folder=problem_folder, overwrite=True)
    convert_problem(problem_folder, overwrite=True)