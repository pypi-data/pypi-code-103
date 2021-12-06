from .helper.gpio import setup_input, edge_detect
from .helper.stats import HostData
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
    OUTPUT,
    WHITE,
)
import asyncio
import os
import logging

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


class Oled:
    """Oled display class."""

    def __init__(self, host_data: HostData) -> None:
        """Initialize OLED screen."""
        self._screen_no = 0
        self._loop = asyncio.get_running_loop()
        self._host_data = host_data
        configure_pin(OLED_PIN)
        setup_input(OLED_PIN)
        edge_detect(OLED_PIN, callback=self._handle_press, bounce=50)
        serial = i2c(port=2, address=0x3C)
        self._device = sh1106(serial)
        _LOGGER.debug("Configuring OLED screen.")

    def get_task(self) -> list:
        """Periodically check for host statistics."""
        return asyncio.create_task(self.render_display())

    async def render_display(self):
        while True:
            screen = screen_order[self._screen_no]
            data = self._host_data.get(screen)
            if data:
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
            await asyncio.sleep(0.5)

    def _handle_press(self, pin: any) -> None:
        """Handle press of PIN for OLED display."""
        if self._screen_no < NUM_OF_SCREENS:
            self._screen_no += 1
        else:
            self._screen_no = 0
