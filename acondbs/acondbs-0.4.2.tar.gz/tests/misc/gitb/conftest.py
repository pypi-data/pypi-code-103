from pathlib import Path
import git

import pytest


##__________________________________________________________________||
@pytest.fixture()
def folder(tmpdir_factory):
    """path to an folder (not a git repo) with two text files

    f.txt
       abc

    g.txt
       123

    """
    folder = Path(tmpdir_factory.mktemp("git"))
    file1 = folder.joinpath("f.txt")
    file2 = folder.joinpath("g.txt")
    file1.write_text("abc\n")
    file2.write_text("123\n")
    yield folder


##__________________________________________________________________||
@pytest.fixture()
def repo(folder):
    """a git repo

    The folder is initialized as a git repo.
    The two files in the folder are committed.


    """
    repo = git.Repo.init(folder)
    repo.git.add(A=True)
    repo.index.commit("initial commit")
    yield repo


##__________________________________________________________________||
@pytest.fixture()
def bare_repo(repo, tmpdir_factory):
    """a bare repo, a clone of the repo"""
    folder = Path(tmpdir_factory.mktemp("git"))
    y = git.Repo.clone_from(repo.working_tree_dir, folder, bare=True)
    yield y


@pytest.fixture()
def github_repo_url(bare_repo, tmpdir_factory):
    """a factory fixture"""
    url = "git@github.com:TaiSakuma/fuzzy-garbanzo.git"

    def _f():
        """create a clone of the bare repo and push force
        the content to the github repo

        """
        folder = Path(tmpdir_factory.mktemp("git"))
        clone = git.Repo.clone_from(bare_repo.git_dir, folder)
        branch_name = clone.active_branch.name
        remote = clone.create_remote("github", url=url)
        remote.push(refspec=f"{branch_name}:{branch_name}", force=True)
        return url

    yield _f


@pytest.fixture(
    params=[
        "local_folder",
        # 'github_repo'
    ]
)
def remote_url(request, bare_repo, github_repo_url):
    p = request.param
    if p == "local_folder":
        y = bare_repo.git_dir
    elif p == "github_repo":
        y = github_repo_url()
    else:
        raise ValueError(f"unknown param: {p}")
    yield y


##__________________________________________________________________||
