import logging

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class LgTvRs232Connector(object):
    """LG RS-232 TV client."""

    def __init__(self, port):
        """Initialize the LG TV client."""
        self.port = port

    async def _send_command(self, command: str, data: int):
        """Send remote control commands to the TV."""
        _LOGGER.debug("sending command: {" + command + "} with data: {" + str(data) + "} to port: {" + self.port + "}")
        return 1

