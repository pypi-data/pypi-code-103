#
# DISCo Python interface library
# Copyright (c) 2021 Greg Van Aken
#

"""DISCo: Descriptive Interface for Self-aware Components"""

import argparse
import discolib
import os
import pathlib
import shutil
from discolib.discogen import discogen

PROJECT_DIR_NAME = 'discoproj'
PROJECT_MAIN_NAME = 'main.py'
EXAMPLES_PATH = pathlib.Path(__file__).parent / 'examples'

STUB_TYPE = 'stub'
SERIAL_TYPE = 'serial'
TCP_TYPE = 'tcp'

def _normal_setup(filename: str) -> None:
    """Normal setup: copying a file."""
    project_path = pathlib.Path(os.getcwd(), PROJECT_DIR_NAME)
    os.mkdir(project_path)
    main_path = pathlib.Path(project_path, PROJECT_MAIN_NAME)
    shutil.copyfile(pathlib.Path(EXAMPLES_PATH, filename), main_path)

def _stub() -> None:
    """A stub project."""
    _normal_setup('stub.py')

def _serial() -> None:
    """A serial-interface project."""
    _normal_setup('serial.py')

def _tcp() -> None:
    """A tcp/ip project."""
    _normal_setup('tcp.py')

INIT_MAP = {
    STUB_TYPE: _stub,
    SERIAL_TYPE: _serial,
    TCP_TYPE: _tcp
}

def get_parser() -> argparse.ArgumentParser:
    """Create a new argument parser."""
    package_name = os.path.dirname(__file__)
    parser = argparse.ArgumentParser(package_name)
    parser.add_argument('--init', type=init, action='store')
    parser.add_argument('--version', '-v', action='version', version=discolib.__version__)
    parser.add_argument('--codegen', type=str, action='store')
    return parser

def init(init_type: str) -> None:
    """Create a new stubbed out example project."""
    if not init_type:
        init_type = STUB_TYPE
    if init_type not in INIT_MAP:
        raise RuntimeError(f'{init_type}: Unknown init type, options are: {list(INIT_MAP.keys())}')
    init_func = INIT_MAP.get(init_type)
    init_func()

def codegen(language: str) -> None:
    """Generate code for a disco component using the target language"""
    if not language:
        language = discogen.LANGUAGE_C
    if language not in discogen.LANGUAGE_MAP:
        raise RuntimeError(f'{language}: Unknown language, options are: {list(discogen.LANGUAGE_MAP.keys())}')
    discogen.LANGUAGE_MAP[language]()


def main(args=None):
    """Parse args and respond"""
    parser = get_parser()
    args = parser.parse_args(args)
    if (args.codegen):
        codegen(args.codegen)


if __name__ == '__main__':
    main()
