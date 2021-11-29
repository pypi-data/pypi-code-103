import os
from copy import deepcopy
from datetime import datetime
from itertools import chain
from typing import List, Union

from _pytest.config import Config
from _pytest.main import Session
from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

from pytest_testrail_api_client.client_config import PRIORITY_REPLACE, VALIDATE_FEATURES
from pytest_testrail_api_client.modules.bdd_classes import TrFeature
from pytest_testrail_api_client.modules.exceptions import MissingSuiteInFeature, ValidationError
from pytest_testrail_api_client.validate import validate_scenario_tags


def get_dict_from_locals(locals_dict: dict, replace_underscore: bool = False, exclude: list = None):
    exclude = ('self', 'kwargs') if exclude is None else tuple(['self', 'kwargs'] + exclude)
    result = {key if replace_underscore else key: value for key, value in
              locals_dict.items() if key not in exclude and '__py' not in key and value is not None}
    if 'kwargs' in locals_dict:
        result.update(locals_dict['kwargs'])
    return result


def split_by_coma(*args):
    def sub_split(value):
        if value is not None:
            if not isinstance(value, (tuple, list)):
                value = trim(value).split(', ')
            return value

    if all([arg is None for arg in args]):
        return None
    elif len(args) > 1:
        return [sub_split(val) for val in args]
    else:
        return args[0].replace(' ', '').split(',') if not isinstance(args[0], (tuple, list)) else args[0]


def validate_id(status_id):
    if status_id is not None:
        if isinstance(status_id, (list, tuple)):
            return ','.join(tuple(map(str, status_id)))
        elif isinstance(status_id, str):
            return status_id.replace(' ', '')


def get_date_from_timestamp(date):
    return None if date is None else datetime.fromtimestamp(date)


def is_main_loop(session: (Session, Config)):
    if isinstance(session, Session):
        if not hasattr(session.config, 'workerinput'):
            return True
        else:
            return session.config.option.dist != "no"
    else:
        if not hasattr(session, 'workerinput'):
            return True
        else:
            return session.option.dist != "no"


def get_worker_id(config):
    if hasattr(config, 'config'):
        config = config.config
    return config.workerinput['workerid'] if hasattr(config, 'workerinput') else 'main'


def trim(string: str) -> str:
    return ' '.join(string.split())


def get_features(path: str, test_rail):
    if path.split('.')[-1] == 'feature':
        feature_files = [path]
    else:
        feature_files = tuple(f"{root}/{file}" for root, dirs, files in os.walk(path, topdown=False)
                              for file in files if file.split('.')[-1] == 'feature')
    feature_files = tuple(get_feature(feature_file) for feature_file in feature_files)
    if VALIDATE_FEATURES is True:
        errors = tuple(chain.from_iterable(validate_scenario_tags(feature) for feature in feature_files))
        if len(errors) > 0:
            raise ValidationError('\n'.join(errors))
    features = []
    suites_list = test_rail.suites.get_suites()
    custom_tags = test_rail.case_fields._service_case_fields()
    case_types = test_rail.case_types._service_case_types()
    priority_list = test_rail.priorities._service_priorities()
    sections = {suite.id: test_rail.sections.get_sections(suite.id) for suite in suites_list}
    for feature in feature_files:
        parsed_feature = parse_feature(feature)
        for scenario in parsed_feature.children:
            tags = list(tag['name'].lower().replace('@', '') for tag in scenario['scenario']['tags'])
            scenario['scenario']['custom_fields'], scenario['scenario']['types'], scenario['scenario']['priority'] = \
                _get_case_options(tags, custom_tags, case_types, priority_list)

        suite_id = next((suite.id for suite in suites_list if parsed_feature.main_suite == suite.name), None)
        if suite_id is not None:
            parsed_feature.main_suite = suite_id
            parent_id = None
            for section in parsed_feature.sections:
                tr_section = next((sn for sn in sections[suite_id] if sn.name == section and sn.parent_id == parent_id),
                                  None)
                if tr_section is None:
                    parent_id = test_rail.sections.add_section(section, suite_id=suite_id, parent_id=parent_id).id
                else:
                    parent_id = tr_section.id
            parsed_feature.last_section = parent_id
        else:
            raise MissingSuiteInFeature(f'Missing suite in {feature}')
        parsed_feature.children = sorted(parsed_feature.children, key=lambda scen: scen['scenario']['location']['line'])
        features.append(parsed_feature)
    return features


