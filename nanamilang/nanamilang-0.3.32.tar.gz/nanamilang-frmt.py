#!/usr/bin/env python3

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

"""NanamiLang Format"""

import os
import argparse
from nanamilang.program import Program


def main():
    """NanamiLang Format Main function"""

    parser = argparse.ArgumentParser('NanamiLang Formatter')
    parser.add_argument('program', help='Path to source code')
    args = parser.parse_args()

    assert args.program
    assert os.path.exists(args.program)

    with open(args.program, encoding='utf-8') as r:
        inp = r.read()

    assert inp, 'A program source code could not be an empty string'

    print(Program(inp).format(), end='')

    return 0

    # Return 0 to system and exit NanamiLang Formatter script after formatting


if __name__ == "__main__":

    main()
