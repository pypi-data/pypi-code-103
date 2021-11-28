from typing import Any

from asking.loaders import Loader
from asking.models import Script
from asking.protocols import StateProtocol


def ask(loader: Loader, state: StateProtocol) -> Any:
    """
    Loads and performs a script.

    Arguments:
        loader: Script loader.
        state:  Runtime state.

    Returns:
        Stop reason.
    """

    script = Script(loader=loader, state=state)
    return script.start()
