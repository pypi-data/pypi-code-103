"""Test fetch data."""
from datetime import datetime
from unittest import mock

import pytest
from click.testing import CliRunner
from modelchallangekleiner.data.fetch_data import fetch_data_cli


TEST_CASES = [
    {
        "description": "the happy path is tested",
        "args": [
            "--date",
            datetime.now().strftime("%Y%m%d"),
            "--dataset_url",
            "EXAMPLE.URL",
            "--context_path",
        ],
        "mock_responses": {"urlretrieve": "example urlretrieve return value"},
        "expected_result": {},
    }
]


@pytest.mark.parametrize("test_cases", TEST_CASES)
@mock.patch("modelchallangekleiner.data.fetch_data.urllib.request.urlretrieve")
def test_fetch_data(urlretrieve, tmpdir, test_cases):
    """Test fetch_data_cli."""
    runner = CliRunner()
    urlretrieve.return_value = test_cases.get("mock_responses").get("urlretrieve")

    result = runner.invoke(fetch_data_cli, test_cases.get("args") + [tmpdir])

    assert result.exit_code == 0
