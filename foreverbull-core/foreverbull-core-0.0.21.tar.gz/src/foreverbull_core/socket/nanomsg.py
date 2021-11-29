from pynng import exceptions

from foreverbull_core.models.socket import SocketConfig

from .exceptions import SocketClosed, SocketTimeout


class NanomsgSocket:
    def __init__(self, config: SocketConfig):
        self._socket = None
        self._config = config
        self._socket = self._config.socket_type.value
        if self._config.listen:
            self._socket = self._config.socket_type.value(listen=f"tcp://{self._config.host}:{self._config.port}")
        else:
            self._socket = self._config.socket_type.value(dial=f"tcp://{self._config.host}:{self._config.port}")
        self._socket.recv_timeout = self._config.recv_timeout
        self._socket.send_timeout = self._config.send_timeout
        if self._config.listen and self._config.port == 0:
            # Pretty hacky way to find the port that OS randomly assigns when it's orginally set as 0
            self._config.port = int(self._socket.listeners[0].url.split(":")[-1])

    def url(self):
        if self._config.listen:
            return self._socket.listeners[0].url
        return self._socket.dialers[0].url

    def send(self, data):
        try:
            return self._socket.send(data)
        except exceptions.Closed as exc:
            raise SocketClosed(exc)

    def recv(self):
        try:
            return self._socket.recv()
        except exceptions.Timeout as exc:
            raise SocketTimeout(exc)
        except exceptions.Closed as exc:
            raise SocketClosed(exc)

    def close(self):
        return self._socket.close()
