"""NanamiLang AST CLass"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List
from nanamilang import datatypes
from nanamilang.token import Token
from nanamilang.builtin import BuiltinFunctions
from nanamilang.shortcuts import ASSERT_IS_INSTANCE_OF
from nanamilang.shortcuts import ASSERT_COLLECTION_IS_NOT_EMPTY
from nanamilang.shortcuts import ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF


class AST:
    """
    NanamiLang AST (abstract syntax tree) Generator

    Usage:
    ```
    from nanamilang import AST, Tokenizer, datatypes
    t: Tokenizer = Tokenizer('(+ 2 2 (* 2 2))')
    tokenized = t.tokenize() # => tokenize input string
    ast: AST = AST(tokenized) # => create new AST instance
    result: datatypes.Base = ast.evaluate() # => <IntegerNumber>: 8
    ```
    """

    _wood: list
    _tokenized: List[Token]

    def __init__(self, tokenized: List[Token]) -> None:
        """Initialize a new NanamiLang AST instance"""

        ASSERT_IS_INSTANCE_OF(tokenized, list)
        ASSERT_COLLECTION_IS_NOT_EMPTY(tokenized)
        ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF(tokenized, Token)

        self._tokenized = tokenized
        self._wood = self._make_wood()

    def wood(self) -> list:
        """NanamiLang AST, self._wood getter"""

        return self._wood

    def _make_wood(self) -> list:
        """NanamiLang AST, make an actual wood of trees"""

        # Written by @buzzer13 (https://gitlab.com/buzzer13)

        # TODO: I need to better understand how it works O.O, thank you Michael

        items = []
        stack = [items]

        for token in self._tokenized:

            if token.type() == Token.ListBegin:

                wired = []
                stack[-1].append(wired)
                stack.append(wired)

            elif token.type() == Token.ListEnd:

                stack.pop()

            else:
                stack[-1].append(token)

        return [i
                if isinstance(i, list)
                else [Token(Token.Identifier, 'identity'), i] for i in items]

    def evaluate(self) -> datatypes.Base:
        """NanamiLang AST, recursively evaluate tree"""

        def recursive_evaluate(environment: dict, tree: list) -> datatypes.Base:
            identifier: (list or Token)
            rest: list
            if not tree:
                return datatypes.Nil('nil')
            identifier, *rest = tree
            arguments: list = []
            argument: (Token or list)
            if isinstance(identifier, Token):
                if isinstance(identifier.dt(), datatypes.Macro):
                    return recursive_evaluate(
                        environment,
                        identifier.dt().reference()(
                            # we need this because we can not import
                            # nanamilang.token module in
                            # nanamilang.builtin module which is
                            # responsible to handle macro
                            rest, environment, recursive_evaluate, Token
                        ))
            for part in rest:
                if isinstance(part, Token):
                    if part.type() == part.Identifier:
                        arguments.append(environment.get(part.dt().origin(), part.dt()))
                    else:
                        arguments.append(part.dt())
                elif isinstance(part, list):
                    arguments.append(recursive_evaluate(environment, part))
            if isinstance(identifier, Token):
                if identifier.type() == identifier.Identifier:
                    identifier_dt = environment.get(identifier.dt().origin(), identifier.dt())
                    # Cheating a little...
                    if not isinstance(identifier_dt, datatypes.Function):
                        ttr = BuiltinFunctions.resolve(identifier_dt.origin())
                        identifier_dt = datatypes.Function(ttr) if ttr else datatypes.Nil('nil')
                    ##############################################################################
                    return identifier_dt.reference()(arguments)\
                        if isinstance(identifier_dt, datatypes.Function) else datatypes.Nil('nil')
                return datatypes.Nil('nil')
            elif isinstance(identifier, list):
                ev = recursive_evaluate(environment, identifier)
                return ev.reference()(arguments) if isinstance(ev, datatypes.Function) else datatypes.Nil('nil')

        return list(recursive_evaluate({}, expression) or datatypes.Nil('nil') for expression in self.wood())[-1]
