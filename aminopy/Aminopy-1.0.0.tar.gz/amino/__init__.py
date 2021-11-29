__title__ = 'Aminopy'
__author__ = 'Oustex'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021 Oustex'
__version__ = '1.0.0'

from .acm import ACM
from .client import Client
from .sub_client import SubClient
from .socket import Callbacks, SocketHandler
from json.decoder import JSONDecodeError
from .src import device, exceptions
from requests import get
from json import loads

try:
    __newest__ = loads(get("https://pypi.python.org/pypi/Amimopy/json").text)["info"]["version"]
    if __version__ != __newest__:
        print(exceptions.LibraryUpdateAvailable(f"New version of {__title__} available: {__newest__} (Using {__version__})"))
except JSONDecodeError:
    pass
