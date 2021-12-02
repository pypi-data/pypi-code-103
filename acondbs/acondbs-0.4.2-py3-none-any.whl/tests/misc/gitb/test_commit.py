import git

from pathlib import Path
import warnings

import pytest

from acondbs.misc import gitb

##__________________________________________________________________||
def test_empty_folder(tmpdir_factory):
    """assert empty folder won't be initialized as a repo
    """
    folder = Path(tmpdir_factory.mktemp('git'))
    with warnings.catch_warnings(record=True) as w:
        gitb.commit(folder)
    assert len(w) == 1
    assert not gitb.is_git_repo(folder)

##__________________________________________________________________||
@pytest.fixture()
def nonexistent_path(tmpdir_factory):
    """path to a nonexistent file
    """
    folder = Path(tmpdir_factory.mktemp('git'))
    path = folder.joinpath('nonexistent')
    yield path

def test_nonexistent_path(nonexistent_path):
    """assert exception is raised for nonexistent path
    """
    with pytest.raises(ValueError):
        gitb.commit(nonexistent_path)

##__________________________________________________________________||
def test_non_empty_folder(folder):
    """assert a repo initialized and files committed
    """
    gitb.commit(folder)
    repo = git.Repo(folder)
    assert not repo.is_dirty(untracked_files=True)
    ncommits = len(list(repo.iter_commits()))
    assert 1 == ncommits

##__________________________________________________________________||
def test_clean_repo(repo):
    """assert no empty commit is made
    """
    folder = repo.working_tree_dir
    with warnings.catch_warnings(record=True) as w:
        gitb.commit(folder)
    assert len(w) == 1
    assert not repo.is_dirty(untracked_files=True)
    ncommits = len(list(repo.iter_commits()))
    assert 1 == ncommits

@pytest.fixture()
def repo_dirty(repo):
    """a dirty repo

    The repo cotains a staged file, a modified file, a deleted file,
    and an untracked file.

    """
    folder = Path(repo.working_tree_dir)
    file1 = folder.joinpath('f.txt')
    file2 = folder.joinpath('g.txt')
    file3 = folder.joinpath('h.txt')
    file1.write_text('xyz')
    repo.git.add(file1)
    file1.write_text('zzz')
    file2.unlink()
    file3.write_text('qwe')
    yield repo

def test_dirty_repo(repo_dirty):
    """assert all changes commit
    """
    repo = repo_dirty
    folder = repo.working_tree_dir
    gitb.commit(folder)
    assert not repo.is_dirty(untracked_files=True)
    ncommits = len(list(repo.iter_commits()))
    assert 2 == ncommits

def test_default_message(repo_dirty):
    repo = repo_dirty
    folder = repo.working_tree_dir
    gitb.commit(folder)
    assert 'commit all' == repo.head.commit.message

def test_custom_message(repo_dirty):
    repo = repo_dirty
    folder = repo.working_tree_dir
    gitb.commit(folder, 'custom message')
    assert 'custom message' == repo.head.commit.message

##__________________________________________________________________||
