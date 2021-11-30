import os
import uuid
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from monite.services import EventsV1
from monite.structures.response import MoniteJSONResponse
from tests.services.mailboxes.test_mailboxes import TestPydanticModel
from tests.services.mocks import simple_json_200_resp

environ = {"EVENTS_URL": "https://localhost", "SERVICE_NAME": "CI TESTS"}


@pytest.mark.asyncio
async def test_create_event(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        events = EventsV1()

    mocker.patch.object(EventsV1, "_make_json_request", simple_json_200_resp)
    payload = TestPydanticModel()
    response = await events.create_webhook_settings(api_user_id=str(uuid.uuid4()), payload=payload)

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_events(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        events = EventsV1()

    mocker.patch.object(EventsV1, "_make_json_request", simple_json_200_resp)
    response = await events.get_webhook_settings(api_user_id=str(uuid.uuid4()))

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_webhook_settings(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        events = EventsV1()

    mocker.patch.object(EventsV1, "_make_json_request", simple_json_200_resp)
    response = await events.get_webhook_settings(api_user_id=str(uuid.uuid4()))

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_webhook_settings(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        events = EventsV1()

    mocker.patch.object(EventsV1, "_make_json_request", simple_json_200_resp)
    payload = TestPydanticModel()
    response = await events.create_webhook_settings(api_user_id=str(uuid.uuid4()), payload=payload)

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_webhook_settings(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        events = EventsV1()

    mocker.patch.object(EventsV1, "_make_json_request", simple_json_200_resp)
    payload = TestPydanticModel()
    response = await events.update_webhook_settings(
        api_user_id=str(uuid.uuid4()), webhook_id=str(uuid.uuid4()), payload=payload
    )
    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_webhook_settings(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        events = EventsV1()

    mocker.patch.object(EventsV1, "_make_json_request", simple_json_200_resp)
    response = await events.delete_webhook_settings(api_user_id=str(uuid.uuid4()), webhook_id=str(uuid.uuid4()))
    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200
