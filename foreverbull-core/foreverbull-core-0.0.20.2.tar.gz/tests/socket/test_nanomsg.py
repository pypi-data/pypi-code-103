import socket

import pynng
import pytest

from foreverbull_core.models.socket import Request, Response, SocketConfig
from foreverbull_core.socket.client import SocketClient
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout
from foreverbull_core.socket.nanomsg import NanomsgSocket


@pytest.fixture(scope="function")
def local_requester():
    socket = None

    def setup(url):
        nonlocal socket
        socket = pynng.Req0(dial=url)
        return socket

    yield setup


@pytest.fixture(scope="function")
def local_replier():
    socket = pynng.Socket

    def setup(url):
        nonlocal socket
        socket = pynng.Rep0(listen=url)
        return socket

    yield setup


def test_default_configuration():
    c = SocketConfig()
    expected = {
        "socket_type": "REPLIER",
        "host": socket.gethostbyname(socket.gethostname()),
        "port": 0,
        "listen": True,
        "recv_timeout": 5000,
        "send_timeout": 5000,
    }
    assert c.dict() == expected


def test_request_model():
    assert Request.schema()["required"] == ["task"]
    r = Request(task="demo", data={"demo": "data"})
    expected = {"task": "demo", "data": {"demo": "data"}}
    assert r.dict() == expected
    assert r.dump() == b'{"task": "demo", "data": {"demo": "data"}}'


def test_response_model():
    assert Response.schema()["required"] == ["task"]
    r = Response(task="demo", error=repr(Exception("no work")), data={"response": "data"})
    expected = {"task": "demo", "error": repr(Exception("no work")), "data": {"response": "data"}}
    assert r.dict() == expected


def test_socket_client(local_requester):
    sc = SocketClient(SocketConfig(host="127.0.0.1"))
    lr = local_requester(sc._socket.url())

    expected = Request(task="demo", data={"demo": "data"})
    lr.send(expected.dump())
    reply = sc.recv()
    assert reply == expected

    expected = Response(task="demo", error=repr(Exception("no work")), data={"response": "data"})
    reply = sc.send(expected)
    reply = lr.recv()
    assert Response.load(reply) == expected


def test_nanomsg_socket():
    config = SocketConfig(socket_type="requester", host="127.0.0.1", port=1337)
    sock = NanomsgSocket(config)
    assert len(sock._socket.dialers) == 0
    assert len(sock._socket.listeners) == 1
    assert sock.url() == "tcp://127.0.0.1:1337"
    sock.close()

    config = SocketConfig(socket_type="replier", host="127.0.0.1", port=1337)
    sock = NanomsgSocket(config)
    assert len(sock._socket.dialers) == 0
    assert len(sock._socket.listeners) == 1
    sock.close()


def test_nanomsg_socket_recv_senc(local_requester):
    config = SocketConfig(socket_type="replier", host="127.0.0.1", port=1337)
    sock = NanomsgSocket(config)

    lr = local_requester(sock.url())

    lr.send(b"hello")
    assert sock.recv() == b"hello"

    sock._socket.recv_timeout = 10
    with pytest.raises(SocketTimeout):
        sock.recv()

    sock.close()
    with pytest.raises(SocketClosed):
        sock.recv()

    lr.close()


def test_nanomsg_socket_dial(local_replier):
    expected_url = "tcp://127.0.0.1:1337"
    lr = local_replier(expected_url)

    config = SocketConfig(socket_type="requester", host="127.0.0.1", port=1337, listen=False)
    sock = NanomsgSocket(config)
    assert sock.url() == expected_url

    sock.close()

    with pytest.raises(SocketClosed):
        sock.send(b"hello")
    lr.close()
