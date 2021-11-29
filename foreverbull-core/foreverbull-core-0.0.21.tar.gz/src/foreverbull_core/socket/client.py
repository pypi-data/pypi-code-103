from foreverbull_core.models.socket import Request, SocketConfig
from foreverbull_core.socket.nanomsg import NanomsgSocket


class SocketClient:
    def __init__(self, config: SocketConfig) -> None:
        self.config = config
        self._socket = NanomsgSocket(config)

    def url(self):
        return self._socket.url()

    def send(self, message):
        self._socket.send(message.dump())

    def recv(self):
        data = self._socket.recv()
        return Request.load(data)

    def close(self):
        self._socket.close()
