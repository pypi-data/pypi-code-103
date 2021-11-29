import json
import os

import pytest
from _pytest.config import Config
from pytest_testrail_api_client import test_rail
from pytest_testrail_api_client.client_config import TR_PREFIX, SECTIONS_SEPARATOR, MAIN_CASE_TEMPLATE_NAME, SKIP_FIELDS
from pytest_testrail_api_client.modules.case import Case
from pytest_testrail_api_client.modules.classes import Suite
from pytest_testrail_api_client.modules.exceptions import TestRailError
from pytest_testrail_api_client.modules.plan import Run
from pytest_testrail_api_client.modules.session import Session
from pytest_testrail_api_client.service import is_main_loop, trim, replace_examples, get_features, _write_feature, \
    sort_configurations
from pytest_testrail_api_client.validate import validate_plan_id, validate_configs


def pytest_addoption(parser):
    group = parser.getgroup("pytest-rail")
    group.addoption('--pytest-testrail-export-test-results', action='store_true', default=False)
    group.addoption('--pytest-testrail-test-plan-id', action='store')
    group.addoption('--pytest-testrail-test-configuration-name', action='store')

    group.addoption("--pytest-testrail-export-test-cases", action="store_true")
    group.addoption("--pytest-testrail-feature-files-relative-path", action="store", default=None)


def pytest_configure(config: Config):
    pytest.test_rail = test_rail.TestRail()
    file_name = Session.get_results_file(config)
    if os.path.isfile(file_name):
        os.remove(file_name)


def pytest_collection_modifyitems(config: Config, items):
    if config.getoption('pytest_testrail_export_test_results', default=None) is True:
        validate_plan_id(config.getoption('pytest_testrail_test_plan_id'), pytest.test_rail)
        validate_configs(config.getoption('pytest_testrail_test_configuration_name'), pytest.test_rail)
    if config.getoption('pytest_testrail_export_test_cases', default=None) is True:
        config.option.markexpr = 'not not_in_scope'
        print('\nUn-select all tests. Exporting is selected')
        abs_path = os.path.join(config.rootdir, config.getoption('pytest_testrail_feature_files_relative_path'))
        features = get_features(abs_path, pytest.test_rail)
        cases_list = {suite: pytest.test_rail.cases.get_cases(suite_id=suite) for suite
                      in set(feature.main_suite for feature in features)}
        template_id = next((template.id for template in pytest.test_rail.templates.get_templates()
                            if template.name == MAIN_CASE_TEMPLATE_NAME), None)
        total_tests, current_test = sum((len(x.children) for x in features)), 1
        for feature in features:
            for scenario in feature.children:
                sc = scenario['scenario']
                case = {
                    'section_id': feature.last_section,
                    'title': sc['name'],
                    'custom_steps_separated': sc['steps'],
                    'estimate': '5m',
                    'template_id': template_id,
                    **sc['custom_fields']
                }
                if 'priority' in sc:
                    case.update({'priority_id': sc['priority']})
                if 'types' in sc:
                    case.update({'type_id': sc['types'][0]})
                for field in SKIP_FIELDS:
                    if field in case:
                        case.pop(field)
                tr_case = next(filter(lambda x: trim(x.title) == sc['name'], cases_list[feature.main_suite]), None)
                current_scenario = Case(case)
                txt = f'scenario {current_scenario.title} in feature {feature.path}. {current_test} of {total_tests}'
                if tr_case is not None:
                    if current_scenario.is_equal(tr_case):
                        print(f'Can\'t find any changes in {txt}')
                    else:
                        case.update({'case_id': tr_case.id})
                        case = pytest.test_rail.cases.update_case(**case)
                        if not any((tag['name'].startswith(TR_PREFIX) for tag in sc['tags'])):
                            location = sc['tags'][0]['location']
                            _write_feature(feature.path, location['line'], location['column'] - 1,
                                           TR_PREFIX + str(case.id))
                        if isinstance(case, str):
                            print(f'{txt}. Error {case}')
                        else:
                            print(f'Updated {txt}')
                else:
                    new_case = pytest.test_rail.cases.add_case(**case)
                    if isinstance(new_case, str):
                        print(f'{txt}. Error {new_case}')
                    else:
                        print(f'Upload new {txt}')
                        location = sc['tags'][0]['location']
                        _write_feature(feature.path, location['line'], location['column'] - 1,
                                       TR_PREFIX + str(new_case.id))
                current_test += 1
        for item in items:
            item.add_marker(pytest.mark.not_in_scope)


