from hdsr_wis_config_reader import constants
from hdsr_wis_config_reader.location_sets.collection import LocationSetCollection
from hdsr_wis_config_reader.readers.config_reader import FewsConfigReader

import pytest


@pytest.fixture()
def fews_config() -> FewsConfigReader:
    # we use config saved in this repo (=static), instead of downloading from repo 'wis_config'
    assert constants.WIS_CONFIG_TEST_DIR.is_dir()
    fews_config = FewsConfigReader(path=constants.WIS_CONFIG_TEST_DIR)
    return fews_config


@pytest.fixture
def loc_sets() -> LocationSetCollection:
    fews_config = FewsConfigReader(path=constants.WIS_CONFIG_TEST_DIR)
    loc_sets = LocationSetCollection(fews_config=fews_config)
    return loc_sets


WIS_CONFIG_TEST_DIR = constants.BASE_DIR / "tests" / "data" / "input" / "config_wis60prd_202002"


def test_test_dir_exists():
    assert WIS_CONFIG_TEST_DIR.is_dir()
