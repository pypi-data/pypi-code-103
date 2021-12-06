import ast
from pathlib import Path
from typing import List, Tuple


def find_func_lines(node: ast.FunctionDef):
    return node.lineno - 1, find_max_func_line(node)


def find_max_func_line(node: ast.FunctionDef):
    max_line = node.lineno

    if hasattr(node, "body"):
        for child in node.body:
            child_max = find_max_func_line(child)
            max_line = max(max_line, child_max)

    if isinstance(node, ast.If):
        for child in node.orelse:
            child_max = find_max_func_line(child)
            max_line = max(max_line, child_max)

    return max_line


def get_specific_python_function(function_name: str, file, max_length: int = 100):
    with open(file, "r") as source:
        tree = ast.parse(source.read())

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue

        if node.name == function_name:
            func_start, func_end = find_func_lines(node)
            return _read_python_func(file, func_start, func_end + 1, max_length)


def get_func_lines(file):
    with open(file, "r") as source:
        tree = ast.parse(source.read())

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            yield find_func_lines(node)


def get_funcs_as_string(
    file, min_length: int = 6, max_length: int = 100, include_docstring: bool = False
):
    for (func_start, func_end) in get_func_lines(file):
        if func_end - func_start >= min_length:
            func_string = _read_python_func(file, func_start, func_end, max_length)

            if not include_docstring:
                func_string = _remove_docstring(func_string)

            yield func_string


def _remove_docstring(func_string):
    """
    Remove docstring from a function call.

    Notes
    -----
    * Naively searches for triple quotes
    """
    split_func = func_string.split('"""')

    # TODO: Will incorrectly parse code if triple quotes present in code body
    if len(split_func) >= 3:
        split_func[0] = (
            split_func[0].rstrip() + "\n"
        )  # rstrip also removes \n. TODO: use raw strings to avoid this
        split_func[2] = split_func[2].lstrip("\n")

        del split_func[1]

    return "".join(split_func)


def _read_python_func(
    file: Path, min_line: int, max_line: int, max_line_difference: int
) -> str:
    """
    Read a subset of lines in a Python function.

    Parameters
    ----------
    min_line : int
        The starting line number (inclusive) which to read
    max_line : int
        The end line number (inclusive) which to read
    file : pathlib.Path
        The file to read
    max_line_different : int
        Maximum amount of lines to read. Overrides `max_line`.

    Returns
    -------
    str
        Subset of lines from the given file
    """
    with open(file, "r") as source:
        code = source.readlines()

    max_line = min(max_line, min_line + max_line_difference)

    return "".join(code[min_line : max_line + 1])
