# pylint: skip-file
import os

import ioc.loader
import pytest
from fastapi.testclient import TestClient

from unimatrix.ext.webapi import Service


@pytest.fixture(scope='function')
def asgi():
    application = Service(
        enable_debug_endpoints=True
    )
    return TestClient(application)
