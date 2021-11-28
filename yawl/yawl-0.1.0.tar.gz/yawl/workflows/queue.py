from contextlib import contextmanager
from typing import Iterator, List

from yawl.workflows.base import WorkFlowStep


class Queue:
    """This class alongside the queue context is responsible for defining a
    precedence order of steps first, and finally responsible for calling
    the execute command of each queued step.

    | Usage:

    |     with queue() as q:
    |         q.add(step_1).add(step_2).process()
    """

    def __init__(self) -> None:
        self.__commands: List[WorkFlowStep] = []

    def add(self, command: WorkFlowStep) -> "Queue":
        if self.__commands:
            command.upstream = self.__commands[-1].dest_table  # type: ignore

        self.__commands.append(command)
        return self

    def process(self) -> None:
        for command in self.__commands:
            command.execute()


@contextmanager
def queue() -> Iterator[Queue]:
    """Context that works with a Queue. Refer to Queue class."""

    queue = Queue()
    yield queue
