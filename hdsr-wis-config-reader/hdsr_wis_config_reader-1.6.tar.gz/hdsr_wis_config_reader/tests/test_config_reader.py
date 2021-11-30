from hdsr_wis_config_reader.tests.fixtures import fews_config


# silence flake8
fews_config = fews_config


expected_parameters = {
    "parameterType": "accumulative",
    "unit": "mm",
    "valueResolution": "0.001",
    "parameter": [
        {"shortName": "Neerslagaccumulatie [mm] - noneq", "id": "Rh.C.0", "name": "Neerslagaccumulatie [mm] - noneq"},
        {"shortName": "Neerslaghoeveelheid [mm] - 5min", "id": "Rh.5", "name": "Neerslaghoeveelheid [mm] - 5min"},
        {"shortName": "Neerslaghoeveelheid [mm] - 10min", "id": "Rh.10", "name": "Neerslaghoeveelheid [mm] - 10min"},
        {"shortName": "Neerslaghoeveelheid [mm] - 15min", "id": "Rh.15", "name": "Neerslaghoeveelheid [mm] - 15min"},
        {"shortName": "Neerslaghoeveelheid [mm] - uur", "id": "Rh.h", "name": "Neerslaghoeveelheid [mm] - uur"},
        {"shortName": "Neerslaghoeveelheid [mm] - dag", "id": "Rh.d", "name": "Neerslaghoeveelheid [mm] - dag"},
        {
            "shortName": "Neerslaghoeveelheid [mm] - 8-8",
            "description": "te gebruiken voor de 8 tot 8 neerslag",
            "id": "Rh88",
            "name": "Neerslaghoeveelheid [mm] - 8-8",
        },
        {"shortName": "Neerslaghoeveelheid [mm] - maand", "id": "Rh.m", "name": "Neerslaghoeveelheid [mm] - maand"},
        {"shortName": "Neerslaghoeveelheid [mm] - jaar", "id": "Rh.y", "name": "Neerslaghoeveelheid [mm] - jaar"},
        {
            "shortName": "Neerslaghoeveelheid- tijdelijke variabele [mm]",
            "id": "Rh.TMP",
            "name": "Neerslaghoeveelheid- tijdelijke variabele [mm]",
        },
        {
            "shortName": "Neerslaghoeveelheid- tijdelijke variabele 2 [mm]",
            "id": "Rh.TMP2",
            "name": "Neerslaghoeveelheid- tijdelijke variabele 2 [mm]",
        },
        {"shortName": "Neerslagtekort [mm] - dag", "id": "RHdef.d", "name": "Neerslagtekort [mm] - dag"},
        {"shortName": "Neerslagtekort [mm] - maand", "id": "RHdef.m", "name": "Neerslagtekort [mm] - maand"},
        {"shortName": "Neerslagtekort [mm] - jaar", "id": "RHdef.y", "name": "Neerslagtekort [mm] - jaar"},
        {
            "shortName": "Cumulatief neerslagtekort [mm] - dag",
            "id": "RHdef.C.d",
            "name": "Cumulatief neerslagtekort [mm] - dag",
        },
    ],
}


def test_fews_config(fews_config):
    parameters_groups_neerslag = fews_config.get_parameters(dict_keys="groups")["Neerslag"]
    assert parameters_groups_neerslag == expected_parameters
    only_parameters = fews_config.get_parameters(dict_keys="parameters")
    assert only_parameters["RHdef.d"] == {
        "shortName": "Neerslagtekort [mm] - dag",
        "name": "Neerslagtekort [mm] - dag",
        "parameterType": "accumulative",
        "unit": "mm",
        "valueResolution": "0.001",
        "groupId": "Neerslag",
    }
