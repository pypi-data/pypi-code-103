# This file is placed in the Public Domain.


from .dpt import Dispatcher
from .evt import Event
from .lop import Loop, Stop
from .ofn import getname


class Handler(Dispatcher, Loop):

    def __init__(self):
        Loop.__init__(self)
        Dispatcher.__init__(self)

    def event(self, txt):
        c = Event()
        c.type = "cmd"
        c.txt = txt or ""
        c.orig = repr(self)
        return c

    def handle(self, clt, e):
        Loop.put(self, e)

    def loop(self):
        while not self.stopped.isSet():
            try:
                txt = self.poll()
            except (Stop, ConnectionRefusedError, ConnectionResetError) as ex:
                self.error(str(ex))
                break
            if txt is None:
                self.error("%s stopped" % getname(self))
                break
            e = self.event(txt)
            if not e:
                self.error("%s stopped" % getname(self))
                return
            self.handle(self, e)

    def poll(self):
        return self.queue.get()
