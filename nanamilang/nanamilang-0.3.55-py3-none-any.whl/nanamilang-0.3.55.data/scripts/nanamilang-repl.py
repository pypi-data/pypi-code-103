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
from nanamilang import program, __version_string__, __author__
from nanamilang.builtin import BuiltinFunctions, BuiltinMacros

history_file_path = os.path.join(
    os.path.expanduser("~"), ".nanamilang_history")
try:
    readline.set_history_length(1000)
    readline.read_history_file(history_file_path)
except FileNotFoundError:
    pass

atexit.register(readline.write_history_file, history_file_path)

readline.parse_and_bind("tab: complete")
readline.parse_and_bind('set blink-matching-paren on')

repl_exit_function_names: list = ['exit!', 'bye!', 'exit', 'bye', 'quit', 'quit!']
builtin_names = BuiltinFunctions.names() + BuiltinMacros.names() + repl_exit_function_names


def complete(t: str, s: int):
    """NanamiLang REPL complete() function for GNU readline"""
    return ([name for name in builtin_names if name.startswith(t)] + [None]).__getitem__(s)


readline.set_completer(complete)


def check_whether_user_wants_to_exit(p: program.Program) -> None:
    """
    1. p.tokenized() contains only ONE token:
    2. that token is a type() of Token.Identifier
    3. that token dt().origin() equals to something from 'valid'

    :param p: current program instance initialized after user input
    """

    if len(p.tokenized()) == 1:
        first = p.tokenized()[0]
        if first.type() == 'Identifier':
            if first.dt().origin() in repl_exit_function_names:
                name = first.dt().origin()
                print(f'Type ({name}) or press "Control+D" or "Control+C" to exit REPL')


def main():
    """NanamiLang REPL Main function"""

    parser = argparse.ArgumentParser('NanamiLang REPL')
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

    for _ in repl_exit_function_names:
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
            # Skip program evaluation in case of empty input
            if not src:
                continue
            p = program.Program(src)
            # Show tips in case user wants to exit NanamiLang REPL script
            check_whether_user_wants_to_exit(p)
            try:
                print(p.evaluate().format())
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
