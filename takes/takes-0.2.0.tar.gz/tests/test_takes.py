#!/usr/bin/env python

"""Tests for `takes` package."""

from dataclasses import dataclass
from functools import wraps

import pytest

from takes.takes import ObjectConversionError, takes


@dataclass
class Point:
    x: int = 0
    y: int = 0


def test_takes_point():
    X, Y = 1, 1

    @takes(Point)
    def test(point):
        assert isinstance(point, Point)
        assert point.x == X
        assert point.y == Y

    test(Point(x=X, y=Y))
    test({"x": X, "y": Y})


def test_keeps_args():
    outer_arg = object()

    @takes(Point)
    def test(point, arg):
        assert isinstance(point, Point)
        assert arg is outer_arg

    test(Point(), outer_arg)


def test_keeps_kwargs():

    outer = object()

    @takes(Point)
    def test(point, kwarg=None):
        assert isinstance(point, Point)
        assert kwarg is outer

    test(Point(), kwarg=outer)


def test_named_argument():
    @takes(Point, name="point")
    def test(arg, point):
        assert isinstance(point, Point)

    test(object(), Point())


def test_kw_only_argument():
    @takes(Point, name="kw_only")
    def test(args, *, kw_only=None):
        assert isinstance(kw_only, Point)

    test(1, kw_only={"x": 1, "y": 1})


def test_pos_or_kwargs_called_as_pos():
    @takes(Point, name="pos_or_kw_2")
    def test(pos_or_kw_1, pos_or_kw_2):
        assert isinstance(pos_or_kw_2, Point)

    test(1, {"x": 1, "y": 1})


def test_first_pos_or_kwarg_called_as_kwarg():
    @takes(Point, name="pos_or_kw_2")
    def test(pos_or_kw_1, pos_or_kw_2):
        assert isinstance(pos_or_kw_2, Point)

    test(pos_or_kw_1=1, pos_or_kw_2={"x": 1, "y": 1})


def test_second_pos_or_kwarg_called_as_kwarg():
    @takes(Point, name="pos_or_kw_2")
    def test(pos_or_kw_1, pos_or_kw_2):
        assert isinstance(pos_or_kw_2, Point)

    test(1, pos_or_kw_2={"x": 1, "y": 1})


def test_wrong_name_throws_at_decoration_time():
    def test(args):
        pass

    with pytest.raises(ValueError) as exc:
        takes(Point, name="missing")(test)
        assert "not a valid argument" in str(exc.value)


def test_decorated_function_called_with_incorrect_kwarg_throws():
    @takes(Point, name="arg_1")
    def test(arg_1):
        pass

    with pytest.raises(TypeError) as exc:
        test(wrong=1)
        assert "wrong" in str(exc.value)


def test_decorated_function_with_positional_arg_called_with_incorrect_kwarg():
    @takes(Point, name="arg_2")
    def test(arg_1, arg_2):
        pass

    with pytest.raises(TypeError) as exc:
        test(1, wrong=1)
        assert "wrong" in str(exc.value)


def test_object_conversion_error():
    @takes(Point)
    def test(point):
        pass

    with pytest.raises(ObjectConversionError) as exc:
        test("not a point")
        assert "Error converting string to Point: not a point" == str(exc.value)


def test_convert_multiple():
    @takes(Point, name="p1")
    @takes(Point, name="p2")
    def test(p1, p2):
        assert isinstance(p1, Point)
        assert isinstance(p2, Point)

    test({"x": 1, "y": 1}, {"x": 1, "y": 1})


def test_use_with_other_decorators():
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper

    @deco
    @takes(Point)
    def test(point):
        assert isinstance(point, Point)

    test({"x": 1, "y": 1})


def test_value_contains_extra_params_throws():
    @takes(Point)
    def test(point):
        assert isinstance(point, Point)

    with pytest.raises(ObjectConversionError):
        test({"x": 1, "y": 1, "z": 1})
