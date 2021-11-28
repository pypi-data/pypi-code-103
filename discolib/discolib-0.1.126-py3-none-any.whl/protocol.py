#
# DISCo Python interface library
# Copyright (c) 2021 Greg Van Aken
#
"""protocol.py: Details of packet protocol construction & parsing."""

from enum import IntEnum

class Const(IntEnum):
    """Constant values present in communication packets."""

    HEADER_1 = 0x42
    HEADER_2 = 0x42

class Cmd(IntEnum):
    """Command types to be sent."""

    GET_PORTS           = 0x01
    GET_PORT_NAME       = 0x02
    GET_PORT_TYPE       = 0x03
    GET_PORT_READBACK   = 0x04
    GET_PORT_SETPOINT   = 0x05

    SET_PORT_SETPOINT   = 0x25

class CommandPacket:
    """A single command packet."""

    MIN_LENGTH = 2 # CMD + CS

    def __init__(self, cmd: Cmd, port: int = None, payload: bytes = bytes([])) -> None:
        """Initialize the bytes requires to send this command (to a port) (with a payload)."""
        self.cmd = cmd
        self.port = bytes([port]) if port else b'' # If no port, no bytes
        self.payload = payload
        self.length = self.MIN_LENGTH + len(self.port) + len(self.payload)
        self._bytes = bytes([Const.HEADER_1, Const.HEADER_2, self.length, self.cmd])
        self._bytes += self.port
        self._bytes += self.payload
        self._bytes += bytes([0x10])  # TODO: CRC
    
    def __bytes__(self):
        """Get the bytes representation of this command."""
        return self._bytes
