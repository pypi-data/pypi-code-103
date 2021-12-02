#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Author:       CN-Robert-LIU
# Date:         2021-12-02
# Version:      V1.0.0
# Description:  Patch And Enhance Appium-Python-API
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver import WebElement as MobileWebElement
from typing import List, Union

__all__ = [
    'patch_find_element_by_id',
    'patch_find_elements_by_id',
    'patch_find_element_by_xpath',
    'patch_find_elements_by_xpath',
    'patch_find_element_by_link_text',
    'patch_find_elements_by_link_text',
    'patch_find_element_by_partial_link_text',
    'patch_find_elements_by_partial_link_text',
    'patch_find_element_by_name',
    'patch_find_elements_by_name',
    'patch_find_element_by_tag_name',
    'patch_find_elements_by_tag_name',
    'patch_find_element_by_class_name',
    'patch_find_elements_by_class_name',
    'patch_find_element_by_css_selector',
    'patch_find_elements_by_css_selector',
    'patch_swipe_ios_up',
    'patch_swipe_ios_down',
    'patch_swipe_ios_left',
    'patch_swipe_ios_right'
]


def patch_find_element_by_id(self, id_: str) -> MobileWebElement:
    """
    Finds an element by id.

    :Args:
     - id\\_ - The id of the element to be found.

    :Returns:
     - `appium.webdriver.webelement.WebElement`: The found element

    :Raises:
     - NoSuchElementException - if the element wasn't found

    :Usage:
        ::

            element = driver.find_element_by_id('foo')
    """
    return self.find_element(by=AppiumBy.ID, value=id_)


def patch_find_elements_by_id(self, id_: str) -> Union[List[MobileWebElement], List]:
    """
    Finds multiple elements by id.

    :Args:
     - id\\_ - The id of the elements to be found.

    :Returns:
     - :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`: The found elements
       empty list if not

    :Usage:
        ::

            elements = driver.find_elements_by_id('foo')
    """
    return self.find_elements(by=AppiumBy.ID, value=id_)


def patch_find_element_by_xpath(self, xpath: str) -> MobileWebElement:
    """
    Finds an element by xpath.

    :Args:
     - xpath - The xpath locator of the element to find.

    :Returns:
     - `appium.webdriver.webelement.WebElement`: The found element

    :Raises:
     - NoSuchElementException - if the element wasn't found

    :Usage:
        ::

            element = driver.find_element_by_xpath('//div/td[1]')
    """
    return self.find_element(by=AppiumBy.XPATH, value=xpath)


def patch_find_elements_by_xpath(self, xpath: str) -> Union[List[MobileWebElement], List]:
    """
    Finds multiple elements by xpath.

    :Args:
     - xpath - The xpath locator of the elements to be found.

    :Returns:
     - :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`: The found elements
       empty list if not

    :Usage:
        ::

            elements = driver.find_elements_by_xpath(
                "//div[contains(@class, 'foo')]")
    """
    return self.find_elements(by=AppiumBy.XPATH, value=xpath)


def patch_find_element_by_link_text(self, link_text: str) -> MobileWebElement:
    """
    Finds an element by link text.

    :Args:
     - link_text: The text of the element to be found.

    :Returns:
     - `appium.webdriver.webelement.WebElement`: The found element

    :Raises:
     - NoSuchElementException - if the element wasn't found

    :Usage:
        ::

            element = driver.find_element_by_link_text('Sign In')
    """
    return self.find_element(by=AppiumBy.LINK_TEXT, value=link_text)


def patch_find_elements_by_link_text(self, text: str) -> Union[List[MobileWebElement], List]:
    """
    Finds elements by link text.

    :Args:
     - link_text: The text of the elements to be found.

    :Returns:
     - :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`: The found elements
       empty list if not

    :Usage:
        ::

            elements = driver.find_elements_by_link_text('Sign In')
    """
    return self.find_elements(by=AppiumBy.LINK_TEXT, value=text)


