__title__ = "Hcl.py"
__author__ = "Kapidev, Slimakoi and Syscall0, Oustex"
__license__ = "None"
__copyright__ = "Copyright 2020-2022 Kapidev, Slimakoi, Syscall0 and Oustex"
__version__ = "0.8.2"

from json import JSONDecodeError
from .client import Client
from .subclient import SubClient
from .acm import ACM
from .socket import Callbacks, SocketHandler
from .src import didgen, exceptions, exceptions_v2, headers, objects, debugs
from requests import get

try:
    __newest__ = get("https://pypi.python.org/pypi/Hcl.py/json").json()["info"]["version"]


    def colored(r, g, b, text, rb : int = None, gb : int = None, bb : int = None):
        # print(colored(200, 20, 200, 0, 0, 0, "Hello World"))
        if rb is None and gb is None and bb is None:
            return "\033[38;2;{};{};{}m{}\033[0m".format(r, g, b, text)
        else:
            return "\033[38;2;{};{};{}m\033[48;2;{};{};{}m{}\033[0m".format(r, g, b, rb, gb, bb, text)

    if __version__ != __newest__:
        print(colored(255, 255, 255, rb=154, gb=0, bb=243, text=" UPDATE ❯ ") + colored(186, 165, 234, rb=36, gb=36, bb=36, text=f" New {__title__} version available! (Latest: {__newest__}, Using: {__version__}) ") + "\n")
except JSONDecodeError:
    pass
