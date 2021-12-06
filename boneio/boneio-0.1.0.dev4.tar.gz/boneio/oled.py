from .helper.gpio import setup_input, edge_detect
from .helper.stats import host_stats
from .input.gpio import configure_pin
from .const import (
    OLED_PIN,
    NETWORK,
    CPU,
    DISK,
    MEMORY,
    SWAP,
    NUM_OF_SCREENS,
    UPTIME,
    HOST,
    OUTPUT,
    WHITE,
    OledDataTypes,
)
import asyncio
import os
import socket
import logging

from functools import partial
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont

_LOGGER = logging.getLogger(__name__)


def make_font(name, size):
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts", name))
    return ImageFont.truetype(font_path, size)


fontBig = make_font("DejaVuSans.ttf", 12)
fontSmall = make_font("DejaVuSans.ttf", 10)

screen_order = [UPTIME, NETWORK, CPU, DISK, MEMORY, SWAP, OUTPUT]
lines = [17, 32, 47]


class HostData:
    """Helper class to store host data."""

    data = {UPTIME: {}, NETWORK: {}, CPU: {}, DISK: {}, MEMORY: {}, SWAP: {}}

    def __init__(self, output: dict) -> None:
        """Initialize HostData."""
        self._hostname = socket.gethostname()
        self.data[UPTIME] = {HOST: self._hostname, UPTIME: 0}
        self._output = output

    def write(self, type: str, data: dict) -> None:
        """Write data of chosen type."""
        self.data[type] = data

    def write_uptime(self, uptime: str) -> None:
        """Write uptime."""
        self.data[UPTIME][UPTIME] = uptime

    def get(self, type: OledDataTypes) -> dict:
        """Get saved stats."""
        if type == OUTPUT:
            return self._get_output()
        return self.data[type]

    def _get_output(self) -> dict:
        """Get stats for output."""
        out = {}
        for output in self._output.values():
            out[output.id] = output.state
        return out


class Oled:
    """Oled display class."""

    def __init__(self, output: dict) -> None:
        """Initialize OLED screen."""
        self._screen_no = 0
        self._loop = asyncio.get_running_loop()
        self._host_data = HostData(output=output)
        configure_pin(OLED_PIN)
        setup_input(OLED_PIN)
        edge_detect(OLED_PIN, callback=self._handle_press, bounce=50)
        serial = i2c(port=2, address=0x3C)
        self._device = sh1106(serial)
        _LOGGER.debug("Configuring OLED screen.")

    def get_tasks(self) -> list:
        """Periodically check for host statistics."""
        return [
            asyncio.create_task(func(self._host_data)) for func in host_stats.values()
        ]

    def _handle_press(self, pin: any) -> None:
        """Handle press of PIN for OLED display."""

        def press_callback(screen_no):
            screen = screen_order[screen_no]
            data = self._host_data.get(screen)
            with canvas(self._device) as draw:
                draw.text((1, 1), screen, font=fontBig, fill=WHITE)
                i = 0
                for k in data:
                    draw.text(
                        (3, lines[i]),
                        f"{k} {data[k]}",
                        font=fontSmall,
                        fill=WHITE,
                    )
                    i += 1

        self._loop.call_soon_threadsafe(partial(press_callback, self._screen_no))
        if self._screen_no < NUM_OF_SCREENS:
            self._screen_no += 1
        else:
            self._screen_no = 0
