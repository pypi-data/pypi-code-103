#!python

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
from nanamilang import datatypes, __version_string__, __author__

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
    parser.add_argument('--dump-wood',
                        help='Dump wood each time',
                        action='store_true', default=False)
    parser.add_argument('--no-greeting',
                        help='Greeting can be disabled',
                        action='store_true', default=False)
    parser.add_argument('--print-traceback',
                        help='Call traceback.print_exc()',
                        action='store_true', default=False)

    args = parser.parse_args()

    p_ver = '.'.join([str(sys.version_info.major),
                      str(sys.version_info.minor),
                      str(sys.version_info.micro)])

    print('NanamiLang', __version_string__, 'by', __author__, 'on Python', p_ver)
    if not args.no_greeting:
        print('History path is:', history_file_path)
        print('Type (doc function-or-macro) to see function-or-macro documentation')
        print('Type (exit!), (bye!), press "Control+D" or "Control+C" to exit REPL')

    for _ in ['exit!', 'bye!', 'exit', 'bye', 'quit', 'quit!']:
        BuiltinFunctions.install(
            {
                'name': _, 'type': 'function',
                'sample': '(exit!)', 'docstring': 'Exit NanamiLang REPL'
            },
            lambda _: sys.exit(0)
        )

    while True:
        try:
            src = input("USER> ")
            if src in ['exit!', 'bye!', 'exit', 'bye', 'quit', 'quit!']:
                print(f'Type ({src}) or press "Control+D" or "Control+C" to exit REPL')
                continue
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
        except (EOFError, KeyboardInterrupt):
            print("Bye for now!")
            break

    return 0

    # Return 0 to system and exit NanamiLang REPL script after playing around with NanamiLang


if __name__ == "__main__":

    main()