@pytest.hookimpl(tryfirst=True)
def pytest_bdd_after_scenario(request, feature, scenario):
    if request.config.getoption('pytest_testrail_export_test_results', default=None) is True:
        suite_name = feature.name.split(SECTIONS_SEPARATOR, maxsplit=1)[0]
        test_name, examples = request.node.name, scenario.examples.example_params
        test_examples, steps = test_name.split('[')[-1].replace(']', ''), []
        main_name = replace_examples(scenario.name, examples, test_examples, scenario.examples.examples)
        for step in scenario.steps:
            step_name = replace_examples(step.name, examples, test_examples, scenario.examples.examples)
            step_result = get_status_number(step.failed)
            data = {
                'content': f'**{step.keyword}:**{step_name}',
                'status_id': step_result,
                'actual': str(step.exception) if step.failed else ''
            }
            steps.append(data)
        main_result = {
            'name': main_name,
            'status_id': get_status_number(scenario.failed),
            'custom_step_results': steps
        }
        write_to_file(request, main_result, suite_name)


def pytest_sessionfinish(session):
    if session.config.getoption('pytest_testrail_export_test_results', default=None) is True:
        if is_main_loop(session):
            print('Start publishing results')
            error_message, suites = [], dict()
            tr: test_rail.TestRail = pytest.test_rail
            for result_file in tr.get_results_files():
                with open(result_file, 'r') as file:
                    for key, value in json.loads(file.read()).items():
                        if key in suites:
                            suites[key] += value
                        else:
                            suites.update({key: value})
                os.remove(result_file)
            plan_id = session.config.option.pytest_testrail_test_plan_id
            config = sort_configurations(session.config.option.pytest_testrail_test_configuration_name, tr)
            plan, suites_list = tr.plans.get_plan(plan_id), tr.suites.get_suites()
            results = []
            for suite, results_list in suites.items():
                run_to_add = plan.get_run_from_entry_name_and_config(suite, config)
                suite_id = tr.service.get_suite_by_name(suite, suites_list)
                if isinstance(suite_id, Suite):
                    if run_to_add is None:
                        run_to_add = add_entry_to_plan(plan_id, suite_id.id, suite, config)
                    tr.plans.update_run_in_plan_entry(run_to_add.id, include_all=True)
                    tests_list = tr.tests.get_tests(run_to_add.id)
                    for index, test_in_list in enumerate(tests_list):
                        tests_list[index].title = trim(tests_list[index].title)
                    for result in results_list:
                        result_test = [test.id for test in tests_list if test.title == trim(result['name'])]
                        if len(result_test) == 0:
                            error_message.append(f'Can\'t find scenario {result["name"]}')
                        else:
                            result.update({'test_id': result_test[0]})
                            results.append(result)
                    tr.results.add_results(run_id=run_to_add.id, results=results)
                    tr.service.delete_untested_tests_from_run(run_to_add.id)
            if len(error_message) > 0:
                print('\n'.join(error_message))
            print('Results published')


def add_entry_to_plan(plan_id: int, suite_id: int, name: str, config: list) -> Run:
    tr: test_rail.TestRail = pytest.test_rail
    config_ids = tr.service.convert_configs_to_ids(config)
    runs = [{'include_all': True, 'config_ids': config_ids}]
    entry = tr.plans.add_plan_entry(
        plan_id, suite_id, name=name, config_ids=config_ids, include_all=True, runs=runs)
    if not isinstance(entry, str):
        return entry.runs[0]
    else:
        raise TestRailError(entry)


def get_status_number(status):
    return {True: 5, False: 1, None: 2}.get(status, 3)


def write_to_file(request, result: dict, suite_name: str):
    file_path = Session.get_results_file(request)
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as file:
            file.write(json.dumps({suite_name: [result]}))
    else:
        with open(file_path, 'r+') as file:
            data = json.loads(file.read())
            if suite_name not in data:
                data[suite_name] = [result]
            else:
                data[suite_name].append(result)
            file.seek(0)
            json.dump(data, file)


def pytest_bdd_step_error(scenario, step, exception):
    _step_error(exception, scenario, step)


def pytest_bdd_step_validation_error(scenario, step, exception):
    _step_error(exception, scenario, step)


def pytest_bdd_step_func_lookup_error(scenario, step, exception):
    _step_error(exception, scenario, step)


def _step_error(exception, scenario, step):
    scenario.exception = exception
    scenario.failed = True
    is_blocked = False
    for scenario_step in scenario.steps:
        scenario_step.failed = None if is_blocked else False
        if scenario_step == step:
            scenario_step.exception = exception
            scenario_step.failed = True
            is_blocked = True
    exception_message = exception.msg if hasattr(exception, 'msg') \
        else exception.message if hasattr(exception, 'message') \
        else exception.args[0] if hasattr(exception, 'args') and exception.args.__len__() > 0 \
        else 'no error message'
    scenario.exception_message = exception_message
