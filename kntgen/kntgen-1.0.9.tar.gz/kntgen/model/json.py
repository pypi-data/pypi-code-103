import json
from collections import OrderedDict
from typing import List

from jinja2 import Environment, PackageLoader

from kntgen.collection_helpers import merged_non_empty
from kntgen.constants import *
from kntgen.str_helpers import *


class JSON(object):
    IMPORT_HEADER = 'import \'package:json_annotation/json_annotation.dart\';\n'

    class Property(object):
        def __init__(self, raw_name: str, name: str, type_name: str):
            self.raw_name = raw_name
            self.name = name
            self.type_name = type_name

        def __eq__(self, other):
            return isinstance(other, __class__) \
                   and other.raw_name == self.raw_name \
                   and other.name == self.name \
                   and other.type_name == self.type_name

        def __hash__(self):
            return id(f'{self.raw_name}_{self.name}_{self.type_name}')

        @property
        def is_user_type(self):
            return self.is_optional \
                   and self.original_type_name not in DART_TYPES_DEFAULT_VALUES

        @property
        def is_optional(self):
            return self.type_name.endswith('?')

        @property
        def is_list(self):
            return self.type_name.startswith('List')

        @property
        def is_array(self):
            return self.type_name.startswith('[')

        @property
        def is_date(self):
            return self.original_type_name == 'DateTime'

        @property
        def is_dart_type(self):
            return self.type_name in DART_TYPES_DEFAULT_VALUES

        @property
        def original_type_name(self):
            origin_name = self.type_name
            if self.is_list:
                origin_name = origin_name.removeprefix('List')
            return ''.join(c for c in origin_name if c not in '?[]<>')

        @property
        def value(self):
            if self.is_optional:
                value = 'null'
            elif self.is_array or self.is_list:
                value = 'const []'
            elif self.type_name in DART_TYPES_DEFAULT_VALUES:
                value = DART_TYPES_DEFAULT_VALUES[self.type_name]
            else:
                value = 'null'
            if self.type_name.startswith('String'):
                value = f'{value!r}'
            return value

    class Model(object):
        def __init__(self, name: str,
                     properties: set = None):
            self.name = name
            self.properties = properties or {}
            self.env = Environment(
                loader=PackageLoader('kntgen_templates', 'json_to_dart'),
                trim_blocks=True,
                lstrip_blocks=True
            )

        def __eq__(self, other):
            return isinstance(other, __class__) and other.name == self.name

        def __hash__(self):
            return id(f'{self.name}_{len(self.properties)}')

        def create_file_from_template(self):
            template = self.env.get_template('json.dart')
            content = template.render(
                model_name=self.name,
                properties=self.properties
            )
            return content

    def __init__(self, model_name: str, json_str: str):
        self.model_name = model_name
        self.json_str = json_str

    def create_model_files(self):
        models = list(
            reversed(JSON._remove_duplicated_models(self._create_models())))
        model_name_snake_case = to_snake_case(self.model_name)
        import_part = f'\npart \'{model_name_snake_case}.g.dart\';\n'
        output = '\n'.join(
            [model.create_file_from_template() for model in models]
        )
        output = JSON.IMPORT_HEADER + import_part + output + '\n'
        return output

    def _create_models(self):
        try:
            dictionary = json.loads(self.json_str,
                                    object_pairs_hook=OrderedDict)
            models = []
            self._extract_to_dart_model(self.model_name, dictionary, models)
            return models
        except Exception as e:
            print(f'The JSON is invalid! {e.__repr__()}')
            exit(1)

    def _extract_to_dart_model(self,
                               model_name: str,
                               dictionary: dict,
                               models: List[Model]):
        properties = []
        if type(dictionary).__name__ == 'list':
            if len(dictionary) > 0:
                if type(dictionary[0]).__name__ == 'OrderedDict':
                    most_key_dict = dictionary[0]
                    # Join all JSON object to find all properties
                    for sub_dict in dictionary[1:]:
                        most_key_dict = merged_non_empty(
                            most_key_dict,
                            sub_dict
                        )
                    self._extract_to_dart_model(
                        model_name,
                        most_key_dict,
                        models
                    )
            return
        for key, value in dictionary.items():
            var_name = snake_to_camel(key)
            type_name = type(value).__name__
            if type_name == 'OrderedDict':
                var_type = snake_to_pascal(key)
                self._extract_to_dart_model(var_type, value, models)
            elif type_name == 'list':
                singular_var_name = plural_to_singular(var_name)
                if len(value) > 0:
                    sub_var_type = type(value[0]).__name__
                    if sub_var_type == 'OrderedDict':
                        most_key_dict = value[0]
                        # Join all JSON object to find all properties
                        for sub_dict in value[1:]:
                            most_key_dict = merged_non_empty(
                                most_key_dict,
                                sub_dict
                            )
                        var_type = f'List<{singular_var_name.title()}?>'
                        self._extract_to_dart_model(
                            singular_var_name.title(),
                            most_key_dict,
                            models
                        )
                    else:
                        var_type = f'List<{PYTHON_TO_DART_TYPES[sub_var_type]}?>'
                else:
                    var_type = 'List'
            else:
                var_type = PYTHON_TO_DART_TYPES[type_name]
                if var_type == 'String':
                    if re.match(DATE_REGEX, value):
                        var_type = 'DateTime?'
                if var_type == 'dynamic':
                    lower_var_name = var_name.lower()
                    # Filter return type with preset common name
                    if lower_var_name.endswith('url') \
                            or lower_var_name.endswith('key') \
                            or lower_var_name.endswith('token') \
                            or 'name' in lower_var_name \
                            or 'email' in lower_var_name:
                        var_type = 'String'
                    elif lower_var_name.endswith('at') \
                            or 'time' in lower_var_name \
                            or 'date' in lower_var_name \
                            or 'birthday' in lower_var_name:
                        var_type = 'DateTime?'
                    elif lower_var_name.endswith('id'):
                        var_type = 'num'
            if var_type not in DART_TYPES_DEFAULT_VALUES \
                    and not var_type.startswith('List'):
                var_type = var_type + '?'
            json_property = JSON.Property(key, var_name, var_type)
            properties.append(json_property)
        model = JSON.Model(model_name, properties)
        models.append(model)

    @staticmethod
    def _remove_duplicated_models(models: list[Model]):
        not_dup_models = []
        total_models = len(models)
        for i in range(total_models):
            model = models[i]
            if model in not_dup_models:
                continue

            for j in range(i + 1, total_models):
                if model == models[j]:
                    # Supplement lacked properties from duplicated models
                    # into existed model
                    model.properties = list(
                        set(model.properties) | set(models[j].properties))

            not_dup_models.append(models[i])
        return not_dup_models
