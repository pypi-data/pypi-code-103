"""
This module is used for checking the project code for compliance with PEP8.

"""


import os

from pylint_af import PyLinter


if __name__ == '__main__':
    PyLinter(
        root_directory=os.path.dirname(os.path.dirname(__file__)),
        ignored_statements={'E0401', 'E0402', 'E0611'}
    ).check()
