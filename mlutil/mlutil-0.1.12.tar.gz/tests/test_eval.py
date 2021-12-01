import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_validate

from mlutil.eval import TimeSeriesSplit


def test_dummy():
    assert True


def test_TimeSeriesSplit():
    X = np.vstack([np.random.normal(size=100), np.random.normal(size=100)]).T
    y = np.random.normal(size=100)
    m = LinearRegression()
    cv = TimeSeriesSplit(test_size=50)
    scores = cross_validate(m, X, y, scoring=["neg_mean_squared_error"], cv=cv)
    assert len(scores["test_neg_mean_squared_error"]) > 0

    cv2 = TimeSeriesSplit(test_size=0.5)
    scores2 = cross_validate(m, X, y, scoring=["neg_mean_squared_error"], cv=cv2)
    np.testing.assert_allclose(
        scores["test_neg_mean_squared_error"], scores2["test_neg_mean_squared_error"]
    )


def test_TimeSeriesSplit_repr():
    cv = TimeSeriesSplit(test_size=50, train_size=20)
    assert str(cv) == "TimeSeriesSplit(test_size=50, train_size=20)"
