import io
import os
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from monite.services import FileSaverV1
from tests.services.mocks import simple_200_resp

environ = {"FILE_SAVER_URL": "https://localhost", "SERVICE_NAME": "CI TESTS"}


@pytest.mark.asyncio
async def test_file_saver(mocker: MockerFixture):
    with mock.patch.dict(os.environ, environ):
        fs = FileSaverV1()

    mocker.patch.object(FileSaverV1, "_make_json_request", simple_200_resp)
    await fs.upload_file(
        file_obj=io.BytesIO(),
        region="eu-central-1",
        file_type="payables",
        preview_sizes=[{"width": 100, "height": 100}],
    )
    await fs.get_file_info(file_id="fewfewfwef")

    with pytest.raises(TypeError):
        await fs.upload_file(
            file_obj=io.BytesIO(),
            region="eu-central-1",
            file_type="payables",
            preview_sizes=[{"widt": 100, "height": 100}],
        )

    with pytest.raises(TypeError):
        await fs.upload_file(file_obj=io.BytesIO(), region="eu-central-1", file_type="payables", preview_sizes=[200])
