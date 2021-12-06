# Encapsulation of requests library

import json
import os
import re
from enum import Enum
from urllib.parse import urlencode, quote, urlparse

from PIL import Image
from bs4 import BeautifulSoup, Tag
from pytesseract import pytesseract
from requests import Session, Response
from requests.auth import HTTPBasicAuth
from requests.utils import dict_from_cookiejar
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

disable_warnings(InsecureRequestWarning)

_CHARACTER_COMMA = ","
_CHARACTER_COLON = ":"
_WAIT_SECONDS = 5
_DEFAULT_ENCODING_UTF8 = "utf-8"
_SUPPORT_METHOD_LIST = ["GET", "POST", "HEAD", "PUT", "DELETE", "POST_URL", "DELETE_URL"]
_DEFAULT_HTML_PARSER = "lxml"
__SUPPORT_SCHEMA_LIST = ["HTTPS", "HTTP"]


class Request(object):
    """
    Desc: Encapsulation of requests library
    Date: 20191127
    Author: Linty Liu (Tingli)
    Email: liu.tingli@outlook.com
    """

    __schema = None
    __host = None
    __port = None
    __headers = None
    __auth = None
    __cookies = None
    __data = None
    __param = None
    __response = None
    __session = None
    __gateway = None
    __middle = None

    class Protocol(Enum):
        """
        请求类型
        """
        HTTP = 1,
        HTTPS = 2

    """
    构造方法
    """

    def __init__(self, schema: Protocol, host: str, port: int = None, gateway: dict = None, middle: str = None):
        """
        构造方法
        :param schema: 请求协议，Protocol 类
        :param host: 主机，支持 主机名称，IP，域名 等
        :param port: 默认为 None，整型
        :param gateway: 默认为 None，dict，网关 URL path
        :param middle: 默认为 None，字符串，网管 与主机之间的部分
        """
        disable_warnings(InsecureRequestWarning)

        self.__schema = schema
        self.__host = host
        self.__port = port
        self.__gateway = gateway
        self.__middle = middle
        self.__headers = {}
        self.__cookies = {}
        self.__data = {}
        self.__param = {}
        self.__session = Session()

    """
    成员方法
    """

    def send(self, uri: str, method: str,
             data_dict=None, is_json_content: bool = False,
             headers=None, cookies=None, auth=None, files=None, gateway_enable=True
             ):
        """
        发送请求
        :param gateway_enable: 开启网关
        :param files:
        :param uri:
        :param method:
        :param data_dict:
        :param is_json_content:
        :param headers:
        :param cookies:
        :param auth:
        :return:
        """

        if data_dict is None:
            data_dict = {}
        url = self._pre_url(uri=uri, gateway_enable=gateway_enable)

        if auth:
            self._pre_auth(auth)

        method = self._pre_request(cookies, headers, method)

        self._request(method=method, url=url, data_dict=data_dict,
                      is_json_content=is_json_content, files=files)

    def request(self, url: str, method: str,
                data_dict=None, is_json_content: bool = False,
                headers=None, cookies=None, auth=None, files=None):
        """
        直接请求 URL
        :param url:
        :param method:
        :param data_dict:
        :param is_json_content:
        :param headers:
        :param cookies:
        :param auth:
        :param files:
        :return:
        """

        if data_dict is None:
            data_dict = {}
        if auth:
            self._pre_auth(auth)
        method = self._pre_request(cookies, headers, method)

        self._request(method=method, url=url, data_dict=data_dict,
                      is_json_content=is_json_content, files=files)

    def clear_cookies(self):
        """
        清除当前请求的 Cookies 对象
        :return:
        """
        self._get_session().cookies.clear()
        self.__cookies.clear()

    def close(self):
        """
        关闭请求，释放请求资源
        :return:
        """
        self.__schema = None
        self.__host = None
        self.__port = None
        self.__auth = None
        self.__cookies = None
        self.__response = None
        self.__gateway = None
        self._close_session()

    def get_soup_elements(self, selector, url=None) -> list:
        """
        通过 beautiful soup 获取多个元素
        :param selector: 一组元素的选择器
        :param url:
        :return:
        """

        if url is not None:
            self.request(url=url, method="get")

        soup = BeautifulSoup(self.__response.text, _DEFAULT_HTML_PARSER)
        tags = soup.select(selector=selector)
        elements = []
        if tags is not None and isinstance(tags, list):
            for tag in tags:
                if isinstance(tag, Tag):
                    elements.append(tag.attrs)

        return elements

    def get_soup_element(self, selector, url=None) -> dict:
        """
        通过 beautiful soup 获取单个元素
        :param selector: 一个元素的选择器
        :param url:
        :return:
        """

        if url is not None:
            self.request(url=url, method="get")

        soup = BeautifulSoup(self.__response.text, _DEFAULT_HTML_PARSER)
        tag = soup.select(selector=selector)[0]
        element = {}

        if isinstance(tag, Tag):
            element.update(tag.attrs)

        return element

    def recognize_verify_code_by_grey_process(self, img_src: str, code_length=0):
        """
        识别普通验证码
        :param code_length:
        :param img_src: 图片 URL
        :return:
        """
        temp_element_snapshot_filename = "temp_element_snapshot.png"

        self._request(url=img_src, method="get", data_dict={}, is_json_content=True)

        with open(file=temp_element_snapshot_filename, mode="wb") as f:
            f.write(self.__response.content)

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

    def _pre_request(self, cookies, headers, method):
        """
        准备 request
        :param cookies:
        :param headers:
        :param method:
        :return:
        """
        if method is not None and method.upper().strip() in _SUPPORT_METHOD_LIST:
            method = method.upper().strip()
        else:
            raise TypeError(
                "请传递一个合法的 HTTP 请求方法, 当前使用的 method = %r"
                % method
            )
        if headers is not None and isinstance(headers, dict):
            self.__headers.update(headers)
        if cookies is not None and isinstance(cookies, dict):
            self.__cookies.update(cookies)
        return method

    """
    property
    """

    @property
    def json_dict(self):
        """
        数据字典
        :return:
        """

        return self._load_json()

    @property
    def json_format_string(self):
        """
        数据字典
        :return:
        """

        return self._dump_json()

    @property
    def status_code(self):
        """
        状态码
        :return:
        """
        if self.__response is not None and isinstance(self.__response, Response):
            status_code = self.__response.status_code
            if status_code is not None and str(status_code) != "":
                return int(str(status_code))

        return None

    @property
    def cookies(self):
        """
        Cookies
        :return:
        """
        if self.__session is not None and isinstance(self.__session, Session):
            return dict_from_cookiejar(self._get_session().cookies)

        return None

    @property
    def data(self):
        """
        请求正文
        :return:
        """
        return self.__data

    @property
    def param(self):
        """
        请求参数
        :return:
        """
        return self.__param

    @property
    def response_dict(self):
        """
        响应字典
        :return:
        """
        if self.__response is not None and isinstance(self.__response, Response):
            return dict(
                url=self.__response.url,
                status_code=self.__response.status_code,
                elapsed="%f毫秒" % round(self.__response.elapsed.microseconds / 1000.0, ndigits=2),
                cookies=dict(self.__response.cookies),
                headers=dict(self.__response.headers),
                reason=self.__response.reason,
                ok=self.__response.ok
            )

        return None

    @property
    def response_url(self):
        """
        响应的 URL
        :return:
        """
        if self.__response is not None and isinstance(self.__response, Response):
            return self.__response.url

        return None

    @property
    def gateway(self):
        """
        数据字典
        :return:
        """

        return self.__gateway

    @property
    def headers(self):
        """
        请求头
        :return:
        """
        return self.__headers

    """
    私有方法
    """

    def _pre_url(self, uri, gateway_enable):
        """
        请求前置操作
        :param uri:
        :param gateway_enable:
        :return:
        """

        url = None

        if self.__schema == self.Protocol.HTTP:
            url = "http://"
        elif self.__schema == self.Protocol.HTTPS:
            url = "https://"

        if self.__host.endswith("/"):
            self.__host = self.__host[0:len(self.__host) - 1]

        if uri is not None and isinstance(uri, str):
            if not uri.startswith("/"):
                uri = "/%s" % uri

        if isinstance(self.__gateway, dict):
            gateway_path = self.__gateway.get("path")
            gateway_exclude_list = self.__gateway.get("exclude")
            for exclude in gateway_exclude_list:
                if exclude in uri:
                    gateway_enable = False
                    break

            if isinstance(gateway_path, str) and gateway_path != "":
                if not gateway_path.startswith("/"):
                    gateway_path = "/%s" % gateway_path

                if gateway_path.endswith("/"):
                    gateway_path = gateway_path[0:len(gateway_path) - 1]

                self.__gateway["path"] = gateway_path

        else:
            self.__gateway = dict(path="")

        if gateway_enable:
            new_uri = self.__gateway.get("path") + uri
        else:
            new_uri = uri

        if self.__middle is not None and isinstance(self.__middle, str) and self.__middle != "":
            middle = self.__middle
            if not middle.startswith("/"):
                middle = "/%s" % middle

            if middle.endswith("/"):
                middle = middle[0:len(middle) - 1]
            new_uri = "%s%s" % (middle, new_uri)

        if self.__port:
            # 如果 协议与默认端口好匹配，则不显示端口号
            if not (self.__schema == self.Protocol.HTTP and str(self.__port) == "80") and not (
                    self.__schema == self.Protocol.HTTPS and str(self.__port) == "443"):
                url = "%s%s:%d%s" % (url, self.__host, self.__port, new_uri)
            else:
                url = url + self.__host + new_uri

        else:
            url = url + self.__host + new_uri
        return url

    def _pre_auth(self, auth):
        """
        处理认证鉴权
        :param auth:
        :return:
        """
        if isinstance(auth, tuple) and len(auth) == 2:
            # special-case basic HTTP auth
            self.__auth = HTTPBasicAuth(*auth)
        elif isinstance(auth, dict):
            auth_headers = {auth["key"]: auth["value"]}
            self.__headers.update(auth_headers)
        elif isinstance(auth, str):
            auth_headers = dict(Authorization=auth)
            self.__headers.update(auth_headers)

    def _request(self, url: str, method: str, data_dict: dict, is_json_content: bool, files=None):
        """
        具体发送请求
        :param url:
        :param method:
        :param data_dict:
        :param is_json_content:
        :param files:
        :return:
        """
        params = jsons = data = None
        if method.lower() in ("get", "head", "post_url", "delete_url"):
            self.__param = params = data_dict
            method = method.lower().replace("_url", "")
            self.__data = jsons = data = None

        elif method.lower() in ("post", "put", "delete"):
            if is_json_content:
                self.__data = jsons = data_dict
            else:
                self.__data = data = data_dict
            self.__param = params = None

        self.__response = self._get_session().request(
            method=method.upper(),
            url=url,
            headers=self.__headers,
            cookies=self.__cookies,
            auth=self.__auth,
            data=data,
            params=params,
            json=jsons,
            files=files,
            verify=False
        )

    def _dump_json(self):
        """
        字典 dict 转为 json
        :return:
        """
        json_string = json.dumps(self._load_json(),
                                 indent=4,
                                 separators=(_CHARACTER_COMMA, _CHARACTER_COLON))
        if json_string is not None and isinstance(json_string, str):
            return json_string.encode('utf-8').decode('unicode_escape')

        return json_string

    def _load_json(self):
        """

        :return:
        """
        r = self.__response
        res_json = None
        if r is not None and isinstance(r, Response) and r.text.startswith("{"):
            try:
                res_json = r.json()

            except Exception as e:
                # if r.text and r.text.startswith("{"):
                #     res_json = json.loads(r.text)
                print("Response 对象调用 json() 发生异常，请抓包 HTTP 来查看原因: %r" % e)

        return res_json

    def _get_session(self) -> Session:
        """
        获取 session 对象
        :return:
        """
        if self.__session is not None and isinstance(self.__session, Session):
            return self.__session
        return Session()

    def _close_session(self):
        """
        关闭 Session
        :return:
        """
        if self.__session is not None and isinstance(self.__session, Session):
            self.__session.close()


