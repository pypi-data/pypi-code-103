import os


def tput(cmd):
    os.system(f'tput {cmd}')


def clear_to_end_of_line():
    tput('el')


def up_lines(lines=1):
    tput(f'cuu {lines}')


def erase_lines(lines=1):
    for _l in range(lines):
        up_lines()
        clear_to_end_of_line()
