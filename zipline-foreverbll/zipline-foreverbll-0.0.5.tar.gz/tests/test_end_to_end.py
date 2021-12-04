import pynng
import pytest
from foreverbull_core.broker import Broker
from foreverbull_core.models.backtest import Session
from foreverbull_core.models.finance import Asset, Order
from foreverbull_core.models.socket import Request, Response

from app.app import Application


@pytest.fixture(scope="function")
def application():
    b = Broker("127.0.0.1:8080", "127.0.0.1")
    a = Application(b)
    a.start()
    yield a
    a.stop()
    for backtest in a.backtests.values():
        pass
        # backtest.stop()
        # backtest.join()
    a.join()


@pytest.fixture(scope="function")
def application_socket(application):
    socket = pynng.Req0(dial=f"{application.broker.socket.url()}")
    socket.recv_timeout = 5000
    socket.send_timeout = 5000
    return socket


@pytest.fixture(scope="function")
def backtest(application_socket):
    session = Session(id="demo_session", backtest_id="backtest_id", worker_count=2)
    req = Request(task="new_backtest", data=session)
    data = req.dump()
    application_socket.send(data)
    rsp_data = application_socket.recv()
    rsp = Response.load(rsp_data)
    return rsp.data


def request_socket(socket_info):
    socket = pynng.Req0(dial=f"tcp://{socket_info['host']}:{socket_info['port']}")
    socket.recv_timeout = 5000
    socket.send_timeout = 5000
    return socket


def feed_socket(socket_info):
    socket = pynng.Sub0(dial=f"tcp://{socket_info['host']}:{socket_info['port']}")
    socket.subscribe(b"")
    socket.recv_timeout = 5000
    return socket


def configure(main_socket, engine_config):
    req = Request(task="configure_backtest", data=engine_config)
    main_socket.send(req.dump())
    rsp_data = main_socket.recv()
    return Response.load(rsp_data)


def run_backtest(main_socket):
    req = Request(task="run_backtest")
    main_socket.send(req.dump())
    rsp_data = main_socket.recv()
    return Response.load(rsp_data)


def new_feed_data(feed_socket):
    msg_data = feed_socket.recv()
    msg = Request.load(msg_data)
    return msg


def day_completed(main_socket):
    req = Request(task="run_new_day")
    main_socket.send(req.dump())
    rsp_data = main_socket.recv()
    return Response.load(rsp_data)


def test_known_assets(backtest):
    main = request_socket(backtest["socket"])
    req = Request(task="known_assets")
    main.send(req.dump())
    rsp_data = main.recv()
    rsp = Response.load(rsp_data)
    assert rsp.error is None
    assert type(rsp.data) == dict
    assert "assets" in rsp.data


def test_simple_run(backtest, engine_config):
    main = request_socket(backtest["socket"])
    feed = feed_socket(backtest["feed"]["socket"])

    rsp = configure(main, engine_config)
    assert rsp.error is None

    rsp = run_backtest(main)
    assert rsp.error is None

    while True:
        msg = new_feed_data(feed)
        if msg.task == "day_completed":
            rsp = day_completed(main)
            assert rsp.error is None
        if msg.task == "backtest_completed":
            break


def test_order_and_result(backtest, engine_config):
    main = request_socket(backtest["socket"])
    feed = feed_socket(backtest["feed"]["socket"])
    broker = request_socket(backtest["broker"]["socket"])
    rsp = configure(main, engine_config)
    assert rsp.error is None

    rsp = run_backtest(main)
    assert rsp.error is None

    while True:  # Just to jump one day
        msg = new_feed_data(feed)
        if msg.task == "day_completed":
            rsp = day_completed(main)
            assert rsp.error is None
            break
        if msg.task == "backtest_completed":
            break

    order = Order(asset=Asset(symbol=engine_config.assets[0], exchange="QUANDL"), amount=10)
    req = Request(task="order", data=order)
    broker.send(req.dump())
    rsp_data = broker.recv()
    rsp = Response.load(rsp_data)
    assert rsp.error is None

    while True:
        msg = new_feed_data(feed)
        if msg.task == "day_completed":
            rsp = day_completed(main)
            assert rsp.error is None
        if msg.task == "backtest_completed":
            break

    req = Request(task="result")
    main.send(req.dump())
    rsp_data = main.recv()
    rsp = Response.load(rsp_data)
    assert rsp.error is None
