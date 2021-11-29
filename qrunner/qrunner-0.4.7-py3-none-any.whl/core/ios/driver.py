import binascii
import time
import requests
import wda
from qrunner import logger, Browser, Device
from qrunner.core.ios.wda_server import WDAServer

max_retry = 3


def relaunch_wda(func):
    def wrapper(self, *args, **kwargs):
        return _inner_retry(self, func, *args, **kwargs)
    return wrapper


def _inner_retry(self, func, *args, **kwargs):
    global max_retry

    while max_retry > 0:
        try:
            return func(self, *args, **kwargs)
        except (requests.exceptions.ConnectionError, wda.WDAError,
                binascii.Error, requests.exceptions.ReadTimeout) as _:
            time.sleep(3)
            logger.info(f'开始重连wda')
            WDAServer(Browser.serial_no).launch_wda()
            max_retry -= 1
            logger.info(f'剩余重连次数: {max_retry}')
    return func(self, *args, **kwargs)


class IosDriver(object):
    # _instance = {}
    #
    # def __new__(cls, serial_no=None):
    #     if not serial_no:
    #         serial_no = Browser.serial_no
    #     if serial_no not in cls._instance:
    #         cls._instance[serial_no] = super().__new__(cls)
    #     return cls._instance[serial_no]

    def __init__(self, serial_no=None):
        if not serial_no:
            self.serial_no = Browser.serial_no
        else:
            self.serial_no = serial_no
        self.bundle_id = Browser.pkg_name
        logger.info(f'启动 ios driver for {self.serial_no}')
        self.d = wda.USBClient(serial_no, port=8100,
                               wda_bundle_id='com.facebook.WebDriverAgentRunner.xctrunner')

    # @classmethod
    # def get_instance(cls, serial_no=None):
    #     if serial_no not in cls._instance:
    #         logger.info(f'{serial_no} Create ios driver singleton')
    #         return IosDriver(serial_no).d
    #     return IosDriver._instance[serial_no].d
    #
    # @classmethod
    # def get_remote_instance(cls, server_url, token):
    #     device = Device(server_url, token)
    #     d = wda.Client(device.get_device(platform='apple'))
    #     return d, device@classmethod
    # def get_instance(cls, serial_no=None):
    #     if serial_no not in cls._instance:
    #         logger.info(f'{serial_no} Create ios driver singleton')
    #         return IosDriver(serial_no).d
    #     return IosDriver._instance[serial_no].d
    #
    # @classmethod
    # def get_remote_instance(cls, server_url, token):
    #     device = Device(server_url, token)
    #     d = wda.Client(device.get_device(platform='apple'))
    #     return d, device

#     def uninstall_app(self, bundle_id=None):
#         if not bundle_id:
#             bundle_id = self.bundle_id
#         cmd = f'tidevice -u {self.serial_no} uninstall {bundle_id}'
#         logger.info(f'卸载应用: {bundle_id}')
#         output = subprocess.getoutput(cmd)
#         if 'Complete' in output.split()[-1]:
#             logger.info(f'{self.serial_no} 卸载应用{bundle_id} 成功')
#             return
#         else:
#             logger.info(f'{self.serial_no} 卸载应用{bundle_id}失败，因为{output}')
#
#     def install_app(self, ipa_url, is_new=False):
#         if is_new:
#             self.uninstall_app(self.bundle_id)
#         cmd = f'tidevice -u {self.serial_no} install {ipa_url}'
#         logger.info(f'安装应用: {ipa_url}')
#         output = subprocess.getoutput(cmd)
#         if 'Complete' in output.split()[-1]:
#             logger.info(f'{self.serial_no} 安装应用{ipa_url} 成功')
#             return
#         else:
#             logger.info(f'{self.serial_no} 安装应用{ipa_url}失败，因为{output}')
#
    @relaunch_wda
    def start_app(self, bundle_id=None):
        if not bundle_id:
            bundle_id = self.bundle_id
        try:
            logger.info(f'启动应用: {bundle_id}')
            self.d.app_start(bundle_id)
            logger.info(f'{self.serial_no} 成功启动APP成功: {bundle_id}')
        except requests.exceptions.ReadTimeout:
            logger.error(f'{self.serial_no} 成功启动APP失败: {bundle_id}')

    @relaunch_wda
    def force_start_app(self, bundle_id=None):
        if not bundle_id:
            bundle_id = self.bundle_id
        logger.info(f'强制启动应用: {bundle_id}')
        self.go_home()
        self.d.app_terminate(bundle_id)
        self.start_app(bundle_id)

    @relaunch_wda
    def stop_app(self, bundle_id=None):
        if not bundle_id:
            bundle_id = self.bundle_id
        logger.info(f'停止应用: {bundle_id}')
        self.d.app_terminate(bundle_id)
