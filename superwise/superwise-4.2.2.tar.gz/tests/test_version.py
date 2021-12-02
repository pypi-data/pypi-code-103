import json
import os
import sys
from datetime import datetime
from pprint import pprint

import jwt
import pandas as pd
import pytest
import requests
from google.cloud import storage
from google.oauth2 import service_account
from requests import Response

from project_root import PROJECT_ROOT
from superwise import Client
from superwise import Superwise
from superwise.controller.exceptions import *
from superwise.controller.summary.entities_validator import EntitiesValidationError
from superwise.models.data_entity import DataEntity
from superwise.models.data_entity import DataEntityCollection
from superwise.models.task import Task
from superwise.models.version import Version
from superwise.resources.superwise_enums import DataTypesRoles
from superwise.resources.superwise_enums import FeatureType
from superwise.resources.superwise_enums import TaskTypes
from tests import config
from tests import get_entities_fixture
from tests import get_sw


@pytest.fixture(scope="function")
def mock_gcp_client(monkeypatch):
    class GCSClient:
        def __init__(self, *args, **kwargs):
            self.name = "test"

        def bucket(self, bucket_name):
            return GCSClient()

        def blob(self, file_name):
            return GCSClient()

        def download_as_string(self):
            return "asdasdaas"

        def upload_from_string(self, data):
            return None

    monkeypatch.setattr(service_account.Credentials, "from_service_account_info", lambda *args, **kwargs: "")
    monkeypatch.setattr(storage, "Client", lambda *args, **kwargs: GCSClient())


@pytest.fixture(scope="function")
def mock_get_token(monkeypatch):
    monkeypatch.setattr(Client, "get_token", lambda *args, **kwargs: "token")
    monkeypatch.setattr(Client, "get_service_account", lambda *args, **kwargs: {})


@pytest.fixture(scope="function")
def mock_jwt_decode(monkeypatch):
    monkeypatch.setattr(jwt, "decode", lambda *args, **kwargs: {"tenantId": "test"})


@pytest.fixture(scope="function")
def sw(mock_gcp_client, mock_jwt_decode):
    return Superwise(client_id="test", secret="test")


@pytest.fixture(scope="function")
def mock_version_requests(sw, monkeypatch):
    the_response = Response()
    the_response.status_code = 201
    with open(f"{PROJECT_ROOT}/tests/resources/data_entity/assets/entities.json", "r") as fh:
        data_entities = fh.read()
    data_response_response = Response()
    data_response_response._content = data_entities
    data_response_response.status_code = 200
    example_task = Task(name="test", description="test", monitor_delay=1)
    example_version = Version(task_id=1, status="Active", name="test version")

    the_response._content = json.dumps(example_version.get_properties())
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: the_response)
    monkeypatch.setattr(sw.task, "get_by_id", lambda *args, **kwargs: example_task)
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: the_response)
    request_get_lambda = lambda url, **kwargs: data_response_response if "data_entities" in url else the_response
    monkeypatch.setattr(requests, "get", request_get_lambda)


def get_entities_fixture(path=f"{PROJECT_ROOT}/tests/resources/basic_schema.json"):
    with open(path, "r") as fh:
        schema = json.loads(fh.read())

    entities = [
        DataEntity(
            dimension_start_ts=m.get("dimension_start_ts", None),
            name=m["name"],
            type=m["type"],
            role=m["role"],
            feature_importance=None,
        )
        for m in schema
    ]
    return entities


def test_dataentity_creation_unit():
    entities = DataEntity(
        dimension_start_ts=None,
        name="barak",
        type=FeatureType.CATEGORICAL,
        role=DataTypesRoles.LABEL,
        feature_importance=None,
    )

    assert entities.type == FeatureType.CATEGORICAL.value
    assert entities.role == DataTypesRoles.LABEL.value


def test_create_version(mock_get_token, sw, mock_version_requests):
    entities = get_entities_fixture()
    version_external = Version(
        task_id=1,
        name="test version",
        baseline_files=["gs://superwise-tools/integration_tests/basic/baseline_meta.parquet"],
        data_entities=entities,
    )
    model = sw.version.create(version_external)
    assert isinstance(model, Version)


def test_get_version(mock_get_token, sw, mock_version_requests):
    version = sw.version.get_by_id(1)
    assert isinstance(version, Version)


def test_get_version_data_entities(mock_get_token, sw, mock_version_requests):
    data_entities = sw.version.get_data_entities(version_id=1)
    assert isinstance(data_entities, list)
    assert isinstance(data_entities[0], DataEntity)


def test_create_from_df(mock_get_token, sw, mock_version_requests):
    entities = get_entities_fixture(f"{PROJECT_ROOT}/tests/resources/internal_sdk/basic_schema.json")
    df = pd.read_json(f"{PROJECT_ROOT}/tests/resources/internal_sdk/data_bool.json")
    versionExternal = Version(
        task_id=1, baseline_df=df, name="test version 1", baseline_files=[], data_entities=entities
    )
    created_version = sw.version.create(versionExternal, wait_until_complete=True)
    assert isinstance(created_version, Version)


def test_create_from_df_base_version(mock_get_token, sw, mock_version_requests):
    entites = get_entities_fixture(f"{PROJECT_ROOT}/tests/resources/internal_sdk/basic_schema.json")
    df = pd.read_json(f"{PROJECT_ROOT}/tests/resources/internal_sdk/data.json")

    base_version = Version(id=1, status="Active")
    entites[0].name = "est_country_name_change"
    df = df.rename(columns={"est_country": "est_country_name_change"})
    versionExternal = Version(
        task_id=1, baseline_df=df, name="test version 1", baseline_files=[], data_entities=entites
    )
    sw.version.create(versionExternal, base_version=base_version, wait_until_complete=True)
