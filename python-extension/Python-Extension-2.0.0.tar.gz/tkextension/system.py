# -*- coding: utf-8  -*-

from pyextension import *

def opensource(module="tkextension"):
    if module == "tkextension" or module == "__init__":
        with open("__init__.py") as file:
            return file.read()
    elif module == "test":
        with open("test.py") as file:
            return file.read()
    elif module == "tix":
        with open("tix/__init__.py") as file:
            return file.read()
    elif module == "tix.blackboard" or module == "blackboard":
        with open("tix/blackboard.py") as file:
            return file.read()
    elif module == "tix.card" or module == "card":
        with open("tix/card.py") as file:
            return file.read()
    elif module == "tix.filedialog" or module == "filedialog":
        with open("tix/filedialog.py") as file:
            return file.read()
    elif module == "tix.listmenu" or module == "listmenu":
        with open("tix/listmenu.py") as file:
            return file.read()
    elif module == "tix.timer" or module == "timer":
        with open("tix/timer.py") as file:
            return file.read()
    elif module == "turtledrawer":
        with open("turtledrawer.py") as file:
            return file.read()
    elif module == "system":
        with open("system.py") as file:
            return file.read()
    else:
        raise AttributeError("\"opensource\" object has no attribute \"%s\"" % module)
