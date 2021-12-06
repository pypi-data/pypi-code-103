import os
import requests
from urllib.parse import urljoin
from notebook.base.handlers import APIHandler

FILE_NAME = 'Notebook.ipynb'


class API_ERROR(Exception):

    def __init__(self, code, msg) -> None:
        self.code = code
        self.msg = msg


class BackendAPIHandler(APIHandler):
    """包含后端请求API的Handler
    """

    def __init__(self, application, request) -> None:
        super().__init__(application, request)
        self.backend_url = os.environ.get('PI_BACKEND_DOMAIN', None)
        self.access_token = os.environ.get('PI_ACCESS_TOKEN', None)
        assert self.backend_url, '未设置 env "PI_BACKEND_DOMAIN"'
        assert self.access_token, '未设置 env "PI_ACCESS_TOKEN"'
        self.headers = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'User-Agent': 'Jupyter'
        }

    def api_request(self, method, url, json_data=None, query_params=None):
        url = urljoin(self.backend_url, url)
        method = method.upper()
        self.log.info('API请求: {} {}'.format(method, url))
        if method == 'GET':
            res = requests.get(url, params=query_params, headers=self.headers)
        elif method == 'PUT':
            res = requests.put(url, json=json_data, headers=self.headers)
        elif method == 'POST':
            res = requests.post(url, json=json_data, headers=self.headers)
        elif method == 'DELETE':
            res = requests.delete(url, json=json_data,
                                  params=query_params, headers=self.headers)
        if res.status_code == 200 and res.json()['code'] == 'succeed':
            data = res.json()
            self.log.info('响应成功: {}'.format(data))
            return data
        else:
            try:
                data = res.json()
            except Exception:
                msg = '请求响应异常, 请稍后再试'
                self.log.warn('响应失败: [{}] {}'.format(res.status_code, res))
            else:
                msg = data['message']
                self.log.warn('响应失败: [{}] {}'.format(res.status_code, data))
            raise API_ERROR(code=res.status_code, msg=msg)
