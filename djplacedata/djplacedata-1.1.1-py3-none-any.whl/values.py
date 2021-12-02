from abc import ABC, abstractmethod

from census import Census
from sodapy import Socrata

from .models import Place
from .settings import CENSUS_API_KEY, SODA_APP_TOKEN


class BaseValue(ABC):
    @property
    @abstractmethod
    def fields(self):
        pass

    @abstractmethod
    def get_value_from_result(self, result):
        pass


class Value(BaseValue):
    def __init__(self, input_field):
        self._input_field = input_field

    @property
    def fields(self):
        return [self._input_field,]

    def get_value_from_result(self, result):
        return result[self._input_field]


class ComputedValue(BaseValue):
    def __init__(self, input_field0,  operator, input_field1):
        self._input_field0 = input_field0
        self._operator = operator
        self._input_field1 = input_field1

    @property
    def fields(self):
        return [self._input_field0, self._input_field1,]

    def get_value_from_result(self, result):
        try:
            value = eval(f'{result[self._input_field0]}{self._operator}{result[self._input_field1]}')
            return value
        except:
            return None


class BaseValues(ABC):
    def __init__(self, **fields):
        self.fields = fields

    @property
    def results(self):
        for place, result in self.query():
            values = {}
            for name, value in self.fields.items():
                values[name] = value.get_value_from_result(result)
            yield place, values

    @property
    def queryable_fields(self):
        values = []
        for field in self.fields.values():
            values += field.fields
        return values

    @abstractmethod
    def query(self):
        pass


_STATE_GEOIDS = [
    '01', '02', '04', '05', '06', '08', '09', '10', '11',
    '12', '13', '15', '16', '17', '18', '19', '20', '21',
    '22', '23', '24', '25', '26', '27', '28', '29', '30',
    '31', '32', '33', '34', '35', '36', '37', '38', '39',
    '40', '41', '42', '44', '45', '46', '47', '48', '49',
    '50', '51', '53', '54', '55', '56',
]


class CensusValues(BaseValues):
    STATE_GEOIDS = _STATE_GEOIDS

    def __init__(self, dataset, year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        census = Census(CENSUS_API_KEY, year=year)
        self.client = getattr(census, dataset)

    def query(self):
        results = [
            (Place.objects.get(geoid=result['state']), result)
            for result in self.client.get(self.queryable_fields, {'for': 'state:*'})
        ]
        results += [
            (Place.objects.get(geoid=result['state'] + result['county']), result)
            for result in self.client.get(self.queryable_fields, {'for': 'county:*'})
        ]
        for state_geoid in self.STATE_GEOIDS:
            results += [
                (
                    Place.objects.get(geoid=result['state'] + result['county'] + result['county subdivision']),
                    result
                )
                for result in
                self.client.get(self.queryable_fields, {'for': 'county subdivision:*', 'in': 'state:%s' % state_geoid})
            ]
            results += [
                (
                    Place.objects.get(geoid=result['state'] + result['county'] + result['tract']),
                    result
                )
                for result in self.client.get(self.queryable_fields, {'for': 'tract:*', 'in': 'state:%s' % state_geoid})
            ]
        return results



class SodaAPIValues(BaseValues):
    def __init__(self, domain, dataset, filters, get_place, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Socrata(
            domain,
            SODA_APP_TOKEN
        )
        self.dataset = dataset
        self.filters = filters
        self.get_place = get_place

    def query(self):
        results = []
        for data in self.client.get(self.dataset, **self.filters):
            place = self.get_place(data)
            if place is None:
                continue
            results.append((place, data))
        return results
