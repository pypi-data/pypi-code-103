from collections import deque
from itertools import islice, count

from .base import RollingObject


class StringContains(RollingObject):
    """
    Iterator object that computes whether a string
    appears in a rolling window over a Python iterable.

    Parameters
    ----------

    iterable : any iterable object
    window_size : integer, the size of the rolling
        window moving over the iterable
    search_term: str, word to search for in the window

    Complexity
    ----------

    Update time:  O(1)
    Memory usage: O(1)

    Examples
    --------

    >>> import rolling
    >>> text = "arollbbbrol"
    >>> r_contains = rolling.StringContains(text, 4, "roll")
    >>> next(r_contains)
    False
    >>> next(r_contains)
    True

    """
    def _init_fixed(self, iterable, window_size, search_term, **kwargs):

        if len(search_term) > window_size:
            raise

        if not search_term:
            raise

        self._search_term = search_term

        # start index of the last match of the search term
        self._last_word_match_start = -1

        # The current match
        self._match_start = -1
        self._next_to_match = 0

        self._i = -1
        self._obs = 1

        for new in islice(self._iterator, window_size - 1):
            self._add_new(new)

    def _init_variable(self, iterable, window_size, **kwargs):
        self._i = -1
        self._obs = 0
        self._last_false = -1

    def _add_new(self, new):
        self._i += 1
        self._obs += 1
        if not new:
            self._last_false = self._i

    def _update_window(self, new):
        self._i += 1
        if not new:
            self._last_false = self._i

    def _remove_old(self):
        self._obs -= 1

    @property
    def current_value(self):
        return self._i - self._obs >= self._last_false
