import os
from sys import stderr
from typing import IO


def open_file(path: str, *args, **kwargs) -> IO:
    if not os.path.exists(path):
        raise RuntimeError(f'文件 `{path}` 不存在')
    if not os.path.isfile(path):
        raise RuntimeError(f'路径 `{path}` 已存在，但不是文件')
    return open(path, *args, **kwargs)


def make_dir(path: str) -> None:
    if not os.path.exists(path):
        os.mkdir(path)
        stderr.write(f'目录 `{path}` 不存在，已自动创建\n')
    elif not os.path.isdir(path):
        raise RuntimeError(f'路径 `{path}` 已存在，但不是目录')


def assert_exists_dir(path: str) -> None:
    if not os.path.exists(path):
        raise RuntimeError(f'目录 `{path}` 不存在')
    if not os.path.isdir(path):
        raise RuntimeError(f'路径 `{path}` 已存在，但不是目录')
