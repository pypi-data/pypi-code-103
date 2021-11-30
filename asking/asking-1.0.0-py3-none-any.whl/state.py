from logging import Logger, getLogger
from sys import stdout
from typing import IO, Any, Dict, List, Optional

from asking.actions import registered_actions
from asking.exceptions import NothingToDoError, Stop
from asking.protocols import StateProtocol
from asking.stop_reasons import InternalStopReason
from asking.types import StageKey


class State(StateProtocol):
    """
    Script state.

    Arguments:
        responses:  Dictionary of previous and updated responses.
        color:      Emit colour.
        directions: User responses to give during testing.
        references: Values referencable during the script.
        out:        Output writer (defaults to stdout).
    """

    def __init__(
        self,
        responses: Any,
        color: bool = True,
        directions: Optional[Any] = None,
        references: Optional[Dict[str, str]] = None,
        out: Optional[IO[str]] = None,
    ) -> None:
        self._color = color
        self._directions = directions or {}
        self._out = out or stdout
        self._references = references or {}
        self._responses = responses

    @property
    def color(self) -> bool:
        """
        Emit colour.
        """

        return self._color

    @property
    def logger(self) -> Logger:
        return getLogger("asking")

    @property
    def out(self) -> IO[str]:
        return self._out

    @property
    def references(self) -> Dict[str, str]:
        """
        Dynamic values referencable at runtime.
        """

        return self._references

    @property
    def responses(self) -> Any:
        """
        Gets the default values and current responses.
        """

        return self._responses

    def perform_action(self, action_dict: Dict[str, Any]) -> Optional[StageKey]:
        self.logger.debug("Performing all known actions on: %s", action_dict)
        any_recognised = False
        for action_cls in registered_actions:
            action = action_cls(action=action_dict, state=self)
            try:
                result = action.perform()
                any_recognised = True
                if result.next:
                    self.logger.debug("Action is redirecting to stage: %s", result.next)
                    return result.next
            except NothingToDoError:
                pass
        if any_recognised:
            self.logger.debug("Action did not direct to a next stage")
        else:
            self.logger.warning("ActionDict was unrecognised: %s", action_dict)
        return None

    def perform_actions(self, actions: List[Dict[str, Any]]) -> StageKey:
        for action_dict in actions:
            if next := self.perform_action(action_dict):
                return next
        self.logger.debug("No more actions: raising NO_MORE_ACTIONS")
        raise Stop(InternalStopReason.NO_MORE_ACTIONS)

    def save_response(
        self,
        key: str,
        value: str,
        responses: Optional[Any] = None,
    ) -> None:
        """
        Saves the response value `value` at `key`.

        Arguments:
            key:   Response path. Use "." as the path separator.
            value: Value
        """

        source = self._responses if responses is None else responses
        self.logger.debug("Saving a value for key %s in response %s", key, source)

        if "." not in key:
            source[key] = value
            return

        key_parts = key.split(".")
        sub_key = key_parts[0]

        if sub_key in source:
            if not isinstance(source[sub_key], dict):
                raise TypeError(
                    f'Expected value at key "{sub_key}" to be a dictionary but found "{source[sub_key]}".'
                )
        else:
            self.logger.debug(
                "Creating sub_key %s subdictionary in %s", sub_key, source
            )
            source[sub_key] = {}

        subdictionary = source[sub_key]

        self.save_response(
            key=".".join(key_parts[1:]),
            value=value,
            responses=subdictionary,
        )

    def get_response(self, key: str) -> Optional[str]:
        """
        Gets a response value.

        Arguments:
            key: Key.

        Returns:
            Value if it exists, else `None`.
        """

        return self._get_value(key=key, source=self._responses)

    def get_direction(self, key: str) -> Optional[str]:
        """
        Gets a direction.

        Arguments:
            key: Key.

        Returns:
            Direction if it exists, else `None`.
        """

        self.logger.debug("Looking up direction: %s", key)
        return self._get_value(key=key, source=self._directions)

    def _get_value(
        self,
        key: str,
        source: Any,
    ) -> Optional[str]:
        """
        Gets the response at `key`.

        Arguments:
            key: Response path. Use "." as the path separator.

        Returns:
            Value if it exists, otherwise `None`.
        """

        if "." not in key:
            value = source.get(key, None)
            return None if value is None else str(value)

        key_parts = key.split(".")
        sub_key = key_parts[0]

        if sub_key in source:
            if not isinstance(source[sub_key], dict):
                raise TypeError(
                    f'Expected value at key "{sub_key}" to be a dictionary but found "{source[sub_key]}".'
                )
        else:
            return None

        subdictionary = source[sub_key]

        return self._get_value(
            key=".".join(key_parts[1:]),
            source=subdictionary,
        )
