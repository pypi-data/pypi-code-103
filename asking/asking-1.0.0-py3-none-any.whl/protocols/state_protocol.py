from logging import Logger
from typing import IO, Any, Dict, List, Optional, Protocol

from asking.types import StageKey


class StateProtocol(Protocol):
    @property
    def color(self) -> bool:
        """
        Emit colour.
        """

    # @property
    # def directions(self) -> Optional[Any]:
    #     """
    #     Preset responses to inject when running non-interactively.
    #     """

    @property
    def logger(self) -> Logger:
        """
        Logger.
        """

    @property
    def out(self) -> IO[str]:
        """
        Output writer.
        """

    def perform_actions(self, actions: List[Dict[str, Any]]) -> StageKey:
        """
        Performs all actions.
        """

    @property
    def responses(self) -> Any:
        """
        Gets the default values and current responses.
        """

    def get_response(self, key: str) -> Optional[str]:
        """
        Gets a response value.

        Arguments:
            key: Key.

        Returns:
            Value if it exists, else `None`.
        """

    def get_direction(self, key: str) -> Optional[str]:
        """
        Gets a direction.

        Arguments:
            key: Key.

        Returns:
            Direction if it exists, else `None`.
        """

    def save_response(self, key: str, value: str) -> None:
        """
        Saves the response value `value` at `key`.

        Arguments:
            key:   Response path. Use "." as the path separator.
            value: Value
        """

    @property
    def references(self) -> Dict[str, str]:
        """
        Dynamic values referencable at runtime.
        """
