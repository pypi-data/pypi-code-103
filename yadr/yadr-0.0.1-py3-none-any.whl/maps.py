"""
maps
~~~~

A module for handling YADN dice maps.
"""
from typing import Callable, Optional

from yadr.base import BaseLexer
from yadr.model import BaseToken, MapToken, map_symbols, Result, TokenInfo


# Lexing.
class Lexer(BaseLexer):
    def __init__(self) -> None:
        state_map: dict[BaseToken, Callable] = {
            MapToken.START: self._start,
            MapToken.END: self._start,
            MapToken.KV_DELIMITER: self._kv_delimiter,
            MapToken.MAP_CLOSE: self._map_close,
            MapToken.MAP_OPEN: self._map_open,
            MapToken.NAME_DELIMITER: self._name_delimiter,
            MapToken.NEGATIVE_SIGN: self._negative_sign,
            MapToken.NUMBER: self._number,
            MapToken.PAIR_DELIMITER: self._pair_delimiter,
            MapToken.QUALIFIER: self._qualifier,
            MapToken.QUALIFIER_END: self._qualifier_end,
            MapToken.WHITESPACE: self._whitespace,
        }
        symbol_map: dict[BaseToken, list[str]] = map_symbols
        bracket_states: dict[BaseToken, BaseToken] = {
            MapToken.NEGATIVE_SIGN: MapToken.NUMBER,
            MapToken.QUALIFIER_DELIMITER: MapToken.QUALIFIER,
        }
        bracket_ends: dict[BaseToken, BaseToken] = {
            MapToken.QUALIFIER: MapToken.QUALIFIER_END,
        }
        result_map: dict[BaseToken, Callable] = {
            MapToken.NUMBER: self._tf_number,
            MapToken.QUALIFIER: self._tf_qualifier,
        }
        no_store: list[BaseToken] = [
            MapToken.START,
            MapToken.QUALIFIER_END,
            MapToken.WHITESPACE,
        ]
        init_state: BaseToken = MapToken.START
        super().__init__(
            state_map,
            symbol_map,
            bracket_states,
            bracket_ends,
            result_map,
            no_store,
            init_state
        )

    # Result transformation rules.
    def _tf_number(self, value: str) -> int:
        return int(value)

    def _tf_qualifier(self, value: str) -> str:
        return value[1:-1]

    # Lexing rules.
    def _kv_delimiter(self, char: str) -> None:
        """Lex a key-value delimiter symbol."""
        can_follow = [
            MapToken.NEGATIVE_SIGN,
            MapToken.NUMBER,
            MapToken.QUALIFIER_DELIMITER,
            MapToken.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _map_close(self, char: str) -> None:
        """Lex a map close symbol."""
        can_follow: list[BaseToken] = []
        self._check_char(char, can_follow)

    def _map_open(self, char: str) -> None:
        """Lex a map open symbol."""
        can_follow = [
            MapToken.MAP_CLOSE,
            MapToken.QUALIFIER_DELIMITER,
            MapToken.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _name_delimiter(self, char: str) -> None:
        """Lex a name delimiter symbol."""
        can_follow = [
            MapToken.NEGATIVE_SIGN,
            MapToken.NUMBER,
            MapToken.QUALIFIER_DELIMITER,
            MapToken.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _number(self, char: str) -> None:
        """Processing a number."""
        can_follow = [
            MapToken.KV_DELIMITER,
            MapToken.MAP_CLOSE,
            MapToken.PAIR_DELIMITER,
        ]

        # Check here if the character is a digit because the checks in
        # Char are currently limited to tokens that no longer than two
        # characters. Check if the state is a number because white
        # space also ends up here, and we want white space to separate
        # numbers.
        if char.isdigit() and self.state == MapToken.NUMBER:
            self.buffer += char
        else:
            self._check_char(char, can_follow)

    def _negative_sign(self, char: str) -> None:
        """Processing a number."""
        can_follow = [
            MapToken.NUMBER,
        ]
        self._check_char(char, can_follow)

    def _pair_delimiter(self, char: str) -> None:
        """Lex a pair delimiter symbol."""
        can_follow = [
            MapToken.NEGATIVE_SIGN,
            MapToken.NUMBER,
            MapToken.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _qualifier(self, char: str) -> None:
        """Lex a qualifier."""
        self.buffer += char
        if self._is_token_start(MapToken.QUALIFIER_DELIMITER, char):
            new_state = MapToken.QUALIFIER_END
            self._change_state(new_state, char)

    def _qualifier_end(self, char: str) -> None:
        can_follow = [
            MapToken.KV_DELIMITER,
            MapToken.MAP_CLOSE,
            MapToken.NAME_DELIMITER,
            MapToken.PAIR_DELIMITER,
            MapToken.WHITESPACE,
        ]
        self._check_char(char, can_follow)

    def _start(self, char: str) -> None:
        """Initial lexer state."""
        if self.tokens:
            self.tokens = []
        can_follow = [
            MapToken.MAP_OPEN,
            MapToken.WHITESPACE,
        ]
        self._check_char(char, can_follow)


# Parsing.
class Parser:
    def __init__(self):
        self.name = ''
        self.pairs = []
        self.buffer: Optional[int] = None
        self.state = MapToken.START
        self.state_map = {
            MapToken.START: self._start,
            MapToken.END: self._start,
            MapToken.KEY: self._key,
            MapToken.NAME: self._name,
            MapToken.VALUE: self._value,
        }

    def parse(self, tokens: tuple[TokenInfo, ...]) -> tuple[str, dict]:
        """Parse YADN dice mapping tokens."""
        for token_info in tokens:
            process = self.state_map[self.state]
            process(token_info)
        return (self.name, {k: v for k, v in self.pairs})

    # Parsing rules.
    def _key(self, token_info: tuple[BaseToken, Result]) -> None:
        token, value = token_info
        if token == MapToken.NUMBER and isinstance(value, int):
            self.buffer = value
        elif token == MapToken.KV_DELIMITER:
            self.state = MapToken.VALUE
        elif token == MapToken.MAP_CLOSE:
            ...
        else:
            msg = f'KEY cannot contain {token.name}.'
            raise ValueError(msg)

    def _name(self, token_info: tuple[BaseToken, Result]) -> None:
        token, value = token_info
        if token == MapToken.QUALIFIER:
            self.name = value
        elif token == MapToken.NAME_DELIMITER:
            self.state = MapToken.KEY
        elif token == MapToken.MAP_CLOSE:
            ...
        else:
            msg = f'NAME cannot contain {token.name}.'
            raise ValueError(msg)

    def _value(self, token_info: tuple[BaseToken, Result]) -> None:
        token, value = token_info
        if (token == MapToken.QUALIFIER
                or token == MapToken.NUMBER and isinstance(value, int)):
            key = self.buffer
            pair = (key, value)
            self.pairs.append(pair)
            self.buffer = None
        elif token == MapToken.PAIR_DELIMITER:
            self.state = MapToken.KEY
        elif token == MapToken.MAP_CLOSE:
            ...
        else:
            msg = f'VALUE cannot contain {token.name}.'
            raise ValueError(msg)

    def _start(self, token_info: tuple[BaseToken, Result]) -> None:
        token, value = token_info
        if token == MapToken.MAP_OPEN:
            self.state = MapToken.NAME
        else:
            msg = f'Dice mapping cannot start with a {value}'
            raise ValueError(msg)
