#!/usr/bin/env python

"""Tests for `selenious` decorators package."""

import pytest
from unittest.mock import MagicMock
from selenium.common.exceptions import NoSuchElementException

from .mock_webdriver import MockDriver, MockWebElement


def test_all_find_el_are_wrapped(snapshot):
    """All find_* functions are wrapped."""
    el = MockDriver().find_element_by_id("ignored")
    result = []
    result.append(el.find_element_by_id("ignored"))
    result.append(el.find_elements_by_id("ignored"))
    result.append(el.find_element_by_xpath("ignored"))
    result.append(el.find_elements_by_xpath("ignored"))
    result.append(el.find_element_by_link_text("ignored"))
    result.append(el.find_elements_by_link_text("ignored"))
    result.append(el.find_element_by_partial_link_text("ignored"))
    result.append(el.find_elements_by_partial_link_text("ignored"))
    result.append(el.find_element_by_name("ignored"))
    result.append(el.find_elements_by_name("ignored"))
    result.append(el.find_element_by_tag_name("ignored"))
    result.append(el.find_elements_by_tag_name("ignored"))
    result.append(el.find_element_by_class_name("ignored"))
    result.append(el.find_elements_by_class_name("ignored"))
    result.append(el.find_element_by_css_selector("ignored"))
    result.append(el.find_elements_by_css_selector("ignored"))
    result.append(el.find_element("ignored", "twice"))
    result.append(el.find_elements("ignored", "twice"))
    snapshot.assert_match(result)
    snapshot.assert_match(el.calls)


def test_time_validators():
    driver = MockDriver()
    el = driver.find_element_by_id("ignored")
    driver.implicitly_wait(0.4)
    with pytest.raises(TypeError, match="timeout 0.1"):
        driver.timeout = 0.1
    with pytest.raises(TypeError, match="timeout 0.1"):
        el.timeout = 0.1

    driver = MockDriver()
    el = driver.find_element_by_id("ignored")
    driver.implicitly_wait(0.4)
    with pytest.raises(TypeError, match="poll_frequency 0.3"):
        driver.poll_frequency = 0.3
    with pytest.raises(TypeError, match="poll_frequency 0.3"):
        el.poll_frequency = 0.3


def test_setters():
    driver = MockDriver(
        timeout=1, implicitly_wait=0.1, debounce=1, recover=lambda: 1, poll_frequency=1
    )
    el = driver.find_element_by_id("ignored")

    el.timeout = 1
    assert el.timeout == 1
    el.debounce = 2
    assert el.debounce == 2
    el.recover = test_setters
    assert el.recover == test_setters
    el.poll_frequency = 1
    assert el.poll_frequency == 1


def test_recover_raises_exception():
    def except_recover(recover_data):
        raise NoSuchElementException("new exception")

    driver = MockDriver()
    el = driver.find_element_by_id("ignored")
    el.recover = except_recover
    el.side_effect = [NoSuchElementException, []]
    with pytest.raises(NoSuchElementException, match="new exception"):
        el.find_element_by_id("_")

    # The recover should have been restored
    assert el.recover == except_recover

    with pytest.raises(NoSuchElementException, match="new exception"):
        el.find_elements_by_id("_", min=1)

    # The recover should have been restored
    assert el.recover == except_recover


@pytest.fixture
def el_plus_decorator_mocks(mocker):
    driver = MockDriver(mocker)
    el = driver.find_element_by_id("ignored")
    mocker.patch("selenious.decorators.monotonic", el.mock_monotonic)
    mocker.patch("selenious.decorators.sleep", el.mock_sleep)
    mocker.patch("selenious.decorators._find_element_next_state", el.mock_next_state)
    mocker.patch("selenious.decorators._find_elements_next_state", el.mock_next_state)
    return el


def test_find_element_decorator_raise(snapshot, el_plus_decorator_mocks):
    """Tests the state machine to test that the driver handles a raise"""
    el = el_plus_decorator_mocks
    el.side_effect = [0, NoSuchElementException, 99, ("raise", MockWebElement())]
    with pytest.raises(NoSuchElementException):
        el.find_element_by_id("_")

    snapshot.assert_match(el.calls)


def test_find_element_decorator_recover_or_raise_null(
    snapshot, el_plus_decorator_mocks
):
    """Tests the state machine to test that the el handles a recover_or_raise with
    null recover"""
    el = el_plus_decorator_mocks
    el.timeout = 200
    el.side_effect = [
        0,
        NoSuchElementException,
        99,
        ("recover_or_raise", MockWebElement()),
    ]
    with pytest.raises(NoSuchElementException):
        el.find_element_by_id("_")

    snapshot.assert_match(el.calls)


def test_find_element_decorator_recover_or_raise_nonnull(
    snapshot, el_plus_decorator_mocks
):
    """Tests the state machine to test that the el handles a recover_or_raise with
    nonnull recover"""
    el = el_plus_decorator_mocks
    el.timeout = 200
    el.recover = MagicMock()
    el.side_effect = [
        0,
        NoSuchElementException,
        99,
        ("recover_or_raise", MockWebElement()),
        None,
        MockWebElement(),
    ]
    el.find_element_by_id("_")
    el.recover.assert_called()

    snapshot.assert_match(el.calls)


