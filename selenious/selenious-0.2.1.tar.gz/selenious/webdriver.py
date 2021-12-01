from .webdriver_mixin import WebDriverMixin

from selenium.webdriver import Remote
from selenium import webdriver


Remote = type("Remote", (WebDriverMixin, Remote), {})

try:
    Firefox = type("Firefox", (WebDriverMixin, webdriver.Firefox), {})
    FirefoxProfile = webdriver.FirefoxProfile
    FirefoxOptions = webdriver.FirefoxOptions
except AttributeError:
    pass

try:
    Chrome = type("Chrome", (WebDriverMixin, webdriver.Chrome), {})
    ChromeOptions = webdriver.ChromeOptions
except AttributeError:
    pass

try:
    Ie = type("Ie", (WebDriverMixin, webdriver.Ie), {})
    IeOptions = webdriver.IeOptions
except AttributeError:
    pass

try:
    Edge = type("Edge", (WebDriverMixin, webdriver.Edge), {})
    EdgeOptions = webdriver.EdgeOptions
except AttributeError:
    pass

try:
    ChromiumEdge = type("ChromiumEdge", (WebDriverMixin, webdriver.ChromiumEdge), {})
except AttributeError:
    pass

try:
    Opera = type("Opera", (WebDriverMixin, webdriver.Opera), {})
except AttributeError:
    pass

try:
    Safari = type("Safari", (WebDriverMixin, webdriver.Safari), {})
except AttributeError:
    pass

try:
    Blackberry = type("Blackberry", (WebDriverMixin, webdriver.Blackberry), {})
except AttributeError:
    pass

try:
    PhantomJS = type("PhantomJS", (WebDriverMixin, webdriver.PhantomJS), {})
except AttributeError:
    pass

try:
    Android = type("Android", (WebDriverMixin, webdriver.Android), {})
except AttributeError:
    pass

try:
    WebKitGTK = type("WebKitGTK", (WebDriverMixin, webdriver.WebKitGTK), {})
    WebKitGTKOptions = webdriver.WebKitGTKOptions
except AttributeError:
    pass

try:
    WPEWebKit = type("WPEWebKit", (WebDriverMixin, webdriver.WPEWebKit), {})
    WPEWebKitOptions = webdriver.WPEWebKitOptions
except AttributeError:
    pass

try:
    DesiredCapabilities = webdriver.DesiredCapabilities
except AttributeError:
    pass

try:
    ActionChains = webdriver.ActionChains
except AttributeError:
    pass

try:
    TouchActions = webdriver.TouchActions
except AttributeError:
    pass

try:
    Proxy = webdriver.Proxy
except AttributeError:
    pass

try:
    Keys = webdriver.Keys
except AttributeError:
    pass
