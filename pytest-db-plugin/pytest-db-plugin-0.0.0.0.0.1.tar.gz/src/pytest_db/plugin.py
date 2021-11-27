import pytest
from .db_client_factory import ClientFactory


def pytest_configure(config):
    config._db = ClientFactory(".config.toml").get_client()
    config.pluginmanager.register(config._db)


def pytest_unconfigure(config):
    db = getattr(config, "_db", None)
    if db:
        del config._db
        config.pluginmanager.unregister(db)
