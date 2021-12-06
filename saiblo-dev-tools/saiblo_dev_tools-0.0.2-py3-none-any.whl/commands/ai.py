import json
from argparse import ArgumentParser, Namespace
from itertools import starmap
from sys import stderr, stdout

import requests

from utils.error import request_failed
from utils.path import open_file
from utils.storage import read_config, read_cookie, read_db, write_db


def _delete(tag: str) -> None:
    db = read_db()
    if tag not in db['ai']:
        raise RuntimeError('AI 不存在')
    token = db['ai'].pop(tag)
    stdout.write(f'删除 AI：`{token}`.\n')
    write_db(db)


def _insert(tag: str, token: str) -> None:
    db = read_db()
    if tag in db['ai']:
        stderr.write(f'AI 已存在，将自动覆盖先前的 token：`{db["ai"][tag]}`\n')
    db['ai'].update({tag: token})
    write_db(db)


def _list() -> None:
    db = read_db()
    ais = starmap(lambda tag, token: f'{tag} :  {token}\n', db['ai'].items())
    stdout.writelines(ais)


def _rename(old_tag: str, new_tag: str) -> None:
    db = read_db()
    if old_tag not in db['ai']:
        raise RuntimeError('AI 不存在')
    if new_tag in db['ai']:
        stderr.write(f'AI 已存在，将自动覆盖先前的 token：`{db["ai"][new_tag]}`\n')
    db['ai'].update({new_tag: db['ai'].pop(old_tag)})
    write_db(db)


def _upload(config_path: str) -> None:
    url = read_config()['url']
    cookie = read_cookie()
    config = json.load(open_file(config_path, encoding='utf-8'))
    ai = {'ai': open_file(config['path'], 'rb')}
    response = requests.post(f'{url}/admin/game/{config["game"]}/ai/', cookies={'sessionid': cookie},
                             data={'language': config['language']}, files=ai)
    if response.status_code != 200:
        request_failed(response)
    else:
        _insert(config['tag'], response.json()['token'])
        stdout.write('上传成功\n')


def subcommand_hook(parser: ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--list', action='store_true', help='列出所有 AI')
    group.add_argument('-i', '--insert', nargs=2, help='添加 AI', metavar=('tag', 'token'))
    group.add_argument('-d', '--delete', help='删除 AI', metavar='tag')
    group.add_argument('-r', '--rename', nargs=2, help='重命名 AI', metavar=('old_tag', 'new_tag'))
    group.add_argument('-u', '--upload', help='上传 AI', metavar='config_path')


def main(args: Namespace) -> None:
    if args.delete is not None:
        _delete(args.delete)
    elif args.insert is not None:
        _insert(*args.insert)
    elif args.list:
        _list()
    elif args.rename is not None:
        _rename(*args.rename)
    elif args.upload is not None:
        _upload(args.upload)
    else:
        raise RuntimeError(f'无法识别参数：`{args}`')
