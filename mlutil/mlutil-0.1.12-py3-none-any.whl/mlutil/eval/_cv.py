from typing import Optional, Union

from mlutil._util import SimpleRepr


class TimeSeriesSplit(SimpleRepr):
    """Split data for nested (rolling) time-series cross-validation"""

    def __init__(
        self,
        test_size: Union[int, float] = 0.5,
        train_size: Optional[Union[int, float]] = None,
        predict_size: Union[int, float] = 1,
        predict_step: Union[int, float] = 1,
        predict_lag: Union[int, float] = 0,
        drop_first_points: Union[int, float] = 0,
        drop_last_points: Union[int, float] = 0,
    ):
        """
        :param test_size: total number of points in the test period
        :param train_size: maximum number of points in the train period
            None - all available data points will be used for training
        :param predict_size: predict <x> points ahead at once
        :param predict_step: place CV folds every <x> points
        :param predict_lag: lag predictions by <x> points
            a non-zero value creates a gap between the train and test periods
        :param drop_first_points: do not use first <x> points
        :param drop_last_points: do not use last <x> points
        """

        assert test_size > 0
        assert (train_size is None) or (test_size > 0)
        assert predict_size > 0
        assert predict_step > 0
        assert predict_lag >= 0
        assert drop_first_points >= 0
        assert drop_last_points >= 0

        self.test_size = test_size
        self.train_size = train_size
        self.predict_size = predict_size
        self.predict_step = predict_step
        self.predict_lag = predict_lag
        self.drop_first_points = drop_first_points
        self.drop_last_points = drop_last_points

    @staticmethod
    def _cv_gen(
        last_idx: int,
        test_size: int,
        train_size: Optional[int],
        predict_size: int,
        predict_lag: int,
        predict_step: int,
        drop_first_points: int,
        drop_last_points: int,
    ):
        last_end_test_idx = last_idx - drop_last_points
        last_end_train_idx = last_end_test_idx - predict_size - predict_lag
        first_end_train_idx = last_end_train_idx - test_size + predict_step
        first_end_train_idx = (
            first_end_train_idx + (last_end_train_idx - first_end_train_idx) % predict_step
        )
        if first_end_train_idx < drop_first_points:
            raise AssertionError(
                f"First training interval is empty: "
                f"{first_end_train_idx} < {drop_first_points}"
            )

        for end_train_idx in range(first_end_train_idx, last_end_train_idx + 1, predict_step):
            if train_size is not None:
                start_train_idx = max(end_train_idx - train_size + 1, drop_first_points)
            else:
                start_train_idx = drop_first_points
            train_ids = slice(start_train_idx, min(end_train_idx, last_idx) + 1)
            test_ids = slice(
                end_train_idx + predict_lag + 1,
                min(end_train_idx + predict_lag + predict_size, last_idx) + 1,
            )
            yield train_ids, test_ids

    @staticmethod
    def _to_points(n: Union[int, float], n_total_points: int) -> Optional[int]:
        if isinstance(n, int):
            if n >= n_total_points:
                raise AssertionError(f"{n} >= {n_total_points} (must be less)")
            n_points = n
        elif isinstance(n, float):
            if n >= 1.0:
                raise AssertionError(f"{n} >= 1.0 (must be less)")
            n_points = int(n * n_total_points)
        else:
            raise ValueError(f"Type of {n} must be int or float")
        return n_points

    def split(self, X, y=None, groups=None):
        n_total = len(X)
        return self._cv_gen(
            last_idx=n_total - 1,
            test_size=self._to_points(self.test_size, n_total),
            train_size=(
                None if self.train_size is None else self._to_points(self.train_size, n_total)
            ),
            predict_size=self._to_points(self.predict_size, n_total),
            predict_step=self._to_points(self.predict_step, n_total),
            predict_lag=self._to_points(self.predict_lag, n_total),
            drop_first_points=self._to_points(self.drop_first_points, n_total),
            drop_last_points=self._to_points(self.drop_last_points, n_total),
        )

    def get_n_splits(self, X, y=None, groups=None):
        n_total = len(X)
        n_splits = self._to_points(self.test_size, n_total) // self._to_points(
            self.predict_step, n_total
        )
        return n_splits
