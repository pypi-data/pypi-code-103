from abc import ABC, abstractmethod
from typing import IO, Any, Generic, Type, TypeVar

from cline.cli_args import CommandLineArguments

TTaskArgs = TypeVar("TTaskArgs")


class Task(ABC, Generic[TTaskArgs]):
    """
    Abstract base task. All tasks must inherit from this.

    Arguments:
        args: Strongly-typed task arguments.
        out:  Output writer.
    """

    def __init__(self, args: TTaskArgs, out: IO[str]) -> None:
        self._args = args
        self._out = out

    @property
    def args(self) -> TTaskArgs:
        """
        Gets the strongly-typed task arguments.
        """

        return self._args

    @abstractmethod
    def invoke(self) -> int:
        """
        Invokes the task.

        Reads arguments from `self.args`. Writes output to `self.out`.

        Returns the shell exit code.
        """

    @classmethod
    @abstractmethod
    def make_args(cls, args: CommandLineArguments) -> TTaskArgs:
        """
        Makes and returns strongly-typed arguments for this task based on the
        parsed command line arguments `args`.

        Arguments:
            args: Parsed command line arguments

        Raises:
            CannotMakeArguments: If the given arguments are not relevant to this
            task

        Returns:
            Task arguments
        """

    @property
    def out(self) -> IO[str]:
        """
        Gets the output writer.
        """

        return self._out


AnyTask = Task[Any]
AnyTaskType = Type[AnyTask]
