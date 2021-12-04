import pytest
import subprocess
from jais.utils.fileloader import load_yaml
from jais.__init__ import ROOT_DIR, PROJ_DIR

# * this function loads the config file for the tests.
@pytest.fixture
def CNF():
    # Set CWD path
    subprocess.run(['jais', 'set-cwd', PROJ_DIR])
    return load_yaml(ROOT_DIR/"configs/default.yaml")

def test_config(CNF):
    """Check if the config file is loaded correctly."""
    # Check project name
    assert CNF.project_name == "jais"
    assert isinstance(CNF.seed, int)

def test_logging(CNF):
    """Check logging settings"""
    import configparser
    logs_conf = configparser.RawConfigParser()
    logs_conf.read(ROOT_DIR/"configs/logs.conf")
    loggers = logs_conf['loggers']['keys'].split(',')
    assert (CNF.project_name in loggers[-1].lower()) == True

def test_root_dir(CNF):
    assert str(CNF.paths.root_dir) == str(ROOT_DIR)