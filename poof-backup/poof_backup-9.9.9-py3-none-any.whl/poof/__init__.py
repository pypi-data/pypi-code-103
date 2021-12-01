# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


import sys

import click


__VERSION__ = "9.9.9"


def _main():
    text = """
The poof project superseded the poof-backup project on 01.Dec.2021.  If you
installed poof-backup please remove it and install poof instead.  On Python-only
installations use:

    pip install -U poof

Homebrew and apt installers are not affected by the migration to the new name.


"""
    click.secho('poof version %s' % __VERSION__, fg = "bright_red")
    click.secho(text, fg = "bright_yellow")

    sys.exit(99)


if '__main__' == __name__:
    _main()

