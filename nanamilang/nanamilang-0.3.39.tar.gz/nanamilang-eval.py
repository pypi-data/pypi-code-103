#!/usr/bin/env python3

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

"""NanamiLang Eval"""

import os
import argparse
from nanamilang import datatypes, program


def main():
    """NanamiLang Eval Main function"""

    parser = argparse.ArgumentParser('NanamiLang Evaluator')
    parser.add_argument('program', help='Path to source code')
    args = parser.parse_args()

    assert args.program
    assert os.path.exists(args.program)

    with open(args.program, encoding='utf-8') as r:
        inp = r.read()

    assert inp, 'A program source code could not be an empty string'

    dt = program.Program(inp).evaluate()

    # Be strict, require program to return 0 or 1, no exceptions

    if isinstance(dt, datatypes.IntegerNumber):
        return dt.reference()
    else:
        raise ValueError(f'Program returned non-integer result, but: {dt}')

    # Return exit code to system and exit NanamiLang Evaluator after evaluating a source


if __name__ == "__main__":

    main()
