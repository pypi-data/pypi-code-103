from abc import abstractmethod
from asyncio import get_event_loop, Future
from functools import partial
from threading import Thread
from typing import TypeVar, Generic, Type, Callable, Any

from datek_jaipur.errors import EventAlreadyAppliedError, EventNotAppliedError

Result = TypeVar("Result")
DataModel = TypeVar("DataModel")


class BaseEvent(Generic[DataModel, Result]):
    __slots__ = ["_result", "_data_model"]

    class Config:
        input_type: Type[DataModel] = ...

    def __init__(self, **kwargs):
        self._result: Result = ...

        self._data_model: DataModel = (
            self.Config.input_type(**kwargs)
            if self.Config.input_type is not ...
            else None
        )

    @property
    def result(self) -> Result:
        if self._result is ...:
            raise EventNotAppliedError

        return self._result

    async def apply(self):
        if self._result is not ...:
            raise EventAlreadyAppliedError

        await self._validate()
        self._result = await self._create_result()

    async def _validate(self):
        pass

    @abstractmethod
    async def _create_result(self) -> Result:  # pragma: no cover
        pass


async def run_in_thread_pool(func, *args, **kwargs):
    executor = CustomThreadExecutor(func, *args, **kwargs)
    return await executor.run()


class CustomThreadExecutor:
    def __init__(self, func: Callable, *args, **kwargs):
        self._loop = get_event_loop()
        self._result = Future()
        self._func = func
        self._args = args
        self._kwargs = kwargs

    async def run(self) -> Any:
        thread = Thread(target=self._run, daemon=True)
        thread.start()
        await self._result
        result = self._result.result()
        thread.join()
        if isinstance(result, Exception):
            raise result

        return self._result.result()

    def _run(self):
        try:
            result = self._func(*self._args, **self._kwargs)
        except Exception as error:
            result = error

        set_result = partial(self._result.set_result, result)
        self._loop.call_soon_threadsafe(set_result)
