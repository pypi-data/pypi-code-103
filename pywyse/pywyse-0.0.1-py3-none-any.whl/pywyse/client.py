import os 

import requests 
from . import __conf

conf = __conf

class Client: 
    def __init__(self, conf=conf, *args, **kwargs): 
        self.conf = conf
        
    def base_url(self, endpoint=''): 
        url = f"https://{self.conf['cw_server']}/{self.conf['cw_codebase']}/apis/{self.conf['cw_apiversion']}"
        url = url + endpoint 
        return url 
    
    def headers(self, **kwargs):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.conf['auth'],
            'clientId': self.conf['cw_clientid'], 
            **kwargs
        } 
        return headers 

    def cw_get(self, endpoint='', verbose=False, **kwargs): 
        endpoint = self.base_url(endpoint=endpoint)
        headers = kwargs.pop('headers', {})
        headers = self.headers(**headers)
        if verbose:
            print(kwargs)
            print(endpoint)
            print(headers)
            
        return requests.get(endpoint, headers=headers, params=kwargs)
        
    def cw_patch(self, endpoint='', verbose=False, **kwargs): 
        endpoint = self.base_url(endpoint=endpoint)
        headers = kwargs.pop('headers', {})
        headers = self.headers(**headers)
        body = kwargs.pop('body', {})
        if verbose:
            print(endpoint)
            print(body)
            print(headers)
        
        return requests.patch(endpoint, headers=headers, json=body)
        
    def cw_put(self, endpoint='', verbose=False, **kwargs): 
        endpoint = self.base_url(endpoint=endpoint)
        headers = kwargs.pop('headers', {})
        headers = self.headers(**headers)
        if verbose:
            print(kwargs)
            print(endpoint)
            print(headers)
        
        return requests.put(endpoint, headers=headers, json=kwargs)
        
    def cw_post(self, endpoint='', verbose=False, body={}, **kwargs): 
        endpoint = self.base_url(endpoint=endpoint)
        headers = kwargs.pop('headers', {})
        headers = self.headers(**headers)
        if verbose:
            print(kwargs)
            print(endpoint)
            print(headers)
            
        return requests.post(endpoint, headers=headers, json=body)
        
    def cw_delete(self, endpoint='', verbose=False, **kwargs): 
        endpoint = self.base_url(endpoint=endpoint)
        headers = kwargs.pop('headers', {})
        headers = self.headers(**headers)
        if verbose:
            print(kwargs)
            print(endpoint)
            print(headers)
            
        return requests.delete(endpoint, headers=headers, **kwargs)

    @staticmethod 
    def build_url(*args):
        return '/'.join(args) 
        

