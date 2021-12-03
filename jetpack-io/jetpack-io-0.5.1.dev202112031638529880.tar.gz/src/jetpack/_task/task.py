from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
import uuid

# Prevent circular dependency
if TYPE_CHECKING:
    from jetpack._task.jetpack_function import JetpackFunction


class Task:
    def __init__(self, jetpack_function: JetpackFunction[Any], target_time: int):
        self.jetpack_function = jetpack_function
        self.target_time = target_time
        self.id: Optional[uuid.UUID] = None
