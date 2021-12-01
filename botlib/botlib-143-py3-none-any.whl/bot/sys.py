# This file is in the Public Domain.


import threading
import time


from .obj import Object, get, update
from .ofn import getname, fmt
from .run import starttime
from .tbl import Table
from .tms import elapsed
from .utl import getmain


def __dir__():
    return ("cmd", "flt", "thr", "upt", "ver")


k = getmain("k")


def cmd(event):
    event.reply(",".join(sorted(list(Table.modnames))))


def flt(event):
    try:
        index = int(event.prs.args[0])
        event.reply(fmt(k.objs[index], skip=["queue", "ready", "iqueue"]))
        return
    except (TypeError, IndexError):
        pass
    event.reply(" | ".join([getname(o) for o in k.objs]))


def thr(event):
    result = []
    for t in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(t).startswith("<_"):
            continue
        o = Object()
        update(o, vars(t))
        if get(o, "sleep", None):
            up = o.sleep - int(time.time() - o.state.latest)
        else:
            up = int(time.time() - starttime)
        thrname = t.getName()
        if not thrname:
            continue
        if thrname:
            result.append((up, thrname))
    res = []
    for up, txt in sorted(result, key=lambda x: x[0]):
        res.append("%s(%s)" % (txt, elapsed(up)))
    if res:
        event.reply(" ".join(res))


def upt(event):
    event.reply("uptime is %s" % elapsed(time.time() - starttime))


def ver(event):
    event.reply("%s %s" % (k.cfg.name.upper(), k.cfg.version))
