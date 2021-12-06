import logging
import time

from ..helper import colored


class TimeContext:
    """Timing a code snippet with a context manager """

    def __init__(self, msg: str, logger: 'logging.Logger' = None):
        """

        :param msg: the context/message
        :param logger: use existing logger or use naive :func:`print`

        Example:

        .. highlight:: python
        .. code-block:: python

            with TimeContext('loop'):
                do_busy()

        """
        self._msg = msg
        self._logger = logger
        self.duration = 0

    def __enter__(self):
        self.start = time.perf_counter()
        if self._logger:
            self._logger.info(f'{self._msg}...')
        else:
            print(self._msg, end=' ...\t', flush=True)
        return self

    def __exit__(self, typ, value, traceback):
        self.duration = time.perf_counter() - self.start
        if self._logger:
            self._logger.info('%s takes %3.3f secs' % (self._msg, self.duration))
        else:
            print(colored('    [%3.3f secs]' % self.duration, 'green'), flush=True)
