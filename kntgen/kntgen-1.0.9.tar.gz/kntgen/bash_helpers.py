import subprocess

from kntgen.printer import *

FLUTTER_FORMAT = 'flutter format .'
FLUTTER_GEN = 'flutter pub run build_runner build --delete-conflicting-outputs'
FLUTTER_GEN_LOCALE = 'flutter pub run easy_localization:generate ' \
                     '-S assets/translations -f keys -o locale_keys.g.dart'


def bash_execute(command: str, need_print=True):
    if need_print:
        info_printer(f'Running command line [{command}] ...')
    process = subprocess.Popen((command or FLUTTER_FORMAT).split(),
                               stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        print(f'Occur an error while running command line: [{error}]')
