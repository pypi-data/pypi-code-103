import inspect
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from qrunner.utils.log import logger
from qrunner.core.h5.driver import relaunch
from qrunner import Browser
from qrunner.utils.exceptions import ElementTypeError, NoSuchElementException, TimeoutException


class Page(object):
    def __init__(self):
        self.driver = Browser.driver


LOC_LIST = {
    'id': By.ID,
    'name': By.NAME,
    'link': By.LINK_TEXT,
    'plink': By.PARTIAL_LINK_TEXT,
    'tag': By.TAG_NAME,
    'class': By.CLASS_NAME,
    'xpath': By.XPATH,
    'css': By.CSS_SELECTOR
}


class Element:
    def __init__(self, *args, **kwargs):
        self.index = kwargs.pop('index', 0)

        if not kwargs:
            raise ElementTypeError('请输入定位方式')

        if len(kwargs) > 1:
            raise ElementTypeError('请仅指定一种定位方式')

        self.k, self.v = next(iter(kwargs.items()))
        if self.k not in LOC_LIST.keys():
            raise ElementTypeError(f'不支持的定位方式: {self.k}')

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
    def _find_element(self, retry=3, timeout=3):
        self._element = Browser.driver.find_elements(self.k, self.v)[self.index]
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
    def _get_element(self):
        element = self._find_element()
        if element is None:
            raise NoSuchElementException(f'未找到元素： {self._kwargs}')
        return element

    @relaunch
    def click(self):
        logger.info(f'点击元素: {self._kwargs}')
        self._get_element().click()

    @relaunch
    def input(self, text):
        logger.info(f'点击元素: {self._kwargs}，然后输入: {text}')
        self._get_element().send_keys(text)
