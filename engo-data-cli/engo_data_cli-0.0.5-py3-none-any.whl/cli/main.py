#!/usr/bin/env python3
# pylint: disable=no-value-for-parameter
import json
import os
import time
from typing import List

import click
import requests

from wxcloud.apis import CollectionAdd, CollectionQuery, Query
from wxcloud.mappings import Model

def __read_from_file(c, data, after, tag):
    with open(data, 'r') as f:
        data = json.load(f)
        for item in data:
            m = Model()
            m.tag = tag
            m.decode_from_webscraper(item)

            if m.when != None and m.when != '' and time.strptime(m.when, '%Y/%m/%d') >= time.strptime(after, '%Y/%m/%d'):
                c.data.append(m)

def __filter_existed_data(results, data):
    result: List = []
    for i in data:
        exists: bool = False
        for j in results:
            d = json.loads(j)
            if i.digest == d['digest']:
                exists = True
                break
        if not exists:
            result.append(i)
    return result

@click.command()
@click.option('--data', default='data/20200823-special.json', show_default=True, help='specify a scraped-json data file')
@click.option('--env', default=lambda: os.environ.get('WX_ENV', 'dev-f7e8f5'), show_default='Environment variable: WX_ENV', help='WeChat Mini Program env variable')
@click.option('--appid', default=lambda: os.environ.get('WX_APPID', None), show_default='Environment variable: WX_APPID', required=True, help='WeChat Mini Program app id')
@click.option('--secret', default=lambda: os.environ.get('WX_SECRET', None), show_default='Environment variable: WX_SECRET', required=True, help='WeChat Mini Program app secret')
@click.option('--after', default='2020/05/01', show_default=True, help='Any latest data before this date can be included')
@click.option('--tag', default='VOA Special English', show_default=True, help='Manually maintain the data tags')
def startbucks(data, env, appid, secret, after, tag):
    c = CollectionQuery('posts', 'digest')
    __read_from_file(c, data, after, tag)

    q = Query(env, c)
    text = q.decode()

    r = requests.get(f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}')
    ak = r.json()['access_token']

    r = requests.post(f'https://api.weixin.qq.com/tcb/databasequery?access_token={ak}', data=text)
    results = r.json()['data']
    excludes = __filter_existed_data(results, c.data)

    c = CollectionAdd('posts')
    c.data = excludes
    q = Query(env, c)
    text = q.decode()

    r = requests.post(f'https://api.weixin.qq.com/tcb/databaseadd?access_token={ak}', data=text)
    print(r.json())
    
