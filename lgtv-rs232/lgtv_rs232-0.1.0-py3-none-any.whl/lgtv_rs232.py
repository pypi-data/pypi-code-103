import logging
import asyncio
from connector import LgTvRs232Connector
from commands.power import PowerCommands, Power
from commands.aspect_ratio import AspectRatioCommands, AspectRatio
from commands.screen_mute import ScreenMuteCommands, ScreenMute

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

__all__ = ['LgTvRs232Client']


class LgTvRs232Client(LgTvRs232Connector):
    """LG RS-232 TV client."""

    def __init__(self, port):
        """Initialize the LG TV client."""
        super().__init__(port)
        self.power = PowerCommands(self._send_command)
        self.aspect_ratio = AspectRatioCommands(self._send_command)
        self.screen_mute = ScreenMuteCommands(self._send_command)
        self.volume_mute = ScreenMuteCommands(self._send_command)


async def run():
    client = LgTvRs232Client("/tty/USB0")
    await client.power.on()
    await client.power.get_state()
    await client.power.set_state(Power.ON)

    await client.aspect_ratio.set_state(AspectRatio.ORIGINAL)
    await client.aspect_ratio.get_state()

    await client.screen_mute.set_state(ScreenMute.SCREEN_MUTE_ON)
    await client.screen_mute.get_state()

asyncio.run(run())
