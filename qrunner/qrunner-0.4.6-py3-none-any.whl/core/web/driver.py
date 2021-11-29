import requests
from selenium import webdriver
from qrunner import Browser, logger


# 重启chromedriver的装饰器
def relaunch(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except requests.exceptions.ConnectionError as _:
            logger.warning("web driver error, relaunch now.")
            self.d = WebDriver.get_instance(Browser.browser_name)
    return wrapper


class WebDriver(object):
    _instance = {}

    def __new__(cls, browser_name=None, headless=False):
        if not browser_name:
            browser_name = Browser.browser_name
        if browser_name not in cls._instance:
            cls._instance[browser_name] = super().__new__(cls)
        return cls._instance[browser_name]

    def __init__(self, browser_name=None, headless=False):
        if not browser_name:
            browser_name = Browser.browser_name

        logger.info(f'启动 web driver for {browser_name}')
        if browser_name == 'chrome':
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('--headless')
            self.d = webdriver.Chrome(options=options)
        elif browser_name == 'firefox':
            self.d = webdriver.Firefox()
        elif browser_name == 'ie':
            self.d = webdriver.Ie()
        elif browser_name == 'edge':
            self.d = webdriver.Edge()
        elif browser_name == 'safari':
            self.d = webdriver.Safari()

        self.d.set_page_load_timeout(30)
        self.d.maximize_window()

    @classmethod
    def get_instance(cls, browser_name=None, headless=False):
        if browser_name not in cls._instance:
            return WebDriver(browser_name, headless=headless).d
        return WebDriver._instance[browser_name].d

    # @relaunch
    # def back(self):
    #     logger.info('返回上一页')
    #     self.d.back()
    #
    # @relaunch
    # def send_keys(self, value):
    #     logger.info(f'输入文本: {value}')
    #     driver.send_keys(value)
    #
    # @relaunch
    # def screenshot(self, filename, timeout=3):
    #     driver.wait_shot(filename, timeout=timeout)
    #
    # @relaunch
    # def get_ui_tree(self):
    #     page_source = self.d.page_source()
    #     logger.info(f'获取页面内容: \n{page_source}')
    #     return page_source
    #
    # @relaunch
    # def get_windows(self):
    #     logger.info(f'获取当前打开的窗口列表')
    #     return self.d.window_handles
    #
    # @relaunch
    # def switch_window(self, old_windows):
    #     logger.info('切换到最新的window')
    #     current_windows = self.get_windows()
    #     newest_window = [window for window in current_windows if window not in old_windows][0]
    #     self.d.switch_to.window(newest_window)
    #
    # @relaunch
    # def execute_js(self, script, element):
    #     logger.info(f'执行js脚本: \n{script}')
    #     self.d.execute_script(script, element)






