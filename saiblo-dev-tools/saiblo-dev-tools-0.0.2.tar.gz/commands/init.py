import json
from argparse import ArgumentParser, Namespace
from sys import stdout

import templates.config
import templates.database
from utils.config import CONFIG, DATABASE, DIR
from utils.path import make_dir


def _init() -> None:
    make_dir(DIR)
    json.dump(templates.config.JSON, open(CONFIG, 'w', encoding='utf-8'))
    json.dump(templates.database.JSON, open(DATABASE, 'w', encoding='utf-8'))
    stdout.write(f'初始化完成，请修改 `{CONFIG}` 中的内容完成配置\n')


def subcommand_hook(parser: ArgumentParser) -> None:
    return


def main(args: Namespace) -> None:
    _init()
