import time

import pytest
from foreverbull_core.models.finance import Asset

from app.backtest.backtest import Backtest
from app.backtest.engine import Engine
from app.backtest.exceptions import ConfigError


def test_backtest_test_info_status():
    backtest = Backtest()
    Engine._config = None
    assert "socket" in backtest.info()
    assert "feed" in backtest.info() and "socket" in backtest.info()["feed"]
    assert "broker" in backtest.info() and "socket" in backtest.info()["broker"]
    assert "running" in backtest.info() and backtest.info()["running"] is False

    assert "running" in backtest.status() and backtest.status()["running"] is False
    assert "session_running" in backtest.status() and backtest.status()["session_running"] is False
    assert "configured" in backtest.status() and backtest.status()["configured"] is False
    assert "day_completed" in backtest.status() and backtest.status()["day_completed"] is False

    backtest.start()
    backtest.stop()
    backtest.join()


def test_known_assets():
    backtest = Backtest()
    assets = backtest.known_assets()
    assert len(assets["assets"]) > 0
    assert type(assets["assets"][0]) == Asset


def test_configured(engine_config):
    backtest = Backtest()
    Engine._config = None
    assert backtest.status()["configured"] is False
    backtest.engine.configure(engine_config)
    assert backtest.status()["configured"] is True


def test_setup_taredown():
    backtest = Backtest()
    backtest._setup()
    assert backtest.broker and backtest.broker.is_alive()
    backtest._taredown()
    assert backtest.broker is None


def test_setup_non_configured():
    Engine._config = None
    backtest = Backtest()
    with pytest.raises(ConfigError, match="needs to be configured before run"):
        backtest._setup()


def test_run_once(engine_config, mocker):
    backtest = Backtest()
    mocker.patch.object(backtest.feed, "wait_for_new_day")
    backtest.engine.configure(engine_config)
    backtest.run_backtest()
    while backtest.engine and backtest.engine.is_alive():
        time.sleep(0.1)
    backtest.stop()


def test_run_twice(engine_config, mocker):
    backtest = Backtest()
    mocker.patch.object(backtest.feed, "wait_for_new_day")
    backtest.engine.configure(engine_config)
    backtest.run_backtest()
    while backtest.engine and backtest.engine.is_alive():
        time.sleep(0.1)
    backtest.stop()
    mocker.patch.object(backtest.feed, "wait_for_new_day")
    backtest.run_backtest()
    while backtest.engine and backtest.engine.is_alive():
        time.sleep(0.1)
    backtest.stop()


def test_run_non_threaded(engine_config, mocker):
    backtest = Backtest()
    mocker.patch.object(backtest.feed, "wait_for_new_day")
    backtest.engine.configure(engine_config)
    backtest.run_backtest(threaded=False)
    backtest.stop()


def test_run_early_stop(engine_config):
    backtest = Backtest()
    backtest.engine.configure(engine_config)
    backtest.run_backtest()
    time.sleep(0.5)
    backtest.stop()
