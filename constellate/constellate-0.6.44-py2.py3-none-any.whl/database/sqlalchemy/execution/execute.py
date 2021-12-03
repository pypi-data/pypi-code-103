import asyncio
from typing import Optional, Any, List, Union, AsyncGenerator, Iterable, TypeVar

from aioitertools import chain
from decorator import decorator
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from sqlalchemy.sql import Select

X = TypeVar("X")


async def _execute_select(
    session: AsyncSession = None,
    execute: bool = True,
    stmt: Select = None,
    result_scalars: bool = None,
    result_scalar: bool = None,
    result_one_or_none: bool = None,
    result_one: bool = None,
    result_all: bool = None,
    result_stream: bool = None,
    result_stream_max_row_buffer: int = None,
    return_result_as_sqlalchemy_native: bool = None,
    return_result_as_async_generator: bool = None,
) -> Union[X, Optional[X], Iterable[X], AsyncGenerator[X, None]]:
    if stmt is None:
        raise NotImplementedError()

    if not execute:
        return stmt

    if result_stream:
        # src:
        # https://docs.sqlalchemy.org/en/14/core/connections.html#using-server-side-cursors-a-k-a-stream-results
        stmt = stmt.execution_options(stream_results=True)

    result = await session.execute(stmt)

    if result_scalars is True:
        result = result.scalars()
    elif result_scalar is True:
        result = result.scalar()

    if result_one_or_none is True:
        result = result.one_or_none()
    elif result_one is True:
        result = result.one()
    elif result_all is True:
        result = result.all()

    if return_result_as_sqlalchemy_native:
        if result_stream:
            # result's type: iter[list[X]]
            result = result.partitions(result_stream_max_row_buffer)
            # result's type: iter[X]
            result = chain.from_iterable(result)

        return await __execute_select_return_sqlalchemy_native(result=result)
    elif return_result_as_async_generator:
        if result_stream:
            # result's type: iter[list[X]]
            result = result.partitions(result_stream_max_row_buffer)
            # result's type: iter[X]
            result = chain.from_iterable(result)

        # coroutine
        result = await __execute_select_return_sqlalchemy_native(result=result)
        # async generator
        return await result
    else:
        raise NotImplementedError()


async def __execute_select_return_sqlalchemy_native(
    result: AsyncResult = None,
) -> Union[X, Optional[X], List[X]]:
    return result


async def __execute_select_return_async_generator(
    result: AsyncResult = None,
) -> AsyncGenerator[X, None]:
    for row in result:
        yield row
        asyncio.sleep(0)


@decorator
async def execute_no_result(func, *args, **kwargs) -> None:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session, stmt=stmt, execute=True, return_result_as_sqlalchemy_native=True
    )


@decorator
async def execute_scalar(func, *args, **kwargs) -> List[X]:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalar=True,
        return_result_as_sqlalchemy_native=True,
    )


@decorator
async def execute_scalars_one_or_none(func, *args, **kwargs) -> Optional[X]:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalars=True,
        result_one_or_none=True,
        return_result_as_sqlalchemy_native=True,
    )


@decorator
async def execute_scalars_one(func, *args, **kwargs) -> X:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalars=True,
        result_one=True,
        return_result_as_sqlalchemy_native=True,
    )


@decorator
async def execute_scalars_all_iterable(func, *args, **kwargs) -> Iterable[X]:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalars=True,
        result_all=True,
        return_result_as_sqlalchemy_native=True,
    )


@decorator
async def execute_scalars_all_async_generator(func, *args, **kwargs) -> AsyncGenerator[X, None]:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalars=True,
        result_all=True,
        return_result_as_async_generator=True,
    )


@decorator
async def execute_scalars_stream_iterable(
    func, max_row_buffer: int = None, *args, **kwargs
) -> Iterable[X]:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalars=True,
        result_stream=True,
        result_stream_max_row_buffer=max_row_buffer,
        return_result_as_sqlalchemy_native=True,
    )


@decorator
async def execute_scalars_stream_async_generator(
    func, max_row_buffer: int = None, *args, **kwargs
) -> AsyncGenerator[X, None]:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalars=True,
        result_stream=True,
        result_stream_max_row_buffer=max_row_buffer,
        return_result_as_async_generator=True,
    )
