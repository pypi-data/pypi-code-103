import time
from threading import Event

import pytest
from foreverbull_core.models.backtest import EngineConfig
from foreverbull_core.models.finance import Asset, Order

from app.backtest.broker import Broker
from app.backtest.engine import Engine
from app.backtest.feed import Feed


@pytest.fixture()
def engine_config():
    config = EngineConfig(start_date="2017-01-01", end_date="2017-01-31", benchmark="AAPL", assets=["AAPL", "TSLA"])
    return config


@pytest.fixture()
def asset():
    asset = Asset(symbol="TSLA", exchange="QUANDL")
    return asset


@pytest.fixture()
def order(asset):
    order = Order(
        asset=asset,
        amount=10,
    )
    return order


@pytest.fixture()
def engine(engine_config):
    engine = Engine()
    engine.configure(engine_config)
    yield engine
    engine.stop()
    engine.join()


@pytest.fixture()
def feed(engine, mocker):
    feed = Feed()
    # engine.set_callbacks(None, feed.handle_data, None)
    # mocker.patch.object(feed, "wait_for_new_day")
    yield feed


@pytest.fixture()
def broker(engine, feed, mocker):
    broker = Broker(engine, bardata)
    yield broker


bardata = None
new_day_event = Event()


def handle_data(context, data):
    global bardata
    bardata = data
    if not new_day_event.is_set():
        new_day_event.wait()


@pytest.fixture()
def running_engine(engine):
    new_day_event.clear()
    engine.set_callbacks(None, handle_data, None)

    def new_day():
        new_day_event.set()
        new_day_event.clear()
        time.sleep(0.2)

    def finish():
        new_day_event.set()
        return

    def start_engine():
        engine.start()
        time.sleep(0.2)
        return new_day, finish

    yield start_engine