def parse_feature(feature):
    examples_scenarios, to_delete = [], []
    for scenario in feature.children:
        if len(scenario['scenario']['examples']) > 0:
            examples = scenario['scenario']['examples'][0]
            examples_names = tuple(var_name['value'] for var_name in examples['tableHeader']['cells'])
            examples_values = []
            for var in tuple(var['cells'] for var in examples['tableBody']):
                examples_values.append([y['value'] for y in var])
            for example in examples_values:
                sc = deepcopy(scenario)
                for index, name in enumerate(examples_names):
                    sc['scenario']['name'] = sc['scenario']['name'].replace(f'<{name}>', example[index])
                    for step in sc['scenario']['steps']:
                        if step.get('content', None) is None:
                            step['content'] = step['text']
                        step['content'] = step['content'].replace(f'<{name}>', example[index])
                examples_scenarios.append(sc)
            to_delete.append(scenario)
    for scenario in to_delete:
        feature.children.remove(scenario)
    for scenario in examples_scenarios:
        feature.children.append(scenario)
    return feature


def get_feature(file_path: str) -> list:
    with open(file_path, "r") as file:
        return TrFeature(Parser().parse(TokenScanner(file.read()))['feature'], file_path)


def _make_step(step: dict) -> str:
    return {'content': f'**{step["keyword"].replace(" ", "")}:**{trim(step["text"])}', 'expected': ''}


def _get_case_options(case_tags: list, tr_tags: dict, tr_case_types: dict, tr_priority: dict):
    custom_fields, cases_type, priority = dict(), [], None
    for key, value in tr_tags.items():
        if key in case_tags:
            if value['type'] == 'multi_select':
                if value['name'] in custom_fields:
                    custom_fields[value['name']].append(int(value['id']))
                else:
                    custom_fields[value['name']] = [int(value['id'])]
            elif value['type'] in ('integer', 'dropdown'):
                custom_fields[value['name']] = int(value['id'])
            else:
                custom_fields[value['name']] = value['id']
    for key, value in PRIORITY_REPLACE.items():
        for val in value:
            if val.lower() in case_tags:
                priority = tr_priority[key.lower()]
                break
    if priority is None:
        priority = tr_priority['low']
    for key, value in tr_case_types.items():
        if key in case_tags and key not in tr_tags:
            cases_type.append(value), case_tags.remove(key)

    return custom_fields, cases_type, priority


def replace_examples(where: str, examples: list, variables: str, all_vars: list):
    current_vars, variables = [], variables.lower()
    for var in all_vars:
        if all((x.lower() in variables for x in var)):
            current_vars = var
            break
    for index, param in enumerate(examples):
        if len(current_vars) > index:
            where = where.replace(f'<{param}>', current_vars[index])
    return where


def to_json(obj_list: List[object]) -> dict:
    return tuple(obj.to_json() if 'to_json' in dir(obj) else obj.__dict__ for obj in obj_list)


def split_list(array: List[Union[tuple, list]], separator: int = 250) -> list:
    if isinstance(array, (tuple, list)):
        if isinstance(separator, int):
            if len(array) > 0:
                result, index = [], 0
                while True:
                    result.append(array[index:index + separator])
                    index += separator
                    if index > len(array):
                        break
                return result
            else:
                return []
        else:
            raise ValueError('separator must be integer')
    else:
        raise ValueError('array variable must be tuple or list')


def validate_variable(variable, var_types, var_name: str):
    if not isinstance(variable, var_types):
        raise ValueError(f'{var_name} must be {var_types}')


def _write_feature(file_path: str, line: int, column: int, value: str) -> None:
    def count_symbols(to_line: str, arr: list) -> int:
        return sum((len(length.encode()) for length in arr[:to_line]))

    with open(file_path, 'r+') as file:
        lines = file.readlines()
        symbols_count = count_symbols(line - 1, lines) + column
        file.seek(symbols_count)
        rem = file.read()
        file.seek(symbols_count)
        file.write(f'{value} {rem}')


def sort_configurations(configuration: str, tr) -> str:
    config_split, config = trim(configuration).split(', '), []
    for param in tr.configs.get_configs():
        for suite in config_split:
            if suite.lower() in [conf.name.lower() for conf in param.configs]:
                config.append(suite)
    return ', '.join(config)
