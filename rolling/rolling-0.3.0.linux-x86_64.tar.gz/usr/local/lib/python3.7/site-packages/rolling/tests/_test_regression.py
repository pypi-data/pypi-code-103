import pytest

from rolling.apply import Apply
from rolling.regression import OrdinaryLeastSquares


def linear_regression(x, y):
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)

    sum_xy = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    sum_x2 = sum((xi - x_mean)**2 for xi in x)

    gradient = sum_xy / sum_x2
    intercept = y_mean - gradient * x_mean

    return gradient, intercept


@pytest.mark.parametrize(
    "array",
    [
        [],
        [3, 1, 4, 1, 5],
        [5, 5, 5, 5, 5, 5, 5, 5, 5],
        [3, 4, 5, 6, 7, 4, 3, 2, 0],
        [1, 6, -1, -9, 0, 1, -8, 3],
    ],
)
@pytest.mark.parametrize("window_size", [2, 3, 4, 5])
@pytest.mark.parametrize("window_type", ["fixed", "variable"])
def test_rolling_sum(array, window_size, window_type):
    got = OrdinaryLeastSquares(array, window_size, window_type=window_type)
    expected = Apply(array, window_size, operation=linear_regression, window_type=window_type)
    assert pytest.approx(list(got)) == list(expected)
