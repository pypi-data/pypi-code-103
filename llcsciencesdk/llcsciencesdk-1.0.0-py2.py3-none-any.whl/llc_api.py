from dataclasses import dataclass, field

import requests
import pandas as pd

from llcsciencesdk.exceptions import (
    ApiAuthenticationError,
    ApiGeneralError,
    ApiTokenError,
)
from llcsciencesdk.urls import make_urls, ApiUrls


@dataclass
class ScienceSdk:
    auth_token: str = field(default_factory=str, repr=False)
    environment: str = "production"
    api_urls: ApiUrls = None

    def __post_init__(self):
        self.api_urls = make_urls(self.environment)

    def login(self, username: str, password: str):
        r = requests.post(
            self.api_urls.AUTH_URL, data={"username": username, "password": password}
        )

        if r.status_code == 401:
            raise ApiAuthenticationError(r.text)

        elif not r.ok:
            raise ApiGeneralError(r.text)

        self.auth_token = r.json()["access"]

    def get_model_input(self, url, site_design_configuration_id: int):
        if not self.auth_token:
            raise ApiTokenError

        response = requests.get(
            url + str(site_design_configuration_id),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )

        return response.json()

    def get_model_input_fast_track_json(
        self, site_design_configuration_id: int
    ) -> dict:
        url = self.api_urls.GET_MODEL_INPUT_FAST_TRACK
        return self.get_model_input(url, site_design_configuration_id)

    def get_model_input_fast_track(self, site_design_configuration_id: int) -> dict:
        data = self.get_model_input_fast_track_json(site_design_configuration_id)
        return self.json_response_to_df(data)

    def get_model_input_calibrate_fast_track_json(
        self, site_design_configuration_id: int
    ) -> dict:
        url = self.api_urls.GET_MODEL_INPUT_CALIBRATE_FAST_TRACK
        return self.get_model_input(url, site_design_configuration_id)

    def get_model_input_calibrate_fast_track(
        self, site_design_configuration_id: int
    ) -> dict:
        data = self.get_model_input_calibrate_fast_track_json(
            site_design_configuration_id
        )
        return self.json_response_to_df(data)

    def get_model_input_density_analyses_fast_track_json(
        self, site_design_configuration_id: int
    ) -> dict:
        url = self.api_urls.GET_MODEL_INPUT_DENSITY_ANALYSES_FAST_TRACK
        return self.get_model_input(url, site_design_configuration_id)

    def get_model_input_density_analyses_fast_track(
        self, site_design_configuration_id: int
    ) -> dict:
        data = self.get_model_input_density_analyses_fast_track_json(
            site_design_configuration_id
        )
        return self.json_response_to_df(data)

    def json_response_to_df(self, data: dict) -> dict:
        dfs = {}
        for key, val in data.items():
            dfs[key] = pd.json_normalize(val)

        return dfs

    # START LEGACY METHODS --------------------
    # TODO: remove once all fast track instances use new SDK methods
    def get_model_inputs_as_df(self, config_option: int, legacy_parameters=False):

        data = self.get_model_input_as_json(config_option, legacy_parameters)

        site_info = data["site_info"]
        plot_types = data["plot_types"]
        parameter_data = data["parameter_data"]
        parameter_info = data["parameter_info"]
        species_info = data["species_info"]
        model_info = data["model_info"]

        df_sites_info = pd.json_normalize(site_info)
        df_plot_types = pd.json_normalize(plot_types)
        df_parameter_data = pd.json_normalize(parameter_data)
        df_parameter_info = pd.json_normalize(parameter_info)
        df_species_info = pd.json_normalize(species_info)
        df_model_info = pd.json_normalize(model_info)

        return (
            df_sites_info,
            df_plot_types,
            df_parameter_data,
            df_parameter_info,
            df_species_info,
            df_model_info,
        )

    def get_model_input_as_json(self, config_option, legacy_parameters):

        if not self.auth_token:
            raise ApiTokenError

        url = self.api_urls.GET_MODEL_INPUT_URL + str(config_option)

        if legacy_parameters:
            url = url + "?legacy_parameters"

        data = requests.get(
            url,
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )

        return data.json()

    def get_old_model_inputs(self, model_runs: list):
        if not self.auth_token:
            raise ApiTokenError

        list_of_runs = ",".join(map(str, model_runs))
        data = requests.get(
            self.api_urls.GET_OLD_MODEL_INPUT_URL + f"={list_of_runs}",
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )

        sites_info = data.json()["sites_info"]
        parameter_data = data.json()["parameter_data"]
        parameter_info = data.json()["parameter_info"]
        species_info = data.json()["species_info"]
        model_info = data.json()["model_info"]

        df_sites_info = pd.json_normalize(sites_info)
        df_parameter_data = pd.json_normalize(parameter_data)
        df_parameter_info = pd.json_normalize(parameter_info)
        df_species_info = pd.json_normalize(species_info)
        df_model_info = pd.json_normalize(model_info)

        return (
            df_sites_info,
            df_parameter_data,
            df_parameter_info,
            df_species_info,
            df_model_info,
        )

    # END LEGACY METHODS --------------------
