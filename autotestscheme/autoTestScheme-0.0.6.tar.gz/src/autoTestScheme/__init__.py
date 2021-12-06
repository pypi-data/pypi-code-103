# -*- coding: utf-8 -*-
from .common import start_data
from ._version import __version__

import os

import pytest
from _pytest.compat import NotSetType

from .common import constant, config as config1, logger, common, tmp
from .run import json_name


def pytest_addoption(parser):
    group = parser.getgroup(json_name, "distributed and subprocess testing")
    group.addoption(
        "--{}".format(json_name),
        action="store",
        help=(
            "provide an identifier shared amongst all workers as the value of "
            "the 'testrun_uid' fixture,\n\n,"
            "if not provided, 'testrun_uid' is filled with a new unique string "
            "on every test run."
        ),
    )



@common.singleton
class A(object):
    run_data = {}


a = A()


def pytest_configure(config):
    uuid = config.option.autoTestScheme
    if uuid is not None:
        _path = os.path.join(constant.RUN_TMP_DIR, uuid, 'case.json')
        a.run_data = config1.Json(_path).get_object()
        start_data.TEST_ENV = a.run_data.get('__env')


def pytest_generate_tests(metafunc):
    _file = os.path.basename(metafunc.module.__file__).replace('.py', '')
    _func = metafunc.function.__name__
    start_data.TEST_ENV = a.run_data.get('__env')
    if 'filename' in dir(metafunc.cls):
        _file = metafunc.cls.filename
    if 'data' in metafunc.fixturenames and _file in list(a.run_data.keys()) \
            and _func in list(a.run_data[_file].keys()):
        data = a.run_data[_file][_func]
        _data = []
        for i in range(len(data)):
            _data.append(pytest.param(data[i], marks=pytest.mark.run(order=data[i]['__order'])))
        metafunc.parametrize("data", _data)
    else:
        metafunc.parametrize("data", [])


def pytest_runtest_setup(item):
    param = item.callspec.params.get('data')
    if param != NotSetType.token:
        _id = param.get('id')
        last = param.get('dependent')
        if param.get('last_dependent') is not None:
            last = param.get('last')
        if last is not None:
            item.callspec.params['data']['lastTmp'] = tmp.tmp.get_lastTmp(last)
            item.callspec.params['data']['dpTmp'] = tmp.tmp.get(last)
        if _id is not None:
            tmp.tmp.append_lastTmp(param.get('id'), param.get('ins'))

        logger.info('开始运行用例:{}'.format(param.get('title')))
        logger.info(item.callspec.params.get('data'))
