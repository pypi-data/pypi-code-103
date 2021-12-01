import numpy as np
import pandas as pd
import pytest
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures

from mlutil.transform import ColumnSelector, QuantileClipper, SigmaClipper


@pytest.mark.parametrize(
    "X, X_new, sigma, sigma_low, sigma_high",
    [
        (
            pd.DataFrame(
                {
                    "a": [np.nan, -1.0, 2.0, 1.0, 1.0, 302.0],
                    "b": [-2.0, 1.0, 3.0, 2.0, -201, np.nan],
                }
            ),
            pd.DataFrame(
                {
                    "a": [np.nan, -1.0, 2.0, 1.0, 1.0, 4.0],
                    "b": [-2.0, 1.0, 3.0, 2.0, -5, np.nan],
                }
            ),
            3.0,
            None,
            None,
        ),
        (
            pd.DataFrame(
                {
                    "a": [np.nan, -1.0, 2.0, 1.0, 1.0, 302.0],
                    "b": [-2.0, 1.0, 3.0, 2.0, -201, np.nan],
                }
            ),
            pd.DataFrame(
                {
                    "a": [np.nan, -1.0, 2.0, 1.0, 1.0, 4.0],
                    "b": [-2.0, 1.0, 3.0, 2.0, -5, np.nan],
                }
            ),
            1.0,
            3.0,
            3.0,
        ),
        (
            np.array(
                [
                    [np.nan, -1.0, 2.0, 1.0, 1.0, 302.0],
                    [-2.0, 1.0, 3.0, 2.0, -201, np.nan],
                ]
            ).T,
            np.array(
                [
                    [np.nan, -1.0, 2.0, 1.0, 1.0, 4.0],
                    [-2.0, 1.0, 3.0, 2.0, -5, np.nan],
                ]
            ).T,
            3.0,
            None,
            None,
        ),
    ],
)
def test_SigmaClipper(X, X_new, sigma, sigma_low, sigma_high):
    t = SigmaClipper(sigma=sigma, low_sigma=sigma_low, high_sigma=sigma_high)
    X_new_ = t.fit_transform(X)
    if isinstance(X, np.ndarray):
        np.testing.assert_allclose(X_new_, X_new)
    elif isinstance(X, pd.DataFrame):
        np.testing.assert_allclose(X_new_.values, X_new.values)
    else:
        raise TypeError(type(X))


@pytest.mark.parametrize(
    "X, X_new, factor, q_low, q_high",
    [
        (
            pd.DataFrame(
                {
                    "a": [np.nan, -1.0, 2.0, 0, 1.0, 302.0],
                    "b": [-2.0, 1.0, 3.0, 2.0, -201, np.nan],
                }
            ),
            pd.DataFrame(
                {
                    "a": [np.nan, -1.0, 2.0, 0, 1.0, 4.0],
                    "b": [-2.0, 1.0, 3.0, 2.0, -8.0, np.nan],
                }
            ),
            3.0,
            0.25,
            0.75,
        ),
        (
            np.array(
                [
                    [np.nan, -1.0, 2.0, 0, 1.0, 302.0],
                    [-2.0, 1.0, 3.0, 2.0, -201, np.nan],
                ]
            ).T,
            np.array(
                [
                    [np.nan, -1.0, 2.0, 0, 1.0, 4.0],
                    [-2.0, 1.0, 3.0, 2.0, -8.0, np.nan],
                ]
            ).T,
            3.0,
            0.25,
            0.75,
        ),
    ],
)
def test_QuantileClipper(X, X_new, factor, q_low, q_high):
    t = QuantileClipper(factor=factor, low_quantile=q_low, high_quantile=q_high)
    X_new_ = t.fit_transform(X)
    if isinstance(X, np.ndarray):
        np.testing.assert_allclose(X_new_, X_new)
    elif isinstance(X, pd.DataFrame):
        np.testing.assert_allclose(X_new_.values, X_new.values)
    else:
        raise TypeError(type(X))


