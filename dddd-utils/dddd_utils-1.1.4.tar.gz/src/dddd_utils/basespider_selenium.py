# -*- coding: utf-8 -*-
__all__ = [
    "SeleniumBaseSpider"
]

import logging
import time
import string
import datetime
import zipfile
import psutil
from selenium.webdriver.common.by import By
from dddd_utils.basespider import BaseSpider


class SeleniumBaseSpider(BaseSpider):
    def __init__(self, task_name, redis_config=None, mysql_config=None, mail_config=None, log_enabled=True, log_level=logging.DEBUG, log_file_path=None):
        super(SeleniumBaseSpider, self).__init__(task_name=task_name, redis_config=redis_config, mysql_config=mysql_config, mail_config=mail_config, log_enabled=log_enabled, log_level=log_level, log_file_path=log_file_path)
        self.headless = True  # 无头模式
        self.incognito = True  # 无痕模式
        self.no_picture = False  # 禁止加载图片元素
        self.no_pop_ups = False  # 禁止弹窗
        self.no_extensions = False  # 禁止使用插件
        self.use_proxy_selenium = False  # 使用代理
        self.use_userdata = False  # 保存历史和缓存（多爬虫同时使用不行）
        self.userdata_file_path = "./userdata"  # 浏览器目录
        self.executable_path = "/usr/local/bin/chromedriver"
        self.page_load_timeout = 180  # 秒
        self.proxy_plugin_path = "./proxy_auth_plugin.zip"  # 代理插件的位置
        self.cur_browser_process_list = []  # 当前webdriver相关的所有进程

    def create_browser(self):
        """
        初始化一个chrome
        """
        from selenium import webdriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("lang=zh_CN.UTF-8")  # 设置中文
        # chrome_options.add_argument(f"user-agent={self.get_random_ua()}")  # 更换头部
        chrome_options.add_argument("--no-sandbox")  # root
        chrome_options.add_argument("--disable-gpu")  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument("--hide-scrollbars")  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument("disable-infobars")  # 关闭提示
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")  # 忽略验证：您的连接不是私密连接
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 取消chrome受自动控制提示

        if self.no_extensions:
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_experimental_option("useAutomationExtension", False)

        if self.no_picture:
            chrome_options.add_argument("blink-settings=imagesEnabled=false")

        if self.no_pop_ups:
            # 禁止弹窗加入
            prefs = {
                "profile.default_content_setting_values":
                    {
                        "notifications": 2
                    }
            }
        else:
            prefs = dict()
        prefs["credentials_enable_service"] = False
        prefs["profile.password_manager_enabled"] = False
        chrome_options.add_experimental_option("prefs", prefs)

        if self.use_proxy_selenium:
            # 无头模式，无痕模式 不支持使用扩展
            self.headless = False
            self.incognito = False
            self.use_userdata = False
            # 获取代理
            proxy_dict = self.get_proxy_ip()
            if proxy_dict.get("username", None) is not None:
                # 创建插件
                plugin_path = self.__create_proxyauth_extension(proxy_host=proxy_dict["ip"], proxy_port=proxy_dict["port"], proxy_username=proxy_dict["username"], proxy_password=proxy_dict["password"])
                chrome_options.add_extension(plugin_path)
            else:
                # 代理不需要账号密码
                chrome_options.add_argument(f"--proxy-server=http://{proxy_dict['ip']}:{proxy_dict['port']}")

        if self.use_userdata:
            chrome_options.add_argument(f"--user-data-dir={self.userdata_file_path}")

        if self.incognito:
            # 无痕
            chrome_options.add_argument("--incognito")

        if self.headless:
            chrome_options.add_argument("--headless")

        for i in range(2):
            try:
                browser = webdriver.Chrome(executable_path=self.executable_path, options=chrome_options)
                browser_process = browser.service.process
                process = psutil.Process(browser_process.pid)
                process_list = process.children(recursive=True)
                self.cur_browser_process_list.append(process)
                self.cur_browser_process_list.extend(process_list)
                break
            except Exception as e:
                from pyvirtualdisplay import Display
                display = Display(visible=False, size=(1792, 1120))
                display.start()
        else:
            # 浏览器启动失败
            raise e

        browser.set_page_load_timeout(self.page_load_timeout)

        # try:
        #     tk = tkinter.Tk()
        #     width = tk.winfo_screenwidth()
        #     height = tk.winfo_screenheight()
        #     tk.quit()
        # except:
        width = 1792
        height = 1120
        browser.set_window_size(width, height)

        browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, "webdriver", {
              get: () => undefined
            })
          """
        })
        return browser

    def clear_and_send_keys(self, browser, by: str, rule: str, msg):
        """
        点击并发送
        每次都获取是因为有时旧的元素定位不到会报错，所以每次都重新获取元素并完成相应操作
        :param browser: 浏览器对象
        :param by: 通过什么方式定位，如： id，xpath，css_selector
        :param rule: 定位的规则
        :param msg: 需要输入的值
        :return:
        """
        by = by.lower()
        self.__get_element(browser, by, rule).clear()
        time.sleep(0.3)
        self.__get_element(browser, by, rule).send_keys(msg)
        time.sleep(0.5)

    def find_element_by_xpath(self, browser, rule: str):
        """通过xpath获取元素"""
        return self.__get_element(browser, "xpath", rule)

    def find_element_by_id(self, browser, rule: str):
        """通过id获取元素"""
        return self.__get_element(browser, "id", rule)

    def click_by_js(self, browser, by, rule):
        """通过js点击"""
        by = by.lower()
        ele = self.__get_element(browser, by, rule)
        browser.execute_script("arguments[0].click();", ele)
        time.sleep(0.5)

    def scroll_to_ele(self, browser, by, rule):
        """滚动到某个元素的位置"""
        ele = self.__get_element(browser, by, rule)
        js4 = "arguments[0].scrollIntoView();"
        browser.execute_script(js4, ele)
        return True

    @staticmethod
    def get_browser_cookies(browser):
        """获取当前浏览器cookie，返回str"""
        cookie_dict = browser.get_cookies()
        cookies = ""
        for cookie in cookie_dict:
            if not cookie["name"].startswith("_"):
                cookies += cookie["name"] + "=" + cookie["value"] + ";"
        return cookies.strip(";")

    def __create_proxyauth_extension(self, proxy_host, proxy_port, proxy_username, proxy_password, scheme="http"):
        """带密码验证的扩展"""
        plugin_path = self.proxy_plugin_path

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = string.Template(
            """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                      singleProxy: {
                        scheme: "${scheme}",
                        host: "${host}",
                        port: parseInt(${port})
                      },
                      bypassList: ["foobar.com"]
                    }
                  };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "${username}",
                        password: "${password}"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ["blocking"]
            );
            """
        ).substitute(
            host=proxy_host,
            port=proxy_port,
            username=proxy_username,
            password=proxy_password,
            scheme=scheme,
        )
        with zipfile.ZipFile(plugin_path, "w") as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return plugin_path

    def close_browser(self, browser):
        """
        关闭浏览器
        """
        try:
            browser.quit()
            time.sleep(0.5)
            for process in self.cur_browser_process_list:
                try:
                    process.kill()
                except:
                    pass
        except:
            pass
        return True

    def init_new_browser(self, browser, next_init_time):
        """
        :param browser: 浏览器
        :param next_init_time: 下次初始化时间
        :return:
        """
        if datetime.datetime.now() >= next_init_time:
            self.close_browser(browser)
            browser = self.create_browser()
            next_init_time = datetime.datetime.now() + datetime.timedelta(hours=2)
        return browser, next_init_time

    def __get_element(self, browser, by, value):
        """通过不同的方式查找界面元素"""
        element = None
        by = by.lower()
        if by == "id":
            element = browser.find_element(by=By.ID, value=value)
        elif by == "name":
            element = browser.find_element(by=By.NAME, value=value)
        elif by == "xpath":
            element = browser.find_element(by=By.XPATH, value=value)
        elif by == "classname":
            element = browser.find_element(by=By.CLASS_NAME, value=value)
        elif by == "css":
            element = browser.find_element(by=By.CSS_SELECTOR, value=value)
        elif by == "link_text":
            element = browser.find_element(by=By.LINK_TEXT, value=value)
        else:
            self.logger.error("无对应方法，请检查")
        return element
