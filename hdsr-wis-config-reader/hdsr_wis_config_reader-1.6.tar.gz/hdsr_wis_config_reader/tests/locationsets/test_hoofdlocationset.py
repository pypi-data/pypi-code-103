from hdsr_wis_config_reader import constants
from hdsr_wis_config_reader.tests.fixtures import loc_sets

import pandas as pd  # noqa pandas comes with geopandas


# silence flake8
loc_sets = loc_sets


expected_idmap_section_name = "KUNSTWERKEN"
expected_name = "hoofdlocaties"
expected_csvfile = "oppvlwater_hoofdloc"
expected_fews_name = "OPVLWATER_HOOFDLOC"


expected_validation_attributes = [
    "HS1_HMAX",
    "HS1_HMIN",
    "HS2_HMAX",
    "HS2_HMIN",
    "HS3_HMAX",
    "HS3_HMIN",
]

expected_validation_rules = [
    {"parameter": "H.S.", "extreme_values": {"hmax": "HS1_HMAX", "hmin": "HS1_HMIN"}},
    {"parameter": "H2.S.", "extreme_values": {"hmax": "HS2_HMAX", "hmin": "HS2_HMIN"}},
    {"parameter": "H3.S.", "extreme_values": {"hmax": "HS3_HMAX", "hmin": "HS3_HMIN"}},
]

expected_csvfile_meta = {
    "file": "oppvlwater_hoofdloc",
    "geoDatum": "Rijks Driehoekstelsel",
    "id": "%LOC_ID%",
    "name": "%LOC_NAME%",
    "description": "Hoofdlocaties oppervlaktewater",
    "toolTip": '<html>\n    <table id="details">\n      <tr>\n\t<td width="50" valign="top">ID</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">%ID%</td>\n      </tr>\n      <tr>\n\t<td width="50" valign="top">Naam</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">%NAME%</td>\n      </tr>\n      <tr>\n\t<td width="50" valign="top">Type</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">%DESCRIPTION%</td>\n      </tr>\n      <tr>\n\t<td width="50" valign="top">Foto</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top"><img src="file:$PHOTO_DIR$/Kunstwerkfoto/%FOTO_ID%" border="0" width="300" height="300"/></td>\n    </tr>\n    </table>\n</html>',  # noqa
    "startDateTime": "%START%",
    "endDateTime": "%EIND%",
    "x": "%X%",
    "y": "%Y%",
    "z": "%Z%",
    "attribute": [
        {"text": "%ALLE_TYPES%", "id": "ALLE_TYPES"},
        {"text": "%SYSTEEM%", "id": "HOOFDSYSTEEM"},
        {"text": "%RAYON%", "id": "RAYON"},
        {"text": "%KOMPAS%", "id": "KOMPAS"},
        {"text": "%FOTO_ID%", "id": "FOTO_ID"},
        {"text": "%SCHEMA%", "id": "SCHEMA"},
    ],
    "attributeFile": [
        {
            "csvFile": "oppvlwater_hoofdloc_parameters.csv",
            "id": "%LOC_ID%",
            "attribute": {"text": "%PARAMETERS%", "id": "PARAMETERS"},
        },
        {
            "csvFile": "oppvlwater_hoofdloc_validations.csv",
            "id": "%LOC_ID%",
            "attribute": [
                {"text": "%kunstvalidatie_streef1%", "id": "kunstvalidatie_streef1"},
                {"text": "%kunstvalidatie_streef2%", "id": "kunstvalidatie_streef2"},
                {"text": "%kunstvalidatie_streef3%", "id": "kunstvalidatie_streef3"},
            ],
        },
        {
            "csvFile": "oppvlwater_kunstvalidatie_streef1.csv",
            "id": "%LOC_ID%",
            "startDateTime": "%STARTDATE%",
            "endDateTime": "%ENDDATE%",
            "attribute": [{"number": "%HS1_HMAX%", "id": "HS1_HMAX"}, {"number": "%HS1_HMIN%", "id": "HS1_HMIN"},],
        },
        {
            "csvFile": "oppvlwater_kunstvalidatie_streef2.csv",
            "id": "%LOC_ID%",
            "startDateTime": "%STARTDATE%",
            "endDateTime": "%ENDDATE%",
            "attribute": [{"number": "%HS2_HMAX%", "id": "HS2_HMAX"}, {"number": "%HS2_HMIN%", "id": "HS2_HMIN"},],
        },
        {
            "csvFile": "oppvlwater_kunstvalidatie_streef3.csv",
            "id": "%LOC_ID%",
            "startDateTime": "%STARTDATE%",
            "endDateTime": "%ENDDATE%",
            "attribute": [{"number": "%HS3_HMAX%", "id": "HS3_HMAX"}, {"number": "%HS3_HMIN%", "id": "HS3_HMIN"},],
        },
        {
            "csvFile": "oppvlwater_kentermeetdata.csv",
            "id": "%LOC_ID%",
            "attribute": [
                {"text": "%KENTER_EAN%", "id": "EAN"},
                {"text": "%KENTER_EAN%", "id": "KENTER_EAN"},
                {"text": "%METER_ID%", "id": "METER_ID"},
            ],
        },
    ],
}

