from typing import Dict, Union, List

from enginelib.errors import Error
from enginelib.rds.client import db_client, db_name


class ICD10:
    def __init__(self):
        self.icd10_hash: Dict[str, str] = dict()

    def __contains__(self, code: str) -> bool:
        return self.is_valid(code)

    def description(self, code: str) -> str:
        if code not in self.icd10_hash:
            self.icd10_hash[code] = self._fetch_description(code)

        return self.icd10_hash[code]

    @staticmethod
    def _fetch_description(code: str) -> str:
        """If 'code' is in the ICD10 dataset, and if the DB query was successful,
        this function returns a non-zero length description of the given ICD10 code.
        If the DB query was not successful, this function raises a DataError.
        If the DB query was successful, but the code was not in the DB, this
        function returns an empty string."""

        # noinspection SqlResolve
        query = f'''
        SELECT "description" 
        FROM {db_name}.icd10
        WHERE "code"='{code}';
        '''
        ref_data, err = db_client.GetReferenceData("multi_policy_prefilter", query)
        if err:
            raise Error(f'Not able to access ICD10 reference data: {err}.')
        try:
            if ref_data is None or not isinstance(ref_data, list) or len(ref_data) == 0:
                return ''
            return ref_data[0]['description'].strip('"')
        except (IndexError, KeyError, TypeError):
            raise Error(f'Not able to access ICD10 reference data to fetch description for code {code}.')

    def is_valid(self, code: str) -> bool:
        description = self.description(code)
        return description != ''

    def in_range(self, code: str, icd10_min: str, icd10_max: str) -> bool:
        """The comparison below is alphanumeric (i.e. string)."""
        return icd10_min <= code <= icd10_max and self.is_valid(code)


class ICD10Range:
    """Represents a range of ICD10 codes without actually storing all of the
    codes in the range. The range is represented by the `max` and `min`
    codes in the range."""
    def __init__(self, code_min: str, code_max: str):
        self.icd10 = ICD10()
        self.code_min = code_min
        self.code_max = code_max

    def __contains__(self, code: str) -> bool:
        return self.icd10.in_range(code, self.code_min, self.code_max)


class ICD10Collection:
    """Stores a collection of individual ICD10 codes and/or ICD10 ranges."""
    def __init__(self):
        self._hash: Dict[str, bool] = dict()
        self._ranges: List[ICD10Range] = list()
        super().__init__()

    def add(self, obj: Union[str, ICD10Range]):
        if isinstance(obj, str):
            self._hash[obj] = True
        else:
            self._ranges.append(obj)

    def __contains__(self, code: str) -> bool:
        if code in self._hash:
            return True
        for _range in self._ranges:
            if code in _range:
                return True
        return False

    @classmethod
    def construct(cls, icd_list_of_codes_and_ranges: str) -> 'ICD10Collection':
        # Split given list using comma or pipe as a separator
        normalized_icd_list = icd_list_of_codes_and_ranges.replace(',', '|')
        items = [item.strip() for item in normalized_icd_list.split('|')]

        icd10_collection = ICD10Collection()
        for item in items:
            if '-' in item:
                try:
                    code_min, code_max = [code.strip() for code in item.split('-')]
                except ValueError:
                    raise Error(f'The entry {item} is a malformed range of ICD10 codes.')
                icd10_collection.add(ICD10Range(code_min, code_max))
            else:
                icd10_collection.add(item)

        return icd10_collection
