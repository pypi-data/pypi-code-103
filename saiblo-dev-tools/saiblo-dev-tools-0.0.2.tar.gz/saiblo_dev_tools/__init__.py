import os.path
import sys
from argparse import ArgumentParser, Namespace

from commands import ai, game, init, login, logout
from utils.config import DIR
from utils.error import exception_handler

parser = ArgumentParser(prog='saiblo-dev-tools', description='Saiblo 开发人员脚本工具')
command = parser.add_subparsers(title='command', description='子命令', dest='command', required=True,
                                help='在每个命令下查看具体帮助信息')
ai.subcommand_hook(command.add_parser('ai', help='AI 管理脚本'))
game.subcommand_hook(command.add_parser('game', help='游戏管理脚本'))
init.subcommand_hook(command.add_parser('init', help='初始化脚本配置文件'))
login.subcommand_hook(command.add_parser('login', help='登录'))
logout.subcommand_hook(command.add_parser('logout', help='注销'))


def check_config() -> None:
    if not os.path.exists(DIR):
        raise RuntimeError(f'目录 `{DIR}` 不存在，请先初始化脚本配置')
    if not os.path.isdir(DIR):
        raise RuntimeError(f'路径 `{DIR}` 已存在，但不是目录')


def main(args: Namespace) -> None:
    if 'command' not in args:
        raise RuntimeError(f'无法识别参数：`{args}`')
    if args.command == 'init':
        init.main(args)
    else:
        check_config()
        if args.command == 'ai':
            ai.main(args)
        elif args.command == 'game':
            game.main(args)
        elif args.command == 'login':
            login.main(args)
        elif args.command == 'logout':
            logout.main(args)
        else:
            raise RuntimeError(f'无法识别参数：`{args}`')


def entry_point():
    try:
        main(parser.parse_args(sys.argv[1:]))
    except Exception as exception:
        exception_handler(exception)
