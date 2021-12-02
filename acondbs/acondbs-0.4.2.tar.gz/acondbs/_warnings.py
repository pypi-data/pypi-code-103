"""Configure the module warnings

https://docs.python.org/3/library/warnings.html

"""
import warnings
from pathlib import Path

##__________________________________________________________________||
_module_path = Path(__file__).resolve().parent.parent
# the path to the dir in which the module is installed,
# i.e., the one dir above the module path.


def format(message, category, filename, lineno, file=None, line=None):
    try:
        filename = Path(filename).resolve().relative_to(_module_path)
    except Exception:
        pass
    ret = "{}:{}: {}\n".format(filename, lineno, message)
    return ret


warnings.formatwarning = format

##__________________________________________________________________||
