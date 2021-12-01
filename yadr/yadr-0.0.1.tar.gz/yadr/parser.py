"""
parse
~~~~~

Parse dice notation.
"""
from functools import wraps
import operator
from typing import Callable, Generic, Optional, Sequence, TypeVar

from yadr import operator as yo
from yadr.model import (
    CompoundResult,
    Result,
    Token,
    TokenInfo,
    op_tokens,
    id_tokens
)


# The dice map.
# This needs to not be a global value, but it will require a very large
# change to this module to get that to work. This will work for now.
dice_map: dict[str, dict] = {}


# Parser specific operations.
def map_result(result: int | tuple[int, ...],
               key: str) -> str | tuple[str, ...]:
    """Map a roll result to a dice map."""
    if isinstance(result, int):
        return dice_map[key][result]
    new_result = [map_result(n, key) for n in result]
    str_result = tuple(str(item) for item in new_result)
    return str_result


# Utility classes and functions.
class Tree:
    """A binary tree."""
    def __init__(self,
                 kind: Token,
                 value: int | str,
                 left: Optional['Tree'] = None,
                 right: Optional['Tree'] = None) -> None:
        self.kind = kind
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        name = self.__class__.__name__
        return f'{name}(kind={self.kind}, value={self.value})'

    def compute(self):
        if self.kind in id_tokens:
            return self.value
        left = self.left.compute()
        right = self.right.compute()
        if self.kind in op_tokens:
            ops_by_symbol = yo.ops_by_symbol
            ops_by_symbol['m'] = map_result
            op = ops_by_symbol[self.value]
        else:
            msg = f'Unknown token {self.kind}'
            raise TypeError(msg)
        return op(left, right)


class Unary(Tree):
    """A unary tree."""
    def __init__(self,
                 kind: Token,
                 value: int | str,
                 child: Optional['Tree'] = None) -> None:
        self.kind = kind
        self.value = value
        self.child = child

    def compute(self):
        if self.kind in id_tokens:
            return self.value
        child = self.child.compute()
        if self.kind in op_tokens:
            op = yo.ops_by_symbol[self.value]
        return op(child)


def next_rule(next_rule: Callable) -> Callable:
    """A decorator for simplifying parsing rules."""
    def outer_wrapper(fn: Callable) -> Callable:
        @wraps(fn)
        def inner_wrapper(*args, **kwargs) -> Callable:
            return fn(next_rule, *args, **kwargs)
        return inner_wrapper
    return outer_wrapper


def u_next_rule(next_rule: Callable) -> Callable:
    """A decorator for simplifying parsing rules."""
    def outer_wrapper(fn: Callable) -> Callable:
        @wraps(fn)
        def inner_wrapper(*args, **kwargs) -> Callable:
            return fn(next_rule, *args, **kwargs)
        return inner_wrapper
    return outer_wrapper


# Parsing initiation.
def parse(tokens: Sequence[TokenInfo]) -> Result | CompoundResult:
    """Parse dice notation tokens."""
    if (Token.ROLL_DELIMITER, ';') not in tokens:
        return _parse_roll(tokens)              # type: ignore

    rolls = []
    while (Token.ROLL_DELIMITER, ';') in tokens:
        index = tokens.index((Token.ROLL_DELIMITER, ';'))
        roll = tokens[0:index]
        rolls.append(roll)
        tokens = tokens[index + 1:]
    else:
        rolls.append(tokens)
    results: Sequence[Result] = []
    for roll in rolls:
        results.append(parse(roll))             # type: ignore
        results = [result for result in results if result is not None]
    if len(results) > 1:
        return CompoundResult(results)
    elif results:
        return results[0]
    return None


def _parse_roll(tokens: Sequence[TokenInfo]) -> Result:
    trees = [Tree(*token) for token in tokens]      # type: ignore
    trees = trees[::-1]
    parsed = last_rule(trees)
    if parsed:
        return parsed.compute()
    return None


