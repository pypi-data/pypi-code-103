# This file is placed in the Public Domain.


import threading


from .obj import Object
from .opt import Output
from .prs import parse as pparse
from .utl import getmain


class Event(Object):

    def __init__(self):
        super().__init__()
        self.channel = None
        self.done = threading.Event()
        self.orig = None
        self.origin = None
        self.prs = Object()
        self.result = []
        self.type = "event"
        self.txt = None

    def bot(self):
        k = getmain("k")
        return k.byorig(self.orig)

    def parse(self):
        pparse(self.prs, self.txt)

    def ready(self):
        self.done.set()

    def reply(self, txt):
        self.result.append(txt)

    def say(self, txt):
        k = getmain("k")
        k.say(self.orig, self.channel, txt)

    def show(self):
        bot = self.bot()
        if bot.speed == "slow" and len(self.result) > 3:
            Output.append(self.channel, self.result)
            self.say("%s lines in cache, use !mre" % len(self.result))
            return
        for txt in self.result:
            self.say(txt)

    def wait(self, timeout=1.0):
        self.done.wait(timeout)
