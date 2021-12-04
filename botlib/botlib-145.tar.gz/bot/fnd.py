# This file is in the Public Domain.


import os
import time


from .dbs import find, fntime
from .obj import Cfg, keys
from .ofn import fmt
from .tms import elapsed


def listfiles(workdir):
    path = os.path.join(Cfg.wd, "store")
    if not os.path.exists(path):
        return []
    return sorted(os.listdir(path))


def fnd(event):
    if not event.prs.args:
        fls = listfiles(Cfg.wd)
        if fls:
            event.reply(",".join(sorted({x.split(".")[-1].lower()
                        for x in fls})))
        return
    otype = event.prs.args[0]
    nr = -1
    if "a" in event.prs.opts:
        args = None
    else:
        args = list(event.prs.gets)
        try:
            args.extend(event.prs.args[1:])
        except IndexError:
            pass
    got = False
    for fn, o in find(otype, event.prs.gets, event.prs.index, event.prs.timed):
        nr += 1
        txt = "%s %s" % (str(nr), fmt(o, args or keys(o),
                                      skip=keys(event.prs.skip)))
        if "t" in event.prs.opts:
            txt = txt + " %s" % (elapsed(time.time() - fntime(fn)))
        got = True
        event.reply(txt)
    if not got:
        event.reply("no result")
