#
#  Copyright (c) 2018-2019 Renesas Inc.
#  Copyright (c) 2018-2019 EPAM Systems Inc.
#

from typing import Iterable

from colorama import Fore, Style


def print_help_with_spaces(text):
    print('  ' + text)


class SignerError(Exception):
    def __init__(self, message, help_text=None):
        super().__init__(message)
        self.help_text = help_text

    def print_message(self):
        print()
        print(f'{Fore.RED}ERROR: {str(self)}{Style.RESET_ALL}')

        if not self.help_text:
            return

        if not isinstance(self.help_text, Iterable):
            print_help_with_spaces(self.help_text)

        for row in self.help_text:
            print_help_with_spaces(row)


class SignerConfigError(SignerError):
    pass


class NoAccessError(SignerError):
    pass