def test_find_elements_decorator_debounce(snapshot, el_plus_decorator_mocks):
    """Tests the state machine to test that the el handles a debounce,"""
    el = el_plus_decorator_mocks
    el.debounce = 0.1
    el.recover = MagicMock()
    el.side_effect = [
        0,
        [],
        1,
        ("debounce", MockWebElement()),
        None,
        [MockWebElement(), MockWebElement(), MockWebElement()],
        99,
        ("success", MockWebElement()),
    ]
    el.find_elements_by_id("_", min=3, timeout=200)
    el.recover.assert_not_called()

    snapshot.assert_match(el.calls)


def test_find_elements_decorator_recover_or_raise_recover(
    snapshot, el_plus_decorator_mocks
):
    """Tests the state machine to test that the el handles a recover_or_raise with
    nonnull recover"""
    el = el_plus_decorator_mocks
    el.debounce = 0.1
    el.recover = MagicMock()
    el.side_effect = [
        0,
        [],
        1,
        ("recover_or_raise", MockWebElement()),
        None,
        [MockWebElement(), MockWebElement(), MockWebElement()],
        99,
        ("success", MockWebElement()),
    ]
    el.find_elements_by_id("_", min=3, timeout=200)
    el.recover.assert_called()

    snapshot.assert_match(el.calls)


def test_find_elements_decorator_recover_or_raise_no_recover(
    snapshot, el_plus_decorator_mocks
):
    """Tests the state machine to test that the el handles a recover_or_raise
    with null recover"""
    el = el_plus_decorator_mocks
    el.debounce = 0.1
    el.side_effect = [0, [], 1, ("recover_or_raise", MockWebElement())]
    with pytest.raises(NoSuchElementException):
        el.find_elements_by_id("_", min=3, timeout=200)

    snapshot.assert_match(el.calls)


def test_find_elements_decorator_raise(snapshot, el_plus_decorator_mocks):
    """Tests the state machine to test that the el handles a raise"""
    el = el_plus_decorator_mocks
    el.debounce = 0.1
    el.side_effect = [0, [], 1, ("raise", MockWebElement())]
    with pytest.raises(NoSuchElementException):
        el.find_elements_by_id("_", min=3, timeout=200)

    snapshot.assert_match(el.calls)


def test_find_elements_decorator_recover_and_retry_recover(
    snapshot, el_plus_decorator_mocks
):
    """Tests the state machine to test that the el handles a recover_and_retry
    with recover"""
    el = el_plus_decorator_mocks
    el.recover = MagicMock()
    el.debounce = 0.1
    el.side_effect = [
        0,
        [],
        1,
        ("recover_and_retry", MockWebElement()),
        None,
        [MockWebElement(), MockWebElement(), MockWebElement()],
        99,
        ("success", MockWebElement()),
    ]
    el.find_elements_by_id("_", min=3, timeout=200)
    el.recover.assert_called()

    snapshot.assert_match(el.calls)


def test_find_elements_decorator_recover_and_retry_no_recover(
    snapshot, el_plus_decorator_mocks
):
    """Tests the state machine to test that the el handles a recover_and_retry
    with recover"""
    el = el_plus_decorator_mocks
    el.debounce = 0.1
    el.side_effect = [
        0,
        [],
        1,
        ("recover_and_retry", MockWebElement()),
        None,
        [MockWebElement(), MockWebElement(), MockWebElement()],
        99,
        ("success", MockWebElement()),
    ]
    el.find_elements_by_id("_", min=3, timeout=200)

    snapshot.assert_match(el.calls)

    # return ("recover_and_retry", min(time_left, poll_frequency))


def test_click_recover_succeeds(snapshot, el_plus_decorator_mocks):
    """Tests the el state machine recover function succeeds"""
    el = el_plus_decorator_mocks
    el.recover = el.mock_recover
    el.side_effect = [
        NoSuchElementException,
        None,
        None,
    ]
    el.click()

    snapshot.assert_match(el.calls)


def test_click_recover_fails(snapshot, el_plus_decorator_mocks):
    """Tests the el state machine recover function didn't help"""
    el = el_plus_decorator_mocks
    el.recover = el.mock_recover
    el.side_effect = [
        NoSuchElementException,
        None,
        NoSuchElementException,
    ]
    with pytest.raises(NoSuchElementException):
        el.click()

    snapshot.assert_match(el.calls)


def test_click_no_recover_excepts(snapshot, el_plus_decorator_mocks):
    """Tests the el state machine without recover raises exception"""
    el = el_plus_decorator_mocks
    el.side_effect = [
        NoSuchElementException,
    ]
    with pytest.raises(NoSuchElementException):
        el.click()

    snapshot.assert_match(el.calls)
