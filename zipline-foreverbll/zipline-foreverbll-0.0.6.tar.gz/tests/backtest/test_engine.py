import pytest

from app.backtest.engine import Engine
from app.backtest.exceptions import ConfigError


def test_configure(engine_config):
    Engine._config = None
    engine = Engine()
    assert engine.configured is False
    engine.configure(engine_config)
    assert engine.configured is True


def test_configure_bad_timezone(engine_config):
    engine = Engine()
    engine_config.timezone = "qwerty"
    with pytest.raises(ConfigError, match="UnknownTimeZoneError.*"):
        engine.configure(engine_config)


def test_configure_bad_symbol(engine_config):
    engine = Engine()
    engine_config.benchmark = "Elon Musk"
    with pytest.raises(ConfigError, match=".*Symbol 'Elon Musk' as a benchmark not found in this bundle."):
        engine.configure(engine_config)


def test_configure_bad_asset(engine_config):
    engine = Engine()
    engine_config.assets = ["Corndogs"]
    with pytest.raises(ConfigError, match=".*Symbol 'CORNDOGS' was not found."):
        engine.configure(engine_config)
