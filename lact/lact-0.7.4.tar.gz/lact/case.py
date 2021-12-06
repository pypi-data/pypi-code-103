import time
from datetime import datetime

import allure
import pytest

from .data import build_data
from .helper import get_project_path, parse_dict, str_to_decimal, Dict
from .logger import build_logger, info, error
from .request import Request, build_request

""" 私有方法，仅供本文件使用 """


def _get_allure_test_level(level: int):
    """
    获取测试用例的执行优先级
    :param level:
    :return:
    1： blocker
    2： critical
    3： normal
    4： minor
    """
    if level not in (1, 2, 3, 4):
        return allure.severity_level.NORMAL

    if level == 1:
        return allure.severity_level.BLOCKER

    if level == 2:
        return allure.severity_level.CRITICAL

    if level == 3:
        return allure.severity_level.NORMAL

    if level == 4:
        return allure.severity_level.MINOR


""" 测试用例使用的 annotation 注解"""


def pytest_configure(config):
    """
    pytest Configure 配置
    :param config:
    :return:
    """
    config.addinivalue_line("markers", "allure_epic: this one is for cool tests.")
    config.addinivalue_line("markers", "allure_feature: this one is for cool tests.")
    config.addinivalue_line("markers", "allure_story: this one is for cool tests.")
    config.addinivalue_line("markers", "allure_tag: this one is for cool tests.")
    config.addinivalue_line("markers", "allure_title: this one is for cool tests.")
    config.addinivalue_line("markers", "allure_severity: this one is for cool tests.")


def allure_epic(desc: dict):
    """
    allure report 装饰器 epic
    :param desc:
    :return:
    """
    return allure.epic(parse_dict(desc, "epic"))


def allure_feature(desc: dict):
    """
    allure report 装饰器 feature
    :param desc:
    :return:
    """
    return allure.feature(parse_dict(desc, "feature"))


def allure_story(desc: dict):
    """
    allure report 装饰器 story
    :param desc:
    :return:
    """
    return allure.story(parse_dict(desc, "story"))


def allure_tag(desc: dict):
    """
    allure report 装饰器 story
    :param desc:
    :return:
    """
    return allure.tag(*tuple(parse_dict(desc, "tag")))


def allure_title(desc: dict):
    """
    allure report 装饰器 story
    :param desc:
    :return:
    """
    return allure.title(parse_dict(desc, "title"))


def allure_severity(desc: dict):
    """
    allure report 装饰器 story
    :param desc:
    :return:
    """
    level = _get_allure_test_level(parse_dict(desc, "level"))
    return allure.severity(level)


def allure_step(title):
    """
    allure report 装饰器 step
    :param title:
    :return:
    """
    return allure.step(title)


def pytest_parametrize(test_data):
    """
    pytest 装饰器，参数化
    :param test_data: 默认使用 “test_data” 作为用例中参数话的参数名
    :return:
    """
    return pytest.mark.parametrize("test_data", test_data)


def pytest_fixture(auto_use: bool):
    """
    pytest 上下文装饰器，配合 yield 进行 setup 和 teardown
    :param auto_use:
    :return:
    """
    return pytest.fixture(autouse=auto_use)


