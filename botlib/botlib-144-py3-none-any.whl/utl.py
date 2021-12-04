# This file is in the Public Domain.

import os
import sys
import traceback


def get_exception(txt="", sep=" "):
    exctype, excvalue, tb = sys.exc_info()
    trace = traceback.extract_tb(tb)
    result = []
    for elem in trace:
        if elem[0].endswith(".py"):
            plugfile = elem[0][:-3].split(os.sep)
        else:
            plugfile = elem[0].split(os.sep)
        mod = []
        for element in plugfile[:-2:-1]:
            mod.append(element.split(".")[-1])
        ownname = ".".join(mod[::-1])
        result.append("%s:%s" % (ownname, elem[1]))
    res = "%s %s: %s %s" % (sep.join(result), exctype, excvalue, str(txt))
    del trace
    return res


def getmain(name):
    return getattr(sys.modules["__main__"], name, None)


def kerror(txt):
    k = getmain("k")
    k.error(txt)


def klog(txt):
    k = getmain("k")
    k.log(txt)


def spl(txt):
    return [x for x in txt.split(",") if x]
