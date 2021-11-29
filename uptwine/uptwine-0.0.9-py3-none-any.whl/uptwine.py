from typing import Optional
from typing import Sequence
import argparse
import json
import sys
import os


def echocmd(cmd: str, args) -> int:
    args = ' '.join(str(item) for item in args)
    cmd = f'{cmd} ' + args
    return os.system(cmd)

def update(package_name: str, username: str, password: str) -> int:
    #  Setup.py
    cmd = ['python', 'setup.py', 'sdist', 'bdist_wheel']
    echocmd(cmd[0], cmd[1:])

    #  Twine
    cmd = ['twine', 'check', 'dist/*']
    echocmd(cmd[0], cmd[1:])

    #  Twine Upload
    cmd = ['twine', 'upload',
    '--repository-url', 'https://upload.pypi.org/legacy/',
    '--username', username,
    '--password', password,
    'dist/*']
    echocmd(cmd[0], cmd[1:])
    
    cmd = ['twine', 'upload',
    '--repository-url', 'https://upload.pypi.org/legacy/',
    '--username', username,
    '--password', password,
    'dist/*']
    echocmd(cmd[0], cmd[1:])

    # Pip install
    cmd = ['pip', 'install',
    '-U', package_name]
    echocmd(cmd[0], cmd[1:])

    return 0

def opencfg() -> int:
    config = {}
    config.update({"username": "username"})
    config.update({"password": "password"})

    with open('configfile.json', 'w') as configjson:
        json.dump(config, configjson)
        
    if sys.platform == 'win32':
        command = 'notepad.exe configfile.json'
        os.system(command)
        return 0

def get_json_username() -> str:
    with open("configfile.json", "r") as f:
        opened = json.loads(f.read())
        username = opened["username"]
        return username

def get_json_password() -> str:
    with open("configfile.json", "r") as f:
        opened = json.loads(f.read())
        password = opened["password"]
        return password

def uptwine(argv: Optional[Sequence[str]] = None) -> int:
    """Execute the ``uptwine`` command.
    :param args:
        The command-line arguments.
    """
    parser = argparse.ArgumentParser(prog='uptwine.py')
    
    #  Optional Arguments
    parser.add_argument('-n', '--package_name', help='name of the package to upload')
    parser.add_argument('-u', '--username', help='your pypi account username')
    parser.add_argument('-p', '--password', help='your pypi account password')
    parser.add_argument('--configfile', help='use configfile as account user & pwd')
    parser.add_argument('--opencfg', help='open config file', action='store_true')

    args = parser.parse_args(argv)
    dict_args = vars(args)
    
    #  Open cfg statement
    if args.opencfg:
        opencfg()

    if args.package_name and args.username and args.password:
        update(dict_args.get("package_name"), dict_args.get("username"), dict_args.get("password"))
    elif args.package_name and args.configfile:
        update(dict_args.get("package_name"), get_json_username(), get_json_password())

    return 0


if __name__ == '__main__':
    exit(uptwine())
