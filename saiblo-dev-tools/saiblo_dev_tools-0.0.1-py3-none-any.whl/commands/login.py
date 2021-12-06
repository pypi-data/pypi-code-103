import os
from argparse import ArgumentParser, Namespace
from getpass import getpass
from sys import stdout

import requests

from utils.config import COOKIE
from utils.error import request_failed
from utils.storage import read_config


def _login(username: str) -> None:
    url = read_config()['url']
    password = getpass() if os.getenv('SAIBLO_PASSWORD') is None else os.getenv('SAIBLO_PASSWORD')
    response = requests.post(f'{url}/admin/script-login/', data={'username': username, 'password': password})
    if response.status_code != 200:
        request_failed(response)
    else:
        open(COOKIE, 'w', encoding='utf-8').write(response.cookies.get('sessionid'))
        stdout.write('登录成功\n')


def subcommand_hook(parser: ArgumentParser) -> None:
    parser.add_argument('login', help='登录', metavar='username')


def main(args: Namespace) -> None:
    if 'login' in args:
        _login(args.login)
    else:
        raise RuntimeError(f'无法识别参数：`{args}`')
