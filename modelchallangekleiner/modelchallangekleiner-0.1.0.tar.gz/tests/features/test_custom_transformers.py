"""Test custom transformers."""
import pandas as pd
import pytest

from modelchallangekleiner.features.transformers.custom_transformers import (
    CustomImputer,
)

FEATURE_A = "feature_a"
FEATURE_B = "feature_b"
TARGET_VALUES = [0, 1]
VALUE = 5


example_dict = {
    FEATURE_A: [0, 1, 5],
    FEATURE_B: ["Sydney", "Delhi", "New york"],
}

TEST_CASES = [
    {
        "description": "the happy path is tested",
        "example_df": pd.DataFrame(example_dict),
        "feature_to_test": FEATURE_A,
        "expected_result": [VALUE, VALUE, VALUE],
    }
]


@pytest.mark.parametrize("test_cases", TEST_CASES)
def test_custom_transformers(test_cases):
    """Test custom_transformers."""

    custom_imputer = CustomImputer(missing_values=TARGET_VALUES, value=VALUE)

    df = custom_imputer.transform(
        test_cases.get("example_df")[test_cases.get("feature_to_test")]
    )

    assert df[FEATURE_A].tolist() == test_cases.get("expected_result")
