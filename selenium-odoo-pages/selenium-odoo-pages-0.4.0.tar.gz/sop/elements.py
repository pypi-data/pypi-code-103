"""Generic Selenium elements which are not tied to odoo
"""
from typing import TYPE_CHECKING, Tuple

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC

if TYPE_CHECKING:
    from selenium import webdriver

Locator = Tuple[str, str]


class ClickElement(EC.element_to_be_clickable):
    """Try to click on an element until it works.

    This extend EC.element_to_be_clickable by catching ElementClickInterceptedException
    to make sure that there is no overlay stoping the click event propagation.

    usage:

    WebDriverWait(self.driver, timeout).until(
        ClickElement(A_LOCATOR)
    )
    """

    def __call__(self, driver: "webdriver"):
        try:
            element = super(ClickElement, self).__call__(driver)
            if element:
                ActionChains(element.parent).move_to_element(element).perform()
                element.click()
                return True
        except (ElementClickInterceptedException, StaleElementReferenceException):
            # we ignore if any overlay stop the event propagation
            return False
        return element


def expected_number_tabs(number: int):
    """An Expectation for checking how many tabs opened in browser."""

    def _predicate(driver):
        if len(driver.window_handles) == number:
            return number
        else:
            return False

    return _predicate


class TextToBeDifferentInElement:
    def __init__(self, locator: Locator, value: str):
        self.locator = locator
        self.value = value

    def __call__(self, driver: "webdriver"):
        element = driver.find_element(*self.locator)
        if not element:
            return False
        return element.text != self.value


class TextToBeEqual(object):
    """An expectation for checking if the given text property of the given
    object to be equal to the given expected value
    """

    def __init__(self, element: object, expected_value, property_attr="text"):
        self.element = element
        self.expected_value = expected_value
        self.property_attr = property_attr

    def __call__(self, driver):
        try:
            return self.expected_value == getattr(self.element, self.property_attr, "")
        except StaleElementReferenceException:
            return False
