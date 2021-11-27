"""Simple Lektor build plugin to run `make lektor` when watched files change."""

import subprocess
from typing import Any

from lektor.pluginsystem import Plugin  # type: ignore


class MakePlugin(Plugin):  # type: ignore
    """Plugin."""

    name = "make"
    description = "Run `make lektor` for custom build systems."
    cmd = ["make", "lektor"]

    def on_before_build_all(self, builder, **extra):
        # type: (Any, **Any) -> None
        """Even hook triggered before the other Lektor build steps."""
        subprocess.Popen(self.cmd).wait()
