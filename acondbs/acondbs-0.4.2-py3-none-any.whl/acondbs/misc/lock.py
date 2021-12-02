import os
from pathlib import Path
import time
import contextlib

##__________________________________________________________________||
class lock:

    def __init__(self, path, timeout=None):
        self.path = Path(path)
        self.timeout = timeout
        self.locked = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def acquire(self):
        start_time = time.time()
        while True:
            if try_make_file(self.path):
                break
            if self.timeout is not None:
                if time.time() - start_time > self.timeout:
                    raise TimeOutAcquiringLock
            time.sleep(0.001)
        self.locked = True

    def release(self):
        if not self.locked:
            return

        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
        self.locked = False

##__________________________________________________________________||
class TimeOutAcquiringLock(Exception):
    pass

##__________________________________________________________________||
def try_make_file(path):
    """try to create a file atomically

    http://stackoverflow.com/questions/33223564/atomically-creating-a-file-if-it-doesnt-exist-in-python
    """
    try:
        os.open(path,  os.O_CREAT | os.O_EXCL)
        return True
    except FileExistsError:
        return False

##__________________________________________________________________||
