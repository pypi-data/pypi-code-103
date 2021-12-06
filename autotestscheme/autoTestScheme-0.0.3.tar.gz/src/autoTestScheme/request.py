import os
import sys
import allure
import copy
import time

import requests

from urllib.parse import urlencode

from .common import config
from . import logger


class requestBase(object):


    def __init__(self):
        self.setup_hook_list = []
        self.teardown_hook_list = []
        self.logger = logger
        self.api_data = {}

    def initialization(self, base_url=None, http='https', client=None, catch_response=False):
        self.base_url = base_url
        self.http = http
        if client is not None:
            self.session = client
        else:
            self.session = requests.Session()
        self.subdomain = None
        self.http = http
        self.catch_response = catch_response

    def read_api_folder(self, *folder_name):
        if isinstance(folder_name, tuple) is False:
            folder_name = (folder_name,)
        folder = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), *folder_name)
        for root, dirs, files in os.walk(folder):
            for name in files:
                _path = os.path.join(root, name)
                if name.endswith('.json') is True:
                    _data = config.Json(_path).get_object()
                    if _data.get('id') is not None:
                        self.register_api(_data)

    def register_api(self, _data):
        _id = _data.get('id')
        if _id in list(self.api_data.keys()):
            self.logger.error("api({})重复注册".format(_id))
        self.api_data[_id] = _data

    def get_api(self, api_id):
        if api_id in list(self.api_data.keys()):
            return self.api_data[api_id]
        assert False, "api({})未注册".format(api_id)

    def register_setup_hook(self, hook):
        self.setup_hook_list.append(hook)

    def register_teardown_hook(self, hook):
        self.teardown_hook_list.append(hook)

    def get_url(self, path):
        '''
            获取网址
        '''
        if self.subdomain is None:
            base_url = self.base_url
        else:
            base_url = self.subdomain + '.' + self.base_url
        url = '{}://{}{}'.format(self.http, base_url, path)
        return url

    def execute(self, request):
        """
            request 请求类
        """
        for hook in self.setup_hook_list:
            hook(request)
        title = request.get('title') if request.get('title') is not None else request.get('path')
        method = request.get('method')
        _json = request.get('json')
        data = request.get('data')
        headers = request.get('headers')
        params = request.get('params')
        path = request.get('path')
        with allure.step(title):
            self.logger.debug('发送请求：{}'.format(title))
            response = self._excute(method, path, data, _json, headers, params, title)
            for hook in self.teardown_hook_list:
                hook(request)
            return response

    def _excute(self, method, path, data=None, _json=None, headers=None, params=None, name=None):
        current_time = time.time()
        url = self.get_url(path)
        request_dict = {}
        request_dict['method'] = method
        request_dict['url'] = url
        request_dict['params'] = params
        request_dict['data'] = data
        request_dict['headers'] = headers
        request_dict['verify'] = False
        request_dict['json'] = _json
        if self.catch_response is True:
            del request_dict['url']
            del request_dict['params']
            request_dict['path'] = url + '?' + urlencode(params)
            request_dict['catch_response'] = True
            request_dict['name'] = name
        result = self.session.request(**request_dict)
        new_params = copy.deepcopy(params)
        response = result.text.replace('\n', '').replace('\r', '').replace('  ', '')
        self.logger.debug('请求参数：method：{}，url：{}, \nparams:{}, headers:{}, \ndata:{}, json:{},'
                          '\n返回：{},时间:{}'.format(method, url, new_params, headers, data, _json, response,
                                                 time.time() - current_time))
        if self.catch_response is True:
            return result
        return result

    def qs_parse(self, data):
        for key in list(data.keys()):
            value = data[key]
            if type(value) == dict:
                del data[key]
                for _key in list(value.keys()):
                    data[key + '[' + _key + ']'] = value[_key]
            elif type(value) == list:
                del data[key]
                for _key in range(len(value)):
                    data[key + '[' + str(_key) + ']'] = value[_key]
