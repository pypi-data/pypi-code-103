"""
Pytest fixture to launch browser and properly exit.

Take manage screenshots in case pytest-bdd exit with
faillures using `pytest-bdd hooks
<https://github.com/pytest-dev/pytest-bdd#hooks>`_.

Use SCREENSHOT_DIR environment variable to define
path where to save screenshots.
"""
import os
import tempfile

import pytest
from dotenv import load_dotenv
from selenium.webdriver.remote.webdriver import WebDriver
from selenium_configurator.configurator import Configurator

load_dotenv()  # take environment variables from .env.


SELENIUM_CONFIG_FILE = os.environ.get("SELENIUM_CONFIG_FILE", "selenium.local.yaml")


def get_webdrivers():
    selenium_conf = Configurator.from_file(SELENIUM_CONFIG_FILE)
    drivers = selenium_conf.get_drivers()
    params = []
    for driver in drivers:
        params.append(pytest.param(driver, id=driver.name))
    return params


@pytest.fixture(params=get_webdrivers())
def selenium(request):
    return request.param


@pytest.fixture()
def webdriver(selenium):
    try:
        yield selenium.selenium
    finally:
        selenium.quit()


def pytest_bdd_step_error(
    request, feature, scenario, step, step_func, step_func_args, exception
):
    """Called when step function failed to execute."""
    take_screenshot_if_possible(request, step_func_args)


def pytest_bdd_step_validation_error(
    request, feature, scenario, step, step_func, step_func_args, exception
):
    """Called when step failed to validate."""
    take_screenshot_if_possible(request, step_func_args)


def take_screenshot_if_possible(request, func_args):
    webdriver = get_webdriver(func_args)
    if webdriver:
        screenshot_path = construct_screenshot_path(request)
        try:
            webdriver.save_screenshot(screenshot_path + ".png")
            print("Screenshot saved ", screenshot_path + ".png")
            with open(screenshot_path + ".html", "w") as html:
                html.write(webdriver.page_source)
                print("Html saved ", screenshot_path + ".html")
        except Exception as ex:
            print("Unable to take a screenshot, following exception occur: ", ex)


def construct_screenshot_path(request):
    directory = os.getenv("SCREENSHOT_DIR", tempfile.gettempdir())
    try:
        return os.path.join(directory, request._pyfuncitem.name)
    except Exception:
        return os.path.join(directory, str(request))


def get_webdriver(func_args):
    """parse func_args if a selenium webdriver is present return it otherwise
    return None
    """
    for _, arg in func_args.items():
        # in case using BasePage class webdriver is in driver attribute
        if hasattr(arg, "driver"):
            arg = arg.driver
        if isinstance(arg, WebDriver):
            return arg
