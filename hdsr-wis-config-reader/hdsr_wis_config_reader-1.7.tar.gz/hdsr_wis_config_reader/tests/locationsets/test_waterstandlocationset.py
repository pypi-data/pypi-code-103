from hdsr_wis_config_reader import constants
from hdsr_wis_config_reader.tests.fixtures import loc_sets

import pandas as pd  # noqa pandas comes with geopandas


# silence flake8
loc_sets = loc_sets

expected_idmap_section_name = "WATERSTANDLOCATIES"
expected_name = "waterstandlocaties"
expected_csvfile = "oppvlwater_waterstanden"
expected_fews_name = "OPVLWATER_WATERSTANDEN_AUTO"


expected_validation_attributes = [
    "HARDMAX",
    "WIN_SMAX",
    "OV_SMAX",
    "ZOM_SMAX",
    "WIN_SMIN",
    "OV_SMIN",
    "ZOM_SMIN",
    "HARDMIN",
]

expected_validation_rules = [
    {
        "parameter": "H.G.",
        "extreme_values": {
            "hmax": "HARDMAX",
            "smax_win": "WIN_SMAX",
            "smax_ov": "OV_SMAX",
            "smax_zom": "ZOM_SMAX",
            "smin_win": "WIN_SMIN",
            "smin_ov": "OV_SMIN",
            "smin_zom": "ZOM_SMIN",
            "hmin": "HARDMIN",
        },
    }
]