@pytest.mark.parametrize(
    "columns, regex, like",
    [
        (["a_dd", "c_dd", "d_dd"], None, None),
        (None, r"\_dd$", None),
        (None, None, r"_dd"),
    ],
)
def test_ColumnSelector_bijective(columns, regex, like):
    df = pd.DataFrame(
        {
            "a_dd": [1.0, 2.0, 3.0, np.nan],
            "b_ff": [1.0, 2.0, 3.0, np.nan],
            "c_dd": [1.0, 2.0, 3.0, np.nan],
            "d_dd": [1.0, 2.0, 3.0, np.nan],
        }
    )
    expected = pd.DataFrame(
        {
            "a_dd": [1.0, 2.0, 3.0, 0],
            "b_ff": [1.0, 2.0, 3.0, np.nan],
            "c_dd": [1.0, 2.0, 3.0, 0],
            "d_dd": [1.0, 2.0, 3.0, 0],
        }
    )
    t = ColumnSelector(
        SimpleImputer(strategy="constant", fill_value=0),
        columns=columns,
        columns_like=like,
        columns_regex=regex,
    )
    actual = t.fit_transform(df)
    pd.testing.assert_frame_equal(expected, actual)
    assert t.new_columns_ == list(actual.columns)


@pytest.mark.parametrize(
    "infer_new_columns, new_columns_attr, new_columns_prefix, remainder, expected_columns",
    [
        (
            "same_attr",
            "categories_",
            None,
            "passthrough",
            ["b_ff", "a_dd_1", "a_dd_2", "c_dd_1", "c_dd_4"],
        ),
        (
            "num",
            None,
            None,
            "passthrough",
            ["b_ff", "a_dd_c_dd_0", "a_dd_c_dd_1", "a_dd_c_dd_2", "a_dd_c_dd_3"],
        ),
        (
            "num",
            None,
            "a_c_dd",
            "passthrough",
            ["b_ff", "a_c_dd_0", "a_c_dd_1", "a_c_dd_2", "a_c_dd_3"],
        ),
        ("num", None, None, "drop", ["a_dd_c_dd_0", "a_dd_c_dd_1", "a_dd_c_dd_2", "a_dd_c_dd_3"]),
    ],
)
def test_ColumnSelector_with_OneHotEncoder(
    infer_new_columns,
    new_columns_attr,
    new_columns_prefix,
    remainder,
    expected_columns,
):
    df = pd.DataFrame(
        {
            "a_dd": [1, 2, 2, 2],
            "b_ff": [1.0, 2.0, 3.0, np.nan],
            "c_dd": [1, 1, 4, 4],
        }
    )
    t = ColumnSelector(
        OneHotEncoder(sparse=False),
        columns=["a_dd", "c_dd"],
        infer_new_columns=infer_new_columns,
        new_columns_attr=new_columns_attr,
        new_columns_prefix=new_columns_prefix,
        remainder=remainder,
    )
    actual = t.fit_transform(df)
    assert list(actual.columns) == expected_columns


def test_ColumnSelector_with_nans_OneHotEncoder_GridSearchCV():
    df = pd.DataFrame(
        {
            "a": np.random.normal(size=6),
            "b": np.arange(6),
            "c": ["black", "black", "white", "black", "white", "black"],
            "d": [None, "dog", "cat", "cat", "cat", "cat"],
            "e": [np.nan, 1, 1, 2, 2, 2],
        }
    )
    pipe = Pipeline(
        [
            (
                "nans_d",
                ColumnSelector(
                    SimpleImputer(missing_values=None, fill_value="none", strategy="constant"),
                    ["d"],
                ),
            ),
            (
                "nans_e",
                ColumnSelector(
                    SimpleImputer(missing_values=np.nan, fill_value=0, strategy="constant"),
                    ["e"],
                ),
            ),
            (
                "onehot",
                ColumnSelector(
                    OneHotEncoder(sparse=False, handle_unknown="ignore"),
                    ["c", "d", "e"],
                    infer_new_columns="same_attr",
                    new_columns_attr="categories_",
                ),
            ),
            ("estimator", LinearRegression()),
        ]
    )
    m = GridSearchCV(
        pipe, {"estimator__fit_intercept": [True, False]}, scoring="neg_mean_absolute_error"
    )
    _ = m.fit(df, np.random.normal(size=len(df)))
    assert m.best_params_ is not None