expected_attrib_files = [
    {
        "csvFile": "oppvlwater_hoofdloc_parameters.csv",
        "id": "%LOC_ID%",
        "attribute": {"text": "%PARAMETERS%", "id": "PARAMETERS"},
    },
    {
        "csvFile": "oppvlwater_hoofdloc_validations.csv",
        "id": "%LOC_ID%",
        "attribute": [
            {"text": "%kunstvalidatie_streef1%", "id": "kunstvalidatie_streef1"},
            {"text": "%kunstvalidatie_streef2%", "id": "kunstvalidatie_streef2"},
            {"text": "%kunstvalidatie_streef3%", "id": "kunstvalidatie_streef3"},
        ],
    },
    {
        "csvFile": "oppvlwater_kunstvalidatie_streef1.csv",
        "id": "%LOC_ID%",
        "startDateTime": "%STARTDATE%",
        "endDateTime": "%ENDDATE%",
        "attribute": [{"number": "%HS1_HMAX%", "id": "HS1_HMAX"}, {"number": "%HS1_HMIN%", "id": "HS1_HMIN"},],
    },
    {
        "csvFile": "oppvlwater_kunstvalidatie_streef2.csv",
        "id": "%LOC_ID%",
        "startDateTime": "%STARTDATE%",
        "endDateTime": "%ENDDATE%",
        "attribute": [{"number": "%HS2_HMAX%", "id": "HS2_HMAX"}, {"number": "%HS2_HMIN%", "id": "HS2_HMIN"},],
    },
    {
        "csvFile": "oppvlwater_kunstvalidatie_streef3.csv",
        "id": "%LOC_ID%",
        "startDateTime": "%STARTDATE%",
        "endDateTime": "%ENDDATE%",
        "attribute": [{"number": "%HS3_HMAX%", "id": "HS3_HMAX"}, {"number": "%HS3_HMIN%", "id": "HS3_HMIN"},],
    },
    {
        "csvFile": "oppvlwater_kentermeetdata.csv",
        "id": "%LOC_ID%",
        "attribute": [
            {"text": "%KENTER_EAN%", "id": "EAN"},
            {"text": "%KENTER_EAN%", "id": "KENTER_EAN"},
            {"text": "%METER_ID%", "id": "METER_ID"},
        ],
    },
]


def test_hoofdlocationset(loc_sets):
    assert loc_sets.hoofdloc.fews_config.path == constants.WIS_CONFIG_TEST_DIR
    assert loc_sets.hoofdloc.idmap_section_name == expected_idmap_section_name
    assert loc_sets.hoofdloc.name == expected_name
    assert loc_sets.hoofdloc.csv_filename == expected_csvfile
    assert loc_sets.hoofdloc.fews_name == expected_fews_name
    assert loc_sets.hoofdloc.get_validation_attributes(int_pars=None) == expected_validation_attributes
    assert loc_sets.hoofdloc.validation_rules == expected_validation_rules
    assert loc_sets.hoofdloc.csv_file_meta == expected_csvfile_meta
    assert loc_sets.hoofdloc.attrib_files == expected_attrib_files
    assert isinstance(loc_sets.hoofdloc.geo_df, pd.DataFrame)
    assert isinstance(loc_sets.hoofdloc.geo_df_original, pd.DataFrame)
    pd.testing.assert_frame_equal(left=loc_sets.hoofdloc.geo_df, right=loc_sets.hoofdloc.geo_df_original)


def test_hoofdlocs_geom_z_nodata(loc_sets):
    # we do not add '-9999' to location csv (as it becomes '-9999.0' since float column, better leave it blank)
    assert loc_sets.hoofdloc.geo_df.iloc[0].Z == "2.87"
    assert loc_sets.hoofdloc.geo_df.iloc[0].geometry.z == 2.87
    assert loc_sets.hoofdloc.geo_df.iloc[1].Z == "", "empty cells should be left empty, so '' in csv and pd.NA in df"
    assert loc_sets.hoofdloc.geo_df.iloc[1].geometry.z == loc_sets.hoofdloc.fews_config.Z_NODATA_VALUE
