import copy

from functools import wraps
from kigo.etl.runtime.registry import MappingRegistry


class set_reader:
    def __init__(self, reader, init_values: dict = {}, mappings=None):
        self.reader = reader
        self.init_values = init_values
        if mappings is None:
            self.mappings = []
        else:
            self.mappings = [mapping.__name__ for mapping in mappings] if isinstance(mappings, list) else [mappings.__name__]

    def __call__(self, fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            mappings_copy = copy.deepcopy(MappingRegistry.mappings)

            for mapping_key in MappingRegistry.mappings:
                if self.mappings and mapping_key not in self.mappings:
                    continue
                for reader in MappingRegistry.mappings[mapping_key].readers:
                    if reader[0] == self.reader:
                        MappingRegistry.mappings[mapping_key].readers[MappingRegistry.mappings[mapping_key].readers.index(reader)] = (reader[0], self.init_values)

            try:
                result = fun(*args, **kwargs)
                MappingRegistry.mappings = mappings_copy
                return result
            except Exception as e:
                MappingRegistry.mappings = mappings_copy
                raise e

        return wrapper
