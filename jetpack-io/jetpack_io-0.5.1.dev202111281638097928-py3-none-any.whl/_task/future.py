from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, cast
import uuid

T = TypeVar("T")

# Prevent circular dependency
if TYPE_CHECKING:
    from jetpack._task.client import Client


class Future(Generic[T]):
    def __init__(self, client: Client, task_id: uuid.UUID) -> None:
        self.client = client
        self.task_id = task_id

    def get(self) -> T:
        # wait_for_result returns any. Can we make this better?
        return cast(T, self.client.wait_for_result(self.task_id))
