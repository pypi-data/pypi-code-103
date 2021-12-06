import os.path
from argparse import ArgumentParser, Namespace
from sys import stdout

from utils.config import COOKIE


def _logout() -> None:
    if not os.path.exists(COOKIE):
        raise RuntimeError('您尚未登录')
    if not os.path.isfile(COOKIE):
        raise RuntimeError(f'路径 `{COOKIE}` 已存在，但不是文件')
    os.remove(COOKIE)
    stdout.write('成功删除 Cookie\n')


def subcommand_hook(parser: ArgumentParser) -> None:
    return


def main(args: Namespace) -> None:
    _logout()
