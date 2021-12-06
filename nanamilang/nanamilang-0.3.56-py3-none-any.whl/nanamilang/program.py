"""NanamiLang Program Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List

from nanamilang.ast import AST
from nanamilang.datatypes import Base
from nanamilang.formatter import Formatter
from nanamilang.shortcuts import ASSERT_COLLECTION_IS_NOT_EMPTY
from nanamilang.shortcuts import ASSERT_IS_INSTANCE_OF
from nanamilang.token import Token
from nanamilang.tokenizer import Tokenizer


class Program:
    """
    NanamiLang Program

    from nanamilang import datatypes, program

    source = '(+ 2 2 (* 2 2))'
    program: program.Program = program.Program(str(source))
    program.format() # => "(+ 2 2 (* 2 2))"
    program.ast() # => get encapsulated AST instance
    program.tokenized() # => collection of a Token instances

    result: datatypes.Base = program.evaluate() # => <IntegerNumber>: 8
    """

    _ast: AST
    _source: str
    _formatter = Formatter
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
        self._formatter = Formatter(self._tokenized)

    def ast(self) -> AST:
        """NanamiLang Program, self._ast getter"""

        return self._ast

    def tokenized(self) -> List[Token]:
        """NanamiLang Program, self._tokenized getter"""

        return self._tokenized

    def format(self) -> str:
        """NanamiLang Program, call self._formatter.format() to format source"""

        return self._formatter.format()

    def evaluate(self) -> Base:
        """NanamiLang Program, call self._ast.evaluate() to evaluate your program"""

        return self._ast.evaluate()
