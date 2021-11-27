from asking.loaders import Loader
from asking.models import Script
from asking.protocols import StateProtocol
from asking.types import StopReason


def ask(loader: Loader, state: StateProtocol) -> StopReason:
    script = Script(loader=loader, state=state)
    return script.start()
