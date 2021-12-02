import git
from pathlib import Path

import pytest

from acondbs.misc import gitb

##__________________________________________________________________||
def test_push(remote_url, tmpdir_factory):
    """test push()

    """

    # create two clones
    folder1 = Path(tmpdir_factory.mktemp('git'))
    repo1 = git.Repo.clone_from(remote_url, folder1)

    folder2 = Path(tmpdir_factory.mktemp('git'))
    repo2 = git.Repo.clone_from(remote_url, folder2)

    # save sha
    head_sha_old = repo1.head.commit.hexsha
    assert head_sha_old == repo2.head.commit.hexsha

    # commit a change in repo1
    file1 = folder1.joinpath('f.txt')
    with file1.open("a") as f:
        f.write('1')
    repo1.git.add(A=True)
    repo1.index.commit('update')

    # save sha
    head_sha_new = repo1.head.commit.hexsha
    assert not head_sha_old == head_sha_new

    # call push()
    gitb.push(folder1)

    # assert
    remote2 = repo2.remotes[repo2.active_branch.tracking_branch().remote_name]
    remote2.pull()
    assert head_sha_new == repo2.head.commit.hexsha


##__________________________________________________________________||
def test_nonexistent_path(tmpdir_factory):
    """assert exception is raised for nonexistent path
    """
    folder = Path(tmpdir_factory.mktemp('git'))
    path = folder.joinpath('nonexistent')

    with pytest.raises(ValueError):
        gitb.push(path)

def test_path_not_repo(folder):
    """assert exception is raised if not a repo
    """

    with pytest.raises(ValueError):
        gitb.push(folder)

def test_repo_no_remote(repo):
    """assert exception is raised if a repo has no tracking branch
    """

    with pytest.raises(ValueError):
        gitb.push(repo.working_tree_dir)

##__________________________________________________________________||
