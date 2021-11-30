from json import dumps
from logging import basicConfig, getLogger
from typing import Any, Dict, Optional

from yaml import safe_load

from asking.loaders import DictionaryLoader, Loader
from asking.models import Script
from asking.protocols import StateProtocol
from asking.state import State


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


def demo(
    script: str,
    directions: Dict[str, str],
    responses: Optional[Any] = None,
) -> None:
    """
    Loads and demonstrates a script.

    Arguments:
        script:     Script as YAML.
        directions: Directions.
        responses:  Responses.
    """

    # This function isn't unit tested because it runs within source.md and we
    # can eyeball the results before committing any updated documentation.

    basicConfig(level="WARNING")
    logger = getLogger("asking")
    logger.setLevel("WARNING")

    loader = DictionaryLoader(safe_load(script))
    responses = responses or {}
    state = State(responses, color=False, directions=directions)
    stop_reason = ask(loader, state)

    print("Stop reason:", stop_reason)
    print("Responses:")
    print(dumps(responses, indent=2, sort_keys=True))
