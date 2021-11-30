import os
import sys
import inspect
import argparse
import mlpractice
from distutils.dir_util import copy_tree
import re


def get_source(match):
    match_object = eval(match.group()[9:-1])
    source_lines = inspect.getsourcelines(match_object)[0]
    new_lines = [line.rstrip() for line in source_lines]

    escape_symbols_re = re.compile(r'([\\"])')

    new_lines = [
        r'"{0}\n",'.format(escape_symbols_re.sub(r'\\\1', line))
        for line
        in new_lines
    ]

    new_lines[0] = new_lines[0][1:]
    new_lines[-1] = new_lines[-1][:-4]

    return ''.join(new_lines)


def inject_sources_into_template(file_path):
    """Inject python source code into the file in places marked with
    #!source<python_object>
    """
    with open(file_path, 'r') as target_file:
        file_as_text = target_file.read()

    reg_exp = re.compile(r'#!source<.+?>')
    modified_file_as_text = reg_exp.sub(get_source, file_as_text)

    with open(file_path, 'w') as target_file:
        target_file.write(modified_file_as_text)


def init():
    """Initialize a directory with tasks."""
    if os.path.isdir('tasks'):
        print('Directory "tasks" already exists!')
        sys.exit(0)

    os.mkdir('tasks')
    os.chdir('tasks')

    templates_dir = os.path.join(
        os.path.dirname(inspect.getfile(mlpractice)),
        'templates',
    )
    tasks_dir = os.getcwd()

    copy_tree(templates_dir, tasks_dir)
    for dir_path, dir_names, filenames in os.walk(tasks_dir):
        for filename in filenames:
            file_path = os.path.join(dir_path, filename)
            inject_sources_into_template(file_path)

    print(f'Initialized a directory with tasks at {tasks_dir}')


def command_line():
    """Parse the user's input and execute the specified command."""
    command_functions = [
        init,
    ]

    command_to_function = {
        func.__name__: func for func in command_functions
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command',
        metavar='<command>',
        choices=command_to_function.keys(),
        help='The command to execute from the list: {0}'.format(
            list(
                command_to_function.keys(),
            ),
        ),
    )

    args = parser.parse_args()
    command_to_function[args.command]()
