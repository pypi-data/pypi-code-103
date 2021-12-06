import os
import re
import time
from enum import Enum

from PIL import Image
from pytesseract import pytesseract
from selenium.webdriver import ActionChains, Chrome, ChromeOptions, Firefox, FirefoxProfile, Ie, Safari
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

_CHARACTER_COMMA = ","
_CHARACTER_COLON = ":"
_WAIT_SECONDS = 3
_DEFAULT_ENCODING_UTF8 = "utf-8"


def _parse_type(driver_type):
    """
    parse driver type
    :param driver_type: str: driver type
        chrome: c or chrome
        firefox: f or firefox
        ie: i or ie
        safari: s or safari
        headless chrome: h or hc or headless, headless chrome
    :return: default value: BoxDriver.DriverType.CHROME
    """
    if driver_type == 'c' or driver_type == "chrome":
        return Browser.DriverType.CHROME
    elif driver_type == 'f' or driver_type == "firefox":
        return Browser.DriverType.FIREFOX
    elif driver_type == 'i' or driver_type == "ie":
        return Browser.DriverType.IE
    elif driver_type == 's' or driver_type == "safari":
        return Browser.DriverType.SAFARI
    elif driver_type == 'e' or driver_type == "edge":
        return Browser.DriverType.EDGE
    elif driver_type == 'h' or driver_type == "headless" \
            or driver_type == "hc" or driver_type == "headless_chrome":
        return Browser.DriverType.CHROME_HEADLESS

    return Browser.DriverType.CHROME


def build_driver(url, driver_type: str, wait_seconds=None):
    """
    get driver for web browser testing
    :param wait_seconds:
    :param url: str，访问浏览器的 url
    :param driver_type: str，指定浏览器的类型，忽略大小写
        : c, chrome
        : i, ie
        : f, firefox
        : o, opera
        : s, safari
        # : e, edge
        : h, headless, headless_chrome, hc
    :return: BoxDriver
    """
    if not isinstance(driver_type, str):
        driver_type = 'c'

    driver_type = _parse_type(driver_type.lower())
    if wait_seconds:
        driver = Browser(driver_type, wait_seconds=wait_seconds)
    else:
        driver = Browser(driver_type)
    driver.clear_cookies()

    driver.navigate(url)
    driver.maximize_window()
    return driver


