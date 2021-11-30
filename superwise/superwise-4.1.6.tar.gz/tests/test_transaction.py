import json
import sys
import uuid
from pprint import pprint

import boto3
import pytest
import requests
from google.cloud import storage
from google.oauth2 import service_account
from requests import Response

from project_root import PROJECT_ROOT
from superwise import Client
from superwise import Superwise
from superwise.controller.exceptions import *
from superwise.models.task import Task
from tests import config
from tests import get_sw
from tests import print_results


@pytest.fixture(scope="function")
def mock_get_token(monkeypatch):
    monkeypatch.setattr(
        Client,
        "get_token",
        lambda *args, **kwargs: "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjQ3ZDdmMDg2In0.eyJzdWIiOiI5YzNlZmUxZC03NGNlLTRlZTItYTMyOC1kMWZmNmQyMDAyM2YiLCJlbWFpbCI6InN3X2JhcmFrQHN1cGVyd2lzZS5haSIsInVzZXJNZXRhZGF0YSI6e30sInRlbmFudElkIjoiYmFyYWsiLCJyb2xlcyI6WyJWaWV3ZXIiXSwicGVybWlzc2lvbnMiOlsiZmUuc2VjdXJlLndyaXRlLnVzZXJBcGlUb2tlbnMiLCJmZS5zZWN1cmUuZGVsZXRlLnVzZXJBcGlUb2tlbnMiLCJmZS5zZWN1cmUucmVhZC51c2VyQXBpVG9rZW5zIl0sIm1ldGFkYXRhIjp7fSwiY3JlYXRlZEJ5VXNlcklkIjoiNDg5ZmM5Y2YtZDlhYy00MWMwLWJmM2ItN2VhNDUyNDY4ODEyIiwidHlwZSI6InVzZXJBcGlUb2tlbiIsInVzZXJJZCI6IjQ4OWZjOWNmLWQ5YWMtNDFjMC1iZjNiLTdlYTQ1MjQ2ODgxMiIsImlhdCI6MTYzNjY0ODIyMywiZXhwIjoxNjM2NzM0NjIzLCJpc3MiOiJmcm9udGVnZyJ9.qhEclIsSpfwXpCTFb8qhKpizRWtpQSnkE7VMsy9Et3guLcOcTiTVZ2wOJPmemtL3g3AStKH2jFSOEwQOoqnvgSR3dum9I_Ae3UwrFNRnM3EqOz7UsD0cJAd1AYy-69-67o5oX9A2U4MPZSA5Dr5Edbvn86-AsBJhADGDs5AyEyuGmlJTq0ACGAmoC8qZlxwnOsn9wIzTiQVU7085M73n5iJ26SNhsy4KNpU-8oR2lC1akDroHzL8aIr5dAWSWZz_cfcyWQyC1gqb4_ZAvG1GXiKwsGW2irFyfGoD9zrwMoMGuWXKCbXnHxIzuv8ImX_cRVPXq5xVBYUXwODr83Q3FA",
    )
    monkeypatch.setattr(Client, "get_service_account", lambda *args, **kwargs: {})


@pytest.fixture(scope="function")
def sw(mock_gcp_client):
    return Superwise(client_id="test", secret="test")


@pytest.fixture(scope="function")
def mock_transaction_requests(monkeypatch):
    the_response = Response()
    the_response._content = b'{ "transaction_id" : "123" }'
    the_response.status_code = 201
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: the_response)


@pytest.fixture(scope="function")
def mock_boto_client(monkeypatch):
    class BotoClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_object(self, *args, **kwargs):
            class ObjectResposne:
                def read(self):
                    return "blablabla"

            return dict(Body=ObjectResposne())

    monkeypatch.setattr(boto3, "client", lambda *args, **kwargs: BotoClient())


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
def get_transaction_records_payload():
    with open(f"{PROJECT_ROOT}/tests/resources/transaction/records_payload.json") as f:
        return json.loads(f.read())


def test_transaction_records(mock_transaction_requests, mock_get_token, sw, get_transaction_records_payload):
    status = sw.transaction.log_batch(task_id=1, records=get_transaction_records_payload)
    assert isinstance(status, dict) and "transaction_id" in status.keys()
    status = sw.transaction.log_batch(task_id="test", version_id="test", records=get_transaction_records_payload)
    assert isinstance(status, dict) and "transaction_id" in status.keys()


def test_transaction_file(mock_transaction_requests, mock_get_token, sw):
    status = sw.transaction.log_file("gs://fvsdfvfdv")
    assert isinstance(status, dict) and "transaction_id" in status.keys()


def test_transaction_with_wrong_file_path(mock_transaction_requests, mock_get_token, sw):
    ok = False
    try:
        status = sw.transaction.log_file("wrong path")
    except Exception as e:
        assert str(e) == "transaction file failed because of wrong file path. file path should be gcs or s3 path."
        ok = True
    assert ok is True


def test_transaction_upload_from_gcs(mock_transaction_requests, mock_get_token, mock_gcp_client, sw):
    status = sw.transaction.log_from_gcs(
        file_path="gs://superwise-oryan-test/new_integration_tests_binary_classification_predictions.csv",
        service_account={},
    )

    assert isinstance(status, dict) and "transaction_id" in status.keys()


def test_transaction_upload_from_s3(mock_transaction_requests, mock_get_token, mock_gcp_client, mock_boto_client, sw):
    status = sw.transaction.log_from_s3(
        file_path="s3://superwise-oryan-test/new_integration_tests_binary_classification_predictions.csv",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    assert isinstance(status, dict) and "transaction_id" in status.keys()
