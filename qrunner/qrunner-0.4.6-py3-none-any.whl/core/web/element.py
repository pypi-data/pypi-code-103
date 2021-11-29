import inspect
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from qrunner.utils.log import logger
from qrunner.core.web.driver import relaunch
from qrunner import Browser
from qrunner.utils.exceptions import ElementTypeError, NoSuchElementException, TimeoutException


class Page(object):
    def __init__(self, url, cookie: dict = None):
        """
        cookie: {
          "name": "xx",
          "value": "xx"
        }
        """
        self.driver = Browser.driver
        self.driver.get(url)
        if cookie:
            self.driver.add_cookie(cookie)
            self.driver.get(url)


LOC_LIST = {
    'id': By.ID,
    'name': By.NAME,
    'link_text': By.LINK_TEXT,
    'tag': By.TAG_NAME,
    'plink_text': By.PARTIAL_LINK_TEXT,
    'class_name': By.CLASS_NAME,
    'xpath': By.XPATH,
    'css': By.CSS_SELECTOR
}


class Element:
    def __init__(self, *args, **kwargs):
        self._index = kwargs.pop('index', 0)

        if not kwargs:
            raise ElementTypeError('请输入定位方式')

        if len(kwargs) > 1:
            raise ElementTypeError('请仅指定一种定位方式')

        self.k, self.v = next(iter(kwargs.items()))
        print(self.k, self.v)
        if self.k not in LOC_LIST.keys():
            raise ElementTypeError(f'不支持的定位方式: {self.k}，仅支持: {LOC_LIST.keys()}')

        self._kwargs = kwargs
        self._element = None

    @relaunch
    def wait(self, timeout=30):
        try:
            WebDriverWait(Browser.driver, timeout=timeout)\
                .until(EC.visibility_of_element_located((LOC_LIST[self.k], self.v)))
            return True
        except TimeoutException:
            return False

    @relaunch
    def _find_elements(self, retry=3, timeout=3):
        self._element = Browser.driver.find_elements(LOC_LIST[self.k], self.v)
        while not self.wait(timeout=timeout):
            if retry > 0:
                retry -= 1
                logger.info(f'重试 查找元素 {self._kwargs}')
                time.sleep(2)
            else:
                frame = inspect.currentframe().f_back
                caller = inspect.getframeinfo(frame)
                logger.warning(f'【{caller.function}:{caller.lineno}】Not found element {self._kwargs}')
                return None
        return self._element

    @relaunch
    def get_element(self):
        element = self._find_elements()[self._index]
        if element is None:
            raise NoSuchElementException(f'未找到元素： {self._kwargs}')
        return element

    @relaunch
    def get_elements(self):
        element = self._find_elements()
        if element is None:
            raise NoSuchElementException(f'未找到元素： {self._kwargs}')
        return element

    @relaunch
    def click(self):
        logger.info(f'点击元素: {self._kwargs}')
        self.get_element().click()

    @relaunch
    def input(self, text):
        logger.info(f'点击元素: {self._kwargs}，然后输入: {text}')
        self.get_element().send_keys(text)

    @relaunch
    def get_text(self):
        logger.info(f'获取元素 {self._kwargs} 文本')
        elements = self.get_elements()
        if len(elements) > 1:
            text = [el.text for el in elements]
        else:
            text = elements[0].text
        # logger.info(text)
        return text




