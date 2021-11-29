import enum
import socket
from typing import Optional, Union

import pydantic
import pynng

from foreverbull_core.models.base import Base


class SocketType(enum.Enum):
    REQUESTER = pynng.Req0
    REPLIER = pynng.Rep0
    PUBLISHER = pynng.Pub0
    SUBSCRIBER = pynng.Sub0

    def __str__(self):
        # return str(self.value())
        return "hegj"


class SocketConfig(Base):
    socket_type: Union[SocketType, str] = SocketType.REPLIER
    host: str = socket.gethostbyname(socket.gethostname())
    port: int = 0
    listen: bool = True
    recv_timeout: int = 5000
    send_timeout: int = 5000

    @pydantic.validator("socket_type")
    def validate_socket_type(cls, v):
        if type(v) is str:
            return getattr(SocketType, v.upper())
        return v

    def dict(self, *args, **kwargs):
        return {
            "socket_type": self.socket_type.name,
            "host": self.host,
            "port": self.port,
            "listen": self.listen,
            "recv_timeout": self.recv_timeout,
            "send_timeout": self.send_timeout,
        }


class Request(Base):
    task: str
    data: Optional[dict] = None


class Response(Base):
    task: str
    error: Optional[str] = None
    data: Optional[dict] = None
