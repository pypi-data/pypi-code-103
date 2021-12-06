"""
Git commands module

Module for interacting with Git command line interface

author: Ryan Long <ryan.long@noaa.gov>
"""

import os
import subprocess
import logging

logger = logging.getLogger(__name__)


def _command_safe(cmd, cwd=os.getcwd()) -> subprocess.CompletedProcess:
    """_command_safe ensures commands are run safely and raise exceptions
    on error

    https://stackoverflow.com/questions/4917871/does-git-return-specific-return-error-codes
    """
    try:
        logger.debug("running '%s' in '%s'", cmd, cwd)
        return subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as error:
        logger.info(error.stdout)
        if error.stderr:
            logger.error(error.stderr)
            raise
        return subprocess.CompletedProcess(returncode=0, args="", stdout=error.stdout)


def add(repopath=os.getcwd()):
    """git_add

    Args:
        _path (str): path of assets to add
        repopath (str, optional): local repository path if not cwd. Defaults to os.getcwd().

    Returns:
        CompletedProcess:
    """
    cmd = ["git", "add", "--all"]
    return _command_safe(cmd, repopath)


def commit(message, repopath=os.getcwd()):
    """git_commit

    Args:
        username (str):
        name (str): name of report to commit
        repopath (str, optional): local repository path if not cwd. Defaults to os.getcwd().

    Returns:
        CompletedProcess:
    """
    cmd = ["git", "commit", "-m", f"'{message}'"]
    return _command_safe(cmd, repopath)


def status(repopath=os.getcwd()):
    """status returns the output from git status

    Args:
        repopath (str, optional): The root path of the repo. Defaults to os.getcwd().

    Returns:
        CompletedProcess
    """
    return _command_safe(["git", "status"], repopath)


def pull(destination="origin", branch=None, repopath=os.getcwd()):
    """git_pull

    Args:
        destination (str, optional): Defaults to "origin".
        branch (str, optional): Defaults to current branch.
        repopath (str, optional): Defaults to os.getcwd().

    Returns:
        CompletedProcess
    """

    cmd = ["git", "pull", destination]
    if branch:
        cmd.append(branch)
    return _command_safe(cmd, repopath)


def push(destination="origin", branch=None, repopath=os.getcwd()):
    """git_push

    Args:
        destination (str, optional): Defaults to "origin".
        branch (str, optional): Defaults to current branch.
        repopath (str, optional): Defaults to os.getcwd().

    Returns:
        CompletedProcess
    """
    cmd = ["git", "push", destination]
    if branch:
        cmd.append(branch)
    return _command_safe(cmd, repopath)


def clone(url, target_path):
    """git_clone

    Args:
        url (str): remote url
        target_path (str): local target path

    Returns:
        CompletedProcess
    """
    cmd = ["git", "clone", url, target_path]
    return _command_safe(cmd, target_path)
