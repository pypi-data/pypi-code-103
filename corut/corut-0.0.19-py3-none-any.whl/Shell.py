#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It is aimed to provide convenience by performing many operations on the operating system.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import sys
import traceback
from subprocess import Popen, PIPE, STDOUT, CalledProcessError, check_output


def print_error(error, *args, **kwargs):
    print("@" * 99)
    print(f"Error   >----> {error.__class__}")
    print(f"Message >----> {error}")
    print('-' * 99)
    print(f"args    >----> {args}")
    print('-' * 99)
    print(f"kwargs  >----> {kwargs}")
    print('-' * 99)
    exc_type, exc_value, exc_tb = sys.exc_info()
    for line in traceback.format_exception(exc_type, exc_value, exc_tb):
        print(line)
    print("@" * 99)


def run_cmd(command, password=None, encoding='utf-8', **kwargs):
    print(f'------------------> Command:{command}')
    try:
        with Popen(
                command,
                stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True,
                encoding=encoding, universal_newlines=True, **kwargs
        ) as process:
            if password:
                process.stdin.write(f'{password}\n')
                process.stdin.flush()
            for line in process.stdout:
                print(line, end='')
    except Exception as error:
        print('Subprocess Popen Error:', error)
    print('\n', '#' * 99, '\n')


def run_cmd_2(cmd, do_combine=False, return_binary=False, encoding='utf-8', **kwargs):
    decode_text = return_binary is False
    try:
        stdout = check_output(
            cmd,
            stderr=STDOUT,
            universal_newlines=decode_text,
            encoding=encoding,
            **kwargs
        )
    except CalledProcessError as cpe:
        stdout = cpe.output
        return_code = cpe.returncode
    else:
        return_code = 0
    if return_code != 0:
        raise Exception(f"Command failed with ({return_code}): {cmd}\n{stdout}")
    if return_binary is True or do_combine is True:
        return stdout
    return stdout.strip('\n').split('\n')


class Cmd:
    print_error = staticmethod(print_error)
    run_cmd = staticmethod(run_cmd)
    run_cmd_2 = staticmethod(run_cmd_2)
