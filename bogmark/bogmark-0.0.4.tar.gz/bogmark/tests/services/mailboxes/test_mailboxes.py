import os
import uuid
from unittest import mock

import pytest
from pydantic import BaseModel
from pytest_mock import MockerFixture

from monite.services import MailboxV1
from monite.structures.response import MoniteJSONResponse
from tests.services.mocks import simple_json_200_resp

environ = {"MAILBOX_URL": "https://localhost", "SERVICE_NAME": "CI TESTS"}


class TestPydanticModel(BaseModel):
    pass


@pytest.mark.asyncio
async def test_get_domains(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        mailboxes = MailboxV1()

    mocker.patch.object(MailboxV1, "_make_json_request", simple_json_200_resp)
    response = await mailboxes.get_domains(api_user_id=str(uuid.uuid4()))

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_domain(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        mailboxes = MailboxV1()

    mocker.patch.object(MailboxV1, "_make_json_request", simple_json_200_resp)
    payload = TestPydanticModel()
    response = await mailboxes.create_domain(api_user_id=str(uuid.uuid4()), payload=payload)

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_verify_domain(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        mailboxes = MailboxV1()

    mocker.patch.object(MailboxV1, "_make_json_request", simple_json_200_resp)
    response = await mailboxes.verify_domain(api_user_id=str(uuid.uuid4()), domain="msk.tech")

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_domain(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        mailboxes = MailboxV1()

    mocker.patch.object(MailboxV1, "_make_json_request", simple_json_200_resp)
    response = await mailboxes.delete_domain(api_user_id=str(uuid.uuid4()), domain="msk.tech")

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_autogenerate_mailbox(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        mailboxes = MailboxV1()

    mocker.patch.object(MailboxV1, "_make_json_request", simple_json_200_resp)
    payload = TestPydanticModel()
    response = await mailboxes.autogenerate_mailbox(
        api_user_id=str(uuid.uuid4()), entity_id=str(uuid.uuid4()), payload=payload
    )

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_mailbox(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        mailboxes = MailboxV1()

    mocker.patch.object(MailboxV1, "_make_json_request", simple_json_200_resp)
    payload = TestPydanticModel()
    response = await mailboxes.create_mailbox(
        api_user_id=str(uuid.uuid4()), entity_id=str(uuid.uuid4()), payload=payload
    )

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_mailboxes(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        mailboxes = MailboxV1()

    mocker.patch.object(MailboxV1, "_make_json_request", simple_json_200_resp)
    response = await mailboxes.get_mailboxes(api_user_id=str(uuid.uuid4()), entity_id=str(uuid.uuid4()))

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_mailbox(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        mailboxes = MailboxV1()

    mocker.patch.object(MailboxV1, "_make_json_request", simple_json_200_resp)
    response = await mailboxes.delete_mailbox(
        api_user_id=str(uuid.uuid4()), entity_id=str(uuid.uuid4()), mailbox_full_address="hello@monite.com"
    )

    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200
