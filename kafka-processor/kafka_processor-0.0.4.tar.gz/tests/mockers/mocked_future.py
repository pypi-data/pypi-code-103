from unittest.mock import MagicMock
from kafka.future import Future


class MockedFuture(MagicMock, Future):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_done = False
        self._tries_count = 0

    @property
    def is_done(self):
        if self._tries_count == 3:
            self._is_done = True

        self._tries_count += 1

        return self._is_done
