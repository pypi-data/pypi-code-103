#!python

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

"""NanamiLang Eval"""

import argparse
import os
import sys

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

    res = program.Program(inp).evaluate()

    # Be strict, require program to return 0 or 1, no exceptions

    if isinstance(res, datatypes.IntegerNumber):
        return res.reference()
    else:
        raise ValueError(f'Program returned non-integer result, but: {res}')

    # Return exit code to system and exit NanamiLang Evaluator script after evaluating a source


if __name__ == "__main__":
    sys.exit(main())
