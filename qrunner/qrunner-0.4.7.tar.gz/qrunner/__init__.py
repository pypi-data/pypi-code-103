from .config import Browser
from .utils.log import logger
from .core.remote import Device
from .core.ios.driver import IosDriver
from .core.ios.wda_server import WDAServer
from .core.h5.driver import H5Driver
from .core.web.driver import WebDriver
from .core.android.driver import AndroidDriver
from .core.android.element import Element as AdrElement, Page as AdrPage
from .core.ios.element import Element as IosElement, Page as IosPage
from .core.web.element import Element as WebElement, Page as WebPage


__version__ = "0.4.7"
__description__ = "Cross platform ui test framework."
