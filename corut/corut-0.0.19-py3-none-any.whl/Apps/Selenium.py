#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It is aimed to make automatic transactions on the web browser.
Selenium library is preferred.
Common functions for basic functions have been added for Selenium.
All codes are designed to work in chrome browser
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from ..Decorators import try_except
from ..Shell import print_error


class Selenium:
    def __init__(self):
        self.__session = None
        self.driver_config = {'Driver': None, 'DriverPath': None}

    @staticmethod
    def __install_driver(driver_type):
        try:
            path = ChromeDriverManager(chrome_type=driver_type).install()
            print(f'"{driver_type.title()}" Driver install Success ===> Path:{path}')
            return path
        except Exception as error:
            print(f'### "{driver_type.title()}" Driver install Error ===> {error} ###')
            return None

    def check_driver(self, url="https://www.google.com.tr/"):
        assert list(self.driver_config.values()) != [None, None], (
            'To use Selenium Webdriver, '
            'please install the stable version of Google Chrome or Chromium'
        )
        print(' Selenium driver available '.center(99, '*'))
        assert self.browser_open(url, run_as_background=True), (
            'Please connect to Free internet and update Selenium driver.'
        )
        print(' Selenium driver works fine. '.center(99, '*'))
        self.browser_close()

    def install_driver(self):
        for driver_type in [ChromeType.GOOGLE, ChromeType.CHROMIUM]:
            path = self.__install_driver(driver_type=driver_type)
            if path:
                self.driver_config.update({'Driver': driver_type.title(), 'DriverPath': path})
                break
        print(f'Selenium Driver Config ===> {self.driver_config}')

    @try_except
    def browser_open(
            self, http_address, download_directory=None, run_as_background=False, arguments=None
    ):
        if arguments is None:
            arguments = ['--ignore-certificate-errors']
        options = Options()
        for argument in arguments:
            options.add_argument(argument)
        if run_as_background:
            options.add_argument('--headless')
        if download_directory:
            options.add_experimental_option(
                "prefs", {"download.default_directory": download_directory}
            )
        self.__session = WebDriver(self.driver_config.get('DriverPath'), chrome_options=options)
        self.__session.get(http_address)
        print('Selenium Chrome Browser launch successful.')
        return self.__session

    @try_except
    def browser_close(self):
        if self.__session:
            self.__session.close()
            print('Selenium Chrome Browser Close.')
            self.__session.quit()
            print('Selenium Chrome Browser Quit.')

    def send_parameter_with_by_name(self, name, value=None, after_send_key=None, hide_value=False):
        """
        General function for selenium
        :param name: Value 1
        :param value: Value 2
        :param after_send_key:
            'NULL', 'CANCEL', 'HELP', 'BACKSPACE', 'BACK_SPACE', 'TAB', 'CLEAR', 'RETURN', 'ENTER',
            'SHIFT', 'LEFT_SHIFT', 'CONTROL', 'LEFT_CONTROL', 'ALT', 'LEFT_ALT', 'PAUSE', 'ESCAPE',
            'SPACE', 'PAGE_UP', 'PAGE_DOWN', 'END', 'HOME', 'LEFT', 'ARROW_LEFT', 'UP', 'ARROW_UP',
            'RIGHT', 'ARROW_RIGHT', 'DOWN', 'ARROW_DOWN', 'INSERT', 'DELETE', 'SEMICOLON',
            'EQUALS', 'NUMPAD0', 'NUMPAD1', 'NUMPAD2', 'NUMPAD3', 'NUMPAD4', 'NUMPAD5', 'NUMPAD6',
            'NUMPAD7', 'NUMPAD8', 'NUMPAD9', 'MULTIPLY', 'ADD', 'SEPARATOR', 'SUBTRACT', 'DECIMAL',
            'DIVIDE', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            'META', 'COMMAND'
        :param hide_value: It is used to not print values such as passwords.
        """
        print(
            f'Selenium find element by name ===> '
            f'Name:#{name}# --- Value:{"xxxxx" if hide_value else value}'
        )
        try:
            page = self.__session.find_element_by_name(name)
            if value:
                page.send_keys(value)
            if after_send_key:
                after_send_key = Keys().__getattribute__(after_send_key)
                print(f'Selenium find element by name ===> Send Later:#{after_send_key}#')
                page.send_keys(after_send_key)
            print('Selenium find element by name ===> All transactions are successful.')
            return page
        except Exception as error:
            print_error(error, locals())
            return self.__session

    def send_parameter_with_by_id(self, name, value=None, args=None):
        print(f'Selenium find element by id ===> Name:#{name}# --- Value:{value}')
        try:
            page = self.__session.find_element_by_id(name)
            if value:
                page.send_keys(value)
            if args:
                getattr(page, args)()
            print('Selenium find element by id ===> All transactions are successful.')
            return page
        except Exception as error:
            print_error(error, locals())
            return self.__session

    def send_parameter_with_by_xpath(self, value, args=None):
        print(f'Selenium find element by xpath ===> Value:{value}')
        try:
            page = self.__session.find_element_by_xpath(value)
            if args:
                getattr(page, args)()
            print('Selenium find element by xpath ===> All transactions are successful.')
            return page
        except Exception as error:
            print_error(self.send_parameter_with_by_xpath.__name__, error)
            return self.__session
