from typing import Any

from asking.exceptions import StageNotFoundError, Stop
from asking.loaders import Loader
from asking.models.stage import Stage
from asking.protocols import StateProtocol


class Script:
    def __init__(self, loader: Loader, state: StateProtocol) -> None:
        self._loader = loader
        self._state = state

    def _get_stage(self, key: str) -> Stage:
        stage = self._loader.script_dict.get(key, None)
        if not stage:
            raise StageNotFoundError(key)
        return Stage(stage=stage, state=self._state)

    def start(self) -> Any:
        """
        Performs the script.

        Returns:
            Reason for stopping.
        """

        stage = self._get_stage("start")

        try:
            while True:
                next = stage.perform()
                stage = self._get_stage(next)
        except Stop as ex:
            return ex.reason
