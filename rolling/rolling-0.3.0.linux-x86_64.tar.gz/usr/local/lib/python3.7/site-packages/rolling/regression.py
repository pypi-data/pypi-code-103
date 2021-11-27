from collections import Counter, deque
from itertools import islice

from .base import RollingObject


class OrdinaryLeastSquares(RollingObject):
    """
    Iterator object that computes the 

    Parameters
    ----------

    iterable : any iterable object
    window_size : integer, the size of the rolling
        window moving over the iterable

    Complexity
    ----------

    Update time:  O(1)
    Memory usage: O(k)

    where k is the size of the rolling window

    Examples
    --------

    >>> import rolling
    >>> seq = [1, 2, 3, 3, 3, 2, 1]

    """
    def _init_common(self, iterable, window_size):

        if window_size == 1:
            raise ValueError("window_size must be greater than 1")

        # x-axis values, starting at zero
        self._x = 0
        self._x_minus_x_mean = 0
        self._sum_x_minus_x_mean_squared = 0

        # y-axis values
        self._y_values = deque(maxlen=window_size)
        self._y_mean = 0

        self._sum_xy_minus_xy_mean_squared = 0

        self._intercept = 0
        self._gradient = 0

    def _init_fixed(self, iterable, window_size, **kwargs):
        self._init_common(iterable, window_size)
        for value in islice(self._iterator, window_size - 1):
            self._add_new(value)

    def _init_variable(self, iterable, window_size, **kwargs):
        self._init_common(iterable, window_size)

    def _update_window(self, new):
        old_y = self._y_values.popleft()
        self._y_values.append(new)

        delta = new - old_y
        delta_old = old_y - self._y_mean
        self._mean += delta / self._obs

    def _add_new(self, new):
        self._y_values.append(new)

        # update x mean
        delta = new - self._mean
        self._mean += delta / self._obs




        # update y mean

        self._x += 1

    def _remove_old(self):

        delta = old - self._mean
        self._mean -= delta / self._obs


    @property
    def current_value(self):
        if self._obs <= 1:
            return None, None
        return self._gradient, self._intercept

    @property
    def _obs(self):
        return len(self._x_values)
