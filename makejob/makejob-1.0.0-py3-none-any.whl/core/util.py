import getpass
import subprocess as sp

import click


def run_cmd(cmd):
    res = sp.run(cmd, shell=True, capture_output=True, encoding='utf-8')
    if res.returncode != 0:
        raise Exception(click.style(f'ERROR: {res.stderr}', fg='red'))
    return res.stdout


def check_queues():
    user = getpass.getuser()
    cmd = f'qselect -U {user}'
    queues = run_cmd(cmd).strip().split()
    queues = set(q.split('@')[0] for q in queues)
    return queues


if __name__ == "__main__":
    queues = check_queues()
    print(queues)