def patch_find_element_by_partial_link_text(self, link_text: str) -> MobileWebElement:
    """
    Finds an element by a partial match of its link text.

    :Args:
     - link_text: The text of the element to partially match on.

    :Returns:
     - `appium.webdriver.webelement.WebElement`: The found element

    :Raises:
     - NoSuchElementException - if the element wasn't found

    :Usage:
        ::

            element = driver.find_element_by_partial_link_text('Sign')
    """
    return self.find_element(by=AppiumBy.PARTIAL_LINK_TEXT, value=link_text)


def patch_find_elements_by_partial_link_text(self, link_text: str) -> Union[List[MobileWebElement], List]:
    """
    Finds elements by a partial match of their link text.

    :Args:
     - link_text: The text of the element to partial match on.

    :Returns:
     - :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`: The found elements
       empty list if not

    :Usage:
        ::

            elements = driver.find_elements_by_partial_link_text('Sign')
    """
    return self.find_elements(by=AppiumBy.PARTIAL_LINK_TEXT, value=link_text)


def patch_find_element_by_name(self, name: str) -> MobileWebElement:
    """
    Finds an element by name.

    :Args:
     - name: The name of the element to find.

    :Returns:
     - `appium.webdriver.webelement.WebElement`: The found element

    :Raises:
     - NoSuchElementException - if the element wasn't found

    :Usage:
        ::

            element = driver.find_element_by_name('foo')
    """
    return self.find_element(by=AppiumBy.NAME, value=name)


def patch_find_elements_by_name(self, name: str) -> Union[List[MobileWebElement], List]:
    """
    Finds elements by name.

    :Args:
     - name: The name of the elements to find.

    :Returns:
     - :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`: The found elements
       empty list if not

    :Usage:
        ::

            elements = driver.find_elements_by_name('foo')
    """
    return self.find_elements(by=AppiumBy.NAME, value=name)


def patch_find_element_by_tag_name(self, name: str) -> MobileWebElement:
    """
    Finds an element by tag name.

    :Args:
     - name - name of html tag (eg: h1, a, span)

    :Returns:
     - `appium.webdriver.webelement.WebElement`: The found element

    :Raises:
     - NoSuchElementException - if the element wasn't found

    :Usage:
        ::

            element = driver.find_element_by_tag_name('h1')
    """
    return self.find_element(by=AppiumBy.TAG_NAME, value=name)


def patch_find_elements_by_tag_name(self, name: str) -> Union[List[MobileWebElement], List]:
    """
    Finds elements by tag name.

    :Args:
     - name - name of html tag (eg: h1, a, span)

    :Returns:
     - :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`: The found elements
       empty list if not

    :Usage:
        ::

            elements = driver.find_elements_by_tag_name('h1')
    """
    return self.find_elements(by=AppiumBy.TAG_NAME, value=name)


def patch_find_element_by_class_name(self, name: str) -> MobileWebElement:
    """
    Finds an element by class name.

    :Args:
     - name: The class name of the element to find.

    :Returns:
     - `appium.webdriver.webelement.WebElement`: The found element

    :Raises:
     - NoSuchElementException - if the element wasn't found

    :Usage:
        ::

            element = driver.find_element_by_class_name('foo')
    """
    return self.find_element(by=AppiumBy.CLASS_NAME, value=name)


def patch_find_elements_by_class_name(self, name: str) -> Union[List[MobileWebElement], List]:
    """
    Finds elements by class name.

    :Args:
     - name: The class name of the elements to find.

    :Returns:
     - :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`: The found elements
       empty list if not

    :Usage:
        ::

            elements = driver.find_elements_by_class_name('foo')
    """
    return self.find_elements(by=AppiumBy.CLASS_NAME, value=name)


