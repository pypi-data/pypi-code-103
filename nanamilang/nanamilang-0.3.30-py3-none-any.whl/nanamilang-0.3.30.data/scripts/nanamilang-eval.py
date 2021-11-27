#!python

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

"""NanamiLang Eval"""

import os
import argparse
from nanamilang.program import Program
from nanamilang import datatypes, stdlib


def main():
    """NanamiLang Eval Main function"""

    parser = argparse.ArgumentParser('NanamiLang Evaluator')
    parser.add_argument('--skip-stdlib-populate',
                        help='No auto stdlib population',
                        action='store_true', default=False)
    parser.add_argument('--override-stdlib-remote-path',
                        help='Override stdlib remote path')
    parser.add_argument('--be-quiet',
                        help='Do not make a sound',
                        action='store_true', default=False)
    parser.add_argument('program', help='Path to source code')
    args = parser.parse_args()

    assert args.program

    print = globals()['__builtins__'].print \
        if not args.be_quiet \
        else lambda *_args_, **__kwargs__: None

    assert os.path.exists(args.program)

    with open(args.program, encoding='utf-8') as r:
        inp = r.read()

    assert inp, 'A program source code could not be an empty string'

    # Populate & Load NanamiLang Standard Library

    if args.skip_stdlib_populate:
        print('WARN: Automatic NanamiLang Standard Library population is turned off!')
        print('      current version could be possibly old and contain unfixed bugs!')
    else:
        print('Populating NanamiLang Standard Library ... ')
        if args.override_stdlib_remote_path:
            stdlib.stdlib_remote_path = lambda: args.override_stdlib_remote_path
        if stdlib.populate_nanamilang_stdlib():
            print('NanamiLang Standard Library was successfully populated to local.')
        else:
            print('For some reason, unable not populate NanamiLang Standard Library')

    if not os.path.exists(stdlib.ensure_stdlib_local_path()):
        print('Unable to continue cause there is no NanamiLang Standard Library')
        return 1

    with open(stdlib.ensure_stdlib_local_path(), 'r', encoding='utf-8') as the_handler:
        Program(the_handler.read()).evaluate()

    dt = Program(inp).evaluate()

    # Be strict, require program to return 0 or 1, no exceptions

    if isinstance(dt, datatypes.IntegerNumber):
        return dt.reference()
    else:
        raise ValueError(f'Program returned non-integer result, but: {dt}')

    # Return exit code to system and exit NanamiLang Evaluator after evaluating a source


if __name__ == "__main__":

    main()
