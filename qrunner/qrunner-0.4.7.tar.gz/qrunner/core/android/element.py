import inspect
import os
import threading
import allure
from qrunner import Browser
from qrunner.utils.log import logger
from qrunner.utils.data import get_time
from qrunner.utils.exceptions import ElementTypeError, NoSuchElementException


# 安卓页面基类
class Page(object):
    def __init__(self):
        self.driver = Browser.driver

    def click(self, x, y):
        self.driver.click(x, y)

    def double_click(self, x, y):
        self.driver.double_click(x, y)

    def long_click(self, x, y):
        self.driver.long_click(x, y)

    def swipe(self, sx, sy, ex, ey):
        self.driver.swipe(sx, sy, ex, ey)

    def swipe_left(self, scale=0.9):
        self.driver.swipe_ext('left', scale=scale)

    def swipe_right(self, scale=0.9):
        self.driver.swipe_ext('right', scale=scale)

    def swipe_up(self, scale=0.8):
        self.driver.swipe_ext('up', scale=scale)

    def swipe_down(self, scale=0.8):
        self.driver.swipe_ext('down', scale=scale)

    def drag(self, sx, sy, ex, ey):
        self.driver.drag(sx, sy, ex, ey)

    def screenshot(self, name):
        self.driver.screenshot(name)

    def upload_pic(self, filename):
        self.screenshot('tmp.png')
        allure.attach.file(
            'tmp.png',
            attachment_type=allure.attachment_type.PNG,
            name=f'{filename}-{get_time()}'
        )
        os.remove('tmp.png')

    def input_text(self, text):
        self.driver.clear_text()
        self.driver.send_keys(text)
        self.driver.send_action('search')
        self.driver.set_fastinput_ime(False)

    def input_password(self, text):
        self.driver(focused=True).set_text(text)

    @property
    def page_content(self):
        return self.driver.dump_hierarchy()

    @property
    def window_size(self):
        return self.driver.window_size()

    def back(self):
        self.driver.press('back')

    def search(self):
        self.driver.press('search')

    def enter(self):
        self.driver.press('enter')


# # 安卓元素基类
# class BaseElement(object):
#     def __init__(self, serial_no=None):
#         self._driver = AndroidDriver.get_instance(serial_no)

LOC_LIST = ['text', 'textContains', 'className', 'resourceId', 'xpath']
DEFAULT_ALERTS = [
    '允许',
    '始终允许',
    '以后',
    '同意',
    '仅使用期间允许',
    '仅在使用中允许'
]


def click(loc):
    timeout = 2
    try:
        if 'id/' in loc:
            Browser.driver(resourceId=f'{Browser.pkg_name}:{loc}').click(timeout=timeout)
        elif '//' in loc:
            Browser.driver.xpath(loc).click(timeout=timeout)
        else:
            Browser.driver(text=loc).click(timeout=timeout)
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


