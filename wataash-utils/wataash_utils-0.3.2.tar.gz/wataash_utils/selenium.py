# SPDX-License-Identifier: Apache-2.0

import re
import typing as t

from selenium.webdriver.remote.webdriver import WebDriver


def _pairs_wh_url(driver: WebDriver):
    pairs_wh_urls = []

    # TODO: want to get the active tab...
    # wh_current = driver.current_window_handle  # not the active tab!

    for wh in driver.window_handles:
        driver.switch_to.window(wh)
        pairs_wh_urls.append((wh, driver.current_url))

    # driver.switch_to.window(wh_current)

    return pairs_wh_urls


def _switch_to_url(driver: WebDriver, url: re.Pattern, pairs_wh_urls: t.List[t.Tuple[str, str]] = None) -> bool:
    if pairs_wh_urls is None:
        pairs_wh_urls = _pairs_wh_url(driver)
    for wh, url_ in pairs_wh_urls:
        m = url.search(url_)
        if m is not None:
            driver.switch_to.window(wh)
            return True
    return False


def switch_to_urls(driver: WebDriver, urls: t.List[re.Pattern]) -> bool:
    pairs_wh_urls = _pairs_wh_url(driver)
    for url in urls:
        if _switch_to_url(driver, url, pairs_wh_urls):
            return True
    return False

# TODO: create new tab
# https://stackoverflow.com/questions/17547473/how-to-open-a-new-tab-using-selenium-webdriver
