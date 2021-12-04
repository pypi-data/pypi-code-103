from abc import ABC, abstractmethod
from logging import basicConfig, getLogger
from sys import argv, stdout
from typing import IO, Callable, List, Optional, Union

from cline.cli_args import CommandLineArguments
from cline.cli_protocol import CliProtocol, TParser
from cline.exceptions import CannotMakeArguments, UserNeedsHelp, UserNeedsVersion
from cline.tasks import AnyTask, AnyTaskType, HelpTask, VersionTask

RegisteredTasks = List[AnyTaskType]


class Cli(ABC, CliProtocol[TParser]):
    """
    Abstract base class for Cline entrypoints.

    Arguments:
        app_version: Host application version (defaults to empty)
        args:        Original command line arguments (defaults to argv)
        out:         stdout or equivalent output writer (defaults to stdout)
    """

    def __init__(
        self,
        app_version: str = "",
        args: Optional[List[str]] = None,
        out: Optional[IO[str]] = None,
    ) -> None:
        self._logger = getLogger("cline")

        self._app_version = app_version
        self._cli_args: Optional[CommandLineArguments] = None
        self._out = out or stdout
        self._parser: Optional[TParser] = None
        self._raw_args = args or argv[1:]
        self._tasks: Optional[List[AnyTaskType]] = None

        self._logger.debug("%s initialised", self.__class__)

    @property
    def app_version(self) -> str:
        """
        Gets the host application version.
        """

        return self._app_version

    @property
    def cli_args(self) -> CommandLineArguments:
        """
        Gets the parsed command line arguments.
        """

        if not self._cli_args:
            self._cli_args = self.make_cli_args(args=self._raw_args)
        return self._cli_args

    @classmethod
    def invoke_and_exit(
        cls,
        app_version: str = "",
        args: Optional[List[str]] = None,
        callback: Optional[Callable[[int], None]] = None,
        init_logging: bool = True,
        log_level: Optional[Union[int, str]] = None,
        out: Optional[IO[str]] = None,
    ) -> None:
        """
        Invokes the correct task for the given command line arguments then
        exits.

        Arguments:
            app_version: Host application version.

            args: Command line arguments. Reads automatically by default.

            callback: Method to call on completion. Defaults to `exit`.

            init_logging: `True` to have Cline initialise logging. `False` to
            initialise logging yourself.

            log_level: Log level.

            out: Output writer. Defaults to stdout.
        """

        callback = callback or exit

        if init_logging:
            fmt = "%(levelname)s • %(name)s • %(pathname)s:%(lineno)d • %(message)s"
            basicConfig(format=fmt)

        if log_level is not None:
            getLogger("cline").setLevel(log_level)

        cli = cls(app_version=app_version, args=args, out=out)
        try:
            exit_code = cli.task.invoke()
        except KeyboardInterrupt:
            exit_code = 100
        except UserNeedsHelp as ex:
            cli.write_help()
            exit_code = 0 if ex.explicit else 1
        except UserNeedsVersion:
            cli.out.write(cli.app_version)
            cli.out.write("\n")
            exit_code = 0
        except Exception as ex:
            getLogger("cline").exception(ex)
            cli.out.write("🔥 ")
            cli.out.write(str(ex))
            cli.out.write("\n")
            exit_code = 101

        callback(exit_code)

    @abstractmethod
    def make_cli_args(self, args: List[str]) -> CommandLineArguments:
        """
        Parses `args` to make and return `CommandLineArguments`.

        Arguments:
            args: Command line arguments

        Returns:
            Parsed command line arguments
        """

    def make_help_task(self) -> HelpTask:
        """
        Gets an instance of the help task.
        """

        args = HelpTask.make_args(self.cli_args)
        return HelpTask(args=args, out=self.out)

    @abstractmethod
    def make_parser(self) -> TParser:
        """
        Creates and returns an argument parser.
        """

    def make_task(self, task: AnyTaskType) -> Optional[AnyTask]:
        """
        Attempts to make a task instance.

        Arguments:
            task: Task class

        Returns
            Task or `None`
        """

        try:
            self._logger.debug("Asking %s to make arguments", task)
            args = task.make_args(self.cli_args)
            self._logger.debug("%s made arguments", task)
            return task(args=args, out=self.out)
        except (CannotMakeArguments, CannotMakeArguments):
            self._logger.debug("%s failed to make arguments", task)
            return None

    @property
    def out(self) -> IO[str]:
        """
        Gets `stdout` or equivalent output writer.
        """

        return self._out

    @property
    def parser(self) -> TParser:
        """
        Gets the argument parser.
        """

        if not self._parser:
            self._parser = self.make_parser()
        return self._parser

    @abstractmethod
    def register_tasks(self) -> RegisteredTasks:
        """
        Gets the host application tasks to consider for invocation.
        """

    @property
    def task(self) -> AnyTask:
        """
        Gets the task to perform.
        """

        if self._tasks is None:
            self._tasks = self.register_tasks()

        # Walk through all the tasks in priority order, and use the first one
        # that's able to make sense of the command line arguments:
        for task in self._tasks:
            if task_instance := self.make_task(task):
                return task_instance

        # If we know the host application's version then we can handle it:
        if self._app_version:
            if task_instance := self.make_task(VersionTask):
                return task_instance

        # We know we can always make the help task:
        return self.make_help_task()

    @abstractmethod
    def write_help(self) -> None:
        """
        Renders application help to the output writer.
        """
