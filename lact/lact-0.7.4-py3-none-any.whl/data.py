from typing import Dict


class Data(Dict):
    """
    Desc: Data Model
    Date: 20200605
    Author: Linty Liu (Tingli)
    Email: liu.tingli@outlook.com
    """

    __param_dict = {}
    __auth_dict = {}
    __header_dict = {}
    __cookie_dict = {}
    __expected_dict = {}
    __extra_dict = {}
    __assertion_dict = {}
    __resp_dict = {}

    def __init__(self, param: dict, auth: dict, header: dict, cookie: dict, expected: dict, extra: dict,
                 assertion: dict):
        """
        构造方法
        :param param:
        :param auth:
        :param header:
        :param cookie:
        :param assertion:
        :param extra:
        :param assertion:
        """
        super().__init__()
        self.__param_dict = param
        self.__auth_dict = auth
        self.__header_dict = header
        self.__cookie_dict = cookie
        self.__expected_dict = expected
        self.__extra_dict = extra
        self.__assertion_dict = assertion
        self.update(dict(
            param=param,
            auth=auth,
            header=header,
            cookie=cookie
        ))

    @property
    def param_dict(self) -> dict:
        """
        参数数据字典
        :return:
        """
        return self.__param_dict

    @param_dict.setter
    def param_dict(self, param):
        """
        参数数据字典
        :return:
        """
        if param is not None and isinstance(param, dict):
            self.__param_dict = param
            self.update(dict(param=param))

    @property
    def auth_dict(self) -> dict:
        """
        鉴权数据字典
        :return:
        """
        return self.__auth_dict

    @auth_dict.setter
    def auth_dict(self, auth):
        """
        鉴权数据字典
        :return:
        """
        if auth is not None and isinstance(auth, dict):
            self.__auth_dict = auth
            self.update(dict(auth=auth))

    @property
    def header_dict(self) -> dict:
        """
        请求头部数据字典
        :return:
        """
        return self.__header_dict

    @header_dict.setter
    def header_dict(self, header):
        """
        请求头部数据字典
        :return:
        """
        if header is not None and isinstance(header, dict):
            self.__header_dict = header
            self.update(dict(header=header))

    @property
    def cookie_dict(self) -> dict:
        """
        Cookie 数据字典
        :return:
        """
        return self.__cookie_dict

    @cookie_dict.setter
    def cookie_dict(self, cookie):
        """
        Cookie 数据字典
        :return:
        """
        if cookie is not None and isinstance(cookie, dict):
            self.__cookie_dict = cookie
            self.update(dict(cookie=cookie))

    @property
    def expected_dict(self) -> dict:
        """
        断言数据字典
        :return:
        """
        return self.__expected_dict

    @expected_dict.setter
    def expected_dict(self, expected):
        """
        断言数据字典
        :return:
        """
        if expected is not None and isinstance(expected, dict):
            self.__expected_dict = expected

    @property
    def extra_dict(self) -> dict:
        """
        额外数据字典
        :return:
        """
        return self.__extra_dict

    @extra_dict.setter
    def extra_dict(self, extra):
        """
        额外数据字典
        :return:
        """
        if extra is not None and isinstance(extra, dict):
            self.__extra_dict = extra

    @property
    def assertion_dict(self) -> dict:
        """
        额外数据字典
        :return:
        """
        return self.__assertion_dict

    @assertion_dict.setter
    def assertion_dict(self, assertion):
        """
        额外数据字典
        :return:
        """
        if assertion is not None and isinstance(assertion, dict):
            self.__assertion_dict = assertion

    @property
    def resp_dict(self) -> dict:
        """
        响应数据字典
        :return:
        """
        return self.__resp_dict

    @resp_dict.setter
    def resp_dict(self, resp):
        """
        额外数据字典
        :return:
        """
        if resp is not None and isinstance(resp, dict):
            self.__resp_dict = resp


def build_data(param_dict: dict, auth_dict: dict, cookie_dict: dict, header_dict: dict, expected_dict: dict,
               extra_dict: dict, assertion_script: dict) -> Data:
    """
    构建 数据对象
    :param assertion_script:
    :param expected_dict:
    :param param_dict:
    :param auth_dict:
    :param cookie_dict:
    :param header_dict:
    :param extra_dict:
    :return:
    """
    return Data(
        param=param_dict,
        auth=auth_dict,
        cookie=cookie_dict,
        header=header_dict,
        expected=expected_dict,
        extra=extra_dict,
        assertion=assertion_script
    )