class Case(object):
    """
    Desc: Encapsulation of requests library
    Date: 20191127
    Author: Linty Liu (Tingli)
    Email: liu.tingli@outlook.com
    """
    __logger = None
    __request = None
    __data = None

    """ 需要子类重写的方法 """

    def pre_test(self):
        """
        测试前准备工作
        :return:
        """
        return

    def post_test(self):
        """
        测试后清理操作
        :return:
        """
        return

    def exec_test(self, test_data):
        """
        执行测试的具体步骤，便于子类调用
        :param test_data: 通过读取 测试数据 得到一条 test_data
        :return:
        """

    """ 基础方法 """

    def info(self, msg):
        """
        记录日志
        :param msg:
        :return:
        """
        info(msg=msg, log=self.logger)

    def error(self, msg):
        """
        记录日志
        :param msg:
        :return:
        """
        error(msg=msg, log=self.logger)

    @pytest_fixture(True)
    def prepare(self):
        """
        测试执行使用的测试固件，包含前置条件和清理操作
        :return: None
        """
        # 首先是前置条件，在 yield 之前
        # 准备日志文件，就可以记录整个测试
        self.pre_test()

        # 是 yield 关键字，代表执行 test_ 开头的方法的具体内容
        self.info("[%s] - 完成测试的前置条件 set_up！ " % __name__)
        yield

        # 最后是清理操作，在 yield 之后
        self.post_test()
        self.info("[%s] - 完成测试的清理操作 tear_down！ " % __name__)

    """ 初始化用例数据 """

    def init_logger(self, file_name: str):
        """
        初始化测试用例的日志文件，传递给 self._logger
        :param file_name: 在用例中，只需要传递 __name__ （固定用法，请勿改）
        :return: None
        """
        if file_name is not None:
            if file_name.strip().endswith(".log"):
                file_name = file_name.strip().replace(".log", "")

            file_name = "report/log/%s_%s.log" % (file_name, self.current_time_string)
        log_path = get_project_path(file_name)
        self.__logger = build_logger(log_path=log_path)
        self.info(
            "[%s] - 系统初始化日志，请求数据：%r" % (__name__, dict(log_path=log_path))
        )

    def init_request(self, schema: str, host: str, port=None, gateway=None, middle=None):
        """
        初始化测试用例的请求对象，传递给 self._request
        :param middle: 主机与接口（网关）之间的路径
        :param gateway: 网关地址
        :param schema: 协议，http 或者 https，忽略大小写
        :param host: 主机，ip 地址，或者 域名，或者 localhost 等主机名，忽略大小写
        :param port: 数字，整型，默认可以不传，如果不传，就使用 schema 的默认端口
            http： 默认 80
            https： 默认 443
        :return: None
        """
        self.__request = build_request(schema=schema, host=host, port=port, gateway=gateway, middle=middle)

        self.info(
            "[%s] - 系统初始化请求，请求数据：%r" % (__name__, dict(schema=schema, host=host, port=port, gateway=gateway))
        )

    def init_data(self, param_dict: dict, auth_dict: dict, header_dict: dict, cookie_dict: dict, expected_dict: dict,
                  extra_dict: dict, assertion_script: dict):
        """
        初始化准备用例的输入数据
        :param assertion_script:
        :param expected_dict:
        :param param_dict:
        :param auth_dict:
        :param header_dict:
        :param cookie_dict:
        :param extra_dict:
        :return:
        """
        self.data = build_data(
            param_dict=param_dict,
            auth_dict=auth_dict,
            header_dict=header_dict,
            cookie_dict=cookie_dict,
            expected_dict=expected_dict,
            assertion_script=assertion_script,
            extra_dict=extra_dict
        )
        self.info(
            "[%s] - 系统初始化测试数据，请求数据：%r" % (__name__, self.__data)
        )

    """ 断言方法 """

    @allure_step(title="断言：结果 包含 期望值")
    def assert_in(self, expected, actual):
        """
        assert in, expected in actual
        :param expected:
        :param actual:
        :return:
            例如
                "胡艳" in "胡晓艳"  fail
                "胡" in "胡晓艳"  success
        """
        if expected is not None and actual is not None:
            if isinstance(actual, int):
                actual = str(actual)
            result = expected in actual
            log_msg = "[%s] - 系统进行断言 assert_in：expected{%r} in {%r} 的结果是 {%r}！" % (__name__, expected, actual, result)

            self.info(log_msg)
            # 如果执行断言失败，就抓包
            if not result:
                self.capture(log_msg[0: 50])
            return result
        return False

    @allure_step(title="断言：结果 属于 期望值")
    def assert_out(self, expected, actual):
        """
        assert out, expected out actual
        :param expected:
        :param actual:
        :return:
            例如
                "胡晓艳" out "胡艳"  fail
                "胡晓艳" out "胡"  success
                如果有 int 型数据，请使用数组
        """
        if expected is not None and actual is not None:
            result = actual in expected
            log_msg = "[%s] - 系统进行断言 assert_out：expected{%r} out actual{%r} 的结果是 {%r}！" % (
                __name__, expected, actual, result)

            self.info(log_msg)
            # 如果执行断言失败，就抓包
            if not result:
                self.capture(log_msg[0: 50])
            return result
        return False

    @allure_step(title="断言：结果为 True")
    def assert_true(self, expression):
        """
        assert equal
        :param expression:
        :return: boolean， True 或者 False，让用例 通过 assert 使用
            :usage
                assert self.assert_equal(expected=xx, actual=yy)
            类型要一致
            例如
                "1" == 1  fail
                1 == 1 success
                str, int, float, boolean( True, False)...
                object 类型不可以相等
                    api1 = NspUserApi()
                    api2 = NspUserApi()
                    api1 == api2  fail
        """
        result = expression is True
        log_msg = "[%s] - 系统进行断言 assert_true：expected{%r} == actual{%r} 的结果是 {%r}！" % (
            __name__, True, expression, result)

        self.info(log_msg)
        # 如果执行断言失败，就抓包
        if not result:
            self.capture(log_msg[0: 25])
        return result

    @allure_step(title="断言：结果 等于 期望值")
    def assert_equal(self, expected, actual):
        """
        assert equal
        :param expected:
        :param actual:
        :return: boolean， True 或者 False，让用例 通过 assert 使用
            :usage
                assert self.assert_equal(expected=xx, actual=yy)
            类型要一致
            例如
                "1" == 1  fail
                1 == 1 success
                str, int, float, boolean( True, False)...
                object 类型不可以相等
                    api1 = NspUserApi()
                    api2 = NspUserApi()
                    api1 == api2  fail
        """
        result = False
        if expected is not None and actual is not None:
            result = expected == actual

        log_msg = "[%s] - 系统进行断言 assert_equal：expected{%r} == actual{%r} 的结果是 {%r}！" % (
            __name__, expected, actual, result)

        self.info(log_msg)
        # 如果执行断言失败，就抓包
        if not result:
            self.capture(log_msg[0: 50])
        return result

    @allure_step(title="断言：结果 整型等于 期望值（忽略字符串与数值）")
    def assert_int_equal(self, expected, actual):
        """
        assert int equal, 忽略字符串和数字之间的差异
        :param expected:
        :param actual:
        :return:
            例如
                assert_int_equal(1, "1") success
                assert_int_equal(1.0, "1")  success
                assert_int_equal(-1.0, "-1")  success
                assert_int_equal(-1.0, "-1.0")  success
                assert_int_equal(-1, "-1.0")  success
        """
        result = False

        expected = str_to_decimal(expected, digits=0)
        actual = str_to_decimal(actual, digits=0)

        if expected is not None and actual is not None:
            result = expected == actual

        log_msg = "[%s] - 系统进行断言 assert_int_equal：expected{%r} == actual{%r} 的结果是 {%r}！" % (
            __name__, expected, actual, result)

        self.info(log_msg)
        # 如果执行断言失败，就抓包
        if not result:
            self.capture(log_msg[0: 50])
        return result

    @allure_step(title="断言：结果 数值型等于 期望值（忽略字符串与数值）")
    def assert_decimal_equal(self, expected, actual, digits=2):
        """
        assert int equal, 忽略字符串和数值的差别
        :param digits: 小数位数
        :param expected:
        :param actual:
        :return:
            例子
                assert_decimal_equal("123.88", 123.88, 2) success
                assert_decimal_equal("123.88", 123.88, 1) success
                assert_decimal_equal("123.88", 123.89, 1) success
                assert_decimal_equal("123.88", 123.89, 2) fail
        """
        result = False

        expected = str_to_decimal(expected, digits)
        actual = str_to_decimal(actual, digits)

        if expected is not None and actual is not None:
            result = expected == actual

        log_msg = "[%s] - 系统进行断言 assert_decimal_equal：小数位{%r}, expected{%r} == actual{%r} 的结果是 {%r}！" \
                  % (__name__, digits, expected, actual, result)

        self.info(log_msg)
        # 如果执行断言失败，就抓包
        if not result:
            self.capture(log_msg[0: 50])
        return result

    @allure_step(title="断言：结果 字典等于 期望值")
    def assert_dict_equal(self, expected, actual, data_key, index=None, sub_key=None):
        """
        断言 字典是否相等
        :param expected: 期望的结果 dict 格式
        :param actual: 实际的结果 dict 格式
        :param data_key: data key
        :param index: 下标，默认为 None
        :param sub_key: 子 data key，默认为 None
        :return:
        """
        result = False
        expected_value = parse_dict(expected, data_key, index, sub_key)
        actual_value = parse_dict(actual, data_key, index, sub_key)

        if expected_value is not None and actual_value is not None:
            result = expected_value == actual_value

        log_msg = "[%s] - 系统进行断言 assert_dict_equal： expected{%r} == actual{%r}, data_key=%s, index=%r, sub_key=%s 的结果是 {%r}！" \
                  % (__name__, expected_value, actual_value, data_key, index, sub_key, result)

        self.info(log_msg)
        # 如果执行断言失败，就抓包
        if not result:
            self.capture(log_msg[0: 50])
        return result

    @allure_step(title="断言：结果 字典包含 期望值")
    def assert_dict_in(self, expected, actual, data_key, index=None, sub_key=None):
        """
        断言 字典是否包含
        :param expected: 期望的结果 dict 格式
        :param actual: 实际的结果 dict 格式
        :param data_key: data key
        :param index: 下标，默认为 None
        :param sub_key: 子 data key，默认为 None
        :return:
        """
        result = False
        expected_value = parse_dict(expected, data_key, index, sub_key)
        actual_value = parse_dict(actual, data_key, index, sub_key)

        if expected_value is not None and actual_value is not None:
            result = expected_value in actual_value

        log_msg = "[%s] - 系统进行断言 assert_dict_in： expected{%r} in actual{%r}, data_key=%s, index=%r, sub_key=%s 的结果是 {%r}！" \
                  % (__name__, expected_value, actual_value, data_key, index, sub_key, result)

        self.info(log_msg)
        # 如果执行断言失败，就抓包
        if not result:
            self.capture(log_msg[0: 50])
        return result

    @allure_step(title="断言：结果 字典属于 期望值")
    def assert_dict_out(self, expected, actual, data_key, index=None, sub_key=None):
        """
        断言 字典是否被包含
        :param expected: 期望的结果 dict 格式
        :param actual: 实际的结果 dict 格式
        :param data_key: data key
        :param index: 下标，默认为 None
        :param sub_key: 子 data key，默认为 None
        :return:
        """
        result = False
        expected_value = parse_dict(expected, data_key, index, sub_key)
        actual_value = parse_dict(actual, data_key, index, sub_key)

        if expected_value is not None and actual_value is not None:
            result = actual_value in expected_value

        log_msg = "[%s] - 系统进行断言 assert_dict_in： expected{%r} out actual{%r}, data_key=%s, index=%r, sub_key=%s 的结果是 {%r}！" \
                  % (__name__, expected_value, actual_value, data_key, index, sub_key, result)

        self.info(log_msg)
        # 如果执行断言失败，就抓包
        if not result:
            self.capture(log_msg[0: 50])
        return result

    """ 其他公有方法 """

    def wait(self, seconds=5):
        """
        让 python 等待，默认 5 秒钟
        :param seconds: int， 大于 0
        :return:
        """
        if not isinstance(seconds, int) or seconds <= 0:
            seconds = 5

        self.info("[%s] - 系统等待执行 %d 秒" % (__name__, seconds))
        time.sleep(seconds)

    def close_request(self):
        """
        关闭请求
        :return:
        """
        self.info("[%s] - 系统关闭请求！" % __name__)
        if self.request is not None and isinstance(self.request, Request):
            self.request.close()

    @allure_step(title="测试步骤抓包截图")
    def capture(self, title=None, content_dict: dict = None):
        """
        抓包 HTTP/HTTPS 请求和响应，并且记录在 allure 报告中
        :param title : 标题
        :param content_dict : 截图内容
        :return: None
        """
        if title is None or title == "":
            title = self.current_time_string

        snapshot_json = ""
        if content_dict is not None and isinstance(content_dict, dict):
            snapshot_json = Dict.dump_json(dict_to_dump=content_dict)

        elif self.request is not None and isinstance(self.request, Request):
            snapshot_json = self.request.json_format_string

        allure.attach(snapshot_json, name="json_%s" % title, attachment_type=allure.attachment_type.JSON)

        self.info("[%s] - 系统进行抓包，snapshot title：json_%s " % (__name__, title))

    """ 测试用例类的属性 """

    @property
    def request(self):
        """
        请求对象，给业务使用，让他使用这个对象发请求
        :return:
        """
        return self.__request

    @property
    def data(self):
        """
        请求对象，给业务使用，让他使用这个对象发请求
        :return:
        """
        return self.__data

    @data.setter
    def data(self, data):
        """
        请求对象，给业务使用，让他使用这个对象发请求
        :return:
        """
        self.__data = data

    @property
    def logger(self):
        """
        日志对象，给业务使用，让他使用这个对象写日志，把他做的事情记录在里面
        :return:
        """
        return self.__logger

    @property
    def current_time_string(self):
        """
        当前时间的字符串格式
        :return:
        """
        return time.strftime("%Y%m%d%H%M%S", time.localtime())

    @property
    def current_time_string_datetime_long(self):
        """
        当前时间的字符串格式
        :return:
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    @property
    def current_time_string_date_only(self):
        """
        当前时间的字符串格式
        :return:
        """
        return time.strftime("%Y-%m-%d", time.localtime())

    @property
    def current_time_string_date_year_month(self):
        """
        当前时间的字符串格式
        :return:
        """
        return time.strftime("%Y%m", time.localtime())

    @property
    def current_datetime(self):
        """
        当前时间，日期格式
        :return:
        """
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    @property
    def current_timestamp(self):
        """
        当前时间戳
        :return: 精确到整数
        """
        return round(time.time(), 0)

    @property
    def current_timestamp2(self):
        """
        当前时间戳
        :return: 精确到整数
        """
        return time.time()
