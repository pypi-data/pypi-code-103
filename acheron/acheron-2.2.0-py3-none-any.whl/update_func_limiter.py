import logging
import time

from PySide2 import QtCore

logger = logging.getLogger(__name__)


class UpdateFuncLimiter:
    def __init__(self, set_func, update_ms, parent=None):
        self.set_func = set_func
        self.update_delay = update_ms / 1000

        self.last_set_time = None
        self.next_value = None

        self.timer = QtCore.QTimer(parent)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timer_cb)

    def update(self, value):
        if self.next_value == value and value is not None:
            return

        self.next_value = value

        if not self.timer.isActive():
            now = time.monotonic()
            if (self.last_set_time is None or
                    self.last_set_time + self.update_delay < now):
                # update now
                self.last_set_time = now
                self.set_func(value)
            else:
                # start the timer
                delay = (self.last_set_time + self.update_delay) - now
                delay_ms = max(0, int(delay * 1000))
                self.timer.start(delay_ms)

    def timer_cb(self):
        self.last_set_time = time.monotonic()
        self.set_func(self.next_value)
