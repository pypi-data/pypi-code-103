# -*- coding: UTF-8 -*-
import json
from functools import partial
import requests
import pickle

class DataApi:
    """
    Database Api for client in SAIF network.
    To initialize api, execute DataApi with str:username, str:password
    e.g. api = DataApi(username='xxx', password='xxx')

    When user correctly authorized, api is ready for query for products.
    With api.product(**kwargs), api return pandas.DataFrame, and more types of output in future.
    
    product names:
        stock_daily
        index_daily
        future_daily
        future_option_daily
        index_option_daily
        shibor_daily
        stock_data
        index_data
        future_data
        index_option_data
        future_option_data
        future_lv1
        future_option_lv1
        index_option_lv1
        stock_lv2_lob
        stock_lv2_trade
        ...

    Check documents site for more details.
    Check simple help on input parameters with:
        api.help('product')
    """

    # server address
    __SERVER = 'http://172.16.210.32:8091'      
    __token = ''

    def __init__(self, username='', password=''):
        """
        Initialize API with username and password.
        e.g. api = DataApi(username='xxx', password='xxx')
        """
        data = {'username':username, 'password':password}
        try:
            res = requests.post(url=self.__SERVER+'/token', data=data)
            if res.status_code == 200:
                token = json.loads(res.text)
                self.__token = token['access_token']
                print('User authorized, Api ready.')
                print('Check document pages: {site} for more details.'.format(site=self.__SERVER))
            else:
                print("User not authorized. Incorrect username or password.")
                print("Execute DataApi(username='your username' , password='your password') to access API.")
        except:
            print('Authorization unable to connect server.')

    def query(self, qry_func, **kwargs):
        """
        Query functions based on products and types. Check documents site for more details.
        """
        headers = {'Authorization':'Bearer {0}'.format(self.__token)}
        url = self.__SERVER + '/query/' + qry_func

        try:
            res = requests.post(url=url, json=kwargs, headers=headers)
        except:
            print('Query unable to connect server, or parameters incorrect.')
            return

        if res.status_code == 200:
            df = pickle.loads(res.content)
            return df
        elif res.status_code == 422:
            msg = json.loads(res.text)['detail'][0]
            print('Parameter error:', msg['loc'][1])
            print(msg['msg'])
        else:
            print(json.loads(res.text)['detail'])

    def help(self, qry_func:str):
        """
        Simple help based on products and types. Check documents site for more details.
        e.g. api.help('stock_data')
        """
        headers = {'Authorization':'Bearer {0}'.format(self.__token)}
        url = self.__SERVER + '/help/' + str(qry_func)

        try:
            res = requests.post(url=url, headers=headers)
        except:
            print('Query unable to connect server, or parameters incorrect.')

        if res.status_code == 200:
            print(eval(res.text))
        else:
            print(json.loads(res.text)['detail'])
            
    def __getattr__(self, qry_func):
        return partial(self.query, qry_func)
