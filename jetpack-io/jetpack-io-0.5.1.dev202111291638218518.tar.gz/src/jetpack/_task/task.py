from __future__ import annotations

import asyncio
import base64
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
import uuid

from jetpack import utils
from jetpack._remote import codec
from jetpack._task.client import Client

T = TypeVar("T")

client = Client()


def get_client() -> Client:
    return client


class AlreadyExistsError(Exception):
    pass


class NotAsyncError(Exception):
    pass


class Task(Generic[T]):
    def __init__(self, func: Callable[..., Union[T, Awaitable[T]]]) -> None:
        if not inspect.iscoroutinefunction(func):
            raise NotAsyncError(
                f"Jetpack funcions must be async. {utils.qualified_func_name(func)} is not async"
            )
        self.func = func
        self.target_time = int(time.time())
        self.id: Optional[uuid.UUID] = None

    async def __call__(self, *args: Any, **kwargs: Any) -> T:
        self.id = await client.create_task(self, args, kwargs)
        result = await client.wait_for_result(self.id)
        return cast(T, result)

    def schedule(self, target_time: int) -> Task[T]:
        self.target_time = target_time
        return self

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
