# -*- coding: utf-8 -*-
"""Checker of PEP-8 Class Constant Naming Conventions."""
import ast

__version__ = '0.1.2'


class ConstantNameChecker(ast.NodeVisitor):
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.issues = []

    def _ccn_101(self, t_id: str, lineno: int, col_offset: int) -> None:
        msg = "CCN101 Class constants must be uppercase {}".format(t_id)
        self.issues.append((lineno,
                            col_offset,
                            msg))
 
    def visit_ClassDef(self, node) -> None:  # noqa: N802
        for n in ast.walk(node):
            if isinstance(n, ast.FunctionDef):
                return

            if isinstance(n, ast.AnnAssign):
                if not n.target.id.isupper():
                    self._ccn_101(n.target.id, n.lineno, n.col_offset)

            if isinstance(n, ast.Assign):
                for target in n.targets:
                    if not target.id.isupper():
                        self._ccn_101(target.id, n.lineno, n.col_offset)
 

class ConstantChecker(object):
    name = 'flake8_class_constants'  # noqa: CCN101
    options = None  # noqa: CCN101
    version = __version__  # noqa: CCN101

    def __init__(self, tree, filename: str):
        print(type(tree))
        self.tree = tree
        self.filename = filename

    def run(self):
        parser = ConstantNameChecker()
        parser.visit(self.tree)

        for lineno, column, msg in parser.issues:
            yield (lineno, column, msg, ConstantChecker)
