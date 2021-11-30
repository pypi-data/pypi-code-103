from hdsr_wis_config_reader import constants
from hdsr_wis_config_reader.tests.fixtures import loc_sets

import pandas as pd  # noqa pandas comes with geopandas


# silence flake8
loc_sets = loc_sets


expected_idmap_section_name = ""
expected_name = "mswlocaties"
expected_csvfile = "msw_stations"
expected_fews_name = "MSW_STATIONS"

expected_validation_attributes = []

expected_validation_rules = []
expected_attrib_files = []

expected_csvfile_meta = {
    "file": "msw_stations",
    "geoDatum": "Rijks Driehoekstelsel",
    "id": "%LOC_ID%",
    "name": "%LOC_NAME%",
    "description": "MSW-station",
    "x": "%X%",
    "y": "%Y%",
    "relation": [
        {"relatedLocationId": "%GAFCODE%", "id": "AFVOERGEBIED"},
        {"relatedLocationId": "%GPGIDENT%", "id": "PEILGEBIED"},
        {"relatedLocationId": "%RBGID%", "id": "RBGID"},
    ],
    "attribute": {"text": "%PARS%", "id": "PARS"},
}


def test_mswlocationset(loc_sets):
    assert loc_sets.mswloc.fews_config.path == constants.WIS_CONFIG_TEST_DIR
    assert loc_sets.mswloc.idmap_section_name == expected_idmap_section_name
    assert loc_sets.mswloc.name == expected_name
    assert loc_sets.mswloc.csv_filename == expected_csvfile
    assert loc_sets.mswloc.fews_name == expected_fews_name
    assert loc_sets.mswloc.get_validation_attributes(int_pars=None) == expected_validation_attributes
    assert loc_sets.mswloc.validation_rules == expected_validation_rules
    assert loc_sets.mswloc.csv_file_meta == expected_csvfile_meta
    assert loc_sets.mswloc.attrib_files == expected_attrib_files
    assert isinstance(loc_sets.mswloc.geo_df, pd.DataFrame)
    assert isinstance(loc_sets.mswloc.geo_df_original, pd.DataFrame)
    pd.testing.assert_frame_equal(left=loc_sets.mswloc.geo_df, right=loc_sets.mswloc.geo_df_original)
