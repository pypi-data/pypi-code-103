import base64
import json
from argparse import ArgumentParser, Namespace
from sys import stderr, stdout

import requests

from utils.error import request_failed
from utils.path import make_dir, open_file
from utils.storage import read_config, read_cookie, read_db


def _test(config_path: str, result_dir: str) -> None:
    url = read_config()['url']
    db = read_db()
    cookie = read_cookie()
    config = json.load(open_file(config_path, encoding='utf-8'))

    def get_ai_from_tag(tag: str) -> str:
        if tag == 'human':
            return tag
        if tag not in db['ai']:
            raise RuntimeError(f'AI `{tag}` 不存在')
        return db['ai'][tag]

    room_id = None
    if 'human' in config['ai']:
        response = requests.post(f'{url}/admin/game/{config["game"]}/create-room/', cookies={'sessionid': cookie},
                                 json={'capacity': len(config['ai'])})
        data = response.json()
        room_id = data['room_id']
        base_url = data['base_url']
        for i, ai in enumerate(config['ai']):
            if ai == 'human':
                human_url = f'{base_url}/{room_id}/saiblo-dev-tools/{i}'
                stdout.write(f'Token of seat <{i}>: {str(base64.b64encode(human_url.encode("utf-8")), "utf-8")}\n')

    response = requests.post(f'{url}/admin/game/{config["game"]}/test/', cookies={'sessionid': cookie},
                             json={'ai': [get_ai_from_tag(tag) for tag in config['ai']],
                                   'room_id': room_id,
                                   'config': config['config']})
    if response.status_code != 200:
        request_failed(response)
    else:
        make_dir(result_dir)
        data = response.json()
        json.dump(data['config'], open(f'{result_dir}/config.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        json.dump(data['info'], open(f'{result_dir}/info.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        try:
            replay_uuid = data["replay_uuid"]
            response = requests.get(f'{url}/admin/game/download-replay/{replay_uuid}/', cookies={'sessionid': cookie})
            if response.status_code != 200:
                raise response.status_code
            with open(f'{result_dir}/replay{data["replay_type"]}', 'wb') as f:
                f.write(response.content)
        except Exception as e:
            stderr.write(f'警告：下载回放文件失败。\n      {e}')
        stdout.write(f'{data["status"]}\n')


def _upload(config_path: str) -> None:
    url = read_config()['url']
    cookie = read_cookie()
    config = json.load(open_file(config_path, encoding='utf-8'))
    game = open_file(config['path'], 'rb')
    game_id = config['id']
    response = requests.post(f'{url}/admin/game/{game_id}/upload/', cookies={'sessionid': cookie},
                             files={'file': game})
    if response.status_code != 200:
        request_failed(response)
    else:
        stdout.write('上传成功\n')
        response = requests.get(f'{url}/admin/make-compile/{game_id}/', cookies={'sessionid': cookie})
        if response.status_code != 200:
            request_failed(response)
        else:
            result = response.json()
            if 'error' in result:
                stderr.write(f'{result["error"]}\n')
            else:
                stdout.write('编译成功\n')


def subcommand_hook(parser: ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--test', nargs=2, help='测试游戏', metavar=('config_path', 'result_dir'))
    group.add_argument('-u', '--upload', help='上传游戏', metavar='config_path')


def main(args: Namespace) -> None:
    if args.test is not None:
        _test(*args.test)
    elif args.upload is not None:
        _upload(args.upload)
    else:
        raise RuntimeError(f'无法识别参数：`{args}`')
