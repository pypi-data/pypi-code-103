import threading
import time

import pytest

from app.backtest.exceptions import EndOfDayError
from app.backtest.feed import Feed


def test_start_stop():
    feed = Feed()
    feed.stop()


def test_timeout():
    feed = Feed()
    feed.lock.clear()

    def set_lock(lock):
        time.sleep(1.0)
        lock.set()

    t1 = threading.Thread(target=set_lock, args=(feed.lock,))
    t1.start()
    feed.wait_for_new_day()


def test_timeout_exception():
    feed = Feed()
    feed.lock.clear()
    feed._timeouts = 2
    with pytest.raises(EndOfDayError, match="timeout when waiting for new day"):
        feed.wait_for_new_day()
