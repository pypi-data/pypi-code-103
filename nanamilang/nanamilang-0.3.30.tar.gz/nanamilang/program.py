"""NanamiLang Program Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List
from nanamilang.ast import AST
from nanamilang.token import Token
from nanamilang.datatypes import Base
from nanamilang.tokenizer import Tokenizer
from nanamilang.formatter import Formatter
from nanamilang.shortcuts import ASSERT_IS_INSTANCE_OF
from nanamilang.shortcuts import ASSERT_COLLECTION_IS_NOT_EMPTY


class Program:
    """
    NanamiLang Program

    from nanamilang import datatypes, Program

    source = '(+ 2 2 (* 2 2))'
    program: Program = Program(str(source))
    program.format() # => "(+ 2 2 (* 2 2))"
    program.ast() # => get encapsulated AST instance
    program.tokenized() # => collection of a Token instances

    result: datatypes.Base = program.evaluate() # => <IntegerNumber>: 8
    """

    _ast: AST
    _source: str
    _tokenized: List[Token]

    def __init__(self, source: str) -> None:
        """
        Initialize a new NanamiLang Program instance

        :param source: your NanamiLang program source code
        """

        ASSERT_IS_INSTANCE_OF(source, str)
        ASSERT_COLLECTION_IS_NOT_EMPTY(source)

        self._source = source
        self._tokenized = Tokenizer(self._source).tokenize()
        self._ast = AST(self._tokenized)

    def dump(self) -> None:
        """NanamiLang Program, dump program AST"""

        def recursive(t, indent=1):
            for tof in t:
                if isinstance(tof, list):
                    recursive(tof, indent + 4)
                else:
                    print(f'{indent * " "}{tof} ({tof.dt()})')

        for tree in self.ast().wood():
            recursive(tree)

    def ast(self) -> AST:
        """NanamiLang Program, self._ast getter"""

        return self._ast

    def tokenized(self) -> List[Token]:
        """NanamiLang Program, self._tokenized getter"""

        return self._tokenized

    def format(self) -> str:
        """NanamiLang Program, call Formatter(self._tokenized).format()"""

        return Formatter(self._tokenized).format()

    def evaluate(self) -> Base:
        """NanamiLang Program, call self._ast.evaluate() to evaluate your program"""

        return self._ast.evaluate()
