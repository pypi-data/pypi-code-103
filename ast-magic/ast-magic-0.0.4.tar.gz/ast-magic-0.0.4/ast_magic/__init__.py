from ast import dump as dump_ast, parse as ast_parse  # Avoid conflict w/ magic
from typing import Optional

from IPython.core.magic import register_line_cell_magic


def print_ast(source: str) -> None:
    print(dump_ast(ast_parse(source), indent=4))


def load_ipython_extension(_ipython):
    @register_line_cell_magic
    def ast(line: Optional[str], cell: Optional[str] = None) -> None:
        if cell is not None:
            print_ast(cell)
            _ipython.ex(cell)
        else:
            print_ast(line)
            _ipython.ex(line)
