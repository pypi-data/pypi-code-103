#!/usr/bin/env python
# -*-coding:utf-8-*-

import pytest


@pytest.fixture
def sample_config():
    return {'a': 1}
