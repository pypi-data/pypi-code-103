from typing import Any, Awaitable, Callable, TypeVar, cast

from jetpack._task.task import Task as _Task
from jetpack.config import symbols

T = TypeVar("T")


class FunctionDecorator:
    def __call__(self, fn: Callable[..., T]) -> Callable[..., Awaitable[T]]:
        task: _Task[T] = _Task(fn)
        symbols.get_symbol_table().register(fn)
        return task


# @function is our general remote work decorator. It does not specify how the
# work will be done (RPC, job, queue, etc) and instead leaves that as an
# implementation detail.
function = FunctionDecorator()
