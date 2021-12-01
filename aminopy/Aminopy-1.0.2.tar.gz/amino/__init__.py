__title__ = 'Aminopy'
__author__ = 'Oustex'
__license__ = 'Apache V2'
__copyright__ = 'Copyright 2021 Oustex'
__version__ = '1.0.2'

from .acm import ACM
from .client import Client
from .sub_client import SubClient
from .socket import Callbacks, SocketHandler
from .src import device, exceptions
from requests import get

__newest__ = get("https://pypi.python.org/pypi/Aminopy/json").json()["info"]["version"]
if __version__ != __newest__:
    print(exceptions.LibraryUpdateAvailable(f"New version of {__title__} available: {__newest__} (Using {__version__})"))
