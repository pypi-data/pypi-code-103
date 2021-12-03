#!/usr/bin/env python
# -*-coding:utf-8-*-

import pytest


@pytest.fixture
def sample_config():
    return {'a': 1}


def test_config_read(sample_config):
    assert sample_config['a'] == 1
