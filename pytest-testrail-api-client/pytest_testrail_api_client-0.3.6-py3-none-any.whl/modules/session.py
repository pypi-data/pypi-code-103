import base64
import configparser
import json
import os
from itertools import chain

import requests

from pytest_testrail_api_client.service import get_worker_id


class Session:

    def __init__(self, host: str = None, username: str = None, token: str = None, env_policy: str = 'clear'):
        """
        https://docs.saucelabs.com/dev/api/

        Insert your api server
        :param host:
        :param username: your username
        :param token: tour API token
        :param env_policy: str
        """
        self.__host: str
        self._result_cache = os.path.join(os.path.dirname(__file__), 'results.json')
        self._session = requests.Session()
        self.project_id = 20
        self.__get_auth(host, username, token, env_policy)
        del host, username, token
        if self.__host[-1] == '/':
            self.__host = self.__host[:-1]
        self.__host = f'{self.__host}/index.php?'
        self.result_url = f'{self.__host}/tests/view'

    def request(self, method: str, url: str, data: dict = None, params: dict = None,
                return_type: str = False, **kwargs):
        data = json.dumps(data) if data else ''
        if 'download' in url or 'upload' in url:
            self._session.headers.pop('Content-Type', None)
        else:
            self._session.headers.update({'Content-Type': 'application/json'})
        response = self._session.request(method=method, url=f'{self.__host}{url}', data=data, params=params, **kwargs)
        if response.status_code in (200, 201):
            if return_type == 'text':
                return response.text
            elif return_type == 'content':
                return response.content
            elif return_type == 'status_code':
                return response.status_code
            else:
                return_dict = response.json()
                if 'limit' in return_dict:
                    size = return_dict['size']
                    main_name = tuple(key for key in return_dict if key not in ('offset', 'limit', 'size', '_links'))[0]
                    if size < 250:
                        return return_dict[main_name]
                    else:
                        if params is None:
                            params = dict()
                        result, offset = [], 250
                        result.append(return_dict[main_name])
                        while True:
                            params.update({'limit': 250, 'offset': offset})
                            resp = self._session.request(method=method, url=f'{self.__host}{url}', data=data,
                                                         params=params, **kwargs).json()
                            result.append(resp[main_name])
                            offset += 250
                            if resp['size'] < 250:
                                return list(chain.from_iterable(result))
                else:
                    return response.json()
        else:
            return f'Error: {response.status_code}: {response.reason} ({response.text})'

    def __get_auth(self, host: str = None, username: str = None, token: str = None, env_policy: str = None):

        if all((host, username, token)):
            self._session.auth, self.__host = Auth(username, token), host
            return
        else:
            env_username, env_token = os.environ.get('TESTRAIL_EMAIL', None), os.environ.get('TESTRAIL_KEY', None)
            env_host = os.environ.get('TESTRAIL_URL', None)
            if all((env_username, env_token, env_host)):
                self._session.auth = Auth(env_username, env_token)
                self.__host = env_host
                # if env_policy == 'clear':
                #     tuple(map(os.environ.pop, ('TESTRAIL_EMAIL', 'TESTRAIL_KEY', 'TESTRAIL_URL')))
                return

            path, config = os.path.dirname(__file__), configparser.ConfigParser()
            for _ in range(9):
                for file in ('pytest', 'test_rail'):
                    file_name = os.path.join(path, f'{file}.ini')
                    if os.path.isfile(file_name):
                        config.read(file_name)
                        if config.has_section('pytest'):
                            options = config.options('pytest')
                            if all((option in options for option in
                                    ('testrail-email', 'testrail-key', 'testrail-url'))):
                                test_rail = config['pytest']
                                self._session.auth = Auth(test_rail['testrail-email'], test_rail['testrail-key'])
                                self.__host = test_rail['testrail-url']
                                return
                path = os.path.dirname(path)
        self.__host = '/'
        self._session.auth = Auth('', '')

    @staticmethod
    def get_results_file(session):
        return os.path.join(os.path.dirname(__file__), 'results', f'results_{get_worker_id(session)}.json')

    @staticmethod
    def get_results_files():
        root_folder = os.path.join(os.path.dirname(__file__), 'results')
        return tuple(os.path.join(root_folder, file) for file in os.listdir(root_folder)
                     if file.split('.')[-1] == 'json')


class Auth:
    def __init__(self, username, password):
        self.data = base64.b64encode(b':'.join((username.encode('ascii'),
                                                password.encode('ascii')))).strip().decode('ascii')

    def __call__(self, r):
        r.headers['Authorization'] = f'Basic {self.data}'
        return r

    def __del__(self):
        return 'BasicAuth'
