"""
General functionallity tests
"""
import json
import os
from pprint import pprint

import pytest

from superwise import Superwise
from superwise.controller.exceptions import *
from superwise.models.task import Task
from tests import get_sw
from tests import print_results
from tests.conf.config import config


@pytest.mark.vcr()
def test_load_superwise_login_user_password():
    ok = True
    try:
        email = config.get("EMAIL", "email")
        password = config.get("PASSWORD", "email")
        print("login with {} and pass {}".format(email, password))
        sw = Superwise(email=email, password=password)
    except:
        ok = False
    assert ok is True


@pytest.mark.vcr()
def test_load_superwise_object_login():
    ok = True
    try:
        sw = Superwise(client_id=config["CLIENT_ID"], secret=config["SECRET"])
    except Exception as e:
        print(e)
        print("remnoivew vasdvasdvas")
        ok = False
    assert ok is True


@pytest.mark.vcr()
def test_invalid_token():
    ok = False
    try:
        sw = Superwise(client_id="test", secret="test_fail")
    except SuperwiseAuthException:
        ok = True
    assert ok is True


@pytest.mark.vcr()
def test_send_wrong_sdkmodel():
    sw = get_sw()
    model = Task()
    ok = False
    try:
        sw.version.create(model)
    except Exception as e:
        ok = True
    assert ok is True
