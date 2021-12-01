# This file is in the Public Domain.


from .obj import Object
from .ofn import save


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


def log(event):
    if not event.prs.rest:
        event.reply("log <txt>")
        return
    o = Log()
    o.txt = event.prs.rest
    save(o)
    event.reply("ok")

def tdo(event):
    if not event.prs.rest:
        event.reply("tdo <txt>")
        return
    o = Todo()
    o.txt = event.prs.rest
    save(o)
    event.reply("ok")
