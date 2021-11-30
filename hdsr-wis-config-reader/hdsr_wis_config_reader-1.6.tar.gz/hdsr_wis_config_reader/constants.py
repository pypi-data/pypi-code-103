from pathlib import Path


# Handy constant for building relative paths
BASE_DIR = Path(__file__).parent

if BASE_DIR.name != "hdsr_wis_config_reader":
    raise AssertionError(f"BASE_DIR {BASE_DIR.name} must be project name 'hdsr_wis_config_reader'")

WIS_CONFIG_TEST_DIR = BASE_DIR / "tests" / "data" / "input" / "config_wis60prd_202002"