# Rule templates.
def _binary_rule(token: Token,
                 next_rule: Callable,
                 trees: list[Tree]) -> Tree:
    """A binary parsing rule."""
    left = next_rule(trees)
    while (trees and trees[-1].kind == token):
        tree = trees.pop()
        tree.left = left
        tree.right = next_rule(trees)
        left = tree
    return left


# Parsing rules.
def groups_and_identity(trees: list[Tree]) -> Tree:
    """Final rule, covering identities, groups, and maps."""
    kind = trees[-1].kind
    value = trees[-1].value
    if kind in id_tokens:
        return trees.pop()
    elif kind == Token.MAP and isinstance(value, tuple):
        name, map_ = value
        global dice_map
        dice_map[name] = map_
        return None
    elif kind == Token.GROUP_OPEN:
        _ = trees.pop()
    else:
        msg = f'Unrecognized token {kind}'
        raise TypeError(msg)
    expression = last_rule(trees)
    if trees[-1].kind == Token.GROUP_CLOSE:
        _ = trees.pop()
    return expression


@next_rule(groups_and_identity)
def pool_gen_operators(next_rule: Callable, trees: list[Tree]):
    """Parse dice operations."""
    return _binary_rule(Token.POOL_GEN_OPERATOR, next_rule, trees)


@next_rule(pool_gen_operators)
def pool_operators(next_rule: Callable, trees: list[Tree]):
    """Parse dice operations."""
    return _binary_rule(Token.POOL_OPERATOR, next_rule, trees)


@u_next_rule(pool_operators)
def u_pool_degen_operators(next_rule: Callable, trees: list[Tree]):
    """Parse dice operations."""
    if trees[-1].kind == Token.U_POOL_DEGEN_OPERATOR:
        tree = trees.pop()
        unary = Unary(tree.kind, tree.value)
        unary.child = next_rule(trees)
        return unary
    return next_rule(trees)


@next_rule(u_pool_degen_operators)
def pool_degen_operators(next_rule: Callable, trees: list[Tree]):
    """Parse dice operations."""
    return _binary_rule(Token.POOL_DEGEN_OPERATOR, next_rule, trees)


@next_rule(pool_degen_operators)
def dice_operators(next_rule: Callable, trees: list[Tree]):
    """Parse dice operations."""
    return _binary_rule(Token.DICE_OPERATOR, next_rule, trees)


@next_rule(dice_operators)
def exponents(next_rule: Callable, trees: list[Tree]):
    """Parse exponents."""
    return _binary_rule(Token.EX_OPERATOR, next_rule, trees)


@next_rule(exponents)
def mul_div(next_rule: Callable, trees: list[Tree]):
    """Parse multiplication and division."""
    return _binary_rule(Token.MD_OPERATOR, next_rule, trees)


@next_rule(mul_div)
def add_sub(next_rule: Callable, trees: list[Tree]):
    """Parse addition and subtraction."""
    return _binary_rule(Token.AS_OPERATOR, next_rule, trees)


@next_rule(add_sub)
def comparison_op(next_rule: Callable, trees: list[Tree]):
    """Parse comparison operator."""
    return _binary_rule(Token.COMPARISON_OPERATOR, next_rule, trees)


@next_rule(comparison_op)
def options_op(next_rule: Callable, trees: list[Tree]):
    """Parse options operator."""
    return _binary_rule(Token.OPTIONS_OPERATOR, next_rule, trees)


@next_rule(options_op)
def choice_op(next_rule: Callable, trees: list[Tree]):
    """Parse options operator."""
    return _binary_rule(Token.CHOICE_OPERATOR, next_rule, trees)


@next_rule(choice_op)
def map_op(next_rule: Callable, trees: list[Tree]):
    """Parse options operator."""
    return _binary_rule(Token.MAPPING_OPERATOR, next_rule, trees)


# Set the last rule in order of operations to make it a little easier
# to update as new operations are added.
last_rule = map_op
