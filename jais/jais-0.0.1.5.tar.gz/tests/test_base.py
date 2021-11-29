import pytest
from jais.utils import load_config, ROOT_DIR

# * this function loads the config file for the tests.
@pytest.fixture
def CNF():
    return load_config(ROOT_DIR/"configs/default.yaml")

def test_config(CNF):
    """Check if the config file is loaded correctly."""
    # Check project name
    assert CNF.project_name == "jais"

def test_logging(CNF):
    """Check logging settings"""
    import configparser
    logs_conf = configparser.RawConfigParser()
    logs_conf.read(ROOT_DIR/"configs/logs.conf")
    loggers = logs_conf['loggers']['keys'].split(',')
    assert (CNF.project_name in loggers[-1].lower()) == True