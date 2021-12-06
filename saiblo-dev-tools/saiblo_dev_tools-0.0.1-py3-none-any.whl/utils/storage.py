import json
import os.path

from utils.config import CONFIG, COOKIE, DATABASE
from utils.path import open_file


def read_db() -> dict:
    return json.load(open_file(DATABASE, encoding='utf-8'))


def write_db(db: dict) -> None:
    json.dump(db, open(DATABASE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def read_config() -> dict:
    config = json.load(open_file(CONFIG, encoding='utf-8'))
    if 'url' not in config:
        raise RuntimeError('配置文件缺少 `url: string`')
    return config


def read_cookie() -> str:
    if not os.path.exists(COOKIE):
        raise RuntimeError('请先登录')
    if not os.path.isfile(COOKIE):
        raise RuntimeError(f'路径 {COOKIE} 已存在，但不是文件')
    return open(COOKIE, encoding='utf-8').read()
