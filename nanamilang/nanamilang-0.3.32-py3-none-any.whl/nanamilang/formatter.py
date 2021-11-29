"""NanamiLang Formatter Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List
from nanamilang import datatypes
from nanamilang.token import Token
from nanamilang.shortcuts import ASSERT_IS_INSTANCE_OF
from nanamilang.shortcuts import ASSERT_COLLECTION_IS_NOT_EMPTY
from nanamilang.shortcuts import ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF


class Formatter:
    """NanamiLang Formatter"""

    _tokenized: List[Token] = None

    def __init__(self, tokenized: List[Token]) -> None:
        """
        Initialize a new NanamiLang Formatter instance

        :param tokenized: a Token instances collection
        """

        ASSERT_IS_INSTANCE_OF(tokenized, list)
        ASSERT_COLLECTION_IS_NOT_EMPTY(tokenized)
        ASSERT_EVERY_COLLECTION_ITEM_IS_INSTANCE_OF(tokenized, Token)

        self._tokenized = tokenized

    def format(self) -> str:
        """NanamiLang Formatter, format tokens as it could be a source code line"""

        def space(idx: int, token: Token) -> str:
            if idx > 0:
                if (token.type() in Token.meta_types
                    and self._tokenized[idx-1].type() in Token.meta_types) or \
                        (token.type() is Token.ListBegin
                         and self._tokenized[idx-1].type() in Token.meta_types) or \
                        (token.type() == Token.ListBegin
                         and self._tokenized[idx-1].type() == Token.ListEnd) or \
                        (token.type() in Token.meta_types
                         and self._tokenized[idx-1].type() == Token.ListEnd):
                    return' '
            return ''

        def symbol(idx: int, token: Token) -> str:
            if token.type() in [Token.ListBegin, Token.ListEnd]:
                return {Token.ListBegin: '(', Token.ListEnd: ')'}.get(token.type())
            elif token.type() in Token.meta_types:
                if isinstance(token.dt(), datatypes.Undefined):
                    return token.dt().origin()
                return token.dt().format()
            else:
                return ''

        return ''.join([f'{space(idx, token)}{symbol(idx, token)}' for idx, token in enumerate(self._tokenized)])
