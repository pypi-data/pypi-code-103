from abc import abstractmethod
import io
import os
import tempfile
import zipfile

import requests

STATE_GEOIDS = [
    '01', '02', '04', '05', '06', '08', '09', '10', '11',
    '12', '13', '15', '16', '17', '18', '19', '20', '21',
    '22', '23', '24', '25', '26', '27', '28', '29', '30',
    '31', '32', '33', '34', '35', '36', '37', '38', '39',
    '40', '41', '42', '44', '45', '46', '47', '48', '49',
    '50', '51', '53', '54', '55', '56',
]


class BaseClient:
    area_type = None
    base_url = 'https://www2.census.gov/geo/tiger/TIGER%d/%s'

    def __init__(self, year):
        self.default_year = year

    def get_shapefiles(self, year=None):
        year = year or self.default_year
        url = self._format_url(year)
        files = self._get_files(year)
        for file in files: 
            with zipfile.ZipFile(io.BytesIO(requests.get(os.path.join(url, file)).content)) as zf:
                with tempfile.TemporaryDirectory() as td:
                    zf.extractall(td)
                    yield td

    def _format_url(self, year):
        return self.base_url % (year, self.area_type)

    @abstractmethod
    def _get_files(self, year):
        pass


class StateClient(BaseClient):
    area_type = 'STATE'

    def _get_files(self, year):
        return ['tl_%d_us_state.zip' % year]


class CountyClient(BaseClient):
    area_type = 'COUNTY'

    def _get_files(self, year):
        return ['tl_%d_us_county.zip' % year]


class CityClient(BaseClient):
    area_type = 'COUSUB'

    def _get_files(self, year):
        return [
            'tl_%d_%s_cousub.zip' % (year, state_geoid)
            for state_geoid in STATE_GEOIDS
        ]


class TractClient(BaseClient):
    area_type = 'TRACT'

    def _get_files(self, year):
        return [
            'tl_%d_%s_tract.zip' % (year, state_geoid)
            for state_geoid in STATE_GEOIDS
        ]


class CensusShapefiles:
    def __init__(self, year):
        self.tract = TractClient(year)
        self.city = CityClient(year)
        self.county = CountyClient(year)
        self.state = StateClient(year)
