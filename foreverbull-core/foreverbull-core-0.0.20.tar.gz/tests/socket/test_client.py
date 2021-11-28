import pynng

from foreverbull_core.models.socket import Request, Response, SocketConfig
from foreverbull_core.socket.client import SocketClient


def test_socket_client():
    client = SocketClient(SocketConfig(host="127.0.0.1"))
    req_socket = pynng.Req0(dial=client.url())

    req = Request(task="demo")
    req_socket.send(req.dump())
    client_recieved = client.recv()

    rsp = Response(task="demo")
    client.send(rsp)
    req_socket_recieved = req_socket.recv()

    assert type(client_recieved) == Request
    assert type(req_socket_recieved) == bytes
    assert client.close() is None
