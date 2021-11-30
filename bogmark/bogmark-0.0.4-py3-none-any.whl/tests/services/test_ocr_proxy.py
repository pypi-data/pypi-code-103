import io
import os
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from monite.services import OcrProxyV1
from tests.services.mocks import simple_200_resp

environ = {"OCR_PROXY_URL": "https://localhost", "SERVICE_NAME": "CI TESTS"}


@pytest.mark.asyncio
async def test_xchange_rates(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        ocr = OcrProxyV1()

    mocker.patch.object(OcrProxyV1, "_make_json_request", simple_200_resp)
    await ocr.recognise_invoice_from_file(
        file_obj=io.BytesIO(),
        ocr_provider="hypatos",
        country_code="DE",
    )
    await ocr.recognise_invoice_from_url(
        url="http://localhost",
        ocr_provider="hypatos",
        country_code="DE",
    )
    await ocr.recognise_receipt_from_file(
        file_obj=io.BytesIO(),
        ocr_provider="hypatos",
        country_code="DE",
    )
    await ocr.recognise_receipt_from_url(
        url="http://localhost",
        ocr_provider="hypatos",
        country_code="DE",
    )
