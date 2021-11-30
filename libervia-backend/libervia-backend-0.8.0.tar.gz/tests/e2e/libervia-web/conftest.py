#!/usr/bin/env python3

# Libervia: an XMPP client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import socket
import pytest
import time
from datetime import datetime
from pathlib import Path
import helium


WEB_HOST = "libervia-web.test"
WEB_PORT_HTTPS = 8443
BASE_URL = f"https://{WEB_HOST}:{WEB_PORT_HTTPS}"
SIZE_DESKTOP = (1024, 728)
SIZE_MOBILE = (380, 640)
accounts_cookies = {}


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # needed to get test results in request fixture
    # cf. https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def screenshot_on_failure(request):
    yield
    if request.node.rep_setup.passed:
        if request.node.rep_call.failed:
            report_dir = Path(os.getenv("LIBERVIA_TEST_REPORT_DIR", "/tmp/tests_report"))
            dest_dir = report_dir/"screenshots"
            dest_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{datetime.now().isoformat()}_{request.node.name}.png"
            dest_path = dest_dir/filename
            helium.get_driver().save_screenshot(str(dest_path))
            print(f"screenshot saved to {dest_path}")


def wait_for_socket(host, port, retries=30):
    sock = socket.socket()
    while True:
        try:
            sock.connect((host, port))
        except ConnectionRefusedError as e:
            retries -= 1
            if retries < 0:
                print(f"Can't access server at {host}:{port}", file=sys.stderr)
                raise e
            else:
                print(f"Can't connect to {host}:{port}, retrying ({retries})")
                time.sleep(1)
        else:
            break


@pytest.fixture(scope="session")
def browser():
    if os.getenv("LIBERVIA_TEST_E2E_WEB_NO_HEADLESS") is not None:
        kwargs = {}
    else:
        kwargs = {"headless": True}
    driver = helium.start_firefox(**kwargs)
    driver.set_window_size(*SIZE_DESKTOP)
    wait_for_socket(WEB_HOST, WEB_PORT_HTTPS)
    yield helium
    if os.getenv("LIBERVIA_TEST_E2E_WEB_KEEP_BROWSER") is None:
        helium.kill_browser()


@pytest.fixture
def nobody_logged_in(browser):
    browser.get_driver().delete_all_cookies()

def log_in(browser, account):
    try:
        account_cookies = accounts_cookies[account]
    except KeyError:
        browser.get_driver().delete_all_cookies()
        browser.go_to("https://libervia-web.test:8443/login")
        browser.write(account, into="login")
        browser.write("test", into="password")
        browser.click("log in")
        accounts_cookies[account] = browser.get_driver().get_cookies()[0]
    else:
        browser.get_driver().add_cookie(account_cookies)

@pytest.fixture
def log_in_account1(browser):
    log_in(browser, "account1")

@pytest.fixture
def log_in_account1_s2(browser):
    log_in(browser, "account1_s2")

@pytest.fixture
def mobile_screen(browser):
    browser.get_driver().set_window_size(*SIZE_MOBILE)


@pytest.fixture
def desktop_screen(browser):
    browser.get_driver().set_window_size(*SIZE_DESKTOP)
