#!/usr/bin/env python
# -*-coding:utf-8-*-

import re
import errno
import os
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def get_project_path(dir=None):
    """
    返回mymodule存放的根目录

    如果指定dir 则返回根目录下的一个文件

    :param dir:
    :return:
    """
    path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if dir:
        path = os.path.join(path, dir)
    return path


def normalized_path(path='.') -> str:
    """
    默认支持 ~ 符号

    返回的是字符串

    which default support the `~`
    """
    if isinstance(path, Path):
        return str(path.expanduser())
    elif isinstance(path, str):
        if path.startswith('~'):
            path = os.path.expanduser(path)
        return path
    else:
        raise TypeError


def normalized_path_obj(path='.') -> Path:
    """
    默认支持 ~ 符号

    返回的是 Path 对象
    :param path:
    :return:
    """
    if isinstance(path, Path):
        return path.expanduser()
    elif isinstance(path, str):
        if path.startswith('~'):
            path = os.path.expanduser(path)
        return Path(path)
    else:
        raise TypeError


def rm(path, recursive=False):
    """
    the function can remove file or empty directory(default).

    use `shutil.rmtree` to remove the non-empty directory,you need add `recursive=True`

    """
    path = normalized_path_obj(path)
    if recursive:
        shutil.rmtree(path)
    else:
        if path.is_file():
            path.unlink()
        else:
            path.rmdir()


def mkdirs(path, mode=0o777):
    """
    Recursive directory creation function base on os.makedirs
    with a little error handling.
    """
    try:
        os.makedirs(path, mode=mode)
    except OSError as e:
        if e.errno != errno.EEXIST:  # File exists
            logger.error('file exists: {0}'.format(e))


def ls(path=".", glob=False):
    """
    like ls common， return Path object

    if `glob` set to True, then you can use the glob language for ls.
    """
    if glob:
        import glob
        return [normalized_path_obj(p) for p in glob.glob(path)]
    else:
        return [p for p in normalized_path_obj(path).iterdir()]


def ls_file(path=".", glob=False):
    """
    based on ls function but only return file.
    """
    return [p for p in ls(path, glob=glob) if p.is_file()]


def ls_dir(path=".", glob=False):
    """
    based on ls function, but only return directory.
    """
    return [p for p in ls(path, glob=glob) if p.is_dir()]


def pwd():
    """
    get current directory
    """
    return Path(os.getcwd())


def gen_filetree(startpath='.', filetype=""):
    """
    利用os.walk 遍历某个目录，收集其内的文件，返回
    (文件路径列表, 本路径下的文件列表)
    比如:
    (['shortly'], ['shortly.py'])
(['shortly', 'templates'], ['shortly.py'])
(['shortly', 'static'], ['shortly.py'])

    第一个可选参数 startpath  默认值 '.'
    第二个参数  filetype  正则表达式模板 默认值是"" 其作用是只选择某些文件
    如果是空值，则所有的文件都将被选中。比如 "html$|pdf$" 将只选中 html和pdf文件。
    """
    for root, dirs, files in os.walk(startpath):
        filelist = []
        for f in files:
            fileName, fileExt = os.path.splitext(f)
            if filetype:
                if re.search(filetype, fileExt):
                    filelist.append(f)
            else:
                filelist = files
        if filelist:  # 空文件夹不加入
            dirlist = root.split(os.path.sep)
            dirlist = dirlist[1:]
            if dirlist:
                yield (dirlist, filelist)
            else:
                yield (['.'], filelist)


def gen_allfile(startpath='.', filetype=""):
    """
    利用os.walk 遍历某个目录，收集其内的文件，返回符合条件的文件路径名
    是一个生成器。
    第一个可选参数 startpath  默认值 '.'
    第二个参数  filetype  正则表达式模板 默认值是"" 其作用是只选择某些文件
    如果是空值，则所有的文件都将被选中。比如 "html$|pdf$" 将只选中 html和pdf文件。
    """

    for dirlist, filelist in gen_filetree(startpath=startpath,
                                          filetype=filetype):
        for f in filelist:
            filename = os.path.join(os.path.join(*dirlist), f)
            yield filename
