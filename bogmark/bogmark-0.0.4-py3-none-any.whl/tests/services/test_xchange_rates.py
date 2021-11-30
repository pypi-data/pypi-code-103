import os
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from monite.services import XchangeRatesV1
from tests.services.mocks import simple_200_resp

environ = {"XCHANGE_RATES_URL": "https://localhost", "SERVICE_NAME": "CI TESTS"}


@pytest.mark.asyncio
async def test_xchange_rates(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        rates_service = XchangeRatesV1()

    mocker.patch.object(XchangeRatesV1, "_make_json_request", simple_200_resp)
    await rates_service.get_rates(currency_code="10")
