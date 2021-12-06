#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import re
from collections import namedtuple
from typing import Dict


class _AttributeAdapter(object):

    def get_field_names_to_attributes(self) -> Dict[str, str]:
        field_names_to_attributes = dict(
            [
                (field_name, getattr(self, field_name)) for field_name in dir(self)
                  if not field_name.startswith('__')
                  and not field_name.startswith('_')
                  and not callable(getattr(self, field_name))
            ]
        )

        if 'datasetId' not in field_names_to_attributes and \
                'dataset_id' in field_names_to_attributes:
            # DL-6445: For backwards compatibility re-add the old attribute name.
            field_names_to_attributes['datasetId'] = field_names_to_attributes['dataset_id']

        return field_names_to_attributes

    @staticmethod
    def __fun(clazz, field_name) -> str:
        return field_name + "='" + str(getattr(clazz, field_name)) + "'"

    def __str__(self):
        sanitised_fields = [self.__fun(self, field_name) for field_name in dir(self) if
                 not field_name.startswith('__') and not field_name.startswith(
                     '_') and not callable(getattr(self, field_name))]

        fields_str: str = ", ".join(sanitised_fields)
        return f"{self.__class__.__name__}({fields_str})"

    def as_dict(self):
        return self.get_field_names_to_attributes()

    def _asdict(self):
        # Support alternative spelling.
        return self.as_dict()


def to_camel_case(snake_str):
    split = snake_str.split('_')
    camel_case_parts = [split[0].lower()] + [s.title() for s in split[1:]]
    return ''.join(camel_case_parts)


def to_camel_cased_dict(dictionary):
    return {to_camel_case(key): value for (key, value) in dictionary.items()}


def to_snake_case(s):
    # need to sanitise the string as in some cases the key might look like
    # 'Data Access' with a space.
    _reg = re.compile(r'(?!^)(?<!_)([A-Z])')
    return _reg.sub(r'_\1', s.replace(' ', '_')).lower()


def object_to_namedtuple(obj):
    e = obj.as_dict()
    namedtuple_obj = namedtuple(obj.__class__.__name__, sorted(e.keys()))(**e)
    return namedtuple_obj


def to_snake_case_keys(dictionary: dict):
    dictionary_snake_case = {to_snake_case(key): value for (key, value) in dictionary.items()}
    return dictionary_snake_case