#!/usr/bin/env python

"""Tests for `selenious` decorators package."""

import os
import time

import pytest
from selenious.webdriver import Chrome
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)


class Test:
    def setup_method(self, test_method):
        file = os.path.join(os.getcwd(), "tests", "integration.html")
        assert os.path.exists(file)
        self.path = "file://{}".format(file)
        self.browser = Chrome()

    def teardown_method(self, test_method):
        self.browser.close()

    def sleep2(self, recover_data):
        time.sleep(2)
        self.sleep_calls = getattr(self, "sleep_calls", 0) + 1

    def noop(self, recover_data):
        self.noop_calls = getattr(self, "noop_calls", 0) + 1

    def test_click_recover(self):
        self.browser.get(self.path)
        target = self.browser.find_element_by_id("target")
        with pytest.raises(ElementClickInterceptedException):
            target.click()

        def recover(recover_data):
            recover_data.webdriver.execute_script(
                "document.getElementById('cover').style.display = 'none';"
            )

        self.browser.recover = recover
        target.click()

    def test_ui_get(self):
        self.browser.get(self.path)
        ul = self.browser.find_element_by_xpath("/html/body/ul")

        # Timeout should wait 2 seconds for #li-2000
        ul.find_element_by_id("li-2000", timeout=2)

        # We should have 3 items visible now
        assert len(ul.find_elements_by_css_selector("li", min=3)) == 3

        # And we shouldn't yet have 4
        with pytest.raises(NoSuchElementException):
            ul.find_elements_by_css_selector("li", min=4)

        # Speed up the polling and get us synchronized to close to after the fourth
        ul.poll_frequency = 0.1
        assert len(ul.find_elements_by_css_selector("li", min=4, timeout=1)) == 4

        # Delay to close to the time the fourth will be seen
        time.sleep(0.7)

        # Make sure it isn't available yet
        assert len(ul.find_elements_by_css_selector("li")) == 4

        # Test that even though the min is visible, the debounce make us wait for 5
        assert len(ul.find_elements_by_css_selector("li", min=4, debounce=0.5)) == 5

        # Get us back to in sync with the 6th li
        assert len(ul.find_elements_by_css_selector("li", min=6, timeout=1)) == 6

        # Now make sure that even with no timeout, we run the recover and find 8
        # after recover is run
        assert (
            len(ul.find_elements_by_css_selector("li", min=7, recover=self.sleep2)) == 8
        )
        assert self.sleep_calls == 1

        # With no timeout, recover should only be run once more and finish quickly
        with pytest.raises(NoSuchElementException):
            ul.find_elements_by_css_selector("li", min=100, recover=self.noop)
        assert self.noop_calls == 1

        # This all should have happend fast enough that we are still at 8 elements
        assert len(ul.find_elements_by_css_selector("li")) == 8

    def test_browser_find(self):
        self.browser.get(self.path)
        # Timeout should wait 2 seconds for #li-2000
        self.browser.find_element_by_id("li-2000", timeout=2)

        # We should have 3 items visible now
        assert len(self.browser.find_elements_by_css_selector("li", min=3)) == 3

        # And we shouldn't yet have 4
        with pytest.raises(NoSuchElementException):
            self.browser.find_elements_by_css_selector("li", min=4)

        # Speed up the polling and get us synchronized to close to after the fourth
        self.browser.poll_frequency = 0.1
        assert (
            len(self.browser.find_elements_by_css_selector("li", min=4, timeout=1)) == 4
        )

        # Delay to close to the time the fourth will be seen
        time.sleep(0.7)

        # Make sure it isn't available yet
        assert len(self.browser.find_elements_by_css_selector("li")) == 4

        # Test that even though the min is visible, the debounce make us wait for 5
        assert (
            len(self.browser.find_elements_by_css_selector("li", min=4, debounce=0.5))
            == 5
        )

        # Get us back to in sync with the 6th li
        assert (
            len(self.browser.find_elements_by_css_selector("li", min=6, timeout=1)) == 6
        )

        # Now make sure that even with no timeout, we run the recover and find 8
        # after recover is run
        assert (
            len(
                self.browser.find_elements_by_css_selector(
                    "li", min=7, recover=self.sleep2
                )
            )
            == 8
        )
        assert self.sleep_calls == 1

        # With no timeout, recover should only be run once more and finish quickly
        with pytest.raises(NoSuchElementException):
            self.browser.find_elements_by_css_selector("li", min=100, recover=self.noop)
        assert self.noop_calls == 1

        # This all should have happend fast enough that we are still at 8 elements
        assert len(self.browser.find_elements_by_css_selector("li")) == 8
