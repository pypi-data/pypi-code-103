import os
import glob
import shutil
from .path import join_path,get_relative_path
import platform
import time
from dulwich.errors import GitProtocolError
def is_linux():
    return platform.system()=='Linux'
def is_windows():
    return platform.system()=='Windows'

def is_mac():
    return platform.system()=='Darwin'


def is_empty_dir(path):
    return os.path.exists(path) and os.path.isdir(path) and len(os.listdir(path))==0
def clean_dir(path):
    assert os.path.isdir(path)
    for item in os.listdir(path):
        child_path=os.path.join(path,item)
        if os.path.isdir(child_path):
            shutil.rmtree(child_path)
        else:
            os.remove(child_path)
def check_and_make_empty_dir(dst,overwrite):
    if os.path.exists(dst):
        if os.path.isfile(dst):
            if overwrite:
                os.remove(dst)
                os.makedirs(dst)
            raise NotADirectoryError('Not a directory:%s'%(dst))
        elif not is_empty_dir(dst):
            if overwrite:
                clean_dir(dst)
            else:
                raise RuntimeError('Directory nor empty : %s'%(dst))
    else:
        os.makedirs(dst)
def generate_hash(s,times=1):
    assert times>=1
    import hashlib
    m = hashlib.md5()
    def gen():
        m.update(s.encode('utf-8'))
        return m.hexdigest()[:10]
    for i in range(times):
        data=gen()
    return data



def copy_repo_files_to(repo_path,relative_path,dst_path,repo_name):
    '''

    :param src:
    :param dst:
    :return:
    TODO:
        should overwrite if file exists?
    '''
    src_path=join_path(repo_path,relative_path)
    if os.path.isfile(src_path):
        shutil.copy(src_path,dst_path)
    elif '*' in src_path:
        # dst_path must be a dir
        items=glob.glob(src_path,recursive=True)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        assert os.path.isdir(dst_path)
        for item_path in items:
            item_rel_path=get_relative_path(repo_path,item_path)
            item_dst_path=join_path(dst_path,item_rel_path)
            if os.path.isdir(item_path):
                shutil.copytree(item_path,item_dst_path)
            else:
                assert os.path.isfile(item_path)
                shutil.copy(item_path,item_dst_path)
    else:
        assert os.path.isdir(src_path)
        if os.path.exists(dst_path):
            assert os.path.isdir(dst_path)
            dst_name=repo_name if relative_path=='/' else os.path.basename(src_path)
            dst_path=join_path(dst_path,dst_name)
            os.makedirs(dst_path)
        else:
            os.makedirs(dst_path)
        if relative_path=='/':
            # copy the whole repo
            copy_repo_files_to_dir(src_path,dst_path,exclude_git=True)
        else:
            # copy some dir under the repo
            copy_repo_files_to_dir(src_path,dst_path,exclude_git=False)


def copy_repo_files_to_dir(src,dst,exclude_git=True):
    if not os.path.exists(dst):
        os.makedirs(dst)
    assert os.path.isdir(dst)
    for child in os.listdir(src):
        if child=='.git' and exclude_git:
            continue
        child_path=os.path.join(src,child)
        dst_child_path=os.path.join(dst,child)
        if os.path.isdir(child_path):
            shutil.copytree(child_path,dst_child_path)
        else:
            shutil.copy(child_path,dst_child_path)
def copy_to_repo(src_path,repo_dir,relative_path,overwrite=True):
    '''copy a file or dir into relative path under repo_dir'''
    src_path=os.path.abspath(src_path)
    dst_path=join_path(repo_dir,relative_path)
    dst_parent = os.path.dirname(dst_path)
    if not os.path.exists(dst_parent):
        os.makedirs(dst_parent)
    if os.path.exists(dst_path):
        if os.path.isdir(src_path):
            dst_path=os.path.join(dst_path,os.path.basename(src_path))
            if os.path.exists(dst_path):
                if overwrite:
                    shutil.rmtree(dst_path)
                    time.sleep(1e-10)
                else:
                    raise FileExistsError('% already exists and overwrite is %s'%(dst_path,overwrite))
            return shutil.copytree(src_path,dst_path)
        else:
            assert os.path.isfile(src_path)
            if os.path.isdir(dst_path):
                shutil.copy(src_path,os.path.join(dst_path,os.path.basename(src_path)))
            else:
                if overwrite:
                    os.remove(dst_path)
                    shutil.copy(src_path,dst_path)
                else:
                    # this will raise an error, by design.
                    shutil.copy(src_path,dst_path)
                    raise FileExistsError('%s already exists but overwrite is not True'%(dst_path))
    else:
        if os.path.isfile(src_path):
            shutil.copy(src_path,dst_path)
        else:
            assert os.path.isdir(src_path)
            shutil.copytree(src_path,dst_path)




