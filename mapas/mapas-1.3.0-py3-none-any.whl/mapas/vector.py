import math
from typing import Tuple, Union

Number = Union[int, float]


def add(a: Tuple[Number, Number], b: Tuple[Number, Number]) -> Tuple[Number, Number]:
    return a[0] + b[0], a[1] + b[1]


def sub(a: Tuple[Number, Number], b: Tuple[Number, Number]) -> Tuple[Number, Number]:
    return a[0] - b[0], a[1] - b[1]


def mul(v: Tuple[Number, Number], a: Number) -> Tuple[Number, Number]:
    return v[0] * a, v[1] * a


def div(v: Tuple[Number, Number], a) -> Tuple[Number, Number]:
    return v[0] / a, v[1] / a


def ceil(v: Tuple[Number, Number]) -> Tuple[int, int]:
    return math.ceil(v[0]), math.ceil(v[1])