expected_csvfile_meta = {
    "file": "oppvlwater_waterstanden",
    "geoDatum": "Rijks Driehoekstelsel",
    "id": "%LOC_ID%",
    "name": "%LOC_NAME%",
    "description": "Locaties waterstanden",
    "toolTip": '<html>\n    <table id="details">\n      <tr>\n\t<td width="50" valign="top">ID</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">%ID%</td>\n      </tr>\n      <tr>\n\t<td width="50" valign="top">Naam</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">%NAME%</td>\n      </tr>\n      <tr>\n\t<td width="50" valign="top">Type</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">%DESCRIPTION%</td>\n      </tr>\n      <tr>\n\t<td width="50" valign="top">Hymos</td>\n\t<td width="5" valign="top">:</td>\n\t<td width="200" valign="top">%HIST_TAG%</td>\n      </tr>\n    </table>\n</html>',  # noqa
    "startDateTime": "%START%",
    "endDateTime": "%EIND%",
    "x": "%X%",
    "y": "%Y%",
    "z": "%Z%",
    "relation": [
        {"relatedLocationId": "%GAFCODE%", "id": "AFVOERGEBIED"},
        {"relatedLocationId": "%GPGIDENT%", "id": "PEILGEBIED"},
        {"relatedLocationId": "%RBGID%", "id": "RBGID"},
        {"relatedLocationId": "%PEILSCHAAL%", "id": "PEILSCHAAL"},
    ],
    "attribute": [
        {"number": "%MAAIVELD%", "id": "MAAIVELD"},
        {"text": "%PEILBESLUI%", "id": "PEILBESLUIT"},
        {"text": "%HIST_TAG%", "id": "HIST_TAG"},
        {"boolean": "%GERELATEERD%", "id": "GERELATEERD"},
        {"text": "%SYSTEEM%", "id": "HOOFDSYSTEEM"},
        {"text": "%RAYON%", "id": "RAYON"},
        {"text": "%FOTO_ID%", "id": "FOTO_ID"},
        {"text": "%GPGIDENT%", "id": "PEILGEBIED"},
        {"boolean": "%SWM%", "id": "SWM"},
        {"boolean": "%NWW-MDV%", "id": "SWMGEBIED_NWW-MDV"},
    ],
    "attributeFile": [
        {
            "csvFile": "oppvlwater_langsprofielen",
            "id": "%LOC_ID%",
            "attribute": [
                {"number": "%Langsprofiel_Kromme_Rijn%", "id": "Langsprofiel_Kromme_Rijn",},
                {"number": "%Langsprofiel_Caspargouwse_Wetering%", "id": "Langsprofiel_Caspargouwse_Wetering",},
                {
                    "number": "%Langsprofiel_Stadswater_Utrecht_en_Vecht%",
                    "id": "Langsprofiel_Stadswater_Utrecht_en_Vecht",
                },
                {
                    "number": "%Langsprofiel_Doorslag-Gekanaliseerde_Hollandse_IJssel%",
                    "id": "Langsprofiel_Doorslag-Gekanaliseerde_Hollandse_IJssel",
                },
                {"number": "%Langsprofiel_Oude_Rijn_boezem_Oost%", "id": "Langsprofiel_Oude_Rijn_boezem_Oost",},
                {"number": "%Langsprofiel_Oude_Rijn_boezem_West%", "id": "Langsprofiel_Oude_Rijn_boezem_West",},
                {"number": "%Langsprofiel_Grecht%", "id": "Langsprofiel_Grecht"},
                {
                    "number": "%Langsprofiel_Lange_Linschoten_tm_Jaap_Bijzerwetering%",
                    "id": "Langsprofiel_Lange_Linschoten_tm_Jaap_Bijzerwetering",
                },
                {"number": "%Langsprofiel_Dubbele_Wiericke%", "id": "Langsprofiel_Dubbele_Wiericke",},
                {"number": "%Langsprofiel_Leidsche_Rijn%", "id": "Langsprofiel_Leidsche_Rijn",},
                {"number": "%Langsprofiel_Amsterdam-Rijnkanaal%", "id": "Langsprofiel_Amsterdam-Rijnkanaal",},
                {"number": "%Langsprofiel_Merwedekanaal%", "id": "Langsprofiel_Merwedekanaal",},
                {"number": "%Langsprofiel_Boezem_AGV%", "id": "Langsprofiel_Boezem_AGV",},
                {"number": "%Langsprofiel_Langbroekerwetering%", "id": "Langsprofiel_Langbroekerwetering",},
                {"number": "%Langsprofiel_Amerongerwetering%", "id": "Langsprofiel_Amerongerwetering",},
                {"number": "%Langsprofiel_Schalkwijkse_wetering%", "id": "Langsprofiel_Schalkwijkse_wetering",},
            ],
        },
        {
            "csvFile": "oppvlwater_waterstanden_diff.csv",
            "id": "%LOC_ID%",
            "relation": {"relatedLocationId": "%REL_DIFF%", "id": "REL_DIFF"},
        },
        {
            "csvFile": "oppvlwater_waterstanden_cacb.csv",
            "id": "%LOC_ID%",
            "relation": {"relatedLocationId": "%REL_CACB%", "id": "REL_CACB"},
            "attribute": [{"number": "%COEF_CA%", "id": "COEF_CA"}, {"number": "%COEF_CB%", "id": "COEF_CB"},],
        },
        {
            "csvFile": "oppvlwater_waterstanden_validations.csv",
            "id": "%LOC_ID%",
            "attribute": {"number": "%watervalidatie%", "id": "watervalidatie"},
        },
        {
            "csvFile": "oppvlwater_watervalidatie.csv",
            "id": "%LOC_ID%",
            "startDateTime": "%STARTDATE%",
            "endDateTime": "%ENDDATE%",
            "checkForContinuousPeriod": "false",
            "attribute": [
                {"number": "%WIN_SMAX%", "id": "WIN_SMAX"},
                {"number": "%WIN_SMIN%", "id": "WIN_SMIN"},
                {"number": "%OV_SMAX%", "id": "OV_SMAX"},
                {"number": "%OV_SMIN%", "id": "OV_SMIN"},
                {"number": "%ZOM_SMAX%", "id": "ZOM_SMAX"},
                {"number": "%ZOM_SMIN%", "id": "ZOM_SMIN"},
                {"number": "%HARDMAX%", "id": "HARDMAX"},
                {"number": "%HARDMIN%", "id": "HARDMIN"},
                {"number": "%RATECHANGE%", "id": "RATECHANGE"},
                {"number": "%SR_DEV%", "id": "SR_DEV"},
                {"number": "%SR_PERIOD%", "id": "SR_PERIOD"},
                {"number": "%SR0.5_DEV%", "id": "SR0.5_DEV"},
                {"number": "%SR0.5_PERIOD%", "id": "SR0.5_PERIOD"},
                {"number": "%SR7_DEV%", "id": "SR7_DEV"},
                {"number": "%SR7_PERIOD%", "id": "SR7_PERIOD"},
                {"number": "%TS_RATE%", "id": "TS_RATE"},
                {"number": "%TS_PERIOD%", "id": "TS_PERIOD"},
            ],
        },
        {
            "csvFile": "oppvlwater_herhalingstijden.csv",
            "id": "%LOC_ID%",
            "attribute": [
                {"text": "Annual Exceedance", "id": "Selection"},
                {"number": "%H_Threshold%", "id": "H_Threshold"},
                {"number": "7", "id": "Viewperiod"},
                {"text": "Exponential", "id": "Function"},
                {"text": "Maximum Likelyhood", "id": "Fit"},
                {"text": "No", "id": "SelectComputationPeriod"},
                {"text": "%RekenPeriode_Start%", "id": "ComputationPeriodStart"},
                {"text": "%RekenPeriode_Eind%", "id": "ComputationPeriodEnd"},
                {"text": "YES", "id": "GraphConfidence"},
                {"number": "95", "id": "Confidence"},
                {"text": "Yes", "id": "GraphLegend"},
                {"number": "100", "id": "XasMax"},
                {"text": "01-01-2000", "id": "DayHourDate"},
                {"number": "%H_T1%", "id": "H_T1"},
                {"number": "%H_T2%", "id": "H_T2"},
                {"number": "%H_T5%", "id": "H_T5"},
                {"number": "%H_T10%", "id": "H_T10"},
                {"number": "%H_T25%", "id": "H_T25"},
                {"number": "%H_T50%", "id": "H_T50"},
                {"number": "%H_T100%", "id": "H_T100"},
            ],
        },
    ],
}
expected_attrib_files_1 = [
    {
        "csvFile": "oppvlwater_langsprofielen",
        "id": "%LOC_ID%",
        "attribute": [
            {"number": "%Langsprofiel_Kromme_Rijn%", "id": "Langsprofiel_Kromme_Rijn"},
            {"number": "%Langsprofiel_Caspargouwse_Wetering%", "id": "Langsprofiel_Caspargouwse_Wetering",},
            {"number": "%Langsprofiel_Stadswater_Utrecht_en_Vecht%", "id": "Langsprofiel_Stadswater_Utrecht_en_Vecht",},
            {
                "number": "%Langsprofiel_Doorslag-Gekanaliseerde_Hollandse_IJssel%",
                "id": "Langsprofiel_Doorslag-Gekanaliseerde_Hollandse_IJssel",
            },
            {"number": "%Langsprofiel_Oude_Rijn_boezem_Oost%", "id": "Langsprofiel_Oude_Rijn_boezem_Oost",},
            {"number": "%Langsprofiel_Oude_Rijn_boezem_West%", "id": "Langsprofiel_Oude_Rijn_boezem_West",},
            {"number": "%Langsprofiel_Grecht%", "id": "Langsprofiel_Grecht"},
            {
                "number": "%Langsprofiel_Lange_Linschoten_tm_Jaap_Bijzerwetering%",
                "id": "Langsprofiel_Lange_Linschoten_tm_Jaap_Bijzerwetering",
            },
            {"number": "%Langsprofiel_Dubbele_Wiericke%", "id": "Langsprofiel_Dubbele_Wiericke",},
            {"number": "%Langsprofiel_Leidsche_Rijn%", "id": "Langsprofiel_Leidsche_Rijn",},
            {"number": "%Langsprofiel_Amsterdam-Rijnkanaal%", "id": "Langsprofiel_Amsterdam-Rijnkanaal",},
            {"number": "%Langsprofiel_Merwedekanaal%", "id": "Langsprofiel_Merwedekanaal",},
            {"number": "%Langsprofiel_Boezem_AGV%", "id": "Langsprofiel_Boezem_AGV"},
            {"number": "%Langsprofiel_Langbroekerwetering%", "id": "Langsprofiel_Langbroekerwetering",},
            {"number": "%Langsprofiel_Amerongerwetering%", "id": "Langsprofiel_Amerongerwetering",},
            {"number": "%Langsprofiel_Schalkwijkse_wetering%", "id": "Langsprofiel_Schalkwijkse_wetering",},
        ],
    },
    {
        "csvFile": "oppvlwater_waterstanden_cacb.csv",
        "id": "%LOC_ID%",
        "relation": {"relatedLocationId": "%REL_CACB%", "id": "REL_CACB"},
        "attribute": [{"number": "%COEF_CA%", "id": "COEF_CA"}, {"number": "%COEF_CB%", "id": "COEF_CB"},],
    },
    {
        "csvFile": "oppvlwater_waterstanden_validations.csv",
        "id": "%LOC_ID%",
        "attribute": {"number": "%watervalidatie%", "id": "watervalidatie"},
    },
    {
        "csvFile": "oppvlwater_watervalidatie.csv",
        "id": "%LOC_ID%",
        "startDateTime": "%STARTDATE%",
        "endDateTime": "%ENDDATE%",
        "checkForContinuousPeriod": "false",
        "attribute": [
            {"number": "%WIN_SMAX%", "id": "WIN_SMAX"},
            {"number": "%WIN_SMIN%", "id": "WIN_SMIN"},
            {"number": "%OV_SMAX%", "id": "OV_SMAX"},
            {"number": "%OV_SMIN%", "id": "OV_SMIN"},
            {"number": "%ZOM_SMAX%", "id": "ZOM_SMAX"},
            {"number": "%ZOM_SMIN%", "id": "ZOM_SMIN"},
            {"number": "%HARDMAX%", "id": "HARDMAX"},
            {"number": "%HARDMIN%", "id": "HARDMIN"},
            {"number": "%RATECHANGE%", "id": "RATECHANGE"},
            {"number": "%SR_DEV%", "id": "SR_DEV"},
            {"number": "%SR_PERIOD%", "id": "SR_PERIOD"},
            {"number": "%SR0.5_DEV%", "id": "SR0.5_DEV"},
            {"number": "%SR0.5_PERIOD%", "id": "SR0.5_PERIOD"},
            {"number": "%SR7_DEV%", "id": "SR7_DEV"},
            {"number": "%SR7_PERIOD%", "id": "SR7_PERIOD"},
            {"number": "%TS_RATE%", "id": "TS_RATE"},
            {"number": "%TS_PERIOD%", "id": "TS_PERIOD"},
        ],
    },
]

