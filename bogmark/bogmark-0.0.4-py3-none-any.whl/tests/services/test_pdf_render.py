import os
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from monite.services import PdfRenderV1
from tests.services.mocks import simple_200_resp

environ = {"PDF_RENDER_URL": "https://localhost", "SERVICE_NAME": "CI TESTS"}


@pytest.mark.asyncio
async def test_pdf_render(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        pdf_render_service = PdfRenderV1()

    mocker.patch.object(PdfRenderV1, "_make_json_request", simple_200_resp)
    await pdf_render_service.get_all_supported_templates_data()
    await pdf_render_service.render_file(
        template_name="monite_template", language="EN", variables={"var1": "1", "var2": "2"}
    )
