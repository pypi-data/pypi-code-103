import os
import uuid
from unittest import mock

import pytest
from pydantic import BaseModel
from pytest_mock import MockerFixture

from monite.services import MailerV1
from monite.structures.response import MoniteJSONResponse
from tests.services.mocks import simple_json_200_resp

environ = {"MAILER_URL": "http://127.0.0.1:8888", "SERVICE_NAME": "CI TESTS"}


@pytest.mark.asyncio
async def test_templates(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        mailer_service = MailerV1()

    api_user_id = uuid.uuid4()

    mocker.patch.object(MailerV1, "_make_json_request", simple_json_200_resp)
    response = await mailer_service.add_custom_template(
        api_user_id=api_user_id,
        template_name="basic_template",
        language_code="en",
        subject_template="{{username}}",
        body_template="{{year_now}}",
    )
    assert response.status_code == 200
    template_id = 1

    response = await mailer_service.get_custom_template(api_user_id=api_user_id, template_id=template_id)
    assert response.status_code == 200

    await mailer_service.update_custom_template(
        api_user_id=api_user_id,
        template_id=template_id,
        language_code="de",
        subject_template="{{username}}",
        body_template="{{year_now}}",
    )

    response = await mailer_service.delete_custom_template(api_user_id=api_user_id, template_id=template_id)
    assert response.status_code == 200

    response = await mailer_service.get_all_custom_templates(api_user_id=api_user_id)
    assert response.status_code == 200

    response = await mailer_service.get_all_system_templates()
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_mail_sender(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        mailer_service = MailerV1()

    class TemplateData(BaseModel):
        username = "Ivan"
        year_now = 2021

    mocker.patch.object(MailerV1, "_make_json_request", simple_json_200_resp)
    response = await mailer_service.send_email(
        template_name="basic_template",
        entity_id=str(uuid.uuid4()),
        api_user_id=str(uuid.uuid4()),
        recipient="ivan.rykov@monite.com",
        language_code="en",
        template_data=TemplateData().dict(),
        attachments={"https://www.w3schools.com/css/trolltunga.jpg": "trolltunga.jpg"},
        external_user_id=None,
    )
    assert isinstance(response, MoniteJSONResponse)
    assert response.status_code == 200
