# pyright: reportUndefinedVariable=false
import re
from decimal import Decimal

import simplejson as json
from boto3.dynamodb.types import Binary
from sly import Parser
from sly.yacc import YaccProduction

from ..exceptions import KeywordError, SyntaxError
from . import Condition
from .lexer import ExpressionLexer


class ExpressionParser(Parser):

    _expression_cache = {}

    # Get the token list from the lexer (required)
    tokens = ExpressionLexer.tokens

    # Define precendence
    precedence = (
        ("left", OR),  # noqa: 821
        ("left", AND),  # noqa: 821
        ("right", NOT),  # noqa: 821
        ("nonassoc", EQ, NE, GT, LT, LTE, GTE),  # noqa: 821
    )

    @staticmethod
    def __strip_quotes(val: str) -> str:
        return val[1:-1]

    def parse(self, expression: str) -> Condition:
        if expression not in self._expression_cache:
            self._expression_cache[expression] = super().parse(
                ExpressionLexer().tokenize(expression)
            )
        return self._expression_cache[expression]

    # Grammar rules and actions
    @_("operand EQ operand")  # noqa: 821
    def condition(self, p):
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) == operand1(m)

    @_("operand NE operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) != operand1(m)

    @_("operand GT operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) > operand1(m)

    @_("operand GTE operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) >= operand1(m)

    @_("operand LT operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) < operand1(m)

    @_("operand LTE operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) <= operand1(m)

    @_("operand BETWEEN operand AND operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        operand2 = p.operand2
        return lambda m: operand1(m) <= operand0(m) <= operand2(m)

    @_('operand IN "(" in_list ")"')  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand = p.operand
        in_list = p.in_list
        return lambda m: operand(m) in in_list(m)

    @_("function")  # noqa: 821
    def condition(self, p):  # noqa: 811
        function = p.function
        return lambda m: function(m)

    @_("condition AND condition")  # noqa: 821
    def condition(self, p):  # noqa: 811
        condition0 = p.condition0
        condition1 = p.condition1
        return lambda m: condition0(m) and condition1(m)

    @_("condition OR condition")  # noqa: 821
    def condition(self, p):  # noqa: 811
        condition0 = p.condition0
        condition1 = p.condition1
        return lambda m: condition0(m) or condition1(m)

    @_("NOT condition")  # noqa: 821
    def condition(self, p):  # noqa: 811
        condition = p.condition
        return lambda m: not condition(m)

    @_("NOT path")  # noqa: 821
    def condition(self, p):  # noqa: 811
        return lambda m: not p.path(m)

    @_('"(" condition ")"')  # noqa: 821
    def condition(self, p):  # noqa: 811
        condition = p.condition
        return lambda m: condition(m)

    @_('ATTRIBUTE_EXISTS "(" path ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path
        return lambda m: path(m) is not None

    @_('ATTRIBUTE_NOT_EXISTS "(" path ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path
        return lambda m: path(m) is None

    @_('ATTRIBUTE_TYPE "(" path "," operand ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path
        operand = p.operand
        return lambda x: path, operand

    @_('BEGINS_WITH "(" path "," operand ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path
        operand = p.operand
        return (
            lambda m: path(m).startswith(operand(m))
            if isinstance(path(m), str)
            else False
        )

    @_('CONTAINS "(" path "," operand ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path
        operand = p.operand
        return (
            lambda m: operand(m) in path(m)
            if isinstance(path(m), (str, set))
            else False
        )

    @_('SIZE "(" path ")"')  # noqa: 821
    def operand(self, p):  # noqa: 811
        path = p.path
        return (
            lambda m: len(path(m))
            if isinstance(path(m), (str, set, dict, bytearray, bytes, list))
            else -1
        )

    @_('in_list "," operand')  # noqa: 821
    def in_list(self, p):  # noqa: 811
        in_list = p.in_list
        operand = p.operand
        return lambda m: [*in_list(m), operand(m)]

    @_('operand "," operand')  # noqa: 821
    def in_list(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: [operand0(m), operand1(m)]

    @_("path")  # noqa: 821
    def operand(self, p):  # noqa: 811
        return p.path

    @_("VALUE")  # noqa: 821
    def operand(self, p):  # noqa: 811
        VALUE = p.VALUE
        if VALUE.startswith("'"):
            VALUE = VALUE.replace(r"\'", "'")
        else:
            VALUE = VALUE.replace(r"\"", '"')

        return lambda m: self.__strip_quotes(VALUE)

    @_("operand MATCH operand")  # noqa: 821
    def condition(self, f):  # noqa: 811
        regex = f.operand1
        str_to_match = f.operand0
        return lambda x: bool(re.match(regex(x), str_to_match(x)))

    @_('path "." NAME')  # noqa: 821
    def path(self, p):  # noqa: 811
        path = p.path
        NAME = p.NAME
        return lambda m: path(m).get(NAME) if isinstance(path(m), dict) else None

    @_('path "[" VALUE "]"')  # noqa: 821
    def path(self, p):  # noqa: 811
        key = self.__strip_quotes(p.VALUE)
        path = p.path

        return lambda m: path(m).get(key) if isinstance(path(m), dict) else None

    @_('path "[" INT "]"')  # noqa: 821
    def path(self, p):  # noqa: 811
        path = p.path
        INT = int(p.INT)
        return (
            lambda m: path(m)[INT]
            if isinstance(path(m), list) and len(path(m)) >= INT
            else None
        )

    @_("INT")  # noqa: 821
    def operand(self, o):  # noqa: 811
        INT = int(o.INT)
        return lambda m: INT

    @_("TRUE")  # noqa: 821
    def operand(self, o):  # noqa: 811
        return lambda m: True

    @_("FALSE")  # noqa: 821
    def operand(self, o):  # noqa: 811
        return lambda m: False

    @_("FLOAT")  # noqa: 821
    def path(self, p):  # noqa: 811
        FLOAT = float(p.FLOAT)
        return lambda m: FLOAT

    @_("KEYS")  # noqa: 821
    def path(self, _):  # noqa: 811
        return lambda m: m.keys

    @_("NEW_IMAGE")  # noqa: 821
    def path(self, _):  # noqa: 811
        return lambda m: m.new_image

    @_("OLD_IMAGE")  # noqa: 821
    def path(self, _):  # noqa: 811
        return lambda m: m.old_image

    @_("NAME")  # noqa: 821
    def path(self, p):  # noqa: 811
        NAME = p.NAME
        if isinstance(p, YaccProduction):
            raise KeywordError(f"Unknown keyword {p.NAME}")
        return lambda m: m.get(NAME) if p(m) is not None else None

    @_('FROM_JSON "(" path ")" ')  # noqa: 821
    def function(self, p):  # noqa: 811
        return lambda m: json.loads(p.path(m))

    @_('CHANGED "(" in_list ")"')  # noqa: 821
    @_('CHANGED "(" VALUE ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        # 1. Key is not in both dicts
        # 2. Key is in one and not the other
        # 3. Key is in both but the items differ
        if hasattr(p, "in_list"):
            key_list = p.in_list(p)
        else:
            key_list = [self.__strip_quotes(p.VALUE)]

        def has_changed(record, keys=key_list):
            for k in keys:
                if (
                    (
                        k not in record.old_image
                        and k in record.new_image
                    )
                    or (
                        k not in record.old_image
                        and k in record.new_image
                    )
                    or (
                        k in record.new_image
                        and k in record.old_image
                        and record.old_image[k] != record.new_image[k]
                    )
                ):
                    return True

            return False

        return has_changed

    @_('IS_TYPE "(" path "," NAME ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path

        TYPE_MAP = {
            "B": lambda m: isinstance(path(m), Binary),
            "BOOL": lambda m: isinstance(path(m), bool),
            "BS": lambda m: isinstance(path(m), set)
            and [x for x in path(m) if isinstance(x, bytes)],
            "L": lambda m: isinstance(path(m), list),
            "M": lambda m: isinstance(path(m), dict),
            "N": lambda m: isinstance(path(m), Decimal),
            "NS": lambda m: isinstance(path(m), set)
            and [x for x in path(m) if isinstance(x, Decimal)],
            "NULL": lambda m: path(m) is None,
            "S": lambda m: isinstance(path(m), str),
            "SS": lambda m: isinstance(path(m), set)
            and [x for x in path(m) if isinstance(x, str)],
        }

        if p.NAME not in TYPE_MAP:
            raise TypeError(f"Unknown type '{p.NAME}'")

        return TYPE_MAP[p.NAME]

    @_("condition error")  # noqa: 821
    def operand(self, x):  # noqa: 811
        raise SyntaxError(f"Unexpected token '{x.error.value}'")
