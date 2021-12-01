# This file is placed in the Public Domain.


import queue
import threading


from .dpt import Dispatcher
from .obj import Object
from .thr import launch
from .utl import get_exception


class Restart(Exception):

    pass


class Stop(Exception):

    pass


class Loop(Object):

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.speed = "normal"
        self.stopped = threading.Event()

    def do(self, e):
        Dispatcher.dispatch(self, e)

    def error(self, txt):
        pass

    def loop(self):
        dorestart = False
        self.stopped.clear()
        while not self.stopped.isSet():
            e = self.queue.get()
            try:
                self.do(e)
            except Restart:
                dorestart = True
                break
            except Stop:
                break
            except Exception:
                self.error(get_exception())
        if dorestart:
            self.restart()

    def restart(self):
        self.stop()
        self.start()

    def put(self, e):
        self.queue.put_nowait(e)

    def start(self):
        launch(self.loop)
        return self

    def stop(self):
        self.stopped.set()
        self.queue.put(None)
