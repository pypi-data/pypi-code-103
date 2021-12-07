try:
    from polidoro_terminal import Format, erase_lines, up_lines
except ModuleNotFoundError as error:
    if error.name != 'polidoro_terminal':
        raise

    class Format:
        @staticmethod
        def remove_format(txt):
            return txt

    def erase_lines(_value):
        pass

    def up_lines(_value):
        pass

from polidoro_table.table import Table
from polidoro_table.property import Property


NAME = 'polidoro_table'
VERSION = '1.1.0'

__all__ = ['Table', 'Property']
