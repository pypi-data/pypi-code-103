from selenious import WebDriverMixin
from selenious.webelement import SeleniousWrapWebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import Remote


class MockWebElement:
    def __init__(self, *args, side_effect=None, parent=None, **kwargs):
        self._id = "MockWebElement"
        self._w3c = False
        self.parent = parent
        self.side_effect = side_effect
        self.calls = [
            {"name": "__init__", "args": args, "kwargs": kwargs, "retval": "self"}
        ]
        return

    def __repr__(self):
        return "MockWebElement"

    def find_element(self, *args, **kwargs):
        return mock_fe(self, "find_element", *args, **kwargs)

    def find_elements(self, *args, **kwargs):
        return mock_fe(self, "find_elements", *args, **kwargs)

    def mock_monotonic(self, *args, **kwargs):
        return mock_fe(self, "monotonic", *args, **kwargs)

    def mock_next_state(self, *args, **kwargs):
        return mock_fe(self, "mock_next_state", *args, **kwargs)

    def mock_sleep(self, *args, **kwargs):
        return mock_fe(self, "mock_sleep", *args, **kwargs)

    def click(self, *args, **kwargs):
        return mock_fe(self, "click", *args, **kwargs)

    def mock_recover(self, *args, **kwargs):
        return mock_fe(self, "recover", *args, **kwargs)

    def mock_element(self, id_=""):
        return WebElement(parent=self, id_=id_)


def mock_fe(self, name, *args, **kwargs):
    if self.side_effect:
        index = min(len(self.side_effect) - 1, len(self.calls) - 1)
        retval = self.side_effect[index]
    elif name.startswith("find_elements"):
        retval = [SeleniousWrapWebElement(MockWebElement(parent=self))]
    else:
        retval = SeleniousWrapWebElement(MockWebElement(parent=self))

    self.calls.append({"name": name, "args": args, "kwargs": kwargs, "retval": retval})

    if retval == NoSuchElementException:
        raise NoSuchElementException

    return retval


class MockWebDriver(Remote):
    def __init__(self, *args, side_effect=None, **kwargs):
        self.side_effect = side_effect
        self.calls = [
            {"name": "__init__", "args": args, "kwargs": kwargs, "retval": "self"}
        ]

    def find_element(self, *args, **kwargs):
        return mock_fe(self, "find_element", *args, **kwargs)

    def find_elements(self, *args, **kwargs):
        return mock_fe(self, "find_elements", *args, **kwargs)

    def implicitly_wait(self, *args, **kwargs):
        return mock_fe(self, "implicitly_wait", *args, **kwargs)

    def mock_monotonic(self, *args, **kwargs):
        return mock_fe(self, "monotonic", *args, **kwargs)

    def mock_next_state(self, *args, **kwargs):
        return mock_fe(self, "mock_next_state", *args, **kwargs)

    def mock_sleep(self, *args, **kwargs):
        return mock_fe(self, "mock_sleep", *args, **kwargs)

    def mock_element(self, id_=""):
        return WebElement(parent=self, id_=id_)


class MockDriver(WebDriverMixin, MockWebDriver):
    pass
