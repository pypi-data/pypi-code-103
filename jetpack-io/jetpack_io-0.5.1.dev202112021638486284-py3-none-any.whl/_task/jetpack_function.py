from __future__ import annotations

import asyncio
import base64
import contextvars
import inspect
import time
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from jetpack import utils
from jetpack._remote import codec
from jetpack._task.client import Client
from jetpack._task.task import Task

T = TypeVar("T")

client = Client()


def get_client() -> Client:
    return client


class AlreadyExistsError(Exception):
    pass


class NotAsyncError(Exception):
    pass


target_time_var = contextvars.ContextVar[int]("target_time")


class JetpackFunction(Generic[T]):
    def __init__(self, func: Callable[..., Union[T, Awaitable[T]]]) -> None:
        if not inspect.iscoroutinefunction(func):
            raise NotAsyncError(
                f"Jetpack functions must be async. {utils.qualified_func_name(func)} is not async"
            )
        self.func = func
        self.target_time: Optional[int] = None

    async def __call__(self, *args: Any, **kwargs: Any) -> T:
        try:
            target_time = target_time_var.get()
        except LookupError:
            target_time = int(time.time())
        task = Task(self, target_time)
        task.id = await client.create_task(task, args, kwargs)
        if not target_time_var.get(False) and target_time <= time.time():
            # Only wait for result if schedule() was not used and target_time is
            # in the past.
            result = await client.wait_for_result(task.id)
        else:
            # This is a little hacky. We want __call__ to have return type T
            # so that when a user defines a function with return type and adds
            # @function decorator, calling the function will have the same return
            # type. But when we use schedule(), we don't care about the return.
            # Returning None technically violates the type T, but this is an
            # internal detail. Note that schedule() does not use the return.
            result = None
        return cast(T, result)

    def name(self) -> str:
        return utils.qualified_func_name(self.func)

    def exec(self, exec_id: str, base64_encoded_args: str = "") -> None:

        args: Tuple[Any, ...] = ()
        kwargs: Dict[str, Any] = {}
        if base64_encoded_args:
            encoded_args = base64.b64decode(base64_encoded_args).decode("utf-8")
            decoded_args, decoded_kwargs = codec.decode_args(encoded_args)
            if decoded_args:
                args = decoded_args
            if decoded_kwargs:
                kwargs = decoded_kwargs

        retval, err = None, None
        try:
            if inspect.iscoroutinefunction(self.func):
                func = cast(Awaitable[T], self.func(*args, **kwargs))
                retval = asyncio.run(func)
            else:
                retval = cast(T, self.func(*args, **kwargs))
        except Exception as e:
            err = e

        # for now, we post the result back to the remotesvc. A slightly better approach is to
        # have the caller of this function post it (the CLI). Doing it here for now because
        # the remotesvc is already initialized and set up here.
        client.post_result(exec_id, value=retval, error=err)


async def schedule(
    coro: Awaitable[T],
    target_time: Optional[int] = None,
    delta: Optional[int] = None,
) -> None:
    if target_time is not None and delta is not None:
        raise ValueError("target_time and delta cannot both be specified")
    if target_time:
        target_time_var.set(target_time)
    elif delta:
        target_time_var.set(int(time.time()) + delta)
    else:
        raise ValueError("target_time or delta must be specified")
    await coro
