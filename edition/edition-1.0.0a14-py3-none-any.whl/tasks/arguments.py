from dataclasses import dataclass
from pathlib import Path


@dataclass
class PressArguments:
    key: str
    """
    Press key.
    """

    log_level: str

    output: Path
    """
    Path to write to.
    """

    source: Path
    """
    Path to read from.
    """