# 安卓元素定义
class Element(object):
    def __init__(self, *args, **kwargs):
        self._index = kwargs.pop('index', 0)

        for _k, _v in kwargs.items():
            if _k not in LOC_LIST:
                raise ElementTypeError(f'不支持的定位方式: {_k}')

        if not kwargs:
            raise ElementTypeError(f'请指定定位方式: {args}')

        self._xpath = kwargs.get('xpath', '')

        _old_pkc_name = kwargs.pop('resourceId', '')
        if _old_pkc_name:
            kwargs['resourceId'] = f'{Browser.pkg_name}:{_old_pkc_name}'

        self._kwargs = kwargs
        self._element = None

    # def __get__(self, instance, owner):
    #     if instance is None:
    #         return None
    #     Browser.driver = instance.driver
    #     return self

    def _find_elements(self, retry=3, timeout=3):
        logger.info(f'查找元素: {self._kwargs},{self._index}')
        self._element = Browser.driver.xpath(self._xpath) if \
            self._xpath else Browser.driver(**self._kwargs)
        while not self._element.wait(timeout=timeout):
            if retry > 0:
                retry -= 1
                logger.warning(f'重试 查找元素： {self._kwargs},{self._index}')
                handle_alert()
            else:
                frame = inspect.currentframe().f_back
                caller = inspect.getframeinfo(frame)
                logger.warning(f'【{caller.function}:{caller.lineno}】未找到元素 {self._kwargs}')
                return None
        return self._element

    def _get_elements(self, retry=3, timeout=3):
        elements = self._find_elements(retry=retry, timeout=timeout)
        if elements is None:
            Page().upload_pic(list(self._kwargs.values())[0])
            raise NoSuchElementException(f'未定位到元素: {self._kwargs}')
        if self._xpath:
            return [elements]
        return elements

    def _get_element(self, retry=3, timeout=3):
        elements = self._get_elements(retry=retry, timeout=timeout)
        if self._xpath:
            return elements
        else:
            return elements[self._index]

    def attr(self, name):
        logger.info(f'元素 {self._kwargs},{self._index} - {name} 属性:')
        element = self._get_element(retry=0)
        _info_dict = {
            'info': element.info,
            'count': element.count,
            'resourceId': element.info.get('resourceName'),
            'text': element.info.get('text'),
            'packageName': element.info.get('packageName'),
            'className': element.info.get('className'),
            'description': element.info.get('contentDescription'),
            'bounds': element.info.get('bounds'),
            'visibleBounds': element.info.get('visibleBounds'),
            'childCount': element.info.get('childCount'),
            'checkable': element.info.get('checkable'),
            'checked': element.info.get('clickable'),
            'enabled': element.info.get('enabled'),
            'focusable': element.info.get('focusable'),
            'focused': element.info.get('focused'),
            'longClickable': element.info.get('longClickable'),
            'scrollable': element.info.get('scrollable'),
            'selected': element.info.get('selected')
        }
        # logger.info(element.info)
        _info = _info_dict.get(name, '未找到该属性')
        logger.info(_info)
        return _info

    def get_text(self):
        """
        跟attr的区别：是为了批量获取text信息（暂时是为了支持爬虫业务）
        """
        logger.info(f'获取元素 {self._kwargs},{self._index} 的text')
        text = [el.get_text() for el in self._get_elements()]
        logger.info(text)
        return text

    def child(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs},{self._index} 的子元素{kwargs}')
        return self._get_element().child(*args, **kwargs)

    def brother(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs},{self._index} 的兄弟元素{kwargs}')
        return self._get_element().sibling(*args, **kwargs)

    # 用于常见分支场景判断
    def exists(self, timeout=1):
        logger.info(f'判断元素是否存在: {self._kwargs},{self._index}')
        return self._find_elements(retry=0, timeout=timeout) is not None

    def click(self):
        logger.info(f'点击元素: {self._kwargs},{self._index}')
        element = self._get_element()
        handle_alert()
        element.click()

    def click_exists(self, timeout=1):
        logger.info(f'存在才点击元素: {self._kwargs},{self._index}')
        if self.exists(timeout=timeout):
            self.click()

    def input(self, text, clear=True):
        logger.info(f'定位元素并输入{text}: {self._kwargs},{self._index}')
        self._get_element().click()
        Browser.driver.send_keys(str(text), clear=clear)
        Browser.driver.send_action('search')
        Browser.driver.set_fastinput_ime(False)

    def drag_to(self, *args, **kwargs):
        logger.info(f'从当前元素{self._kwargs},{self._index}, 拖动到元素: {kwargs}')
        self._get_element().drag_to(*args, **kwargs)

    def swipe_left(self):
        logger.info(f'往左滑动元素: {self._kwargs},{self._index}')
        self._get_element().swipe("left")

    def swipe_right(self):
        logger.info(f'往右滑动元素: {self._kwargs},{self._index}')
        self._get_element().swipe("right")

    def swipe_up(self):
        logger.info(f'往上滑动元素: {self._kwargs},{self._index}')
        self._get_element().swipe("up")

    def swipe_down(self):
        logger.info(f'往下滑动元素: {self._kwargs},{self._index}')
        self._get_element().swipe("down")