class Browser(object):
    """
    a simple usage of selenium framework tool
    """

    """
    私有全局变量
    """
    _web_driver = None
    _by_char = None
    _wait_seconds = None

    """
    构造方法
    """

    class DriverType(Enum):
        CHROME = 1,
        FIREFOX = 2,
        IE = 3,
        SAFARI = 4,
        CHROME_HEADLESS = 5,
        EDGE = 6

    def __init__(self,
                 driver_type: DriverType,
                 by_char=_CHARACTER_COMMA,
                 wait_seconds=_WAIT_SECONDS,
                 firefox_profile=None
                 ):
        """
        构造方法：实例化 BoxDriver 时候使用
        :type wait_seconds: object
        :param driver_type: DriverType: selenium driver
        :param by_char: 分隔符，默认使用","
        :param firefox_profile: 火狐浏览器配置
        """
        self._by_char = by_char
        self._wait_seconds = wait_seconds

        if driver_type is None or driver_type == "":
            driver_type = self.DriverType.CHROME

        self._set_selenium_driver(driver_type, firefox_profile)

    def _set_selenium_driver(self, driver_type, firefox_profile):

        if driver_type == self.DriverType.CHROME:
            self._web_driver = Chrome()

        elif driver_type == self.DriverType.FIREFOX:

            if firefox_profile and os.path.exists(firefox_profile):
                profile = FirefoxProfile(firefox_profile)
                self._web_driver = Firefox(firefox_profile=profile)
            else:
                self._web_driver = Firefox()

        elif driver_type == self.DriverType.IE:
            self._web_driver = Ie()

        elif driver_type == self.DriverType.SAFARI:
            self._web_driver = Safari()

        elif driver_type == self.DriverType.EDGE:
            # TODO: waiting for selenium updated or other solution
            self._web_driver = Chrome()

        elif driver_type == self.DriverType.CHROME_HEADLESS:
            profile = ChromeOptions()
            profile.add_argument('headless')
            profile.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
            self._web_driver = Chrome(options=profile)

        else:
            self._web_driver = Chrome()
            print("Invalid Driver Type filled: %r" % driver_type)

    """
    私有方法
    """

    def _convert_selector_to_locator(self, selector):
        """
        转换自定义的 selector 为 Selenium 支持的 locator
        :param selector: 定位字符，字符串类型，"i, xxx"
        :return: locator
        """
        if self._by_char not in selector:
            return By.ID, selector

        selector_by = selector.split(self._by_char)[0].strip()
        selector_value = selector.split(self._by_char)[1].strip()
        if selector_by == "i" or selector_by == 'id':
            locator = (By.ID, selector_value)
        elif selector_by == "n" or selector_by == 'name':
            locator = (By.NAME, selector_value)
        elif selector_by == "c" or selector_by == 'class_name':
            locator = (By.CLASS_NAME, selector_value)
        elif selector_by == "l" or selector_by == 'link_text':
            locator = (By.LINK_TEXT, selector_value)
        elif selector_by == "p" or selector_by == 'partial_link_text':
            locator = (By.PARTIAL_LINK_TEXT, selector_value)
        elif selector_by == "t" or selector_by == 'tag_name':
            locator = (By.TAG_NAME, selector_value)
        elif selector_by == "x" or selector_by == 'xpath':
            locator = (By.XPATH, selector_value)
        elif selector_by == "s" or selector_by == 'css_selector':
            locator = (By.CSS_SELECTOR, selector_value)
        else:
            raise NameError("Please enter a valid selector of targeting elements.")

        return locator

    def _locate_element(self, selector):
        """
        to locate element by selector
        :arg
        selector should be passed by an example with "i,xxx"
        "x,//*[@id='langs']/button"
        :returns
        DOM element
        """
        locator = self._convert_selector_to_locator(selector)
        if locator is not None:
            element = self._web_driver.find_element(*locator)
        else:
            raise NameError("Please enter a valid locator of targeting elements.")

        return element

    def _locate_elements(self, selector):
        """
        to locate element by selector
        :arg
        selector should be passed by an example with "i,xxx"
        "x,//*[@id='langs']/button"
        :returns
        DOM element
        """
        locator = self._convert_selector_to_locator(selector)
        if locator is not None:
            elements = self._web_driver.find_elements(*locator)
        else:
            raise NameError("Please enter a valid locator of targeting elements.")

        return elements

    def _locate_sub_element(self, current_element: WebElement, selector):
        """
        to locate sub element by current element with selector
        :arg
        selector should be passed by an example with "i,xxx"
        "x,//*[@id='langs']/button"
        :returns
        DOM element
        """
        locator = self._convert_selector_to_locator(selector)
        if locator is not None and current_element is not None:
            element = current_element.find_element(*locator)
        else:
            raise NameError("Please enter a valid locator of targeting elements.")

        return element

    @staticmethod
    def _grey_process_img(img_obj):
        """
        使用灰度的方法处理图片
        :param img_obj:
        :return:
        """
        img = img_obj.convert("L")  # 转灰度
        pix_data = img.load()
        w, h = img.size
        threshold = 100
        # 遍历所有像素，大于阈值的为黑色
        for y in range(h):
            for x in range(w):
                if pix_data[x, y] < threshold:
                    pix_data[x, y] = 0
                else:
                    pix_data[x, y] = 255

        img_grey_again = img.convert("L")
        threshold = 140
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        out = img_grey_again.point(table, '1')
        return out

    @staticmethod
    def _reduce_noise(img_obj_processed):
        """
        对图片进行降噪
        :param img_obj_processed:
        :return:
        """
        if img_obj_processed is None:
            return None
        data = img_obj_processed.getdata()
        w, h = img_obj_processed.size

        black_point = 0
        for x in range(1, w - 1):
            for y in range(1, h - 1):
                mid_pixel = data[w * y + x]  # 中央像素点像素值
                if mid_pixel < 50:  # 找出上下左右四个方向像素点像素值
                    top_pixel = data[w * (y - 1) + x]
                    left_pixel = data[w * y + (x - 1)]
                    down_pixel = data[w * (y + 1) + x]
                    right_pixel = data[w * y + (x + 1)]
                    # 判断上下左右的黑色像素点总个数
                    if top_pixel < 10:
                        black_point += 1
                    if left_pixel < 10:
                        black_point += 1
                    if down_pixel < 10:
                        black_point += 1
                    if right_pixel < 10:
                        black_point += 1
                    if black_point < 1:
                        img_obj_processed.putpixel((x, y), 255)
                    black_point = 0

        return img_obj_processed

    """
    cookie 相关方法
    """

    def clear_cookies(self):
        """
        clear all cookies after driver init
        """
        self._web_driver.delete_all_cookies()

    def add_cookies(self, cookies):
        """
        Add cookie by dict
        :param cookies:
        :return:
        """
        self._web_driver.add_cookie(cookie_dict=cookies)

    def add_cookie(self, cookie_dict):
        """
        Add single cookie by dict
        添加 单个 cookie
        如果该 cookie 已经存在，就先删除后，再添加
        :param cookie_dict: 字典类型，有两个key：name 和 value
        :return:
        """
        cookie_name = cookie_dict["name"]
        cookie_value = self._web_driver.get_cookie(cookie_name)
        if cookie_value is not None:
            self._web_driver.delete_cookie(cookie_name)

        self._web_driver.add_cookie(cookie_dict)

    def remove_cookie(self, name):
        """
        移除指定 name 的cookie
        :param name:
        :return:
        """
        # 检查 cookie 是否存在，存在就移除
        old_cookie_value = self._web_driver.get_cookie(name)
        if old_cookie_value is not None:
            self._web_driver.delete_cookie(name)

    """
    浏览器本身相关方法
    """

    def refresh(self, url=None):
        """
        刷新页面
        如果 url 是空值，就刷新当前页面，否则就刷新指定页面
        :param url: 默认值是空的
        :return:
        """
        if url is None:
            self._web_driver.refresh()
        else:
            self._web_driver.get(url)

        self.forced_wait(self._wait_seconds)

    def maximize_window(self):
        """
        最大化当前浏览器的窗口
        :return:
        """
        self._web_driver.maximize_window()

    def navigate(self, url):
        """
        打开 URL
        :param url:
        :return:
        """
        self._web_driver.get(url)
        self.forced_wait(self._wait_seconds)

    def quit(self):
        """
        退出驱动
        :return:
        """
        self._web_driver.quit()

    def close_browser(self):
        """
        关闭浏览器
        :return:
        """
        self._web_driver.close()

    """
    基本元素相关方法
    """

    def type(self, selector, text):
        """
        Operation input box.

        Usage:
        driver.type("i,el","selenium")
        """
        el = self._locate_element(selector)
        el.clear()
        el.send_keys(text)

    def click(self, selector):
        """
        It can click any text / image can be clicked
        Connection, check box, radio buttons, and even drop-down box etc..

        Usage:
        driver.click("i,el")
        """
        el = self._locate_element(selector)
        el.click()
        self.forced_wait(self._wait_seconds)

    def click_by_enter(self, selector):
        """
        It can type any text / image can be located  with ENTER key

        Usage:
        driver.click_by_enter("i,el")
        """
        el = self._locate_element(selector)
        el.send_keys(Keys.ENTER)

        self.forced_wait(self._wait_seconds)

    def click_by_text(self, text):
        """
        Click the element by the link text

        Usage:
        driver.click_text("新闻")
        """
        self._locate_element('p%s' % self._by_char + text).click()
        self.forced_wait(self._wait_seconds)

    def submit(self, selector):
        """
        Submit the specified form.

        Usage:
        driver.submit("i,el")
        """
        el = self._locate_element(selector)
        el.submit()

        self.forced_wait(self._wait_seconds)

    def move_to(self, selector):
        """
        to move mouse pointer to selector
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        ActionChains(self._web_driver).move_to_element(el).perform()
        self.forced_wait(self._wait_seconds)

    def right_click(self, selector):
        """
        to click the selector by the right button of mouse
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        ActionChains(self._web_driver).context_click(el).perform()
        self.forced_wait(self._wait_seconds)

    def count_elements(self, selector):
        """
        数一下元素的个数
        :param selector: 定位符
        :return:
        """
        els = self._locate_elements(selector)
        return len(els)

    def drag_element(self, source, target):
        """
        拖拽元素
        :param source:
        :param target:
        :return:
        """

        el_source = self._locate_element(source)
        el_target = self._locate_element(target)

        if self._web_driver.w3c:
            ActionChains(self._web_driver).drag_and_drop(el_source, el_target).perform()
        else:
            ActionChains(self._web_driver).click_and_hold(el_source).perform()
            ActionChains(self._web_driver).move_to_element(el_target).perform()
            ActionChains(self._web_driver).release(el_target).perform()

        self.forced_wait(self._wait_seconds)

    def lost_focus(self):
        """
        当前元素丢失焦点
        :return:
        """
        ActionChains(self._web_driver).key_down(Keys.TAB).key_up(Keys.TAB).perform()
        self.forced_wait(self._wait_seconds)

    """
    <select> 元素相关
    """

    def select_by_index(self, selector, index):
        """
        It can click any text / image can be clicked
        Connection, check box, radio buttons, and even drop-down box etc..

        Usage:
        driver.select_by_index("i,el")
        """
        el = self._locate_element(selector)
        Select(el).select_by_index(index)

        self.forced_wait(self._wait_seconds)

    def get_selected_text(self, selector):
        """
        获取 Select 元素的选择的内容
        :param selector: 选择字符 "i, xxx"
        :return: 字符串
        """
        el = self._locate_element(selector)
        selected_opt = Select(el).first_selected_option()
        return selected_opt.text

    def select_by_visible_text(self, selector, text):
        """
        It can click any text / image can be clicked
        Connection, check box, radio buttons, and even drop-down box etc..

        Usage:
        driver.select_by_index("i,el")
        """
        el = self._locate_element(selector)
        Select(el).select_by_visible_text(text)

        self.forced_wait(self._wait_seconds)

    def select_by_value(self, selector, value):
        """
        It can click any text / image can be clicked
        Connection, check box, radio buttons, and even drop-down box etc..

        Usage:
        driver.select_by_index("i,el")
        """
        el = self._locate_element(selector)
        Select(el).select_by_value(value)

        self.forced_wait(self._wait_seconds)

    """
    JavaScript 相关
    """

    def execute_js(self, script):
        """
        Execute JavaScript scripts.

        Usage:
        driver.js("window.scrollTo(200,1000);")
        """
        self._web_driver.execute_script(script)

        self.forced_wait(self._wait_seconds)

    """
    元素属性相关方法
    """

    def get_value(self, selector):
        """
        返回元素的 value
        :param selector: 定位字符串
        :return:
        """
        el = self._locate_element(selector)
        return el.get_attribute("value")

    def get_attribute(self, selector, attribute):
        """
        Gets the value of an element attribute.

        Usage:
        driver.get_attribute("i,el","type")
        """
        el = self._locate_element(selector)
        return el.get_attribute(attribute)

    def get_text(self, selector):
        """
        Get element text information.

        Usage:
        driver.get_text("i,el")
        """
        el = self._locate_element(selector)
        return el.text

    def get_displayed(self, selector):
        """
        Gets the element to display,The return result is true or false.

        Usage:
        driver.get_display("i,el")
        """
        el = self._locate_element(selector)
        return el.is_displayed()

    def get_selected(self, selector):
        """
        to return the selected status of an WebElement
        :param selector: selector to locate
        :return: True False
        """
        el = self._locate_element(selector)
        return el.is_selected()

    def get_text_list(self, selector, sub_selector=None, attribute=None):
        """
        根据selector 获取多个元素，取得元素的text 列表
        :param attribute:
        :param selector:
        :param sub_selector:
        :return: list
        """

        el_list = self._locate_elements(selector)

        results = []
        for el in el_list:
            if sub_selector is not None:
                new_el = self._locate_sub_element(
                    current_element=el,
                    selector=sub_selector
                )
                if attribute is not None:
                    results.append(new_el.get_attribute(attribute))
                else:
                    results.append(new_el.text)
            else:
                results.append(el.text)

        return results

    """
    窗口相关方法
    """

    def accept_alert(self):
        """
        Accept warning box.

        Usage:
        driver.accept_alert()
        """
        self._web_driver.switch_to.alert.accept()

        self.forced_wait(self._wait_seconds)

    def dismiss_alert(self):
        """
        Dismisses the alert available.

        Usage:
        driver.dismissAlert()
        """
        self._web_driver.switch_to.alert.dismiss()

        self.forced_wait(self._wait_seconds)

    def switch_to_frame(self, selector):
        """
        Switch to the specified frame.

        Usage:
        driver.switch_to_frame("i,el")
        """
        el = self._locate_element(selector)
        self._web_driver.switch_to.frame(el)

        self.forced_wait(self._wait_seconds)

    def switch_to_default(self):
        """
        Returns the current form machine form at the next higher level.
        Corresponding relationship with switch_to_frame () method.

        Usage:
        driver.switch_to_default()
        """
        self._web_driver.switch_to.default_content()

        self.forced_wait(self._wait_seconds)

    def switch_to_parent(self):
        """
        switch to parent frame
        :return:
        """
        self._web_driver.switch_to.parent_frame()

        self.forced_wait(self._wait_seconds)

    def switch_to_window_by_title(self, title):
        for handle in self._web_driver.window_handles:
            self._web_driver.switch_to.window(handle)
            if self._web_driver.title == title:
                break

            self._web_driver.switch_to.default_content()
            self.forced_wait(self._wait_seconds)

    def open_new_window(self, selector):
        """
        Open the new window and switch the handle to the newly opened window.

        Usage:
        driver.open_new_window()
        """
        original_windows = self._web_driver.current_window_handle
        el = self._locate_element(selector)
        el.click()
        all_handles = self._web_driver.window_handles
        for handle in all_handles:
            if handle != original_windows:
                self._web_driver.switch_to.window(handle)
                break

    def save_window_snapshot(self, file_name):
        """
        save screen snapshot
        :param file_name: the image file name and path
        :return:
        """
        driver = self._web_driver
        driver.save_screenshot(file_name)
        self.forced_wait(self._wait_seconds)

    def save_window_snapshot_by_png(self):
        return self._web_driver.get_screenshot_as_png()

    def save_element_snapshot_by_png(self, selector):
        """
        控件截图
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        self.forced_wait(self._wait_seconds)
        return el.screenshot_as_png

    def save_window_snapshot_by_io(self):
        """
        保存截图为文件流
        :return:
        """
        return self._web_driver.get_screenshot_as_base64()

    def save_element_snapshot_by_io(self, selector):
        """
        控件截图
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        return el.screenshot_as_base64

    """
    验证码
    """

    def recognize_verify_code_by_grey_process(self, selector, code_length=0):
        """
        识别普通验证码
        :param code_length:
        :param selector:
        :return:
        """
        el = self._locate_element(selector)
        temp_element_snapshot_filename = "temp_element_snapshot.png"
        if el is not None:
            el.screenshot(temp_element_snapshot_filename)

        with Image.open(fp=temp_element_snapshot_filename) as img_obj:
            img_obj_processed = self._grey_process_img(img_obj)
            img_obj_noise_reduced = self._reduce_noise(img_obj_processed)
            pytesseract.tesseract_cmd = r"tesseract.exe"

            # 图片转文字
            result = pytesseract.image_to_string(img_obj_noise_reduced)

        os.remove(temp_element_snapshot_filename)

        # 去除识别出来的特殊字符并返回
        result = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", result)
        if code_length > 0:
            return result[0: code_length]

        return result

    """
    等待方法
    """

    @staticmethod
    def forced_wait(seconds):
        """
        强制等待
        :param seconds:
        :return:
        """
        time.sleep(seconds)

    def implicitly_wait(self, seconds):
        """
        Implicitly wait. All elements on the page.
        :param seconds 等待时间 秒
        隐式等待

        Usage:
        driver.implicitly_wait(10)
        """
        self._web_driver.implicitly_wait(seconds)

    def explicitly_wait(self, selector, seconds):
        """
        显式等待
        :param selector: 定位字符
        :param seconds: 最长等待时间，秒
        :return:
        """
        locator = self._convert_selector_to_locator(selector)

        WebDriverWait(self._web_driver, seconds).until(expected_conditions.presence_of_element_located(locator))

    def get_explicitly_wait_element_text(self, selector, seconds):
        """
        显式等待，得到元素的 text
        :param selector: locator
        :param seconds: max timeout sencods
        :return:  str, element.text
        """

        locator = self._convert_selector_to_locator(selector)
        driver = self._web_driver

        el = WebDriverWait(driver, seconds).until(lambda d: d.find_element(*locator))
        if el and isinstance(el, WebElement):
            return el.text

        return None

    """
    属性
    """

    @property
    def current_title(self):
        '''
        Get window title.

        Usage:
        driver.current_title
        '''
        return self._web_driver.title

    @property
    def current_url(self):
        """
        Get the URL address of the current page.

        Usage:
        driver.current_url
        """
        return self._web_driver.current_url
