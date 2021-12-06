"""Basic Relay module."""

import asyncio
from typing import Callable, Union
from ..const import STATE, RELAY, ON, OFF, SWITCH
import logging

_LOGGER = logging.getLogger(__name__)


class BasicRelay:
    """Basic relay class."""

    def __init__(
        self,
        send_message: Callable[[str, Union[str, dict]], None],
        topic_prefix: str,
        id: str = None,
        ha_type=SWITCH,
    ) -> None:
        """Initialize Basic relay."""
        self._id = id
        self._ha_type = ha_type
        self._send_message = send_message
        self._relay_topic = f"{topic_prefix}/{RELAY}/"
        self._send_topic = f"{self._relay_topic}{self.id}"
        self._state = False
        self._loop = asyncio.get_running_loop()

    @property
    def id(self) -> bool:
        """Id of the relay."""
        return self._id or self._pin

    @property
    def state(self) -> bool:
        """Is relay active."""
        return self._state

    def send_state(self) -> None:
        """Send state to Mqtt on action."""
        state = ON if self.is_active else OFF
        self._state = state
        self._send_message(
            topic=self._send_topic,
            payload={STATE: state},
        )

    def toggle(self) -> None:
        """Toggle relay."""
        _LOGGER.debug("Toggle relay.")
        if self.is_active:
            self.turn_off()
        else:
            self.turn_on()

    @property
    def is_active(self) -> bool:
        """Is active check."""
        raise NotImplementedError

    def turn_on(self) -> None:
        """Call turn on action."""
        raise NotImplementedError

    def turn_off(self) -> None:
        """Call turn off action."""
        raise NotImplementedError
