import pytest
from foreverbull_core.broker import Broker
from foreverbull_core.models.backtest import Session
from foreverbull_core.models.socket import Request

from app.app import Application


@pytest.fixture(scope="function")
def application():
    b = Broker("127.0.0.1:8080", "127.0.0.1")
    a = Application(b)
    yield a
    for backtest in a.backtests.values():
        backtest.stop()
        backtest.join()


@pytest.fixture(scope="function")
def stored_backtest(application):
    s = Session(id="abc123", backtest_id="bbid1", worker_count=1)
    req = Request(task="new_backtest", data=s)
    rsp = application._router(req)
    assert rsp.error is None
    assert rsp.data is not None
    yield s


def test_start_stop():
    b = Broker("127.0.0.1:8080", "127.0.0.1")
    a = Application(b)
    a.start()
    a.stop()
    a.join()


def test_route_new_backtest(application):
    s = Session(id="abc123", backtest_id="bbid1", worker_count=1)
    req = Request(task="new_backtest", data=s)
    rsp = application._router(req)
    assert rsp.error is None
    assert rsp.data is not None
    assert "socket" in rsp.data
    assert "broker" in rsp.data
    assert "feed" in rsp.data


def test_route_new_backtest_twice(application):
    s = Session(id="abc123", backtest_id="bbid1", worker_count=1)
    req = Request(task="new_backtest", data=s)
    first = application._router(req)
    second = application._router(req)
    assert first.error is None
    assert second.error is not None
    assert second.error == "ApplicationError('remove backtest before creating new one')"


def test_route_backtest_status(application, stored_backtest):
    req = Request(task="backtest_status", data=stored_backtest)
    rsp = application._router(req)
    assert rsp.error is None
    assert rsp.data is not None
    assert "running" in rsp.data
    assert "session_running" in rsp.data


def test_route_backtest_status_not_stored(application):
    s = Session(id="abc123", backtest_id="bbid1", worker_count=1)
    req = Request(task="backtest_status", data=s)
    rsp = application._router(req)
    assert rsp.error is not None
    assert rsp.data is None
    assert rsp.error == "ApplicationError('backtest not found')"


def test_route_abort_backtest(application, stored_backtest):
    req = Request(task="abort_backtest", data=stored_backtest)
    rsp = application._router(req)
    assert rsp.error is None
    assert rsp.data is None


def test_route_abort_backtest_not_stored(application):
    s = Session(id="abc123", backtest_id="bbid1", worker_count=1)
    req = Request(task="abort_backtest", data=s)
    rsp = application._router(req)
    assert rsp.error is not None
    assert rsp.data is None
    assert rsp.error == "ApplicationError('backtest not found')"


def test_route_remove_backtest(application, stored_backtest):
    req = Request(task="remove_backtest", data=stored_backtest)
    rsp = application._router(req)
    assert rsp.error is None
    assert rsp.data is None


def test_route_remove_backtest_not_stored(application):
    s = Session(id="abc123", backtest_id="bbid1", worker_count=1)
    req = Request(task="remove_backtest", data=s)
    rsp = application._router(req)
    assert rsp.error is not None
    assert rsp.data is None
    assert rsp.error == "ApplicationError('backtest not found')"


@pytest.mark.skip("Dont know how to handle result yet")
def test_route_backtest_result():
    pass


@pytest.mark.skip("Dont know how to handle result yet")
def test_route_backtest_result_negative():
    pass
