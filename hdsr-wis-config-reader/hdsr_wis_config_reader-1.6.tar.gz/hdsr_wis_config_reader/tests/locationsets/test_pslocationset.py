from hdsr_wis_config_reader import constants
from hdsr_wis_config_reader.tests.fixtures import loc_sets

import pandas as pd  # noqa pandas comes with geopandas


# silence flake8
loc_sets = loc_sets


expected_idmap_section_name = ""
expected_name = "peilschalen"
expected_csvfile = "oppvlwater_peilschalen"
expected_fews_name = "OPVLWATER_PEILSCHALEN"

expected_validation_attributes = []

expected_validation_rules = []
expected_attrib_files = []
expected_csvfile_meta = {
    "file": "oppvlwater_peilschalen",
    "geoDatum": "Rijks Driehoekstelsel",
    "id": "%LOC_ID%",
    "name": "%LOC_NAME%",
    "description": "Locaties waterstanden",
    "toolTip": '<html>\n    <table id="details">\n      <tr>\n\t<td width="50" valign="top">ID</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">%ID%</td>\n      </tr>\n      <tr>\n\t<td width="50" valign="top">Naam</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">%NAME%</td>\n      </tr>\n      <tr>\n\t<td width="50" valign="top">Type</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">%DESCRIPTION%</td>\n      </tr>\n      <tr>\n\t<td width="50" valign="top">Foto</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">\n\t   <img src="file:$PHOTO_DIR$/Peilschaalfoto/%FOTO_ID%" border="0" width="300" height="300"/>\n\t</td>\n      </tr>\n    </table>\n</html>',  # noqa
    "startDateTime": "%START%",
    "endDateTime": "%EIND%",
    "x": "%X%",
    "y": "%Y%",
    "relation": [
        {"relatedLocationId": "%GAFCODE%", "id": "AFVOERGEBIED"},
        {"relatedLocationId": "%GPGIDENT%", "id": "PEILGEBIED"},
        {"relatedLocationId": "%RBGID%", "id": "RBGID"},
    ],
    "attribute": [
        {"text": "%PEILBESLUI%", "id": "PEILBESLUIT"},
        {"text": "%RAYON%", "id": "RAYON"},
        {"text": "%FOTO_ID%", "id": "FOTO_ID"},
    ],
}


def test_pslocationset(loc_sets):
    assert loc_sets.psloc.fews_config.path == constants.WIS_CONFIG_TEST_DIR
    assert loc_sets.psloc.idmap_section_name == expected_idmap_section_name
    assert loc_sets.psloc.name == expected_name
    assert loc_sets.psloc.csv_filename == expected_csvfile
    assert loc_sets.psloc.fews_name == expected_fews_name
    assert loc_sets.psloc.get_validation_attributes(int_pars=None) == expected_validation_attributes
    assert loc_sets.psloc.validation_rules == expected_validation_rules
    assert loc_sets.psloc.csv_file_meta == expected_csvfile_meta
    assert loc_sets.psloc.attrib_files == expected_attrib_files
    assert isinstance(loc_sets.psloc.geo_df, pd.DataFrame)
    assert isinstance(loc_sets.psloc.geo_df_original, pd.DataFrame)
    pd.testing.assert_frame_equal(left=loc_sets.psloc.geo_df, right=loc_sets.psloc.geo_df_original)
