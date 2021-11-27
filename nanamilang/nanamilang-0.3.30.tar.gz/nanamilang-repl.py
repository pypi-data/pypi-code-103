#!/usr/bin/env python3

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

"""NanamiLang REPL"""

import os
import sys
import atexit
import readline
import argparse
import traceback
from nanamilang.program import Program
from nanamilang.builtin import BuiltinFunctions, BuiltinMacros
from nanamilang import datatypes, stdlib, __version_string__, __author__

history_file_path = os.path.join(
    os.path.expanduser("~"), ".nanamilang_history")
try:
    readline.read_history_file(history_file_path)
    readline.set_history_length(1000)
except FileNotFoundError:
    pass

atexit.register(readline.write_history_file, history_file_path)

readline.parse_and_bind("tab: complete")


def complete(t: str, s: int):
    """NanamiLang REPL complete() function for GNU readline"""
    vocabulary = BuiltinFunctions.completions() + BuiltinMacros.completions()
    return ([name for name in vocabulary if name.startswith(t)] + [None]).__getitem__(s)


readline.set_completer(complete)


def main():
    """NanamiLang REPL Main function"""

    parser = argparse.ArgumentParser('NanamiLang REPL')
    parser.add_argument('--no-greeting',
                        help='Greeting can be disabled',
                        action='store_true', default=False)
    parser.add_argument('--dump-wood',
                        help='Dump wood each time',
                        action='store_true', default=False)
    parser.add_argument('--print-traceback',
                        help='Call traceback.print_exc()',
                        action='store_true', default=False)
    parser.add_argument('--skip-stdlib-populate',
                        help='No auto stdlib population',
                        action='store_true', default=False)
    parser.add_argument('--override-stdlib-remote-path',
                        help='Override stdlib remote path')

    args = parser.parse_args()

    p_ver = '.'.join([str(sys.version_info.major),
                      str(sys.version_info.minor),
                      str(sys.version_info.micro)])

    print('NanamiLang', __version_string__, 'by', __author__, 'on Python', p_ver)
    if not args.no_greeting:
        print('History path is:', history_file_path)
        print('Type (doc function-or-macro) to see function-or-macro sample doc')
        print('Type (exit!) or press "Control+D" / "Control+C" to exit the REPL')

    BuiltinFunctions.install(
        {
            'name': 'exit!', 'type': 'function',
            'sample': '(exit!)', 'docstring': 'Exit NanamiLang REPL'
        },
        lambda _: sys.exit(0)
    )

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

    while True:
        try:
            src = input("USER> ")
            # Skip evaluating in case of empty string
            if not src:
                continue
            try:
                p = Program(src)
                if args.dump_wood:
                    p.dump()
                res = p.evaluate()
                print(res.format())
            except Exception as e:
                if args.print_traceback:
                    traceback.print_exc()
                else:
                    print(e)
                print(datatypes.Nil('nil').format())
        except EOFError:
            print("Bye for now!")
            break
        except KeyboardInterrupt:
            print("\b\bBye for now!")
            break

    return 0

    # Return 0 to system and exit NanamiLang REPL script after playing around with NanamiLang


if __name__ == "__main__":

    main()