expected_attrib_files = [
    {
        "csvFile": "oppvlwater_langsprofielen",
        "id": "%LOC_ID%",
        "attribute": [
            {"number": "%Langsprofiel_Kromme_Rijn%", "id": "Langsprofiel_Kromme_Rijn"},
            {"number": "%Langsprofiel_Caspargouwse_Wetering%", "id": "Langsprofiel_Caspargouwse_Wetering",},
            {"number": "%Langsprofiel_Stadswater_Utrecht_en_Vecht%", "id": "Langsprofiel_Stadswater_Utrecht_en_Vecht",},
            {
                "number": "%Langsprofiel_Doorslag-Gekanaliseerde_Hollandse_IJssel%",
                "id": "Langsprofiel_Doorslag-Gekanaliseerde_Hollandse_IJssel",
            },
            {"number": "%Langsprofiel_Oude_Rijn_boezem_Oost%", "id": "Langsprofiel_Oude_Rijn_boezem_Oost",},
            {"number": "%Langsprofiel_Oude_Rijn_boezem_West%", "id": "Langsprofiel_Oude_Rijn_boezem_West",},
            {"number": "%Langsprofiel_Grecht%", "id": "Langsprofiel_Grecht"},
            {
                "number": "%Langsprofiel_Lange_Linschoten_tm_Jaap_Bijzerwetering%",
                "id": "Langsprofiel_Lange_Linschoten_tm_Jaap_Bijzerwetering",
            },
            {"number": "%Langsprofiel_Dubbele_Wiericke%", "id": "Langsprofiel_Dubbele_Wiericke",},
            {"number": "%Langsprofiel_Leidsche_Rijn%", "id": "Langsprofiel_Leidsche_Rijn",},
            {"number": "%Langsprofiel_Amsterdam-Rijnkanaal%", "id": "Langsprofiel_Amsterdam-Rijnkanaal",},
            {"number": "%Langsprofiel_Merwedekanaal%", "id": "Langsprofiel_Merwedekanaal",},
            {"number": "%Langsprofiel_Boezem_AGV%", "id": "Langsprofiel_Boezem_AGV"},
            {"number": "%Langsprofiel_Langbroekerwetering%", "id": "Langsprofiel_Langbroekerwetering",},
            {"number": "%Langsprofiel_Amerongerwetering%", "id": "Langsprofiel_Amerongerwetering",},
            {"number": "%Langsprofiel_Schalkwijkse_wetering%", "id": "Langsprofiel_Schalkwijkse_wetering",},
        ],
    },
    {
        "csvFile": "oppvlwater_waterstanden_cacb.csv",
        "id": "%LOC_ID%",
        "relation": {"relatedLocationId": "%REL_CACB%", "id": "REL_CACB"},
        "attribute": [{"number": "%COEF_CA%", "id": "COEF_CA"}, {"number": "%COEF_CB%", "id": "COEF_CB"},],
    },
    {
        "csvFile": "oppvlwater_waterstanden_validations.csv",
        "id": "%LOC_ID%",
        "attribute": {"number": "%watervalidatie%", "id": "watervalidatie"},
    },
    {
        "csvFile": "oppvlwater_watervalidatie.csv",
        "id": "%LOC_ID%",
        "startDateTime": "%STARTDATE%",
        "endDateTime": "%ENDDATE%",
        "checkForContinuousPeriod": "false",
        "attribute": [
            {"number": "%WIN_SMAX%", "id": "WIN_SMAX"},
            {"number": "%WIN_SMIN%", "id": "WIN_SMIN"},
            {"number": "%OV_SMAX%", "id": "OV_SMAX"},
            {"number": "%OV_SMIN%", "id": "OV_SMIN"},
            {"number": "%ZOM_SMAX%", "id": "ZOM_SMAX"},
            {"number": "%ZOM_SMIN%", "id": "ZOM_SMIN"},
            {"number": "%HARDMAX%", "id": "HARDMAX"},
            {"number": "%HARDMIN%", "id": "HARDMIN"},
            {"number": "%RATECHANGE%", "id": "RATECHANGE"},
            {"number": "%SR_DEV%", "id": "SR_DEV"},
            {"number": "%SR_PERIOD%", "id": "SR_PERIOD"},
            {"number": "%SR0.5_DEV%", "id": "SR0.5_DEV"},
            {"number": "%SR0.5_PERIOD%", "id": "SR0.5_PERIOD"},
            {"number": "%SR7_DEV%", "id": "SR7_DEV"},
            {"number": "%SR7_PERIOD%", "id": "SR7_PERIOD"},
            {"number": "%TS_RATE%", "id": "TS_RATE"},
            {"number": "%TS_PERIOD%", "id": "TS_PERIOD"},
        ],
    },
    {
        "csvFile": "oppvlwater_herhalingstijden.csv",
        "id": "%LOC_ID%",
        "attribute": [
            {"text": "Annual Exceedance", "id": "Selection"},
            {"number": "%H_Threshold%", "id": "H_Threshold"},
            {"number": "7", "id": "Viewperiod"},
            {"text": "Exponential", "id": "Function"},
            {"text": "Maximum Likelyhood", "id": "Fit"},
            {"text": "No", "id": "SelectComputationPeriod"},
            {"text": "%RekenPeriode_Start%", "id": "ComputationPeriodStart"},
            {"text": "%RekenPeriode_Eind%", "id": "ComputationPeriodEnd"},
            {"text": "YES", "id": "GraphConfidence"},
            {"number": "95", "id": "Confidence"},
            {"text": "Yes", "id": "GraphLegend"},
            {"number": "100", "id": "XasMax"},
            {"text": "01-01-2000", "id": "DayHourDate"},
            {"number": "%H_T1%", "id": "H_T1"},
            {"number": "%H_T2%", "id": "H_T2"},
            {"number": "%H_T5%", "id": "H_T5"},
            {"number": "%H_T10%", "id": "H_T10"},
            {"number": "%H_T25%", "id": "H_T25"},
            {"number": "%H_T50%", "id": "H_T50"},
            {"number": "%H_T100%", "id": "H_T100"},
        ],
    },
]


def test_waterstandlocationset(loc_sets):
    assert loc_sets.waterstandloc.fews_config.path == constants.WIS_CONFIG_TEST_DIR
    assert loc_sets.waterstandloc.idmap_section_name == expected_idmap_section_name
    assert loc_sets.waterstandloc.name == expected_name
    assert loc_sets.waterstandloc.csv_filename == expected_csvfile
    assert loc_sets.waterstandloc.fews_name == expected_fews_name
    assert loc_sets.waterstandloc.get_validation_attributes(int_pars=None) == expected_validation_attributes
    assert loc_sets.waterstandloc.validation_rules == expected_validation_rules
    assert loc_sets.waterstandloc.csv_file_meta == expected_csvfile_meta
    assert loc_sets.waterstandloc.attrib_files == expected_attrib_files
    assert isinstance(loc_sets.waterstandloc.geo_df, pd.DataFrame)
    assert isinstance(loc_sets.waterstandloc.geo_df_original, pd.DataFrame)
    pd.testing.assert_frame_equal(left=loc_sets.waterstandloc.geo_df, right=loc_sets.waterstandloc.geo_df_original)
    assert "Z" in loc_sets.waterstandloc.geo_df
    assert not loc_sets.waterstandloc.geo_df["Z"].hasnans
