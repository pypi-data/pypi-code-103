# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import string
import pytest
import pathlib

from . import models
from . import create_app
from .models import db

#from .tests.loaders import 
    

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_uri = 'sqlite:///:memory:'

    # create the app with common test config
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': db_uri,
        'SECURITY_PASSWORD_SALT': 'some_random_stuff',
        'SECRET_KEY': 'some_test_key'

    }, use_sentry=False)

    yield app


@pytest.fixture(scope="session")
def init_db(app):
    # create the database and load test data
    db.create_all(app=app)
    yield app


@pytest.fixture(scope="session")
def app_config(app, init_db):
    # Load the config file with initial setup
    config_file = pathlib.Path(__file__).parent / 'tests' / 'config' / 'test_config.yml'
    from .util.helpers import load_config_file
    load_config_file(app, config_file, silent=True)

    yield app


@pytest.fixture(scope="session")
def random_test_data(app, init_db, app_config):
    #TODO: now loading random tasks, which is not ideal. Data loading has to split 
    # out in multiple fixtures.
    base_tasks_path = pathlib.Path(__file__).parent / 'tests' / 'tasks'
    # Load random tasks 3 times
    create_random_test_tasks(app, base_tasks_path, silent=True)
    create_random_test_tasks(app, base_tasks_path, silent=True)
    create_random_test_tasks(app, base_tasks_path, silent=True)
    # Create a couple of random taskgroups
    create_random_test_taskgroup(app, num_tasks=2, silent=True)
    create_random_test_taskgroup(app, num_tasks=3, silent=True)
    create_random_test_taskgroup(app, num_tasks=4, silent=True)

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    # To add authentication, see: https://kite.com/python/docs/flask.current_app.test_client
    return app.test_client()


@pytest.fixture(scope="session")
def no_db_app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_uri = 'mysql+pymysql://user:password@localhost/non_existing_db'

    # create the app with common test config
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': db_uri,
    }, use_sentry=False)

    yield app


@pytest.fixture
def no_db_client(no_db_app):
    """A test client for the app."""
    return no_db_app.test_client()
