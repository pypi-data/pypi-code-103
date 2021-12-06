from .input import GpioInputButton
from .relay import GpioRelay, MCPRelay
from .oled import Oled
from .const import (
    ACTION,
    ACTIONS,
    ADDRESS,
    GPIO,
    HA_TYPE,
    ID,
    KIND,
    MCP,
    MCP_ID,
    OUTPUT,
    PIN,
    RELAY,
    ON,
    OFF,
    ONLINE,
    STATE,
    ClickTypes,
)
from typing import Callable, Optional, Union, List, Any
import logging
import asyncio
from busio import I2C
from board import SCL, SDA
from adafruit_mcp230xx.mcp23017 import MCP23017

_LOGGER = logging.getLogger(__name__)


def ha_availibilty_message(topic, relay_id):
    """Create availability topic for HA."""
    return {
        "availability": [{"topic": f"{topic}/{STATE}"}],
        "command_topic": f"{topic}/relay/{relay_id}/set",
        "device": {
            "identifiers": [topic],
            "manufacturer": "BoneIO",
            "model": "BoneIO Relay Board",
            "name": f"BoneIO {topic}",
            "sw_version": "0.0.1",
        },
        "name": f"Relay {relay_id}",
        "payload_off": OFF,
        "payload_on": ON,
        "state_topic": f"{topic}/{RELAY}/{relay_id}",
        "unique_id": f"{topic}{RELAY}{relay_id}",
        "value_template": "{{ value_json.state }}",
    }


class Manager:
    """Manager to communicate MQTT with GPIO inputs and outputs."""

    def __init__(
        self,
        send_message: Callable[[str, Union[str, dict]], None],
        topic_prefix: str,
        relay_pins: List,
        input_pins: List,
        ha_discovery: bool = True,
        ha_discovery_prefix: str = "homeassistant",
        mcp23017: Optional[List] = None,
        oled: bool = False,
    ) -> None:
        """Initialize the manager."""
        loop = asyncio.get_event_loop()

        self.send_message = send_message
        self._topic_prefix = topic_prefix
        self.relay_topic = f"{topic_prefix}/{RELAY}/+/set"
        self._input_pins = input_pins
        self._i2cbusio = I2C(SCL, SDA)
        self._mcp = {}
        self._oled = None

        if mcp23017:
            for mcp in mcp23017:
                self._mcp[mcp[ID] or mcp[ADDRESS]] = MCP23017(
                    i2c=self._i2cbusio, address=mcp[ADDRESS]
                )

        def configure_relay(gpio: dict) -> Any:
            """Configure kind of relay. Most common MCP."""
            if gpio[KIND] == MCP:
                mcp = self._mcp.get(gpio.get(MCP_ID, ""))
                if not mcp:
                    _LOGGER.error("No such MCP configured!")
                    return
                return MCPRelay(
                    pin=int(gpio[PIN]),
                    id=gpio[ID],
                    send_message=self.send_message,
                    topic_prefix=topic_prefix,
                    mcp=mcp,
                    ha_type=gpio[HA_TYPE],
                )
            elif gpio[KIND] == GPIO:
                return GpioRelay(
                    pin=gpio[PIN],
                    id=gpio[ID],
                    send_message=self.send_message,
                    topic_prefix=topic_prefix,
                )

        self.output = {gpio[ID]: configure_relay(gpio) for gpio in relay_pins}
        for out in self.output.values():
            if ha_discovery:
                _LOGGER.debug("Sending HA discovery.")
                self.send_ha_autodiscovery(
                    relay=out.id, ha_type=out.ha_type, prefix=ha_discovery_prefix
                )
            loop.call_soon_threadsafe(
                loop.call_later,
                0.5,
                out.send_state,
            )

        self.buttons = [
            GpioInputButton(
                pin=gpio[PIN],
                press_callback=lambda x, i: self.press_callback(x, i, gpio[ACTIONS]),
                rest_pin=gpio,
            )
            for gpio in self._input_pins
        ]

        if oled:
            self._oled = Oled(self.output)

        self.send_message(topic=f"{topic_prefix}/{STATE}", payload=ONLINE)

    def get_oled_tasks(self) -> any:
        if not self._oled:
            return []
        return self._oled.get_tasks()

    def press_callback(self, x: ClickTypes, inpin: str, actions: dict) -> None:
        """Press callback to use in input gpio.
        If relay input map is provided also toggle action on relay."""
        self.send_message(topic=f"{self._topic_prefix}/input/{inpin}", payload=x)
        action = actions.get(x)
        if action:
            if action[ACTION] == OUTPUT:
                """For now only output type is supported"""
                output_gpio = self.output.get(action[PIN])
                if output_gpio:
                    output_gpio.toggle()

    def send_ha_autodiscovery(
        self, relay: str, prefix: str, ha_type: str = "switch"
    ) -> None:
        """Send HA autodiscovery information for each relay."""
        msg = ha_availibilty_message(self._topic_prefix, relay_id=relay)
        topic = f"{prefix}/{ha_type}/{self._topic_prefix}/{ha_type}/config"
        self.send_message(topic=topic, payload=msg)

    def receive_message(self, topic: str, message: str) -> None:
        """Callback for receiving action from Mqtt."""
        extracted_relay = topic.replace(f"{self._topic_prefix}/{RELAY}/", "").replace(
            "/set", ""
        )
        target_device = self.output.get(extracted_relay)
        if target_device:
            if message == ON:
                target_device.turn_on()
            elif message == OFF:
                target_device.turn_off()
