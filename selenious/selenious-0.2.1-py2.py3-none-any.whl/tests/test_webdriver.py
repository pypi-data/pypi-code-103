#!/usr/bin/env python

"""Tests for `selenious` decorators package."""

import pytest
from unittest.mock import MagicMock
from selenium.common.exceptions import NoSuchElementException

from .mock_webdriver import MockDriver, MockWebElement
from selenious import decorators


def test_all_find_el_are_wrapped(snapshot):
    """All find_* functions are wrapped."""
    driver = MockDriver()
    result = []
    result.append(driver.find_element_by_id("ignored"))
    result.append(driver.find_elements_by_id("ignored"))
    result.append(driver.find_element_by_xpath("ignored"))
    result.append(driver.find_elements_by_xpath("ignored"))
    result.append(driver.find_element_by_link_text("ignored"))
    result.append(driver.find_elements_by_link_text("ignored"))
    result.append(driver.find_element_by_partial_link_text("ignored"))
    result.append(driver.find_elements_by_partial_link_text("ignored"))
    result.append(driver.find_element_by_name("ignored"))
    result.append(driver.find_elements_by_name("ignored"))
    result.append(driver.find_element_by_tag_name("ignored"))
    result.append(driver.find_elements_by_tag_name("ignored"))
    result.append(driver.find_element_by_class_name("ignored"))
    result.append(driver.find_elements_by_class_name("ignored"))
    result.append(driver.find_element_by_css_selector("ignored"))
    result.append(driver.find_elements_by_css_selector("ignored"))
    result.append(driver.find_element("ignored", "twice"))
    result.append(driver.find_elements("ignored", "twice"))
    snapshot.assert_match(result)
    snapshot.assert_match(driver.calls)


def test_time_validators():
    driver = MockDriver(poll_frequency=5, timeout=3)
    with pytest.raises(TypeError, match="timeout 3"):
        driver.implicitly_wait(4)

    driver = MockDriver()
    with pytest.raises(TypeError, match="poll_frequency 0.5"):
        driver.implicitly_wait(5)

    driver = MockDriver(poll_frequency=5, timeout=3)
    with pytest.raises(TypeError, match="timeout 3"):
        driver.implicitly_wait(5)

    driver = MockDriver()
    with pytest.raises(TypeError, match="poll_frequency 0.5"):
        driver.implicitly_wait(5)

    driver = MockDriver()
    driver.implicitly_wait(0.4)
    with pytest.raises(TypeError, match="timeout 0.1"):
        driver.timeout = 0.1

    driver = MockDriver()
    driver.implicitly_wait(0.4)
    with pytest.raises(TypeError, match="poll_frequency 0.3"):
        driver.poll_frequency = 0.3


def test_stripped_selenious_args(snapshot):
    driver = MockDriver(
        timeout=1, implicitly_wait=0.1, debounce=1, recover=lambda: 1, poll_frequency=1
    )
    snapshot.assert_match(driver.calls)


def test_setters():
    driver = MockDriver(
        timeout=1, implicitly_wait=0.1, debounce=1, recover=lambda: 1, poll_frequency=1
    )
    driver.timeout = 1
    assert driver.timeout == 1
    driver.debounce = 2
    assert driver.debounce == 2
    driver.recover = test_setters
    assert driver.recover == test_setters
    driver.poll_frequency = 1
    assert driver.poll_frequency == 1


def test_recover_raises_exception():
    def except_recover(recover_data):
        raise NoSuchElementException("new exception")

    driver = MockDriver(
        recover=except_recover,
    )
    driver.side_effect = [NoSuchElementException, []]
    with pytest.raises(NoSuchElementException, match="new exception"):
        driver.find_element_by_id("_")

    # The recover should have been restored
    assert driver.recover == except_recover

    with pytest.raises(NoSuchElementException, match="new exception"):
        driver.find_elements_by_id("_", min=1)

    # The recover should have been restored
    assert driver.recover == except_recover


@pytest.fixture
def driver_plus_decorator_mocks(mocker):
    driver = MockDriver(mocker)
    mocker.patch("selenious.decorators.monotonic", driver.mock_monotonic)
    mocker.patch("selenious.decorators.sleep", driver.mock_sleep)
    mocker.patch(
        "selenious.decorators._find_element_next_state", driver.mock_next_state
    )
    mocker.patch(
        "selenious.decorators._find_elements_next_state", driver.mock_next_state
    )
    return driver


def test_find_element_decorator_raise(snapshot, driver_plus_decorator_mocks):
    """Tests the state machine to test that the driver handles a raise"""
    driver = driver_plus_decorator_mocks
    driver.side_effect = [0, NoSuchElementException, 99, ("raise", MockWebElement())]
    with pytest.raises(NoSuchElementException):
        driver.find_element_by_id("_")

    snapshot.assert_match(driver.calls)


def test_find_element_decorator_recover_or_raise_null(
    snapshot, driver_plus_decorator_mocks
):
    """Tests the state machine to test that the driver handles a recover_or_raise with
    null recover"""
    driver = driver_plus_decorator_mocks
    driver.timeout = 200
    driver.side_effect = [
        0,
        NoSuchElementException,
        99,
        ("recover_or_raise", MockWebElement()),
    ]
    with pytest.raises(NoSuchElementException):
        driver.find_element_by_id("_")

    snapshot.assert_match(driver.calls)