@pytest.mark.parametrize(
    "infer_new_columns, new_columns_attr, new_columns_prefix, remainder, expected_columns",
    [
        (
            "attr",
            "powers_",
            None,
            "passthrough",
            ["b_ff", "a_dd_c_dd_[0 0]", "a_dd_c_dd_[1 0]", "a_dd_c_dd_[0 1]", "a_dd_c_dd_[1 1]"],
        ),
        (
            "attr",
            "powers_",
            "a_c_dd",
            "passthrough",
            ["b_ff", "a_c_dd_[0 0]", "a_c_dd_[1 0]", "a_c_dd_[0 1]", "a_c_dd_[1 1]"],
        ),
        (
            "num",
            None,
            None,
            "passthrough",
            ["b_ff", "a_dd_c_dd_0", "a_dd_c_dd_1", "a_dd_c_dd_2", "a_dd_c_dd_3"],
        ),
        (
            "num",
            None,
            "a_c_dd",
            "passthrough",
            ["b_ff", "a_c_dd_0", "a_c_dd_1", "a_c_dd_2", "a_c_dd_3"],
        ),
        ("num", None, None, "drop", ["a_dd_c_dd_0", "a_dd_c_dd_1", "a_dd_c_dd_2", "a_dd_c_dd_3"]),
    ],
)
def test_ColumnSelector_with_PolynomialFeatures(
    infer_new_columns,
    new_columns_attr,
    new_columns_prefix,
    remainder,
    expected_columns,
):
    df = pd.DataFrame(
        {
            "a_dd": [1, 2, 2, 2],
            "b_ff": [1.0, 2.0, 3.0, np.nan],
            "c_dd": [1, 1, 4, 4],
        }
    )
    t = ColumnSelector(
        PolynomialFeatures(degree=2, interaction_only=True),
        columns=["a_dd", "c_dd"],
        infer_new_columns=infer_new_columns,
        new_columns_attr=new_columns_attr,
        new_columns_prefix=new_columns_prefix,
        remainder=remainder,
    )
    actual = t.fit_transform(df)
    assert list(actual.columns) == expected_columns


@pytest.mark.parametrize(
    "infer_new_columns, new_columns_attr, new_columns_prefix, remainder, expected_columns",
    [
        ("num", None, None, "passthrough", ["b_ff", "a_dd_c_dd_0"]),
        ("num", None, "a_c_dd", "passthrough", ["b_ff", "a_c_dd_0"]),
        ("num", None, None, "drop", ["a_dd_c_dd_0"]),
    ],
)
def test_ColumnSelector_with_PCA(
    infer_new_columns,
    new_columns_attr,
    new_columns_prefix,
    remainder,
    expected_columns,
):
    df = pd.DataFrame(
        {
            "a_dd": [1, 2, 2, 2],
            "b_ff": [1.0, 2.0, 3.0, np.nan],
            "c_dd": [1, 1, 4, 4],
        }
    )
    t = ColumnSelector(
        PCA(n_components=1),
        columns=["a_dd", "c_dd"],
        infer_new_columns=infer_new_columns,
        new_columns_attr=new_columns_attr,
        new_columns_prefix=new_columns_prefix,
        remainder=remainder,
    )
    actual = t.fit_transform(df)
    assert list(actual.columns) == expected_columns


@pytest.mark.parametrize(
    "X, X_new, columns",
    [
        (
            pd.DataFrame(
                {
                    "a": [np.nan, -1.0, 2.0, 1.0, 1.0, 302.0],
                    "b": [-2.0, 1.0, 3.0, 2.0, -201, np.nan],
                }
            ),
            pd.DataFrame(
                {
                    "a": [np.nan, -1.0, 2.0, 1.0, 1.0, 4.0],
                    "b": [-2.0, 1.0, 3.0, 2.0, -5, np.nan],
                }
            ),
            None,
        ),
        (
            pd.DataFrame(
                {
                    "a": [np.nan, -1.0, 2.0, 1.0, 1.0, 302.0],
                    "b": [-2.0, 1.0, 3.0, 2.0, -201, np.nan],
                }
            ),
            pd.DataFrame(
                {
                    "a": [np.nan, -1.0, 2.0, 1.0, 1.0, 4.0],
                    "b": [-2.0, 1.0, 3.0, 2.0, -201, np.nan],
                }
            ),
            ["a"],
        ),
    ],
)
def test_ColumnSelector_with_SigmaClipper(X, X_new, columns):
    t = ColumnSelector(
        SigmaClipper(low_sigma=3, high_sigma=3),
        columns=columns,
    )
    X_new_ = t.fit_transform(X)
    if isinstance(X, np.ndarray):
        np.testing.assert_allclose(X_new_, X_new)
    elif isinstance(X, pd.DataFrame):
        np.testing.assert_allclose(X_new_.values, X_new.values)
    else:
        raise TypeError(type(X))
