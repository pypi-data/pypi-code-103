from typing import Dict, Optional, Type

from dinject.executors.bash import BashExecutor
from dinject.executors.python import PythonExecutor
from dinject.types import Executor

executors: Dict[str, Type[Executor]] = {
    "bash": BashExecutor,
    "python": PythonExecutor,
}


def make_executor(language: Optional[str], script: str) -> Optional[Executor]:
    """
    Creates a `language` executor for `script`.

    Arguments:
        language: Language.
        script:   Script.

    Returns:
        Executor if one was found, otherwise `None`.
    """

    if t := executors.get(language or "text", None):
        return t(script)
    return None
