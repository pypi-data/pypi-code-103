import getpass
import subprocess as sp

import click


def run_cmd(cmd):
    res = sp.run(cmd, shell=True, capture_output=True, encoding='utf-8')
    if res.returncode != 0:
        raise Exception(click.style(f'ERROR: {res.stderr}', fg='red'))
    return res.stdout


def check():
    user = getpass.getuser()
    cmd = f'qselect -U {user}'
    res = run_cmd(cmd)
    print(res)


if __name__ == "__main__":
    print(run_cmd('whoami'))
    # check()
