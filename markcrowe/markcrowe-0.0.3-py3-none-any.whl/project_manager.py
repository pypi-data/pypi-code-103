# Copyright (c) 2021 Mark Crowe <https://github.com/markcrowe-com>. All rights reserved.

FILE_PATH = './..'
GITHUB_RAW_QUERY_STRING = '?raw=true'
REPOSITORY_URL = 'https://github.com/markcrowe-com/population-planning-data-analytics/blob/master'


class ProjectArtifactManager:

    def __init__(self, repository_url: str = REPOSITORY_URL, folder: str = FILE_PATH, is_remote: bool = False):
        self.folder = folder
        self.is_remote = is_remote
        self.repository_url = repository_url
        self.query_string = GITHUB_RAW_QUERY_STRING
        self.COUNTY_BIRTHS_EDA_FILENAME = 'artifacts/births-by-county-1985-2020-eda-output.csv'
        self.BIRTHS_DEATHS_MARRIAGES_EDA_FILENAME = 'artifacts/births-deaths-marriages-ireland-1960-2021-eda-output.csv'
        self.REGION_DEATHS_EDA_FILENAME = 'artifacts/deaths-region-2007-2020-eda-output.csv'

    def get_all_eda_filepaths(self, query_string: str = '') -> list:
        query_string_state = self.query_string
        self.query_string = query_string
        filepaths = [self.get_county_births_eda_filepath(),
                     self.get_births_deaths_marriages_eda_filepath(),
                     self.get_region_deaths_eda_filepath()]
        self.query_string = query_string_state
        return filepaths

    def get_county_births_eda_filepath(self) -> str:
        return get_filepath(self.folder, self.repository_url, self.COUNTY_BIRTHS_EDA_FILENAME, self.is_remote, self.query_string)

    def get_births_deaths_marriages_eda_filepath(self) -> str:
        return get_filepath(self.folder, self.repository_url, self.BIRTHS_DEATHS_MARRIAGES_EDA_FILENAME, self.is_remote, self.query_string)

    def get_region_deaths_eda_filepath(self) -> str:
        return get_filepath(self.folder, self.repository_url, self.REGION_DEATHS_EDA_FILENAME, self.is_remote, self.query_string)


class ProjectAssetManager:

    def __init__(self, repository_url: str = REPOSITORY_URL, folder: str = FILE_PATH, is_remote: bool = False):
        self.folder = folder
        self.is_remote = is_remote
        self.repository_url = repository_url
        self.query_string = GITHUB_RAW_QUERY_STRING
        self.COUNTY_BIRTHS_FILENAME = 'assets/births-by-county-1985-2020.csv'
        self.BIRTHS_DEATHS_MARRIAGES_FILENAME = 'assets/births-deaths-marriages-ireland-1960-2021.csv'
        self.REGION_DEATHS_FILENAME = 'assets/deaths-region-2007-2020.csv'

    def get_all_filepaths(self, query_string: str = '') -> list:
        query_string_state = self.query_string
        self.query_string = query_string
        filepaths = [self.get_county_births_filepath(),
                     self.get_births_deaths_marriages_filepath(),
                     self.get_region_deaths_filepath()]
        self.query_string = query_string_state
        return filepaths

    def get_county_births_filepath(self) -> str:
        return get_filepath(self.folder, self.repository_url, self.COUNTY_BIRTHS_FILENAME, self.is_remote, self.query_string)

    def get_births_deaths_marriages_filepath(self) -> str:
        return get_filepath(self.folder, self.repository_url, self.BIRTHS_DEATHS_MARRIAGES_FILENAME, self.is_remote, self.query_string)

    def get_region_deaths_filepath(self) -> str:
        return get_filepath(self.folder, self.repository_url, self.REGION_DEATHS_FILENAME, self.is_remote, self.query_string)


def get_filepath(folder: str, repository_url: str, filename: str, is_remote: bool = True, query_string: str = GITHUB_RAW_QUERY_STRING) -> str:
    if is_remote:
        return f'{repository_url}/{filename}{query_string}'
    else:
        return f'{folder}/{filename}'
