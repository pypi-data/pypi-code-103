from pathlib import Path
import git

import pytest
from graphene.test import Client


from acondbs.db.ops import export_db_to_csv_files
from acondbs.schema import schema_admin

from acondbs.db.backup import backup_db_as_csv_to_github_

##__________________________________________________________________||
@pytest.fixture
def local_repo(app, tmpdir_factory):
    """
    """

    # create a local repo with CSV files
    local_folder = Path(tmpdir_factory.mktemp('backup'))
    with app.app_context():
        export_db_to_csv_files(local_folder)
    local_repo = git.Repo.init(local_folder)
    local_repo.git.add(A=True)
    local_repo.index.commit('initial commit')

    yield local_repo

@pytest.fixture
def remote_repo(local_repo, tmpdir_factory):
    """remote repo

    """

    # create a remote repo (bare repo)
    folder = Path(tmpdir_factory.mktemp('backup'))
    remote_repo = git.Repo.init(folder, bare=True)
    remote_url = remote_repo.git_dir

    # push the current branch of the local repo to the remote repo
    remote = local_repo.create_remote('origin', url=remote_url)
    branch_name = local_repo.active_branch.name
    remote.push(refspec='{}:{}'.format(branch_name, branch_name))
    local_repo.heads[branch_name].set_tracking_branch(remote.refs[branch_name])

    yield remote_repo

##__________________________________________________________________||
def test_backup_db_as_csv_to_github_(app, local_repo, remote_repo):

    repo_path = local_repo.working_tree_dir
    head_sha_old = local_repo.head.commit.hexsha
    assert head_sha_old == remote_repo.head.commit.hexsha

    # change the DB content
    mutation = '''
          mutation m {
            deleteProduct(productId: 1001) {
              ok
            }
          }
        '''
    client = Client(schema_admin)
    with app.app_context():
        result = client.execute(mutation, context_value={})
        assert 'errors' not in result

    # take backup
    with app.app_context():
        backup_db_as_csv_to_github_(repo_path)

    # assert
    assert not local_repo.is_dirty(untracked_files=True)
    head_sha_new = local_repo.head.commit.hexsha
    assert not head_sha_old == head_sha_new
    assert head_sha_new == remote_repo.head.commit.hexsha

##__________________________________________________________________||
