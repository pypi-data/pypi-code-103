from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import get_terminal_size
from typing import Any, Dict, Optional

# pyright: reportGeneralTypeIssues=false, reportMissingTypeStubs=false
from ansiwrap import fill

from asking.exceptions import NothingToDoError
from asking.protocols import ActionProtocol, StateProtocol


@dataclass
class ActionResult:
    next: Optional[str]


class Action(ABC, ActionProtocol):
    def __init__(self, action: Dict[str, Any], state: StateProtocol) -> None:
        self._action = action
        self._state = state

    def get_string(
        self,
        key: str,
        source: Optional[Dict[str, str]] = None,
        wrap: bool = True,
    ) -> str:
        source = source or self._action
        value = source.get(key, None)
        if value is None:
            raise NothingToDoError()

        str_value = str(value)

        try:
            str_value = str_value.format(None, **self.state.references)
        except KeyError as ex:
            self._state.logger.warning("Missed reference key: %s", ex)

        if wrap:
            str_value = self.wrap(str_value)

        return str(str_value)

    def wrap(self, text: str) -> str:
        try:
            column_count, _ = get_terminal_size()
        except OSError:
            column_count = 70
        width = min(70, column_count)
        filled: str = fill(text, width)
        return str(filled)

    @abstractmethod
    def perform(self) -> ActionResult:
        """
        Performs the action and returns its result.
        """

    @property
    def state(self) -> StateProtocol:
        return self._state
