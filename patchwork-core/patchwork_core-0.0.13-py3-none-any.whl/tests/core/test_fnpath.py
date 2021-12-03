# -*- coding: utf-8 -*-
from typing import Type

import pytest
from pydantic import BaseModel

from patchwork.core.typing import FuncPath


class Result:
    pass


def test_function():
    return Result


async def test_coroutine():
    return Result


def test_function_no_type():
    class M(BaseModel):
        path: FuncPath

    m = M(path='tests.core.test_fnpath:test_function')
    assert m.path() == Result


def test_function_default():
    class M(BaseModel):
        path: FuncPath = FuncPath(test_function)

    m = M()
    assert m.path() == Result


@pytest.mark.asyncio
async def test_coroutine_no_type():
    class M(BaseModel):
        path: FuncPath

    m = M(path='tests.core.test_fnpath:test_coroutine')
    assert await m.path() == Result


@pytest.mark.asyncio
async def test_coroutine_default():
    class M(BaseModel):
        path: FuncPath = FuncPath(test_coroutine)

    m = M()
    assert await m.path() == Result