#
#     @relaunch_wda
#     def app_current(self):
#         cur_apps = self.d.app_current()
#         logger.info(f'获取运行中的app列表: {cur_apps}')
#         return cur_apps
#
#     @relaunch_wda
#     def app_launch(self, bundle_id=None):
#         if not bundle_id:
#             bundle_id = self.bundle_id
#         logger.info(f'将应用切到前台: {bundle_id}')
#         self.d.app_launch(bundle_id)
#
#     @relaunch_wda
#     def back(self):
#         logger.info('返回上一页')
#         time.sleep(1)
#         self.d.swipe(0, 100, 100, 100)
#
#     @relaunch_wda
#     def locked(self):
#         logger.info('锁屏')
#         self.d.locked()
#
#     @relaunch_wda
#     def unlock(self):
#         logger.info('退出锁屏')
#         if self.locked():
#             self.d.unlock()
#
    @relaunch_wda
    def go_home(self):
        logger.info('返回手机主页')
        self.d.home()
#
#     @relaunch_wda
#     def send_keys(self, value):
#         logger.info(f'输入: {value}')
#         self.d.send_keys(value)
#
#     @relaunch_wda
#     def screenshot(self, img_path):
#         logger.info(f'截图并保存至: {img_path}')
#         im = self.d.screenshot()
#         rgb_im = im.convert('RGB')
#         rgb_im.save(img_path)
#
#     @relaunch_wda
#     def allure_shot(self, filename, timeout=1):
#         logger.info(f'{filename}-截图')
#         time.sleep(timeout)
#         self.screenshot('tmp.png')
#         allure.attach.file('tmp.png', attachment_type=allure.attachment_type.PNG, name=f'{filename}-截图')
#         os.remove('tmp.png')
#
#     @relaunch_wda
#     def get_ui_tree(self):
#         page_source = self.d.source(accessible=False)
#         logger.info(f'获取页面内容: \n{page_source}')
#         return page_source
#
#     @relaunch_wda
#     def get_window_size(self):
#         size = self.d.window_size()
#         logger.info(f'获取屏幕尺寸: {size}')
#         return size
#
#     @relaunch_wda
#     def tap(self, x, y):
#         logger.info(f'点击坐标: ({x}, {y})')
#         logger.info(f'{self.serial_no} Tap point ({x}, {y})')
#         self.d.appium_settings({"snapshotMaxDepth": 0})
#         self.d.tap(x, y)
#         self.d.appium_settings({"snapshotMaxDepth": 50})
#         time.sleep(1)
#
#     @relaunch_wda
#     def swipe(self, start_x, start_y, end_x, end_y, duration=0):
#         logger.info(f'从坐标({start_x}, {start_y})滑动到({end_x}, {end_y})')
#         logger.info(f'{self.serial_no} swipe from point ({start_x}, {start_y}) to ({end_x}, {end_y})')
#         self.d.appium_settings({"snapshotMaxDepth": 2})
#         self.d.swipe(int(start_x), int(start_y), int(end_x), int(end_y), duration)
#         self.d.appium_settings({"snapshotMaxDepth": 50})
#         time.sleep(2)
#
#     @relaunch_wda
#     def swipe_by_screen_percent(self, start_x_percent, start_y_percent, end_x_percent, end_y_percent, duration=0):
#         logger.info(f'根据屏幕百分比进行滑动')
#         w, h = self.get_window_size()
#         start_x = w * start_x_percent
#         start_y = h * start_y_percent
#         end_x = w * end_x_percent
#         end_y = h * end_y_percent
#         self.swipe(start_x, start_y, end_x, end_y, duration=duration)
#
#     @relaunch_wda
#     def swipe_left(self, start_percent=1, end_percent=0.5):
#         logger.info('往左边滑动')
#         w, h = self.get_window_size()
#         self.swipe(start_percent * (w - 1), h/2, end_percent * w, h/2)
#
#     @relaunch_wda
#     def swipe_right(self, start_percent=0.5, end_percent=1):
#         logger.info('往右边滑动')
#         w, h = self.get_window_size()
#         self.swipe(start_percent * w, h / 2, end_percent * (w - 1), h / 2)
#
#     @relaunch_wda
#     def swipe_up(self, start_percent=0.8, end_percent=0.2):
#         logger.info('往上边滑动')
#         w, h = self.get_window_size()
#         self.swipe(w / 2, start_percent * h, w / 2, end_percent * h)
#
#     @relaunch_wda
#     def swipe_down(self, start_percent=0.2, end_percent=0.8):
#         logger.info('往下面滑动')
#         w, h = self.get_window_size()
#         self.swipe(w / 2, start_percent * h, w / 2, end_percent * h)
#
#
# # 初始化
# driver = Driver()
# d = driver.d
