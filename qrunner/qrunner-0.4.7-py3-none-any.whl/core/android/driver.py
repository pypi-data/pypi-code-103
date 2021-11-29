import uiautomator2 as u2
from qrunner import Browser, logger, Device


class AndroidDriver(object):
    _instance = {}

    def __new__(cls, serial_no=None):
        if not serial_no:
            serial_no = Browser.serial_no
        if serial_no not in cls._instance:
            cls._instance[serial_no] = super().__new__(cls)
        return cls._instance[serial_no]

    def __init__(self, serial_no=None):
        if not serial_no:
            serial_no = Browser.serial_no
        logger.info(f'启动 android driver for {serial_no}')
        self.d = u2.connect(serial_no)

    @classmethod
    def get_instance(cls, serial_no=None):
        """Create singleton"""
        if serial_no not in cls._instance:
            logger.info(f'[{serial_no}] Create android driver singleton')
            return AndroidDriver(serial_no).d
        return AndroidDriver._instance[serial_no].d

    @classmethod
    def get_remote_instance(cls, server_url, token):
        device = Device(server_url, token)
        d = u2.connect(device.get_device())
        return d, device

    # def uninstall_app(self, pkg_name=None):
    #     if not pkg_name:
    #         pkg_name = self.pkg_name
    #     logger.info(f'卸载应用: {pkg_name}')
    #     self.d.app_uninstall(pkg_name)
    #
    # def install_app(self, apk_path, is_new=False):
    #     if is_new:
    #         self.uninstall_app(self.pkg_name)
    #     logger.info(f'安装应用: {apk_path}')
    #     self.d.app_install(apk_path)
    #
    # def start_app(self, pkg_name=None):
    #     if not pkg_name:
    #         pkg_name = self.pkg_name
    #     logger.info(f'启动应用: {pkg_name}')
    #     self.d.app_start(pkg_name)
    #
    # def stop_app(self, pkg_name=None):
    #     if not pkg_name:
    #         pkg_name = self.pkg_name
    #     logger.info(f'退出应用: {pkg_name}')
    #     self.d.app_stop(pkg_name)
    #
    # def force_start_app(self, pkg_name=None):
    #     if not pkg_name:
    #         pkg_name = self.pkg_name
    #     logger.info(f'强制启动应用: {pkg_name}')
    #     self.d.app_start(pkg_name, stop=True)
    #
    # def go_home(self):
    #     time.sleep(1)
    #     logger.info('返回手机桌面')
    #     self.d.press('home')
    #
    # def back(self):
    #     time.sleep(1)
    #     logger.info('返回上一页')
    #     self.d.press('back')
    #
    # def swipe(self, x1, y1, x2, y2, duration=0):
    #     logger.info(f'从坐标({x1}, {y1})滑到坐标({x2}, {y2})')
    #     self.d.swipe(x1, y1, x2, y2, duration=duration)
    #     time.sleep(2)
    #
    # def swipe_left(self):
    #     logger.info('向左边滑动')
    #     self.d.swipe_ext('left')
    #
    # def swipe_right(self):
    #     logger.info('向右边滑动')
    #     self.d.swipe_ext('right')
    #
    # def swipe_up(self):
    #     logger.info('向上滑动')
    #     self.d.swipe_ext('up')
    #
    # def swipe_down(self):
    #     logger.info('向下滑动')
    #     self.d.swipe_ext('down')
    #
    # def tap(self, x, y):
    #     logger.info(f'点击坐标({x},{y})')
    #     self.d.click(x, y)
    #     time.sleep(1)
    #
    # def screenshot(self, img_path):
    #     logger.info(f'截屏并保存至: {img_path}')
    #     image = self.d.screenshot()
    #     image.save(img_path)
    #
    # def allure_shot(self, filename, timeout=1):
    #     logger.info(f'{filename}-截图')
    #     time.sleep(timeout)
    #     self.d.screenshot('tmp.png')
    #     allure.attach.file('tmp.png', attachment_type=allure.attachment_type.PNG, name=f'{filename}-截图')
    #     os.remove('tmp.png')
    #
    # def send_keys(self, value):
    #     logger.info(f'输入: {value}')
    #     self.d.set_fastinput_ime(True)
    #     self.d.send_keys(value)
    #     self.d.send_action('search')
    #     self.d.set_fastinput_ime(False)
    #
    # def send_password(self, value):
    #     logger.info(f'输入密码: {value}')
    #     self.d(focused=True).set_text(value)
    #
    # # def enter(self):
    # #     logger.info('键盘点击enter')
    # #     self.d.press('enter')
    #
    # def delete(self):
    #     logger.info('点击一次退格键')
    #     self.d.press('delete')
    #
    # # 有时候clear_text方法不管用，可以尝试该方法
    # def clear(self, num=10):
    #     logger.info('清空输入框: 通过点击10次退格键实现')
    #     for i in range(num):
    #         self.delete()
    #
    # @property
    # def page_source(self):
    #     page_source = self.d.dump_hierarchy()
    #     logger.info(f'获取页面内容: \n{page_source}')
    #     return page_source




