# -*- coding: utf-8 -*-

import asyncio
import warnings
from enum import IntEnum
from typing import List, Dict, Any, AsyncGenerator, Iterable

from .base import SynchronousPublisher, SynchronousSubscriber, AsyncPublisher, AsyncSubscriber


class SyncLocalPublisher(SynchronousPublisher):
    """
    Patchwork is asynchronous framework with fully async nodes, so locally async Python must be supported
    to run the worker. Synchronous client make no sense in that case.
    """
    def __init__(self):
        raise NotImplementedError("There is no synchronous local client")


class SyncLocalSubscriber(SynchronousSubscriber):
    """
    Patchwork is asynchronous framework with fully async nodes, so locally async Python must be supported
    to run the worker. Synchronous client make no sense in that case.
    """
    def __init__(self):
        raise NotImplementedError("There is no synchronous local client")


class DummySerializer:

    @classmethod
    def dumps(cls, data):
        return data

    @classmethod
    def loads(cls, data):
        return data


class MissingBehaviour(IntEnum):
    SKIP = 0
    WARN = 1
    CREATE = 2
    EXCEPTION = 3


class AsyncLocalBroker:
    """
    Simple local broker working on asyncio loop for testing and development purposes only.

    !!! danger
        For development purposes only!
    """

    __default = []

    def __init__(
            self,
            initial_queues: Iterable[str] = tuple(),
            publish_missing: MissingBehaviour = MissingBehaviour.CREATE,
            subscribe_missing: MissingBehaviour = MissingBehaviour.WARN,
            max_queue_size: int = 100
    ):
        self._queues: Dict[str, asyncio.Queue] = {}
        self._publish_missing = publish_missing
        self._subscribe_missing = subscribe_missing
        self._queue_size = max_queue_size

        for q_name in initial_queues:
            self._create_queue(q_name)

    @classmethod
    def default(cls):
        if not cls.__default:
            cls.__default.append(cls())

        return cls.__default[0]

    def _create_queue(self, name):
        self._queues[name] = asyncio.Queue(maxsize=self._queue_size)

    def get_queue(self, name: str) -> asyncio.Queue:
        return self._queues[name]

    async def put(self, msg: Any, *, queue_name: str):
        if queue_name not in self._queues:
            if self._publish_missing == MissingBehaviour.SKIP:
                return
            elif self._publish_missing == MissingBehaviour.WARN:
                warnings.warn(
                    f'{self.__class__.__name__}: unable to deliver message to queue {queue_name}: no such queue'
                )
                return
            elif self._publish_missing == MissingBehaviour.CREATE:
                self._create_queue(queue_name)
            else:
                raise ValueError(f'{queue_name}: no such queue')

        await self._queues[queue_name].put(msg)

    async def subscribe(self, queue_names: List[str]) -> AsyncGenerator:

        waiters: Dict[asyncio.Task, str] = {}

        for queue_name in queue_names:
            if queue_name not in self._queues:
                if self._subscribe_missing == MissingBehaviour.SKIP:
                    return
                elif self._subscribe_missing == MissingBehaviour.WARN:
                    warnings.warn(
                        f'{self.__class__.__name__}: unable to subscribe on queue {queue_name}: no such queue')
                    return
                elif self._subscribe_missing == MissingBehaviour.CREATE:
                    self._create_queue(queue_name)
                else:
                    raise ValueError(f'{queue_name}: no such queue')

            waiters[asyncio.create_task(self._queues[queue_name].get())] = queue_name

        while True:
            try:
                done, pending = await asyncio.wait(waiters.keys(), return_when=asyncio.FIRST_COMPLETED)

                for fut in done:
                    # remove resolved future from dict, get associated queue name
                    q_name = waiters.pop(fut)
                    # create new waiter task for this queue name
                    waiters[asyncio.create_task(self._queues[q_name].get())] = q_name
                    # yield fetched value
                    yield fut.result()
                    self._queues[q_name].task_done()
            except asyncio.CancelledError:
                for w in waiters.keys():
                    if not w.done():
                        w.cancel()
                raise
            except GeneratorExit:
                for w in waiters.keys():
                    w.cancel()

                return

    def __str__(self):
        return f'<{self.__class__.__name__}: {", ".join(self._queues.keys())}>'


class AsyncLocalPublisher(AsyncPublisher):
    """
    Simple patchwork client working on local event loop using given local broker

    !!! danger
        For development purposes only!
    """

    def __init__(self, parent=None, broker: AsyncLocalBroker = None, **options):
        """
        :param queue:   asyncio queue to bind to
        """
        super().__init__(parent=parent, **options)
        if broker is None:
            broker = AsyncLocalBroker.default()

        self._broker = broker

    def __repr__(self):
        res = super().__repr__()
        return f"<{res[1:-1]}, broker={self._broker}]>"

    @property
    def broker(self):
        return self._broker

    async def _start(self):
        self.logger.debug(f"Publisher attached to broker {self._broker}")

    async def _stop(self):
        self.logger.debug(f"Publisher left broker {self._broker}")

    async def _send(self, payload, task, timeout: float = None):
        assert task.meta.queue_name, "missing task queue name"
        try:
            if timeout == 0:
                await self._broker.put(payload, queue_name=task.meta.queue_name)
            else:
                await asyncio.wait_for(self._broker.put(payload, queue_name=task.meta.queue_name), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"send operation timeout, can't deliver in {timeout}s")


class AsyncLocalSubscriber(AsyncSubscriber):

    class Config(AsyncSubscriber.Config):
        queue_names: List[str] = []

    def __init__(self, parent=None, broker: AsyncLocalBroker = None, **options):
        """
        :param queue:   asyncio queue to bind to
        """
        if broker is None:
            broker = AsyncLocalBroker.default()

        self._broker = broker
        super().__init__(parent=parent, **options)
        self.uncommitted = set()
        self._fetcher: AsyncGenerator

    def __repr__(self):
        res = super().__repr__()
        return f"<{res[1:-1]}, broker={self._broker}]>"

    @property
    def broker(self):
        return self._broker

    async def _start(self):
        self.logger.debug(f"Subscriber attached to broker {self._broker}")
        self._fetcher = self._broker.subscribe(self.settings.queue_names)

    async def _stop(self):
        await self._fetcher.aclose()
        self.logger.debug(f"Subscriber left broker {self._broker}")

    async def _fetch_one(self, timeout: float = None):
        try:
            return await asyncio.wait_for(self._fetcher.__anext__(), timeout=timeout), {}
        except AttributeError:
            if not hasattr(self, '_fetcher'):
                raise RuntimeError(
                    "Can't fetch task: subscriber seems to be not started. "
                    "Did you forgot to call run() method and await?"
                )
            raise
        except asyncio.TimeoutError:
            raise TimeoutError(f"fetch operation timeout, no messages in {timeout}s")

    async def commit(self, task, *, timeout: float = None):
        self.uncommitted.remove(task.uuid)

    async def get(self, *, timeout: float = None):
        task = await super().get(timeout=timeout)
        self.uncommitted.add(task.uuid)
        return task
