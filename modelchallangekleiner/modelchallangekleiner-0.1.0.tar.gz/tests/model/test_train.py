"""Test train."""
import joblib
import pytest
import pandas as pd
from click.testing import CliRunner
from modelchallangekleiner.model.train import train_cli

TEST_CASES = [
    {
        "description": "the happy path is tested",
        "args": ["--date", "test_dataset", "--context_path", "tests/model/"],
        "mock_responses": {"urlretrieve": "example urlretrieve return value"},
        "expected_result": {},
    }
]


@pytest.mark.parametrize("test_cases", TEST_CASES)
def test_train_cli(tmpdir, test_cases):
    """Test train_cli."""
    runner = CliRunner()

    result = runner.invoke(
        train_cli, test_cases.get("args") + ["--output_model_path", tmpdir]
    )

    model = joblib.load(f"{tmpdir}/model.pkl")

    assert result.exit_code == 0

    df = pd.DataFrame(
        {
            "LIMIT_BAL": [0],
            "SEX": [0],
            "EDUCATION": [0],
            "MARRIAGE": [0],
            "AGE": [0],
            "PAY_0": [0],
            "PAY_2": [0],
            "PAY_3": [0],
            "PAY_4": [0],
            "PAY_5": [0],
            "PAY_6": [0],
            "BILL_AMT1": [0],
            "BILL_AMT2": [0],
            "BILL_AMT3": [0],
            "BILL_AMT4": [0],
            "BILL_AMT5": [0],
            "BILL_AMT6": [0],
            "PAY_AMT1": [0],
            "PAY_AMT2": [0],
            "PAY_AMT3": [0],
            "PAY_AMT4": [0],
            "PAY_AMT5": [0],
            "PAY_AMT6": [0],
        }
    )

    assert result.exit_code == 0
    assert (model.predict(df) == [0]) or model.predict(df) == [1]
