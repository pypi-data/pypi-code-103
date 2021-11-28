from dataclasses import dataclass
from json import dumps
from pathlib import Path
from typing import Any, Dict, Optional

from cline import CommandLineArguments, Task

from asking.loaders.file_loader import FileLoader
from asking.models import Script
from asking.state import State


@dataclass
class PerformTaskArguments:
    path: Path
    directions: Optional[Dict[str, str]] = None
    responses: Optional[Any] = None


class PerformTask(Task[PerformTaskArguments]):
    @classmethod
    def make_args(cls, args: CommandLineArguments) -> PerformTaskArguments:
        return PerformTaskArguments(path=Path(args.get_string("path")))

    def invoke(self) -> int:
        responses: Any = {}
        state = State(responses, directions=self.args.directions)
        script = Script(FileLoader(self.args.path), state)
        stop_reason = script.start()

        self.out.write("Stopped with reason: ")
        self.out.write(str(stop_reason))
        self.out.write("\n")
        self.out.write("Stopped with responses: ")
        self.out.write(dumps(responses, indent=2, sort_keys=True))
        self.out.write("\n")

        return 0
