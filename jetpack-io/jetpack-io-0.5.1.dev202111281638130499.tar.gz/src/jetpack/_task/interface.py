from typing import Any, Callable

from jetpack._task.task import Task as _Task
from jetpack.config import symbols


class TaskDecorator:
    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        task = _Task(fn)
        symbols.get_symbol_table().register(fn)
        return task


# @function is our general remote work decorator. It does not specify how the
# work will be done (RPC, job, queue, etc) and instead leaves that as an
# implementation detail.
function = TaskDecorator()