def patch_find_element_by_css_selector(self, css_selector: str) -> MobileWebElement:
    """
    Finds an element by css selector.

    :Args:
     - css_selector - CSS selector string, ex: 'a.nav#home'

    :Returns:
     - `appium.webdriver.webelement.WebElement`: The found element

    :Raises:
     - NoSuchElementException - if the element wasn't found

    :Usage:
        ::

            element = driver.find_element_by_css_selector('#foo')
    """
    return self.find_element(by=AppiumBy.CSS_SELECTOR, value=css_selector)


def patch_find_elements_by_css_selector(self, css_selector: str) -> Union[List[MobileWebElement], List]:
    """
    Finds elements by css selector.

    :Args:
     - css_selector - CSS selector string, ex: 'a.nav#home'

    :Returns:
     - :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`: The found elements
       empty list if not

    :Usage:
        ::

            elements = driver.find_elements_by_css_selector('.foo')
    """
    return self.find_elements(by=AppiumBy.CSS_SELECTOR, value=css_selector)


def patch_swipe_ios_up(self, duration: int = 0):
    """
    Swipe Up For IOS Mobile.

    :Returns:
     - :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`: The found elements
       empty list if not

    :Usage:
        ::

            driver.swipe_ios_up()
    """
    import time
    self.execute_script("mobile:swipe", {"direction": "up"})
    if duration:
        time.sleep(duration)


def patch_swipe_ios_down(self, duration: int = 0):
    """
    Swipe Down For IOS Mobile.

    :Usage:
        ::

            driver.swipe_ios_down()
    """
    import time
    self.execute_script("mobile:swipe", {"direction": "down"})
    if duration:
        time.sleep(duration)


def patch_swipe_ios_left(self, duration: int = 0):
    """
    Swipe LEFT For IOS Mobile.

    :Usage:
        ::

            driver.swipe_ios_left()
    """
    import time
    self.execute_script("mobile:swipe", {"direction": "left"})
    if duration:
        time.sleep(duration)


def patch_swipe_ios_right(self, duration: int = 0):
    """
    Swipe Up For IOS Mobile.

    :Usage:
        ::

            driver.swipe_ios_right()
    """
    import time
    self.execute_script("mobile:swipe", {"direction": "right"})
    if duration:
        time.sleep(duration)


def patch_all():
    """
    Do all of the default monkey patching (calls every other applicable
    function in this module).

    :return:
        appium.webdriver.WebDriver as Remote
    """
    # from .webdriver import WebDriver as Remote
    from appium.webdriver.webdriver import WebDriver
    # Update Hot Pacth To webdriver API
    WebDriver.find_element_by_id = patch_find_element_by_id
    WebDriver.find_elements_by_id = patch_find_elements_by_id
    WebDriver.find_element_by_xpath = patch_find_element_by_xpath
    WebDriver.find_elements_by_xpath = patch_find_elements_by_xpath
    WebDriver.find_element_by_link_text = patch_find_element_by_link_text
    WebDriver.find_elements_by_link_text = patch_find_elements_by_link_text
    WebDriver.find_element_by_partial_link_text = patch_find_element_by_partial_link_text
    WebDriver.find_elements_by_partial_link_text = patch_find_elements_by_partial_link_text
    WebDriver.find_element_by_name = patch_find_element_by_name
    WebDriver.find_elements_by_name = patch_find_elements_by_name
    WebDriver.find_element_by_tag_name = patch_find_element_by_tag_name
    WebDriver.find_elements_by_tag_name = patch_find_elements_by_tag_name
    WebDriver.find_element_by_class_name = patch_find_element_by_class_name
    WebDriver.find_elements_by_class_name = patch_find_elements_by_class_name
    WebDriver.find_element_by_css_selector = patch_find_element_by_css_selector
    WebDriver.find_elements_by_css_selector = patch_find_elements_by_css_selector
    WebDriver.swipe_ios_up = patch_swipe_ios_up
    WebDriver.swipe_ios_down = patch_swipe_ios_down
    WebDriver.swipe_ios_left = patch_swipe_ios_left
    WebDriver.swipe_ios_right = patch_swipe_ios_right
    Remote = WebDriver
    return Remote
