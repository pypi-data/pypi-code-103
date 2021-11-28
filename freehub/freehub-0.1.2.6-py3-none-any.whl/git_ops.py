from dulwich import porcelain
from dulwich.repo import Repo
from dulwich.index import build_index_from_tree
from dulwich.client import get_transport_and_path
from dulwich.client import HttpGitClient
import logging
import os
import shutil
import glob


def create_branch(repo, branch, force=False):
    porcelain.branch_create(repo, branch, force=force)


def switch_branch(repo, branch, recover=True):
    porcelain.update_head(repo, branch)
    if recover:
        clean_repo(repo)
        recover_from_head(repo)


def get_current_branch(repo):
    branch = porcelain.active_branch(repo)
    return branch


def is_git_repo(path):
    git_dir = os.path.join(path, '.git')
    return os.path.exists(path) and os.path.exists(git_dir) and os.path.isdir(git_dir)



def commit_current_branch(repo, message='empty message'):
    assert isinstance(repo, Repo)
    repo.do_commit(message=message.encode('utf-8'))


def list_remote_branch(remote_location):
    client, path = get_transport_and_path(remote_location)
    remote_refs, _, _ = client._discover_references(b"git-upload-pack", client._get_url(path))
    branches = []
    for key in remote_refs:
        key = key.decode()
        if key.startswith('refs/heads/'):
            key = key[11:]
            branches.append(key)
    return branches


def clean_repo(repo):
    path = repo.path
    children = os.listdir(path)
    for child in children:
        child = os.path.join(path, child)
        if os.path.basename(child) == '.git':
            continue
        if os.path.isdir(child):
            shutil.rmtree(child)
        else:
            os.remove(child)


def stage_all_changes(repo):
    status = porcelain.status(repo)
    paths = status.untracked + status.unstaged
    paths = [p.decode() if isinstance(p, bytes) else p for p in paths]
    paths = [repo.path + '/' + p for p in paths]
    if not paths:
        logging.info('Working tree is clean. Nothing to add.')
        return
    paths.append(repo.path)
    porcelain.add(repo, paths)


def recover_from_head(repo):
    '''git checkout -- .'''
    assert isinstance(repo, Repo)
    build_index_from_tree(repo.path, repo.index_path(), repo.object_store, repo[b'HEAD'].tree)


def clone_remote_repo(remote_location, target, quiet=True):
    porcelain.clone(remote_location, target, quiet=quiet)


def create_head(repo):
    git_add(repo, repo.path)
    commit_current_branch(repo)


def list_branch(repo):
    return [str(x, encoding='utf-8') for x in porcelain.branch_list(repo)]


def delete_branch(repo, branch):
    porcelain.branch_delete(repo, branch)


def merge_branch():
    pass


def fetch_remote_branch():
    pass


none_stream = porcelain.NoneStream()


def pull_remote_branch(repo, remote_location, branch, quiet=True):
    if quiet:
        porcelain.pull(repo, remote_location, branch,
                       outstream=none_stream, errstream=none_stream
                       )
    else:
        porcelain.pull(repo, remote_location, branch,
                       )


def push_local_branch(repo, branch, remote_location, quiet=True):
    '''local branch must be same with remote branch?'''
    if quiet:
        porcelain.push(repo, remote_location, branch,
                       outstream=none_stream, errstream=none_stream
                       )
    else:
        porcelain.push(repo, remote_location, branch,
                       )


# def push_local_branch_old(repo,branch,remote_location,remote_branch):
#     client, path = get_transport_and_path(remote_location)
#     remote_branch=('refs/heads/'+remote_branch).encode('utf-8')
#     branch=('refs/heads/'+branch).encode('utf-8')
#     def update_refs(refs):
#         refs[remote_branch] = repo[branch].id
#     client.send_pack(path, update_refs, repo.object_store.generate_pack_data,progress=porcelain.default_bytes_err_stream)

def git_init(path, mkdir=False):
    return Repo.init(path, mkdir)


def git_add(repo, paths):
    if isinstance(paths, str):
        paths = [paths]
    porcelain.add(repo, paths)


def exists_remote_branch(remote_location, branch):
    branches = list_remote_branch(remote_location)
    return branch in branches


def git_stash():
    pass


def git_stash_apply():
    pass


def git_stash_pop():
    pass


def test():
    default_remote_location = 'https://OpenGitspace:Gitspace@123456@gitee.com/OpenGitspace/meta'
    repo_path = './data/OpenGitspace'
    if is_git_repo(repo_path):
        repo = Repo(repo_path)
    else:
        repo = Repo.init(repo_path)

    branches = list_remote_branch(default_remote_location)
    branches = list(filter(lambda x: x[0] == 'n', branches))
    print(branches)
    print('local_branches:', list_branch(repo))
    create_head(repo)
    test_branch = '000_test'
    create_branch(repo, test_branch)
    switch_branch(repo, test_branch)
    pull_remote_branch(repo, default_remote_location, 'test')
    push_local_branch(repo, test_branch, default_remote_location, test_branch)
    status = porcelain.status(repo)
    paths = status.untracked + status.unstaged
    print(status)


if __name__ == '__main__':
    test()
