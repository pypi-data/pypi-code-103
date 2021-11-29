import inspect
import os
import threading
import allure
from qrunner import Browser
from qrunner.utils.exceptions import ElementTypeError
from qrunner.utils.log import logger
from qrunner.core.ios.driver import relaunch_wda
from selenium.common.exceptions import NoSuchElementException
from qrunner.utils.data import get_time


class Page(object):
    def __init__(self):
        self.driver = Browser.driver

    def screenshot(self, filename):
        self.driver.screenshot(filename)

    def upload_pic(self, filename):
        self.screenshot('tmp.png')
        allure.attach.file('tmp.png',
                           attachment_type=allure.attachment_type.PNG,
                           name=f'{filename}-{get_time()}')
        os.remove('tmp.png')

    @property
    def window_size(self):
        return self.driver.window_size()

    @property
    def page_content(self):
        return self.driver.source()

    def click(self, x, y):
        self.driver.click(x, y)

    def double_click(self, x, y):
        self.driver.double_tap(x, y)

    def swipe(self, x1, y1, x2, y2):
        self.swipe(x1, y1, x2, y2)

    def swipe_left(self):
        self.driver.swipe_left()

    def swipe_right(self):
        self.driver.swipe_right()

    def swipe_up(self):
        self.driver.swipe_up()

    def swipe_down(self):
        self.driver.swipe_down()


LOC_LIST = ['name', 'nameContains', 'label', 'labelContains', 'value', 'valueContains', 'className', 'xpath']
DEFAULT_ALERTS = [
    '同意',
    '使用App时允许',
    '允许',
    '始终允许'
]


def click(loc):
    timeout = 2
    try:
        if '//' in loc:
            Browser.driver.xpath(loc).click(timeout=timeout)
        else:
            Browser.driver(name=loc).click(timeout=timeout)
    except Exception:
        pass


def handle_alert():
    alert_list = []
    alert_list.extend(DEFAULT_ALERTS)
    alert_list.extend(Browser.alert_config)
    thread_list = []
    for alert in alert_list:
        t = threading.Thread(target=click, args=(alert,))
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()


class Element(object):
    def __init__(self, *args, **kwargs):
        self._index = kwargs.pop('index', 0)

        for k, v in kwargs.items():
            if k not in LOC_LIST:
                raise ElementTypeError(f'不支持的定位方式: {k}')

        if not kwargs:
            raise ElementTypeError(f'请指定定位方式: {args}')

        self.xpath = kwargs.get('xpath', '')
        self._kwargs = kwargs
        self._element = None

    @relaunch_wda
    def find_element(self, retry=3, timeout=3):
        self._element = Browser.driver.xpath(self.xpath) if \
            self.xpath else Browser.driver(**self._kwargs)[self._index]
        while not self._element.wait(timeout=timeout):
            if retry > 0:
                retry -= 1
                logger.warning(f'重试 查找元素： {self._kwargs}')
                handle_alert()
            else:
                frame = inspect.currentframe().f_back
                caller = inspect.getframeinfo(frame)
                logger.warning(f'【{caller.function}:{caller.lineno}】未找到元素 {self._kwargs}')
                return None
        return self._element

    @relaunch_wda
    def _get_element(self, retry=5, timeout=3):
        element = self.find_element(retry=retry, timeout=timeout)
        if element is None:
            Page().upload_pic(list(self._kwargs.values())[0])
            raise NoSuchElementException(f'未定位到元素: {self._kwargs}')
        return element

    @relaunch_wda
    def attr(self, name):
        logger.info(f'元素 {self._kwargs},{self._index}-{name} 属性:')
        element = self._get_element(retry=0)

        info_dict = {
            'info': element.info,
            'count': element.count(),
            'name': element.name,
            'label': element.label,
            'value': element.value,
            'className': element.className,
            'visible': element.visible,
            'bounds': element.bounds,
            'text': element.text
        }
        _info = info_dict.get(name)
        logger.info(_info)
        return _info

    # 用于常见分支场景判断
    @relaunch_wda
    def exists(self, timeout=1):
        logger.info(f'元素 {self._kwargs},{self._index} 是否存在:')
        _exist = self.find_element(retry=0, timeout=timeout) is not None
        logger.info(_exist)
        return _exist

    @relaunch_wda
    def click(self):
        logger.info(f'点击元素: {self._kwargs},{self._index}')
        element = self._get_element()
        handle_alert()
        element.click()

    @relaunch_wda
    def click_exists(self, timeout=1):
        if self.exists(timeout=timeout):
            self.click()

    @relaunch_wda
    def input(self, text, clear=True):
        logger.info(f'输入框 {self._kwargs},{self._index} 输入: {text}')
        element = self._get_element()
        if clear:
            element.clear_text()
        element.set_text(text)
        logger.info('输入成功')

    @relaunch_wda
    def scroll(self):
        self._get_element().scroll()

    @relaunch_wda
    def swipe_left(self):
        self._get_element().swipe("left")

    @relaunch_wda
    def swipe_right(self):
        self._get_element().swipe("right")

    @relaunch_wda
    def swipe_up(self):
        self._get_element().swipe("up")

    @relaunch_wda
    def swipe_down(self):
        self._get_element().swipe("down")

    @relaunch_wda
    def child(self, *args, **kwargs):
        return self._get_element().child(*args, **kwargs)




