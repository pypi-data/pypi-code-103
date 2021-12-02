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
from . import create_app
from .models import db

from .tests.loaders import InvalidParameterException, CannotReachIfdbException
from .tests.loaders import FindingScraper, ingest_json 

import yaml

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
def subject_data(app, init_db, app_config):
    from datetime import date
    from .models import Subject
    from .models import db

    # Create 2 test subjects
    for subject_id in range(1, 3):
        study_id = f"Test Subject_{subject_id}"
        generator_url = f'none://test-generator-finding{subject_id}'
        subject = Subject(study_id=study_id, generator_url=generator_url)
        with app.app_context():
            db.session.add(subject)
            db.session.commit()
    yield app

@pytest.fixture(scope="session")
def experiment_data(app, init_db, app_config):
    from datetime import date
    from .models import Experiment
    from .models import db

    # Create 2 test experiments
    
    for experiment_id in range(1, 3):
        experiment_label = f"Test exp_{experiment_id}"
        scan_date = date(2019, 1, experiment_id)
        experiment = Experiment(label=experiment_label, subject_id=experiment_id, date=scan_date)
        with app.app_context():
            db.session.add(experiment)
            db.session.commit()

    yield app

@pytest.fixture(scope="session")
def random_data(app, init_db, app_config):
    from datetime import datetime
    # create a finding with properties from a yaml template for an experiment
    task_template = 'test-template'
    subject_study_id = 'test-ergo-id'
    subject_generator_id = 'none://test-generator-subject'
    experiment_label = 'test_label'
    experiment_date = datetime.now()
    finding_generator_url = 'none://test-generator-finding'
    findings_path =  pathlib.Path(__file__).parent / 'tests' / 'findings.yaml'
    template_path =  pathlib.Path(__file__).parent / 'tests' / 'template.yaml'
    with open(findings_path) as fh:
        findings_data = yaml.safe_load(fh)
    with open(template_path) as fh:
        template_data = yaml.safe_load(fh)
    try:
        retval = ingest_json(app=app,
            findings_data=findings_data,
            template_data=template_data,
            task_template=task_template,
            subject_study_id=subject_study_id,
            subject_generator_url=subject_generator_id,
            experiment_label=experiment_label,
            experiment_date=experiment_date,
            finding_generator_url=finding_generator_url
        )
    except InvalidParameterException as e:
        print(e)
        assert False
    except CannotReachIfdbException as e:
        print(e)
        assert False

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