def test_find_element_decorator_recover_or_raise_nonnull(
    snapshot, driver_plus_decorator_mocks
):
    """Tests the state machine to test that the driver handles a recover_or_raise with
    nonnull recover"""
    driver = driver_plus_decorator_mocks
    driver.timeout = 200
    driver.recover = MagicMock()
    driver.side_effect = [
        0,
        NoSuchElementException,
        99,
        ("recover_or_raise", MockWebElement()),
        None,
        MockWebElement(),
    ]
    driver.find_element_by_id("_")
    driver.recover.assert_called()

    snapshot.assert_match(driver.calls)


def test_find_elements_decorator_debounce(snapshot, driver_plus_decorator_mocks):
    """Tests the state machine to test that the driver handles a debounce,"""
    driver = driver_plus_decorator_mocks
    driver.debounce = 0.1
    driver.recover = MagicMock()
    driver.side_effect = [
        0,
        [],
        1,
        ("debounce", MockWebElement()),
        None,
        [MockWebElement(), MockWebElement(), MockWebElement()],
        99,
        ("success", MockWebElement()),
    ]
    driver.find_elements_by_id("_", min=3, timeout=200)
    driver.recover.assert_not_called()

    snapshot.assert_match(driver.calls)


def test_find_elements_decorator_recover_or_raise_recover(
    snapshot, driver_plus_decorator_mocks
):
    """Tests the state machine to test that the driver handles a recover_or_raise with
    nonnull recover"""
    driver = driver_plus_decorator_mocks
    driver.debounce = 0.1
    driver.recover = MagicMock()
    driver.side_effect = [
        0,
        [],
        1,
        ("recover_or_raise", MockWebElement()),
        None,
        [MockWebElement(), MockWebElement(), MockWebElement()],
        99,
        ("success", MockWebElement()),
    ]
    driver.find_elements_by_id("_", min=3, timeout=200)
    driver.recover.assert_called()

    snapshot.assert_match(driver.calls)


def test_find_elements_decorator_recover_or_raise_no_recover(
    snapshot, driver_plus_decorator_mocks
):
    """Tests the state machine to test that the driver handles a recover_or_raise
    with null recover"""
    driver = driver_plus_decorator_mocks
    driver.debounce = 0.1
    driver.side_effect = [0, [], 1, ("recover_or_raise", MockWebElement())]
    with pytest.raises(NoSuchElementException):
        driver.find_elements_by_id("_", min=3, timeout=200)

    snapshot.assert_match(driver.calls)


def test_find_elements_decorator_raise(snapshot, driver_plus_decorator_mocks):
    """Tests the state machine to test that the driver handles a raise"""
    driver = driver_plus_decorator_mocks
    driver.debounce = 0.1
    driver.side_effect = [0, [], 1, ("raise", MockWebElement())]
    with pytest.raises(NoSuchElementException):
        driver.find_elements_by_id("_", min=3, timeout=200)

    snapshot.assert_match(driver.calls)


def test_find_elements_decorator_recover_and_retry_recover(
    snapshot, driver_plus_decorator_mocks
):
    """Tests the state machine to test that the driver handles a recover_and_retry
    with recover"""
    driver = driver_plus_decorator_mocks
    driver.recover = MagicMock()
    driver.debounce = 0.1
    driver.side_effect = [
        0,
        [],
        1,
        ("recover_and_retry", MockWebElement()),
        None,
        [MockWebElement(), MockWebElement(), MockWebElement()],
        99,
        ("success", MockWebElement()),
    ]
    driver.find_elements_by_id("_", min=3, timeout=200)
    driver.recover.assert_called()

    snapshot.assert_match(driver.calls)


def test_find_elements_decorator_recover_and_retry_no_recover(
    snapshot, driver_plus_decorator_mocks
):
    """Tests the state machine to test that the driver handles a recover_and_retry
    with recover"""
    driver = driver_plus_decorator_mocks
    driver.debounce = 0.1
    driver.side_effect = [
        0,
        [],
        1,
        ("recover_and_retry", MockWebElement()),
        None,
        [MockWebElement(), MockWebElement(), MockWebElement()],
        99,
        ("success", MockWebElement()),
    ]
    driver.find_elements_by_id("_", min=3, timeout=200)

    snapshot.assert_match(driver.calls)

    # return ("recover_and_retry", min(time_left, poll_frequency))


def test_find_element_next_state():
    f = decorators._find_element_next_state
    # f(prev_state, time_left, poll_frequency) == (next_state, sleep_time)
    assert f(None, 10, 0.5) == ("recover_and_retry", 0.5)
    assert f(None, 0, 0.5) == ("recover_or_raise", 0.0)
    assert f("recover_and_retry", 10, 1.0) == ("recover_and_retry", 1.0)
    assert f("recover_and_retry", 0.5, 1.0) == ("recover_and_retry", 0.5)
    assert f("recover_and_retry", 0, 1.0) == ("raise", None)
    assert f("recover_or_raise", 0, 1.0) == ("raise", None)


def test_find_elements_next_state():
    f = decorators._find_elements_next_state
    e = Exception("this should not have been accessed")
    # f(prev_state, time_left, poll_frequency, debounce, stable_time, ismin) ==
    # (next_state, sleep_time)
    assert f(e, e, e, 1, 1, True) == ("success", None)
    assert f(e, e, e, 1, 0.75, True) == ("debounce", 0.25)
    assert f("debounce", 0, e, e, e, False) == ("raise", None)
    assert f("recover_or_raise", 0, e, e, e, False) == ("raise", None)
    assert f("recover_and_retry", 0, e, e, e, False) == ("raise", None)
    assert f(None, 0, e, e, e, False) == ("recover_or_raise", 0)
    assert f(e, 1, 0.5, e, e, False) == ("recover_and_retry", 0.5)
    assert f(e, 1, 1.5, e, e, False) == ("recover_and_retry", 1.0)
