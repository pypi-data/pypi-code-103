from cline.cli_args import CommandLineArguments
from cline.exceptions import UserNeedsVersion
from cline.tasks.task import Task


class VersionTask(Task[None]):
    def invoke(self) -> int:
        raise UserNeedsVersion()

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> None:
        args.assert_true("version")
