"""
model
~~~~~

Common data elements for the yadr package.
"""
from collections import UserString
from enum import Enum, EnumMeta, auto
from typing import Generic, NamedTuple, Sequence, Union, Tuple, TypeVar


# YADN Tokens.
class Token(Enum):
    START = auto()
    END = auto()
    AS_OPERATOR = auto()
    BOOLEAN = auto()
    CHOICE_OPERATOR = auto()
    CHOICE_OPTIONS = auto()
    COMPARISON_OPERATOR = auto()
    DICE_OPERATOR = auto()
    EX_OPERATOR = auto()
    GROUP_OPEN = auto()
    GROUP_CLOSE = auto()
    MAP = auto()
    MAP_CLOSE = auto()
    MAP_END = auto()
    MAP_OPEN = auto()
    MAPPING_OPERATOR = auto()
    MD_OPERATOR = auto()
    MEMBER = auto()
    MEMBER_DELIMITER = auto()
    NEGATIVE_SIGN = auto()
    NUMBER = auto()
    OPERATOR = auto()
    OPTIONS_OPERATOR = auto()
    POOL = auto()
    POOL_CLOSE = auto()
    POOL_DEGEN_OPERATOR = auto()
    POOL_END = auto()
    POOL_GEN_OPERATOR = auto()
    POOL_OPEN = auto()
    POOL_OPERATOR = auto()
    QUALIFIER = auto()
    QUALIFIER_END = auto()
    QUALIFIER_DELIMITER = auto()
    ROLL_DELIMITER = auto()
    U_POOL_DEGEN_OPERATOR = auto()
    WHITESPACE = auto()


op_tokens = (
    Token.CHOICE_OPERATOR,
    Token.COMPARISON_OPERATOR,
    Token.DICE_OPERATOR,
    Token.POOL_GEN_OPERATOR,
    Token.POOL_DEGEN_OPERATOR,
    Token.POOL_OPERATOR,
    Token.U_POOL_DEGEN_OPERATOR,
    Token.OPTIONS_OPERATOR,
    Token.OPERATOR,
    Token.AS_OPERATOR,
    Token.MD_OPERATOR,
    Token.EX_OPERATOR,
    Token.MAPPING_OPERATOR,
)

id_tokens = (
    Token.BOOLEAN,
    Token.NUMBER,
    Token.POOL,
    Token.QUALIFIER,
)

# Symbols for YADN tokens.
# This maps the symbols used in YADN to tokens for lexing. This isn't
# a direct mapping from the YADN specification document. It's just
# the basic things that can be handled by the lexer easily. More
# complicated things are handled through the lexer itself.
yadn_symbols_raw = {
    Token.START: '',
    Token.AS_OPERATOR: '+ -',
    Token.BOOLEAN: 'T F',
    Token.CHOICE_OPERATOR: '?',
    Token.CHOICE_OPTIONS: '',
    Token.COMPARISON_OPERATOR: '< > >= <= != ==',
    Token.DICE_OPERATOR: 'd d! dc dh dl dw',
    Token.EX_OPERATOR: '^',
    Token.GROUP_OPEN: '(',
    Token.GROUP_CLOSE: ')',
    Token.MAP: '',
    Token.MAP_CLOSE: '}',
    Token.MAP_END: '',
    Token.MAP_OPEN: '{',
    Token.MAPPING_OPERATOR: 'm',
    Token.MD_OPERATOR: '* / %',
    Token.MEMBER_DELIMITER: ',',
    Token.NEGATIVE_SIGN: '-',
    Token.NUMBER: '0 1 2 3 4 5 6 7 8 9',
    Token.OPTIONS_OPERATOR: ':',
    Token.POOL_CLOSE: ']',
    Token.POOL: '',
    Token.POOL_END: '',
    Token.POOL_OPEN: '[',
    Token.POOL_DEGEN_OPERATOR: 'nb ns',
    Token.POOL_GEN_OPERATOR: 'g g!',
    Token.POOL_OPERATOR: 'pa pb pc pf ph pl pr p%',
    Token.QUALIFIER: '',
    Token.QUALIFIER_DELIMITER: '"',
    Token.QUALIFIER_END: '',
    Token.ROLL_DELIMITER: ';',
    Token.U_POOL_DEGEN_OPERATOR: 'C N S',
    Token.WHITESPACE: '',
}


# YADN dice mapping tokens.
# These are the YADN tokens that are specific to dice maps. These are
# split out so they won't confuse the main YADN lexer. Dice maps are
# parsed by their own lexer.
class MapToken(Enum):
    START = auto()
    END = auto()
    KEY = auto()
    KV_DELIMITER = auto()
    MAP_CLOSE = auto()
    MAP_OPEN = auto()
    NAME = auto()
    NAME_DELIMITER = auto()
    NEGATIVE_SIGN = auto()
    NUMBER = auto()
    PAIR_DELIMITER = auto()
    QUALIFIER = auto()
    QUALIFIER_DELIMITER = auto()
    QUALIFIER_END = auto()
    VALUE = auto()
    WHITESPACE = auto()


# Symbols for YADN dice mapping tokens.
map_symbols_raw = {
    MapToken.START: '',
    MapToken.END: '',
    MapToken.KEY: '',
    MapToken.KV_DELIMITER: ':',
    MapToken.MAP_CLOSE: '}',
    MapToken.MAP_OPEN: '{',
    MapToken.NAME: '',
    MapToken.NAME_DELIMITER: '=',
    MapToken.NEGATIVE_SIGN: '-',
    MapToken.NUMBER: '0 1 2 3 4 5 6 7 8 9',
    MapToken.PAIR_DELIMITER: ',',
    MapToken.QUALIFIER: '',
    MapToken.QUALIFIER_DELIMITER: '"',
    MapToken.QUALIFIER_END: '',
    MapToken.VALUE: '',
    MapToken.WHITESPACE: '',
}


# Classes.
class CompoundResult(Tuple):
    """The result of multiple rolls."""


# Types.
BaseToken = Union[Token, MapToken]
Result = Union[int, bool, str, Tuple[int], Tuple[str], dict, None]
TokenInfo = tuple[BaseToken, Union[Result, CompoundResult]]


# Symbols by token.
def split_symbols(d: dict, enum: EnumMeta) -> dict[BaseToken, list[str]]:
    """Split the symbol strings and add whitespace."""
    split_symbols = {k: v.split() for k, v in d.items()}
    for member in enum:                                 # type: ignore
        if member.name == 'WHITESPACE':
            split_symbols[member] = [' ', '\t', '\n']
            break
    return split_symbols


symbols = split_symbols(yadn_symbols_raw, Token)
map_symbols = split_symbols(map_symbols_raw, MapToken)
