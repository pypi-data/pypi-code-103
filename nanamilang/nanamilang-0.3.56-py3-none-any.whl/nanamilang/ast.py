"""NanamiLang AST CLass"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List

from nanamilang import datatypes
from nanamilang.shortcuts import ASSERT_COLLECTION_IS_NOT_EMPTY
from nanamilang.shortcuts import ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF
from nanamilang.shortcuts import ASSERT_IS_INSTANCE_OF
from nanamilang.token import Token


class ASTEvalIsNotAFunctionDataType(Exception):
    """
    NanamiLang AST Eval Error
    Is not a function data type
    """

    _identifier: str = None

    def __init__(self, identifier, *args):
        """NanamiLang ASTEvalIsNotAFunctionDataType"""

        self._identifier = identifier

        super(ASTEvalIsNotAFunctionDataType).__init__(*args)

    def __str__(self):
        """NanamiLang ASTEvalIsNotAFunctionDataType"""

        return f'"{self._identifier}" is not a function data type'


class ASTEvalNotFoundInThisContentError(Exception):
    """
    NanamiLang AST Eval Error
    Not found in this content error
    """

    _identifier: str = None

    def __init__(self, identifier, *args):
        """NanamiLang ASTEvalNotFoundInThisContentError"""

        self._identifier = identifier

        super(ASTEvalNotFoundInThisContentError).__init__(*args)

    def __str__(self):
        """NanamiLang ASTEvalNotFoundInThisContentError"""

        return f'"{self._identifier}" was not found in this context'


class AST:
    """
    NanamiLang AST (abstract syntax tree) Generator

    Usage:
    ```
    from nanamilang import ast, tokenizer, datatypes
    t: tokenizer.Tokenizer = tokenizer.Tokenizer('(+ 2 2 (* 2 2))')
    tokenized = t.tokenize() # => tokenize input string
    ast: ast.AST = ast.AST(tokenized) # => create new AST instance
    result: datatypes.Base = ast.evaluate() # => <IntegerNumber>: 8
    ```
    """

    _wood: List[List[Token] or Token] = None
    _tokenized: List[List[Token] or Token] = None

    def __init__(self, tokenized: List[Token]) -> None:
        """
        Initialize a new NanamiLang AST instance

        :param tokenized: collection of Token instances
        """

        ASSERT_IS_INSTANCE_OF(tokenized, list)
        ASSERT_COLLECTION_IS_NOT_EMPTY(tokenized)
        ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF(tokenized, Token)

        self._tokenized = tokenized
        self._wood = self._make_wood()

    def _make_wood(self) -> list:
        """NanamiLang AST, make an actual wood of trees"""

        # Initially was written by @buzzer13 (https://gitlab.com/buzzer13)

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
        """NanamiLang AST, recursively evaluate wood"""

        def recursive(environment: dict, tree: List[Token]) -> datatypes.Base:
            identifier: List[Token] or Token
            rest: List[Token or List[Token]]
            if not tree:
                return datatypes.Nil('nil')
            identifier, *rest = tree
            argument: Token or List[Token]
            arguments: List[datatypes.Base] = []
            if isinstance(identifier, Token):
                if isinstance(identifier.dt(), datatypes.Macro):
                    return recursive(
                        environment,
                        identifier.dt().reference()(rest, environment, recursive, Token))
            for part in rest:
                if isinstance(part, Token):
                    if part.type() == part.Identifier:
                        m_known = part.dt()
                        if isinstance(part.dt(), datatypes.Undefined):
                            m_known = environment.get(part.dt().origin())
                            if not m_known:
                                raise ASTEvalNotFoundInThisContentError(part.dt().origin())
                        arguments.append(m_known)
                    else:
                        arguments.append(part.dt())
                elif isinstance(part, list):
                    arguments.append(recursive(environment, part))
            if isinstance(identifier, Token):
                if identifier.type() == identifier.Identifier:
                    m_known_dt = identifier.dt()
                    if isinstance(identifier.dt(), datatypes.Undefined):
                        m_known_dt = environment.get(identifier.dt().origin())
                        if not m_known_dt:
                            raise ASTEvalNotFoundInThisContentError(identifier.dt().origin())
                    if isinstance(m_known_dt, datatypes.Function):
                        return m_known_dt.reference()(arguments)
                    raise ASTEvalNotFoundInThisContentError(identifier.dt().origin())
                raise ASTEvalIsNotAFunctionDataType(identifier.dt().format())
            elif isinstance(identifier, list):
                ev = recursive(environment, identifier)
                return ev.reference()(arguments) \
                    if isinstance(ev, datatypes.Function) else datatypes.Nil('nil')

        return list(recursive({}, expression) or datatypes.Nil('nil') for expression in self._wood)[-1]
