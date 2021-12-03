from os import environ
import requests


class Client:
    datetime = None
    _step = 0
    paused = False
    stopped = False

    def __init__(self, request_host=None, api_endpoint=None, api_key=None):

        if api_endpoint is None:
            if request_host:
                api_endpoint = request_host + 'api/v1'
            else:
                api_endpoint = 'https://www.openagua.org/api/v1'

        # set up api
        self.api_key = api_key or environ.get('OA_SECRET_KEY')
        self.api_endpoint = api_endpoint
        self.api_headers = {'X-API-KEY': self.api_key}

    def __getattr__(self, name):
        def method(*args, **kwargs):
            if name[:4] == 'add_':
                return self.add(name[4:] + 's', **kwargs)
            elif name[:4] == 'get_':
                return self.get(name[4:] + 's', *args, **kwargs)
            elif name[:7] == 'update_':
                return self.update(name[7:] + 's', *args, **kwargs)
            else:
                return getattr(self, name)(*args, **kwargs)

        return method

    def get(self, resource, *args, **kwargs):
        resource_id = args[0]
        url = '{}/{}/{}'.format(self.api_endpoint, resource, resource_id)
        resp = requests.get(url, headers=self.api_headers, params=kwargs)
        return self.prepare_response(resp)

    def add(self, resource, **kwargs):
        url = '{}/{}'.format(self.api_endpoint, resource)
        resp = requests.post(url, headers=self.api_headers, json=kwargs)
        return self.prepare_response(resp)

    def update(self, resource, *args, **kwargs):
        resource_id = args[0]
        url = '{}/{}/{}'.format(self.api_endpoint, resource, resource_id)
        resp = requests.get(url, headers=self.api_headers, params=kwargs)
        return self.prepare_response(resp)

    @staticmethod
    def prepare_response(resp):
        if resp.status_code == 200:
            return resp.json()
        else:
            return {'status_code': resp.status_code}
