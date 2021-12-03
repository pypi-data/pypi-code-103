from ast import dump as dump_ast, parse as ast_parse  # Avoid conflict w/ magic
from typing import Optional

from IPython.core.magic import register_line_cell_magic


def print_ast(source: str) -> None:
    print(dump_ast(ast_parse(source), indent=4))


@register_line_cell_magic
def ast(line: Optional[str], cell: Optional[str]) -> None:
    if cell is not None:
        print_ast(cell)
    else:
        print_ast(line)


__all__ = ['ast']