def build_request(
        schema: str,
        host: str,
        port: int = None,
        middle: str = None,
        gateway: dict = None):
    """
    get request for web api testing
    :param middle: 主机与网管之间的地址
    :param gateway: 网关
    :param schema: 协议
    :param port: 主机端口号
    :param host: API 网址的 主机部分
    :return: HttpRequest
    """

    if schema is not None and schema.upper().strip() in __SUPPORT_SCHEMA_LIST:
        if schema.upper().strip() == "HTTP":
            schema = Request.Protocol.HTTP
        elif schema.upper().strip() == "HTTPS":
            schema = Request.Protocol.HTTPS
        else:
            raise TypeError(
                "请传递一个合法的请求协议, 当前使用的 schema = %r"
                % schema
            )

    return Request(schema=schema, host=host, port=port, gateway=gateway, middle=middle)


def encode_url(url: str, params: dict):
    """
    对 URL 进行编码
    :param url:
    :param params:
    :return:
    """
    return url, urlencode(params)


def encode_headers(header_value: str):
    """
    对请求头进行 编码
    @param header_value:
    @return:
    """
    if header_value is None:
        header_value = ""
    return quote(header_value.encode('utf-8'))


def parse_url(url: str):
    """
    解析 URL
    @param url:
    @return:
    """
    return urlparse(url)


def remove_url_param(url: str):
    """
    移除 URL 的参数，片段等
    :param url:
    :return:
    """
    if url is not None:
        index = url.index("?")
        if index >= 0:
            return url[:index]
