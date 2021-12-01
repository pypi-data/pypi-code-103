import numpy as np
import pandas as pd

from mlutil.model import GAM


def test_GAM():
    m = GAM()
    X = np.arange(20)[:, None]
    y = np.arange(20) + np.random.normal(scale=0.1, size=20)
    m.fit(X, y)
    X_test = np.arange(15, 25)[:, None]
    y_test = np.arange(15, 25)
    y_hat = m.predict(X_test)
    np.testing.assert_allclose(y_test, y_hat, atol=1.0)


def test_GAM_pandas():
    m = GAM()
    X = pd.DataFrame({"a": np.arange(20)})
    y = pd.Series(np.arange(20) + np.random.normal(scale=0.1, size=20))
    m.fit(X, y)
    X_test = np.arange(15, 25)[:, None]
    y_test = np.arange(15, 25)
    y_hat = m.predict(X_test)
    np.testing.assert_allclose(y_test, y_hat, atol=1.0)
    assert m.feature_names == ["a", "a_s0", "a_s1", "a_s2", "a_s3", "a_s4"]
