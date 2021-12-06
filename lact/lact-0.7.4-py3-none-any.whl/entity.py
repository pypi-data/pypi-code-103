import time

import allure

from .case import allure_step
from .data import Data
from .helper import Dict
from .logger import Logger, info
from .request import Request


class Entity(object):
    """
    Desc: basic api entity 基础实体类
    Date: 20191127
    Author: Linty Liu (Tingli)
    Email: liu.tingli@outlook.com
    """
    __logger: Logger = None
    __request = None
    __header: dict
    __param: dict
    __template_param: dict
    __resp: list

    def __init__(self, request: Request, logger: Logger = None):
        """
        ApiPage 类的构造方法
        :param request: 传递 用例中的 HttpRequest 实例化对象，默认是 self.request
        :param logger: 传递 用例中的 Logger 实例化对象，默认是 self.logger
        """

        self.__request = request
        self.__logger = logger
        self.info("[%s] - 使用构造方法完成实例化!" % __name__)
        # super().__init__(**data)

    """ 基础方法 """

    def info(self, msg):
        """
        记录日志
        :param msg:
        :return:
        """
        info(msg=msg, log=self.logger)

    """ 核心私有方法 """

    def _send(self, uri: str,
              method: str,
              data_dict=None,
              auth=None,
              cookies=None,
              headers=None,
              files=None,
              is_json_content=True,
              gateway_enable=True):
        """
        发送 HTTP/HTTPS 请求
        :param uri: 请求网址的路径部分（去掉协议，主机和端口）
        :param method:  请求方法
        :param data_dict:  请求需要传递的数据，与请求方法无关
        :param auth:  请求的授权认证
            支持 HTTP basic Auth， 传递 tuple，两个元素，分别是用户名和密码
            支持 Auth 2.0 认证，传递 str，字符串
            支持 自定义或者其他认证，传递 dict，两个key： key 和 value
        :param cookies:
        :param headers: 请求头
        :param files:  请求文件
        :param is_json_content: 是否是 JSON 格式的内容
        :param gateway_enable: 是否在 uri 中添加网关
        :return:
        """

        self.info("[%s] - 在 BaseApi 类中发送请求，使用的数据：uri=%s, method=%s, data_dict=%r, auth=%r"
                  % (__name__, uri, method, data_dict, auth))

        if self.request is not None and isinstance(self.request, Request):
            self.request.send(
                uri=uri,
                method=method,
                data_dict=data_dict,
                auth=auth,
                cookies=cookies,
                headers=headers,
                files=files,
                is_json_content=is_json_content,
                gateway_enable=gateway_enable
            )

    def _request(self, url: str,
                 method: str,
                 data_dict=None,
                 auth=None,
                 cookies=None,
                 headers=None,
                 files=None,
                 is_json_content=True):
        """
        发送 HTTP/HTTPS 请求
        :param url: 请求网址
        :param method:  请求方法
        :param data_dict:  请求需要传递的数据，与请求方法无关
        :param auth:  请求的授权认证
            支持 HTTP basic Auth， 传递 tuple，两个元素，分别是用户名和密码
            支持 Auth 2.0 认证，传递 str，字符串
            支持 自定义或者其他认证，传递 dict，两个key： key 和 value
        :param cookies:
        :param headers: 请求头
        :param files:  请求文件
        :param is_json_content: 是否是 JSON 格式的内容
        :return:
        """

        # self.info("[%s] - 在 BaseApi 类中发送请求，使用的数据：uri=%s, method=%s, data_dict=%r, auth=%r"
        #           % (__name__, url, method, data_dict, auth))

        if self.request is not None and isinstance(self.request, Request):
            self.request.request(
                url=url,
                method=method,
                data_dict=data_dict,
                auth=auth,
                cookies=cookies,
                headers=headers,
                files=files,
                is_json_content=is_json_content
            )

    def _get_resp(self, resp_dict: dict = None):
        """
        获取响应
        :param resp_dict:
        :return:
        """
        http_resp = self._parse_http_resp()
        req_data = self._get_http_req()

        resp_data = Dict.merge_dict(first_dict=req_data, second_dict=http_resp)
        if resp_dict is not None and isinstance(resp_dict, dict):
            new_resp_data = Dict.merge_dict(first_dict=resp_dict, second_dict=resp_data)
        else:
            new_resp_data = dict(resp_dict=self.json_dict)

        return Dict.merge_dict(first_dict=new_resp_data, second_dict=resp_data)

    def _get_http_req(self):
        """
        分析 http 的请求
        :return:
        """
        if self.request is not None and isinstance(self.request, Request):
            return dict(
                req_data=self.request.data,
                req_param=self.request.param,
                req_headers=self.request.headers,
                req_cookies=self.request.cookies,
            )

    def _parse_http_resp(self):
        """
        分析 http 的响应
        :return: 返回 dict
            status_code
            response_headers
            full_response
            json_dict
        """
        resp = {}
        if self.request is not None and isinstance(self.request, Request):
            resp["status_code"] = self.request.status_code
            resp["cookies"] = self.request.cookies
            resp["response_dict"] = self.request.response_dict

        return resp

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

    """ 需要子类重写的方法，实体类基础操作 """

    @allure_step
    def create(self, data: Data):
        """
        创建实体
        :param data:
        :return:
        """
        raise TypeError("需要子类重写的方法，实体类基础操作，请在子类中重写 create() 方法")

    @allure_step
    def update(self, data: Data):
        """
        更新实体
        :param data:
        :return:
        """
        raise TypeError("需要子类重写的方法，实体类基础操作，请在子类中重写 update() 方法")

    @allure_step
    def view(self, data: Data):
        """
        查看实体
        :param data:
        :return:
        """
        raise TypeError("需要子类重写的方法，实体类基础操作，请在子类中重写 view() 方法")

    @allure_step
    def query(self, data: Data):
        """
        查询实体
        :param data:
        :return:
        """
        raise TypeError("需要子类重写的方法，实体类基础操作，请在子类中重写 query() 方法")

    @allure_step
    def check(self, data: Data):
        """
        创建实体
        :param data:
        :return:
        """
        raise TypeError("需要子类重写的方法，实体类基础操作，请在子类中重写 check() 方法")

    @allure_step
    def delete(self, data: Data):
        """
        删除实体
        :param data:
        :return:
        """
        raise TypeError("需要子类重写的方法，实体类基础操作，请在子类中重写 delete() 方法")

    @allure_step
    def create_delete(self, data: Data):
        """
        创建实体然后删除实体
        :param data:
        :return:
        """
        raise TypeError("需要子类重写的方法，实体类基础操作，请在子类中重写 create_delete() 方法")

    @allure_step
    def query_view(self, data: Data):
        """
        查询实体列表，然后查看每一个实体
        :param data:
        :return:
        """
        raise TypeError("需要子类重写的方法，实体类基础操作，请在子类中重写 query_view() 方法")

    @allure_step(title="接口请求抓包")
    def capture(self, title: str, content_dict: dict = None):
        """
        抓包 HTTP/HTTPS 请求和响应，并且记录在 allure 报告中
        :param title : 标题
        :param content_dict : 截图内容
        :return: None
        """

        if content_dict is not None and isinstance(content_dict, dict):
            snapshot_json = Dict.dump_json(dict_to_dump=content_dict)
            allure.attach(snapshot_json, name="json_%s" % title, attachment_type=allure.attachment_type.JSON)

            self.info("[%s] - 系统进行抓包，snapshot title：json_%s " % (__name__, title))

    """ 实体类的属性 """

    @property
    def request(self):
        """
        get current request
        :return:
        """
        return self.__request

    @property
    def response(self):
        """
        get current response
        :return:
        """
        if self.request and isinstance(self.request, Request):
            return self.request.response_dict

        return None

    @property
    def logger(self):
        """
        日志对象，给业务使用，让他使用这个对象写日志，把他做的事情记录在里面
        :return:
        """
        return self.__logger

    @property
    def json_dict(self):
        """
        当前业务API 的json 字典
        :return:  dict
        """
        if self.request and isinstance(self.request, Request):
            return self.request.json_dict

        return None
